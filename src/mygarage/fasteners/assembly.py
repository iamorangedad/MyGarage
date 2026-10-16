"""Solids held together by threaded joints.

A higher-level part such as an engine is an assembly: named members, plus
the bolts and nuts that clamp one member to another. A member on the loose
side of a joint is secured only when every such nut is seated. The gap that
member can open is set by the nut that is still the tightest.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from mygarage.fasteners.joint import ThreadedJoint


@dataclass
class Member:
    """One solid in an assembly. The block is the root; the head can separate."""

    member_id: str
    name: str
    pose: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    size: Tuple[float, float, float] = (0.1, 0.1, 0.05)
    gap_joint: Optional[str] = None
    rendered: bool = False
    rgba: str = '0.35 0.35 0.38 1'


class Assembly:
    """Members and the fasteners that hold them."""

    def __init__(self, assembly_id: str, members: Dict[str, Member], joints: List[ThreadedJoint]):
        self.assembly_id = assembly_id
        self.members = members
        self.joints = joints
        nuts = [joint.nut.nut_id for joint in joints]
        if len(nuts) != len(set(nuts)):
            raise ValueError(f'{assembly_id} has more than one joint for the same nut')

    def joint_for_nut(self, nut_id: str) -> ThreadedJoint:
        for joint in self.joints:
            if joint.nut.nut_id == nut_id:
                return joint
        known = ', '.join(joint.nut.nut_id for joint in self.joints)
        raise KeyError(f'Unknown nut {nut_id}. Known nuts: {known}')

    def turn(self, nut_id: str, delta_turns: float) -> ThreadedJoint:
        """Turn one nut. Positive tightens it."""
        joint = self.joint_for_nut(nut_id)
        joint.turn(delta_turns)
        return joint

    def seat_all(self) -> None:
        """Tighten every nut to its seat. This is the factory state."""
        for joint in self.joints:
            joint.seat()

    def _holding(self, member_id: str) -> List[ThreadedJoint]:
        """Joints whose loose side is this member."""
        return [joint for joint in self.joints if joint.clamps[1] == member_id]

    def member_secured(self, member_id: str) -> bool:
        """True when every nut that clamps this member is seated.

        The root member, which is only the planted side of its bolts, is
        always secured. One loose nut is enough to unseal the other side.
        """
        holding = self._holding(member_id)
        if not holding:
            return True
        return all(joint.seated for joint in holding)

    def clamp_gap(self, member_id: str) -> float:
        """How far this member can lift, in meters.

        The tightest nut holds the face down, so the gap is the smallest
        remaining distance from any nut to its seat.
        """
        holding = self._holding(member_id)
        if not holding:
            return 0.0
        return min((joint.seated_turns - joint.turns) * joint.bolt.thread.pitch_m for joint in holding)

    def joint_targets(self) -> Dict[str, float]:
        """MuJoCo joint values implied by the current fastener state.

        Each nut has a hinge (radians) and a slide (meters from the thread
        tip toward the seat). A member that can separate has a slide whose
        position is ``clamp_gap``.
        """
        targets = {}
        for joint in self.joints:
            targets[joint.nut.spin_joint] = joint.spin_rad
            targets[joint.nut.travel_joint] = joint.advance_m
        for member in self.members.values():
            if member.gap_joint:
                targets[member.gap_joint] = self.clamp_gap(member.member_id)
        return targets

    def status(self) -> List[dict]:
        """Readings for the service menu."""
        rows = []
        for joint in self.joints:
            rows.append({
                'nut': joint.nut.nut_id,
                'bolt': joint.bolt.bolt_id,
                'turns': round(joint.turns, 4),
                'seated_turns': round(joint.seated_turns, 4),
                'advance_mm': round(joint.advance_m * 1000.0, 3),
                'seated': joint.seated,
                'clamps': list(joint.clamps),
            })
        return rows
