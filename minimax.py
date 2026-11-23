"""Adversarial search for the Tactic Battle AI (AI Fundamentals, Week 4).

Self-contained, pygame-free module implementing:

* :func:`minimax_value` -- classic Minimax over an arbitrary game tree, with
  Alpha-Beta pruning.
* :class:`AdversarialTargetSelector` -- uses Minimax + Alpha-Beta to choose
  which enemy a unit should engage, assuming the enemy (minimiser) picks the
  best counter-attack.

Keeping this module free of pygame/Unit-mutation makes it directly unit-testable.
"""

from math import inf
from typing import Any, Callable, List, Optional, Sequence, Tuple

from config import COMBAT_ADVANTAGE, UnitType
from units import Unit


INFINITY = float("inf")


def estimate_damage(attacker: Unit, defender: Unit) -> float:
    """Expected damage of one attack, including the type-advantage multiplier."""
    if not attacker.alive or not defender.alive:
        return 0.0
    mult = COMBAT_ADVANTAGE.get((attacker.unit_type, defender.unit_type), 1.0)
    return float(attacker.damage) * float(mult)


def minimax_value(
    state: Any,
    depth: int,
    alpha: float,
    beta: float,
    maximizing: bool,
    successors: Callable[[Any, bool], Sequence[Any]],
    evaluate: Callable[[Any], float],
) -> float:
    """Minimax with Alpha-Beta pruning.

    ``successors(state, maximizing)`` returns the child states available to the
    side to move; ``evaluate(state)`` scores a leaf (higher == better for the
    maximiser).  ``alpha``/``beta`` are the running bounds.
    """
    if depth <= 0:
        return evaluate(state)

    children = list(successors(state, maximizing))
    if not children:
        return evaluate(state)

    if maximizing:
        value = -INFINITY
        for child in children:
            value = max(value, minimax_value(child, depth - 1, alpha, beta, False,
                                            successors, evaluate))
            alpha = max(alpha, value)
            if beta <= alpha:
                break  # Beta cut-off (Alpha-Beta pruning)
        return value

    value = INFINITY
    for child in children:
        value = min(value, minimax_value(child, depth - 1, alpha, beta, True,
                                        successors, evaluate))
        beta = min(beta, value)
        if beta <= alpha:
            break  # Alpha cut-off (Alpha-Beta pruning)
    return value


class AdversarialTargetSelector:
    """Pick an enemy target for ``unit`` via Minimax + Alpha-Beta."""

    def __init__(self, depth: int = 2):
        self.depth = max(1, int(depth))
        self.nodes_evaluated = 0

    def choose(self, unit: Unit, enemies: Sequence[Unit],
               allies: Optional[Sequence[Unit]] = None) -> Optional[Unit]:
        enemies = [e for e in enemies if e.alive]
        if not enemies:
            return None
        if len(enemies) == 1:
            return enemies[0]

        self._enemies = list(enemies)
        self._unit = unit
        self.nodes_evaluated = 0

        alpha = -INFINITY
        beta = INFINITY
        best_score = -INFINITY
        best_target = enemies[0]

        for enemy in enemies:
            child_state = (unit, enemy, None)
            # minimiser (enemy) chooses the counter-attack at the next level
            score = minimax_value(
                child_state,
                self.depth - 1,
                alpha,
                beta,
                False,
                self._successors,
                self._evaluate,
            )
            if score > best_score:
                best_score = score
                best_target = enemy
            alpha = max(alpha, best_score)
            if beta <= alpha:
                break  # Alpha-Beta pruning at the root

        return best_target

    # -- helpers used as callbacks by minimax_value -------------------------

    def _successors(self, state: Any, maximizing: bool) -> Sequence[Any]:
        unit, target, counter = state
        if maximizing:
            # maximiser (our AI) picks a target
            return [(unit, e, None) for e in self._enemies]
        # minimiser (enemy) picks a counter-attacker
        return [(unit, target, e) for e in self._enemies]

    def _evaluate(self, state: Any) -> float:
        self.nodes_evaluated += 1
        unit, target, counter = state
        if target is None:
            return 0.0

        dmg_dealt = estimate_damage(unit, target)
        counter_dmg = estimate_damage(counter, unit) if counter is not None else 0.0

        kill_bonus = 50.0 if (target.health <= dmg_dealt) else 0.0
        death_penalty = 50.0 if (unit.health <= counter_dmg) else 0.0
        # Prefer finishing off wounded enemies: a unit at 20% HP is a better
        # target than a full-health one with the same damage trade.
        wound_bonus = (target.max_health - target.health) * 0.1

        return (dmg_dealt - counter_dmg) + kill_bonus - death_penalty + wound_bonus
