# Ultimate-Tic-Tac-Toe
An ultimate tic tac toe game. You can play with a random agent, AI agent (implemented with Monte Carlo Tree Search), or let them playing with each other.

## To run the program

Use the following command to run the program
```
python game.py [-h] [-m] [-n NUMBER_OF_GAMES] [-s BOARD_SIZE] player_1 player_2
```
positional arguments:  
  player_1              Agent of player 1. (random, human or MCTS)  
  player_2              Agent of player 2. (random, human or MCTS)  

optional arguments:  
  -h, --help            show this help message and exit  
  -m, --mute            Do not print board  
  -n NUMBER_OF_GAMES, --number_of_games NUMBER_OF_GAMES  
                        Number of games to play. Default 1.  
  -s BOARD_SIZE, --board_size BOARD_SIZE  
                        Board Size. Default 3.  

For example if you want to be player 1 and play against a MCTS agent
```
python game.py human MCTS
```

## AI Performance
I implemented the AI using Monte Carlo Tree Search.
Currently, without any improvements on the algorithm, when tested with 1000 games, it achieved a win rate of 95% against a random player,
with 2.1% draw and 2.9% loss.

## Sample Game Board and Result
```
(Skipped all 59 boards above)
************************
  Move 60 by Player 2
************************
------------------------
1|2|1 || 1|2|1 || 2|1|2
2|2|2 || _|1|2 || 2|_|_
_|1|2 || 1|_|_ || 2|_|1
------------------------
_|1|1 || _|2|2 || 2|_|1
1|1|_ || 2|1|2 || 2|_|1
1|2|_ || 2|_|2 || 2|_|_
------------------------
_|2|1 || 2|1|_ || 1|_|2
2|1|1 || 2|1|1 || 1|1|2
1|2|_ || _|1|1 || 2|1|2
------------------------
The winner is ...... Player 2!!!
Result of 1 game(s) random vs random
Win (Player 1):  0
Draw:  0
Loss:  1
```

## TO DO
1. Speed up the simulation using threads
2. Try out pygame to create a GUI