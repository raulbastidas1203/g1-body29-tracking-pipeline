# G1 Body29 Tracking Pipeline

Single-clip motion tracking for `Unitree G1` body-only `29 DoF`, from `video2robot` output to `mjlab` training and `RoboJuDo` sim2sim.

---

## Results

### Original clip

[![Original TikTok](docs/media/gifs/video_005_original_tiktok.gif)](docs/media/videos/video_005_original_tiktok.mp4)

### Reference motion used for training

[![Reference motion](docs/media/gifs/video_005_reference_motion.gif)](docs/media/videos/video_005_reference_motion.mp4)

### `mjlab` rollout

[![mjlab rollout](docs/media/gifs/video_005_mjlab_model_8000.gif)](docs/media/videos/video_005_mjlab_model_8000.mp4)

### Original vs robot

![Original vs RoboJuDo](docs/media/gifs/video_005_original_vs_robojudo_14000.gif)

### RoboJuDo sim2sim

[![RoboJuDo rollout](docs/media/gifs/video_005_robojudo_model_14000.gif)](docs/media/videos/video_005_robojudo_model_14000.mp4)

---

## Overview

This repo packages the exact workflow we used for `video_005`:

1. validate `video2robot` output
2. convert to `motion.npz`
3. train a single-clip policy in `mjlab`
4. export an actor-only ONNX
5. test the policy in a `g1-moves` / `RoboJuDo` style sim2sim stack

The repo is intentionally lightweight:

- local pipeline code lives here
- upstream repos are cloned on demand
- local `mjlab` changes are carried as a patch in [`patches/mjlab-body29-local-flow.patch`](patches/mjlab-body29-local-flow.patch)

---

## Current Status

- input clip: `video_005`
- active task: `Mjlab-Tracking-Flat-Unitree-G1-G1MovesCompat`
- training stack: `mjlab` + PPO
- sim2sim stack: `RoboJuDo` XML + ONNX metadata-driven control
- best `mjlab` checkpoint among evaluated ones: `model_10000`
- best current transfer checkpoint: `model_14000`

---

## Metrics

### `mjlab`

| Checkpoint | success_rate | mpkpe | r_mpkpe | joint_vel_error | ee_pos_error | ee_ori_error |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `model_8000` | `1.0000` | `0.0482` | `0.0345` | `5.8182` | `0.0713` | `0.2041` |
| `model_10000` | `1.0000` | `0.0471` | `0.0342` | `5.8426` | `0.0710` | `0.2003` |

Raw files:

- [`docs/results/model_8000_eval.json`](docs/results/model_8000_eval.json)
- [`docs/results/model_10000_eval.json`](docs/results/model_10000_eval.json)

### RoboJuDo sim2sim

| Checkpoint | mpkpe | r_mpkpe | joint_vel_error | anchor_xy_error | anchor_xy_error_max |
| --- | ---: | ---: | ---: | ---: | ---: |
| `model_8000` | `0.1155` | `0.0284` | `4.8246` | `0.1002` | `0.1875` |
| `model_10000` | `0.0915` | `0.0275` | `4.7982` | `0.0748` | `0.1601` |
| `model_12000` | `0.0936` | `0.0283` | `4.7258` | `0.0758` | `0.1776` |
| `model_14000` | `0.0857` | `0.0286` | `4.7900` | `0.0655` | `0.1770` |

Raw files:

- [`docs/results/robojudo_model_8000_full_scaled.json`](docs/results/robojudo_model_8000_full_scaled.json)
- [`docs/results/robojudo_model_10000_full_scaled.json`](docs/results/robojudo_model_10000_full_scaled.json)
- [`docs/results/robojudo_model_12000_full_scaled.json`](docs/results/robojudo_model_12000_full_scaled.json)
- [`docs/results/robojudo_model_14000_full_scaled.json`](docs/results/robojudo_model_14000_full_scaled.json)

