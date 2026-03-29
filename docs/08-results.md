# Results Snapshot

This file freezes the main metrics that were copied into the repo for `video_005`.

## `mjlab`

| Checkpoint | success_rate | mpkpe | r_mpkpe | joint_vel_error | ee_pos_error | ee_ori_error |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `model_8000` | `1.0000` | `0.0482` | `0.0345` | `5.8182` | `0.0713` | `0.2041` |
| `model_10000` | `1.0000` | `0.0471` | `0.0342` | `5.8426` | `0.0710` | `0.2003` |

Raw files:

- [`results/model_8000_eval.json`](results/model_8000_eval.json)
- [`results/model_10000_eval.json`](results/model_10000_eval.json)

## RoboJuDo

| Checkpoint | mpkpe | r_mpkpe | joint_vel_error | anchor_xy_error | anchor_xy_error_max |
| --- | ---: | ---: | ---: | ---: | ---: |
| `model_8000` | `0.1155` | `0.0284` | `4.8246` | `0.1002` | `0.1875` |
| `model_10000` | `0.0915` | `0.0275` | `4.7982` | `0.0748` | `0.1601` |
| `model_12000` | `0.0936` | `0.0283` | `4.7258` | `0.0758` | `0.1776` |
| `model_14000` | `0.0857` | `0.0286` | `4.7900` | `0.0655` | `0.1770` |

Raw files:

- [`results/robojudo_model_8000_full_scaled.json`](results/robojudo_model_8000_full_scaled.json)
- [`results/robojudo_model_10000_full_scaled.json`](results/robojudo_model_10000_full_scaled.json)
- [`results/robojudo_model_12000_full_scaled.json`](results/robojudo_model_12000_full_scaled.json)
- [`results/robojudo_model_14000_full_scaled.json`](results/robojudo_model_14000_full_scaled.json)

## Current Recommendation

- best `mjlab` checkpoint among evaluated ones: `model_10000`
- best RoboJuDo transfer checkpoint: `model_14000`
