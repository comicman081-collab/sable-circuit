"""Split source-UV cells at semantic boundaries without inventing image pixels."""
from fractions import Fraction

# Annotation boundaries are rational source-pixel coordinates. Keep exact
# arithmetic until the shared topology is complete: float clipping otherwise
# leaves nearly coincident slivers and contradictory edge subdivisions.
EPS=0


def cross(a,b,p):
    return (b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])


def area(polygon):
    return sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(polygon,polygon[1:]+polygon[:1]))/2


def clean(polygon):
    result=[]
    for point in polygon:
        point=tuple(value if isinstance(value,Fraction) else Fraction(str(value)) for value in point)
        if not result or point!=result[-1]:result.append(point)
    if len(result)>1 and result[-1]==result[0]:result.pop()
    return result if len(result)>=3 and abs(area(result))>EPS else []


def triangulate(polygon):
    polygon=clean(polygon)
    if not polygon:raise ValueError('NONEMPTY_SIMPLE_REGION_POLYGON_REQUIRED')
    if area(polygon)<0:polygon.reverse()
    result=[]
    while len(polygon)>3:
        found=False
        for i,b in enumerate(polygon):
            a=polygon[i-1];c=polygon[(i+1)%len(polygon)]
            if cross(a,b,c)<=EPS:continue
            others=[p for j,p in enumerate(polygon) if j not in ((i-1)%len(polygon),i,(i+1)%len(polygon))]
            if any(cross(a,b,p)>=-EPS and cross(b,c,p)>=-EPS and cross(c,a,p)>=-EPS for p in others):continue
            result.append([a,b,c]);polygon.pop(i);found=True;break
        if not found:raise ValueError('SELF_INTERSECTING_OR_DEGENERATE_REGION')
    result.append(polygon)
    return result


def half_plane(polygon,a,b,inside):
    result=[]
    for first,second in zip(polygon,polygon[1:]+polygon[:1]):
        d1=cross(a,b,first);d2=cross(a,b,second)
        keep1=d1>=-EPS if inside else d1<=EPS
        keep2=d2>=-EPS if inside else d2<=EPS
        if keep1:result.append(first)
        if keep1!=keep2 and abs(d1-d2)>EPS:
            t=d1/(d1-d2)
            result.append((first[0]+t*(second[0]-first[0]),first[1]+t*(second[1]-first[1])))
    return clean(result)


def subtract_triangle(polygon,triangle):
    remaining=polygon;outside=[]
    for a,b in zip(triangle,triangle[1:]+triangle[:1]):
        if not remaining:break
        discarded=half_plane(remaining,a,b,False)
        if discarded:outside.append(discarded)
        remaining=half_plane(remaining,a,b,True)
    return remaining,outside


def compile_regions(regions):
    result=[]
    for index,region in enumerate(regions):
        polygon=region['polygon_px']
        xs=[p[0] for p in polygon];ys=[p[1] for p in polygon]
        result.append({'id':index,'bounds':(min(xs),min(ys),max(xs),max(ys)),
                       'triangles':triangulate(polygon)})
    return result


def partition_cell(x0,y0,x1,y1,regions):
    remaining=[[(x0,y0),(x1,y0),(x1,y1),(x0,y1)]];assigned=[]
    for region in regions:
        bx0,by0,bx1,by1=region['bounds']
        if bx1<x0 or bx0>x1 or by1<y0 or by0>y1:continue
        for triangle in region['triangles']:
            next_remaining=[]
            for polygon in remaining:
                hit,outside=subtract_triangle(polygon,triangle)
                if hit:assigned.append((region['id'],hit))
                next_remaining.extend(outside)
            remaining=next_remaining
            if not remaining:break
    assigned.extend((-1,polygon) for polygon in remaining)
    expected=(x1-x0)*(y1-y0)
    if sum(abs(area(polygon)) for _,polygon in assigned)!=expected:
        raise ValueError('SOURCE_UV_PARTITION_HAS_GAP_OR_OVERLAP')
    return assigned


def conforming_triangles(pieces, bucket_size=8):
    """Join all same-region edge subdivisions before convex-piece triangulation.

    Clipping can leave collinear polygon vertices and T junctions. A fan from
    the first corner makes zero-area triangles; independent cell fans also
    disagree on shared edge subdivisions. Insert the global boundary vertices
    and use an interior center, retaining every nonzero boundary segment.
    Exact rational arithmetic retains shared intersections. Conversion to
    floating point happens only after topology is complete, for Blender's
    coordinates. The caller derives every UV directly from the source XY.
    """
    from collections import defaultdict
    from math import floor

    buckets=defaultdict(set)
    canonical=[]
    for region,polygon in pieces:
        points=[]
        for x,y in polygon:
            point=(Fraction(x),Fraction(y))
            if not points or point!=points[-1]:points.append(point)
        if len(points)>1 and points[0]==points[-1]:points.pop()
        if len(points)<3 or area(points)==0:continue
        if area(points)<0:points.reverse()
        canonical.append((region,points))
        for x,y in points:
            buckets[(region,floor(x/bucket_size),floor(y/bucket_size))].add((x,y))

    result=[]
    for region,polygon in canonical:
        boundary=[]
        for a,b in zip(polygon,polygon[1:]+polygon[:1]):
            dx=b[0]-a[0];dy=b[1]-a[1];length2=dx*dx+dy*dy
            candidates=set()
            for bx in range(floor(min(a[0],b[0])/bucket_size),
                            floor(max(a[0],b[0])/bucket_size)+1):
                for by in range(floor(min(a[1],b[1])/bucket_size),
                                floor(max(a[1],b[1])/bucket_size)+1):
                    candidates.update(buckets.get((region,bx,by),()))
            ordered=[]
            for point in candidates:
                t=((point[0]-a[0])*dx+(point[1]-a[1])*dy)/length2
                if 0<=t<1 and cross(a,b,point)==0:
                    ordered.append((t,point))
            for _,point in sorted(ordered):
                if not boundary or boundary[-1]!=point:boundary.append(point)
        if len(boundary)<3:raise ValueError('CONFORMING_POLYGON_LOST_BOUNDARY')
        center=(sum(p[0] for p in boundary)/len(boundary),
                sum(p[1] for p in boundary)/len(boundary))
        for a,b in zip(boundary,boundary[1:]+boundary[:1]):
            signed=cross(center,a,b)
            if signed<=0:raise ValueError('NONCONVEX_OR_DEGENERATE_CONFORMING_PIECE')
            result.append((region,tuple(tuple(map(float,p)) for p in (center,a,b))))
    return result
