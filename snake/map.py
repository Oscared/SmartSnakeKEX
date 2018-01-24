import noise, random;

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

		self.spawn_chance = 0.1;
		self.despawntime = (self.width+self.height)//3;

		self.array = list();
		self.golden_apples = list();

		for i in range(height):
			self.array.append(list());
			for j in range(width):
				self.array[i].append(Map.tile_empty);

	def update(self):
		
		if(random.random() < self.spawn_chance):
			for i in range(10):
				x = random.randint(1,self.width-1);
				y = random.randint(1,self.height-1);

				if(self.getTile(x,y) == Map.tile_empty):
					self.setTile(x,y,Map.tile_apple);
					break;

		if(random.random() < self.spawn_chance/5):
			x = random.randint(1,self.width-1);
			y = random.randint(1,self.height-1);

			if(self.getTile(x,y) == Map.tile_empty):
				self.setTile(x,y,Map.tile_golden_apple);
				self.golden_apples.append([x,y,0]);

		remove = list();
		for apple in self.golden_apples:
			apple[2] += 1;
			if(apple[2] > self.despawntime):
				if(random.random() < 0.33):
					remove.append(apple);
		for apple in remove:
			self.golden_apples.remove(apple);
			self.setTile(apple[0],apple[1],Map.tile_empty);


	def generateMap(self):

		## Add walls to the border of the map
		for x in range(self.width):
			self.array[0][x] = Map.tile_wall;
			self.array[self.height-1][x] = Map.tile_wall;

		for y in range(self.height):
			self.array[y][0] = Map.tile_wall;
			self.array[y][self.width-1] = Map.tile_wall;


		## Perlin noise generated random walls in the middle of the map
		for x in range(1,self.width-1):
			for y in range(1,self.height-1):
				n = noise.pnoise2(x/self.width,y/self.height, base=random.randint(0,1023));
				if(n > 0.35):
					self.setTile(x,y,Map.tile_wall);

		x1 = self.width//2-5;
		x2 = self.width//2+5;

		## Add som apples
		for i in range(random.randint(4,10)):
			x = random.randint(1,self.width-1);
			y = random.randint(1,self.height-1);

			if(self.getTile(x,y) == Map.tile_empty):
				self.setTile(x,y, Map.tile_apple);


		## Clear the center 10x10 tiles from obstacles
		if(x1 < 1 or x2 > self.width-1):
			x1 = 1;
			x2 = self.width-1;

		y1 = self.height//2-5;
		y2 = self.height//2+5;

		if(y1 < 1 or y2 > self.height-1):
			y1 = 1;
			y2 = self.height-1;

		for x in range(x1,x2):
			for y in range(y1,y2):
				self.setTile(x,y,Map.tile_empty);

		"""
		## Add in the snake
		for x in range(x1+3, x1+6):
			self.setTile(x,y1+5,Map.tile_snake);
		self.setTile(x1+6,y1+5, Map.tile_snake_mouth);
		"""

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
		self.array[y][x] = type;

	def getTile(self, x,y):
		return self.array[y][x];