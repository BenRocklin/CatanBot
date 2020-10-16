# CatanBot

### Repository Setup
1. Clone the repository via `git clone`.
2. Install virtualenv via `pip3 install virtualenv`.
3. Navigate to the root directory in Terminal.
4. Create a new virtual environment via running `python3 -m venv catanEnv` in Terminal.
   4. If you receive a warning during this step, simply run the command that the warning suggests and try this again.
5. Activate the virtual environment via `source catanEnv/bin/activate`.
6. From the repository root, install every package needed by running `pip3 install -r requirements.txt`.
7. Run `python3 main.py` to run a game of Catan with 2 players.
8. When finished running commands, run `deactivate` to stop using the virtual environment. Be sure to reactivate the
virtual environment per the instructions given above when you choose to run another round of Catan.