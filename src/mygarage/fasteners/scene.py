"""Pose the garage scene from an assembly.

MuJoCo has hinge and slide joints, and no screw joint. The thread law stays
in ``ThreadedJoint``: each nut is a hinge plus a slide, and both coordinates
are written from the turns. The scene file only marks where those bodies go.
"""

from pathlib import Path

from mygarage.fasteners.assembly import Assembly
from mygarage.fasteners.engine import build_engine

_MARKER = '<!-- STRUCTURAL_FASTENERS -->'


def _garage_scene_path() -> Path:
    return Path(__file__).resolve().parents[1] / 'mjcf' / 'garage_scene.xml'


def render_assembly(assembly: Assembly) -> str:
    """MJCF fragment for every rendered member and every nut."""
    lines = []
    for member in assembly.members.values():
        if not member.rendered or not member.gap_joint:
            continue
        x_pos, y_pos, z_pos = member.pose
        sx, sy, sz = member.size
        lines.append(
            f'          <body name="{member.member_id}" pos="{x_pos} {y_pos} {z_pos}" gravcomp="1">\n'
            f'            <joint name="{member.gap_joint}" type="slide" axis="0 0 1" '
            f'limited="true" range="0 0.016" ref="0" damping="20"/>\n'
            f'            <geom name="{member.member_id}_geom" type="box" '
            f'size="{sx} {sy} {sz}" rgba="{member.rgba}" mass="8" contype="0" conaffinity="0"/>\n'
            '          </body>'
        )
    for joint in assembly.joints:
        x_pos, y_pos, z_pos = joint.bolt.position
        spin_deg = joint.seated_turns * 360.0
        travel = joint.bolt.thread.length_m
        nut_id = joint.nut.nut_id
        lines.append(
            f'          <body name="{joint.bolt.bolt_id}" pos="{x_pos} {y_pos} {z_pos}">\n'
            f'            <geom name="{joint.bolt.bolt_id}_shank" type="cylinder" '
            f'size="0.005 0.028" pos="0 0 -0.028" rgba="0.72 0.72 0.75 1" contype="0" conaffinity="0"/>\n'
            f'            <body name="{nut_id}" pos="0 0 0" gravcomp="1">\n'
            f'              <joint name="{nut_id}_spin" type="hinge" axis="0 0 1" '
            f'limited="true" range="0 {spin_deg + 20:.1f}" ref="{spin_deg:.1f}" damping="1"/>\n'
            f'              <joint name="{nut_id}_travel" type="slide" axis="0 0 -1" '
            f'limited="true" range="0 {travel + 0.001:.4f}" ref="{travel:.4f}" damping="2"/>\n'
            f'              <geom name="{nut_id}_hex" type="cylinder" size="0.012 0.004" '
            f'rgba="0.85 0.82 0.75 1" mass="0.05" contype="0" conaffinity="0"/>\n'
            '            </body>\n'
            '          </body>'
        )
    return '\n'.join(lines)


def load_garage_xml(assembly: Assembly = None) -> str:
    """Base garage scene with the assembly's fasteners inserted."""
    assembly = assembly or build_engine()
    text = _garage_scene_path().read_text(encoding='utf-8')
    if _MARKER not in text:
        raise RuntimeError(f'{_garage_scene_path()} is missing {_MARKER}')
    return text.replace(_MARKER, render_assembly(assembly), 1)
