from __future__ import annotations

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
MJLAB_ROOT = ROOT_DIR / "research" / "mjlab"
MJLAB_G1_XML = (
  MJLAB_ROOT / "src" / "mjlab" / "asset_zoo" / "robots" / "unitree_g1" / "xmls" / "g1.xml"
)
UNITREE_MUJOCO_G1_SCENE_29DOF = (
  ROOT_DIR / "research" / "unitree_mujoco" / "unitree_robots" / "g1" / "scene_29dof.xml"
)

DEFAULT_PROJECT_NAME = "video_005"
DEFAULT_INPUT_DIR = ROOT_DIR / "00_RL_input" / DEFAULT_PROJECT_NAME
DEFAULT_OUTPUT_DIR = ROOT_DIR / "artifacts" / DEFAULT_PROJECT_NAME

DEFAULT_CSV_PATH = DEFAULT_INPUT_DIR / "robot_motion.csv"
DEFAULT_PKL_PATH = DEFAULT_INPUT_DIR / "robot_motion.pkl"
DEFAULT_MANIFEST_PATH = ROOT_DIR / "00_RL_input" / "manifest.json"
DEFAULT_NPZ_PATH = DEFAULT_OUTPUT_DIR / "motion.npz"
DEFAULT_VIDEO_PATH = DEFAULT_OUTPUT_DIR / "motion.mp4"
DEFAULT_ROLLOUT_VIDEO_PATH = DEFAULT_OUTPUT_DIR / "policy_rollout.mp4"
DEFAULT_ROLLOUT_METRICS_PATH = DEFAULT_OUTPUT_DIR / "policy_rollout_metrics.json"

DEFAULT_EXPERIMENT_NAME = "body29dof_only"
DEFAULT_TASK_ID = "Mjlab-Tracking-Flat-Unitree-G1"
DEFAULT_SAFE_HAND_Q = (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

BODY_29_JOINT_NAMES = (
  "left_hip_pitch_joint",
  "left_hip_roll_joint",
  "left_hip_yaw_joint",
  "left_knee_joint",
  "left_ankle_pitch_joint",
  "left_ankle_roll_joint",
  "right_hip_pitch_joint",
  "right_hip_roll_joint",
  "right_hip_yaw_joint",
  "right_knee_joint",
  "right_ankle_pitch_joint",
  "right_ankle_roll_joint",
  "waist_yaw_joint",
  "waist_roll_joint",
  "waist_pitch_joint",
  "left_shoulder_pitch_joint",
  "left_shoulder_roll_joint",
  "left_shoulder_yaw_joint",
  "left_elbow_joint",
  "left_wrist_roll_joint",
  "left_wrist_pitch_joint",
  "left_wrist_yaw_joint",
  "right_shoulder_pitch_joint",
  "right_shoulder_roll_joint",
  "right_shoulder_yaw_joint",
  "right_elbow_joint",
  "right_wrist_roll_joint",
  "right_wrist_pitch_joint",
  "right_wrist_yaw_joint",
)

DEX3_JOINT_NAMES = (
  "thumb_0",
  "thumb_1",
  "thumb_2",
  "index_0",
  "index_1",
  "middle_0",
  "middle_1",
)

DEFAULT_DEPLOY_CONFIG_PATH = (
  ROOT_DIR / "body29_pipeline" / "config" / "body29dof_only.json"
)
