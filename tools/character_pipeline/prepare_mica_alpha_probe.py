"""Reserve exactly one user-authorized native-alpha ImageGen probe."""
from pathlib import Path
import generation_harness as g

work=g.ROOT/'art_src/characters/mica/rigged_v2/source_alpha_probe_r1'
if (g.ROOT/'artifacts/quarantine/generation_diagnostics/mica_native_alpha_probe_r1/RESULT.md').exists():
    raise SystemExit('Probe already completed and failed native alpha; no automatic regeneration.')
request=g.read('art_src/characters/mica/rigged_v2/source_front_r1/request.json')
request.update(output_root=work.relative_to(g.ROOT).as_posix(),background='transparent_alpha',
    prompt=g.ref(work/'prompt.txt'),
    references=[{**g.ref('art_src/characters/mica/rigged_v2/source_front_r1/MICA_C03_S_NEUTRAL_RIG_GREEN_R1.png'),
                 'role':'identity_authority'}])
g.write(work/'request.json',request)
print(g.audit_request(work/'request.json'))
print(g.reserve_request(work/'request.json'))
