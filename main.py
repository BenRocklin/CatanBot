import sys

from play_game import play_game

player_types = ["Human", "Random", "RL", "OP"]

def main():
    # assign the below two to either "Human", "Random", "RL", or "OP"
    # note: RL will be for the reinforcement learning bot, OP will be for the online planning bot
    # red player will always be the first player for simplicity right now, this may change in the future
    # TODO: change the below to be command line args instead of explicit red/blue
    red_player = "Random"
    if red_player not in player_types:
        sys.exit("Improper player type for player red, exiting.")
    blue_player = "Random"
    if blue_player not in player_types:
        sys.exit("Improper player type for player red, exiting.")
    play_game([red_player, blue_player])

if __name__ == "__main__":
    main()