import numpy as np;
import matplotlib.pyplot as plt;

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
		self.epsilon = 0.1
		self.epsilon_min = 0.05;
		self.epsilon_decay = 0.9995;
		self.learning_rate = 0.005;
		self.step_reward = -0.02;

		self.times = [0,0,0,0];

	def modelSummary(self):
		self.model.summary();

	def setModel(self, model):
		self.model = model;

	def _createModel(self):
		self.model = keras.models.Sequential();
		self.model.add(keras.layers.Convolution2D(25, (3,3), padding='same', activation="relu", input_shape=self.state_size));
		self.model.add(keras.layers.Convolution2D(25, (3,3), padding='same', activation='relu'));
		self.model.add(keras.layers.AveragePooling2D(pool_size=(2,2)));
		self.model.add(keras.layers.Convolution2D(50, (3,3), padding='same', activation='relu'));
		self.model.add(keras.layers.Convolution2D(50, (3,3), padding='same', activation='relu'));
		self.model.add(keras.layers.AveragePooling2D(pool_size=(2,2)));

		self.model.add(keras.layers.Flatten());
		self.model.add(keras.layers.Dropout(0.1));
		self.model.add(keras.layers.Dense(100, activation="relu"));
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
			if(target == 0):
				target = self.step_reward;
			if not done:
				target += self.gamma * np.amax(self.model.predict(new_state)[0]);

			target_f = self.model.predict(state);
			target_f[0][action] = target;

			states[i] = state;
			targets[i] = target_f;
			i+=1;

		self.model.fit(states, targets, batch_size=32, epochs=1, verbose=0);
		
		if self.epsilon > self.epsilon_min:
			self.epsilon *= self.epsilon_decay


