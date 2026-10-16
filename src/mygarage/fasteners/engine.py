"""The engine is a block and a head clamped by four studs.

This is the pattern for every later part: the named component is an assembly
of members, and the members stay together only while their nuts are seated.
"""

from typing import Dict

from mygarage.fasteners.assembly import Assembly, Member
from mygarage.fasteners.bolt import Bolt
from mygarage.fasteners.joint import ThreadedJoint
from mygarage.fasteners.nut import Nut
from mygarage.fasteners.thread import Thread

# M10 x 1.5, 15 mm of thread: ten turns from first engagement to the seat.
HEAD_THREAD = Thread(diameter_m=0.010, pitch_m=0.0015, length_m=0.015)
HEAD_THICKNESS_M = 0.04
DECK_Z = 0.15
# Thread tip sits one thread length above the head's top face.
TIP_Z = DECK_Z + HEAD_THICKNESS_M + HEAD_THREAD.length_m


def build_engine() -> Assembly:
    """Cylinder head clamped to the block by four nuts. They start seated."""
    corners = (
        (0.10, 0.08),
        (0.10, -0.08),
        (-0.10, 0.08),
        (-0.10, -0.08),
    )
    members: Dict[str, Member] = {
        'engine_block': Member(
            'engine_block',
            '气缸体 Engine Block',
            rendered=False,
        ),
        'cylinder_head': Member(
            'cylinder_head',
            '气缸盖 Cylinder Head',
            pose=(0.0, 0.0, DECK_Z + HEAD_THICKNESS_M / 2.0),
            size=(0.18, 0.14, HEAD_THICKNESS_M / 2.0),
            gap_joint='head_clamp',
            rendered=True,
            rgba='0.40 0.40 0.43 1',
        ),
    }
    joints = []
    for index, (x_pos, y_pos) in enumerate(corners, start=1):
        bolt = Bolt(
            bolt_id=f'head_bolt_{index}',
            thread=HEAD_THREAD,
            planted_in='engine_block',
            position=(x_pos, y_pos, TIP_Z),
        )
        nut = Nut(nut_id=f'head_nut_{index}', thread=HEAD_THREAD, thickness_m=0.008)
        joint = ThreadedJoint(
            joint_id=f'head_fastener_{index}',
            bolt=bolt,
            nut=nut,
            clamps=('engine_block', 'cylinder_head'),
        )
        joint.seat()
        joints.append(joint)
    return Assembly('engine', members, joints)
