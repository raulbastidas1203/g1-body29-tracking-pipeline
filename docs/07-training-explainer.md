# Training Explainer

## Why This File Exists

This note explains:

- how the `mjlab` training loop works for this project
- what the policy actually sees and outputs
- how we decide whether the policy is learning
- what changed across the three main task variants we tried
- why `Gate B` and `Gate C` were useful but still did not guarantee `sim2sim`

The goal is not to restate every source file. The goal is to make review easier for teammates who want to understand the logic behind the experiments.

## What We Are Training

We are training a single-clip motion tracking policy for `Unitree G1` body-only `29 DoF`.

The reference motion comes from:

- `video2robot` output
- converted to `robot_motion.csv`
- converted again to `motion.npz` with `mjlab.scripts.csv_to_npz`

The policy is trained in `mjlab` on a tracking task from the family:

- `Mjlab-Tracking-Flat-Unitree-G1-*`

For this project the policy controls:

- legs
- waist
- arms

It does not control:

- Dex3 fingers

## What The Policy Receives

The actor observation is effectively `160` dimensions:

1. reference joint position at the current motion frame: `29`
2. reference joint velocity at the current motion frame: `29`
3. anchor position error in body frame: `3`
4. anchor orientation error in 6D rotation form: `6`
5. base angular velocity: `3`
6. base linear velocity: `3`
7. current joint position relative to default pose: `29`
8. current joint velocity: `29`
9. previous action: `29`

Total: `29 + 29 + 3 + 6 + 3 + 3 + 29 + 29 + 29 = 160`

This matters because `sim2sim` must reproduce these semantics very closely. A policy that is good in `mjlab` can still fail if the deployment side computes even a few of these terms differently.

## What The Policy Outputs

The policy outputs a `29`-dimensional action vector.

That raw action is not a torque yet. In the training stack it becomes:

- `target_joint_pos = action * action_scale + default_joint_pos`

Then MuJoCo built-in position actuators handle the low-level control in the `mjlab` environment.

This is one of the most important differences with our current `unitree_mujoco` `sim2sim` runner: there we manually reconstruct a PD torque loop, so the plant is similar but not identical.

## PPO Setup

The G1 tracking task uses PPO with this base configuration:

- actor MLP: `512 -> 256 -> 128`, `ELU`
- critic MLP: `512 -> 256 -> 128`, `ELU`
- observation normalization: enabled
- action distribution: Gaussian, scalar std, initial std `1.0`
- PPO clip parameter: `0.2`
- entropy coefficient: `0.005`
- learning rate: `1e-3`, adaptive schedule
- learning epochs per iteration: `5`
- mini-batches per iteration: `4`
- `gamma = 0.99`
- `lambda = 0.95`
- desired KL: `0.01`
- max grad norm: `1.0`
- rollout length: `24` steps per environment per iteration

## What An Iteration Means

An iteration is not one episode.

An iteration means:

- collect `24` environment steps from each parallel environment
- build PPO rollouts from that batch
- optimize actor and critic for several epochs and mini-batches
- optionally save a checkpoint

Examples:

- smoke run with `64` envs:
  - `64 * 24 = 1,536` env steps per iteration
- real training with `1024` envs:
  - `1024 * 24 = 24,576` env steps per iteration
- `1000` iterations with `1024` envs:
  - `24,576,000` env steps
- `1500` iterations with `1024` envs:
  - `36,864,000` env steps

So when we say "1000 iterations", that is already a serious training run, not a toy run.

## How The Task Rewards Learning

The tracking task rewards the policy for matching the motion reference in several ways:

- global anchor position
- global anchor orientation
- relative key-body positions
- relative key-body orientations
- body linear velocity
- body angular velocity

It also penalizes:

- large action changes
- joint limit violations
- self-collisions

This combination is why the policy can sometimes "dance well" but still drift globally: if relative body matching is good enough, the robot may preserve the style of the clip while walking away from the ghost.

