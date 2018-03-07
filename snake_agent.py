import numpy as np

import keras
from collections import deque
import sys, getopt, time, pickle
import snake, map, random
keras.backend.set_image_dim_ordering('tf');


"""
Requires perlin noise package from https://github.com/caseman/noise
Download and install via "python setup.py install"

"""



class Agent(object):

	def __init__(self, state_size, action_size):
		self.state_size = state_size;
		self.action_size = action_size;

		self.memory = list();
		self.gamma = 0.95;
		self.epsilon = 1.0
		self.epsilon_min = 0.05;
		self.epsilon_decay = 0.9995;
		self.learning_rate = 0.001;

		self.times = [0,0,0,0];

	def modelSummary(self):
		self.model.summary();

	def setModel(self, model):
		self.model = model;

	def _createModel(self):
		self.model = keras.models.Sequential();
		self.model.add(keras.layers.Convolution2D(24, (3,3), padding='same', activation="relu", input_shape=self.state_size));
		self.model.add(keras.layers.Convolution2D(24, (3,3), padding='same', activation='relu'));
		self.model.add(keras.layers.AveragePooling2D(pool_size=(2,2)));
		self.model.add(keras.layers.Convolution2D(48, (3,3), padding='same', activation='relu'));
		self.model.add(keras.layers.Convolution2D(48, (3,3), padding='same', activation='relu'));

		self.model.add(keras.layers.Flatten());
		self.model.add(keras.layers.Dense(64, activation="relu"));
		self.model.add(keras.layers.Dropout(0.25));
		self.model.add(keras.layers.Dense(self.action_size, activation="linear"));

		self.model.compile(loss="mse", optimizer=keras.optimizers.Adam(lr=self.learning_rate));

	def openModel(self,path):
		self.model = keras.models.load_model(path);

	def saveModel(self, path):
		self.model.save(path);

	def memoryPut(self, state, action, reward, new_state, done):
		self.memory.append((state, action, reward, new_state, done));

	def nextAction(self, state, explore=True):
		if(explore and np.random.rand() < self.epsilon):
			return np.random.randint(self.action_size);

		act_values = self.model.predict(state);
		i = np.argmax(act_values[0]);
		return i;

	def replay(self, size):
		batch = random.sample(self.memory, size);

		states = np.zeros((size, self.state_size[0], self.state_size[1], self.state_size[2]));
		targets = np.zeros((size, 4));
		i = 0;
		for state, action, target, new_state, done in batch:
			if not done:
				target += self.gamma * np.amax(self.model.predict(new_state)[0]);

			target_f = self.model.predict(state);
			target_f[0][action] = target;

			states[i] = state;
			targets[i] = target_f;
			i+=1;
			# self.model.fit(state, target_f, epochs=1, verbose=0)
			# fit_time = time.time()-t-predict_time;
			# self.times[2] += fit_time;

		self.model.fit(states, targets, batch_size=32, epochs=1, verbose=0);
		
		if self.epsilon > self.epsilon_min:
			self.epsilon *= self.epsilon_decay


