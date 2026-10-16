"""Nut and bolt law, and the engine assembled from those joints."""

import math

import pytest

from mygarage.fasteners.bolt import Bolt
from mygarage.fasteners.engine import HEAD_THREAD, build_engine
from mygarage.fasteners.joint import ThreadedJoint
from mygarage.fasteners.nut import Nut
from mygarage.fasteners.thread import Thread
from mygarage.game import Game
from mygarage.system_model import SystemModel


def warm(system: SystemModel, seconds: int = 40):
    for _ in range(seconds):
        system.step(1.0)


class TestThreadLaw:
    def test_one_turn_advances_one_pitch(self):
        assert HEAD_THREAD.advance_m(1) == pytest.approx(0.0015)
        assert HEAD_THREAD.turns_available == pytest.approx(10)

    def test_nut_stops_at_the_seat_and_at_the_first_thread(self):
        engine = build_engine()
        joint = engine.joint_for_nut('head_nut_1')
        assert joint.seated
        assert joint.turn(3) == 0
        assert joint.turns == pytest.approx(joint.seated_turns)
        joint.turn(-100)
        assert joint.turns == 0
        assert joint.advance_m == 0
        assert joint.engaged is False

    def test_mismatched_thread_is_rejected(self):
        bolt = Bolt('bolt', Thread(0.010, 0.0015, 0.015), planted_in='block')
        nut = Nut('nut', Thread(0.008, 0.0010, 0.010))
        with pytest.raises(ValueError):
            ThreadedJoint('bad', bolt, nut, clamps=('block', 'cover'))


class TestEngineAssembly:
    def test_a_seated_head_is_clamped_with_no_gap(self):
        engine = build_engine()
        assert engine.member_secured('cylinder_head')
        assert engine.clamp_gap('cylinder_head') == 0
        assert len(engine.joints) == 4

    def test_one_loose_nut_unseals_the_head_but_the_others_hold_the_gap(self):
        engine = build_engine()
        engine.turn('head_nut_2', -2)
        assert engine.member_secured('cylinder_head') is False
        assert engine.clamp_gap('cylinder_head') == 0
        loose = engine.joint_for_nut('head_nut_2')
        assert loose.advance_m == pytest.approx(0.012)
        assert engine.joint_for_nut('head_nut_1').seated

    def test_backing_off_every_nut_opens_the_head_by_the_same_pitch(self):
        engine = build_engine()
        for nut_id in ('head_nut_1', 'head_nut_2', 'head_nut_3', 'head_nut_4'):
            engine.turn(nut_id, -2)
        assert engine.clamp_gap('cylinder_head') == pytest.approx(0.003)
        targets = engine.joint_targets()
        assert targets['head_nut_1_travel'] == pytest.approx(0.012)
        assert targets['head_nut_1_spin'] == pytest.approx(8 * 2 * math.pi)
        assert targets['head_clamp'] == pytest.approx(0.003)


class TestFastenerSimulation:
    def test_turning_a_nut_moves_it_along_the_bolt(self):
        game = Game(headless=True)
        try:
            before = game.simulation.joint_qpos('head_nut_1_travel')
            assert before == pytest.approx(0.015)
            assert game.simulation.joint_qpos('head_clamp') == pytest.approx(0)
            result = game.turn_fastener('head_nut_1', -4)
            game.step_simulation(20)
            assert result['seated'] is False
            assert result['head_clamped'] is False
            assert game.simulation.joint_qpos('head_nut_1_travel') == pytest.approx(0.009)
            assert game.simulation.joint_qpos('head_nut_1_spin') == pytest.approx(6 * 2 * math.pi)
            assert game.simulation.joint_qpos('head_nut_2_travel') == pytest.approx(0.015)
            assert game.simulation.joint_qpos('head_clamp') == pytest.approx(0)
        finally:
            game.close()

    def test_loosening_every_head_nut_lifts_the_head_and_overheats(self):
        game = Game(headless=True)
        try:
            for nut_id in ('head_nut_1', 'head_nut_2', 'head_nut_3', 'head_nut_4'):
                game.turn_fastener(nut_id, -3)
            game.step_simulation(10)
            assert game.simulation.joint_qpos('head_clamp') == pytest.approx(0.0045)
            assert game.system_model.state['head_clamped'] is False
            game.system_model.start_attempt()
            warm(game.system_model)
            assert game.system_model.state['coolant_temp_c'] > 105
        finally:
            game.close()
