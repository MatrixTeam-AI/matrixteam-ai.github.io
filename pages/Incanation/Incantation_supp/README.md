# Incantation Supplementary Materials

This folder collects supplementary demos and data examples for Incantation, an interactive video world model that uses natural language as a per-frame, per-entity action interface. The materials are organized to show qualitative generation results, the local annotation workflow, and both raw and processed data formats. More examples can be appended later.

## What This Supports

The paper studies single-viewpoint multi-entity control: multiple entities share one camera, but each entity receives its own action prompt at 0.25 s granularity. The key claim is that a natural-language interface can express controls that fixed action IDs or scene-level captions cannot, including cross-entity action transfer, out-of-vocabulary action phrasing, and cross-world reuse with the same architecture.

This supplement therefore includes:

- qualitative comparisons against strong video-generation baselines;
- examples of fine-grained per-entity action annotation;
- demos for multi-entity and longer-horizon generation;
- raw memory-derived animation logs and the processed caption format used by the pipeline.

## Contents

### Annotation Pipeline

- `annotate.html`: local AR annotation interface.
  - Works offline in the browser.
  - Uses 0.25 s temporal resolution.
  - Annotates one action per character per segment.
  - Stores progress in browser `localStorage`.
  - Exports ratings as JSONL via the page's `Export JSONL` button.
- `kof_0_part0.mp4`: short annotation example video showing frame-level action changes in a two-entity fighting scene.

### Method Comparison Videos

- `Ours.mp4`: our method.
- `kling3.0.mp4`: Kling 3.0 baseline.
- `longlive.mp4`: LongLive baseline.
- `seedance2.0.mp4`: Seedance 2.0 baseline.

These videos are intended for side-by-side qualitative comparison. The comparison focuses on whether each model preserves fine-grained player and boss actions, entity interaction, and temporal coherence under the same high-level scene intent.

### Generalization Demo

- `Three_entity.mp4`: three-entity generalization example. It illustrates that the prompt-slot interface can extend from the two-entity training setting to simultaneous control of three entities without changing the model architecture.

### 30s Demos

- `long_horizon_30s_demo.mp4`: 30-second generated rollout for checking action consistency, temporal coherence, and longer-horizon stability beyond short clips.

## Pipeline Summary

At a high level, the data pipeline is:

1. Record gameplay video and read per-entity animation states from memory.
2. Split the recording into aligned video/CSV segments.
3. Map raw animation IDs into human-readable per-entity action labels.
4. Convert each clip into a structured JSONL sample with global captions, participant descriptions, and per-entity action timelines.
5. Use the annotation interface to review generated clips and export human ratings.

## Example Data

### Raw Segment Example

Located in `examples/raw_segment/`.

- `20260117_180710_0_256p.mp4`: one raw segment extracted from `2026-01-17 18-07-10.mp4` and downsampled to 256p for lightweight preview.
- `0_raw.csv`: the corresponding raw animation CSV copied from `2026-01-17 18-07-10_segments/0.csv`, with runtime memory addresses removed for public sharing.

The raw CSV contains per-timestamp animation IDs for the player and target:

- `RelativeTime_s`: segment-relative timestamp in seconds, reset to `0.000` at the beginning of the segment.
- `Player_Anim`: decimal player animation ID.
- `Player_Anim_Hex`: hexadecimal player animation ID.
- `Target_Anim`: decimal target animation ID.
- `Target_Anim_Hex`: hexadecimal target animation ID.

This is the pre-caption, pre-cleanup representation used as input to later processing. It documents the frame-accurate supervision source before raw animation IDs are merged into semantic action labels.

### Processed Data Example

Located in `examples/processed_sample/`.

- `20260117_180710_0.mp4`: one processed video clip from `33_pisces_eldenring`, downsampled to 256p for lightweight preview.
- `output_captions_sample.jsonl`: one corresponding processed JSONL entry.

Each processed JSONL line is one training/evaluation sample. The top-level fields are:

- `video`: filename of the processed clip.
- `verified`: whether the sample has been manually verified.
- `prompt.scene_clarity`: coarse scene quality label.
- `prompt.global_caption`: whole-clip caption with short and long descriptions, visible objects, and clip start/end times.
- `prompt.participants`: per-entity descriptions and action timelines. Each timeline item includes `start_time`, `end_time`, `short_caption`, `long_caption`, `distinguishing_feature`, `is_interaction`, and `interaction_with`.
- `statistics`: derived metadata, such as maximum timeline event count and whether boss interaction is present.

This is the cleaned, captioned representation used after the processing pipeline. It is the model-facing format: each sample pairs a video clip with a natural-language description of the scene and temporally localized actions for each entity.

## Notes

- Open `annotate.html` directly in a browser to use the local annotation interface.
- The `.mp4` files in the root folder are demo assets for qualitative viewing.
- The files under `examples/` are small samples meant to document the raw and processed data formats.