---

## Input

Expected bundle:

```text
00_RL_input/video_005/
  original.mp4
  robot_motion.csv
  robot_motion.pkl
```

The CSV is the training source of truth:

- shape: `172 x 36`
- layout: `root_pos(3) + root_quat_xyzw(4) + dof_pos(29)`

---

## Quickstart

### 1. Setup

```bash
python3 -m pip install -e .
bash scripts/bootstrap_upstreams.sh
```

### 2. Validate and convert

```bash
python3 -m body29_pipeline.cli validate --strict
python3 -m body29_pipeline.cli convert --render
```

### 3. Smoke training

```bash
python3 -m body29_pipeline.cli smoke-train \
  --task-id Mjlab-Tracking-Flat-Unitree-G1-G1MovesCompat \
  --iterations 100 \
  --num-envs 64 \
  --save-interval 50 \
  --run-name smoke_video_005_g1_moves_compat
```

### 4. Long training

```bash
python3 -m body29_pipeline.cli train \
  --task-id Mjlab-Tracking-Flat-Unitree-G1-G1MovesCompat \
  --motion-file artifacts/video_005/motion.npz \
  --iterations 15000 \
  --num-envs 2048 \
  --save-interval 2000 \
  --experiment-name body29dof_g1_moves_compat \
  --run-name train_video_005_g1_moves_compat_long_tty \
  --seed 42
```

### 5. Evaluate inside `mjlab`

```bash
python3 -m body29_pipeline.cli evaluate \
  --task-id Mjlab-Tracking-Flat-Unitree-G1-G1MovesCompat \
  --motion-file artifacts/video_005/motion.npz \
  --checkpoint-file research/mjlab/logs/rsl_rl/body29dof_g1_moves_compat/<run>/model_10000.pt \
  --num-envs 16
```

### 6. Export ONNX

```bash
python3 -m body29_pipeline.cli export-onnx \
  --task-id Mjlab-Tracking-Flat-Unitree-G1-G1MovesCompat \
  --checkpoint-file research/mjlab/logs/rsl_rl/body29dof_g1_moves_compat/<run>/model_14000.pt
```

### 7. Run RoboJuDo sim2sim

```bash
cd research/g1-moves/RoboJuDo
./.venv/bin/python scripts/eval_mjlab_g1moves_robojudo.py \
  --onnx-file /path/to/model_14000.onnx \
  --motion-file /home/raul/00_cursor/RL/artifacts/video_005/motion.npz \
  --xml-file /home/raul/00_cursor/RL/research/g1-moves/RoboJuDo/assets/robots/g1/g1_29dof_rev_1_0.xml \
  --output-video /path/to/output.mp4 \
  --output-metrics /path/to/output.json \
  --action-mode scaled_offset \
  --obs-default metadata \
  --video-width 640 \
  --video-height 480
```

---

## Training Notes

- the long run saved checkpoints through `model_14000.pt`
- the process stalled near the very end around iteration `14811`
- we attempted to resume, but CUDA initialization broke for new processes in that session
- we therefore selected the best checkpoint from saved artifacts instead of forcing an unreliable continuation

---

## Repo Layout

- [`body29_pipeline`](body29_pipeline): local CLI
- [`docs/03-training-curriculum.md`](docs/03-training-curriculum.md): training route
- [`docs/05-sim2sim.md`](docs/05-sim2sim.md): RoboJuDo sim2sim notes
- [`docs/07-training-explainer.md`](docs/07-training-explainer.md): PPO and metric interpretation
- [`docs/08-results.md`](docs/08-results.md): frozen result snapshot
- [`docs/results`](docs/results): raw JSON metrics committed into the repo

---

## Pinned Upstreams

- `mjlab`
- `g1-moves`
- `RoboJuDo`
- `TWIST2`
- `unitree_mujoco`

See [`upstreams/lock.json`](upstreams/lock.json) for exact pins.
