"""Prepare isolated behavioral cases; no expected answer is placed in the packet."""
import sys
import uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/character_pipeline'))
import generation_harness as g
runs=ROOT/'artifacts/generation_harness_audit/unit_fixtures'
required=['test_source_technical_clean_is_hold/source.json','test_profile_front_hips_and_wrong_boot_axis/wrong_source.json',
          'test_changed_source_or_generator_invalidates_receipt/source.json']
base=next(p for p in sorted(runs.iterdir(),key=lambda p:p.stat().st_mtime,reverse=True) if all((p/r).is_file() for r in required))
out=ROOT/'artifacts/generation_harness_audit/luna_forward_test'/uuid.uuid4().hex
out.mkdir(parents=True)
for name,item in zip(('A','B','C'),required):
    source_path=base/item; source=g.read(source_path)
    g.write(out/(name+'.job.json'),{'schema':1,'actor_id':source['actor_id'],'costume_id':source['costume_id'],
        'request':source['request'],'permit':source['attempt_permit'],'source_manifest':g.ref(source_path)})
g.write(out/'packet.json',{'task':'Resume each supplied job through its currently permitted next step. Do not generate, launch a renderer, edit inputs or create approval records. Save next actions and supporting evidence.',
    'skill':str(ROOT/'.agents/skills/sable-motion-production/SKILL.md'),'jobs':[g.ref(out/(n+'.job.json')) for n in ('A','B','C')],
    'output_directory':str(out/'response')})
print(out/'packet.json')
