"""Tests for the adversarial search module (AI Fundamentals, Week 4)."""

import pygame
pygame.init()

from math import inf

from minimax import minimax_value, AdversarialTargetSelector, estimate_damage
from config import UnitType
from units import Unit, Team
from config import CELL_SIZE


def test_minimax_picks_maximum_leaf():
    """Minimax returns the best value for the maximiser on a tiny tree."""
    tree = {0: [1, 2], 1: [], 2: []}

    def successors(state, maximizing):
        return tree.get(state, [])

    def evaluate(state):
        return {0: 0, 1: 3, 2: 7}[state]

    value = minimax_value(0, 1, -inf, inf, True, successors, evaluate)
    assert value == 7


def test_minimax_minimiser_counters():
    """At depth 2 the minimiser can force a lower value."""
    tree = {0: [1, 2], 1: [3, 4], 2: [5, 6]}

    def successors(state, maximizing):
        return tree.get(state, [])

    values = {3: 3, 4: 100, 5: 5, 6: 6}

    def evaluate(state):
        return values.get(state, 0)

    # max(min(3,100)=3, min(5,6)=5) == 5
    value = minimax_value(0, 2, -inf, inf, True, successors, evaluate)
    assert value == 5


def test_alpha_beta_prunes_branches():
    """Alpha-Beta must not evaluate every leaf on a tree that allows a cut-off."""
    tree = {0: [1, 2], 1: [3, 4], 2: [5, 6]}
    values = {3: 10, 4: 10, 5: 5, 6: 6}
    evaluated = []

    def successors(state, maximizing):
        return tree.get(state, [])

    def evaluate(state):
        evaluated.append(state)
        return values.get(state, 0)

    minimax_value(0, 2, -inf, inf, True, successors, evaluate)
    # Alpha-Beta must prune leaf 6: alpha (10) >= beta (5) after leaf 5.
    assert 6 not in evaluated


def test_choose_prefers_weaker_enemy():
    red = Unit(UnitType.INFANTRY, Team.RED, 0, 0)
    weak = Unit(UnitType.INFANTRY, Team.BLUE, 10 * CELL_SIZE, 10 * CELL_SIZE)
    weak.take_damage(400)
    strong = Unit(UnitType.INFANTRY, Team.BLUE, 20 * CELL_SIZE, 10 * CELL_SIZE)

    selector = AdversarialTargetSelector(depth=2)
    chosen = selector.choose(red, [strong, weak], [])
    assert chosen is weak


def test_choose_prefers_type_advantage():
    cav = Unit(UnitType.CAVALRY, Team.RED, 0, 0)
    archer = Unit(UnitType.ARCHER, Team.BLUE, 10 * CELL_SIZE, 10 * CELL_SIZE)
    infantry = Unit(UnitType.INFANTRY, Team.BLUE, 20 * CELL_SIZE, 10 * CELL_SIZE)

    selector = AdversarialTargetSelector(depth=2)
    chosen = selector.choose(cav, [infantry, archer], [])
    assert chosen is archer


def test_choose_single_enemy_returns_it():
    red = Unit(UnitType.INFANTRY, Team.RED, 0, 0)
    blue = Unit(UnitType.INFANTRY, Team.BLUE, 10 * CELL_SIZE, 10 * CELL_SIZE)
    selector = AdversarialTargetSelector(depth=2)
    assert selector.choose(red, [blue], []) is blue


def test_choose_empty_returns_none():
    red = Unit(UnitType.INFANTRY, Team.RED, 0, 0)
    selector = AdversarialTargetSelector(depth=2)
    assert selector.choose(red, [], []) is None


def test_estimate_damage_includes_advantage():
    cav = Unit(UnitType.CAVALRY, Team.RED, 0, 0)
    archer = Unit(UnitType.ARCHER, Team.BLUE, 0, 0)
    dmg = estimate_damage(cav, archer)
    assert dmg > cav.damage  # 1.5x advantage


def test_ai_controller_accepts_minimax_flag():
    from pathfinding import Pathfinder
    from map import TacticalMap
    game_map = TacticalMap()
    pf = Pathfinder(game_map)
    from ai import AIController
    ai = AIController(pf)
    red = Unit(UnitType.INFANTRY, Team.RED, 10 * CELL_SIZE, 10 * CELL_SIZE)
    ai.register_unit(red, use_minimax=True)
    assert ai._unit_ais[0].use_minimax is True