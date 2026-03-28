# Evaluation And Gates

## Standard Evaluation

```bash
python3 -m body29_pipeline.cli evaluate \
  --task-id Mjlab-Tracking-Flat-Unitree-G1-SoftRoot \
  --checkpoint-file research/mjlab/logs/rsl_rl/body29dof_only_soft_root/<run>/model_2399.pt \
  --motion-file artifacts/video_005/motion.npz \
  --num-envs 64 \
  --output-file artifacts/video_005/model_2399_eval.json
```

## Rollout Video

PyTorch rollout:

```bash
python3 -m body29_pipeline.cli record-rollout \
  --task-id Mjlab-Tracking-Flat-Unitree-G1-SoftRoot \
  --checkpoint-file research/mjlab/logs/rsl_rl/body29dof_only_soft_root/<run>/model_2399.pt \
  --motion-file artifacts/video_005/motion.npz \
  --output-video artifacts/video_005/model_2399_rollout_pt.mp4 \
  --output-metrics artifacts/video_005/model_2399_rollout_pt.json \
  --num-steps 285 \
  --no-terminations
```

ONNX rollout:

```bash
python3 -m body29_pipeline.cli record-rollout-onnx \
  --task-id Mjlab-Tracking-Flat-Unitree-G1-SoftRoot \
  --checkpoint-file research/mjlab/logs/rsl_rl/body29dof_only_soft_root/<run>/model_2399.pt \
  --motion-file artifacts/video_005/motion.npz \
  --output-video artifacts/video_005/model_2399_rollout_onnx.mp4 \
  --output-metrics artifacts/video_005/model_2399_rollout_onnx.json \
  --num-steps 285 \
  --no-terminations
```

## Gate B

For this project we treated Gate B as:

- moderate-noise evaluation
- `64` environments
- `success_rate >= 0.5`

Command:

```bash
python3 -m body29_pipeline.cli evaluate \
  --task-id Mjlab-Tracking-Flat-Unitree-G1-SoftRootRobust \
  --checkpoint-file research/mjlab/logs/rsl_rl/body29dof_only_soft_root/<run>/model_2399.pt \
  --motion-file artifacts/video_005/motion.npz \
  --num-envs 64 \
  --output-file artifacts/video_005/gate_b_moderate/model_2399_softrootrobust.json
```

Current result:

- `success_rate = 0.546875`

## Gate C

Gate C is PT / ONNX behavioral parity.

Command:

```bash
python3 -m body29_pipeline.cli compare-onnx \
  --task-id Mjlab-Tracking-Flat-Unitree-G1-SoftRoot \
  --checkpoint-file research/mjlab/logs/rsl_rl/body29dof_only_soft_root/<run>/model_2399.pt \
  --motion-file artifacts/video_005/motion.npz \
  --num-envs 1 \
  --num-steps 285 \
  --output-file artifacts/video_005/model_2399_parity.json
```

Current result:

- mean action difference is on the order of `1e-7` to `1e-6`

## Honest Note

Strict noisy evaluation on the plain `SoftRoot` task is still harder than the moderate Gate B threshold we used for sim2sim entry. That tradeoff should be kept visible in reviews.

