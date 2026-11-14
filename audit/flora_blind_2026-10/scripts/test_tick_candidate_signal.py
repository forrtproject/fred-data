"""Exercise the generated candidate wrapper with real signals and a fake CLI."""
import ctypes
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest


ROOT = Path(__file__).resolve().parents[1]


def alive(pid):
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False


class CandidateSignalTest(unittest.TestCase):
    def wrapper(self):
        # Run the actual tick, replacing only its app/terminal tools with mocks.
        script = r"""
const fs=require('fs');
const AsyncFunction=Object.getPrototypeOf(async function(){}).constructor;
const tick=new AsyncFunction('tools','text',fs.readFileSync(process.argv[1],'utf8'));
let prompt;
const tools={exec_command:async({cmd})=>{
 let value=null;
 if(cmd.includes("'plan'"))value={status:'active',active:[],slot_cost:0,
  luna_active:0,luna_pending:[],luna_limit:3,luna_completed:0,luna_total:0};
 else if(cmd.includes("'candidate-cli-dispatch'")&&!cmd.includes('FIXTURE_OWNER'))
  value={snapshot:'fixture',workers:1,round:1,clientRequestId:'fixture-round'};
 return {exit_code:0,output:JSON.stringify(value)};
},mcp__t3_code__delegate_task:async request=>{
 prompt=request.task;
 return {structuredContent:{taskId:'FIXTURE_OWNER',status:'running',
  providerInstanceId:'codex',model:'gpt-6.1-sol',
  options:{reasoningEffort:'medium',serviceTier:'default'}}};
}};
tick(tools,()=>{}).then(()=>process.stdout.write(JSON.stringify(
 prompt.split('Script:\n')[1].split('\nReport the helper result')[0]
))).catch(e=>{console.error(e);process.exitCode=1;});
"""
        result = subprocess.run(
            ['node', '-e', script, str(ROOT / 'scripts/tick_evidence_followup.js')],
            check=True, capture_output=True, text=True, timeout=5)
        return json.loads(result.stdout)

    def exercise(self, terminate):
        # Adopt only fixture descendants if the buggy waiting wrapper dies first.
        ctypes.CDLL(None).prctl(36, 1, 0, 0, 0)
        private = ROOT / 'evidence_followup/private'
        private.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='signal-regression-', dir=private) as d:
            case = Path(d)
            control = case / 'control.json'
            control.write_text(json.dumps({'clientRequestId': 'fixture-round',
                'reservation': {'snapshot': 'fixture', 'workers': 1,
                                'taskId': 'FIXTURE_OWNER'}}))
            helper = case / 'helper.py'
            helper.write_text('''import concurrent.futures,importlib.util,json,os,signal,sys
from pathlib import Path
case=Path(__file__).parent
spec=importlib.util.spec_from_file_location('relay', ''' + repr(str(
                ROOT / 'evidence_followup/candidate_cli_relay.py')) + ''')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
signal.signal(signal.SIGTERM,m.interrupted)
(case/'helper.pid').write_text(str(os.getpid()))
fake="import os,time;from pathlib import Path;Path("+repr(str(case/'cli.pid'))+").write_text(str(os.getpid()));time.sleep(''' + (
                '20' if terminate else '0.05') + ''')"
with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
 rc=pool.submit(m.cli_transport,[sys.executable,'-c',fake],case/'raw',30).result()
print(json.dumps({'helper_completed':True,'cli_rc':rc}),flush=True)
''')
            script = self.wrapper().replace(str(ROOT / 'evidence_followup/candidate_cli/control.json'),
                                            str(control)).replace(
                str(ROOT / 'evidence_followup/candidate_cli_relay.py'), str(helper))
            env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
            process = subprocess.Popen([sys.executable, '-c', script],
                start_new_session=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
            pids = [process.pid]
            try:
                deadline = time.monotonic() + 3
                while not (case / 'cli.pid').exists():
                    if time.monotonic() >= deadline:
                        self.fail('fake CLI did not start')
                    time.sleep(0.01)
                helper_pid = int((case / 'helper.pid').read_text())
                cli_pid = int((case / 'cli.pid').read_text())
                pids += [helper_pid, cli_pid]
                if terminate:
                    os.kill(process.pid, signal.SIGTERM)
                process.wait(timeout=3)
                self.assertFalse(alive(helper_pid), 'waiting wrapper stranded its helper')
                self.assertFalse(alive(cli_pid), 'waiting wrapper stranded its CLI group')
                stdout, stderr = process.communicate(timeout=3)
                self.assertEqual(json.loads((case / 'raw.process.json').read_text())['status'], 'reaped')
                if terminate:
                    self.assertNotEqual(process.returncode, 0)
                else:
                    self.assertEqual(process.returncode, 0, stderr.decode())
                    self.assertTrue(json.loads(stdout)['helper_completed'])
            finally:
                for pid in set(pids):
                    if alive(pid):
                        try:
                            os.kill(pid, signal.SIGTERM)
                        except ProcessLookupError:
                            pass
                if process.poll() is None:
                    process.communicate(timeout=3)
                deadline = time.monotonic() + 2
                while time.monotonic() < deadline:
                    try:
                        while os.waitpid(-1, os.WNOHANG)[0]:
                            pass
                    except ChildProcessError:
                        break
                    time.sleep(0.01)
                for pid in set(pids):
                    self.assertFalse(alive(pid), 'fixture process leaked')
                process.communicate(timeout=3)

    def test_outer_sigterm_reaches_helper_and_reaps_cli(self):
        self.exercise(True)

    def test_normal_completion_is_collected(self):
        self.exercise(False)


if __name__ == '__main__':
    unittest.main()
