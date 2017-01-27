
from mcts_node import MCTSNode
import random
from math import sqrt, log
from timeit import default_timer as time

num_nodes = 1000
#num_red_nodes = 1000
#num_blue_nodes = 1000
explore_faction = 1.

def traverse_nodes(node, state, identity):
    """ Traverses the tree until the end criterion are met.

    Args:
        node:       A tree node from which the search is traversing.
        state:      The state of the game.
        identity:   The bot's identity, either 'red' or 'blue'.

    Returns:        A node from which the next stage of the search can proceed.

    """
    if state.is_terminal():
        return node
    if len(node.untried_actions) > 0:        #check all the possible actions in current node
        return expand_leaf(node, state)

    highest_UCB =  float('-inf')
                                                            #since we're here, that means all untried actions are not legal
    for each_child_node in node.child_nodes:           #go to each child node if the node im on has existing children
        C = explore_faction                                             #exploration term
        UCB = (each_child_node.wins / each_child_node.visits) + C * (sqrt((2.0 * log(node.visits)) / each_child_node.visits))
        # print("UCB %s" % str(UCB))
        if UCB >= highest_UCB:          #go through each to find the lowest # of visits
            highest_UCB = UCB
            node = each_child_node

    state.apply_move(node.parent_action)               #apply what the chosen current node DID to get to child_node
    return traverse_nodes(node, state, identity)
    # Hint: return leaf_node


def expand_leaf(node, state):
    """ Adds a new leaf to the tree by creating a new child node for the given node.

    Args:
        node:   The node for which a child will be added.
        state:  The state of the game.

    Returns:    The added child node.

    """
    new_action_state = state.copy()
    an_action = node.untried_actions.pop(0)
    new_action_state.apply_move(an_action)
    new_action_list = new_action_state.legal_moves
    new_node = MCTSNode(node, an_action, new_action_list)
    node.child_nodes[new_node] = new_node
    return new_node
    # Hint: return new_node


def rollout(state, identity):
    """ Given the state of the game, the rollout plays out the remainder randomly.

    Args:
        state:  The state of the game.

    """
    # Define a helper function to calculate the difference between the bot's score and the opponent's.
    def outcome(score):
        red_score = score.get('red', 0)
        blue_score = score.get('blue', 0)
        return red_score - blue_score

    DEPTH = 5
    # Sample a set number of games where the target move is immediately applied.
    rollout_state = state.copy()

    # Only play to the specified depth.
    for i in range(DEPTH):
        if rollout_state.is_terminal():
            break
        rollout_move = random.choice(rollout_state.legal_moves)
        rollout_state.apply_move(rollout_move)

    if identity == 'red':
        if outcome(rollout_state.score) > 0:
            return 1                                    #red wins assuming red is player and blue is bot
        elif outcome(rollout_state.score) == 0:
            return 0
        return -1                                        #blue wins
    else:
        if outcome(rollout_state.score) > 0:
            return -1                                    #red wins assuming red is player and blue is bot
        elif outcome(rollout_state.score) == 0:
            return 0
        return 1                                        #blue wins


def backpropagate(node, won):
    """ Navigates the tree from a leaf node to the root, updating the win and visit count of each node along the path.

    Args:
        node:   A leaf node.
        won:    An indicator of whether the bot won or lost the game.
                0 = bot lost
                1 = bot won
    """
    while node.parent is not None:                  #this will stop on the nodes which attach to root
        node.wins = (node.wins+won) / 2.0
        node.visits += 1.0
        node = node.parent
    node.visits += 1.0                              #increment the root_nodes visit



def think(state):
    """ Performs MCTS by sampling games and calling the appropriate functions to construct the game tree.

    Args:
        state:  The state of the game.

    Returns:    The action to be taken.

    """
    #if state.player_turn == 'red':
    #    num_nodes = num_red_nodes
    #else:
    #    num_nodes = num_blue_nodes

    #print("NUM_NODES: ",num_nodes, state.player_turn)
    start = time()
    time_elapsed = 0.0
    identity_of_bot = state.player_turn
    root_node = MCTSNode(parent=None, parent_action=None, action_list=state.legal_moves)

    for step in range(num_nodes):
    #while time_elapsed < 1.0:
        time_elapsed = time()-start
        # Copy the game for sampling a playthrough
        sampled_game = state.copy()
        # Start at root
        node = root_node

        # Do MCTS - This is all you!
        #traverse
        node = traverse_nodes(node, sampled_game, identity_of_bot)
        #expand
        #rollout & backpropagate
        backpropagate(node, rollout(sampled_game, identity_of_bot))

    best_node = None
    highest_win = float('-inf')
    for each_node in root_node.child_nodes:
        if  each_node.wins >= highest_win:
            best_node = each_node
            highest_win = each_node.wins
    if len(root_node.child_nodes) is 0:
        print(": %s" % str(root_node))
    # Return an action, typically the most frequently used action (from the root) or the action with the best
    # estimated win rate.
    return best_node.parent_action
