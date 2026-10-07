"""Small API-contract regressions; never visual or generation approval."""
import ast
import types
import unittest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Historical API regression only. The actual production entrypoint is retired.
BUILDER = ROOT / 'artifacts/quarantine/generation_diagnostics/art_authority_retired_scripts_r1/build_mica_anatomical_candidate.py'
sys.path.insert(0, str(ROOT / 'tools/character_pipeline'))
from mesh_surface_orientation import closed_component_orientation
from triangle_surface_checks import triangles_intersect, intersection_beyond_shared
from facial_overlay_projection import projected_area2


class ProjectionAreaTests(unittest.TestCase):
    def test_existing_uv_double_area_boundary_not_relaxed(self):
        self.assertEqual(projected_area2([(0,0),(.5,0),(0,.5)],1,1),.25)
        self.assertLess(projected_area2([(0,0),(.5,0),(0,.499)],1,1),.25)
        self.assertEqual(projected_area2([(0,0),(.5,.5),(1,1)],1024,1536),0)


class TriangleIntersectionTests(unittest.TestCase):
    a = [(0.,0.,0.), (2.,0.,0.), (0.,2.,0.)]

    def test_noncoplanar_cross_and_separation(self):
        self.assertTrue(triangles_intersect(self.a,[(.5,.5,-1.),(.5,.5,1.),(1.,1.,0.)]))
        self.assertFalse(triangles_intersect(self.a,[(.5,.5,1.),(1.,.5,1.),(.5,1.,1.)]))

    def test_coplanar_overlap_and_bounding_box_false_positive(self):
        self.assertTrue(triangles_intersect(self.a,[(.2,.2,0.),(1.,.2,0.),(.2,1.,0.)]))
        self.assertFalse(triangles_intersect(self.a,[(1.5,1.5,0.),(2.,1.5,0.),(1.5,2.,0.)]))

    def test_touch_and_degenerate(self):
        self.assertTrue(triangles_intersect(self.a,[(2.,0.,0.),(3.,0.,0.),(2.,1.,0.)]))
        with self.assertRaisesRegex(ValueError,'DEGENERATE'):
            triangles_intersect(self.a,[(0.,0.,0.)]*3)

    def test_shared_point_cannot_hide_crossing(self):
        a=[(0.,0.,0.),(1.,0.,0.),(0.,1.,0.)]
        self.assertTrue(intersection_beyond_shared(a,[(0.,0.,0.),(.5,.5,-1.),(.5,.5,1.)],[a[0]]))
        self.assertFalse(intersection_beyond_shared(a,[(0.,0.,0.),(-1.,0.,0.),(0.,-1.,0.)],[a[0]]))

    def test_intended_shared_edge_and_coplanar_overlap(self):
        a=[(0.,0.,0.),(1.,0.,0.),(0.,1.,0.)]
        self.assertFalse(intersection_beyond_shared(a,[(1.,0.,0.),(0.,0.,0.),(0.,0.,1.)],a[:2]))
        self.assertFalse(intersection_beyond_shared(a,[(1.,0.,0.),(0.,0.,0.),(0.,-1.,0.)],a[:2]))
        self.assertTrue(intersection_beyond_shared(a,[(1.,0.,0.),(0.,0.,0.),(.5,.5,0.)],a[:2]))


class ClosedSurfaceTests(unittest.TestCase):
    vertices = [(0.,0.,0.), (1.,0.,0.), (0.,1.,0.), (0.,0.,1.)]
    faces = [[0,2,1], [0,1,3], [1,2,3], [2,0,3]]

    def test_disconnected_shells_are_measured_independently(self):
        vertices = self.vertices + [(x-4,y,z) for x,y,z in self.vertices]
        faces = self.faces + [[i+4 for i in reversed(f)] for f in self.faces]
        before = [tuple(v) for v in vertices]
        components = closed_component_orientation(vertices, faces)
        self.assertAlmostEqual(components[0]['signed_volume_m3'], 1/6)
        self.assertAlmostEqual(components[1]['signed_volume_m3'], -1/6)
        inward = {i for c in components if c['signed_volume_m3'] < 0 for i in c['face_ids']}
        fixed = [list(reversed(f)) if i in inward else f[:] for i,f in enumerate(faces)]
        self.assertTrue(all(c['signed_volume_m3'] > 0 for c in closed_component_orientation(vertices, fixed)))
        self.assertEqual(vertices, before)
        self.assertEqual({i for f in faces for i in f}, {i for f in fixed for i in f})

    def test_open_and_nonmanifold_are_not_auto_approved(self):
        for faces in (self.faces[:-1], self.faces + [self.faces[0]]):
            with self.assertRaisesRegex(ValueError, 'CLOSED_MANIFOLD'):
                closed_component_orientation(self.vertices, faces)

    def test_one_inconsistent_face_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'CONSISTENT_COMPONENT'):
            closed_component_orientation(self.vertices, [self.faces[0][::-1]] + self.faces[1:])


class LibraryNamesTests(unittest.TestCase):
    def test_actual_loader_block_preserves_expected_names(self):
        tree = ast.parse(BUILDER.read_text(encoding='utf-8'))
        build = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'build')
        index = next(i for i, n in enumerate(build.body) if isinstance(n, ast.Assign)
                     and any(isinstance(t, ast.Name) and t.id == 'wanted' for t in n.targets))
        statements = build.body[index:index + 2]
        self.assertIsInstance(statements[1], ast.With)
        expected = ast.literal_eval(statements[0].value)
        selected = types.SimpleNamespace(objects=[])

        class MutableBlenderLibrary:
            def __enter__(self):
                return types.SimpleNamespace(objects=expected[:]), selected

            def __exit__(self, *_):
                # bpy library loading replaces names in the supplied list.
                selected.objects[:] = [types.SimpleNamespace(name=n) for n in selected.objects]

        env = {'bpy': types.SimpleNamespace(data=types.SimpleNamespace(
            libraries=types.SimpleNamespace(load=lambda *a, **k: MutableBlenderLibrary()))),
            'RIG_INPUT': 'synthetic API contract only'}
        exec(compile(ast.Module(body=statements, type_ignores=[]), str(BUILDER), 'exec'), env)
        self.assertEqual(env['wanted'], expected)
        self.assertIsNot(env['wanted'], selected.objects)
        self.assertEqual(next(o for o in selected.objects if o.name == env['wanted'][0]).name, expected[0])


if __name__ == '__main__':
    unittest.main()
