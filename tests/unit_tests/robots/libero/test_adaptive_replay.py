"""Offline regression checks for live grasp recovery and unused-anchor pruning."""
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np
import pytest

from robots.libero.flash import replay as module


def scene(reading=(0.12, 0.10, 0.8), failures=1):
    commands = []
    picks = 0
    state = SimpleNamespace(latest_step=0)

    def execute(name, args):
        nonlocal picks
        commands.append((name, args.copy()))
        if name == 'segment':
            return SimpleNamespace(is_error=False, data={'world_xyz':
                [0.10, 0.10, 0.8] if args['step'] == 0 else list(reading)})
        state.latest_step += 1
        if name == 'pi0_pick':
            picks += 1
            return SimpleNamespace(is_error=False, data={'success': picks > failures})
        return SimpleNamespace(is_error=False, data={})

    toolkit = SimpleNamespace(state=state, execute_tool=execute, solved=lambda: picks > failures)
    program = {
        'reference': {'cup': np.array([0.10, 0.10]), 'unused': np.array([0.3, 0.3])},
        'locator_of': {'cup': 'segment', 'unused': 'segment'},
        'plan': [
            {'action': 'move_to', 'arguments': {'xyz': [0.10, 0.10, 1.1], 'gripper': -1},
             'anchor': 'cup', 'anchor_distance': 0, 'offset': [0, 0]},
            {'action': 'pi0_pick', 'arguments': {'prompt': 'grasp the cup', 'max_chunks': 8}},
        ],
    }
    return toolkit, program, commands


def test_fresh_observation_moves_failed_approach_without_reset():
    toolkit, program, commands = scene()
    result = module.replay(toolkit, None, program)
    assert result['done']
    segments = [args for name, args in commands if name == 'segment']
    assert [a['prompt'] for a in segments] == ['cup', 'cup']
    assert [a['step'] for a in segments] == [0, 2]
    moves = [args['xyz'] for name, args in commands if name == 'move_to']
    np.testing.assert_allclose(moves, [[0.10, 0.10, 1.1], [0.12, 0.10, 1.1]])
    assert sum(name == 'pi0_pick' for name, _ in commands) == 2
    assert not any('reset' in name for name, _ in commands)


def test_successful_first_pick_avoids_recovery_perception():
    toolkit, program, commands = scene(failures=0)
    assert module.replay(toolkit, None, program)['done']
    assert sum(name == 'segment' for name, _ in commands) == 1


@pytest.mark.parametrize('reading', [(0.35, 0.10, 0.8), (float('nan'), 0.1, 0.8), (0.5, 0.1, 0.8)])
def test_wrong_object_or_invalid_depth_keeps_original_approach(reading):
    toolkit, program, commands = scene(reading=reading)
    module.replay(toolkit, None, program)
    moves = [args['xyz'] for name, args in commands if name == 'move_to']
    assert moves[0] == moves[1]


def test_failed_picks_preserve_baseline_attempt_limit():
    toolkit, program, commands = scene(failures=99)
    assert not module.replay(toolkit, None, program)['done']
    assert sum(name == 'pi0_pick' for name, _ in commands) == module.PICK_ATTEMPTS == 3


def test_point_anchor_uses_molmo_and_retains_orientation():
    toolkit, program, _ = scene()
    recent = [('move_pose', {'xyz': [0.10, 0.10, 1.1], 'quat': [1, 0, 0, 0]}, 'cup')]
    live = {'cup': np.array([0.1, 0.1])}
    with patch.object(module, 'locate', return_value={'xy': np.array([0.12, 0.1])}) as locate:
        result = module.refresh_failed_approach(toolkit, object(), toolkit.state,
            recent, live, {'cup': 'point'}, lambda _: None)
    assert locate.call_count == 1
    assert result[0][1]['quat'] == [1, 0, 0, 0]
    assert recent[0][1]['xyz'] == [0.1, 0.1, 1.1]
    assert result[0][1]['xyz'] == [0.12, 0.1, 1.1]


def test_unavailable_recovery_observation_does_not_abort_retry():
    toolkit, program, commands = scene()
    original = toolkit.execute_tool

    def execute(name, args):
        if name == 'segment' and args['step'] > 0:
            return SimpleNamespace(is_error=True, data={'error': 'no mask'})
        return original(name, args)

    toolkit.execute_tool = execute
    assert module.replay(toolkit, None, program)['done']
    assert sum(name == 'pi0_pick' for name, _ in commands) == 2
