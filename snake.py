import pygame, random ,sys
from pygame.locals import *

def collide(x1, x2, y1, w1, w2, h1, h2):
if x1+w1>x2 and x1<x2+w2 and y1+h1>y2 and y1<y2+h2 :
    return True
else :
    return False
    def die (screen, score):
        f=pygame.font.SysFont('Arial', 30)
        t=f.render('Your score was: '+str(score), True, (0, 0, 0))
        screen.blit(t, (10,270))
        pygame.time.wait(2000)
        sys.exit(0)

        APPLE_SIZE = 10
        SEGMENT_SIZE = 20
        INITIAL_SNAKE_LENGTH = 5

        class Dir:
            DOWN = 0
            UP = 1
            RIGHT = 2
            LEFT = 3

            @staticmethod
            def to_P2(direction):
                return {Dir.DOWN: P2(0, 1),
                Dir.UP: P2(0, -1),
                Dir.RIGHT: P2(1, 0),
                Dir.LEFT: P2(-1, 0),
                }[direction]


                class P2(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __add__(self, other):
        return P2(self.x + other.x, self.y + other.y)
    def __sub__(self, other):
        return P2(self.x - other.x, self.y - other.y)
    def __mul__(self, factor):
        return P2(self.x*factor, self.y*factor)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __str__(self):
        return "P2(%s,%s)" % (self.x, self.y)

class MyRect(object):
    def __init__(self, upperleft, size):
        self.upperleft = uppperleft
        self.size = size

    def contains(self, p):
        return p.x >= self.upperleft.x \
           and p.y >= self.upperleft.y \
           and p.x < self.upperleft.x + self.size.x \
           and p.y < self.upperleft.y + self.size.y

    def collides_with(self, other):
        print "TODO"
        return False


class Snake(object):
    def __init__(self, headpos, length, direction):
        self.to_grow = 0
        self.grow_speed = 1
        self.direction = direction
        taildir = Dir.to_P2(direction) * (-SEGMENT_SIZE)
        segments = []
        pos = headpos
        for i in range(length):
            segments.append(pos)
            pos += taildir
        self.segments = segments
        self.slow_factor = 1
        self.wait_cycles = 1
        print "Created " + self.dump()

    def length(self):
        return len(self.segments)

    def dump(self):
        o = []
        o.append("Snake(len=%d)" % self.length())
        for s in self.segments: o.append("(%d,%d)" % (s.x, s.y))
        return "".join(o)

class Player(object):
    def __init__(self, name, controls):
        self.name = name
        self.score = 0
        self.snake = None
        self.controls = controls

arrowKeys = {Dir.UP: K_UP, Dir.DOWN: K_DOWN, Dir.LEFT: K_LEFT, Dir.RIGHT: K_RIGHT}
asdfKeys =  {Dir.UP: K_s, Dir.DOWN: K_d, Dir.LEFT: K_a, Dir.RIGHT: K_f}
players = [Player("Spieler1", arrowKeys), Player("Spieler2", asdfKeys)]

for pnum, player in enumerate(players):
    headpos = P2(290,290) + P2(2*pnum*SEGMENT_SIZE, 0)
    direction = [Dir.UP, Dir.DOWN][pnum%2]
    player.snake = Snake(headpos, INITIAL_SNAKE_LENGTH, direction)

players[1].snake.slow_factor = 8 # only for testing purposes

applepos = P2(random.randint(0, 590), random.randint(0, 590))
pygame.init()
s=pygame.display.set_mode((600, 600))
pygame.display.set_caption('Schlange')
appleimage = pygame.Surface((APPLE_SIZE, APPLE_SIZE))
appleimage.fill((0, 255, 0))
images = []
for color in [(255,0,0), (0,255,0), (0,0,255)]: # red, green and blue
    img = pygame.Surface((SEGMENT_SIZE, SEGMENT_SIZE))
    img.fill(color)
    images.append(img)
font = pygame.font.SysFont('Arial', 20)
clock = pygame.time.Clock()
while True:
    clock.tick(10)
    # Handle Keyboard events
    for e in pygame.event.get():
        if e.type == QUIT:
            sys.exit(0)
        elif e.type == KEYDOWN:
            for player in players:
                snake = player.snake
                controls = player.controls
                if e.key == controls[Dir.UP] and snake.direction != Dir.DOWN: snake.direction = Dir.UP
                elif e.key == controls[Dir.DOWN] and snake.direction != Dir.UP: snake.direction = Dir.DOWN
                elif e.key == controls[Dir.LEFT] and snake.direction != Dir.RIGHT: snake.direction = Dir.LEFT
                elif e.key == controls[Dir.RIGHT] and snake.direction != Dir.LEFT: snake.direction = Dir.RIGHT

    for player in players:
        snake = player.snake
        head = snake.segments[0]
        # Test for collisions with other snakes
        for other_player in players:
            other_snake = other_player.snake
            for segment in other_snake.segments:
                # use plain == instead of collide (should be good enough)
                # collision = collide(head.x, segment.x, head.y, segment.y, SEGMENT_SIZE, SEGMENT_SIZE, SEGMENT_SIZE, SEGMENT_SIZE)
                collision = (segment == head)
                if collision and not (segment is head): # ignore own head
                    print "%s runs into %s" % (player.name, other_player.name)
                    print "%s head @ %s, %s segment @ %s" % (player.name, head, other_player.name, segment)
                    die(s, player.score)

        # Test for collision with apple
        if collide(head.x, applepos.x, head.y, applepos.y, SEGMENT_SIZE, APPLE_SIZE, SEGMENT_SIZE, APPLE_SIZE):
            print "%s eats apple @ %s" % (player.name, applepos)
            player.score += 1
            snake.to_grow += 1
            applepos=P2(random.randint(0,590),random.randint(0,590))

        # Test for collision with border
        if head.x < 0 or head.x > 580 or head.y < 0 or head.y > 580:
            print "%s runs into border." % player.name
            die(s, player.score)

    # Now move all the snakes (and let them grow perhaps)
    for player in players:
        snake = player.snake
        snake.wait_cycles -= 1
        if snake.wait_cycles > 0:
            continue # do not move this snake this time
        snake.wait_cycles = snake.slow_factor
        # We dont change the positions of all segments.
        # Instead, we insert a new segment at the beginning
        # (as the new head) and remove the last element
        # (the tail) unless the snake is growing.

        d = Dir.to_P2(snake.direction) * SEGMENT_SIZE
        old_head = snake.segments[0]
        new_head = old_head + d
        #print player.name, "d=", d, "new_head=", new_head
        snake.segments.insert(0, new_head)
        if snake.to_grow > 0 and True:
            snake.to_grow -= 1
        else:
            snake.segments.pop() # remove last segment

    # Draw the new scene
    s.fill((0, 0, 0))
    for plnum, player in enumerate(players):
        img = images[plnum]
        snake = player.snake
        for segment in snake.segments:
            s.blit(img, (segment.x, segment.y))
        txt = font.render("%s: %s" % (player.name, player.score), True, (255, 255, 0))
        s.blit(txt, (10 + 400*(plnum%2), 10+(400*int(plnum/2)%2)))
    s.blit(appleimage, (applepos.x, applepos.y))
    pygame.display.update()
    #print players[0].snake.dump()
