#!/usr/bin/env python3
"""Visually select a normalized key-event region from a video frame.

Example:
    python scripts/select_key_event_region.py \
        --video static/videos/example1.mp4 \
        --time 7.0 \
        --side tie \
        --state success

Drag a rectangle in the preview window, press Enter/Space to accept, or Esc to
cancel. The script prints a --key-box value for synthesize_timestamp_comparison.py.
"""

from __future__ import annotations

import argparse
import html
import json
import webbrowser
from pathlib import Path

import cv2


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Select a key-event region from a video frame.")
    parser.add_argument("--video", type=Path, required=True, help="Source video path.")
    parser.add_argument("--time", type=float, required=True, help="Timestamp in seconds.")
    parser.add_argument(
        "--side",
        choices=("tie", "seedance", "both"),
        default="tie",
        help="Generator panel side for the emitted --key-box.",
    )
    parser.add_argument(
        "--state",
        choices=("success", "fail"),
        default="success",
        help="Whether the region marks a successful or failed response.",
    )
    parser.add_argument(
        "--window-width",
        type=int,
        default=1200,
        help="Maximum OpenCV preview window width; selection is converted back to source coordinates.",
    )
    parser.add_argument(
        "--html-output",
        type=Path,
        default=Path(__file__).resolve().parent / "key_region_selector.html",
        help="Fallback browser selector HTML path.",
    )
    parser.add_argument(
        "--no-open-browser",
        action="store_true",
        help="Write fallback HTML without asking the default browser to open it.",
    )
    return parser.parse_args()


def read_frame(video_path: Path, timestamp: float):
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise FileNotFoundError(f"Could not open video: {video_path}")
    cap.set(cv2.CAP_PROP_POS_MSEC, max(0.0, timestamp) * 1000.0)
    ok, frame = cap.read()
    cap.release()
    if not ok:
        raise RuntimeError(f"Could not read frame at {timestamp:g}s from {video_path}")
    return frame


def emit_browser_selector(args: argparse.Namespace, frame) -> Path:
    output_html = args.html_output.resolve()
    output_html.parent.mkdir(parents=True, exist_ok=True)
    frame_path = output_html.with_name(f"{output_html.stem}_frame.jpg")
    ok = cv2.imwrite(str(frame_path), frame)
    if not ok:
        raise RuntimeError(f"Could not write selector frame: {frame_path}")

    source_h, source_w = frame.shape[:2]
    image_src = json.dumps(frame_path.name)
    side = json.dumps(args.side)
    state = json.dumps(args.state)
    timestamp = json.dumps(f"{args.time:g}")
    title = html.escape(f"{args.video.name} at {args.time:g}s")

    output_html.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Key Region Selector</title>
  <style>
    body {{
      margin: 0;
      font-family: Arial, sans-serif;
      color: #172033;
      background: #f4f6f9;
    }}
    main {{
      max-width: 1240px;
      margin: 24px auto;
      padding: 0 18px;
    }}
    h1 {{
      margin: 0 0 14px;
      font-size: 22px;
    }}
    canvas {{
      display: block;
      max-width: 100%;
      height: auto;
      border: 1px solid #cfd6e1;
      background: #111827;
      cursor: crosshair;
    }}
    output {{
      display: block;
      margin-top: 14px;
      padding: 12px;
      border: 1px solid #cfd6e1;
      background: #fff;
      font-family: Consolas, monospace;
      white-space: pre-wrap;
      word-break: break-all;
    }}
    button {{
      margin-top: 10px;
      padding: 8px 12px;
      border: 1px solid #aeb8c7;
      border-radius: 6px;
      background: #fff;
      cursor: pointer;
    }}
  </style>
