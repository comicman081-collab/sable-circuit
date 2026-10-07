"""Bounded verification of the actual rejected ROOK; never approve or build art."""
import argparse
import contextlib
import copy
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import time

LAB=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(LAB))
import character_workflow as w
import character_handoff
import cycle_review
import build_character
from locomotion_review import validate_report


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--cycle-packet',required=True)
    args=parser.parse_args()
    out=Path(__file__).parent/w.stamp().replace(':','-')
    out.mkdir(parents=True,exist_ok=False)
    env=os.environ.copy()
    env.update(PYTHONDONTWRITEBYTECODE='1',TEMP=str(out),TMP=str(out),PYTHONIOENCODING='utf-8')

    def snapshot():
        files=[]
        for character in ('rook','aster','mica'):
            for relative in (f'dist/{character.upper()}_Motion_Studio.html',f'public/standalone/{character}.html',
                             f'dist/{character}.package.json'):
                path=LAB/relative
                if path.is_file():files.append(path)
            atlas=LAB/f'public/assets/atlas/{character}'
            files.extend(path for path in atlas.rglob('*') if path.is_file())
        files.extend(path for _,path in w.slots(w.recipe('rook')))
        return {path.relative_to(LAB).as_posix():w.sha(path) for path in files}

    before=snapshot()
    commands=[
        [sys.executable,'-B','-m','unittest','discover','-s','tests','-v'],
        ['node','--test',*[str(path) for path in sorted((LAB/'tests').glob('*.test.js'))]],
        [sys.executable,'-B',str(Path('C:/Users/AAA/.codex/skills/.system/skill-creator/scripts/quick_validate.py')),
         str(LAB.parent/'.agents/skills/sable-character-studio')],
    ]
    tests=[]
    for index,cmd in enumerate(commands):
        started=time.monotonic()
        result=subprocess.run(cmd,cwd=LAB,env=env,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=120)
        log=out/f'test_{index}.log';log.write_text(result.stdout+'\n'+result.stderr,encoding='utf-8')
        tests.append(dict(command=cmd,exitCode=result.returncode,seconds=time.monotonic()-started,log=w.binding(log)))
        print(json.dumps({'check':index,'exitCode':result.returncode,'log':str(log)}),flush=True)
        if result.returncode:raise RuntimeError('Verification failed; inspect '+str(log))

    probes=[]
    def reject(name,call):
        try:call()
        except ValueError as error:
            probes.append({'name':name,'rejected':True,'reason':str(error)})
        else:raise RuntimeError('Invalid workflow was accepted: '+name)

    package=w.check_package('rook')
    actual=w.read(LAB/'qa/rook_locomotion_browser.json')
    script=w.sha(LAB/'public/qa/locomotion-checks.js')
    profile=w.read(LAB/'public/assets/atlas/rook/profile.json')
    assert validate_report(actual,'rook',package['inputSHA256'],script,profile)
    changed=copy.deepcopy(actual)
    for row in changed['results']:
        if not row['stationary']:
            for sample in row['samples']:sample['frame']=[0,3,1,4,2,5][sample['frame']]
    reject('permuted chronology retaining six frame IDs',lambda:validate_report(changed,'rook',package['inputSHA256'],script,profile))
    frozen=copy.deepcopy(actual)
    for row in frozen['results']:
        for sample in row['samples']:sample.update(time=0,phase=0,position=[0,0])
    reject('frozen samples retaining travel summaries',lambda:validate_report(frozen,'rook',package['inputSHA256'],script,profile))
    reject('source-complete but unreviewed active build',lambda:build_character.compile_character(LAB/'characters/rook.json'))
    reject('blank actual cycle observation approval',lambda:cycle_review.record('rook','E','walk','approved',args.cycle_packet))
    reject('non-E expansion before approved E cycle',lambda:cycle_review.require_pilot('rook','SE'))
    reject('delivery of current rejected ROOK',lambda:w.deliver('rook','qa/rook_combat_browser.json','qa/rook_locomotion_browser.json'))

    state=w.workflow_status('rook')
    assert state['sourcesReady'] and not state['activeBuildReady'] and not state['ready']
    assert state['runtimeRepairRequired']
    assert cycle_review.current('rook','SE')['state']=='repair'
    assert cycle_review.current('rook','N')['state']=='repair'
    packet=character_handoff.make('rook')
    path=out/'rook.handoff.json';w.write(path,packet)
    handoff=character_handoff.verify(str(path))
    assert handoff['nextAction']=='REPAIR_RUNTIME_VISUAL'
    after=snapshot()
    assert before==after,'Active character or raw source changed during verification'
    report={'recordedAt':w.stamp(),'status':'PASS_IMPLEMENTED_GUARDS_NOT_CHARACTER_APPROVAL',
            'tests':tests,'negativeProbes':probes,'originalBrowserTechnicalReportAccepted':True,
            'handoff':handoff,'handoffPacket':w.binding(path),'sourceStatus':state,
            'activeAssetsAndRookSourcesUnchanged':True,'beforeAndAfter':before,
            'rookDelivery':w.read(LAB/'dist/rook.delivery.json'),
            'cycleKit':w.binding(w.local(args.cycle_packet)),
            'visualQualityApproved':False,'lunaGenerationTested':False}
    result_path=out/'verification.json';w.write(result_path,report)
    print(json.dumps({'status':report['status'],'report':str(result_path),'handoff':str(path),'negativeProbes':probes},ensure_ascii=False),flush=True)


if __name__=='__main__':main()
