"""Controls for the contact-shadow freshness check of tools/environment/build_site7_mood_light.py.

`--check` must not fail because another zlib or numpy build rounds a pixel or encodes the PNG differently (same_masks
already tolerates that for the void masks), and it must still fail for a real change: two steps, a missing or extra
plate, another padding, scale, size or schema. The test reads the shipped data and writes no file.

It also guards operation 10's void (2026-10-02, the `null` abyss read almost black): the abyss row stays lit (`NullAbyssLit`;
the near-black row it replaced is the negative control), and the plate masks keep their pocket fill (`VoidFill`): with a
lit abyss a near-black wall that reaches the image border through a narrow dark gap would show the abyss through its
recesses as blue-grey patches.
"""
import base64
import copy
import importlib.util
import io
import json
from pathlib import Path
import unittest

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('mood_tool', ROOT / 'tools/environment/build_site7_mood_light.py')
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)


def encode(pixels: np.ndarray, level: int = 6) -> str:
    out = io.BytesIO()
    Image.fromarray(pixels.astype(np.uint8), 'L').save(out, 'PNG', compress_level=level)
    return base64.b64encode(out.getvalue()).decode('ascii')


def decode(row: dict) -> np.ndarray:
    return np.asarray(Image.open(io.BytesIO(base64.b64decode(row['mask']))), np.int16)


