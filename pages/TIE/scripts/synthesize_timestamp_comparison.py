#!/usr/bin/env python3
"""Synthesize a side-by-side timestamp comparison demo video.

The script reads the event timeline for a demo from index.html, places the TIE
and Seedance videos side by side, and draws a multi-lane event-duration bar
under each video with a moving playhead.
"""

from __future__ import annotations

import argparse
import html
import math
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TIE_VIDEO = ROOT / "static" / "videos" / "example1.mp4"
DEFAULT_SEEDANCE_VIDEO = ROOT / "static" / "videos" / "example1_seedance.mp4"
DEFAULT_OUTPUT = ROOT / "static" / "videos" / "timestamp_comparison_example1.mp4"
DEFAULT_INDEX = ROOT / "index.html"
DEFAULT_KEY_LABELS = {
    "example5": [
        (3.0, "player hits"),
        (5.5, "boss jumps back"),
        (7.75, "player goes back"),
    ],
    "example1": [
        (3.0, "the man raises his arm"),
        (7.0, "a train appears"),
        (8.5, "the man lowers hand"),
    ],
    "example3": [
        (4.3, "right arm stops"),
        (7.2, "left gripper closes"),
        (9.3, "right gripper opens"),
    ],
}
DEFAULT_KEY_TARGETS = {
    "example1": {
        "tie": [
            (3.0, 0.38, 0.28, 0.18, 0.42, True),
            (7.0, 0.0023,0.0150,0.4634,0.3580, True),
            (8.5, 0.38, 0.28, 0.18, 0.42, True),
        ],
        "seedance": [
            (3.0, 0.38, 0.28, 0.18, 0.42, False),
            (7.0, 0.0023,0.0150,0.4634,0.3580, True),
            (8.5, 0.38, 0.28, 0.18, 0.42, False),
        ],
    },
    "example3": {
        "tie": [
            (4.3, 0.4925,0.1736,0.4963,0.4219, True),
            (7.2, 0.2394,0.1944,0.3878,0.4801, True),
            (9.3, 0.5287,0.2035,0.3491,0.4568, True),
        ],
        "seedance": [
            (4.3, 0.4925,0.1736,0.4963,0.4219, True),
            (7.2, 0.2394,0.1944,0.3878,0.4801, False),
            (9.3, 0.5287,0.2035,0.3491,0.4568, False),
        ],
    },
    "example5": {
        "tie": [
            (3.0, 0.2572,0.1860,0.5091,0.5033, True),
            (5.5,0.2802,0.0249,0.4055,0.5631, True),
            (7.75,0.3695,0.3929,0.2428,0.4842, True),
        ],
        "seedance": [
            (3.0, 0.2730,0.2625,0.5409,0.5257, False),
            (5.5, 0.3740,0.0772,0.3399,0.484, False),
            (7.75, 0.1300,0.2915,0.4100,0.6985, True),
        ],
    },
}

CANVAS_BG = (248, 249, 251)
PANEL_BG = (255, 255, 255)
TEXT = (25, 31, 42)
MUTED = (92, 102, 118)
TRACK = (224, 229, 236)
PLAYHEAD = (10, 18, 32)
TIE_ACCENT = (29, 102, 219)
SEEDANCE_ACCENT = (225, 101, 39)
EVENT_COLORS = [
    (51, 112, 255),
    (34, 153, 84),
    (182, 94, 222),
    (222, 129, 38),
    (212, 66, 93),
    (32, 145, 160),
    (121, 110, 235),
    (94, 124, 32),
]
SUCCESS = (22, 163, 74)
FAILURE = (220, 38, 38)
KEY_BOX_PRE_WINDOW = 0.5
KEY_BOX_POST_WINDOW = 1.0


