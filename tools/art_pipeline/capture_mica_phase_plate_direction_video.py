#!/usr/bin/env python3
"""Capture one phase-plate gait direction on native 1080p review canvases.

The fixed view exposes the exact runtime frame cadence.  The world-grid view
uses the declared UAL contact state and the visible sole landmark to lock the
active support foot along the travel axis.  This is review evidence only; it
does not promote or rewrite runtime assets.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import av
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage


ROOT = Path(__file__).resolve().parents[2]
WIDTH, HEIGHT = 1920, 1080
CELL, FPS, FRAME_COUNT = 384, 24, 120
UNITS = {
    "E": (1.0, 0.0),
    "SE": (math.sqrt(0.5), math.sqrt(0.5)),
    "S": (0.0, 1.0),
    "SW": (-math.sqrt(0.5), math.sqrt(0.5)),
    "W": (-1.0, 0.0),
    "NW": (-math.sqrt(0.5), -math.sqrt(0.5)),
    "N": (0.0, -1.0),
    "NE": (math.sqrt(0.5), -math.sqrt(0.5)),
}


def project_path(value: Path) -> Path:
    path = (value if value.is_absolute() else ROOT / value).resolve()
    try:
        path.relative_to(ROOT)
    except ValueError as exc:
        raise SystemExit(f"project-local path required: {path}") from exc
    return path


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    path = Path("C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf")
    return ImageFont.truetype(path, size) if path.is_file() else ImageFont.load_default()


def sole_point(frame: Image.Image) -> tuple[float, float]:
    """Find one visible boot sole in a single isolated lower plate.

    The bottom-most two raster rows are the authored outsole/toe contact band.
    Including a third row pulled a different calf/heel silhouette into the
    centroid when the boot translated, which made a planted foot appear to
    drift even though its actual outsole translated by the declared root
    step.  Keep the marker tied to the stable contact band.
    """
    alpha = np.asarray(frame.getchannel("A")) > 24
    lower = np.zeros_like(alpha)
    lower[278:] = alpha[278:]
    labels, count = ndimage.label(lower)
    components: list[tuple[int, float, float]] = []
    for label in range(1, count + 1):
        ys, xs = np.where(labels == label)
        if xs.size < 20:
            continue
        bottom = int(ys.max())
        band = xs[ys >= bottom - 1]
        components.append((int(xs.size), float(band.mean()), float(bottom)))
    if not components:
        raise SystemExit("could not isolate a visible boot component in isolated lower plate")
    _size, x, bottom = max(components, key=lambda item: item[0])
    return (x, bottom)


def sole_points(
    frame: Image.Image,
    isolated_components: dict[str, Image.Image] | None = None,
) -> dict[str, tuple[float, float]]:
    # The merged composite is ordered by screen X, which is not the same as
    # the logical left/right leg on diagonal views when the feet cross.  When
    # Blender has emitted named per-leg plates, preserve that ownership first
    # so support markers follow the manifest's screen_left/screen_right state.
    if isolated_components is not None and set(isolated_components) == {"left", "right"}:
        return {
            "left": sole_point(isolated_components["left"]),
            "right": sole_point(isolated_components["right"]),
        }
    alpha = np.asarray(frame.getchannel("A")) > 24
    lower = np.zeros_like(alpha)
    lower[278:] = alpha[278:]
    labels, count = ndimage.label(lower)
    components: list[tuple[int, float, float]] = []
    for label in range(1, count + 1):
        ys, xs = np.where(labels == label)
        if xs.size < 80:
            continue
        bottom = int(ys.max())
        band = xs[ys >= bottom - 2]
        components.append((int(xs.size), float(band.mean()), float(bottom)))
    components.sort(reverse=True)
    if len(components) < 2:
        # Side-view source art can place the two authored boots in one connected
        # raster component.  In that case, use the immutable per-leg Blender
        # plate renders rather than guessing two soles from the merged image.
        if isolated_components is not None and set(isolated_components) == {"left", "right"}:
            return {
                "left": sole_point(isolated_components["left"]),
                "right": sole_point(isolated_components["right"]),
            }
        raise SystemExit("could not isolate two visible boot components in lower runtime cell")
    boots = sorted(components[:2], key=lambda item: item[1])
    return {"left": (boots[0][1], boots[0][2]), "right": (boots[1][1], boots[1][2])}


def contact_state(record: dict) -> dict[str, bool]:
    contacts = record.get("ual_contacts")
    if isinstance(contacts, dict):
        return {"left": bool(contacts.get("left")), "right": bool(contacts.get("right"))}
    legs = record.get("legs", {})
    if isinstance(legs, dict):
        return {
            "left": bool(legs.get("screen_left", {}).get("planted")),
            "right": bool(legs.get("screen_right", {}).get("planted")),
        }
    return {"left": False, "right": False}


def support_side(record: dict) -> str:
    phase = str(record.get("phase_key", ""))
    contacts = contact_state(record)
    left, right = bool(contacts.get("left")), bool(contacts.get("right"))
    if left and not right:
        return "left"
    if right and not left:
        return "right"
    if "before_right" in phase:
        return "left"
    if "before_left" in phase:
        return "right"
    if phase.startswith("right_"):
        return "right"
    if left and right:
        return "left" if int(record.get("index", 0)) < 12 else "right"
    return "left"


def plan_raster_cadence_origins(
    roots: list[np.ndarray],
    unit: np.ndarray,
    target_step: float,
    support_sides: list[str] | None = None,
) -> list[np.ndarray]:
    """Plan integer paste origins without raster stalls or catch-up jumps.

    The runtime root is intentionally kept as a float so the support sole can
    remain locked on the travel axis.  The review canvas, however, pastes a
    384px cell at an integer origin.  Naively rounding each root independently
    creates duplicate frames and occasional three-pixel diagonal jumps.  This
    small dynamic-programming pass chooses a nearby integer lattice point for
    each frame, constraining travel-axis error to <=0.75px, keeping each
    contiguous support window within a 1px travel-axis band, forbidding a
    duplicate origin, and capping a single raster transition at sqrt(8)px.
    The chosen path is only a review-capture rasterization; it never rewrites
    Blender/UAL source cells or the float runtime track.
    """
    if not roots:
        return []
    max_transition = max(math.sqrt(8.0) + 1e-6, float(target_step) * 1.75)
    candidates: list[list[tuple[tuple[int, int], float, float]]]=[]
    for root in roots:
        center_x, center_y = int(round(float(root[0]))), int(round(float(root[1])))
        frame_candidates: list[tuple[tuple[int, int], float, float]] = []
        for x in range(center_x - 3, center_x + 4):
            for y in range(center_y - 3, center_y + 4):
                point = np.array((float(x), float(y)), dtype=np.float64)
                error = point - root
                along_error = float(np.dot(error, unit))
                if abs(along_error) > 0.75:
                    continue
                frame_candidates.append(
                    ((x, y), float(np.linalg.norm(error)), along_error)
                )
        if not frame_candidates:
            raise SystemExit(
                "raster cadence lock could not find an integer origin within "
                "0.75px of the travel axis"
            )
        candidates.append(frame_candidates)

    if support_sides is None:
        support_sides = ["all"] * len(roots)
    if len(support_sides) != len(roots):
        raise SystemExit("raster cadence lock support sequence length mismatch")

    segments: list[tuple[int, int]] = []
    segment_start = 0
    for index in range(1, len(support_sides)):
        if support_sides[index] != support_sides[index - 1]:
            segments.append((segment_start, index - 1))
            segment_start = index
    segments.append((segment_start, len(support_sides) - 1))
    support_span_limit = 1.0

    def plan_segment(
        start: int,
        end: int,
        previous_key: tuple[int, int] | None,
        force_first: tuple[int, int] | None,
    ) -> list[tuple[int, int]] | None:
        best_segment: tuple[float, list[tuple[int, int]]] | None = None
        for first_key, first_error, first_along in candidates[start]:
            if force_first is not None and first_key != force_first:
                continue
            boundary_delta = 0.0
            if previous_key is not None:
                boundary_delta = math.dist(first_key, previous_key)
                if boundary_delta < 1e-6 or boundary_delta > max_transition:
                    continue
            # Try one-pixel travel-axis intervals that contain this segment's
            # first candidate.  This keeps the active support sole within a
            # bounded band while allowing lateral integer dithering.
            for fraction in np.linspace(0.0, 1.0, 41):
                low = first_along - support_span_limit * fraction
                high = low + support_span_limit
                states: list[
                    dict[tuple[int, int], tuple[float, tuple[int, int] | None]]
                ] = [
                    {
                        first_key: (
                            first_error
                            + abs(first_along - (low + high) / 2.0)
                            + (
                                0.08 * abs(boundary_delta - float(target_step))
                                if previous_key is not None
                                else 0.0
                            ),
                            previous_key,
                        )
                    }
                ]
                for index in range(start + 1, end + 1):
                    next_states: dict[
                        tuple[int, int], tuple[float, tuple[int, int] | None]
                    ] = {}
                    for key, error, along_error in candidates[index]:
                        if along_error < low - 1e-9 or along_error > high + 1e-9:
                            continue
                        point = np.array(key, dtype=np.float64)
                        best: tuple[float, tuple[int, int]] | None = None
                        for previous, (previous_cost, _predecessor) in states[-1].items():
                            transition = float(
                                np.linalg.norm(point - np.array(previous, dtype=np.float64))
                            )
                            if transition < 1e-6 or transition > max_transition:
                                continue
                            cost = (
                                previous_cost
                                + error
                                + abs(along_error - (low + high) / 2.0)
                                + 0.08 * abs(transition - float(target_step))
                            )
                            if best is None or cost < best[0]:
                                best = (cost, previous)
                        if best is not None:
                            next_states[key] = best
                    if not next_states:
                        break
                    states.append(next_states)
                if len(states) != end - start + 1:
                    continue
                current_key = min(states[-1], key=lambda key: states[-1][key][0])
                path: list[tuple[int, int]] = [current_key]
                for index in range(len(states) - 1, 0, -1):
                    predecessor = states[index][path[-1]][1]
                    if predecessor is None:
                        raise SystemExit(
                            "raster cadence lock backtrace lost a predecessor"
                        )
                    path.append(predecessor)
                path.reverse()
                cost = states[-1][current_key][0]
                if best_segment is None or cost < best_segment[0]:
                    best_segment = (cost, path)
        return None if best_segment is None else best_segment[1]

    planned: list[tuple[int, int]] = []
    previous_key: tuple[int, int] | None = None
    initial_key = (int(round(float(roots[0][0]))), int(round(float(roots[0][1]))))
    for segment_index, (start, end) in enumerate(segments):
        segment = plan_segment(
            start,
            end,
            previous_key,
            initial_key if segment_index == 0 else None,
        )
        if segment is None:
            raise SystemExit(
                f"raster cadence lock has no safe integer path for frames {start}..{end}"
            )
        planned.extend(segment)
        previous_key = planned[-1]
    return [np.array(key, dtype=np.float64) for key in planned]


def draw_grid(draw: ImageDraw.ImageDraw) -> None:
    for x in range(0, WIDTH + 1, 64):
        draw.line((x, 78, x, HEIGHT), fill="#173242", width=1)
    for y in range(78, HEIGHT + 1, 64):
        draw.line((0, y, WIDTH, y), fill="#173242", width=1)
    for x in range(0, WIDTH + 1, 256):
        draw.line((x, 78, x, HEIGHT), fill="#255166", width=2)
    for y in range(78, HEIGHT + 1, 256):
        draw.line((0, y, WIDTH, y), fill="#255166", width=2)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--render-manifest", type=Path, required=True)
    parser.add_argument("--direction", choices=tuple(UNITS), required=True)
    parser.add_argument("--mode", choices=("fixed-grid", "world-grid"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--step-advance", type=float, default=12.0)
    parser.add_argument(
        "--base-x",
        type=float,
        default=(WIDTH - CELL) / 2.0,
        help="Initial runtime-cell X origin on the 1920x1080 review canvas.",
    )
    parser.add_argument(
        "--base-y",
        type=float,
        default=390.0,
        help="Initial runtime-cell Y origin on the 1920x1080 review canvas.",
    )
    parser.add_argument(
        "--continuous-root-step",
        type=float,
        default=0.0,
        help="Advance the actor root by this many runtime pixels every output frame; use with internally stance-compensated cells.",
    )
    parser.add_argument(
        "--sole-lock-feedback",
        action="store_true",
        help="Apply a travel-axis feedback correction so the declared support sole remains fixed while the nominal root advances continuously.",
    )
    parser.add_argument(
        "--runtime-sole-lock",
        action="store_true",
        help="Use a continuous runtime root track with per-support ground anchors; this is the production-root/stance integration path, not capture-only feedback.",
    )
    parser.add_argument(
        "--raster-cadence-lock",
        action="store_true",
        help="Plan integer review paste origins from the float root so decoded frames have no raster zero-step/catch-up pulse; review capture only.",
    )
    parser.add_argument(
        "--subpixel-root-translation",
        action="store_true",
        help="Apply the float residual inside the selected integer paste cell so the visible actor follows the continuous root without quantization stalls; review capture only.",
    )
    parser.add_argument(
        "--runtime-track-output",
        type=Path,
        default=None,
        help="Optional project-local JSON path for the runtime root/sole-lock track generated with --runtime-sole-lock.",
    )
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    if args.runtime_sole_lock and args.sole_lock_feedback:
        raise SystemExit("--runtime-sole-lock and --sole-lock-feedback are mutually exclusive")
    if args.raster_cadence_lock and not args.runtime_sole_lock:
        raise SystemExit("--raster-cadence-lock requires --runtime-sole-lock")
    if args.subpixel_root_translation and not args.raster_cadence_lock:
        raise SystemExit("--subpixel-root-translation requires --raster-cadence-lock")

    candidate = project_path(args.candidate)
    manifest_path = project_path(args.render_manifest)
    output = project_path(args.output)
    if args.runtime_track_output is not None:
        args.runtime_track_output = project_path(args.runtime_track_output)
    if output.exists() and not args.overwrite:
        raise SystemExit(f"refusing to overwrite existing video: {output}")
    if output.exists():
        output.unlink()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    records = manifest["frames"]
    if len(records) != 24:
        raise SystemExit(f"expected 24 manifest frames, got {len(records)}")

    frames: list[Image.Image] = []
    points: list[dict[str, tuple[float, float]]] = []
    for index in range(24):
        path = candidate / "blender_frames" / args.direction / "move" / f"{index:02d}.png"
        opened = Image.open(path).convert("RGBA")
        if opened.size != (CELL, CELL):
            raise SystemExit(f"invalid runtime cell: {path} {opened.size}")
        frames.append(opened)
        component_root = candidate / "blender_components" / args.direction / "move"
        # Logical leg ownership must survive diagonal crossings as well as
        # side-view boot contact.  Prefer the named Blender plates whenever
        # they are present; only older candidates without component renders
        # fall back to screen-space component ordering.
        isolated_paths = {
            "left": component_root / f"{index:02d}_screen_left.png",
            "right": component_root / f"{index:02d}_screen_right.png",
        }
        if all(path.is_file() for path in isolated_paths.values()):
            isolated = {
                name: Image.open(path).convert("RGBA")
                for name, path in isolated_paths.items()
            }
            try:
                points.append(sole_points(opened, isolated_components=isolated))
            finally:
                isolated["left"].close()
                isolated["right"].close()
        else:
            points.append(sole_points(opened))

    unit = np.array(UNITS[args.direction], dtype=np.float64)
    base = np.array((args.base_x, args.base_y), dtype=np.float64)
    along_base = float(np.dot(base, unit))
    anchors: dict[str, float] = {}
    last_support: str | None = None
    root_positions: list[tuple[float, float]] = []
    for index, record in enumerate(records):
        side = support_side(record)
        local = np.array(points[index][side], dtype=np.float64)
        if side not in anchors:
            if last_support is None:
                anchors[side] = float(np.dot(base + local, unit))
            else:
                anchors[side] = anchors[last_support] + args.step_advance
        elif last_support is not None and side != last_support:
            anchors[side] = anchors[last_support] + args.step_advance
        target_along = anchors[side] - float(np.dot(local, unit))
        root = base + unit * (target_along - along_base)
        root_positions.append((float(root[0]), float(root[1])))
        last_support = side
    wrap_switch = support_side(records[-1]) != support_side(records[0])
    support_switches = sum(
        support_side(records[index]) != support_side(records[index - 1])
        for index in range(1, len(records))
    ) + int(wrap_switch)
    cycle_advance = args.step_advance * support_switches

    # A diagonal projection has a larger left/right sole separation along its
    # travel axis.  The old anchor splice could therefore teleport the whole
    # upper body at F11->F12 (and again at the cycle wrap) even though every
    # source cell was correct.  Refuse that unsafe evidence path unless the
    # caller explicitly selects continuous per-frame root motion.
    anchor_roots = [np.asarray(item, dtype=np.float64) for item in root_positions]
    anchor_frame_deltas = [
        float(np.linalg.norm(anchor_roots[index] - anchor_roots[index - 1]))
        for index in range(1, len(anchor_roots))
    ]
    anchor_wrap_delta = float(
        np.linalg.norm(anchor_roots[0] + unit * cycle_advance - anchor_roots[-1])
    )
    diagonal_directions = {"SE", "SW", "NW", "NE"}
    if (
        args.mode == "world-grid"
        and args.direction in diagonal_directions
        and args.continuous_root_step <= 0.0
        and max(anchor_frame_deltas + [anchor_wrap_delta]) > 4.0
    ):
        raise SystemExit(
            "diagonal world-grid anchor splice is discontinuous "
            f"(max transition {max(anchor_frame_deltas + [anchor_wrap_delta]):.2f}px); "
            "rerun with --continuous-root-step"
        )

    rendered_roots: list[np.ndarray] = []
    for number in range(FRAME_COUNT):
        if args.mode != "world-grid":
            rendered_roots.append(base.copy())
        elif args.continuous_root_step > 0.0:
            rendered_roots.append(base + unit * (number * args.continuous_root_step))
        else:
            rendered_roots.append(
                anchor_roots[number % 24]
                + unit * ((number // 24) * cycle_advance)
            )

    # Production root/stance integration: preserve the active support sole
    # against a declared ground anchor while keeping a non-zero nominal root
    # advance at every support handoff.  Unlike the review-only feedback mode,
    # this track is deterministic from the authored Blender component cells
    # and is recorded as the runtime integration path in the capture payload.
    runtime_sole_lock = bool(
        args.mode == "world-grid"
        and args.continuous_root_step > 0.0
        and args.runtime_sole_lock
    )
    if runtime_sole_lock:
        support_sequence: list[str] = []
        support_first_index: dict[str, int] = {}
        previous_side: str | None = None
        for index in range(24):
            side = support_side(records[index])
            if side != previous_side:
                support_sequence.append(side)
                support_first_index.setdefault(side, index)
                previous_side = side
        if not support_sequence:
            raise SystemExit("runtime sole lock requires at least one UAL support window")
        runtime_roots: list[np.ndarray] = []
        runtime_ground_anchors: list[float] = []
        previous_side = None
        current_offset = 0.0
        previous_root: np.ndarray | None = None
        windows_per_cycle = len(support_sequence)
        for number in range(FRAME_COUNT):
            index = number % 24
            side = support_side(records[index])
            cycle = number // 24
            side_rank = support_sequence.index(side)
            local = np.asarray(points[index][side], dtype=np.float64)
            first_local = np.asarray(
                points[support_first_index[side]][side], dtype=np.float64
            )
            ground_anchor = float(
                np.dot(base + first_local, unit)
                + (cycle * windows_per_cycle + side_rank) * args.step_advance
            )
            lock_root = base + unit * (
                ground_anchor - float(np.dot(base, unit)) - float(np.dot(local, unit))
            )
            if previous_root is None:
                current_offset = 0.0
            elif side != previous_side:
                # Keep the root moving at the declared cadence through the
                # F11→F12/F23→F00 handoff instead of resetting it to zero.
                current_offset = float(
                    np.dot(
                        previous_root + unit * args.continuous_root_step - lock_root,
                        unit,
                    )
                )
            root = lock_root + unit * current_offset
            runtime_roots.append(root)
            runtime_ground_anchors.append(ground_anchor)
            previous_root = root
            previous_side = side
        rendered_roots = runtime_roots

    # A continuous nominal root step and a rasterized lower plate do not
    # necessarily cancel to sub-pixel support drift.  When requested, keep
    # the nominal travel cadence but solve a small travel-axis correction from
    # the actual isolated sole for the active UAL support side.  The correction
    # is reset only at a support handoff and is anchored to the previous actual
    # root, so the upper body remains continuous and the incoming foot never
    # teleports.  This is review-capture feedback; it does not alter runtime
    # source cells or the Blender render manifest.
    sole_lock_feedback = bool(
        args.mode == "world-grid"
        and args.continuous_root_step > 0.0
        and args.sole_lock_feedback
    )
    if sole_lock_feedback:
        feedback_roots: list[np.ndarray] = []
        support_anchor: float | None = None
        previous_side: str | None = None
        for number in range(FRAME_COUNT):
            index = number % 24
            side = support_side(records[index])
            nominal = base + unit * (number * args.continuous_root_step)
            local = np.asarray(points[index][side], dtype=np.float64)
            if support_anchor is None:
                support_anchor = float(np.dot(nominal + local, unit))
            elif side != previous_side:
                previous_root = feedback_roots[-1]
                support_anchor = float(np.dot(previous_root + local, unit))
            correction = support_anchor - float(np.dot(nominal + local, unit))
            feedback_roots.append(nominal + unit * correction)
            previous_side = side
        rendered_roots = feedback_roots
    raster_origins: list[np.ndarray] | None = None
    raster_root_deltas: list[float] = []
    raster_support_axis_drift: dict[str, float] = {}
    if args.raster_cadence_lock:
        raster_origins = plan_raster_cadence_origins(
            rendered_roots,
            unit,
            args.continuous_root_step,
            [support_side(records[number % 24]) for number in range(FRAME_COUNT)],
        )
        raster_root_deltas = [
            float(np.linalg.norm(raster_origins[index] - raster_origins[index - 1]))
            for index in range(1, len(raster_origins))
        ]
        for support_name in ("left", "right"):
            samples = [
                float(
                    np.dot(
                        raster_origins[index]
                        + np.asarray(points[index][support_name], dtype=np.float64),
                        unit,
                    )
                )
                for index in range(24)
                if support_side(records[index]) == support_name
            ]
            if samples:
                raster_support_axis_drift[support_name] = max(samples) - min(samples)
    rendered_root_deltas = [
        float(np.linalg.norm(rendered_roots[index] - rendered_roots[index - 1]))
        for index in range(1, len(rendered_roots))
    ]
    rendered_root_max_delta = max(rendered_root_deltas, default=0.0)
    support_axis_drift: dict[str, float] = {}
    for support_name in ("left", "right"):
        samples = [
            float(
                np.dot(
                    rendered_roots[index] + np.asarray(points[index][support_name], dtype=np.float64),
                    unit,
                )
            )
            for index in range(24)
            if support_side(records[index]) == support_name
        ]
        if samples:
            support_axis_drift[support_name] = max(samples) - min(samples)

    output.parent.mkdir(parents=True, exist_ok=True)
    if runtime_sole_lock and args.runtime_track_output is not None:
        track_path = project_path(args.runtime_track_output)
        track_path.parent.mkdir(parents=True, exist_ok=True)
        track = {
            "schema": 1,
            "role": "MICA runtime continuous root/stance sole-lock integration track",
            "candidate": candidate.relative_to(ROOT).as_posix(),
            "render_manifest": manifest_path.relative_to(ROOT).as_posix(),
            "direction": args.direction,
            "source_art_modified": False,
            "trajectory_mode": "runtime_continuous_sole_lock",
            "continuous_root_step_px": args.continuous_root_step,
            "step_advance_px": args.step_advance,
            "frame_count": FRAME_COUNT,
            "support_sole_axis_drift_px": support_axis_drift,
            "root_transition_min_px": min(rendered_root_deltas, default=0.0),
            "root_transition_max_px": max(rendered_root_deltas, default=0.0),
            "root_zero_step_count": sum(
                delta < 1e-6 for delta in rendered_root_deltas
            ),
            "raster_cadence_lock": bool(args.raster_cadence_lock),
            "raster_support_sole_axis_drift_px": raster_support_axis_drift,
            "raster_root_transition_min_px": min(raster_root_deltas, default=0.0),
            "raster_root_transition_max_px": max(raster_root_deltas, default=0.0),
            "raster_root_zero_step_count": sum(
                delta < 1e-6 for delta in raster_root_deltas
            ),
            "subpixel_root_translation": bool(args.subpixel_root_translation),
            "subpixel_residual_max_px": max(
                (float(np.linalg.norm(rendered_roots[index] - raster_origins[index]))
                 for index in range(len(rendered_roots)))
                if raster_origins is not None
                else 0.0,
                default=0.0,
            ),
            "frames": [
                {
                    "frame": number,
                    "source_index": number % 24,
                    "support": support_side(records[number % 24]),
                    "ground_anchor_axis_px": round(runtime_ground_anchors[number], 6),
                    "root_xy_px": [
                        round(float(rendered_roots[number][0]), 6),
                        round(float(rendered_roots[number][1]), 6),
                    ],
                    "raster_root_xy_px": (
                        [
                            int(round(float(raster_origins[number][0]))),
                            int(round(float(raster_origins[number][1]))),
                        ]
                        if raster_origins is not None
                        else None
                    ),
                }
                for number in range(FRAME_COUNT)
            ],
        }
        track_path.write_text(json.dumps(track, indent=2) + "\n", encoding="utf-8")
    container = av.open(str(output), mode="w")
    stream = container.add_stream("libx264", rate=FPS)
    stream.width, stream.height, stream.pix_fmt = WIDTH, HEIGHT, "yuv420p"
    stream.options = {"crf": "18", "preset": "medium", "movflags": "+faststart"}
    title_font, label_font, small_font = font(30, True), font(20, True), font(16)
    try:
        for number in range(FRAME_COUNT):
            index = number % 24
            record = records[index]
            side = support_side(record)
            canvas = Image.new("RGB", (WIDTH, HEIGHT), "#071019")
            draw = ImageDraw.Draw(canvas)
            draw_grid(draw)
            draw.rectangle((0, 0, WIDTH, 78), fill="#0b1722")
            mode_label = "STANCE-SOLE WORLD LOCK" if args.mode == "world-grid" else "FIXED RUNTIME CELL"
            draw.text((48, 19), f"{args.title} | {args.direction} | {mode_label}", fill="#e7f7ff", font=title_font)
            if args.mode == "world-grid":
                if args.continuous_root_step > 0.0:
                    translated = (
                        rendered_roots[number]
                        if sole_lock_feedback or runtime_sole_lock
                        else base + unit * (number * args.continuous_root_step)
                    )
                else:
                    completed_cycles = number // 24
                    relative = np.array(root_positions[index], dtype=np.float64)
                    translated = relative + unit * (completed_cycles * cycle_advance)
                origin = (float(translated[0]), float(translated[1]))
            else:
                origin = (float(base[0]), float(base[1]))
            paste_origin = np.array(origin, dtype=np.float64)
            if raster_origins is not None:
                paste_origin = raster_origins[number]
                if args.subpixel_root_translation:
                    # Keep the marker on the true float root while the image
                    # is pasted at the planned integer lattice point.  The
                    # fractional residual is applied below via a transparent
                    # bilinear translate, so visible support lock is not
                    # replaced by a rounded-origin approximation.
                    origin = (
                        float(rendered_roots[number][0]),
                        float(rendered_roots[number][1]),
                    )
                else:
                    origin = (
                        float(paste_origin[0]),
                        float(paste_origin[1]),
                    )
            paste_xy = (round(float(paste_origin[0])), round(float(paste_origin[1])))
            frame_to_paste = frames[index]
            translated_frame: Image.Image | None = None
            if raster_origins is not None and args.subpixel_root_translation:
                residual_x = float(rendered_roots[number][0] - paste_origin[0])
                residual_y = float(rendered_roots[number][1] - paste_origin[1])
                translated_frame = frame_to_paste.transform(
                    (CELL, CELL),
                    Image.Transform.AFFINE,
                    (1.0, 0.0, -residual_x, 0.0, 1.0, -residual_y),
                    resample=Image.Resampling.BILINEAR,
                    fillcolor=(0, 0, 0, 0),
                )
                frame_to_paste = translated_frame
            canvas.paste(frame_to_paste, paste_xy, frame_to_paste)
            if translated_frame is not None:
                translated_frame.close()
            sole = points[index][side]
            sx, sy = origin[0] + sole[0], origin[1] + sole[1]
            draw.ellipse((sx - 7, sy - 7, sx + 7, sy + 7), outline="#ffce4b", width=3)
            draw.line((sx - 18, sy, sx + 18, sy), fill="#ffce4b", width=2)
            phase = str(record.get("phase_key") or f"ual_phase_{float(record.get('phase', 0.0)):.3f}")
            contacts = contact_state(record)
            draw.rounded_rectangle((45, 855, 1040, 1018), radius=12, fill="#0b1722", outline="#33556b", width=2)
            draw.text((72, 878), f"FRAME {index:02d}/23  •  PHASE {phase}", fill="#83ddff", font=label_font)
            draw.text((72, 918), f"CONTACT L={bool(contacts.get('left'))} R={bool(contacts.get('right'))}  •  ACTIVE SUPPORT={side.upper()}", fill="#f5d77b", font=label_font)
            draw.text((72, 960), f"ROOT [{origin[0]:.1f}, {origin[1]:.1f}]  •  SUPPORT SOLE [{sx:.1f}, {sy:.1f}]", fill="#a6bac7", font=small_font)
            capture_note = (
                "Native 1920×1080 • actual 384×384 runtime cells • subpixel root translation • yellow marker is review overlay"
                if args.subpixel_root_translation
                else "Native 1920×1080 • actual 384×384 runtime cells • no sprite upscale/interpolation • yellow marker is review overlay"
            )
            draw.text((48, 1045), capture_note, fill="#a6bac7", font=small_font)
            video_frame = av.VideoFrame.from_image(canvas)
            for packet in stream.encode(video_frame):
                container.mux(packet)
        for packet in stream.encode():
            container.mux(packet)
    finally:
        container.close()
        for frame in frames:
            frame.close()

    check = av.open(str(output))
    video = check.streams.video[0]
    decoded = sum(1 for _ in check.decode(video))
    payload = {
        "gate": "PASS_CONTAINER_ONLY" if decoded == FRAME_COUNT else "FAIL",
        "quality_claim": False,
        "path": output.relative_to(ROOT).as_posix(),
        "mode": args.mode,
        "resolution": [video.codec_context.width, video.codec_context.height],
        "fps": float(video.average_rate),
        "decoded_frames": decoded,
        "duration_seconds": decoded / FPS,
        "stance_sole_lock_axis_only": args.mode == "world-grid",
        "world_cycle_advance_px": (
            float(np.dot(rendered_roots[24] - rendered_roots[0], unit))
            if args.mode == "world-grid"
            and args.continuous_root_step > 0.0
            and len(rendered_roots) > 24
            and (sole_lock_feedback or runtime_sole_lock)
            else args.continuous_root_step * 24.0
            if args.mode == "world-grid" and args.continuous_root_step > 0.0
            else cycle_advance if args.mode == "world-grid" else 0.0
        ),
        "continuous_root_step_px": args.continuous_root_step if args.mode == "world-grid" else 0.0,
        "sole_lock_feedback": sole_lock_feedback,
        "runtime_sole_lock": runtime_sole_lock,
        "runtime_track_output": (
            args.runtime_track_output.relative_to(ROOT).as_posix()
            if runtime_sole_lock and args.runtime_track_output is not None
            else None
        ),
        "root_trajectory_mode": (
            "runtime_continuous_sole_lock"
            if runtime_sole_lock
            else "capture_feedback"
            if sole_lock_feedback
            else "nominal_continuous"
            if args.mode == "world-grid" and args.continuous_root_step > 0.0
            else "fixed_cell"
        ),
        "raster_cadence_lock": bool(args.raster_cadence_lock),
        "raster_root_transition_max_px": max(raster_root_deltas, default=0.0),
        "raster_root_transition_min_px": min(raster_root_deltas, default=0.0),
        "raster_root_zero_step_count": sum(
            delta < 1e-6 for delta in raster_root_deltas
        ),
        "raster_support_sole_axis_drift_px": raster_support_axis_drift,
        "subpixel_root_translation": bool(args.subpixel_root_translation),
        "subpixel_residual_max_px": max(
            (float(np.linalg.norm(rendered_roots[index] - raster_origins[index]))
             for index in range(len(rendered_roots)))
            if raster_origins is not None
            else 0.0,
            default=0.0,
        ),
        "support_sole_axis_drift_px": support_axis_drift,
        "world_root_transition_max_px": rendered_root_max_delta
        if args.mode == "world-grid"
        else 0.0,
        "world_root_transition_min_px": min(rendered_root_deltas, default=0.0)
        if args.mode == "world-grid"
        else 0.0,
        "world_root_zero_step_count": sum(
            delta < 1e-6 for delta in rendered_root_deltas
        )
        if args.mode == "world-grid"
        else 0,
        "anchor_wrap_delta_px": anchor_wrap_delta if args.mode == "world-grid" else 0.0,
        "base_origin_px": [float(args.base_x), float(args.base_y)],
    }
    check.close()
    print(json.dumps(payload, ensure_ascii=False))
    return 0 if decoded == FRAME_COUNT else 1


if __name__ == "__main__":
    raise SystemExit(main())
