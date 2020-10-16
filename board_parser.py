from PyCatan import CatanBuilding

row_lengths = {0: 7, 1: 9, 2: 11, 3: 11, 4: 9, 5: 7}

def get_adjacent_locations(location):
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

def get_road_locations(board, player, num):
    road_locations = []
    for r in range(6):
        for l in range(row_lengths[r]):
            adjacent_locations = get_adjacent_locations((r, l))
            for adjacent in adjacent_locations:
                if player.road_location_is_valid([r, l], [adjacent[0], adjacent[1]]) == 2:
                    pointA = board.points[r][l]
                    pointB = board.points[adjacent[0]][adjacent[1]]
                    if (pointA and pointA.owner == num) or (pointB and pointB.owner == num):
                        # need to check that a player owns an adjacent settlement/city
                        road_locations.append([[r, l], list(adjacent)])
                    else:
                        # need to check that it is adjacent to another player-owned road
                        for road in board.roads:
                            if road.owner == num:
                                road_start = road.point_one
                                road_end = road.point_two
                                if (road_start[0] == r and road_start[1] == l) or\
                                   (road_end[0] == r and road_end[1] == l) or\
                                   (road_start[0] == adjacent[0] and road_start[1] == adjacent[1]) or\
                                   (road_end[0] == adjacent[0] and road_end[1] == adjacent[1]):
                                    road_locations.append([[r, l], list(adjacent)])
    return road_locations

def get_city_locations(board, num):
    open_locations = []
    for r in range(6):
        for l in range(row_lengths[r]):
            building = board.points[r][l]
            if building and building.type == CatanBuilding.BUILDING_SETTLEMENT and building.owner == num:
                # if the building is a player-owned settlement, add it to that player's city locations
                open_locations.append([r, l])
    return open_locations

def get_initial_settlement_locations(board):
    open_locations = []
    for r in range(6):
        for l in range(row_lengths[r]):
            if check_settlement_valid(board, (r, l)):
                open_locations.append((r, l))
    return open_locations

def get_settlement_locations(board, num):
    open_locations = []
    for road in board.roads:
        if road.owner == num:
            road_start = road.point_one
            road_end = road.point_two
            if check_settlement_valid(board, road_start):
                open_locations.append(road_start)
            if check_settlement_valid(board, road_end):
                open_locations.append(road_end)
    return open_locations

def check_settlement_valid(board, location):
    locations = board.points
    row = location[0]
    slot = location[1]
    if locations[row][slot] != None:
        return False

    adjacent_locations = get_adjacent_locations(location)
    for adjacent in adjacent_locations:
        if locations[adjacent[0]][adjacent[1]] is not None:
            return False

    return True
