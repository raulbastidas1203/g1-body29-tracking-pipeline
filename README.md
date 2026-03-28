# G1 Body29 Tracking Pipeline

This repository packages the local work we did for:

- `video2robot` -> `mjlab`
- single-clip RL tracking for `Unitree G1` 29 DoF
- ONNX export and parity checks
- a clean baseline aligned with the `g1-moves` / `mjlab` training route

It is intentionally lightweight:

- this repo contains our own pipeline code and documentation
- `mjlab`, `unitree_mujoco`, and `unitree_sdk2_python` are pulled from upstream on demand
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
  --task-id Mjlab-Tracking-Flat-Unitree-G1 \
  --iterations 30000 \
  --num-envs 1024 \
  --save-interval 2000 \
  --run-name train_video_005_base

python3 -m body29_pipeline.cli evaluate \
  --task-id Mjlab-Tracking-Flat-Unitree-G1 \
  --checkpoint-file research/mjlab/logs/rsl_rl/body29dof_only/<run>/model_29999.pt
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
- `unitree_mujoco`: `https://github.com/unitreerobotics/unitree_mujoco` at `1a37b05`
- `unitree_sdk2_python`: `https://github.com/unitreerobotics/unitree_sdk2_python` at `ab0d8ae`

## Notes

- This repo is `body_29dof_only` by design.
- Dex3 fingers stay fixed and outside policy / reward / motion reference.
- The active route is now the standard `mjlab` tracking task, matching the public `g1-moves` workflow as closely as possible.
- The old `unitree_mujoco` baseline runner was retired after cleanup; a new sim2sim path will be added only once it matches the deployment contract we actually want.
