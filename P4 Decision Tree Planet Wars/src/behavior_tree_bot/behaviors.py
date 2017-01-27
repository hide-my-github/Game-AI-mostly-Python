import sys
import logging, traceback, sys, os, inspect
sys.path.insert(0, '../')
from planet_wars import issue_order
from heapq import heappop, heappush
from timeit import default_timer as time


def attack_weakest_enemy_planet(state):
    # (1) If we currently have a fleet in flight, abort plan.
    if len(state.my_fleets()) >= 1:
        return False

    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships, default=None)

    # (3) Find the weakest enemy planet.
    weakest_planet = min(state.enemy_planets(), key=lambda p: p.num_ships, default=None)

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships / 2)


def spread_to_weakest_neutral_planet(state):
    # (1) If we currently have a fleet in flight, just do nothing.
    if len(state.my_fleets()) >= 1:
        return False

    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships, default=None)

    # (3) Find the weakest neutral planet.
    weakest_planet = min(state.neutral_planets(), key=lambda p: p.num_ships, default=None)

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships / 2)


def find_index(state, planet):
    logging.info("Find_index argument: %s" % str(planet))
    planets = state.my_planets() + state.not_my_planets()
    for i in range(0, len(planets)):
        if planets[i] is planet:
            logging.info("Find_index: %s" % str(planets[i]))
            return i


def get_planet(state, index):
    planets = state.my_planets() + state.not_my_planets()
    planets = sorted(planets, key=lambda p: p[0])
    return planets[index]


def has_no_incoming(state, planet):
    #logging.info("has_no_incoming: %s: " % str(planet))
    for el in state.enemy_fleets():
        #logging.info("el[3]: %s" % str(el[3]))
        if el[3] == planet.ID:
            return False
    return True


def no_friendlies_en_route(state, target):
    for fleet in state.my_fleets():
        if fleet.destination_planet == target.ID:
            return False
    return True


def settarget(state):
    start = time()
    #heapq my largest/strongest planets
    strongest_list = sorted(state.my_planets(), key=lambda p: p[4])
    strongest_list = strongest_list[::-1]
    #grab 3 of the strongest that DON'T have enemies approaching them
    top_3 = []
    for strong in strongest_list:
        invalid = False
        for enemy_fleet in state.enemy_fleets():
            if enemy_fleet.destination_planet == strong.ID:
                invalid = True
                break
        if invalid:
            continue
        top_3.append(strong)
        if len(top_3) >= 3:
            break
    strongest_planet = top_3[0]
    #logging.info("A TIME: %s" %str(time()-start))
    shortest = 50                       #50 turns is a LOT
    #find strongest planet's closest enemy planet to attack
    enemies = list(state.enemy_planets())
    closest_enemy = enemies[0]
    for el in enemies:
        dist = state.distance(el.ID, strongest_planet.ID)
        if dist < shortest and no_friendlies_en_route(state, el):
            shortest = dist
            closest_enemy = el

    #logging.info("B TIME: %s" %str(time()-start))
    enemies.remove(closest_enemy)

    #find closest_enemy's friends within a radius of dist
    enemy_backup = 0
    enemy_avg = closest_enemy.num_ships
    enemy_total = closest_enemy.num_ships
    for enemy in enemies:
        dist = state.distance(enemy.ID, closest_enemy.ID)
        if dist <= shortest:
            enemy_backup += 1
            enemy_avg = (enemy_avg + enemy.num_ships-1)/2
            enemy_total += enemy.num_ships

    #logging.info("C TIME: %s" %str(time()-start))
    top_3_avg = 0
    top_3_total = 0
    for top in top_3:
        top_3_avg = (top_3_avg + top.num_ships)/2
        top_3_total += (top.num_ships-1)
    sent_order = False
    if enemy_avg < top_3_avg:                   #they have don't enough backup to beat our guys.
        amt_to_send = closest_enemy.num_ships + (shortest * closest_enemy.growth_rate) + (enemy_avg)
        if amt_to_send < top_3_total:
            for strong in top_3:
                if strong.num_ships < amt_to_send:
                    send_90 = int(strong.num_ships*0.9)
                    issue_order(state, strong.ID, closest_enemy.ID, send_90)
                    sent_order = True
                    amt_to_send -= send_90
                else:
                    issue_order(state, strong.ID, closest_enemy.ID, amt_to_send)
                    sent_order = True

    #logging.info("D TIME: %s" %str(time()-start))
    if sent_order:
        return True
    return False


