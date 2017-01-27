#!/usr/bin/env python
#

"""
// The do_turn function is where your code goes. The PlanetWars object contains
// the state of the game, including information about all planets and fleets
// that currently exist.
//
// There is already a basic strategy in place here. You can use it as a
// starting point, or you can throw it out entirely and replace it with your
// own.
"""
import logging, traceback, sys, os, inspect
logging.basicConfig(filename=__file__[:-3] +'.log', filemode='w', level=logging.DEBUG)
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from behavior_tree_bot.behaviors import *
from behavior_tree_bot.checks import *
from behavior_tree_bot.bt_nodes import Selector, Sequence, Action, Check

from planet_wars import PlanetWars, finish_turn


def setup_behavior_tree():
    # Top-down construction of behavior tree
    #start = time()
    #logging.info("TIME: %s" %str(start))
    root = Selector(name='High Level Ordering of Strategies')
    spread_sequence = Sequence(name='Spread Strategy')
    quick_attack_sequence = Sequence(name='Quick Attack Sequence')
    offensive_plan = Sequence(name='Offensive Strategy')

    q_attack = Action(quick_attack)
    enemy_fleets_check = Check(enemy_fleets_exist)
    quick_attack_sequence.child_nodes = [enemy_fleets_check, q_attack]

    spread_action = Action(spread_to_most_efficient_neutral_planet)
    neutral_planets_check = Check(if_neutral_planet_available)
    spread_sequence.child_nodes = [neutral_planets_check, spread_action]

    planets_exist = Check(have_planets_not_my_own)
    more_enemies = Check(more_enemies_than_neutrals)
    set_target = Action(settarget)#refer to behaviours.py
    offensive_plan.child_nodes = [planets_exist, more_enemies, set_target]

    default_attack = Action(attack_weakest_enemy_planet)

    root.child_nodes = [quick_attack_sequence, spread_sequence, offensive_plan, default_attack]
    logging.info('\n' + root.tree_to_string())
    return root

def do_turn():
    """
    Here is where you have to implement your strategy using the behaviour tree you defined.
    """
    return

if __name__ == '__main__':
    logging.basicConfig(filename=__file__[:-3] + '.log', filemode='w', level=logging.DEBUG)

    behavior_tree = setup_behavior_tree()
    try:
        map_data = ''
        while True:
            current_line = input()
            if len(current_line) >= 2 and current_line.startswith("go"):
                planet_wars = PlanetWars(map_data)
                behavior_tree.execute(planet_wars)
                finish_turn()
                map_data = ''
            else:
                map_data += current_line + '\n'

    except KeyboardInterrupt:
        print('ctrl-c, leaving ...')
    except Exception:
        traceback.print_exc(file=sys.stdout)
        logging.exception("Error in bot.")
