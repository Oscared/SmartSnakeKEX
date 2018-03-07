import snake, map, sys;
import time, select;
import pickle;
import numpy as np;

class Memory(object):

	def __init__(self, size):
		self.state_size = size;
		self.memory = list();

		self.stats = list();

	def writeToFile(self, file):
		with open(file, "wb") as f:
			pickle.dump(self.memory, f);
			f.close();


	def readFromFile(self, file):
		with open(file, "rb") as f:
			self.memory = pickle.load(f);
			f.close();


	def memoryAdd(self, state, action, reward, new_state, done):
		self.memory.append((state, action, reward, new_state, done));

	def statsAdd(self, score, length, steps):
		self.stats.append((score, length, steps));

	def writeScore(self, path):
		with open(path, "a+") as f:
			for score, length, steps in self.stats:
				f.write("{},{},{}\n".format(score, length, steps));
			f.close();



if __name__ == "__main__":

	size = (16,8,1);
	action_space = [snake.Snake.direction_up
		, snake.Snake.direction_left
		, snake.Snake.direction_right
		, snake.Snake.direction_down];

	environment = map.Map(size[0], size[1]);
	player = snake.Snake(environment);
	player.initPosition([size[0]//2+1, size[1]//2], [[size[0]//2, size[1]//2], [size[0]//2-1, size[1]//2]]);
	memory = Memory(size);
	memory.readFromFile("mem.pkl");

	print("Memory len: {}".format(len(memory.memory)));
	time.sleep(1);

	while True:

		environment.reset();
		player.reset();

		steps = 0;
		action = 2;

		state = environment.getState();
		state = np.reshape(state, [1
			, size[0]
			, size[1]
			, size[2]]);

		while player.isAlive():

			environment.render();
			i, o, e = select.select( [sys.stdin], [], [], 0.5)
			if (i):
				inp = sys.stdin.readline().strip();
				if(inp == 'w'):
					action = 0;
				elif(inp == 's'):
					action = 3;
				elif(inp == 'a'):
					action = 1;
				elif(inp == 'd'):
					action = 2;

			direction = action_space[action];
			reward = player.move(direction);

			done = not player.isAlive();
			if(done):
				reward = -10;

			if(reward == 0):
				reward = -0.05;

			environment.update();

			new_state = environment.getState();
			new_state = np.reshape(new_state, [1
			, size[0]
			, size[1]
			, size[2]]);

			memory.memoryAdd(state, action, reward, new_state, done);

			steps += 1;
			state = new_state;

		environment.render();
		memory.statsAdd(player.getScore(), player.getLength(), steps);

		print("Score {}p, {} steps".format(player.getScore(), steps));
		print("memory len: {}".format(len(memory.memory)));
		print("Play again? [y/N]");

		ans = input();
		if(ans.lower() == "y"):
			print("");
			continue;

		else:
			break;

	memory.writeToFile("mem.pkl");
	memory.writeScore("res.csv");
	print("Saved memory to mem.pkl");