def quick_attack(state):
    # this attack is meant to attack a weakened enemy planet
    # preferably a neutral planet that was JUST conquered by the enemy.
    # only do this attack if we have nearby planets to the target planet

    start = time()
    target_planet = state.enemy_fleets()[0].destination_planet
    turns_until_full_arrival = 0
    total_fleets_en_route = 0
    enemy_fleets_dict = {}
    my_fleets_dict = {}
    for el in state.enemy_fleets():
        if el.destination_planet == target_planet:
            total_fleets_en_route += el.num_ships
            if el.turns_remaining > turns_until_full_arrival:
                turns_until_full_arrival = el.turns_remaining
        else:
            enemy_fleets_dict[target_planet] = [turns_until_full_arrival, total_fleets_en_route]
            target_planet = el.destination_planet
            total_fleets_en_route = el.num_ships
            turns_until_full_arrival = el.turns_remaining
    enemy_fleets_dict[target_planet] = [turns_until_full_arrival, total_fleets_en_route]

    #logging.info("A TIME: %s" %str(time()-start))
    # now we should have a dict of planets expecting fleets from the enemy
    # do the same thing for our planets
    if len(state.my_fleets()) != 0:
        target_planet = state.my_fleets()[0].destination_planet
        turns_until_full_arrival = 0
        total_fleets_en_route = 0
        for el in state.my_fleets():
            if el.destination_planet == target_planet:
                total_fleets_en_route += el.num_ships
                if el.turns_remaining > turns_until_full_arrival:
                    turns_until_full_arrival = el.turns_remaining
            else:
                my_fleets_dict[target_planet] = [turns_until_full_arrival, total_fleets_en_route]
                target_planet = el.destination_planet
                total_fleets_en_route = el.num_ships
                turns_until_full_arrival = el.turns_remaining
        my_fleets_dict[target_planet] = [turns_until_full_arrival, total_fleets_en_route]

    #logging.info("B TIME: %s" %str(time()-start))
    # go through both dicts to see if we need to add/reinforce our fleets to the same planet
    for el in enemy_fleets_dict.keys():
        # make priority queue of closest planets to target
        heapq = []  # quick cap
        for p in state.my_planets():
            if el != p.ID:                                          # don't put target planet in queue
                distance = state.distance(p.ID, el)
                heappush(heapq, (distance, p))

        planet = get_planet(state, el)
        #now i have a priority queue of planets closest to the target that ISN'T the target
        if planet in state.my_planets():                                #if the target planet is a planet that I own
            current_fleets = 0                                      # reinforce, dont quickcap
            if el in my_fleets_dict:                                #i also already have fleets going to the planet
                current_fleets += my_fleets_dict[el][1]
            pop_at_arrival = current_fleets + planet.num_ships +(enemy_fleets_dict[el][0] * planet.growth_rate)
            if enemy_fleets_dict[el][1] > pop_at_arrival:
                difference = enemy_fleets_dict[el][1] - pop_at_arrival
                while len(heapq) > 0:
                    dist, closest_planet = heappop(heapq)
                    if has_no_incoming(state, closest_planet):
                        if closest_planet.num_ships > difference+2:
                            if dist-enemy_fleets_dict[el][0] > 1:
                                turns = dist - enemy_fleets_dict[el][0]
                                difference += (turns * planet.growth_rate)
                            issue_order(state, closest_planet.ID, planet.ID, difference+1)
                            break

        elif planet in state.neutral_planets():                             #target planet is neutral; QUICK CAP
            if el in my_fleets_dict:                                    #if i have fleets en route to target planet
                if enemy_fleets_dict[el][1] >= my_fleets_dict[el][1]:    #the enemy planet has more fleets en route than me
                    difference = enemy_fleets_dict[el][1] - my_fleets_dict[el][1]
                    while len(heapq) > 0:
                        dist, closest_planet = heappop(heapq)
                        if has_no_incoming(state,closest_planet):
                            if enemy_fleets_dict[el][0] > my_fleets_dict[el][0]:
                                turns_since_cap = enemy_fleets_dict[el][0] - my_fleets_dict[el][0]
                                total_on_arrival = difference + (turns_since_cap * planet.growth_rate)
                                if closest_planet.num_ships > total_on_arrival+2:
                                    issue_order(state, closest_planet.ID, planet.ID, total_on_arrival+1)
                                    break


            else:                                                       #i have no fleets going to target planet
                enemy_turns, enemy_total = enemy_fleets_dict[el]
                if enemy_total > planet.num_ships:
                    difference = enemy_total - planet.num_ships
                    while len(heapq) > 0:
                        dist, closest_planet = heappop(heapq)
                        if has_no_incoming(state, closest_planet):
                            if dist > enemy_turns:
                                turn_difference = dist - enemy_turns
                                total_on_arrival = difference + (turn_difference * planet.growth_rate)
                                if closest_planet.num_ships > total_on_arrival+2:
                                    issue_order(state, closest_planet.ID, planet.ID, total_on_arrival+1)
                                    break
    #logging.info("meowC TIME: %s" %str(time()-start))
    return False


def spread_to_most_efficient_neutral_planet(state):
    start = time()
    nothing_sent = True

    for source in state.my_planets():
        pq = []
        num_ships = int(source.num_ships)
        for neut in state.neutral_planets():
            unit_en_route = False
            for fleets in state.my_fleets():
                if fleets.destination_planet == neut.ID:
                    unit_en_route = True
                    break
            if unit_en_route:
                continue
            distance = state.distance(source.ID, neut.ID)
            if distance <= 12:
                heappush(pq, (distance, source, neut))
        while len(pq) > 0:
            dist, src, nt = heappop(pq)
            fleet_size = nt.num_ships + 1
            if num_ships > fleet_size:
                if has_no_incoming(state, src):
                    issue_order(state, src.ID, nt.ID, fleet_size)
                    num_ships -= fleet_size
                    nothing_sent = False

    #logging.info("A TIME: %s" %str(time()-start))

    if nothing_sent:
        return False
    return True