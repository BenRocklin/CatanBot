from PyCatan import CatanBuilding

row_lengths = {0: 7, 1: 9, 2: 11, 3: 11, 4: 9, 5: 7}

def get_road_locations(board, player, player_id):
    """
    Helper function to fetch all possible settlement building locations during standard gameplay.

    :param board: board to find locations on
    :param player: CatanGame internal player object representation (game.players[player_id])
    :param player_id: id of the player to find locations for
    :return: list of all valid locations
    """
    road_locations = []
    for r in range(6):
        for l in range(row_lengths[r]):
            # get all adjacent locations to a given point to get three possible roads for each spot in the hexgrid
            adjacent_locations = get_adjacent_locations((r, l))
            for adjacent in adjacent_locations:
                # for each of the three roads...
                if player.road_location_is_valid([r, l], [adjacent[0], adjacent[1]]) == 2:
                    # use internal check to ensure that the road may be placed by a player (complicated logic)
                    # NOTE: the above is buggy and mainly just checks that another road isn't already there, more checks below are necessary
                    pointA = board.points[r][l]
                    pointB = board.points[adjacent[0]][adjacent[1]]
                    if (adjacent[0] < r) or (adjacent[0] == r and adjacent[1] < l):
                        # ensure each road is listed only once for the user's sanity
                        continue
                    if (pointA and pointA.owner == player_id) or (pointB and pointB.owner == player_id):
                        # need to check that a player owns an adjacent settlement/city (simulator checks miss this)
                        road_locations.append([[r, l], list(adjacent)])
                    else:
                        # need to check that it is adjacent to another player-owned road (simulator checks miss this)
                        for road in board.roads:
                            if road.owner == player_id:
                                # if the road is owned by the same player, check if it connects to the proposed road
                                road_start = road.point_one
                                road_end = road.point_two
                                if (road_start[0] == r and road_start[1] == l) or\
                                   (road_end[0] == r and road_end[1] == l) or\
                                   (road_start[0] == adjacent[0] and road_start[1] == adjacent[1]) or\
                                   (road_end[0] == adjacent[0] and road_end[1] == adjacent[1]):
                                    road_locations.append([[r, l], list(adjacent)])
    return road_locations

def get_city_locations(board, player_id):
    """
    Helper function to fetch all possible city building locations during standard gameplay.

    :param board: board to find locations on
    :param player_id: id of the player to find locations for
    :return: list of all valid locations
    """
    # TODO: potentially wasteful, could just check all player owned structures instead, works for now
    open_locations = []
    for r in range(6):
        for l in range(row_lengths[r]):
            building = board.points[r][l]
            if building and building.type == CatanBuilding.BUILDING_SETTLEMENT and building.owner == player_id:
                # if the building is a player-owned settlement, add it to that player's city locations
                open_locations.append([r, l])
    return open_locations

def get_initial_settlement_locations(board):
    """
    Helper function to fetch all possible settlement building locations during initial placement.

    :param board: board to find locations on
    :return: list of all valid locations
    """
    open_locations = []
    for r in range(6):
        for l in range(row_lengths[r]):
            # simply need to check adjacency since settlements may be freely placed in any valid location by any player
            if check_settlement_valid(board, (r, l)):
                open_locations.append((r, l))
    return open_locations

def get_settlement_locations(board, player_id):
    """
    Helper function to fetch all possible settlement building locations during standard gameplay.

    :param board: board to find locations on
    :param player_id: id of the player to find locations for
    :return: list of all valid locations
    """
    open_locations = []

    # TODO: potentially lots of wasteful work here but shouldn't be too bad for board of this size
    # settlements always occur at the end of player-owned roads, so we enumerate the list of roads to find locations
    for road in board.roads:
        if road.owner == player_id:
            road_start = road.point_one
            road_end = road.point_two
            # check each end of the road to see if settlement valid
            if check_settlement_valid(board, road_start):
                open_locations.append(road_start)
            if check_settlement_valid(board, road_end):
                open_locations.append(road_end)
    return open_locations

def get_adjacent_locations(location):
    """
    Helper function to find all adjacent positions to another in CatanGame coordinates.

    :param location: CatanGame location coordinates
    :return: list of adjacent locations
    """
    row = location[0]
    slot = location[1]

    adjacent_locations = []

    # check left node
    if slot > 0:
        adjacent_locations.append((row, slot - 1))

    # check right node
    if slot < row_lengths[row] - 1:
        adjacent_locations.append((row, slot + 1))

    # check other row
    if (row == 0 or row == 1) and slot % 2 == 0:
        adjacent_locations.append((row + 1, slot + 1))
    if (row == 1 or row == 2) and slot % 2 == 1:
        adjacent_locations.append((row - 1, slot - 1))
    if row == 2 and slot % 2 == 0:
        adjacent_locations.append((row + 1, slot))
    if row == 3 and slot % 2 == 0:
        adjacent_locations.append((row - 1, slot))
    if (row == 3 or row == 4) and slot % 2 == 1:
        adjacent_locations.append((row + 1, slot - 1))
    if (row == 4 or row == 5) and slot % 2 == 0:
        adjacent_locations.append((row - 1, slot + 1))
    return adjacent_locations

def check_settlement_valid(board, location):
    """
    Checks if a settlement can be placed in a given location on a board.

    :param board: the board to check the location on
    :param location: the settlement location to check
    :return: a boolean specifying if a settlement may be placed in the given location or not
    """
    # if the settlement location is occupied, it isn't valid
    locations = board.points
    row = location[0]
    slot = location[1]
    if locations[row][slot] != None:
        return False

    adjacent_locations = get_adjacent_locations(location)
    # a valid settlement cannot have another settlement less than two roads away/adjacent to it
    for adjacent in adjacent_locations:
        if locations[adjacent[0]][adjacent[1]] is not None:
            return False

    return True
