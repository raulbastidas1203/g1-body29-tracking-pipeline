# Sim2Sim

## Status

The active `sim2sim` route is now the standalone `g1-moves`-compatible runner.

What this means:

- policy is exported as actor-only ONNX: `obs -> actions`
- reference motion stays external in `motion.npz`
- the standalone runner reconstructs observations from `onnx + npz + xml`
- PD gains, default joint positions, and action scale come from ONNX metadata

## Default XML

The default XML path in this repo is:

`research/TWIST2/assets/g1/g1_29dof_rev_1_0.xml`

This is not bundled in this repository; `bootstrap_upstreams.sh` clones `TWIST2` so the default path exists on a fresh machine.

## Command

```bash
python3 -m body29_pipeline.cli sim2sim \
  --checkpoint-file research/mjlab/logs/rsl_rl/body29dof_g1_moves_compat/<run>/model_<step>.pt \
  --motion-file artifacts/video_005/motion.npz \
  --xml-file research/TWIST2/assets/g1/g1_29dof_rev_1_0.xml \
  --output-video artifacts/video_005/g1_moves_compat_sim2sim.mp4 \
  --output-metrics artifacts/video_005/g1_moves_compat_sim2sim.json
```

## What The Runner Does

- loads the actor-only ONNX
- reads `joint_names`, `action_scale`, `joint_stiffness`, `joint_damping`, `anchor_body_name`, and body-name metadata
- selects the correct reference bodies from `motion.npz`
- rebuilds the 160-dim observation vector in the `g1-moves` order
- runs MuJoCo at the simulation timestep declared in the ONNX metadata
- applies PD torques to the XML actuators
- records MP4 and JSON metrics

## Notes

- The XML framebuffer may be smaller than 1280x720; the runner auto-clamps to the XML offscreen framebuffer size.
- If standalone falls while `mjlab` rollout is fine, treat that as a contract/debug issue first, not as proof that PPO failed.
