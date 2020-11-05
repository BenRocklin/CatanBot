import board_parser
import random
from PyCatan import CatanCards

class RandomBot:
    def __init__(self, board, player, name):
        self.is_bot = True
        self.player = player
        self.name = name

    def pick_initial_location(self, game):
        board = game.board
        settlement_locations = board_parser.get_initial_settlement_locations(board)
        chosen_location = random.choice(settlement_locations)
        print("Bot placed settlement in location:", chosen_location)
        game.add_settlement(self.player, chosen_location[0], chosen_location[1], True)
        road_locations = board_parser.get_road_locations(board, game.players[self.player], self.player)
        chosen_road = random.choice(road_locations)
        print("Bot placed road in location:", chosen_road)
        game.add_road(self.player, chosen_road[0], chosen_road[1], True)
        print(self.player)
        print(board.roads)

    def play_turn(self, game, rolled, card_played, building):
        actions = []
        player_obj = game.players[self.player]
        player_cards = player_obj.cards
        if not card_played and not building:
            # haven't played a dev card yet or started building, add dev cards as a potential action
            # for dev_card in player_obj.dev_cards:
            #     if dev_card != CatanCards.DEV_VP:
            #         actions.append(player_obj)
            # actions.append("P" + str(args))
            pass # for now, don't worry about dev cards as an action


        if not rolled:
            # we haven't rolled, must roll or play dev card first
            # Changed to append from extend, otherwise it says "invalid action: O"
            actions.append("ROLL")
        else:
            # if player has rolled, doesn't have to do anything else, can end turn
            actions.append("E")
            if not building:
                # don't have to roll, can opt to trade (have random bot not trade at all yet)
                pass
            if player_cards.count(CatanCards.CARD_BRICK) >= 1 and player_cards.count(CatanCards.CARD_WOOD) >= 1:
                # append all road building locations
                for road in board_parser.get_road_locations(game.board, player_obj, self.player):
                    actions.append("R" + str(road))
            if player_cards.count(CatanCards.CARD_BRICK) >= 1 and player_cards.count(CatanCards.CARD_WOOD) >= 1 and\
               player_cards.count(CatanCards.CARD_WHEAT) >= 1 and player_cards.count(CatanCards.CARD_SHEEP) >= 1:
                # append all settlement locations
                for settlement in board_parser.get_settlement_locations(game.board, self.player):
                    actions.append("S" + str(settlement))
            if player_cards.count(CatanCards.CARD_WHEAT) >= 2 and player_cards.count(CatanCards.CARD_ORE) >= 3:
                # append all city locations
                for city in board_parser.get_city_locations(game.board, self.player):
                    actions.append("C" + str(city))
            if player_cards.count(CatanCards.CARD_WHEAT) >= 1 and player_cards.count(CatanCards.CARD_ORE) >= 1 and\
               player_cards.count(CatanCards.CARD_SHEEP) >= 1:
                # append dev card purchase
                actions.append("D")

        # pick a random action
        return random.choice(actions)

    def review_trade(self, game, requested, rewards):
        # randomly accept the trade
        return bool(random.getrandbits(1))
