from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from body29_pipeline.constants import (
  BODY_29_JOINT_NAMES,
  DEFAULT_DEPLOY_CONFIG_PATH,
  DEFAULT_SAFE_HAND_Q,
  DEX3_JOINT_NAMES,
)


@dataclass(frozen=True)
class Body29Dex3Command:
  q_body_ref: np.ndarray
  q_left_hand_ref: np.ndarray
  q_right_hand_ref: np.ndarray


class Body29Dex3Adapter:
  """Compose body-only policy outputs with fixed Dex3 hand references.

  The body joint order is intentionally identical to mjlab's G1 tracking order and
  Unitree's documented 29DoF low-level body order, so the default body mapping is
  the identity map.
  """

  def __init__(
    self,
    *,
    body_joint_names: tuple[str, ...] = BODY_29_JOINT_NAMES,
    body_to_unitree_lowcmd_indices: tuple[int, ...] | None = None,
    dex3_joint_names: tuple[str, ...] = DEX3_JOINT_NAMES,
    left_dex3_safe_q: tuple[float, ...] = DEFAULT_SAFE_HAND_Q,
    right_dex3_safe_q: tuple[float, ...] = DEFAULT_SAFE_HAND_Q,
  ) -> None:
    self.body_joint_names = tuple(body_joint_names)
    self.body_to_unitree_lowcmd_indices = tuple(
      body_to_unitree_lowcmd_indices
      if body_to_unitree_lowcmd_indices is not None
      else range(len(self.body_joint_names))
    )
    self.dex3_joint_names = tuple(dex3_joint_names)
    self.left_dex3_safe_q = np.asarray(left_dex3_safe_q, dtype=np.float32)
    self.right_dex3_safe_q = np.asarray(right_dex3_safe_q, dtype=np.float32)

    if len(self.body_joint_names) != 29:
      raise ValueError("body_joint_names must contain exactly 29 joints.")
    if len(self.body_to_unitree_lowcmd_indices) != 29:
      raise ValueError("body_to_unitree_lowcmd_indices must contain exactly 29 values.")
    if len(self.dex3_joint_names) != 7:
      raise ValueError("dex3_joint_names must contain exactly 7 joint names.")
    if self.left_dex3_safe_q.shape != (7,) or self.right_dex3_safe_q.shape != (7,):
      raise ValueError("Dex3 safe hand poses must contain exactly 7 joint targets.")

  @classmethod
  def from_config(cls, config_path: Path = DEFAULT_DEPLOY_CONFIG_PATH):
    with open(config_path) as f:
      data: dict[str, Any] = json.load(f)
    return cls(
      body_joint_names=tuple(data["body_joint_names"]),
      body_to_unitree_lowcmd_indices=tuple(data["body_to_unitree_lowcmd_indices"]),
      dex3_joint_names=tuple(data["dex3_joint_names"]),
      left_dex3_safe_q=tuple(data["left_dex3_safe_q"]),
      right_dex3_safe_q=tuple(data["right_dex3_safe_q"]),
    )

  def compose(
    self,
    q_body_ref: np.ndarray | list[float] | tuple[float, ...],
    *,
    q_left_hand_ref: np.ndarray | list[float] | tuple[float, ...] | None = None,
    q_right_hand_ref: np.ndarray | list[float] | tuple[float, ...] | None = None,
  ) -> Body29Dex3Command:
    body = np.asarray(q_body_ref, dtype=np.float32)
    if body.shape != (29,):
      raise ValueError("q_body_ref must have shape (29,).")
    left = (
      np.asarray(q_left_hand_ref, dtype=np.float32)
      if q_left_hand_ref is not None
      else self.left_dex3_safe_q.copy()
    )
    right = (
      np.asarray(q_right_hand_ref, dtype=np.float32)
      if q_right_hand_ref is not None
      else self.right_dex3_safe_q.copy()
    )
    if left.shape != (7,) or right.shape != (7,):
      raise ValueError("Dex3 hand targets must have shape (7,).")
    return Body29Dex3Command(
      q_body_ref=body,
      q_left_hand_ref=left,
      q_right_hand_ref=right,
    )

  def body_targets_in_lowcmd_order(self, command: Body29Dex3Command) -> np.ndarray:
    ordered = np.zeros(29, dtype=np.float32)
    ordered[list(self.body_to_unitree_lowcmd_indices)] = command.q_body_ref
    return ordered

  def as_dict(self, command: Body29Dex3Command) -> dict[str, list[float]]:
    return {
      "q_body_ref": command.q_body_ref.tolist(),
      "q_body_ref_lowcmd_order": self.body_targets_in_lowcmd_order(command).tolist(),
      "q_left_hand_ref": command.q_left_hand_ref.tolist(),
      "q_right_hand_ref": command.q_right_hand_ref.tolist(),
    }
