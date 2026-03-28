# Team Checklist

## For A Fresh Machine

1. Clone this repo.
2. Install the local package with `pip install -e .`.
3. Run `bash scripts/bootstrap_upstreams.sh`.
4. Run `uv sync` inside `research/mjlab`.
5. Place the input bundle in `00_RL_input/video_005/`.
6. Run `validate --strict`.
7. Run `convert --render`.
8. Run the `G1MovesCompat` smoke training.
9. Export ONNX explicitly with `export-onnx`.
10. Run parity and ONNX rollout checks.
11. Run standalone `sim2sim` against the `g1_29dof_rev_1_0.xml` default or pass a custom XML.
12. Only then start the long single-clip training run.

## Files To Review First

- [`README.md`](../README.md)
- [`docs/03-training-curriculum.md`](03-training-curriculum.md)
- [`docs/04-evaluation-and-gates.md`](04-evaluation-and-gates.md)
- [`docs/05-sim2sim.md`](05-sim2sim.md)
- [`docs/07-training-explainer.md`](07-training-explainer.md)

## Review Expectations

Teammates reviewing this repo should be able to answer:

- what inputs are required
- what was changed in upstream `mjlab`
- which tracking task is active right now
- what the actor-only ONNX contract is
- how the best checkpoint will be selected
- what evidence shows the policy learned inside `mjlab`
- how the standalone runner reconstructs the observation vector
