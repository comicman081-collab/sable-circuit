"""Narrow-phase geometric checks, independent of BVH bounding-box candidates."""
import math


def sub(a,b): return tuple(x-y for x,y in zip(a,b))
def dot(a,b): return sum(x*y for x,y in zip(a,b))
def cross(a,b): return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])


def triangles_intersect(a,b,tolerance=1e-9):
    """Closed triangles incl. non-adjacent touch; SAT with coplanar edge axes.

    Callers separately exclude topologically adjacent pairs. Degenerate
    triangles are invalid input, not evidence of clean geometry.
    """
    if len(a)!=3 or len(b)!=3 or any(len(v)!=3 or not all(math.isfinite(x) for x in v) for v in list(a)+list(b)):
        raise ValueError('TWO_FINITE_TRIANGLES_REQUIRED')
    ea=[sub(a[(i+1)%3],a[i]) for i in range(3)]
    eb=[sub(b[(i+1)%3],b[i]) for i in range(3)]
    na=cross(ea[0],ea[1]);nb=cross(eb[0],eb[1])
    if dot(na,na)<1e-24 or dot(nb,nb)<1e-24:
        raise ValueError('DEGENERATE_TRIANGLE')
    axes=[na,nb]+[cross(x,y) for x in ea for y in eb]
    axes += [cross(n,e) for n in (na,nb) for e in ea+eb]
    origin=a[0];aa=[sub(v,origin) for v in a];bb=[sub(v,origin) for v in b]
    for axis in axes:
        length=math.sqrt(dot(axis,axis))
        if length<1e-18:continue
        av=[dot(v,axis)/length for v in aa];bv=[dot(v,axis)/length for v in bb]
        if max(av)<min(bv)-tolerance or max(bv)<min(av)-tolerance:return False
    return True


def intersection_beyond_shared(a,b,shared,tolerance=1e-8):
    """Detect intersection away from the explicitly shared point/edge.

    Intersection endpoints are measured in 3D; coplanar pairs use polygon
    clipping. Intended mesh adjacency alone is allowed, not a crossing that
    happens to share one vertex. The absolute tolerance is recorded by callers.
    """
    def length(v):return math.sqrt(dot(v,v))
    def scale(v,s):return tuple(x*s for x in v)
    def add(a,b):return tuple(x+y for x,y in zip(a,b))
    def unit(v):
        size=length(v)
        if size<1e-12:raise ValueError('DEGENERATE_TRIANGLE')
        return scale(v,1/size)
    na=unit(cross(sub(a[1],a[0]),sub(a[2],a[0])))
    nb=unit(cross(sub(b[1],b[0]),sub(b[2],b[0])))
    parallel=length(cross(na,nb))<1e-10
    # Two noncoplanar triangles sharing a complete edge intersect only on that
    # edge's line; each triangle meets the line only at its actual edge.
    if len(shared)==2 and not parallel:return False
    def inside(p,tri,n):
        for i in range(3):
            edge=sub(tri[(i+1)%3],tri[i])
            if dot(cross(edge,sub(p,tri[i])),n)<-tolerance*length(edge):return False
        return True
    points=[]
    if parallel:
        if abs(dot(sub(b[0],a[0]),na))>tolerance:return False
        # Convex Sutherland-Hodgman clipping in the common 3D plane.
        points=[tuple(v) for v in a]
        for i in range(3):
            origin=b[i];edge=sub(b[(i+1)%3],origin);clip_normal=cross(nb,edge)
            prior=points;points=[]
            if not prior:break
            p=prior[-1];dp=dot(sub(p,origin),clip_normal)
            for q in prior:
                dq=dot(sub(q,origin),clip_normal);limit=tolerance*length(edge)
                pin=dp>=-limit;qin=dq>=-limit
                if pin!=qin and abs(dp-dq)>1e-20:points.append(add(p,scale(sub(q,p),dp/(dp-dq))))
                if qin:points.append(q)
                p=q;dp=dq
    else:
        for first,second,normal in ((a,b,nb),(b,a,na)):
            for i,p in enumerate(first):
                q=first[(i+1)%3];dp=dot(sub(p,second[0]),normal);dq=dot(sub(q,second[0]),normal)
                if abs(dp)<=tolerance and inside(p,second,normal):points.append(p)
                if dp*dq<0:
                    v=add(p,scale(sub(q,p),dp/(dp-dq)))
                    if inside(v,second,normal):points.append(v)
    def permitted(p):
        if len(shared)==1:return length(sub(p,shared[0]))<=tolerance
        if len(shared)==2:
            edge=sub(shared[1],shared[0]);squared=dot(edge,edge)
            if squared<=1e-24:raise ValueError('DEGENERATE_SHARED_EDGE')
            t=max(0.,min(1.,dot(sub(p,shared[0]),edge)/squared))
            return length(sub(p,add(shared[0],scale(edge,t))))<=tolerance
        return False
    return any(not permitted(p) for p in points)