</head>
<body>
  <main>
    <h1>{title}</h1>
    <canvas id="canvas" width="{source_w}" height="{source_h}"></canvas>
    <output id="result">Drag a rectangle on the image.</output>
    <button id="copy" type="button">Copy</button>
  </main>
  <script>
    const canvas = document.getElementById('canvas');
    const ctx = canvas.getContext('2d');
    const result = document.getElementById('result');
    const copy = document.getElementById('copy');
    const image = new Image();
    const side = {side};
    const time = {timestamp};
    const state = {state};
    let start = null;
    let selection = null;

    function canvasPoint(event) {{
      const rect = canvas.getBoundingClientRect();
      return {{
        x: (event.clientX - rect.left) * canvas.width / rect.width,
        y: (event.clientY - rect.top) * canvas.height / rect.height
      }};
    }}

    function normalizedBox(box) {{
      const x = Math.min(box.x0, box.x1);
      const y = Math.min(box.y0, box.y1);
      const w = Math.abs(box.x1 - box.x0);
      const h = Math.abs(box.y1 - box.y0);
      return [x / canvas.width, y / canvas.height, w / canvas.width, h / canvas.height]
        .map((value) => value.toFixed(4));
    }}

    function commandFor(box) {{
      return `--key-box "${{side}}:${{time}}:${{normalizedBox(box).join(',')}}:${{state}}"`;
    }}

    function draw() {{
      ctx.drawImage(image, 0, 0, canvas.width, canvas.height);
      if (!selection) return;
      const x = Math.min(selection.x0, selection.x1);
      const y = Math.min(selection.y0, selection.y1);
      const w = Math.abs(selection.x1 - selection.x0);
      const h = Math.abs(selection.y1 - selection.y0);
      ctx.lineWidth = 5;
      ctx.strokeStyle = state === 'success' ? '#16a34a' : '#dc2626';
      ctx.strokeRect(x, y, w, h);
      ctx.lineWidth = 2;
      ctx.strokeStyle = '#ffffff';
      ctx.strokeRect(x - 3, y - 3, w + 6, h + 6);
    }}

    canvas.addEventListener('pointerdown', (event) => {{
      start = canvasPoint(event);
      selection = {{ x0: start.x, y0: start.y, x1: start.x, y1: start.y }};
      canvas.setPointerCapture(event.pointerId);
      draw();
    }});

    canvas.addEventListener('pointermove', (event) => {{
      if (!start) return;
      const point = canvasPoint(event);
      selection = {{ x0: start.x, y0: start.y, x1: point.x, y1: point.y }};
      result.textContent = commandFor(selection);
      draw();
    }});

    canvas.addEventListener('pointerup', () => {{
      start = null;
      if (selection) result.textContent = commandFor(selection);
    }});

    copy.addEventListener('click', async () => {{
      await navigator.clipboard.writeText(result.textContent);
    }});

    image.onload = draw;
    image.src = {image_src};
  </script>
</body>
</html>
""",
        encoding="utf-8",
    )
    if not args.no_open_browser:
        webbrowser.open(output_html.as_uri())
    return output_html


def select_roi_with_opencv(args: argparse.Namespace, frame):
    source_h, source_w = frame.shape[:2]

    scale = min(1.0, args.window_width / source_w)
    preview_w = max(1, int(round(source_w * scale)))
    preview_h = max(1, int(round(source_h * scale)))
    preview = cv2.resize(frame, (preview_w, preview_h), interpolation=cv2.INTER_AREA)

    window_name = f"Select region at {args.time:g}s - {args.video.name}"
    roi = cv2.selectROI(window_name, preview, showCrosshair=True, fromCenter=False)
    cv2.destroyWindow(window_name)
    return roi, scale


def main() -> None:
    args = parse_args()
    frame = read_frame(args.video, args.time)
    source_h, source_w = frame.shape[:2]

    try:
        roi, scale = select_roi_with_opencv(args, frame)
    except cv2.error as exc:
        if "The function is not implemented" not in str(exc):
            raise
        output_html = emit_browser_selector(args, frame)
        print(f"OpenCV GUI is unavailable. Open this browser selector instead:\n{output_html}")
        return

    x, y, w, h = roi
    if w <= 0 or h <= 0:
        raise SystemExit("No region selected.")

    source_x = x / scale
    source_y = y / scale
    source_roi_w = w / scale
    source_roi_h = h / scale

    normalized = (
        source_x / source_w,
        source_y / source_h,
        source_roi_w / source_w,
        source_roi_h / source_h,
    )
    box = ",".join(f"{value:.4f}" for value in normalized)
    print(f'--key-box "{args.side}:{args.time:g}:{box}:{args.state}"')


if __name__ == "__main__":
    main()
