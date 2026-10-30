"""Reject private source media from the audit index and owned branch commits."""
import json
import subprocess
from pathlib import Path

B = Path(__file__).resolve().parent.parent
BASE = 'b3dc7675c94d1f0fbe11e7dd7988800033588976'
PRIVATE_MEDIA = {'.pdf', '.png', '.jpg', '.jpeg', '.tif', '.tiff'}


def git(*args):
    return subprocess.check_output(['git', *args]).decode().splitlines()


def main():
    root = Path(git('rev-parse', '--show-toplevel')[0])
    relative = str(B.relative_to(root))
    indexed = git('ls-files', relative)
    assert not [p for p in indexed if Path(p).suffix.lower() in PRIVATE_MEDIA]
    commits = git('rev-list', BASE + '..HEAD')
    for commit in commits:
        paths = git('ls-tree', '-r', '--name-only', commit, relative)
        assert not [p for p in paths if Path(p).suffix.lower() in PRIVATE_MEDIA], commit
    print(json.dumps({'indexed_audit_files': len(indexed),
                      'owned_commits_checked': len(commits),
                      'private_media_in_index_or_owned_history': 0}))


if __name__ == '__main__':
    main()
