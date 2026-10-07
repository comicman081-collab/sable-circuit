"""Preserve known rejected outputs; no deletion, source overwrite or promotion."""
from pathlib import Path
import json,hashlib,shutil
lab=Path(__file__).resolve().parents[2]
out=lab/'art/quarantine/site7_rifle_pair_failures_20260913'
out.mkdir(parents=True,exist_ok=True)
rows=[]
for name,scope,notes in [
    ('rifle_Epair1','left figure only','Left figure repeats the right-planted pose instead of right-swing-behind; right figure is retained as the current E4 candidate, not approved.'),
    ('rifle_Epair2','both figures','Both figures repeat the near holstered right support leg; neither supplies the requested opposite passing pair. Right pose also has stiff forward kick.')]:
    source=lab/'art/site7_enemies_raw'/f'{name}.png'
    proof=Path(__file__).parent/f'{name}_tool_response.json'
    assets=[]
    for path in [source,proof]:
        target=out/path.name
        digest=hashlib.sha256(path.read_bytes()).hexdigest()
        if target.exists() and hashlib.sha256(target.read_bytes()).hexdigest()!=digest:raise ValueError('Do not overwrite prior rejected evidence')
        if not target.exists():shutil.copy2(path,target)
        assert hashlib.sha256(target.read_bytes()).hexdigest()==digest
        assets.append({'source':str(path.relative_to(lab)),'quarantineCopy':str(target.relative_to(lab)),'sha256':digest})
    rows.append({'id':name,'decision':'FAIL_NOT_PROMOTABLE','scope':scope,'notes':notes,'assets':assets})
ledger=out/'rejections.json'
if ledger.exists():raise ValueError('Keep prior ledger intact')
ledger.write_text(json.dumps({'retained':rows,'deleted':False,'reviewer':'Codex actual source-image inspection','partialMasterPreserved':True},indent=2),encoding='utf-8')
print(ledger)
