# Team Checklist

## For A Fresh Machine

1. Clone this repo.
2. Install the local package with `pip install -e .`.
3. Run `bash scripts/bootstrap_upstreams.sh`.
4. Run `uv sync` inside `research/mjlab`.
5. Place the input bundle in `00_RL_input/video_005/`.
6. Run `validate --strict`.
7. Run `convert --render`.
8. Run the smoke training.
9. Run the main `SoftRoot` training.
10. Evaluate, record rollout, and compare ONNX.
11. Run sim2sim only after Gate B and Gate C are closed.

## Files To Review First

- [`README.md`](../README.md)
- [`docs/03-training-curriculum.md`](03-training-curriculum.md)
- [`docs/04-evaluation-and-gates.md`](04-evaluation-and-gates.md)
- [`docs/05-sim2sim.md`](05-sim2sim.md)

## Review Expectations

Teammates reviewing this repo should be able to answer:

- what inputs are required
- what was changed in upstream `mjlab`
- which task variants were used
- how the best checkpoint was selected
- what gate threshold was used for sim2sim entry
- what still fails in sim2sim
