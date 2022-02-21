# Build an AI for the Kalah

## The game
Kalah is a 2-player board game that has relatively simple rules:

The board consists of n pits for each player. These pits are divided into n-1 houses, that are located on the side of each player and 1 store to the right side of each player. At the start, all houses contain m seeds. The goal is to direct more seeds into your store than your opponent.  
The seeds are distributed in the following manner: the active player chooses one of his non-empty houses, takes all its seeds and places them seed-by-seed in a clockwise manner into the subsequent pits. Only the opponent’s store is skipped in this process.
2 special rules exist:
-	If the last seed falls into one of the active player’s empty houses, the seeds in the opponent’s house directly across are captured. Those seeds along with the active player’s last seed are moved into the active player’s store.
-	If the last seed falls into the active player’s store, the player is allowed to do an extra-move.
The game ends when after a move all houses of a player are empty. In that case, the other player moves all remaining seeds from his houses to his store.

## The AI
As is the case with basically any board game, computers can be made to play Kalah extremely well. One method that is at the heart of many AIs tasked with winning board games is Monte Carlo Tree Search (MCTS). Most notably, MCTS is used in AlphaGo – the famous computer program that a couple of years ago defeated the best humans in the board game Go, which previously had been one of the last games that humans still had the upper hand.
Roughly sketched, MCTS works as follows: It traverses the tree of game states up to a limited depth and estimates the winningness of these states, e.g., by simulating randomly to a terminal game state. In its traversal MCTS balances two goals: exploitation (preferably visiting game states that appear promising) and exploration (preferably visiting game states that have not been looked at much). For a complete description of MCTS, see e.g., [here](https://medium.com/@quasimik/monte-carlo-tree-search-applied-to-letterpress-34f41c86e238).
The implementation here mostly adheres to the basic algorithm (with the biggest tweak being that states corresponding to moves that provide extra moves are preferably expanded in the game tree to account for the fact that in Kalah stringing large chains of extra moves together is a successful strategy).

## Play
Running `play.py` opens a start screen window where you can start a game of Kalah with your prefered configuration. Play against a friend or feel free to test if you can beat the AI!


## Repository Content
The code is structured into three files: 
- `play.py` is concerned with the GUI, which is built with Python’s tkinter module. 
-	`mcts.py` conducts Monte Carlo Tree Search to determine the AI's choice
-	`utils.py` contains several utility functions
-	the `images` folder contains 31 images – depicting houses with 0 to 30 seeds – that are used for the GUI. 
