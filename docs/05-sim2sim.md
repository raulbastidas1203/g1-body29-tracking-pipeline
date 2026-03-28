# Sim2Sim

## Purpose

The goal of sim2sim here is:

- keep the trained `mjlab` policy fixed
- execute it in a different simulator stack
- measure how much transfer survives before touching real hardware

## Current Command

```bash
python3 -m body29_pipeline.cli sim2sim \
  --checkpoint-file research/mjlab/logs/rsl_rl/body29dof_only_soft_root/<run>/model_2399.pt \
  --motion-file artifacts/video_005/motion.npz \
  --output-video artifacts/video_005/sim2sim_unitree_mujoco/model_2399_full.mp4 \
  --output-metrics artifacts/video_005/sim2sim_unitree_mujoco/model_2399_full.json \
  --num-steps 285 \
  --onnx-provider cpu
```

## What The Current Sim2Sim Runner Does

- loads the official `unitree_mujoco` G1 29-DoF XML
- loads the exported ONNX policy
- reconstructs the 160-dim tracking observation
- applies the same action semantics used in `mjlab`
- runs a PD torque controller
- records a video and a metrics JSON

## Current Status

The first full transfer is not yet good enough.

Current full-run baseline:

- `fell = true`
- `body_mpkpe ~= 1.01`
- `r_mpkpe ~= 0.45`

This is still useful because it gives us:

- a reproducible baseline
- a concrete alternate simulator target
- a place to debug transfer rather than retraining blind

## Expected Next Work

- tighten observation matching between `mjlab` and `unitree_mujoco`
- tune the sim2sim controller loop
- inspect remaining actuator / velocity / frame-convention mismatches

