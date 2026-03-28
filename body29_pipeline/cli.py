from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
from pathlib import Path

from body29_pipeline.constants import (
  DEFAULT_CSV_PATH,
  DEFAULT_EXPERIMENT_NAME,
  DEFAULT_INPUT_DIR,
  DEFAULT_MANIFEST_PATH,
  DEFAULT_NPZ_PATH,
  DEFAULT_OUTPUT_DIR,
  DEFAULT_PKL_PATH,
  DEFAULT_PROJECT_NAME,
  DEFAULT_ROLLOUT_METRICS_PATH,
  DEFAULT_ROLLOUT_VIDEO_PATH,
  DEFAULT_TASK_ID,
  DEFAULT_VIDEO_PATH,
  MJLAB_G1_XML,
  MJLAB_ROOT,
)
from body29_pipeline.validate_input import validate_motion_bundle


def run_command(cmd: list[str], *, cwd: Path = MJLAB_ROOT) -> int:
  env = os.environ.copy()
  env.setdefault("MUJOCO_GL", "egl")
  print(f"$ {shlex.join(cmd)}")
  completed = subprocess.run(cmd, cwd=cwd, env=env, check=False)
  return completed.returncode


def latest_checkpoint(experiment_name: str) -> Path:
  root = MJLAB_ROOT / "logs" / "rsl_rl" / experiment_name
  if not root.exists():
    raise FileNotFoundError(f"No logs found for experiment: {experiment_name}")

  run_dirs = sorted([p for p in root.iterdir() if p.is_dir()])
  if not run_dirs:
    raise FileNotFoundError(f"No run directories found under: {root}")

  for run_dir in reversed(run_dirs):
    checkpoints = sorted(run_dir.glob("model_*.pt"))
    if checkpoints:
      return checkpoints[-1]
  raise FileNotFoundError(f"No checkpoints found under: {root}")


def default_onnx_path(checkpoint: Path) -> Path:
  run_dir = checkpoint.parent
  return run_dir / f"{run_dir.name}.onnx"


def command_validate(args: argparse.Namespace) -> int:
  summary = validate_motion_bundle(
    csv_path=args.csv,
    pkl_path=args.pkl,
    xml_path=args.g1_xml,
    manifest_path=args.manifest,
  )
  print(json.dumps(summary, indent=2))

  failed = any(
    (
      summary["csv_shape"] != [summary["pkl_num_frames"], 36],
      summary["dof_limit_violations"] != 0,
      not summary["csv_matches_pkl_root_pos"],
      not summary["csv_matches_pkl_root_rot"],
      not summary["csv_matches_pkl_dof"],
      abs(summary["root_quat_norm_min"] - 1.0) > 1e-3,
      abs(summary["root_quat_norm_max"] - 1.0) > 1e-3,
    )
  )
  return 1 if args.strict and failed else 0


def command_convert(args: argparse.Namespace) -> int:
  args.output.parent.mkdir(parents=True, exist_ok=True)
  if args.render:
    args.video.parent.mkdir(parents=True, exist_ok=True)

  cmd = [
    "uv",
    "run",
    "-m",
    "mjlab.scripts.csv_to_npz",
    "--input-file",
    str(args.csv),
    "--output-name",
    args.motion_name,
    "--input-fps",
    str(args.input_fps),
    "--output-fps",
    str(args.output_fps),
    "--device",
    args.device,
    "--output-file",
    str(args.output),
    "--wandb-mode",
    "skip",
  ]
  if args.render:
    cmd.extend(["--render", "True", "--video-file", str(args.video)])
  return run_command(cmd)


def command_smoke_train(args: argparse.Namespace) -> int:
  return command_train(args)


def command_train(args: argparse.Namespace) -> int:
  cmd = [
    "uv",
    "run",
    "train",
    args.task_id,
    "--env.commands.motion.motion-file",
    str(args.motion_file),
    "--env.scene.num-envs",
    str(args.num_envs),
    "--agent.max-iterations",
    str(args.iterations),
    "--agent.save-interval",
    str(args.save_interval),
    "--agent.logger",
    args.logger,
    "--agent.experiment-name",
    args.experiment_name,
    "--agent.run-name",
    args.run_name,
  ]
  if args.seed is not None:
    cmd.extend(["--agent.seed", str(args.seed)])
  if args.resume:
    cmd.extend(
      [
        "--agent.resume",
        "True",
        "--agent.load-run",
        args.load_run,
        "--agent.load-checkpoint",
        args.load_checkpoint,
      ]
    )
  if args.video:
    cmd.extend(
      [
        "--video",
        "True",
        "--video-length",
        str(args.video_length),
        "--video-interval",
        str(args.video_interval),
      ]
    )
  return run_command(cmd)


