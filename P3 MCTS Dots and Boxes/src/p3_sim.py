from p3_game import create_game, State
from timeit import default_timer as time

import mcts_modified as red_bot
import mcts_vanilla as blue_bot

BOTS = {'red': red_bot, 'blue': blue_bot}

# You can set the MCTS tree size like this:
if hasattr(blue_bot, 'num_blue_nodes'):
    blue_bot.num_blue_nodes = 1000
    #print("BLUE_NUM_NODES: ",blue_bot.num_blue_nodes)
if hasattr(red_bot, 'num_red_nodes'):
    red_bot.num_red_nodes = 2
    #print("RED_NUM_NODES: ",red_bot.num_red_nodes)
rounds = 100
wins = {}

start = time()  # To log how much time the simulation takes.
for i in range(rounds):

    # print("")
    # print("Round %d, fight!" % i)

    game = create_game(4)   # Specify the size of the grid in vertices. In this case, 4x4
    state = State(game)     # Create a state from the instance of the game

    while not state.is_terminal():
        move = BOTS[state.player_turn].think(state.copy())
        state.apply_move(move)

    final_score = state.score
    winner = state.winner
    # print("The %s bot wins this round! (%s)" % (winner, str(final_score)))
    wins[winner] = wins.get(winner, 0) + 1

print("")
print("Final win counts:", dict(wins))

# Also output the time elapsed.
end = time()
print(end-start, ' seconds')
