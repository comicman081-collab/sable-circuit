"""Real Blender BVH enclosure regression. Technical geometry, no artwork."""
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/character_pipeline'))
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from anatomical_boot_envelope import point_inside_closed_shell
import generation_harness as g


def run():
    vertices=[Vector(v) for v in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),
                                  (-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
    faces=[(0,2,1),(0,3,2),(4,5,6),(4,6,7),(0,1,5),(0,5,4),
           (1,2,6),(1,6,5),(2,3,7),(2,7,6),(3,0,4),(3,4,7)]
    bvh=BVHTree.FromPolygons(vertices,faces,all_triangles=True)
    cases=[((0,0,0),'inside'),((1.2,1.2,0),'outside'),((1.0001,.5,.5),'outside'),
           ((.9999,.5,.5),'inside'),((1.000001,0,0),'boundary_tolerance'),((-1.2,-1.2,-1.2),'outside')]
    result=[]
    for xyz,expected in cases:
        actual=point_inside_closed_shell(Vector(xyz),bvh,vertices,faces)
        assert actual['classification']==expected,(xyz,actual,expected)
        result.append({'point':xyz,'expected':expected,'actual':actual})
    return {'technical_only':True,'cases':result,'helper':g.ref(ROOT/'tools/character_pipeline/anatomical_boot_envelope.py')}


if __name__=='__main__':
    destination=sys.argv[sys.argv.index('--')+1]
    g.write(destination,run())
    print('PASS_REAL_BVH_ENCLOSURE_REGRESSION')
