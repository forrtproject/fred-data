// One bounded scheduler tick, evaluated inside functions.exec; never a watcher loop.
const base='/home/lukas/.t3/worktrees/fred-data/audit-fred-stats-2026-10/audit/fred_stats_2026-10/completion_pass_2026-10-31';
const read=async cmd=>{const r=await tools.exec_command({cmd,max_output_tokens:22000});if(r.exit_code!==0)throw Error(r.output);return r.output};
const save=async(path,data)=>await tools.exec_command({cmd:"python3 - <<'FREDTASKJSON'\nfrom pathlib import Path\nimport json\np=Path("+JSON.stringify(path)+");old=json.loads(p.read_text()) if p.exists() else {};old.update(json.loads("+JSON.stringify(JSON.stringify(data))+"));p.write_text(json.dumps(old,indent=2)+chr(10))\nFREDTASKJSON",max_output_tokens:100});
const q=JSON.parse(await read(`python3 -c "from pathlib import Path;p=Path('${base}');print((p/('work_queue.json' if (p/'work_queue.json').exists() else 'pilot_queue.json')).read_text())"`));
const tasks=JSON.parse(await read(`python3 - <<'PY'\nimport json\nfrom pathlib import Path\np=Path('${base}/tasks')\nprint(json.dumps({f.stem:{k:v for k,v in json.loads(f.read_text()).items() if k in ['taskId','status','started_at']} for f in p.glob('*.json')}))\nPY`));
let active=0;let finished=0;
for(const [key,t] of Object.entries(tasks)){
 if(!t.taskId||['completed','failed','cancelled','interrupted'].includes(t.status)){if(t.status==='completed')finished++;continue;}
 const res=await tools.mcp__t3_code__task_status({taskId:t.taskId});const s=res.structuredContent;if(!s)throw Error('Status response absent');
 Object.assign(t,{status:s.status,hasPendingChildRuns:s.hasPendingChildRuns,summary:s.summary,last_checked_at:new Date().toISOString()});
 if(!['completed','failed','cancelled','interrupted'].includes(s.status)||s.hasPendingChildRuns){active++;const age=(Date.now()-Date.parse(t.started_at))/60000;if(age>14){await tools.mcp__t3_code__task_cancel({taskId:t.taskId,reason:'Owned completion worker exceeded hard runtime allowance',clientRequestId:'cancel-'+key});t.status='cancelled';active--;}}
 else {t.completed_at=t.completed_at||new Date().toISOString();finished++;}
 await save(`${base}/tasks/${key}.json`,t);
}
let launched=0;
for(const b of q){if(tasks[b.key]||active>=6)continue;
 const res=await tools.mcp__t3_code__delegate_task({clientRequestId:'fred-completion-pilot-'+b.key+'-v1',title:'Blind source completion '+b.key,mode:'async',isolation:'shared',target:{providerInstanceId:'codex',model:'gpt-6.1-sol',options:{reasoningEffort:'medium',serviceTier:'default'}},task:`Fresh BLIND source-grouped completion. Read ONLY ${base}/extraction_brief.txt (assigned schema and instructions), input ${b.input}, and primary text/PDF named there. No other repo files, datasets, old extractions/comparisons/baselines/reports/prompts, repository searches, network/acquisition, delegation, or Git. Check all unfinished_fields for the assigned rows together from this source. YOUR_OUTPUT=${b.output}; YOUR_SOURCE_KEY=${b.key}. Core schema checkpoints plus dispositions.json, one code/reason/evidence record for EVERY assigned unfinished field. Do not assign targets by row order or numeric matching. Preserve printed metric and same-test p bounds; analytic N sums only from explicit mutually exclusive final groups, with arithmetic/roles/exclusions recorded. Quotes must match supplied canonical text literally or ordered fragments with ...; render target PDF pages for layout/OCR ONLY under /home/lukas/.cache/fred-completion-renders/${b.key}. Aim8min hard12min; checkpoint progressively. Return counts and paths only.`});
 const s=res.structuredContent;if(!s||s.providerInstanceId!=='codex'||s.model!=='gpt-6.1-sol'||!s.options?.some(o=>o.id==='reasoningEffort'&&o.value==='medium'))throw Error('Model/options mismatch');
 const t={...b,taskId:s.taskId,status:s.status,started_at:new Date().toISOString(),provider:s.providerInstanceId,model:s.model,options:s.options};await save(`${base}/tasks/${b.key}.json`,t);active++;launched++;
}
text({active_children:active,finished_tasks:finished,launched,remaining_pilot_sources:q.filter(b=>!tasks[b.key]).length-launched});
