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
	tile_snake_tail = 4;
	tile_snake = 5;
	tile_snake_mouth = 6;
	

	tile_scaleing = 6;

	


	def __init__(self,width,height):

		self.random = random.Random();
		self.seed = None;
		self.isseeded = False;

		self.width = width;
		self.height = height;

		self.spawn_chance = 6 - (width+height)//10;
		if(self.spawn_chance < 1):
			self.spawn_chance = 1;
		self.despawn_time = (self.width+self.height)//3;

		self.array = numpy.zeros((self.width, self.height), dtype=numpy.int8);
		self.apples = 0;
		self.golden_apples = list();

		self.map_area = width*height;

	def setSeed(self, x):
		self.random.seed(x);
		self.seed = x;
		self.isseeded = True;

	def getSeed(self):
		return self.seed;

	def update(self):
		
		if(self.random.random() < 1/(self.spawn_chance+self.apples*2)):
			for i in range(10):
				if(self.spawnApple()):
					break;

		if(self.apples == 0):
			for i in range(10):
				if(self.spawnApple()):
					break;

		if(self.random.random() < 1/(self.spawn_chance*5+len(self.golden_apples)*5)):
			x = self.random.randint(1,self.width-1);
			y = self.random.randint(1,self.height-1);

			if(self.getTile(x,y) == Map.tile_empty):
				self.setTile(x,y,Map.tile_golden_apple);
				self.golden_apples.append([x,y,0]);

		remove = list();
		for apple in self.golden_apples:
			apple[2] += 1;
			if(apple[2] > self.despawn_time):
				if(self.random.random() < 0.33):
					remove.append(apple);
		for apple in remove:
			self.golden_apples.remove(apple);
			## Keep bug were snake despawns where it has picked up a
			## golden apple. But don't despawn the snake head.
			## Half fix - keeping bug as 'feature'
			if(self.getTile(apple[0],apple[1]) == Map.tile_golden_apple):
				self.setTile(apple[0],apple[1],Map.tile_empty);


	def getState(self):
		return self.array/Map.tile_scaleing;


	def generateMap(self):
		global perlin;
		if(self.isseeded):
			self.random.seed(self.seed);
		else:
			self.seed = random.randint(10000,1000000000000);
			self.random.seed(self.seed);
		self.isseeded = False;
		

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
					n = noise.pnoise2(x/self.width,y/self.height, base=self.random.randint(0,1023));
					if(n > 0.35):
						self.setTile(x,y,Map.tile_wall);
		else:
			for i in range(self.random.randint(4,10)):
				x = self.random.randint(1,self.width-1);
				y = self.random.randint(1,self.height-1);
				self.setTile(x,y, Map.tile_wall);

		## Add som apples
		for i in range(self.random.randint(4,10)):
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

		self.map_area = self.width*self.height;
		for x in range(self.width):
			for y in range(self.height):
				if(self.getTile(x,y) == Map.tile_wall):
					self.map_area -= 1;

		

	def spawnApple(self):
		x = self.random.randint(1,self.width-1);
		y = self.random.randint(1,self.height-1);

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

	def clear(self, size=None):

		"""
		for x in range(self.width):
			self.array[x][0] = Map.tile_wall;
			self.array[x][self.height-1] = Map.tile_wall;

		for y in range(self.height):
			self.array[0][y] = Map.tile_wall;
			self.array[self.width-1][y] = Map.tile_wall;
		"""
		w = self.width;
		h = self.height;
		if(size != None):
			w = size[0];
			h = size[1];

		for x in range(0,w):
			for y in range(0,h):
				self.setTile(x,y,Map.tile_empty);

	def overlay(self, other):
		self.clear((other.width, other.height));
		self.array[0:other.width, 0:other.height] = other.array;

	def saveState(self, path):
		with open(path, "a+") as file:
			for y in range(self.height):
				for x in range(self.width):
					file.write(str(self.getTile(x,y)/Map.tile_scaleing));
					file.write(",");
				file.write("\n");
			file.close();
		
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
		if(tile == Map.tile_snake_tail):
			return 'q';

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

	def getOpenArea(self):
		return self.map_area;




class RestrictedMap(object):


	def __init__(self, width, height):
		self.width = width;
		self.height = height;
		self.map = Map(width, height);

		self.blank = Map(width, height);
		self.blank.clear();

	def init(self):
		self.blank.overlay(self.map);

	def limitSize(self, width, height):
		self.map = Map(width, height);
		self.blank.clear();

	def reset(self):
		self.blank.clear();
		self.map.reset();
		self.blank.overlay(self.map);

	def update(self):
		self.map.update();
		self.blank.overlay(self.map);

	def getSeed(self):
		return self.map.getSeed();

	def setSeed(self, seed):
		self.map.setSeed(seed);

	def getOpenArea(self):
		return self.map.getOpenArea();

	def render(self):
		self.blank.render();

	def saveState(self, path):
		self.map.saveState(path);

	def getState(self):
		return self.blank.getState();

	def getMap(self):
		return self.map;