@dataclass(frozen=True)
class KeyTarget:
    time: float
    x: float
    y: float
    w: float
    h: float
    success: bool


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a TIE vs Seedance demo with timestamp event bars."
    )
    parser.add_argument("--demo-id", default="example1", help="Event timeline key in index.html.")
    parser.add_argument("--index", type=Path, default=DEFAULT_INDEX, help="HTML file containing eventTimelines.")
    parser.add_argument("--tie-video", type=Path, default=DEFAULT_TIE_VIDEO, help="TIE source video.")
    parser.add_argument(
        "--seedance-video",
        type=Path,
        default=DEFAULT_SEEDANCE_VIDEO,
        help="Seedance source video.",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output MP4 path.")
    parser.add_argument("--duration", type=float, default=10.0, help="Timeline duration in seconds.")
    parser.add_argument("--output-fps", type=float, default=30.0, help="Rendered comparison video FPS.")
    parser.add_argument("--tie-label-fps", type=float, default=16.0, help="FPS label for TIE.")
    parser.add_argument("--seedance-label-fps", type=float, default=20.0, help="FPS label for Seedance.")
    parser.add_argument(
        "--key-label",
        action="append",
        default=[],
        metavar="TIME:TEXT",
        help="Add a turning-point label, e.g. --key-label \"5.5:boss jumps back\". Can be repeated.",
    )
    parser.add_argument(
        "--no-default-key-labels",
        action="store_true",
        help="Disable built-in key labels for demos that define them.",
    )
    parser.add_argument(
        "--key-box",
        action="append",
        default=[],
        metavar="SIDE:TIME:X,Y,W,H:STATE",
        help=(
            "Add a key-component overlay box in normalized video coordinates. "
            "SIDE is tie, seedance, or both; STATE is success/fail. "
            "Example: --key-box \"tie:7.0:0.55,0.37,0.40,0.20:success\"."
        ),
    )
    parser.add_argument(
        "--no-default-key-boxes",
        action="store_true",
        help="Disable built-in key-component overlay boxes for demos that define them.",
    )
    parser.add_argument("--width", type=int, default=1920, help="Output width.")
    parser.add_argument("--height", type=int, default=1080, help="Output height.")
    return parser.parse_args()


def read_events(index_path: Path, demo_id: str) -> list[dict[str, float | str]]:
    source = index_path.read_text(encoding="utf-8")
    match = re.search(rf"{re.escape(demo_id)}\s*:\s*\[(.*?)\]\s*,\s*\w+\s*:", source, re.S)
    if not match:
        match = re.search(rf"{re.escape(demo_id)}\s*:\s*\[(.*?)\]\s*\n\s*}}", source, re.S)
    if not match:
        raise ValueError(f"Could not find event timeline for {demo_id!r} in {index_path}")

    events: list[dict[str, float | str]] = []
    item_pattern = re.compile(
        r"\{\s*start:\s*([0-9.]+)\s*,\s*end:\s*([0-9.]+)\s*,\s*text:\s*'([^']*)'\s*}",
        re.S,
    )
    for item in item_pattern.finditer(match.group(1)):
        text = html.unescape(item.group(3)).replace("..", ".")
        events.append({"start": float(item.group(1)), "end": float(item.group(2)), "text": text})
    if not events:
        raise ValueError(f"Found {demo_id!r}, but no event objects could be parsed.")
    return events


def parse_key_labels(args: argparse.Namespace) -> list[tuple[float, str]]:
    labels: list[tuple[float, str]] = []
    if not args.no_default_key_labels:
        labels.extend(DEFAULT_KEY_LABELS.get(args.demo_id, []))

    for raw_label in args.key_label:
        if ":" not in raw_label:
            raise ValueError(f"Invalid --key-label {raw_label!r}; expected TIME:TEXT.")
        raw_time, text = raw_label.split(":", 1)
        text = text.strip()
        if not text:
            raise ValueError(f"Invalid --key-label {raw_label!r}; label text is empty.")
        labels.append((float(raw_time.strip()), text))

    return sorted(labels, key=lambda item: item[0])


def parse_key_targets(args: argparse.Namespace) -> dict[str, list[KeyTarget]]:
    targets: dict[str, list[KeyTarget]] = {"tie": [], "seedance": []}
    if not args.no_default_key_boxes:
        for side, side_targets in DEFAULT_KEY_TARGETS.get(args.demo_id, {}).items():
            targets[side].extend(KeyTarget(*target) for target in side_targets)

    for raw_box in args.key_box:
        parts = raw_box.split(":")
        if len(parts) != 4:
            raise ValueError(
                f"Invalid --key-box {raw_box!r}; expected SIDE:TIME:X,Y,W,H:STATE."
            )
        side, raw_time, raw_box_values, raw_state = (part.strip().lower() for part in parts)
        if side not in {"tie", "seedance", "both"}:
            raise ValueError(f"Invalid --key-box side {side!r}; expected tie, seedance, or both.")
        box_values = [float(value.strip()) for value in raw_box_values.split(",")]
        if len(box_values) != 4:
            raise ValueError(f"Invalid --key-box box {raw_box_values!r}; expected X,Y,W,H.")
        if any(value < 0 for value in box_values) or box_values[0] > 1 or box_values[1] > 1:
            raise ValueError(f"Invalid --key-box coordinates {raw_box_values!r}; use normalized values.")
        state_map = {"success": True, "pass": True, "ok": True, "fail": False, "failure": False}
        if raw_state not in state_map:
            raise ValueError(f"Invalid --key-box state {raw_state!r}; expected success or fail.")

        target = KeyTarget(float(raw_time), *box_values, state_map[raw_state])
        sides = ("tie", "seedance") if side == "both" else (side,)
        for target_side in sides:
            targets[target_side].append(target)

    return {side: sorted(side_targets, key=lambda target: target.time) for side, side_targets in targets.items()}


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ]
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def fit_frame(frame, size: tuple[int, int]):
    target_w, target_h = size
    h, w = frame.shape[:2]
    scale = min(target_w / w, target_h / h)
    new_w = max(1, int(round(w * scale)))
    new_h = max(1, int(round(h * scale)))
    resized = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)
    canvas = cv2.copyMakeBorder(
        resized,
        (target_h - new_h) // 2,
        target_h - new_h - (target_h - new_h) // 2,
        (target_w - new_w) // 2,
        target_w - new_w - (target_w - new_w) // 2,
        cv2.BORDER_CONSTANT,
        value=(244, 246, 249),
    )
    return cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB)


