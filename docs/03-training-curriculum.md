# Training Plan

## Active Route

The active documented route in this repo is:

- `Mjlab-Tracking-Flat-Unitree-G1-G1MovesCompat`

This is the task we actually used for the long public run documented in the README.

## Why This Task

It keeps the parts we needed for transfer:

- `g1-moves`-style actor observation layout
- actor-only ONNX export
- explicit control metadata in ONNX
- compatibility with the RoboJuDo sim2sim runner

## Recommended Training Order

1. validate the input bundle
2. convert to `motion.npz`
3. replay the reference motion
4. run a smoke training job
5. run the long single-clip training job
6. evaluate checkpoints inside `mjlab`
7. export ONNX
8. compare checkpoints in RoboJuDo sim2sim

## Smoke Run

```bash
python3 -m body29_pipeline.cli smoke-train \
  --task-id Mjlab-Tracking-Flat-Unitree-G1-G1MovesCompat \
  --iterations 100 \
  --num-envs 64 \
  --save-interval 50 \
  --run-name smoke_video_005_g1_moves_compat
```

## Long Run

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

## Monitoring

```bash
tensorboard --logdir research/mjlab/logs/rsl_rl/body29dof_g1_moves_compat
```

Focus on:

- `Train/mean_episode_length`
- `Train/mean_reward`
- `Metrics/motion/error_body_pos`
- `Metrics/motion/error_anchor_pos`
- `Metrics/motion/error_joint_vel`
- `Episode_Termination/ee_body_pos`

## Checkpoint Selection

We do not assume the last checkpoint is the best checkpoint.

Selection order:

1. strong `mjlab` metrics
2. clean full-clip replay
3. strong RoboJuDo transfer metrics
4. visual quality in sim2sim

That is why the repo currently treats:

- `model_10000` as the best measured `mjlab` checkpoint
- `model_14000` as the best current RoboJuDo transfer checkpoint
