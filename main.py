from play_game import play_game

def main():
	# Trying to make two random bots play against each other
    num_players = 0 # <-- number of human players
    bots = ["Random", "Random2"] # <-- bot types (Random)
    play_game(num_players, bots)

if __name__ == "__main__":
    main()