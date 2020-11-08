import board_parser
import random
import sys

from PyCatan import CatanCards, CatanBuilding
import play_game

class OnlinePlanningBot:
    def __init__(self, game, player_id, name):
        """
        Bot constructor

        :param game: the CatanGame (in case the bot wants to preprocess)
        :param player_id: the bot's unique ID to store
        :param name: the name of the bot
        """
        self.is_bot = True
        self.player_id = player_id
        self.name = name
        
    def add_yield_for_roll(self, game, roll, state):
        """
        Bug-free version to add dice roll yields.

        :param game: CatanGame instance
        :param roll: the roll to use
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
                                if owner == self.player_id: 
                                    if card_type ==CatanCards.CARD_BRICK: 
                                        state[1][0] += 1
                                    elif card_type == CatanCards.CARD_WOOD: 
                                        state[1][1] += 1 
                                    elif card_type == CatanCards.CARD_SHEEP: 
                                        state[1][2] += 1
                                    elif card_type == CatanCards.CARD_WHEAT: 
                                        state[1][3] += 1
                                    else: 
                                        state[1][4] += 1
                        except:
                            print("INVALID HEX, SKIPPING")
        return state 

    def pick_initial_location(self, game, logfile):
        """
        Function to pick the first settlement and road locations.

        :param game: the CatanGame instance
        :param logfile: file to log optional output in
        """
        board = game.board

        # pick a random settlement location
        settlement_locations = board_parser.get_initial_settlement_locations(board)
        while True:
            chosen_location = random.choice(settlement_locations)
            if (chosen_location[0] != 0 and chosen_location[0] != 5 and chosen_location[1] != 0 and chosen_location[1] != 11):
                break
        
        retval = game.add_settlement(self.player_id, chosen_location[0], chosen_location[1], True)
        print(self.name, "placed settlement in location:", chosen_location, "with retval", retval)
        if retval != 2:
            sys.exit("INVALID LOCATION PICKED FOR INITIAL SETTLEMENT, FIX ME")

        # pick a random road location
        road_locations = board_parser.get_road_locations(board, game.players[self.player_id], self.player_id)
        chosen_road = random.choice(road_locations)
        retval = game.add_road(self.player_id, chosen_road[0], chosen_road[1], True)
        print(self.name, "placed road in location:", chosen_road, "with retval", retval)
        if retval != 2:
            sys.exit("INVALID LOCATION PICKED FOR INITIAL SETTLEMENT, FIX ME")
            
    def update_resources(self, state, action): 
        if action == 'C':
            state[1][3] -= 2
            state[1][4] -= 3
            return state

        state[1][0] -= 1 # brick 
        state[1][1] -= 1 # wood 
        if action == 'S': 
            state[1][2] -= 1 # sheep 
            state[1][3] -= 1 # wheat 
        return state

    def restore_resources(self, state, action): 
        if action == 'C':
            state[1][3] += 2
            state[1][4] += 3
            return state
        state[1][0] += 1 # brick 
        state[1][1] += 1 # wood 
        if action == 'S': 
            state[1][2] += 1 # sheep 
            state[1][3] += 1 # wheat 
        return state
    
    # state -> [victory_points, resource_cards, rolled]
    # state[0]: victory_points 
    # state[1] : resource_cards 
    # state[2] : rolled 
    def lookahead(self, game, state, board, card_played, building, depth): 
        print("DOING LOOKAHEAD AT DEPTH ", depth, "AND STATE IS ", state)
        if depth == 0: 
            #print("AT DEPTH 0 AND OUR STATE IS", state)
            #print("GOING TO RETURN E")
            return 0, "E"
        best_val = 0
        best_action = "E"
        
        if state[2]: 
            actions = self.get_possible_actions(game, state, state[2], card_played, building)
#            print("ACTIONS ARE", actions)
            for action in actions: 
                if action[0] == 'R': 
                    print("WE ARE IN ROADS")
                    roads = action[1]
                    pt1 = roads[0]
                    pt2 = roads[1]
                    simulated_road = CatanBuilding(self.player_id, CatanBuilding.BUILDING_ROAD, pt1, pt2)
                    board.roads.append(simulated_road)
                    state = self.update_resources(state, action[0])
                    state[2] = False
                    expected_val = 0.99 * self.lookahead(game, state, board, card_played, building, depth - 1)[0]
                    board.roads.pop()
                    state = self.restore_resources(state, action[0])
                    if expected_val >= best_val:
                        best_action = action
                        best_val = expected_val
                elif action[0] == 'S': 
                    

                    print("WE ARE IN SETTLEMENTS")
                    settlement = action[1] # settlment coordinate 
                    simulated_settlement = CatanBuilding(self.player_id, CatanBuilding.BUILDING_SETTLEMENT)
                    board.points[settlement[0]][settlement[1]] = simulated_settlement
                    state[0] += 1
                    state = self.update_resources(state, action[0])
                    state[2] = False
                    #if state[0] == 4: 
                    #    expected_val = 10
                    #else:
                    expected_val = 1 + 0.99 * self.lookahead(game, state, board, card_played, building, depth - 1)[0]
                    board.points[settlement[0]][settlement[1]] = None 
                    state = self.restore_resources(state, action[0])
                    if expected_val >= best_val: 
                        best_val = expected_val
                        best_action = action
                elif action[0] == 'C': 
                
                    print("WE ARE IN CITIES")
                    city = action[1] # settlment coordinate 
                    simulated_city = CatanBuilding(self.player_id, CatanBuilding.BUILDING_CITY)
                    board.points[city[0]][city[1]] = simulated_city
                    state[0] += 1
                    state = self.update_resources(state, action[0])
                    state[2] = False
                    #if state[0] == 4: 
                    #    expected_val = 10
                    #else:
                    expected_val = 1 + 0.99 * self.lookahead(game, state, board, card_played, building, depth - 1)[0]
                    board.points[city[0]][city[1]] = CatanBuilding(self.player_id, CatanBuilding.BUILDING_SETTLEMENT) 
                    state = self.restore_resources(state, action[0])
                    if expected_val >= best_val: 
                        best_val = expected_val
                        best_action = action
            #print("ABOUT TO RETURN FOR ROLLED = TRUE")
            print("OUR BEST VALUE IS", best_val)
            return best_val, best_action
        else: 
            # call lookahead 10 times and weigh based on how likely it'll happen 
            # consider dist where 2 has prob of 1/36 showing up. 
            # pick a random num from dist 2-6 or 8-11 
            # assume that number and and call lookahead 
            # pick a random number between one and 36. if num is 1 -> correspond to 
            rand30 = random.randint(1, 30)
            dice_sum = 2
            if rand30 == 1: 
                dice_sum = 2
            elif rand30 == 2 or rand30 == 3:
                dice_sum = 3
            elif rand30 <= 6:
                dice_sum = 4
            elif rand30 <= 10:
                dice_sum = 5
            elif rand30 <= 15:
                dice_sum = 6
            elif rand30 <= 20:
                dice_sum = 8
            elif rand30 <= 24:
                dice_sum = 9
            elif rand30 <= 27:
                dice_sum = 10
            elif rand30 <= 29:
                dice_sum = 11
            else:
                dice_sum = 12
                
            state = self.add_yield_for_roll(game, dice_sum, state)
            state[2] = True
            #print("ABOUT TO RETURN FOR ROLL = FALSE")
            return 0.99 * self.lookahead(game, state, board, card_played, building, depth - 1)[0], "ROLL"




                
    def get_possible_actions(self, game, state, rolled, card_played, building):
        print("OUR STATE IS", state)
        """
        Return all possible actions

        :param game: CatanGame instance
        :param rolled: whether or not the dice have been rolled for this turn
        :param card_played: whether or not a card has been played on this turn
        :param building: whether or not something has been built on this turn
        :param logfile: file to log optional output in
        :return: the action to take
        """
        actions = []

        # enumerate all possible actions below

        if not card_played and not building:
            # haven't played a dev card yet or started building, add dev cards as a potential action
            # for dev_card in player_obj.dev_cards:
            #     if dev_card != CatanCards.DEV_VP:
            #         actions.append(player_obj)
            # actions.append("P" + str(args))
            pass # for now, don't worry about dev cards as an action

        if not rolled:
            # we haven't rolled, must roll or play dev card first
            actions.append(["ROLL"])
        else:
            # if player has rolled, doesn't have to do anything else, can end turn, can also now build
            actions.append(["E"])
            player_obj = game.players[self.player_id]
            if not building:
                # don't have to roll, can opt to trade (have random bot not trade at all yet)
                pass
            if state[1][0] >= 1 and state[1][1] >= 1:
            #if True:
                # append all road building locations
                for road in board_parser.get_road_locations(game.board, player_obj, self.player_id):
                    actions.append(["R", road])
            if state[1][0] >= 1 and state[1][1] >= 1 and state[1][2] >= 1 and state[1][3] >= 1:
                # append all settlement locations
                for settlement in board_parser.get_settlement_locations(game.board, self.player_id):
                    actions.append(["S", settlement])

            if state[1][3] >= 2 and state[1][4] >= 3:
                # append all city locations
                for city in board_parser.get_city_locations(game.board, self.player_id):
                    actions.append(["C", city])
            # if player_cards.count(CatanCards.CARD_WHEAT) >= 2 and player_cards.count(CatanCards.CARD_ORE) >= 3:
            #     # append all city locations
            #     for city in board_parser.get_city_locations(game.board, self.player_id):
            #         actions.append(["C", city])

            # for now, don't allow dev card purchases
            # if player_cards.count(CatanCards.CARD_WHEAT) >= 1 and player_cards.count(CatanCards.CARD_ORE) >= 1 and\
            #    player_cards.count(CatanCards.CARD_SHEEP) >= 1:
            #     # append dev card purchase
            #     actions.append("D")

        # action = random.choice(actions)
        return actions
    
    def get_turn_action(self, game, rolled, card_played, building, logfile): 
        state = [0, [0, 0, 0, 0, 0], rolled]
        
        state[0] = game.players[self.player_id].get_VP()
        player_obj = game.players[self.player_id]
        player_cards = player_obj.cards
        state[1][0] = player_cards.count(CatanCards.CARD_BRICK)
        state[1][1] = player_cards.count(CatanCards.CARD_WOOD)
        state[1][2] = player_cards.count(CatanCards.CARD_SHEEP)
        state[1][3] = player_cards.count(CatanCards.CARD_WHEAT)
        state[1][4] = player_cards.count(CatanCards.CARD_ORE)
        #state = [0, [10, 10, 10, 10, 10], rolled]
        if not rolled:
            return ["ROLL"] 
        
        depth = 8
        best_v = self.lookahead(game, state, game.board, card_played, building, depth)[0]
        best_a = self.lookahead(game, state, game.board, card_played, building, depth)[1]
        print("ABOUT TO RETURN FOR THE LAST TIME AND OUR BEST ACTION IS", best_a)
        print("ABOUT TO LAST RETURN AND OUR BEST VALUE IS ", best_v)
        return best_a

    def review_trade(self, game, requested, rewards):
        # randomly accept the trade
        return bool(random.getrandbits(1))
