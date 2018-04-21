from map import Map;

class Snake(object):

	direction_up = 1;
	direction_left = 2;
	direction_right = 3;
	direction_down = 4;


	def __init__(self, _map):
		self.map = _map;
		self.isdead = False;

		self.score = 0;
		self.stepsSinceScoring = 0;

	def initPosition(self, position, tail):

		self.position = position;
		self.tail = tail;
		self.direction = Snake.direction_right;

		self.start_position = [list(position), list(tail)];

		self.reset();
		

	def reset(self):
		self.position = list(self.start_position[0]);
		self.tail = list(self.start_position[1]);

		for pos in self.tail:
			self.map.setTile(pos[0], pos[1], Map.tile_snake);
		self.map.setTile(self.position[0], self.position[1], Map.tile_snake_mouth);
		self.map.setTile(self.tail[-1][0], self.tail[-1][1], Map.tile_snake_tail);

		self.isdead = False;
		self.score = 0;
		self.stepsSinceScoring = 0;


	def move(self, direction):
		

		self.direction = direction;

		prev_pos = list(self.position);

		if(self.direction == Snake.direction_up):
			self.position[1] -= 1;
		elif(self.direction == Snake.direction_left):
			self.position[0] -= 1;
		elif(self.direction == Snake.direction_right):
			self.position[0] += 1;
		elif(self.direction == Snake.direction_down):
			self.position[1] += 1;

		tile = self.map.stepTo(self.position[0], self.position[1]);
		self.tail.insert(0,prev_pos);

		self.map.setTile(prev_pos[0], prev_pos[1], Map.tile_snake);

		self.stepsSinceScoring += 1;

		if (tile != Map.tile_apple and tile != Map.tile_golden_apple):
			end = self.tail.pop();
			tail = self.tail[-1];
			self.map.setTile(end[0], end[1], Map.tile_empty);
			self.map.setTile(tail[0], tail[1], Map.tile_snake_tail);
			self.stepsSinceScoring = 0;

		
		self.map.setTile(self.position[0], self.position[1], Map.tile_snake_mouth);


		if(tile == Map.tile_wall or tile == Map.tile_snake or tile == Map.tile_snake_tail):
			self.die();
		if(self.stepsSinceScoring > 40):
			self.die();

		s = 0;
		if(tile == Map.tile_apple):
			s = 1;
		if(tile == Map.tile_golden_apple):
			s = 5;

		self.score += s;
		return s;


	def die(self):
		self.isdead = True;


	def isAlive(self):
		return not self.isdead;

	def getLength(self):
		return len(self.tail)+1;

	def getScore(self):
		return self.score;