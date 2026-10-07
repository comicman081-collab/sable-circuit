"""Bind actual time-specific visual observations to the captured current runtime."""
import math
import character_workflow as w

FIELDS=('oppositeFootExchange','footSliding','loopContinuity')


def template(character, package, capture):
    return {'kind':'sable-runtime-observations','character':character,
            'inputSHA256':package['inputSHA256'],'videoSHA256':capture['videoSHA256'],
            'reviewer':'','decision':'unreviewed',
            'directions':{d:{action:{'seconds':[],**{field:'' for field in FIELDS}}
                             for action in ('walk','run')} for d in w.DIRECTIONS},
            'transitions':{name:{'seconds':[],'notes':''} for name in
                           ('adjacent turn + fire','opposite turn','speed up','speed down + stop fire','stop + planted fire','resume')}}


def validate(report, character, package, capture, reviewer):
    if (report.get('kind')!='sable-runtime-observations' or report.get('character')!=character or
        report.get('inputSHA256')!=package['inputSHA256'] or report.get('videoSHA256')!=capture['videoSHA256']):
        raise ValueError('Runtime observations do not belong to this captured build')
    if report.get('decision')!='approved' or not reviewer or report.get('reviewer')!=reviewer:
        raise ValueError('Record an actual runtime observer and decision')
    observations=capture['observations']
    def times(row,selected):
        values=row.get('seconds',[])
        if (not isinstance(values,list) or len(values)<2 or
            any(type(t) not in (int,float) or not math.isfinite(t) for t in values) or
            any(b<=a for a,b in zip(values,values[1:]))):
            raise ValueError('Record at least two chronological video times per observation')
        if not selected:raise ValueError('This video lacks the reviewed segment')
        start,end=selected[0]['elapsedMs']/1000,selected[-1]['elapsedMs']/1000
        if any(t<start or t>end for t in values):raise ValueError('Observation timestamp is outside its actual captured segment')
    if set(report.get('directions',{}))!=set(w.DIRECTIONS):raise ValueError('Observe all eight runtime directions')
    for direction in w.DIRECTIONS:
        for action in ('walk','run'):
            row=report['directions'][direction].get(action,{})
            for field in FIELDS:
                if not isinstance(row.get(field),str) or len(row[field].strip())<12:raise ValueError('Missing actual visual observation: '+direction+'/'+action+'/'+field)
            selected=[s for s in observations if s.get('segment','').startswith(direction+' '+action) and ' / ' not in s.get('segment','') and s.get('amount',0)>.9]
            times(row,selected)
    for name in template(character,package,capture)['transitions']:
        row=report.get('transitions',{}).get(name,{})
        if not isinstance(row.get('notes'),str) or len(row['notes'].strip())<12:raise ValueError('Missing transition observation: '+name)
        times(row,[s for s in observations if s.get('segment','').endswith(' / '+name)])
    return True
