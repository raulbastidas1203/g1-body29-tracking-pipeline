# Evaluation And Gates

## Standard Evaluation

```bash
python3 -m body29_pipeline.cli evaluate \
  --task-id Mjlab-Tracking-Flat-Unitree-G1-G1MovesCompat \
  --checkpoint-file research/mjlab/logs/rsl_rl/body29dof_g1_moves_compat/<run>/model_<step>.pt \
  --motion-file artifacts/video_005/motion.npz \
  --num-envs 64 \
  --output-file artifacts/video_005/g1_moves_compat_eval.json
```

## Rollout Video

PyTorch rollout:

```bash
python3 -m body29_pipeline.cli record-rollout \
  --task-id Mjlab-Tracking-Flat-Unitree-G1-G1MovesCompat \
  --checkpoint-file research/mjlab/logs/rsl_rl/body29dof_g1_moves_compat/<run>/model_<step>.pt \
  --motion-file artifacts/video_005/motion.npz \
  --output-video artifacts/video_005/g1_moves_compat_rollout_pt.mp4 \
  --output-metrics artifacts/video_005/g1_moves_compat_rollout_pt.json \
  --num-steps 285 \
  --no-terminations
```

ONNX rollout:

```bash
python3 -m body29_pipeline.cli record-rollout-onnx \
  --task-id Mjlab-Tracking-Flat-Unitree-G1-G1MovesCompat \
  --checkpoint-file research/mjlab/logs/rsl_rl/body29dof_g1_moves_compat/<run>/model_<step>.pt \
  --motion-file artifacts/video_005/motion.npz \
  --output-video artifacts/video_005/g1_moves_compat_rollout_onnx.mp4 \
  --output-metrics artifacts/video_005/g1_moves_compat_rollout_onnx.json \
  --num-steps 285 \
  --no-terminations
```

## Gate A

Before standalone `sim2sim`, require:

- `5/5` full rollouts without early termination inside `mjlab`
- `mpkpe <= 0.06`
- `r_mpkpe <= 0.05`
- `ee_pos_error <= 0.11`
- `ee_ori_error <= 0.35`

## Gate B

For this route, Gate B is the checkpoint-selection gate:

- prefer the checkpoint with the highest full-clip survival
- use `mpkpe` as first tie-breaker
- use `anchor_xy_error` as second tie-breaker

## Gate C

Gate C is PT / ONNX behavioral parity.

Command:

```bash
python3 -m body29_pipeline.cli compare-onnx \
  --task-id Mjlab-Tracking-Flat-Unitree-G1-G1MovesCompat \
  --checkpoint-file research/mjlab/logs/rsl_rl/body29dof_g1_moves_compat/<run>/model_<step>.pt \
  --motion-file artifacts/video_005/motion.npz \
  --num-envs 1 \
  --num-steps 285 \
  --output-file artifacts/video_005/g1_moves_compat_parity.json
```

Pass condition:

- mean action difference is on the order of `1e-7` to `1e-6`

## Standalone Entry Gate

Only after Gate A and Gate C pass do we move to standalone `sim2sim`.

For the standalone runner, the first acceptance target is:

- `5/5` rollouts complete without fall
- `anchor_xy_error <= 0.15 m`
- `mpkpe <= 0.10`
- visual behavior reasonably close to the `mjlab` rollout
