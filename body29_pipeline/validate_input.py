from __future__ import annotations

import argparse
import json
import pickle
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

import numpy as np

from body29_pipeline.constants import (
  DEFAULT_CSV_PATH,
  DEFAULT_MANIFEST_PATH,
  DEFAULT_PKL_PATH,
  MJLAB_G1_XML,
)


def load_joint_ranges(xml_path: Path) -> list[tuple[str, float, float]]:
  root = ET.parse(xml_path).getroot()
  joint_ranges: list[tuple[str, float, float]] = []
  for joint in root.iter("joint"):
    name = joint.attrib.get("name")
    range_value = joint.attrib.get("range")
    if name is None or range_value is None or name == "freejoint":
      continue
    lo_str, hi_str = range_value.split()
    joint_ranges.append((name, float(lo_str), float(hi_str)))
  return joint_ranges


def validate_motion_bundle(
  csv_path: Path,
  pkl_path: Path,
  xml_path: Path,
  manifest_path: Path | None = None,
) -> dict[str, Any]:
  csv = np.loadtxt(csv_path, delimiter=",", dtype=np.float32)

  with open(pkl_path, "rb") as f:
    pkl = pickle.load(f)

  joint_ranges = load_joint_ranges(xml_path)
  dof = csv[:, 7:]
  quat_norms = np.linalg.norm(csv[:, 3:7], axis=1)

  per_joint: list[dict[str, Any]] = []
  limit_violations = 0
  for i, (name, lo, hi) in enumerate(joint_ranges):
    joint_min = float(dof[:, i].min())
    joint_max = float(dof[:, i].max())
    violates = joint_min < lo or joint_max > hi
    limit_violations += int(violates)
    per_joint.append(
      {
        "joint": name,
        "min": joint_min,
        "max": joint_max,
        "limit_lo": lo,
        "limit_hi": hi,
        "violates": violates,
      }
    )

  summary: dict[str, Any] = {
    "csv_path": str(csv_path),
    "pkl_path": str(pkl_path),
    "csv_shape": list(csv.shape),
    "pkl_num_frames": int(pkl["num_frames"]),
    "fps": float(pkl["fps"]),
    "robot_type": pkl["robot_type"],
    "root_quat_norm_min": float(quat_norms.min()),
    "root_quat_norm_max": float(quat_norms.max()),
    "root_height_min": float(csv[:, 2].min()),
    "root_height_max": float(csv[:, 2].max()),
    "dof_min": float(dof.min()),
    "dof_max": float(dof.max()),
    "dof_limit_violations": limit_violations,
    "link_body_count": len(pkl["link_body_list"]),
    "local_body_pos_shape": list(np.asarray(pkl["local_body_pos"]).shape),
    "csv_matches_pkl_root_pos": bool(
      np.allclose(csv[:, :3], np.asarray(pkl["root_pos"]), atol=1e-6)
    ),
    "csv_matches_pkl_root_rot": bool(
      np.allclose(csv[:, 3:7], np.asarray(pkl["root_rot"]), atol=1e-6)
    ),
    "csv_matches_pkl_dof": bool(
      np.allclose(csv[:, 7:], np.asarray(pkl["dof_pos"]), atol=1e-6)
    ),
    "per_joint": per_joint,
  }

  if manifest_path is not None and manifest_path.exists():
    with open(manifest_path) as f:
      manifest = json.load(f)
    requested_name = csv_path.parent.name
    manifest_entry = next(
      (
        project
        for project in manifest.get("projects", [])
        if project.get("name") == requested_name
      ),
      None,
    )
    summary["manifest_has_requested_project"] = manifest_entry is not None
    summary["manifest_entry"] = manifest_entry

  return summary


def main() -> int:
  parser = argparse.ArgumentParser(
    description="Validate a video2robot -> mjlab single-motion input bundle."
  )
  parser.add_argument("--csv", type=Path, default=DEFAULT_CSV_PATH)
  parser.add_argument("--pkl", type=Path, default=DEFAULT_PKL_PATH)
  parser.add_argument("--g1-xml", type=Path, default=MJLAB_G1_XML)
  parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST_PATH)
  parser.add_argument(
    "--strict",
    action="store_true",
    help="Return a non-zero exit code if any validation check fails.",
  )
  args = parser.parse_args()

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


if __name__ == "__main__":
  raise SystemExit(main())
