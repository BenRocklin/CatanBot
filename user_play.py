import board_parser
from PyCatan import CatanCards
row_lengths = {0: 7, 1: 9, 2: 11, 3: 11, 4: 9, 5: 7}

class User:
    def __init__(self, game, player_id, name):
        """
        Player constructor

        :param game: the CatanGame (in case the user wants to preprocess)
        :param player_id: the player's unique ID to store
        :param name: the name of the player
        """
        self.is_bot = False
        self.player_id = player_id
        self.name = name

    def pick_initial_location(self, game, logfile):
        """
        Function to pick the first settlement and road locations.

        :param game: the CatanGame instance
        :param logfile: file to log optional output in
        """
        board = game.board

        # fetch the free settlement location and keep trying to place it until it passes. If it fails, print the error
        print("Player", self.name, ":")
        while True:
            chosen_location = self.settlement_input(game, True)
            retval = game.add_settlement(self.player_id, chosen_location[0], chosen_location[1], True)
            if retval == 2:
                break
            else:
                print("Location failed with status code", retval, ", please try another valid location.")

        # fetch the free road location and keep trying to place it until it passes. If it fails, print the error
        while True:
            chosen_location = self.road_input(game)

            # attempt to place it
            retval = game.add_road(self.player_id, chosen_location[0], chosen_location[1], True)
            if retval == 2:
                break
            else:
                print("Location failed with status code", retval, ", please try another valid location.")

    def get_turn_action(self, game, rolled, card_played, building, logfile):
        player_obj = game.players[self.player_id]
        player_cards = player_obj.cards # the bot's resource cards

        # enumerate all possible actions to player
        print("Player", self.name, ", please pick an action:")
        print("Owned cards:", str(player_cards))
        possible_actions = []
        if not rolled:
            possible_actions.append("ROLL")
        else:
            possible_actions.append("END")
            if player_cards.count(CatanCards.CARD_BRICK) >= 1 and player_cards.count(CatanCards.CARD_WOOD) >= 1:
                possible_actions.append("ROAD")
            if player_cards.count(CatanCards.CARD_BRICK) >= 1 and player_cards.count(CatanCards.CARD_WOOD) >= 1 and\
               player_cards.count(CatanCards.CARD_WHEAT) >= 1 and player_cards.count(CatanCards.CARD_SHEEP) >= 1:
                possible_actions.append("SETTLEMENT")
            if player_cards.count(CatanCards.CARD_WHEAT) >= 2 and player_cards.count(CatanCards.CARD_ORE) >= 3:
                possible_actions.append("CITY")

        # have user pick action from possible actions
        print("Possible actions:", str(possible_actions))
        valid = False
        action = None
        while not valid:
            # while the user hasn't picked a proper action, keep prompting
            action_input = input("Please enter an action: ")
            # check the input to make sure it's a valid action and, if necessary, obtain additional input (i.e. locations)
            if action_input.lower() == "roll" and "ROLL" in possible_actions:
                valid = True
                action = "ROLL"
            if (action_input.lower() == "end" or action_input.lower() == "e") and "END" in possible_actions:
                valid = True
                action = "E"
            if (action_input.lower() == "road" or action_input.lower() == "r") and "ROAD" in possible_actions:
                valid = True
                action = "R" + str(self.road_input(game))
            if (action_input.lower() == "settlement" or action_input.lower() == "s") and "SETTLEMENT" in possible_actions:
                valid = True
                action = "S" + str(self.settlement_input(game))
            if (action_input.lower() == "city" or action_input.lower() == "c") and "CITY" in possible_actions:
                valid = True
                action = "C" + str(self.city_input(game))
            print("INVALID ACTION INPUT:", action_input)
        return action

    def review_trade(self, game, requested, rewards):
        pass

    def location_input(self):
        """
        Helper function to deal with user inputting a Catan location (takes the form [i, j] where i, j are indices)

        :return: the Catan location to return
        """
        row = None
        while row is None or row < 0 or row > 5:
            try:
                row = int(input("Please enter a row number from 0 to 5: "))
            except:
                row = None
        slot = None
        while slot is None or slot < 0 or slot > row_lengths[row]:
            try:
                slot = int(input("Please enter a position on the row from 0 to " + str(row_lengths[row]) + ": "))
            except:
                slot = None
        return row, slot

    def city_input(self, game):
        """
        Helper function to deal with user inputting a city location

        :return: the location of the city
        """
        print("Please pick a city location from the list of options below:")
        print(board_parser.get_city_locations(game.board, self.player_id))
        return list(self.location_input())

    def settlement_input(self, game, initial=False):
        """
        Helper function to deal with user inputting a settlement location

        :return: the location of the settlement
        """
        print("Please pick a settlement location from the list of options below:")
        if initial:
            print(board_parser.get_initial_settlement_locations(game.board))
        else:
            print(board_parser.get_settlement_locations(game.board, self.player_id))
        return list(self.location_input())

    def road_input(self, game):
        """
        Helper function to deal with user inputting a road location

        :return: the location of the settlement
        """
        print("Please pick a road location from the list of options below:")
        print(board_parser.get_road_locations(game.board, game.players[self.player_id], self.player_id))
        print("Pick the first location:")
        first_location = self.location_input()
        print("Pick the second location:")
        second_location = self.location_input()
        return [list(first_location), list(second_location)]
