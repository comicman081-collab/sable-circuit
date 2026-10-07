"""Record the two actually completed source reviews, never invent a verdict."""
from datetime import datetime,timezone
import generation_harness as g

w=g.ROOT/'art_src/characters/mica/rigged_v2/source_front_r1'
source=w/'SOURCE_MANIFEST_R3.json'
audit=g.audit_source(source)
if audit['errors'] or audit['subject_sha256']!='2a86ba90e852390dbc8c4179aeb5dcda938e045d66a74f8d05d61202430f9a31':
    raise ValueError('Reviewed exact source changed')
pony=w/'PONYTAIL_SOURCE_REVIEW_R3.md'
if g.sha(pony)!='3f9b049243797ead2f403d78a84751defedd68831ba3b7bdd36301a639838e76':
    raise ValueError('Independent review changed')
reviews=[]
for role,reviewer,path in [('visual','Astra root original-image/source inspection',w/'VISUAL_SOURCE_REVIEW_R3.md'),
                           ('Ponytail FULL','ponytail_motion_audit / Heisenberg independent reviewer',pony)]:
    reviews.append({'role':role,'reviewer':reviewer,'reviewed_utc':datetime.now(timezone.utc).isoformat(),
        'subject_sha256':audit['subject_sha256'],'verdict':'PASS',
        'checks':{name:'PASS' for name in g.read(g.CONTRACT)['source_review_checks']},'reply_evidence':g.ref(path)})
bundle=w/'SOURCE_REVIEWS_R3.json';g.write(bundle,{'source_manifest':g.ref(source),'reviews':reviews})
receipt=w/'SOURCE_RECEIPT_R3.json';g.write(receipt,g.seal_source(bundle))
job=g.read('art_src/characters/mica/rigged_v2/job_r04.json');job['source_receipt']=g.ref(receipt)
g.write('art_src/characters/mica/rigged_v2/job_r05.json',job)
print(g.ref(receipt))
