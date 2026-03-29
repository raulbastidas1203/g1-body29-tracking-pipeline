# Sim2Sim

## Active Path

The active sim2sim route is the RoboJuDo-style runner under:

- `research/g1-moves/RoboJuDo/scripts/eval_mjlab_g1moves_robojudo.py`

This is the path that gave the best transfer results for the current policy family.

## XML

The XML we actually used is:

- `research/g1-moves/RoboJuDo/assets/robots/g1/g1_29dof_rev_1_0.xml`

## Contract

The runner consumes:

- actor-only ONNX
- `motion.npz`
- RoboJuDo G1 XML

The ONNX metadata supplies:

- `joint_names`
- `default_joint_pos`
- `action_scale`
- `joint_stiffness`
- `joint_damping`
- `anchor_body_name`
- `body_names`

## Working Mode

For the current `mjlab`-trained checkpoints, the best working mode was:

- `action_mode = scaled_offset`
- `obs_default = metadata`

This performed better than the literal direct-target mode.

## Example Command

```bash
cd research/g1-moves/RoboJuDo
./.venv/bin/python scripts/eval_mjlab_g1moves_robojudo.py \
  --onnx-file /path/to/model.onnx \
  --motion-file /home/raul/00_cursor/RL/artifacts/video_005/motion.npz \
  --xml-file /home/raul/00_cursor/RL/research/g1-moves/RoboJuDo/assets/robots/g1/g1_29dof_rev_1_0.xml \
  --output-video /path/to/output.mp4 \
  --output-metrics /path/to/output.json \
  --action-mode scaled_offset \
  --obs-default metadata \
  --video-width 640 \
  --video-height 480
```

## Metrics To Watch

- `mpkpe`
- `r_mpkpe`
- `joint_vel_error`
- `anchor_xy_error`
- `anchor_xy_error_max`

## Current Best

At the time of writing, the best committed transfer result is:

- `model_14000`

See:

- [`docs/results/robojudo_model_14000_full_scaled.json`](results/robojudo_model_14000_full_scaled.json)