def command_play(args: argparse.Namespace) -> int:
  checkpoint = args.checkpoint_file or latest_checkpoint(args.experiment_name)
  cmd = [
    "uv",
    "run",
    "play",
    args.task_id,
    "--checkpoint-file",
    str(checkpoint),
    "--motion-file",
    str(args.motion_file),
  ]
  if args.viewer is not None:
    cmd.extend(["--viewer", args.viewer])
  return run_command(cmd)


def command_evaluate(args: argparse.Namespace) -> int:
  checkpoint = args.checkpoint_file or latest_checkpoint(args.experiment_name)
  args.output_file.parent.mkdir(parents=True, exist_ok=True)
  cmd = [
    "uv",
    "run",
    "-m",
    "mjlab.tasks.tracking.scripts.evaluate",
    args.task_id,
    "--checkpoint-file",
    str(checkpoint),
    "--motion-file",
    str(args.motion_file),
    "--num-envs",
    str(args.num_envs),
    "--output-file",
    str(args.output_file),
  ]
  return run_command(cmd)


def command_record_rollout(args: argparse.Namespace) -> int:
  checkpoint = args.checkpoint_file or latest_checkpoint(args.experiment_name)
  args.output_video.parent.mkdir(parents=True, exist_ok=True)
  if args.output_metrics is not None:
    args.output_metrics.parent.mkdir(parents=True, exist_ok=True)

  cmd = [
    "uv",
    "run",
    "-m",
    "mjlab.tasks.tracking.scripts.record_rollout",
    args.task_id,
    "--checkpoint-file",
    str(checkpoint),
    "--motion-file",
    str(args.motion_file),
    "--output-video",
    str(args.output_video),
    "--video-height",
    str(args.video_height),
    "--video-width",
    str(args.video_width),
  ]
  if args.output_metrics is not None:
    cmd.extend(["--output-metrics", str(args.output_metrics)])
  if args.device is not None:
    cmd.extend(["--device", args.device])
  if args.num_steps is not None:
    cmd.extend(["--num-steps", str(args.num_steps)])
  if args.no_terminations:
    cmd.extend(["--no-terminations", "True"])
  return run_command(cmd)


def command_evaluate_onnx(args: argparse.Namespace) -> int:
  checkpoint = args.checkpoint_file or latest_checkpoint(args.experiment_name)
  onnx_file = args.onnx_file or default_onnx_path(checkpoint)
  args.output_file.parent.mkdir(parents=True, exist_ok=True)
  cmd = [
    "uv",
    "run",
    "-m",
    "mjlab.tasks.tracking.scripts.evaluate_onnx",
    args.task_id,
    "--onnx-file",
    str(onnx_file),
    "--motion-file",
    str(args.motion_file),
    "--num-envs",
    str(args.num_envs),
    "--output-file",
    str(args.output_file),
  ]
  return run_command(cmd)


def command_record_rollout_onnx(args: argparse.Namespace) -> int:
  checkpoint = args.checkpoint_file or latest_checkpoint(args.experiment_name)
  onnx_file = args.onnx_file or default_onnx_path(checkpoint)
  args.output_video.parent.mkdir(parents=True, exist_ok=True)
  if args.output_metrics is not None:
    args.output_metrics.parent.mkdir(parents=True, exist_ok=True)

  cmd = [
    "uv",
    "run",
    "-m",
    "mjlab.tasks.tracking.scripts.record_rollout_onnx",
    args.task_id,
    "--onnx-file",
    str(onnx_file),
    "--motion-file",
    str(args.motion_file),
    "--output-video",
    str(args.output_video),
    "--video-height",
    str(args.video_height),
    "--video-width",
    str(args.video_width),
  ]
  if args.output_metrics is not None:
    cmd.extend(["--output-metrics", str(args.output_metrics)])
  if args.device is not None:
    cmd.extend(["--device", args.device])
  if args.num_steps is not None:
    cmd.extend(["--num-steps", str(args.num_steps)])
  if args.no_terminations:
    cmd.extend(["--no-terminations", "True"])
  return run_command(cmd)


def command_compare_onnx(args: argparse.Namespace) -> int:
  checkpoint = args.checkpoint_file or latest_checkpoint(args.experiment_name)
  onnx_file = args.onnx_file or default_onnx_path(checkpoint)
  args.output_file.parent.mkdir(parents=True, exist_ok=True)
  cmd = [
    "uv",
    "run",
    "-m",
    "mjlab.tasks.tracking.scripts.compare_pt_onnx",
    args.task_id,
    "--checkpoint-file",
    str(checkpoint),
    "--onnx-file",
    str(onnx_file),
    "--motion-file",
    str(args.motion_file),
    "--num-envs",
    str(args.num_envs),
    "--num-steps",
    str(args.num_steps),
    "--output-file",
    str(args.output_file),
  ]
  return run_command(cmd)


