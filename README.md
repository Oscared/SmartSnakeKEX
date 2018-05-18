# SmartSnakeKEX
Bachelor Thesis 2018 Oscar Örnberg Jonas Nylund Royal Institute of Technology



*============================================================================================*
* INSTALLATION 

To run this code, a few libraries are required. 
* Keras: The Python Deep Learning library - https://keras.io/
* Numpy

Either one of 
* Tensorflow 
* Theano

To save and load model files
* H5py

Recommended but not required:
* Python noise module - https://github.com/caseman/noise

All of these except the latter can be installed through pip.
This code is targeted at python3, but seems to work in python2 aswell.


*============================================================================================*
* RUNNING AN AGENT

Main entry to the program is through the snake_agent.py file. This file accepts a number of command line arguments;

IO:
-m path/to/file : load an existing keras model including weights.
-o path/to/file : save a trained keras model including weights to a file. Overwrites the file if it exists.
-n path/to/file : combination of -m and -o; open a file and then save it to the same file after training.
-d : describe the network structure

Training:
-t : Train the network
-g (int) : Number of games to train on per epoch
-e (int) : Number of epochs to train
-v : verbose output
-r : record training progress to a csv file. The file is either placed next to the saved model if specified (-o), or to /record.csv
-i : use incremental map sixe for training.
-w (int) : use incremental map size for training, set initial width to this value.
-h (int) : use incremental map size for training, set initial height to this value.
-a path/to/file : Pretrain the agent on recorded data, as outputted from the data_input.py file (see below)

Playing:
-p : have the agent play a game
-s (int)/(string) : Seed the random number generator of the map, to play a particular map/game.
-b : benchmark the agents performance
-w (int) : set a reduced map size for playing (width)
-h (int) : set a reduced map size for playing (height)
-k : step through a played game. The environment will update on key_enter

Examples:
python3 snake_agent.py -m models/saved_model -o models/updated_model -g 1000 -e 10 -t -v -r -i
- open a saved model in "models/saved_model", train it for 10000 games in total over 10 epochs using an expanding environment and then save the trained network to "models/updated_model". Also save progress to a csv file.

python3 snake_agent.py -n models/updated_model -g 5000 -e 100 -t -v -r
- open "models/updated_model", train it for 500000 games over a 100 epochs, and then save the trained model to the same file. Also record progress.

python3 snake_agent.py -m models/updated_model -p
- Have the agent play a game and show the progress.

python3 snake_agent.py -m models/updated_model -b
- Benchmark the model


*============================================================================================*
* PLAYING THE GAME MANUALLY;

To play the game yourself, to get a feeling for it, run the data_input.py file. The interface might be the clunkiest ever, the controls being
w/a/s/d+enter.

The game is terminal based, and prints a single game state to the command line at once. If you have a large terminal open, this means you might have multiple states at once showing one after another.
Keep your eyes on the bottom most map, as it is the most recent. 
Steer the snake with w,a,s,d. But, you will also have to press enter after any of those keys. So w-enter-d-enter-s-enter will make a U-turn.
You will get used to it after a while.

Playing the game like this will also produce two outputfiles. One is a csv file of stats from your games. The other is a file containing the state-action pairs that you produces during the game. 
These can be used as input to the neural network to train it on human games befor letting it play itself, which might help reduce training time.


*============================================================================================*
* I ONLY WANT THE ENVIRONMENT

Of course, you can also just forego all of this and write your own code for training and testing the network, and only wants to use our environemnt.
If so, you only need the map.py and snake.py files. The map.py code relies on numpy arrays, so you still need numpy, and the noise module is still recommended but not required.

You will have to reverse engineer the useage a bit, but all the neccesary info should be in the Universe class in snake_agent.py.

But essentially;

environment = map.RestrictedMap(width, height);
environment.limitSize(w,h);
snake = snake.Snake(self.environment.getMap());
snake.initPosition([width//2+1, height//2], [[width//2, height//2]]);
environment.init();

To set it up, and then read _run. :)


