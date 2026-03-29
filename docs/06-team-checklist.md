# Team Checklist

## Fresh Reproduction

1. clone this repo
2. install the local package with `pip install -e .`
3. run `bash scripts/bootstrap_upstreams.sh`
4. place the input bundle in `00_RL_input/video_005/`
5. run `validate --strict`
6. run `convert --render`
7. run the `G1MovesCompat` smoke training
8. run the long single-clip training
9. evaluate checkpoints inside `mjlab`
10. export ONNX
11. run RoboJuDo sim2sim
12. compare checkpoints by transfer, not only by in-sim reward

## Files To Read First

- [`README.md`](../README.md)
- [`docs/03-training-curriculum.md`](03-training-curriculum.md)
- [`docs/05-sim2sim.md`](05-sim2sim.md)
- [`docs/07-training-explainer.md`](07-training-explainer.md)
- [`docs/08-results.md`](08-results.md)

## Questions A Reviewer Should Be Able To Answer

- what the input bundle looks like
- what task was actually used for the final run
- how `motion.npz` is generated
- which checkpoints were saved
- how checkpoint quality is measured in `mjlab`
- why RoboJuDo is the preferred sim2sim route here
- why `model_14000` is currently the recommended transfer checkpoint