## How We Measure Whether It Is Learning

We used four layers of evidence.

### 1. Smoke Run

Purpose:

- confirm the pipeline works end to end
- confirm the task resets, the optimizer runs, checkpoints save, ONNX exports

What it does not prove:

- good tracking
- robustness
- transfer readiness

### 2. Standard Evaluation

This runs many parallel episodes and reports aggregate metrics.

The most important metric fields are:

- `success_rate`
  - fraction of episodes that survive until timeout rather than terminating early
- `mpkpe`
  - mean per-keybody position error in world frame
- `r_mpkpe`
  - root-relative pose error
- `joint_vel_error`
  - how different the joint velocities are from the reference
- `ee_pos_error`
  - average end-effector position error
- `ee_ori_error`
  - average end-effector orientation error

How to read them:

- low `mpkpe` and low `r_mpkpe`
  - good global tracking and good relative body tracking
- low `r_mpkpe` but worse `mpkpe`
  - the dance shape is right, but the robot drifts in world space
- low pose errors but low `success_rate`
  - good nominal tracking, weak robustness
- high `joint_vel_error`
  - the pose may look acceptable, but the motion is dynamically wrong or too jerky

### 3. Full-Clip Rollout Without Terminations

This is critical for dance.

We record a rollout over the whole clip with terminations disabled so we can see:

- if the style is correct
- if the root walks away from the ghost
- if the robot lags behind the reference
- if a checkpoint only looks good because it terminates early

This was often more informative than `success_rate` by itself.

### 4. Gates

We used two gates before trying `sim2sim`.

`Gate B`

- moderate-noise evaluation
- `64` envs
- target: `success_rate >= 0.5`

`Gate C`

- PT / ONNX parity
- we compare actions step by step on identical observations

These were useful gates, but they still only validated behavior inside the `mjlab` contract.

## The Three Main Cases We Tried

## Case 1: Base Tracking Task

Task:

- `Mjlab-Tracking-Flat-Unitree-G1`

Intent:

- verify that single-clip imitation works at all
- establish a first serious baseline

What happened:

- the robot learned the dance structure fairly well
- but it tended to walk forward relative to the ghost

Signals:

- smoke baseline in `artifacts/video_005/metrics.json`
  - `success_rate = 0.0`
  - `mpkpe = 0.0636`
  - `r_mpkpe = 0.0610`
  - `joint_vel_error = 14.7170`
  - `ee_pos_error = 0.1099`
  - `ee_ori_error = 0.5091`
- later full rollout of the stronger base checkpoint in `artifacts/video_005/policy_rollout_model_999.json`
  - `mpkpe = 0.0656`
  - `r_mpkpe = 0.0561`
  - `joint_vel_error = 8.6653`
  - `ee_pos_error = 0.1118`
  - `ee_ori_error = 0.3580`

Interpretation:

- body tracking improved a lot over the smoke baseline
- the remaining visible problem was global root drift, not total failure of imitation

## Case 2: PreciseRoot

Task:

- `Mjlab-Tracking-Flat-Unitree-G1-PreciseRoot`

Intent:

- stop the policy from "cheating" by matching the body pose while drifting away from the reference in world XY

What changed:

- tighter root tracking reward
- no `push_robot`
- stricter anchor termination in full XYZ
- less slack around the root

What happened:

- anchor drift got better
- but the task became more brittle
- checkpoints in the middle often looked unstable or fell
- total body tracking quality got worse than the best base checkpoint

Measured tradeoff from `artifacts/video_005/precise_root_comparison.json`:

- old mean anchor XY error: `0.8914`
- precise-root mean anchor XY error: `0.5273`
- old full-rollout `mpkpe`: `0.0656`
- precise-root full-rollout `mpkpe`: `0.0693`
- old `joint_vel_error`: `8.6653`
- precise-root `joint_vel_error`: `10.3267`
- old `ee_ori_error`: `0.3580`
- precise-root `ee_ori_error`: `0.4009`

