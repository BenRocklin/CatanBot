import board_parser
import random
import sys
from PyCatan import CatanCards

class RandomBot:
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

    def pick_initial_location(self, game, logfile):
        """
        Function to pick the first settlement and road locations.

        :param game: the CatanGame instance
        :param logfile: file to log optional output in
        """
        board = game.board

        # pick a random settlement location
        settlement_locations = board_parser.get_initial_settlement_locations(board)
        chosen_location = random.choice(settlement_locations)
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

    def get_turn_action(self, game, rolled, card_played, building, logfile):
        """
        Function to pick the bot's action for a given turn given the state of the turn.

        :param game: CatanGame instance
        :param rolled: whether or not the dice have been rolled for this turn
        :param card_played: whether or not a card has been played on this turn
        :param building: whether or not something has been built on this turn
        :param logfile: file to log optional output in
        :return: the action to take
        """
        actions = []
        # fetch the internal player object from CatanGame
        player_obj = game.players[self.player_id]
        player_cards = player_obj.cards # the bot's resource cards

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
            actions.append("ROLL")
        else:
            # if player has rolled, doesn't have to do anything else, can end turn, can also now build
            actions.append("E")
            if not building:
                # don't have to roll, can opt to trade (have random bot not trade at all yet)
                pass
            if player_cards.count(CatanCards.CARD_BRICK) >= 1 and player_cards.count(CatanCards.CARD_WOOD) >= 1:
                # append all road building locations
                for road in board_parser.get_road_locations(game.board, player_obj, self.player_id):
                    actions.append("R" + str(road))
            if player_cards.count(CatanCards.CARD_BRICK) >= 1 and player_cards.count(CatanCards.CARD_WOOD) >= 1 and\
               player_cards.count(CatanCards.CARD_WHEAT) >= 1 and player_cards.count(CatanCards.CARD_SHEEP) >= 1:
                # append all settlement locations
                for settlement in board_parser.get_settlement_locations(game.board, self.player_id):
                    actions.append("S" + str(settlement))
            if player_cards.count(CatanCards.CARD_WHEAT) >= 2 and player_cards.count(CatanCards.CARD_ORE) >= 3:
                # append all city locations
                for city in board_parser.get_city_locations(game.board, self.player_id):
                    actions.append("C" + str(city))

            # for now, don't allow dev card purchases
            # if player_cards.count(CatanCards.CARD_WHEAT) >= 1 and player_cards.count(CatanCards.CARD_ORE) >= 1 and\
            #    player_cards.count(CatanCards.CARD_SHEEP) >= 1:
            #     # append dev card purchase
            #     actions.append("D")

        # pick a random action
        action = random.choice(actions)
        print(self.name, "chose action", action)
        return action

    def review_trade(self, game, requested, rewards):
        # randomly accept the trade
        return bool(random.getrandbits(1))
