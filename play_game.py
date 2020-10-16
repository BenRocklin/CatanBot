import random

from bots.random_bot import RandomBot
from user_play import User

from PyCatan import CatanBoard, CatanCards, CatanGame, CatanPlayer, CatanStatuses

def begin_play(game, order, players):
    for player_name in order:
        player = players[player_name]
        print(player_name, "picking an initial settlement")
        location = player.pick_initial_location(game)
    for player_name in reversed(order):
        player = players[player_name]
        print(player_name, "picking a second initial settlement")
        location = player.pick_initial_location(game)

def continue_play(game, order, players):
    while True:
        for player_name in order:
            rolled = False
            card_played = False
            building = False
            player = players[player_name]
            print(player_name, "playing turn")
            while True:
                action = player.play_turn(game, rolled, card_played, building)
                if action == "ROLL":
                    roll = game.get_roll()
                    game.add_yield_for_roll(roll)
                    print("Rolled a", roll)
                    rolled = True
                elif action[0] == 'P':
                    # playing a dev card
                    args = list(action[1:])
                    game.use_dev_card(player.player, args[0], args[1:])
                    card_played = True
                elif action[0] == 'R':
                    # building a road
                    args = list(action[1:])
                    game.add_road(player.player, args[0], args[1])
                    building = True
                elif action[0] == 'S':
                    # building a settlement
                    args = list(action[1:])
                    game.add_settlement(player.player, args[0], args[1])
                    building = True
                elif action[0] == 'C':
                    # building a city
                    args = list(action[1:])
                    game.add_city(args[0], args[1], player.player)
                    building = True
                elif action[0] == 'D':
                    # building a development card
                    game.build_dev(player.player)
                    building = True
                elif action[0] == 'T':
                    # trading
                    args = list(action[1:])
                    tradee = args[0]
                    trader_send_cards = args[1]
                    trader_receive_cards = args[2]
                    for other in players:
                        if other.player == tradee and other.review_trade(game, trader_receive_cards, trader_send_cards):
                            # if other player accepted, perform trade
                            game.trade(player.player, tradee, trader_send_cards, trader_receive_cards)
                elif action[0] == 'B':
                    # trade cards into bank (counts as building)
                    args = list(action[1:])
                    toss_cards = args[0]
                    gain_card = args[1]
                    game.trade_to_bank(player.player, toss_cards, gain_card)
                elif action[0] == 'E':
                    break
                else:
                    print("UNRECOGNIZED ACTION:", action)

def play_game(player_num, bots_types):
    game = CatanGame(player_num + len(bots_types))
    order = []

    index = 0
    players = {}
    for player_id in range(player_num):
        player_name = "Player" + str(player_id)
        players[player_name] = User(game.board, index, player_name)
        order.append(player_name)
        index += 1
    bots = {}
    for bot_id in range(len(bots_types)):
        bot_type = bots_types[bot_id]
        bot_name = bot_type + str(bot_id)
        if bot_type == "Random":
            players[bot_name] = RandomBot(game.board, index, player_name)
        order.append(bot_name)
        index += 1
    random.shuffle(order)
    begin_play(game, order, players)
    continue_play(game, order, players)