Interpretation:

- the hard root constraint fixed part of the walking-away problem
- but it over-constrained the policy and made the dance less natural

## Case 3: SoftRoot

Task:

- `Mjlab-Tracking-Flat-Unitree-G1-SoftRoot`

Intent:

- keep the robot near the shadow
- but still allow a small corridor for natural balance correction

What changed relative to `PreciseRoot`:

- small allowed XY corridor instead of near-zero drift allowance
- root reward still important, but less rigid
- no `push_robot`
- cleaner `play` mode with startup noise removed for checkpoint video comparison

What happened:

- this became the best single-clip compromise
- the dance quality improved
- the forward drift was reduced dramatically

Measured from `artifacts/video_005/soft_root_comparison.json`:

- old full-rollout `mpkpe`: `0.0656`
- `SoftRoot model_1499` full-rollout `mpkpe`: `0.0566`
- old `r_mpkpe`: `0.0561`
- `SoftRoot model_1499` `r_mpkpe`: `0.0471`
- old `ee_pos_error`: `0.1118`
- `SoftRoot model_1499` `ee_pos_error`: `0.1058`
- old `ee_ori_error`: `0.3580`
- `SoftRoot model_1499` `ee_ori_error`: `0.3239`
- old mean anchor XY error: `1.2446`
- `SoftRoot model_1499` mean anchor XY error: `0.0649`

Interpretation:

- `SoftRoot` solved the main visual problem much better than the previous two approaches
- it became the foundation for the later gating runs

## What Happened After The Three Cases

The three cases above were the main design variants.

After that we did curriculum-style refinement:

1. train `SoftRoot` until `model_1499`
2. fine-tune on `SoftRootRobust` to improve moderate-noise survival
3. refine back on stricter `SoftRoot`

That produced the final candidate `model_2399`.

From `artifacts/video_005/gate_status_and_sim2sim_summary.json`:

- `Gate B success_rate = 0.546875`
- PT rollout `mpkpe = 0.0575`
- ONNX rollout `mpkpe = 0.0573`
- PT / ONNX mean action difference: `2.85e-07`

Interpretation:

- the policy was strong enough inside `mjlab`
- ONNX export was faithful
- but the jump to `unitree_mujoco` still failed, which now looks like a sim2sim interface problem rather than a training problem

## Why A Checkpoint Can Look Better Than Another Even If It Is Later

PPO is not monotonic.

This means:

- `model_600` can look better than `model_700`
- `model_999` can recover after worse intermediate checkpoints
- the best checkpoint is often not the final one

That is why we saved videos every `100` checkpoints and compared:

- quantitative evaluation
- full-clip rollout quality
- root drift relative to the ghost

## What We Actually Selected As "Best"

We did not use a single number.

We selected checkpoints by balancing:

- visible full-clip dance quality
- root drift
- evaluation metrics
- ONNX parity
- moderate-noise robustness

That is why:

- `model_1499` was the best clean `SoftRoot` tracking checkpoint
- `model_2399` became the best gate-passing checkpoint for sim2sim entry

## Why Passing The Gates Was Not Enough For `sim2sim`

The gates proved:

- the policy tracks well in `mjlab`
- the ONNX export matches the PyTorch policy

They did not prove:

- that `unitree_mujoco` computes the same observation semantics
- that the deployment-side actuator model matches the training-side actuator model
- that the chosen XML uses the same IMU and anchor conventions

That is the main reason the current `sim2sim` fails even though the training results themselves were legitimate.

## Practical Review Rule

When reviewing a new run, ask these questions in order:

1. does the full-clip rollout still look like the target dance?
2. does the root stay near the ghost?
3. do `mpkpe` and `r_mpkpe` improve together?
4. does `success_rate` hold under moderate noise?
5. does ONNX still match PT?

If the answer is yes to all five, the next bottleneck is usually sim2sim integration, not PPO.
