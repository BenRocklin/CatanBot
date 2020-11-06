from bots.random_bot import RandomBot
from user_play import User

from PyCatan import CatanBoard, CatanBuilding, CatanCards, CatanGame, CatanPlayer, CatanStatuses

"""
Catan controller to maintain game. All code should be RL-agnostic (that is, all code related to states/actions/models
of the game should be handled within the players!).
"""

def add_yield_for_roll(game, roll):
    """
    Bug-free version to add dice roll yields.

    :param game:
    :param roll:
    :return:
    """
    board = game.board
    for r in range(len(board.points)):
        for i in range(len(board.points[r])):

            if board.points[r][i] != None:

                hex_indexes = board.get_hexes_for_point(r, i)

                # checks if any hexes have the right number
                for num in hex_indexes:

                    # makes sure the robber isn't there
                    if board.robber[0] == num[0] and board.robber[1] == num[1]:

                        # skips this hex
                        continue

                    try:
                        if board.hex_nums[num[0]][num[1]] == roll:

                            # adds the card to the player's inventory
                            owner = board.points[r][i].owner

                            # gets the card type
                            hex_type = board.hexes[num[0]][num[1]]
                            card_type = CatanBoard.get_card_from_hex(hex_type)

                            # adds two if it is a city
                            if board.points[r][i].type == CatanBuilding.BUILDING_CITY:
                                game.players[owner].add_cards([
                                    card_type,
                                    card_type
                                ])

                            else:
                                game.players[owner].add_cards([
                                    card_type
                                ])
                    except:
                        print("INVALID HEX, SKIPPING")

def begin_play(game, order, players, logfile):
    """
    Handles initial input for the first two settlements for all players. For now, do not award cards placed
    on initial settlement.

    :param game: the CatanGame object instantiated earlier
    :param order: the order in which the players play
    :param players: dictionary containing all player objects implementing standard player API
    :param logfile: file to log optional output in
    """
    # place first settlement and road for each player
    for player_name in order:
        player = players[player_name]
        print(player_name, "picking an initial settlement")
        player.pick_initial_location(game, logfile)

    # place second settlement and road for each player in reversed order
    for player_name in reversed(order):
        player = players[player_name]
        print(player_name, "picking a second initial settlement")
        player.pick_initial_location(game, logfile)

def continue_play(game, order, players, logfile):
    """
    Handles standard gameplay loop of roll->trade->build. For now, trade is abstracted out from the loop.

    :param game: CatanGame instance
    :param order: order in which players play
    :param players: dictionary containing all player objects implementing standard player API
    :param logfile: file to log optional output in
    """
    while True:
        # TODO: For now, infinite loop. Eventually break once a player has the desired win condition (probably 5 points)
        # note for Sandy: point checks can be done via game.players[player_name].get_VP()
        for player_name in order:
            # give each player all information necessary to make a decision
            rolled = False # if the player has rolled this turn (means they can't roll again but can now build)
            card_played = False # if the player has played a dev card this turn (means they can't play another)
            building = False # if the player has begun to build this turn (means they can't trade or play cards this turn)
            player = players[player_name]
            print(player_name, "playing turn")
            while True:
                # let player continue playing turn until they decide to end it
                action = player.get_turn_action(game, rolled, card_played, building, logfile)
                retval = 2 # return value from game performing given action for debugging purposes
                if action[0] == "ROLL":
                    # if the player rolled, get a random number (prevent 7 for simplicity) and payout money
                    roll = game.get_roll()
                    while roll == 7:
                        roll = game.get_roll()
                    print("Rolled a", roll)
                    add_yield_for_roll(game, roll)
                    rolled = True
                elif action[0] == 'R':
                    # building a road
                    args = action[1]
                    print(args)
                    retval = game.add_road(player.player_id, args[0], args[1])
                    print("ROAD BUILT")
                    building = True if (retval == 2) else building # only say we've built if the user chose a correct location
                elif action[0] == 'S':
                    # building a settlement
                    args = action[1]
                    retval = game.add_settlement(player.player_id, args[0], args[1])
                    building = True if (retval == 2) else building # only say we've built if the user chose a correct location
                elif action[0] == 'C':
                    # building a city
                    args = action[1]
                    retval = game.add_city(args[0], args[1], player.player_id)
                    building = True if (retval == 2) else building # only say we've built if the user chose a correct location
                # elif action[0] == 'B':
                #     # trade cards into bank (counts as building)
                #     args = list(action[1:])
                #     toss_cards = args[0]
                #     gain_card = args[1]
                #     game.trade_to_bank(player.player, toss_cards, gain_card)
                #     building = true
                elif action[0] == 'E':
                    # user is ending turn
                    break
                else:
                    # user's action is unrecognized, do nothing
                    print("UNRECOGNIZED ACTION:", action)
                    continue
                print("Action resulted in retval:", retval)

def play_game(player_types):
    """
    Main function to handle starting a game and initializing players.

    :param player_types: Types of the players as set in main.py
    """
    game = CatanGame(2)
    order = ["Red", "Blue"]

    print(game.board.hex_nums)
    print(game.board.points)
    print(game.board.hexes)
    for r in range(len(game.board.points)):
        for i in range(len(game.board.points[r])):
            print(r, i)
            hex_indexes = game.board.get_hexes_for_point(r, i)
            print(hex_indexes)

    index = 0
    players = {}
    for player_type in player_types:
        if player_type == "Random":
            players[order[index]] = RandomBot(game, index, order[index])
        elif player_type == "RL":
            # TODO: replace below constructor with RLBot constructor
            players[order[index]] = RandomBot(game, index, order[index])
        elif player_type == "OP":
            # TODO: replace below constructor with OnlinePlanningBot constructor
            players[order[index]] = RandomBot(game, index, order[index])
        else:
            # replace with a human otherwise
            players[order[index]] = User(game, index, order[index])
        index += 1

    logfile = open('storage.csv', "w")
    begin_play(game, order, players, logfile)
    continue_play(game, order, players, logfile)