class Universe(object):

	action_space = [snake.Snake.direction_up
		, snake.Snake.direction_left
		, snake.Snake.direction_right
		, snake.Snake.direction_down];

	def __init__(self, map_size):

		self.best_benchmark = (0,0,0);

		self.batch_size = 32;
		self.map_size = map_size;
		self.state_size = (map_size[0], map_size[1], 1);
		self.min_step = 2;

		width = map_size[0];
		height = map_size[1];

		self.agent = Agent((width, height, 1), len(Universe.action_space));
		self.environment = map.RestrictedMap(map_size[0], map_size[1]);
		self.snake = snake.Snake(self.environment.getMap());

		self.snake.initPosition([width//2+1, height//2], [[width//2, height//2]]);
		self.environment.init();

	def setSize(self, width, height):
		w = width;
		h = height;

		if(w < 5):
			w = 5;
		if(h < 5):
			h = 5;
		if(w >= self.map_size[0]):
			w = self.map_size[0];
		if(h >= self.map_size[1]):
			h = self.map_size[1];

		self.environment.limitSize(w,h);
		self.snake = snake.Snake(self.environment.getMap());
		self.snake.initPosition([w//2+1, h//2], [[w//2, h//2]]);
		self.environment.init();

	def setModel(self, model):
		self.agent.setModel(model);

	def loadModel(self, path):
		self.agent.openModel(path);

	def saveModel(self, path):
		self.agent.saveModel(path);

	def createModel(self):
		self.agent._createModel();

	def trainOnExternalData(self, path, verbose=True):
		epsilon = self.agent.epsilon;

		l = 0;
		with open(path, "rb") as f:
			data = pickle.load(f);
			l = len(data);

			self.agent.memory = data;
			f.close();

		s = 128;
		x = (l//32)*4;
		g = int(np.log10(x))+1;
		if(s > l):
			s = l;
		if(verbose):
			sys.stdout.write("Training on external data:");
		for i in range(x):
			if(verbose):
				progressbar = "="*(20*i//x) + ">" + " "*(19-20*i//x);
				sys.stdout.write(("\rBatch {: "+str(g)+"d}/{:d} |{:s}| ").format(i+1, x, progressbar));

			self.agent.replay(s);
		self.agent.epsilon = epsilon;


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
				for j in range(2+steps//self.batch_size):
					self.agent.replay(self.batch_size);

			if(verbose):
				progressbar = "="*(20*i//games) + ">" + " "*(19-20*i//games);
				sys.stdout.write(("\rGame {: "+str(g)+"d}/{:d} |{:s}| {}p, {}steps ").format(i+1, games, progressbar, total_score, total_steps));

		sys.stdout.write("\rFinished {} games in {} seconds. Total score {}p in {} steps\n".format(games
			, round(time.time()-t)
			, total_score
			, total_steps));


	def play(self, render=True, step=False):
		score, steps, length = self._run(memorize=False, render=render, step=step);
		seed = self.environment.getSeed();
		oa = self.environment.getOpenArea();
		if(render):
			print("{} points with length {} in {} steps  (seed was {})".format(score, length, steps, seed));
		return (score, steps, length, oa);

	def benchmark(self, games, verbose=False):
		score = 0;
		steps = 0;
		length = 0;
		area = 0;
		g = int(np.log10(games))+1;
		for i in range(games):
			s, c, l, oa = self.play(render=False);
			score += s;
			steps += c;
			length += l;
			area += oa;
			if(verbose):
				progressbar = "="*(20*i//games) + ">" + " "*(19-20*i//games);
				sys.stdout.write(("\r{:"+str(g)+"d}/{:d} |{:s}| ").format(i+1, games, progressbar));

		if(verbose):
			sys.stdout.write("\r");

		return (score/games, steps/games, length/games, area/games);
		

	def plot(self):

		self.environment.saveState("test.state");
		

	def _run(self, memorize=True, render=False, step=False):

		self.environment.reset();
		self.snake.reset();
		self.environment.init();

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

			if(memorize):
				self.agent.memoryPut(state, action, reward, next_state, done);

			if(render):
				time.sleep(0.25);
				self.environment.render();
			if(step):
				print("Step [s]/plot [p]/exit [e]?");
				inp = input();
				if(inp == "s"):
					continue;
				elif(inp == "p"):
					self.plot();
				elif(inp == "e"):
					break;

			state = next_state;

		return (self.snake.getScore(), steps, self.snake.getLength());



if __name__ == "__main__":

	opts, args = getopt.getopt(sys.argv[1:], "m:n:o:g:e:a:s:w:h:kvptrdbi"
		, ["model=", "output=", "games=", "epochs=", "pretrain=", "seed=", "width=", "height=", "step", "play", "verbose", "train", "incremental", "describe", "record", "benchmark"]);

	size = [12, 8];
	mapsize = [6,5];
	limitsize = False;
	model = None;
	output = None;
	games = 500;
	epochs = 25;
	train = False;
	play = False;
	summarize = False;
	pretrain = None;
	verbose = False;
	record = False;
	benchmark = False;
	seed = None;
	step = False;

	for o, a in opts:
		if(o in ["-m", "--model"]):
			model = a;
		elif(o in ["-o", "--output"]):
			output = a;
		elif(o in ["-g", "--games"]):
			games = int(a);
		elif(o in ["-e", "--epochs"]):
			epochs = int(a);
		elif(o in ["-a", "--pretrain"]):
			pretrain = a;
		elif(o in ["-s", "--seed"]):
			seed = a;
		elif(o in ["-w", "--width"]):
			mapsize[0] = int(a);
			limitsize = True;
		elif(o in ["-h", "--height"]):
			mapsize[1] = int(a);
			limitsize = True;
		elif(o == "-n"):
			model = output = a;
		elif(o == "-p"):
			play = True;
		elif(o == "-t"):
			train = True;
		elif(o == "-d"):
			summarize = True;
		elif(o == "-v"):
			verbose = True;
		elif(o == "-r"):
			record = True;
		elif(o == "-b"):
			benchmark = True;
		elif(o == "-i"):
			limitsize = True;
		elif(o == "-k"):
			step = True;

	for a in args:
		if(a in ["-p","play"]):
			play = True;
		elif(a in ["-t", "train"]):
			train = True;
		elif(a in ["-d","describe"]):
			summarize = True;
		elif(a in ["-v", "verbose"]):
			verbose = True;
		elif(a in ["-r", "record"]):
			record = True;
		elif(a in ["-b", "benchmark"]):
			benchmark = True;
		elif(a in ["-i", "incremental"]):
			limitsize = True;
			

	universe = Universe(size);

	if(limitsize):
		universe.setSize(mapsize[0], mapsize[1]);
		print("Using incremental mapsize for training");
	else:
		mapsize = size;
		print("Using fixed mapsize for training");

	if(model != None):
		universe.loadModel(model);
	else:
		universe.createModel();

	if(summarize):
		universe.agent.modelSummary();

	if(pretrain != None):
		universe.trainOnExternalData(pretrain);

	if(train):
		start = time.time();
		for i in range(epochs):
			
			if(limitsize):
				print("Epoch {}, size: {}x{}".format(i+1, mapsize[0], mapsize[1]));
			else:
				print("Epoch " + str(i+1));
			
			universe.train(games, verbose=verbose);
			universe.agent.epsilon_min /= np.exp(np.log(20)/epochs);
			score, steps, length, area = universe.benchmark(games//10, verbose=verbose);
			
			if(games*i%5000 == 0):
				universe.agent.memory.clear();
			if(output != None):
				universe.saveModel(output);
			if(record):			
				print("Playing average: {}p in {} steps with length {}".format(score, steps, length));
				name = output;
				if(name == None):
					name = "record";
				name += ".csv";
				with open(name, "a+") as f:
					f.write("{},{},{},{},{},{}\n".format((i+1)*games, (time.time()-start)/3600, score, steps, length, mapsize[0]*mapsize[1]));
					f.close();

			if(limitsize and (length >= int((mapsize[0]-2)*(mapsize[1]-2)*0.8-2) or area-length < 6*(mapsize[0]*mapsize[1]/(size[0]*size[1])))):
				mapsize[0]+=1;
				mapsize[1]+=1;
				if(mapsize[0] > size[0]):
					mapsize[0] = size[0];
				if(mapsize[1] > size[1]):
					mapsize[1] = size[1];

				universe.setSize(mapsize[0], mapsize[1]);
				universe.agent.epsilon += 0.15;

	if(benchmark):
		print("Benchmarking...");
		score, steps, length, best = universe.benchmark(250, verbose);
		print("Playing average: {}p in {} steps with length {}".format(score, steps, length));


	if(play):
		if(seed != None):
			try:
				seed = int(seed);
			except ValueError:
				pass;
			universe.environment.setSeed(seed);
		while True:
			universe.play(step=step);
			print("Play again? [y/N]");
			if(input() != "y"):
				break;
		

	



	



