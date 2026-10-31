"""Copy only the explicitly public report and downloads into a clean deploy directory."""
import hashlib,json,shutil,sys,zipfile
from pathlib import Path
P=Path(__file__).resolve().parent
FILES=['index.html','fred_audit_fixes_2026-10.zip','fred_fixes.csv','merge_fred_fixes.R','row_guard.csv','confirmed_corrections.csv','field_summary.csv','field_summary_by_project.csv','availability_followups.csv','screen_recheck.csv','release_summary.json','README.md','SHA256SUMS.txt']
def main():
 dest=Path(sys.argv[1]).resolve();dest.mkdir(parents=True,exist_ok=True)
 assert not any(p.name not in FILES for p in dest.iterdir()),'Unexpected old staged file'
 for name in FILES:
  path=P/name;assert path.is_file() and not path.is_symlink()
  if path.suffix!='.zip':
   text=path.read_text(encoding='utf-8-sig')
   for forbidden in ['/home/','/Users/','private_batch_','private_source/','CLOUDFLARE_API_TOKEN','access_token=']:
    assert forbidden not in text,(name,forbidden)
  else:
   with zipfile.ZipFile(path) as archive:
    assert all(n in FILES and n not in ['index.html','fred_audit_fixes_2026-10.zip'] for n in archive.namelist())
    assert all(archive.read(n)==(P/n).read_bytes() for n in archive.namelist())
  shutil.copyfile(path,dest/name)
 manifest={name:{'bytes':(dest/name).stat().st_size,'sha256':hashlib.sha256((dest/name).read_bytes()).hexdigest()} for name in FILES}
 (P/'public_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({'staged_public_files':len(FILES),'directory':str(dest),'private_source_media_or_paths':0}))
if __name__=='__main__':main()
