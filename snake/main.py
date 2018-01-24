import map, snake, time;
import sys, select;

width = 25;
height = 23;
environment = map.Map(width,height);
environment.generateMap();

player = snake.Snake(environment);
player.initPosition([width//2+2,height//2], [[width//2+1,height//2],[width//2,height//2],[width//2-1,height//2]]);

environment.render();
score = 0;
direction = snake.Snake.direction_right;

while player.isAlive():
	tile = player.move(direction);

	if(tile == map.Map.tile_apple):
		score += 1;
	if(tile == map.Map.tile_golden_apple):
		score += 10;

	environment.update();
	environment.render();

	i, o, e = select.select( [sys.stdin], [], [], 0.5)
	if (i):
		inp = sys.stdin.readline().strip();
		if(inp == 'w'):
			direction = snake.Snake.direction_up;
		elif(inp == 's'):
			direction = snake.Snake.direction_down;
		elif(inp == 'a'):
			direction = snake.Snake.direction_left;
		elif(inp == 'd'):
			direction = snake.Snake.direction_right;
		
print("Score: " + str(score));
print("Length: " + str(player.getLength()));