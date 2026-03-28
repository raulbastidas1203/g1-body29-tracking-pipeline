# Sim2Sim

## Status

The previous `unitree_mujoco` baseline runner was intentionally removed during cleanup.

We are no longer treating that path as the active route for this repository because it mixed:

- a policy trained with the standard `mjlab` G1 tracking contract
- a standalone runner with different deployment assumptions
- and an official MuJoCo XML/controller stack that did not match training closely enough

## Active Direction

The current direction is to follow the public `g1-moves` pattern more closely:

- train in the standard `mjlab` tracking task
- validate with `mjlab` play / rollout first
- keep the training/deployment contract consistent
- only add a standalone sim2sim path once the target XML, observation semantics, and control loop are frozen

## What Not To Do

Do not revive the old `body29_pipeline.cli sim2sim` command from older notes.

That route was retired on purpose so the repo does not keep pointing teammates at a stale baseline that we already decided not to pursue.

## Next Sim2Sim Milestone

Before a new sim2sim path is added back, we need all of the following:

- a chosen deployment stack
- a chosen target XML
- a confirmed observation contract
- a confirmed action contract
- a confirmed controller contract

Once those are frozen, this document will be replaced with the new reproducible sim2sim procedure.
