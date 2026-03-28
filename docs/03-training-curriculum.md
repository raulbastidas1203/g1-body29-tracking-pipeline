# Training Curriculum

## Philosophy

We do not jump straight to hardware. The intended order is:

1. conversion + replay
2. `g1-moves`-compatible smoke run
3. full single-clip training from scratch
4. checkpoint selection
5. ONNX parity
6. standalone `sim2sim`

## Active Task

The active task is:

- `Mjlab-Tracking-Flat-Unitree-G1-G1MovesCompat`

What changes versus the base task:

- `anchor_body_name = pelvis`
- actor observation order matches `g1-moves`
- ONNX export is actor-only (`obs -> actions`)
- standalone replay consumes `onnx + motion.npz + xml`

## Smoke Run

Use this to verify that:

- the task builds
- PPO runs without NaNs
- checkpoints save
- ONNX export/parity work

```bash
python3 -m body29_pipeline.cli smoke-train \
  --task-id Mjlab-Tracking-Flat-Unitree-G1-G1MovesCompat \
  --iterations 100 \
  --num-envs 64 \
  --save-interval 50 \
  --run-name smoke_video_005_g1_moves_compat \
  --video \
  --video-interval 100 \
  --video-length 285
```

## Main Single-Clip Training

Train from scratch on the active task:

```bash
python3 -m body29_pipeline.cli train \
  --task-id Mjlab-Tracking-Flat-Unitree-G1-G1MovesCompat \
  --motion-file artifacts/video_005/motion.npz \
  --iterations 15000 \
  --num-envs 2048 \
  --save-interval 2000 \
  --experiment-name body29dof_g1_moves_compat \
  --run-name train_video_005_g1_moves_compat \
  --video \
  --video-interval 5000 \
  --video-length 285
```

## Checkpoint Selection

We do not assume the last checkpoint is the best checkpoint.

Selection order:

1. highest full-clip survival / timeout completion
2. lowest `mpkpe`
3. lowest `anchor_xy_error`

## Export After Training

Once a candidate checkpoint is chosen:

```bash
python3 -m body29_pipeline.cli export-onnx \
  --task-id Mjlab-Tracking-Flat-Unitree-G1-G1MovesCompat \
  --checkpoint-file research/mjlab/logs/rsl_rl/body29dof_g1_moves_compat/<run>/model_<step>.pt
```

The exported ONNX is actor-only and is the artifact used for standalone `sim2sim`.
