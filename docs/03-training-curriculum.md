# Training Curriculum

## Philosophy

We do not jump straight to hardware. The intended order is:

1. conversion + replay
2. smoke run
3. real single-clip training
4. robust gating
5. ONNX parity
6. sim2sim

## Base Smoke Run

```bash
python3 -m body29_pipeline.cli smoke-train \
  --task-id Mjlab-Tracking-Flat-Unitree-G1 \
  --iterations 2 \
  --num-envs 64 \
  --save-interval 1 \
  --run-name smoke_video_005
```

## Main Single-Clip Training

The strongest clean-tracking branch we built used `SoftRoot`:

```bash
python3 -m body29_pipeline.cli train \
  --task-id Mjlab-Tracking-Flat-Unitree-G1-SoftRoot \
  --motion-file artifacts/video_005/motion.npz \
  --iterations 1500 \
  --num-envs 1024 \
  --save-interval 100 \
  --experiment-name body29dof_only_soft_root \
  --run-name train_video_005_soft_root_1500 \
  --video \
  --video-interval 100 \
  --video-length 285
```

## Robust Fine-Tune

To improve Gate B we used a robust task variant:

```bash
python3 -m body29_pipeline.cli train \
  --task-id Mjlab-Tracking-Flat-Unitree-G1-SoftRootRobust \
  --motion-file artifacts/video_005/motion.npz \
  --iterations 1000 \
  --num-envs 1024 \
  --save-interval 100 \
  --experiment-name body29dof_only_soft_root \
  --run-name finetune_softrootrobust_from1499_1000 \
  --resume \
  --load-run 2026-03-27_22-32-12_train_video_005_soft_root_1500 \
  --load-checkpoint model_1499.pt
```

## Strict Re-Refine

We then refined back on the stricter `SoftRoot` task:

```bash
python3 -m body29_pipeline.cli train \
  --task-id Mjlab-Tracking-Flat-Unitree-G1-SoftRoot \
  --motion-file artifacts/video_005/motion.npz \
  --iterations 600 \
  --num-envs 1024 \
  --save-interval 100 \
  --experiment-name body29dof_only_soft_root \
  --run-name refine_softroot_from_robust1800_600 \
  --resume \
  --load-run 2026-03-27_23-27-31_finetune_softrootrobust_from1499_1000 \
  --load-checkpoint model_1800.pt
```

## Why This Curriculum

- `SoftRoot` gave better visible single-clip tracking than rigid root variants
- `SoftRootRobust` improved moderate-noise survival for Gate B
- the refine stage recovered some fidelity after the robust phase

## Current Best Candidate

The current candidate selected for gating and sim2sim is:

- `model_2399.pt` from the refine stage

