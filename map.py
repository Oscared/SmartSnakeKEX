import random, numpy;
try:
	import noise;
	perlin = True;
	print("Using perlin noise for in-map walls");
except ImportError:
	perlin = False;
	print("Noise module not found. Falling back to random in-map wall placements");

class Map(object):

	tile_empty = 0;
	tile_wall = 1;
	tile_apple = 2;
	tile_golden_apple = 3;
	tile_snake = 4;
	tile_snake_mouth = 5;


	def __init__(self,width,height):

		self.width = width;
		self.height = height;

		self.spawn_chance = 6 - (width+height)//10;
		if(self.spawn_chance < 1):
			self.spawn_chance = 1;
		self.despawn_time = (self.width+self.height)//3;

		self.array = numpy.zeros((self.width, self.height), dtype=numpy.int8);
		self.apples = 0;
		self.golden_apples = list();


	def update(self):
		
		if(random.random() < 1/(self.spawn_chance+self.apples*2)):
			for i in range(10):
				if(self.spawnApple()):
					break;

		if(self.apples == 0):
			for i in range(10):
				if(self.spawnApple()):
					break;

		if(random.random() < 1/(self.spawn_chance*5+len(self.golden_apples)*5)):
			x = random.randint(1,self.width-1);
			y = random.randint(1,self.height-1);

			if(self.getTile(x,y) == Map.tile_empty):
				self.setTile(x,y,Map.tile_golden_apple);
				self.golden_apples.append([x,y,0]);

		remove = list();
		for apple in self.golden_apples:
			apple[2] += 1;
			if(apple[2] > self.despawn_time):
				if(random.random() < 0.33):
					remove.append(apple);
		for apple in remove:
			self.golden_apples.remove(apple);
			## Keep bug were snake despawns where it has picked up a
			## golden apple. But don't despawn the snake head.
			## Half fix - keeping bug as 'feature'
			if(self.getTile(apple[0],apple[1]) == Map.tile_snake_mouth):
				continue;
			self.setTile(apple[0],apple[1],Map.tile_empty);


	def getState(self):
		return self.array/5;


	def generateMap(self):


		## Add walls to the border of the map
		for x in range(self.width):
			self.array[x][0] = Map.tile_wall;
			self.array[x][self.height-1] = Map.tile_wall;

		for y in range(self.height):
			self.array[0][y] = Map.tile_wall;
			self.array[self.width-1][y] = Map.tile_wall;


		## Perlin noise (if available) generated random walls in the middle of the map
		if(perlin):
			for x in range(1,self.width-1):
				for y in range(1,self.height-1):
					n = noise.pnoise2(x/self.width,y/self.height, base=random.randint(0,1023));
					if(n > 0.35):
						self.setTile(x,y,Map.tile_wall);
		else:
			for i in range(random.randint(4,10)):
				x = random.randint(1,self.width-1);
				y = random.randint(1,self.height-1);
				self.setTile(x,y, Map.tile_wall);

		## Add som apples
		for i in range(random.randint(4,10)):
			self.spawnApple();


		## Clear the center 6x6 tiles from obstacles
		x1 = self.width//2-2;
		x2 = self.width//2+2;

		if(x1 < 1 or x2 > self.width-1):
			x1 = 1;
			x2 = self.width-1;

		y1 = self.height//2-1;
		y2 = self.height//2+1;

		if(y1 < 1 or y2 > self.height-1):
			y1 = 1;
			y2 = self.height-1;

		for x in range(x1,x2):
			for y in range(y1,y2):
				if(self.getTile(x,y) == Map.tile_apple):
					self.apples -= 1;
				self.setTile(x,y,Map.tile_empty);

		"""
		## Add in the snake
		for x in range(x1+3, x1+6):
			self.setTile(x,y1+5,Map.tile_snake);
		self.setTile(x1+6,y1+5, Map.tile_snake_mouth);
		"""

	def spawnApple(self):
		x = random.randint(1,self.width-1);
		y = random.randint(1,self.height-1);

		if(self.getTile(x,y) == Map.tile_empty):
			self.setTile(x,y, Map.tile_apple);
			self.apples += 1;
			return True;
		return False;

	def reset(self):
		self.array = numpy.zeros((self.width, self.height), dtype=numpy.int8);
		self.apples = 0;
		self.golden_apples = list();
		self.generateMap();
		
	def render(self):
		for y in range(self.height):
			line = "";
			for x in range(self.width):
				line += self.renderTile(x,y);
			print(line);

	def renderTile(self, x,y):
		tile = self.getTile(x,y);

		if(tile == Map.tile_empty):
			return ' ';
		if(tile == Map.tile_wall):
			return '#';
		if(tile == Map.tile_apple):
			return '+';
		if(tile == Map.tile_golden_apple):
			return '*';
		if(tile == Map.tile_snake):
			return 'o';
		if(tile == Map.tile_snake_mouth):
			return 'O';

		return ' ';

	def setTile(self, x,y, type):
		self.array[x][y] = type;

	def getTile(self, x,y):
		return self.array[x][y];

	def stepTo(self, x,y):
		tile = self.getTile(x,y);
		if(tile != Map.tile_empty):
			if(tile == Map.tile_apple):
				self.apples -= 1;
			if(tile == Map.tile_golden_apple):
				pass # Fix bug width despawning snake after eating golden apple here

		return tile;
