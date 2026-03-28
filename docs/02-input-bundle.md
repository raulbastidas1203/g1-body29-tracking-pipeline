# Input Bundle

## Expected Files

The default workspace layout assumes:

```text
00_RL_input/
  video_005/
    robot_motion.csv
    robot_motion.pkl
```

## Bundle Meaning

- `robot_motion.csv`
  - shape `[T, 36]`
  - `root_pos(3) + root_quat_xyzw(4) + dof_pos(29)`
- `robot_motion.pkl`
  - audit/debug source with richer metadata

## Validate Before Training

```bash
python3 -m body29_pipeline.cli validate --strict
```

This checks:

- frame count agreement
- quaternion normalization
- CSV vs PKL agreement
- 29 DoF shape
- joint limit violations against the G1 asset

## Convert Into Local Training Motion

```bash
python3 -m body29_pipeline.cli convert --render
```

Outputs:

- `artifacts/video_005/motion.npz`
- `artifacts/video_005/motion.mp4`

## Important Assumption

The current pipeline is for:

- `Unitree G1`
- `29 DoF`
- body-only policy
- Dex3 fingers excluded from motion and policy