def build_parser() -> argparse.ArgumentParser:
  parser = argparse.ArgumentParser(
    description="Workspace helpers for the body-only G1 tracking pipeline."
  )
  subparsers = parser.add_subparsers(dest="command", required=True)

  validate_parser = subparsers.add_parser("validate")
  validate_parser.add_argument("--csv", type=Path, default=DEFAULT_CSV_PATH)
  validate_parser.add_argument("--pkl", type=Path, default=DEFAULT_PKL_PATH)
  validate_parser.add_argument("--g1-xml", type=Path, default=MJLAB_G1_XML)
  validate_parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST_PATH)
  validate_parser.add_argument("--strict", action="store_true")
  validate_parser.set_defaults(func=command_validate)

  convert_parser = subparsers.add_parser("convert")
  convert_parser.add_argument("--csv", type=Path, default=DEFAULT_CSV_PATH)
  convert_parser.add_argument("--motion-name", default=DEFAULT_PROJECT_NAME)
  convert_parser.add_argument("--input-fps", type=float, default=30.0)
  convert_parser.add_argument("--output-fps", type=float, default=50.0)
  convert_parser.add_argument("--device", default="cuda:0")
  convert_parser.add_argument("--output", type=Path, default=DEFAULT_NPZ_PATH)
  convert_parser.add_argument("--render", action="store_true")
  convert_parser.add_argument("--video", type=Path, default=DEFAULT_VIDEO_PATH)
  convert_parser.set_defaults(func=command_convert)

  smoke_parser = subparsers.add_parser("smoke-train")
  smoke_parser.add_argument("--task-id", default=DEFAULT_TASK_ID)
  smoke_parser.add_argument("--motion-file", type=Path, default=DEFAULT_NPZ_PATH)
  smoke_parser.add_argument("--iterations", type=int, default=2)
  smoke_parser.add_argument("--save-interval", type=int, default=1)
  smoke_parser.add_argument("--num-envs", type=int, default=64)
  smoke_parser.add_argument("--experiment-name", default=DEFAULT_EXPERIMENT_NAME)
  smoke_parser.add_argument("--run-name", default="smoke_video_005")
  smoke_parser.add_argument("--logger", choices=("tensorboard", "wandb"), default="tensorboard")
  smoke_parser.add_argument("--seed", type=int, default=42)
  smoke_parser.add_argument("--resume", action="store_true")
  smoke_parser.add_argument("--load-run", default=".*")
  smoke_parser.add_argument("--load-checkpoint", default="model_.*.pt")
  smoke_parser.add_argument("--video", action="store_true")
  smoke_parser.add_argument("--video-length", type=int, default=200)
  smoke_parser.add_argument("--video-interval", type=int, default=2000)
  smoke_parser.set_defaults(func=command_smoke_train)

  train_parser = subparsers.add_parser("train")
  train_parser.add_argument("--task-id", default=DEFAULT_TASK_ID)
  train_parser.add_argument("--motion-file", type=Path, default=DEFAULT_NPZ_PATH)
  train_parser.add_argument("--iterations", type=int, default=1000)
  train_parser.add_argument("--save-interval", type=int, default=100)
  train_parser.add_argument("--num-envs", type=int, default=512)
  train_parser.add_argument("--experiment-name", default=DEFAULT_EXPERIMENT_NAME)
  train_parser.add_argument("--run-name", default="train_video_005")
  train_parser.add_argument("--logger", choices=("tensorboard", "wandb"), default="tensorboard")
  train_parser.add_argument("--seed", type=int, default=42)
  train_parser.add_argument("--resume", action="store_true")
  train_parser.add_argument("--load-run", default=".*")
  train_parser.add_argument("--load-checkpoint", default="model_.*.pt")
  train_parser.add_argument("--video", action="store_true")
  train_parser.add_argument("--video-length", type=int, default=200)
  train_parser.add_argument("--video-interval", type=int, default=2000)
  train_parser.set_defaults(func=command_train)

  play_parser = subparsers.add_parser("play")
  play_parser.add_argument("--task-id", default=DEFAULT_TASK_ID)
  play_parser.add_argument("--motion-file", type=Path, default=DEFAULT_NPZ_PATH)
  play_parser.add_argument("--checkpoint-file", type=Path)
  play_parser.add_argument("--experiment-name", default=DEFAULT_EXPERIMENT_NAME)
  play_parser.add_argument("--viewer", choices=("auto", "native", "viser"))
  play_parser.set_defaults(func=command_play)

  eval_parser = subparsers.add_parser("evaluate")
  eval_parser.add_argument("--task-id", default=DEFAULT_TASK_ID)
  eval_parser.add_argument("--motion-file", type=Path, default=DEFAULT_NPZ_PATH)
  eval_parser.add_argument("--checkpoint-file", type=Path)
  eval_parser.add_argument("--experiment-name", default=DEFAULT_EXPERIMENT_NAME)
  eval_parser.add_argument("--num-envs", type=int, default=64)
  eval_parser.add_argument(
    "--output-file",
    type=Path,
    default=DEFAULT_OUTPUT_DIR / "metrics.json",
  )
  eval_parser.set_defaults(func=command_evaluate)

  rollout_parser = subparsers.add_parser("record-rollout")
  rollout_parser.add_argument("--task-id", default=DEFAULT_TASK_ID)
  rollout_parser.add_argument("--motion-file", type=Path, default=DEFAULT_NPZ_PATH)
  rollout_parser.add_argument("--checkpoint-file", type=Path)
  rollout_parser.add_argument("--experiment-name", default=DEFAULT_EXPERIMENT_NAME)
  rollout_parser.add_argument("--output-video", type=Path, default=DEFAULT_ROLLOUT_VIDEO_PATH)
  rollout_parser.add_argument(
    "--output-metrics",
    type=Path,
    default=DEFAULT_ROLLOUT_METRICS_PATH,
  )
  rollout_parser.add_argument("--video-height", type=int, default=720)
  rollout_parser.add_argument("--video-width", type=int, default=1280)
  rollout_parser.add_argument("--device")
  rollout_parser.add_argument("--num-steps", type=int)
  rollout_parser.add_argument("--no-terminations", action="store_true")
  rollout_parser.set_defaults(func=command_record_rollout)

  eval_onnx_parser = subparsers.add_parser("evaluate-onnx")
  eval_onnx_parser.add_argument("--task-id", default=DEFAULT_TASK_ID)
  eval_onnx_parser.add_argument("--motion-file", type=Path, default=DEFAULT_NPZ_PATH)
  eval_onnx_parser.add_argument("--checkpoint-file", type=Path)
  eval_onnx_parser.add_argument("--onnx-file", type=Path)
  eval_onnx_parser.add_argument("--experiment-name", default=DEFAULT_EXPERIMENT_NAME)
  eval_onnx_parser.add_argument("--num-envs", type=int, default=1)
  eval_onnx_parser.add_argument(
    "--output-file",
    type=Path,
    default=DEFAULT_OUTPUT_DIR / "metrics_onnx.json",
  )
  eval_onnx_parser.set_defaults(func=command_evaluate_onnx)

  rollout_onnx_parser = subparsers.add_parser("record-rollout-onnx")
  rollout_onnx_parser.add_argument("--task-id", default=DEFAULT_TASK_ID)
  rollout_onnx_parser.add_argument("--motion-file", type=Path, default=DEFAULT_NPZ_PATH)
  rollout_onnx_parser.add_argument("--checkpoint-file", type=Path)
  rollout_onnx_parser.add_argument("--onnx-file", type=Path)
  rollout_onnx_parser.add_argument("--experiment-name", default=DEFAULT_EXPERIMENT_NAME)
  rollout_onnx_parser.add_argument(
    "--output-video",
    type=Path,
    default=DEFAULT_OUTPUT_DIR / "policy_rollout_onnx.mp4",
  )
  rollout_onnx_parser.add_argument(
    "--output-metrics",
    type=Path,
    default=DEFAULT_OUTPUT_DIR / "policy_rollout_metrics_onnx.json",
  )
  rollout_onnx_parser.add_argument("--video-height", type=int, default=720)
  rollout_onnx_parser.add_argument("--video-width", type=int, default=1280)
  rollout_onnx_parser.add_argument("--device")
  rollout_onnx_parser.add_argument("--num-steps", type=int)
  rollout_onnx_parser.add_argument("--no-terminations", action="store_true")
  rollout_onnx_parser.set_defaults(func=command_record_rollout_onnx)

  compare_onnx_parser = subparsers.add_parser("compare-onnx")
  compare_onnx_parser.add_argument("--task-id", default=DEFAULT_TASK_ID)
  compare_onnx_parser.add_argument("--motion-file", type=Path, default=DEFAULT_NPZ_PATH)
  compare_onnx_parser.add_argument("--checkpoint-file", type=Path)
  compare_onnx_parser.add_argument("--onnx-file", type=Path)
  compare_onnx_parser.add_argument("--experiment-name", default=DEFAULT_EXPERIMENT_NAME)
  compare_onnx_parser.add_argument("--num-envs", type=int, default=1)
  compare_onnx_parser.add_argument("--num-steps", type=int, default=200)
  compare_onnx_parser.add_argument(
    "--output-file",
    type=Path,
    default=DEFAULT_OUTPUT_DIR / "onnx_parity.json",
  )
  compare_onnx_parser.set_defaults(func=command_compare_onnx)

  return parser


def main() -> int:
  parser = build_parser()
  args = parser.parse_args()
  return args.func(args)


if __name__ == "__main__":
  raise SystemExit(main())
