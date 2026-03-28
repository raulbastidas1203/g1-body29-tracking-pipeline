# G1 Body29 Tracking Pipeline

This repository packages the local work we did for:

- `video2robot` -> `mjlab`
- single-clip RL tracking for `Unitree G1` 29 DoF
- `g1-moves`-compatible ONNX export and parity checks
- standalone `sim2sim` against a `g1-moves`-compatible MuJoCo XML

It is intentionally lightweight:

- this repo contains our own pipeline code and documentation
- `mjlab`, `TWIST2`, `unitree_mujoco`, and `unitree_sdk2_python` are pulled from upstream on demand
- our `mjlab` changes are carried as a patch in [`patches/mjlab-body29-local-flow.patch`](patches/mjlab-body29-local-flow.patch)

## What Is Included

- [`body29_pipeline`](body29_pipeline)
  - local CLI for validate / convert / train / evaluate / rollout / ONNX parity
- [`patches/mjlab-body29-local-flow.patch`](patches/mjlab-body29-local-flow.patch)
  - our local `mjlab` modifications and helper scripts
- [`scripts/bootstrap_upstreams.sh`](scripts/bootstrap_upstreams.sh)
  - clones pinned upstreams and applies the `mjlab` patch
- [`scripts/apply_mjlab_patch.sh`](scripts/apply_mjlab_patch.sh)
  - reapplies the patch if a teammate already cloned `mjlab`
- [`upstreams/lock.json`](upstreams/lock.json)
  - pinned upstream URLs and commits
- [`docs`](docs)
  - step-by-step usage and replication notes

## Quickstart

1. Clone this repo.
2. Install the local helper package:

```bash
python3 -m pip install -e .
```

3. Bootstrap upstream dependencies:

```bash
bash scripts/bootstrap_upstreams.sh
```

4. Put your `video2robot` bundle under:

```text
00_RL_input/video_005/
  robot_motion.csv
  robot_motion.pkl
```

5. Validate and convert:

```bash
python3 -m body29_pipeline.cli validate --strict
python3 -m body29_pipeline.cli convert --render
```

6. Train and evaluate:

```bash
python3 -m body29_pipeline.cli train \
  --task-id Mjlab-Tracking-Flat-Unitree-G1-G1MovesCompat \
  --iterations 15000 \
  --num-envs 2048 \
  --save-interval 2000 \
  --run-name train_video_005_g1_moves_compat

python3 -m body29_pipeline.cli evaluate \
  --task-id Mjlab-Tracking-Flat-Unitree-G1-G1MovesCompat \
  --checkpoint-file research/mjlab/logs/rsl_rl/body29dof_g1_moves_compat/<run>/model_*.pt
```

7. Export and validate the actor-only ONNX:

```bash
python3 -m body29_pipeline.cli export-onnx
python3 -m body29_pipeline.cli compare-onnx --num-steps 285
python3 -m body29_pipeline.cli record-rollout-onnx --num-steps 285
```

8. Run standalone `sim2sim`:

```bash
python3 -m body29_pipeline.cli sim2sim \
  --num-steps 285 \
  --xml-file research/TWIST2/assets/g1/g1_29dof_rev_1_0.xml
```

## Documentation Map

- [`docs/00-overview.md`](docs/00-overview.md)
- [`docs/01-bootstrap.md`](docs/01-bootstrap.md)
- [`docs/02-input-bundle.md`](docs/02-input-bundle.md)
- [`docs/03-training-curriculum.md`](docs/03-training-curriculum.md)
- [`docs/04-evaluation-and-gates.md`](docs/04-evaluation-and-gates.md)
- [`docs/05-sim2sim.md`](docs/05-sim2sim.md)
- [`docs/06-team-checklist.md`](docs/06-team-checklist.md)
- [`docs/07-training-explainer.md`](docs/07-training-explainer.md)

## Pinned Upstreams

- `mjlab`: `https://github.com/mujocolab/mjlab` at `6abd0eb`
- `TWIST2`: `https://github.com/amazon-far/TWIST2` at `d5c7108`
- `unitree_mujoco`: `https://github.com/unitreerobotics/unitree_mujoco` at `1a37b05`
- `unitree_sdk2_python`: `https://github.com/unitreerobotics/unitree_sdk2_python` at `ab0d8ae`

## Notes

- This repo is `body_29dof_only` by design.
- Dex3 fingers stay fixed and outside policy / reward / motion reference.
- The active route is now `Mjlab-Tracking-Flat-Unitree-G1-G1MovesCompat`.
- The exported ONNX is `obs -> actions` only, with motion left external in `motion.npz`.
- The standalone `sim2sim` path targets the `g1-moves`-compatible `g1_29dof_rev_1_0.xml` fallback and reads all control metadata from the ONNX.