def read_frame_at(cap: cv2.VideoCapture, t: float, duration: float):
    cap.set(cv2.CAP_PROP_POS_MSEC, min(max(t, 0.0), duration - 1e-3) * 1000.0)
    ok, frame = cap.read()
    if ok:
        return frame
    cap.set(cv2.CAP_PROP_POS_FRAMES, max(0, int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) - 1))
    ok, frame = cap.read()
    if not ok:
        raise RuntimeError("Could not read a frame from source video.")
    return frame


def draw_rounded(draw: ImageDraw.ImageDraw, box, radius: int, fill, outline=None, width: int = 1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def label_for_key_time(key_labels: list[tuple[float, str]], key_time: float) -> str:
    for label_time, label_text in key_labels:
        if abs(label_time - key_time) <= 1e-3:
            return label_text
    return f"{key_time:g}s"


def draw_status_mark(draw: ImageDraw.ImageDraw, center: tuple[int, int], radius: int, success: bool):
    cx, cy = center
    color = SUCCESS if success else FAILURE
    draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=color)
    if success:
        draw.line(
            (
                cx - radius * 0.55,
                cy,
                cx - radius * 0.18,
                cy + radius * 0.38,
                cx + radius * 0.58,
                cy - radius * 0.45,
            ),
            fill=(255, 255, 255),
            width=max(3, radius // 3),
            joint="curve",
        )
    else:
        offset = radius * 0.48
        draw.line((cx - offset, cy - offset, cx + offset, cy + offset), fill=(255, 255, 255), width=max(3, radius // 3))
        draw.line((cx + offset, cy - offset, cx - offset, cy + offset), fill=(255, 255, 255), width=max(3, radius // 3))


def draw_key_target_overlays(
    image: Image.Image,
    video_box: tuple[int, int, int, int],
    key_labels: list[tuple[float, str]],
    key_targets: list[KeyTarget],
    current_time: float,
):
    draw = ImageDraw.Draw(image)
    label_font = load_font(18, bold=True)
    video_x, video_y, video_w, video_h = video_box
    for target in key_targets:
        elapsed = current_time - target.time
        if elapsed < -KEY_BOX_PRE_WINDOW or elapsed > KEY_BOX_POST_WINDOW:
            continue

        window = KEY_BOX_PRE_WINDOW if elapsed < 0 else KEY_BOX_POST_WINDOW
        progress = 1.0 - abs(elapsed) / window
        outline = SUCCESS if target.success else FAILURE
        box_x0 = video_x + int(round(target.x * video_w))
        box_y0 = video_y + int(round(target.y * video_h))
        box_x1 = video_x + int(round(min(1.0, target.x + target.w) * video_w))
        box_y1 = video_y + int(round(min(1.0, target.y + target.h) * video_h))
        box_x1 = max(box_x0 + 24, box_x1)
        box_y1 = max(box_y0 + 24, box_y1)

        glow_pad = int(round(4 + 5 * progress))
        draw.rectangle(
            (box_x0 - glow_pad, box_y0 - glow_pad, box_x1 + glow_pad, box_y1 + glow_pad),
            outline=(255, 255, 255),
            width=3,
        )
        draw.rectangle((box_x0, box_y0, box_x1, box_y1), outline=outline, width=5)

        label_text = label_for_key_time(key_labels, target.time)
        max_label_w = min(330, video_x + video_w - box_x0)
        text = label_text
        while len(text) > 6:
            text_box = draw.textbbox((0, 0), text, font=label_font)
            if text_box[2] - text_box[0] <= max_label_w - 52:
                break
            text = text[:-2].rstrip() + "."

        text_box = draw.textbbox((0, 0), text, font=label_font)
        text_w = text_box[2] - text_box[0]
        pill_w = text_w + 50
        pill_h = 32
        pill_x1 = min(video_x + video_w - 6, box_x1)
        pill_x0 = max(video_x + 6, pill_x1 - pill_w)
        pill_y0 = max(video_y + 6, box_y0 + 6)
        pill_x1 = pill_x0 + pill_w
        pill_y1 = pill_y0 + pill_h

        draw_rounded(draw, (pill_x0, pill_y0, pill_x1, pill_y1), 7, (255, 255, 255), outline, width=2)
        draw_status_mark(draw, (pill_x0 + 18, pill_y0 + pill_h // 2), 11, target.success)
        draw.text((pill_x0 + 36, pill_y0 + 6), text, fill=TEXT, font=label_font)


def pack_events_into_lanes(
    events: list[dict[str, float | str]], duration: float
) -> list[list[tuple[int, dict[str, float | str]]]]:
    """Pack non-overlapping event intervals into the fewest visual lanes."""
    lanes: list[list[tuple[int, dict[str, float | str]]]] = []
    lane_ends: list[float] = []
    indexed_events = sorted(
        enumerate(events),
        key=lambda item: (float(item[1]["start"]), float(item[1]["end"]), item[0]),
    )

    for idx, event in indexed_events:
        start = max(0.0, min(duration, float(event["start"])))
        end = max(start, min(duration, float(event["end"])))
        for lane_idx, lane_end in enumerate(lane_ends):
            if start >= lane_end - 1e-6:
                lanes[lane_idx].append((idx, event))
                lane_ends[lane_idx] = end
                break
        else:
            lanes.append([(idx, event)])
            lane_ends.append(end)
    return lanes


def draw_video_panel(
    image: Image.Image,
    origin: tuple[int, int],
    frame,
    title: str,
    subtitle: str,
    accent,
    events: list[dict[str, float | str]],
    current_time: float,
    duration: float,
    panel_w: int,
    video_h: int,
    key_labels: list[tuple[float, str]],
    key_targets: list[KeyTarget],
):
    x, y = origin
    draw = ImageDraw.Draw(image)
    title_font = load_font(31, bold=True)
    meta_font = load_font(19)
    event_font = load_font(16)
    label_font = load_font(17, bold=True)

    draw_rounded(draw, (x, y, x + panel_w, y + video_h + 430), 18, PANEL_BG, (222, 227, 234))
    draw.text((x + 24, y + 20), title, fill=TEXT, font=title_font)
    draw.text((x + 24, y + 58), subtitle, fill=MUTED, font=meta_font)

    video_y = y + 92
    video_w = panel_w - 48
    image.paste(Image.fromarray(frame), (x + 24, video_y))
    draw.rectangle((x + 24, video_y, x + 24 + video_w, video_y + video_h), outline=(206, 213, 222), width=2)
    draw_key_target_overlays(
        image,
        (x + 24, video_y, video_w, video_h),
        key_labels,
        key_targets,
        current_time,
    )

    timeline_x = x + 24
    timeline_y = video_y + video_h + 48
    timeline_w = video_w
    lane_h = 22
    lane_gap = 8
    lanes = pack_events_into_lanes(events, duration)

    draw.text((timeline_x, timeline_y - 31), f"{current_time:04.1f}s / {duration:.0f}.0s", fill=TEXT, font=label_font)
    draw.line((timeline_x, timeline_y - 8, timeline_x + timeline_w, timeline_y - 8), fill=(196, 203, 214), width=2)
    for second in range(0, int(duration) + 1):
        tx = timeline_x + int(round((second / duration) * timeline_w))
        draw.line((tx, timeline_y - 15, tx, timeline_y - 2), fill=(139, 148, 163), width=1)
        if second % 2 == 0:
            draw.text((tx - 10, timeline_y - 39), f"{second}s", fill=MUTED, font=event_font)

    for lane_idx, lane in enumerate(lanes):
        lane_y = timeline_y + lane_idx * (lane_h + lane_gap)
        draw_rounded(draw, (timeline_x, lane_y, timeline_x + timeline_w, lane_y + lane_h), 6, TRACK)
        for idx, event in lane:
            start = max(0.0, min(duration, float(event["start"])))
            end = max(start, min(duration, float(event["end"])))
            bx0 = timeline_x + int(round((start / duration) * timeline_w))
            bx1 = timeline_x + int(round((end / duration) * timeline_w))
            color = EVENT_COLORS[idx % len(EVENT_COLORS)]
            draw_rounded(draw, (bx0, lane_y, max(bx0 + 2, bx1), lane_y + lane_h), 6, color)

    play_x = timeline_x + int(round((current_time / duration) * timeline_w))
    timeline_bottom = timeline_y + len(lanes) * (lane_h + lane_gap) - lane_gap
    draw.line((play_x, timeline_y - 21, play_x, timeline_bottom + 8), fill=PLAYHEAD, width=4)
    draw.ellipse((play_x - 7, timeline_y - 28, play_x + 7, timeline_y - 14), fill=accent)

    key_y = timeline_bottom + 24
    if key_labels:
        draw.text((timeline_x, key_y + 2), "Key Visual Change", fill=TEXT, font=label_font)
    for label_idx, (label_time, label_text) in enumerate(key_labels):
        if label_time < 0 or label_time > duration:
            continue
        key_x = timeline_x + int(round((label_time / duration) * timeline_w))
        label_w = 204
        label_x = max(timeline_x, min(timeline_x + timeline_w - label_w, key_x - label_w // 2))
        label_y = key_y + label_idx * 28

        bounce_elapsed = current_time - label_time
        bounce_offset = 0
        bounce_scale = 1.0
        if 0 <= bounce_elapsed <= 0.45:
            phase = bounce_elapsed / 0.45
            bounce_offset = int(round(-13 * math.sin(math.pi * phase) * (1 - phase * 0.25)))
            bounce_scale = 1.0 + 0.08 * math.sin(math.pi * phase) * (1 - phase)

        chip_w = int(round(label_w * bounce_scale))
        chip_h = int(round(23 * bounce_scale))
        chip_x = max(timeline_x, min(timeline_x + timeline_w - chip_w, key_x - chip_w // 2))
        chip_y = label_y + bounce_offset
        draw.line((key_x, timeline_y - 4, key_x, chip_y + chip_h // 2), fill=accent, width=2)
        draw_rounded(draw, (chip_x, chip_y, chip_x + chip_w, chip_y + chip_h), 6, (239, 243, 248), (209, 216, 226))
        label = f"{label_time:g}s {label_text}"[:30]
        text_box = draw.textbbox((0, 0), label, font=event_font)
        text_w = text_box[2] - text_box[0]
        text_h = text_box[3] - text_box[1]
        draw.text(
            (chip_x + (chip_w - text_w) / 2, chip_y + (chip_h - text_h) / 2 - 1),
            label,
            fill=TEXT,
            font=event_font,
        )

    active_events = [
        (idx, event)
        for lane in lanes
        for idx, event in lane
        if float(event["start"]) <= current_time < float(event["end"])
        or (current_time >= duration - 1e-3 and float(event["end"]) >= duration - 1e-3)
    ]
    active_y = timeline_bottom + 32 + len(key_labels) * 28
    draw.text((timeline_x, active_y), "Current events", fill=TEXT, font=label_font)
    if not active_events:
        draw.text((timeline_x, active_y + 31), "No active event", fill=MUTED, font=event_font)
    else:
        for row, (idx, event) in enumerate(active_events[:4]):
            row_y = active_y + 30 + row * 28
            color = EVENT_COLORS[idx % len(EVENT_COLORS)]
            draw_rounded(draw, (timeline_x, row_y + 3, timeline_x + 18, row_y + 21), 4, color)
            label = f"{float(event['start']):g}-{float(event['end']):g}s  {event['text']}"
            draw.text((timeline_x + 28, row_y), label[:96], fill=TEXT, font=event_font)


def main() -> None:
    args = parse_args()
    events = read_events(args.index, args.demo_id)
    key_labels = parse_key_labels(args)
    key_targets = parse_key_targets(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)

    tie_cap = cv2.VideoCapture(str(args.tie_video))
    seedance_cap = cv2.VideoCapture(str(args.seedance_video))
    if not tie_cap.isOpened():
        raise FileNotFoundError(f"Could not open TIE video: {args.tie_video}")
    if not seedance_cap.isOpened():
        raise FileNotFoundError(f"Could not open Seedance video: {args.seedance_video}")

    raw_output = args.output.with_name(f"{args.output.stem}_opencv_tmp{args.output.suffix}")
    panel_gap = 36
    margin_x = 42
    top = 32
    panel_w = (args.width - 2 * margin_x - panel_gap) // 2
    video_w = panel_w - 48
    video_h = int(round(video_w * 480 / 872))
    if top + video_h + 430 > args.height:
        raise ValueError("Output height is too small for the videos and event bars.")

    writer = cv2.VideoWriter(
        str(raw_output),
        cv2.VideoWriter_fourcc(*"mp4v"),
        args.output_fps,
        (args.width, args.height),
    )
    if not writer.isOpened():
        raise RuntimeError(f"Could not create temporary output video: {raw_output}")

    total_frames = int(math.ceil(args.duration * args.output_fps))
    for frame_idx in range(total_frames):
        t = min(args.duration, frame_idx / args.output_fps)
        tie_frame = fit_frame(read_frame_at(tie_cap, t, args.duration), (video_w, video_h))
        seedance_frame = fit_frame(read_frame_at(seedance_cap, t, args.duration), (video_w, video_h))

        canvas = Image.new("RGB", (args.width, args.height), CANVAS_BG)
        draw = ImageDraw.Draw(canvas)
        header_font = load_font(38, bold=True)
        draw.text(
            (margin_x, args.height - 58),
            "Event interval timestamp response comparison",
            fill=TEXT,
            font=header_font,
        )

        draw_video_panel(
            canvas,
            (margin_x, top),
            tie_frame,
            "TIE",
            f"{args.demo_id} | source label: {args.tie_label_fps:g} fps | interval-aware timestamps",
            TIE_ACCENT,
            events,
            t,
            args.duration,
            panel_w,
            video_h,
            key_labels,
            key_targets["tie"],
        )
        draw_video_panel(
            canvas,
            (margin_x + panel_w + panel_gap, top),
            seedance_frame,
            "Seedance",
            f"{args.demo_id} | source label: {args.seedance_label_fps:g} fps | baseline response",
            SEEDANCE_ACCENT,
            events,
            t,
            args.duration,
            panel_w,
            video_h,
            key_labels,
            key_targets["seedance"],
        )

        writer.write(cv2.cvtColor(np.asarray(canvas), cv2.COLOR_RGB2BGR))
        if frame_idx % max(1, int(args.output_fps)) == 0:
            print(f"rendered {frame_idx}/{total_frames} frames", flush=True)

    writer.release()
    tie_cap.release()
    seedance_cap.release()

    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-i",
            str(raw_output),
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "20",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            str(args.output),
        ],
        check=True,
    )
    raw_output.unlink(missing_ok=True)
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