class ContactCompare(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stored = json.loads((ROOT / 'data/visual/site7_contact_shadows.json').read_text(encoding='utf-8'))
        cls.asset = sorted(cls.stored['plates'])[0]

    def fresh(self, mutate=None):
        data = copy.deepcopy(self.stored)
        if mutate:
            mutate(data)
        return data

    def nudged(self, delta: int):
        """A copy whose middle pixel of the first plate moved by `delta` steps (towards the mid range)."""
        def mutate(data):
            row = data['plates'][self.asset]
            pixels = decode(row).copy()
            y, x = pixels.shape[0] // 2, pixels.shape[1] // 2
            pixels[y, x] += delta if pixels[y, x] + delta <= 255 else -delta
            row['mask'] = encode(pixels)
        return self.fresh(mutate)

    def test_shipped_data_matches_itself(self):
        self.assertTrue(tool.same_contacts(self.stored, self.fresh()))

    def test_another_png_encoding_of_the_same_pixels_passes(self):
        def mutate(data):
            row = data['plates'][self.asset]
            row['mask'] = encode(decode(row), level=0)
        fresh = self.fresh(mutate)
        self.assertNotEqual(fresh['plates'][self.asset]['mask'], self.stored['plates'][self.asset]['mask'])
        self.assertTrue(tool.same_contacts(self.stored, fresh))

    def test_one_step_of_rounding_passes_two_steps_fail(self):
        self.assertTrue(tool.same_contacts(self.stored, self.nudged(1)))
        self.assertFalse(tool.same_contacts(self.stored, self.nudged(2)))

    def test_a_missing_or_extra_plate_fails(self):
        self.assertFalse(tool.same_contacts(self.stored, self.fresh(lambda d: d['plates'].pop(self.asset))))
        self.assertFalse(tool.same_contacts(self.stored, self.fresh(
            lambda d: d['plates'].__setitem__('assets/extra.png', d['plates'][self.asset]))))

    def test_padding_scale_size_and_schema_changes_fail(self):
        self.assertFalse(tool.same_contacts(self.stored, self.fresh(
            lambda d: d['plates'][self.asset].__setitem__('padding_px', d['plates'][self.asset]['padding_px'] - 1))))
        self.assertFalse(tool.same_contacts(self.stored, self.fresh(
            lambda d: d['plates'][self.asset].__setitem__('scale', 0.5))))
        self.assertFalse(tool.same_contacts(self.stored, self.fresh(
            lambda d: d['plates'][self.asset].__setitem__('mask', encode(decode(d['plates'][self.asset])[:-1])))))
        self.assertFalse(tool.same_contacts(self.stored, self.fresh(lambda d: d.__setitem__('schema', 2))))


class VoidFill(unittest.TestCase):
    """`outer_void` (the abyss row's `void_fill_px`) and the operation 10 masks built with it."""

    @staticmethod
    def plate(channel: int = 4) -> np.ndarray:
        """A 140 x 220 plate: void all round a 140 x 80 opaque wall, and inside the wall an 80 x 40 px dark recess
        that a horizontal channel `channel` px tall joins to the outside (what the border-connected rule calls void)."""
        void = np.ones((140, 220), bool)
        void[30:110, 40:180] = False
        void[50:90, 70:150] = True
        void[70 - channel // 2:70 + channel // 2, 40:70] = True
        return void

    def test_a_recess_joined_by_a_narrow_channel_is_not_void(self):
        kept = tool.outer_void(self.plate(), 8.0)
        self.assertFalse(kept[70, 110], 'the recess is see-through')
        self.assertFalse(kept[70, 55], 'the channel is see-through')
        self.assertTrue(kept[5, 5] and kept[70, 20], 'the outer void was dropped')

    def test_a_passage_wider_than_twice_the_radius_keeps_its_void(self):
        self.assertTrue(tool.outer_void(self.plate(channel=24), 8.0)[70, 110])

    def test_no_fill_is_the_plain_rule(self):
        void = self.plate()
        self.assertTrue(tool.outer_void(void, 0.0)[70, 110], 'negative control: without the fill the recess is void')
        self.assertTrue(np.array_equal(tool.outer_void(void, 0.0), void))

    def test_the_image_border_never_erodes_the_void(self):
        kept = tool.outer_void(self.plate(), 8.0)
        self.assertTrue(kept[0, :].all() and kept[-1, :].all() and kept[:, 0].all() and kept[:, -1].all())

    @classmethod
    def setUpClass(cls):
        cls.masks = json.loads((ROOT / 'data/visual/site7_void_masks.json').read_text(encoding='utf-8'))['plates']
        cls.art = json.loads((ROOT / 'data/visual/site7_battle_art.json').read_text(encoding='utf-8'))['missions']
        cls.mood = json.loads((ROOT / 'data/visual/site7_mood.json').read_text(encoding='utf-8'))['missions']

    def removed_shares(self, mission: str, fill: float) -> list:
        """Per plate, the share of its stored void (kept at VOID_SCALE of the plate) that the fill would still remove."""
        shares = []
        for plate in self.art[mission]['rooms'] + self.art[mission]['connectors']:
            image = Image.open(io.BytesIO(base64.b64decode(self.masks[plate['asset']]))).convert('L')
            void = np.asarray(image) >= 128
            kept = tool.outer_void(void, fill * tool.VOID_SCALE)
            shares.append(float((void & ~kept).sum()) / float(void.sum()))
        return shares

    def test_operation_10_masks_hold_no_narrow_pockets(self):
        fill = float(self.mood['MIS_CH01_10']['abyss'].get('void_fill_px', 0.0))
        self.assertGreaterEqual(fill, 20.0, 'operation 10 lost its void_fill_px')
        shares = self.removed_shares('MIS_CH01_10', fill)
        self.assertEqual(len(shares), 15)
        self.assertLess(max(shares), 0.002, shares)

    def test_a_mission_without_the_fill_still_has_them(self):
        # Negative control: operation 5's masks follow the plain rule and hold the dark wall recesses the fill removes.
        shares = self.removed_shares('MIS_CH01_05', 28.0)
        self.assertGreater(sum(shares) / len(shares), 0.02, shares)


class NullAbyssLit(unittest.TestCase):
    """Operation 10's `null` abyss must not read black (user, 2026-10-02: almost black, and no black background)."""
    # The row it shipped with until then; measured 0.025 mean luma over the visible void (lit row 0.124), operations 1-7
    # and 9 0.062-0.107, operation 8's dawn sea 0.175.
    BLACK_ROW = {'style': 'null', 'base': [0.012, 0.014, 0.02], 'fog': [0.022, 0.028, 0.038], 'fog_strength': 0.1,
                 'haze_strength': 0.045}

    @staticmethod
    def luma(rgb) -> float:
        return 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]

    def lift(self, row: dict) -> float:
        """Luma of the row's own colour in an average fog bank: its base plus 0.3 of the fog it brings."""
        return self.luma(row['base']) + 0.3 * float(row['fog_strength']) * self.luma(row['fog'])

    def lit(self, row: dict) -> bool:
        return self.lift(row) >= 0.06 and float(row['fog_strength']) >= 0.5 and float(row['haze_strength']) >= 0.08

    def test_operation_10_abyss_is_lit(self):
        row = json.loads((ROOT / 'data/visual/site7_mood.json').read_text(encoding='utf-8'))['missions']['MIS_CH01_10']['abyss']
        self.assertEqual(row['style'], 'null')
        self.assertTrue(self.lit(row), (self.lift(row), row['fog_strength'], row['haze_strength']))

    def test_the_near_black_row_is_rejected(self):
        self.assertFalse(self.lit(self.BLACK_ROW))
        self.assertLess(self.lift(self.BLACK_ROW), 0.03)


if __name__ == '__main__':
    unittest.main()
