import json
from collections import namedtuple, defaultdict, OrderedDict
from timeit import default_timer as time
from heapq import heappop, heappush
import random

Recipe = namedtuple('Recipe', ['name', 'check', 'effect', 'cost'])


class State(OrderedDict):
    """ This class is a thin wrapper around an OrderedDict, which is simply a dictionary which keeps the order in
        which elements are added (for consistent key-value pair comparisons). Here, we have provided functionality
        for hashing, should you need to use a state as a key in another dictionary, e.g. distance[state] = 5. By
        default, dictionaries are not hashable. Additionally, when the state is converted to a string, it removes
        all items with quantity 0.

        Use of this state representation is optional, should you prefer another.
    """

    def __key(self):
        return tuple(self.items())

    def __hash__(self):
        return hash(self.__key())

    def __lt__(self, other):
        return self.__key() < other.__key()

    def copy(self):
        new_state = State()
        new_state.update(self)
        return new_state

    def __str__(self):
        return str(dict(item for item in self.items() if item[1] > 0))


def make_checker(rule):
    # Implement a function that returns a function to determine whether a state meets a
    # rule's requirements. This code runs once, when the rules are constructed before
    # the search is attempted.
    requires = {}
    consumes = {}
    if 'Consumes' in rule:
        consumes = rule['Consumes']
    if 'Requires' in rule:
        requires = rule['Requires']
    def check(state):
        # This code is called by graph(state) and runs millions of times.
        # Tip: Do something with rule['Consumes'] and rule['Requires'].
        for item in requires:
            if item not in state:
                return False
        for item in consumes:
            if item not in state:
                return False
            if state[item] < consumes[item]:
                return False
        return True

    return check


def make_effector(rule):
    # Implement a function that returns a function which transitions from state to
    # new_state given the rule. This code runs once, when the rules are constructed
    # before the search is attempted.
    consumes = {}
    produces = {}
    if 'Consumes' in rule:
        consumes = rule['Consumes']
    if 'Produces' in rule:
        produces = rule['Produces']

    def effect(state):
        # This code is called by graph(state) and runs millions of times
        # Tip: Do something with rule['Produces'] and rule['Consumes'].
        next_state = state.copy()
        for item in consumes:
            next_state[item] -= consumes[item]
        for item in produces:
            if item not in state:
                next_state[item] = 0
            next_state[item] += produces[item]
        return next_state

    return effect


def make_goal_checker(goal):
    # Implement a function that returns a function which checks if the state has
    # met the goal criteria. This code runs once, before the search is attempted.
    def is_goal(state):
        # This code is used in the search process and may be called millions of times.
        return_this = False
        for item, amt in Crafting['Goal'].items():
            if item in state:                                   #if the item in inventory
                if state[item] >= amt:                           #is less than the amount required
                    return_this = True
                else:
                    return_this = False
        return return_this
    return is_goal


def graph(state):
    # Iterates through all recipes/rules, checking which are valid in the given state.
    # If a rule is valid, it returns the rule's name, the resulting state after application
    # to the given state, and the cost for the rule.
    for r in all_recipes:
        if r.check(state):
            yield (r.name, r.effect(state), r.cost)


def heuristic(state, cost_so_far, final_mats, path_so_far):
    new_mats = dict(final_mats)
    new_cost = cost_so_far + state[2]
    time_needed = state[2]

    t_item = None
    t_amt = None
    temp = Crafting['Recipes'][state[0]]['Produces']
    for craft in temp:
        t_item = craft
        t_amt = temp[craft]

    if t_item not in final_mats:
        #we don't need to go further, this item is useless to us
        return -1,-1,new_mats

    if final_mats[t_item] == 0:
        return -1,-1,new_mats

    for item, amt in Crafting['Goal'].items(): # only one item in goal dict
        if state[0].lower().find(item.lower()) != -1: # if the rule of next action includes (str) goal item
            return new_cost, 0, new_mats # give it a heur such that we pop it next

    if t_amt >= new_mats[t_item]:# if the state provides the need amt, or more, of an item
        new_mats.pop(t_item)
    elif t_amt < final_mats[t_item]: # if the state provides less the the necessary amt
        new_mats[t_item] -= t_amt

    some_heur = float(1/(t_amt+len(path_so_far)))
    return new_cost, (time_needed + some_heur), new_mats #the smaller this is the better








