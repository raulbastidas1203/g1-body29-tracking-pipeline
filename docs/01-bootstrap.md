# Bootstrap

## Required Tools

- `git`
- `python3`
- `pip`
- `uv`
- `gh` if you want to publish changes back to GitHub

## Install Local Helper Package

From the repo root:

```bash
python3 -m pip install -e .
```

## Clone and Pin Upstreams

Run:

```bash
bash scripts/bootstrap_upstreams.sh
```

This will:

1. clone `mjlab`
2. checkout `6abd0eb`
3. apply [`patches/mjlab-body29-local-flow.patch`](../patches/mjlab-body29-local-flow.patch)
4. clone `unitree_mujoco`
5. checkout `1a37b05`
6. clone `unitree_sdk2_python`
7. checkout `ab0d8ae`

## Sync `mjlab`

After bootstrap:

```bash
cd research/mjlab
uv sync
```

## Layout After Bootstrap

```text
g1-body29-tracking-pipeline/
  body29_pipeline/
  docs/
  patches/
  scripts/
  upstreams/
  research/
    mjlab/
    unitree_mujoco/
    unitree_sdk2_python/
```