class Universe(object):

	action_space = [snake.Snake.direction_up
		, snake.Snake.direction_left
		, snake.Snake.direction_right
		, snake.Snake.direction_down];

	def __init__(self, map_size):

		self.batch_size = 32;
		self.state_size = (map_size[0], map_size[1], 1);

		width = map_size[0];
		height = map_size[1];

		self.agent = Agent((width, height, 1), len(Universe.action_space));
		self.environment = map.Map(map_size[0], map_size[1]);
		self.snake = snake.Snake(self.environment);

		self.environment.generateMap();
		self.snake.initPosition([width//2+1, height//2], [[width//2, height//2], [width//2-1, height//2]]);

	def setModel(self, model):
		self.agent.setModel(model);

	def loadModel(self, path):
		self.agent.openModel(path);

	def saveModel(self, path):
		self.agent.saveModel(path);

	def createModel(self):
		self.agent._createModel();

	def trainOnExternalData(self, path, verbose=True):
		l = 0;
		with open(path, "rb") as f:
			data = pickle.load(f);
			l = len(data);

			self.agent.memory = data;
			f.close();

		s = 128;
		x = (l//32)*5;
		g = int(np.log10(x))+1;
		if(s > l):
			s = l;
		if(verbose):
			print("Training on external data:");
		for i in range(x):
			if(verbose):
				progressbar = "="*(20*i//x) + ">" + " "*(19-20*i//x);
				sys.stdout.write(("\rBatch {: "+str(g)+"d}/{:d} |{:s}| ").format(i+1, x, progressbar));

			self.agent.replay(s);

		if(verbose):
			print("");


	def train(self, games, verbose=True):
		t = time.time();
		total_score = 0;
		total_steps = 0;
		g = int(np.log10(games))+1;

		for i in range(games):
			score, steps, length = self._run(memorize=True, render=False);
			total_score += score;
			total_steps += steps;
			if(len(self.agent.memory) > self.batch_size):
				self.agent.replay(self.batch_size);

			if(verbose):
				progressbar = "="*(20*i//games) + ">" + " "*(19-20*i//games);
				sys.stdout.write(("\rGame {: "+str(g)+"d}/{:d} |{:s}| {}p, {}steps ").format(i+1, games, progressbar, total_score, total_steps));

		sys.stdout.write("\rFinished {} games in {} seconds. Total score {}p in {} steps\n".format(games
			, round(time.time()-t)
			, total_score
			, total_steps));


	def play(self, render=True):
		score, steps, length = self._run(memorize=False, render=render);
		if(render):
			print("{} points in {} steps".format(score, steps));
		return (score, steps, length);

	def benchmark(self, games, verbose=False):
		score = 0;
		steps = 0;
		length = 0;
		
		for i in range(games):
			s, c, l = self.play(render=False);
			score += s;
			steps += c;
			length += l;
		return (score/games, steps/games, length/games);
		


	def _run(self, memorize=True, render=False):

		self.environment.reset();
		self.snake.reset();

		if(render):
			self.environment.render();

		state = self.environment.getState();
		state = np.reshape(state, [1
			, self.state_size[0]
			, self.state_size[1]
			, self.state_size[2]]);

		steps = 0;
		while self.snake.isAlive():

			steps += 1;
			action = self.agent.nextAction(state, explore=memorize);
			direction = Universe.action_space[action];

			reward = self.snake.move(direction);
			self.environment.update();

			next_state = self.environment.getState();
			next_state = np.reshape(next_state, [1
				, self.state_size[0]
				, self.state_size[1]
				, self.state_size[2]]);

			done = not self.snake.isAlive();
			if(done):
				reward = -5;

			if(reward == 0):
				reward = -0.1;

			if(memorize):
				self.agent.memoryPut(state, action, reward, next_state, done);

			if(render):
				time.sleep(0.25);
				self.environment.render();

			state = next_state;

		return (self.snake.getScore(), steps, self.snake.getLength());



if __name__ == "__main__":

	opts, args = getopt.getopt(sys.argv[1:], "m:n:o:g:d:e:vptsrb"
		, ["model=", "output=", "games=", "epochs=", "pretrain=" "play", "verbose", "train", "summarize", "record", "benchmark"]);

	size = (16, 8);
	model = None;
	output = None;
	games = 250;
	epochs = 1;
	train = False;
	play = False;
	summarize = False;
	pretrain = None;
	verbose = False;
	record = False;
	benchmark = False;

	for o, a in opts:
		if(o in ["-m", "--model"]):
			model = a;
		elif(o in ["-o", "--output"]):
			output = a;
		elif(o in ["-g", "--games"]):
			games = int(a);
		elif(o in ["-e", "--epochs"]):
			epochs = int(a);
		elif(o in ["-d", "--pretrain"]):
			pretrain = a;
		elif(o == "-n"):
			model = output = a;
		elif(o == "-p"):
			play = True;
		elif(o == "-t"):
			train = True;
		elif(o == "-s"):
			summarize = True;
		elif(o == "-v"):
			verbose = True;
		elif(o == "-r"):
			record = True;
		elif(o == "-b"):
			benchmark = True;

	for a in args:
		if(a in ["-p","play"]):
			play = True;
		elif(a in ["-t", "train"]):
			train = True;
		elif(a in ["-s","summarize"]):
			summarize = True;
		elif(a in ["-v", "verbose"]):
			verbose = True;
		elif(a in ["-r", "record"]):
			record = True;
		elif(a in ["-b", "benchmark"]):
			benchmark = True;
			

	universe = Universe(size);

	if(model != None):
		universe.loadModel(model);
	else:
		universe.createModel();

	if(summarize):
		universe.agent.modelSummary();

	if(pretrain != None):
		universe.trainOnExternalData(pretrain);

	if(train):
		for i in range(epochs):
			print("Epoch " + str(i+1));
			universe.train(games, verbose=verbose);
			universe.agent.memory.clear();
			universe.agent.epsilon += 0.1;
			universe.agent.epsilon_min /= np.exp(np.log(10)/epochs);
			if(output != None):
				universe.saveModel(output);
			if(record):
				score, steps, length = universe.benchmark(100);				
				print("Playing average: {}p in {} steps with length {}".format(score, steps, length));
				name = output;
				if(name == None):
					name = "record";
				name += ".csv";
				with open(name, "a+") as f:
					f.write("{},{},{},{}\n".format((i+1)*games, score, steps, length));
					f.close();

	if(benchmark):
		print("Benchmarking...");
		score, steps, length = universe.benchmark(100);
		print("Playing average: {}p in {} steps with length {}".format(score, steps, length));


	if(play):
		universe.play();

	



	



