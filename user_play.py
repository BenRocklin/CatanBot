import board_parser
row_lengths = {0: 7, 1: 9, 2: 11, 3: 11, 4: 9, 5: 7}

class User:
    def __init__(self, board, player, name):
        self.is_bot = False
        self.player = player
        self.name = name

    def location_input(self):
        row = None
        while row is None or row < 0 or row > 5:
            try:
                row = int(input("    Please enter a row number from 0 to 5: "))
            except:
                row = None
        slot = None
        while slot is None or slot < 0 or slot > row_lengths[row]:
            try:
                slot = int(input("    Please enter a position on the row from 0 to " + str(row_lengths[row]) + ": "))
            except:
                slot = None
        return row, slot

    def pick_initial_location(self, game):
        board = game.board
        print("Player", self.name, ", please pick a settlement location.")
        print(board_parser.get_initial_settlement_locations(board))
        while True:
            chosen_location = self.location_input()
            retval = game.add_settlement(self.player, chosen_location[0], chosen_location[1], True)
            if retval == 2:
                break
            else:
                print("Location failed with status code", retval, ", please try another valid location.")

        print("Player", self.name, ", please pick a road location.")
        print(board_parser.get_road_locations(board, game.players[self.player], self.player))
        while True:
            print("Pick the first location:")
            first_location = self.location_input()
            print("Pick the second location:")
            second_location = self.location_input()
            retval = game.add_road(self.player, list(first_location), list(second_location), True)
            if retval == 2:
                break
            else:
                print("Location failed with status code", retval, ", please try another valid location.")

    def play_turn(self, game, rolled, card_played, building):
        pass

    def review_trade(self, game, requested, rewards):
        pass