def find_mats(state):
    mats = {}
    for item, amt in state.items():
        mats[item] = amt
        q = [(amt, item)]

    while len(q) > 0:
        amt, item = q.pop(0)
        for action, rule in Crafting['Recipes'].items():
            if item == "cobble":
                if action == "iron_pickaxe for cobble" or action == "stone_pickaxe for cobble" or \
                                action == "iron_axe for wood" or action == "stone_axe for wood" or \
                                action == "iron_pickaxe for coal" or action == "stone_pickaxe for coal":
                    continue
            if item in rule['Produces']:
                if 'Requires' in rule:
                    for el in rule['Requires'].keys():
                        if el not in mats:
                            q.append((1, el))
                            mats[el] = 1
                if amt > rule['Produces'][item]:
                    difference = amt - rule['Produces'][item]
                    q.insert(0, (difference, item))
                if 'Consumes' in rule:
                    for consume in rule['Consumes']:
                        if consume != "wood":
                            found = False
                            for el in q:
                                if el[1] == consume:
                                    found = True
                                    index = q.index(el)
                                    q.pop(index)
                                    total = el[0] + rule['Consumes'][consume]
                                    insert_this = (total, consume)
                                    q.insert(index, insert_this)
                            if not found:
                                q.append((rule['Consumes'][consume], consume))
                        if consume not in mats:
                            mats[consume] = 0
                        mats[consume] += rule['Consumes'][consume]

    #print("Final Mats: ",mats)





    return mats


def search(graph, state, is_goal, limit, heuristic, mats):
    i = 0
    start_time = time()

    # Implement your search here! Use your heuristic here!
    # When you find a path to the goal return a list of tuples [(state, action)]
    # representing the path. Each element (tuple) of the list represents a state
    # in the path and the action that took you to this state
    print("")
    print("")
    path = []
    return_this = [(state, "Given")]
    #set up an inventory
    inventory = Crafting['Initial']
    step = 0
    adjacent_list = graph(inventory)
    priority_queue = []
    for item in inventory.keys():
        if item in mats:
            mats[item] = mats[item] - inventory[item]
    if is_goal(inventory):
        return return_this
    for each_side in adjacent_list:
        time_required, heur, new_mats = heuristic(each_side, 0, mats, path)
        i += 1
        heappush(priority_queue, (heur, i, time_required, each_side, path, new_mats))
    return_this = []
    while time() - start_time < limit:
        pop = priority_queue.pop(0)
        inventory = pop[3][1]
        current_cost = pop[2]
        pop_path =  list(pop[4])                #make a clone of the path list
        pop_path.append((pop[3]))
        if is_goal(inventory):
            for path in pop_path:
                step += 1
                return_this.append((path[1], path[0]))
            print("[cost=",current_cost,", len=",step,"]")
            print("Compute Time: ",time()-start_time)
            return return_this
        step = 0
        adjacent_list = graph(pop[3][1])
        for each_side in adjacent_list:
            time_required, heur, new_mats = heuristic(each_side, current_cost, pop[5], pop_path)
            if heur >= 0:
                heappush(priority_queue, (heur, i, time_required, each_side, pop_path, new_mats))
                i += 1
                break
    # Failed to find a path
    print(time() - start_time, 'seconds.')
    print("Failed to find a path from", state, 'within time limit.')
    return None

if __name__ == '__main__':
    with open('Crafting.json') as f:
        Crafting = json.load(f)

    # List of items that can be in your inventory:
    print('All items:', Crafting['Items'])

    # List of items in your initial inventory with amounts:
    print('Initial inventory:', Crafting['Initial'])

    # List of items needed to be in your inventory at the end of the plan:
    print('Goal:',Crafting['Goal'])

    # Dict of crafting recipes (each is a dict):
    print('Example recipe:','craft stone_pickaxe at bench ->',Crafting['Recipes']['craft stone_pickaxe at bench'])

    # Build rules
    all_recipes = []
    for name, rule in Crafting['Recipes'].items():
        checker = make_checker(rule)
        effector = make_effector(rule)
        recipe = Recipe(name, checker, effector, rule['Time'])
        all_recipes.append(recipe)

    # Create a function which checks for the goal
    is_goal = make_goal_checker(Crafting['Goal'])
    mats_needed = find_mats(Crafting['Goal'])

    # Initialize first state from initial inventory
    state = State({key: 0 for key in Crafting['Items']})
    state.update(Crafting['Initial'])
    # Search for a solution
    resulting_plan = search(graph, state, is_goal, 30, heuristic, mats_needed)

    if resulting_plan:
        # Print resulting plan
        for state, action in resulting_plan:
            print('\t',state)
            print(action)

