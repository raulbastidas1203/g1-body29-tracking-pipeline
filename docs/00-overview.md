# Overview

## Goal

This repo captures a reproducible path from:

1. `video2robot` motion output
2. `mjlab` motion imitation training for `Unitree G1`
3. checkpoint + ONNX export
4. first `unitree_mujoco` sim2sim validation

## Scope

This is not a monorepo of every dependency.

- Included:
  - our pipeline code
  - our `mjlab` patch
  - documentation
  - bootstrap scripts
- Not included:
  - full upstream clones
  - large input bundles
  - training artifacts and experiment videos

## Current Pipeline

- Input: `robot_motion.csv` + `robot_motion.pkl`
- Canonical motion format: local `motion.npz`
- Training family: `Mjlab-Tracking-Flat-Unitree-G1-*`
- Current policy mode: `body_29dof_only`
- Current hand strategy: Dex3 fixed safe pose

## Current State

- Gate B passed with moderate-noise evaluation on `SoftRootRobust`
- Gate C passed with PT / ONNX parity
- Sim2sim infrastructure is implemented
- Full transfer to `unitree_mujoco` still needs more tuning

