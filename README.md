# Ultimate-Tic-Tac-Toe
An ultimate tic tac toe game. You can play with a random agent, AI agent (implemented with Monte Carlo Tree Search), or let them play with each other.
This program also supports board sizes other than 3, you can set the board size when you run the program.

## To run the program

Use the following command to run the program:
```
python game.py [-h] [-m] [-n NUMBER_OF_GAMES] [-b BOARD_SIZE] [-s NUMBER_OF_SIMULATIONS] [-t TIME_LIMIT] player_1 player_2
```
player_1 and player_2 are one of the followings: random, human and mcts, mcrave, hmcrave (super slow), and mctss (currently the strongest AI).

For example if you want to be player 1 and play against a MCTS agent,
```
python game.py human mcts
```

For all the MCTS player, you can set the number of simulations per move, and time limit per move.
It will run the given number of simulations per move unless the time limit is reached.
The default number of simulations per move is 100, and the default time limit is None.

## AI Performance
I implemented the AI using Monte Carlo Tree Search.   
MCTS Player:  
Using 100 iterations per move, the AI wins 99 games out of 100, with 1 draw, against a random agent.  
Using 1000 iterations per move, the AI wins all 100 games against a random agent.  
Using 10000 iterations per move, the AI can beat me sometimes.  
  
Trying to improve the AI, I implemented a UCT MC-RAVE player.
It's performance is similar to pure MCTS, maybe even a bit worse than pure MCTS. One possible reason could be the small relation between moves encoutered in rollout, and the same move as a sibling. This is due to the nature of the game, where legal moves jump from sub-boards to sub-boards. 
Another possible reason is the exploration weight in UCB1 and the arbitrary constant in Beta are not perfectly fine tuned.  

I also implemented a heuristic version of UCT MC-RAVE. The win rate against pure MCTS does improve, but the agent becomes too slow.

Result of 100 game(s) hmcrave vs mcts  
Played as both players for 50 times each
Number of simulations per move:  1000  
Win (Player 1):  57  
Draw:  11  
Loss:  32  

After that, I implemented the MCTS Solver described by M. H. M. Winands, Y. Bjo ̈rnsson, and J.-T. Saito in their paper “Monte-Carlo Tree Search Solver”. The result is promising:
Result of 100 game(s) mctss vs mcts  
Played as both player for 50 games  
Number of simulations per move:  1000  
Win (Player 1):  48  
Draw:  25  
Loss:  27  

In the next step, I am going to try out neural networks for futher improvements.

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
1. Neural Networks
2. Keep simulating when opponent is making move(?)
3. Try to make it run faster
4. Try out pygame to create a GUI
