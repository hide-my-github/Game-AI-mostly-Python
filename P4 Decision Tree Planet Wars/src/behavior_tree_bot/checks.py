

def if_neutral_planet_available(state):
    return any(state.neutral_planets())


def more_enemies_than_neutrals(state):
    if len(state.neutral_planets()) > len(state.enemy_planets()):
        return False
    return True


def have_largest_fleet(state):
    return sum(planet.num_ships for planet in state.my_planets()) \
             + sum(fleet.num_ships for fleet in state.my_fleets()) \
           > sum(planet.num_ships for planet in state.enemy_planets()) \
             + sum(fleet.num_ships for fleet in state.enemy_fleets())


def enemy_fleets_exist(state):
    #if enemy has no fleets then q_atk isn't needed. move onto Spread
    if len(state.enemy_fleets()) == 0:
        return False
    return True


def have_planets_not_my_own(state):
    if len(state.not_my_planets()) != 0:
        return True
    return False


def succeed(state):
    return True


def failure(state):
    return False