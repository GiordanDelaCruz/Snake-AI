import pygame
import random
from enum import Enum
from collections import namedtuple
import numpy as np

pygame.init()
font = pygame.font.Font('arial.ttf', 25)
#font = pygame.font.SysFont('arial', 25)

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

Point = namedtuple('Point', 'x, y')

# rgb colors
WHITE = (255, 255, 255)
RED = (200,0,0)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
BLACK = (0,0,0)

BLOCK_SIZE = 20
SPEED = 400 # Original speed = 40

class SnakeGameAI:

    def __init__(self, w=640, h=480):
        self.w = w
        self.h = h
        # init display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Snake')
        self.clock = pygame.time.Clock()
        self.reset()


    def reset(self):
        # init game state
        self.direction = Direction.RIGHT

        self.head = Point(self.w/2, self.h/2)
        self.snake = [self.head,
                      Point(self.head.x-BLOCK_SIZE, self.head.y),
                      Point(self.head.x-(2*BLOCK_SIZE), self.head.y)]

        self.score = 0
        self.food = None
        self._place_food()
        self.frame_iteration = 0
        self.frame_timeout_period = 0        # Restart frame_timeout_period
        self.frame_1_danger = -1             # Restart frame_1_danger
        self.flag_frame_1_danger == False    
        self.frame_2_danger = -1             # Restart frame_2_danger
        self.flag_frame_2_danger == False

    def _place_food(self):
        x = random.randint(0, (self.w-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE
        y = random.randint(0, (self.h-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE
        self.food = Point(x, y)
        if self.food in self.snake:
            self._place_food()


    def play_step(self, action):
        self.frame_iteration += 1
        self.frame_timeout_period += 1           # Update frame_timeout_period

        # 1. collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        
        # 2.1 move
        self._move(action) # update the head
        
        # 2.2 check danger probability alert
        # frame_1_danger_alert
        if self._is_danger_alert() and self.flag_frame_1_danger == False:
            self.frame_1_danger = self.frame_iteration
            self.flag_frame_1_danger == True
        # frame_2_danger_alert
        if self.flag_frame_1_danger == True:
            if self._is_danger_alert():
                self.frame_2_danger = self.frame_iteration
                self.flag_frame_2_danger == True
        # Calculate number of moves until snake is safe
        moves_till_safe = len(self.snake) - ((self.frame_iteration - self.frame_2_danger) - (self.frame_iteration - self.frame_1_danger)) + 1
        # Release frame_1_danger_alert & frame_2_danger_alert after snake is safe
        #TODO;

        # 3. check if game over
        reward = 0
        game_over = False

        # 3.1 collision detection
        if self.is_collision():
            game_over = True
            reward = -10
            return reward, game_over, self.score

        # 3.2 timeout strategy
        p_steps = ( 0.7*len(self.snake) ) + 10
        print("Frame Iteration = {f}, P steps = {p}".format( p = p_steps, f = self.frame_timeout_period ))
        if self.frame_timeout_period > p_steps:
            reward = -0.5 / len(self.snake)

        # 3.3 idle too long
        if self.frame_timeout_period == 1000:
            game_over = True
            reward = -20
            return reward, game_over, self.score   

        # 4. place new food or just move
        if self.head == self.food:
            self.score += 1
            self.frame_timeout_period = 0        # Reset frame_timeout_period
            reward = 10
            self._place_food()
        else:
            self.snake.pop()
        
        # 5. update ui and clock
        self._update_ui()
        self.clock.tick(SPEED)
        # 6. return game over and score
        return reward, game_over, self.score


    def is_collision(self, pt=None):
        if pt is None:
            pt = self.head
        # hits boundary
        if pt.x > self.w - BLOCK_SIZE or pt.x < 0 or pt.y > self.h - BLOCK_SIZE or pt.y < 0:
            return True
        # near boundry
        if pt.x > self.w - BLOCK_SIZE or pt.x < 0 or pt.y > self.h - BLOCK_SIZE or pt.y < 0:
            return True
        # hits itself
        if pt in self.snake[1:]:
            return True

        return False


    def _update_ui(self):
        self.display.fill(BLACK)

        for pt in self.snake:
            pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.display, BLUE2, pygame.Rect(pt.x+4, pt.y+4, 12, 12))

        pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))

        text = font.render("Score: " + str(self.score), True, WHITE)
        self.display.blit(text, [0, 0])
        pygame.display.flip()


    def _move(self, action):
        # [straight, right, left]

        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clock_wise.index(self.direction)

        if np.array_equal(action, [1, 0, 0]):
            new_dir = clock_wise[idx] # no change
        elif np.array_equal(action, [0, 1, 0]):
            next_idx = (idx + 1) % 4
            new_dir = clock_wise[next_idx] # right turn r -> d -> l -> u
        else: # [0, 0, 1]
            next_idx = (idx - 1) % 4
            new_dir = clock_wise[next_idx] # left turn r -> u -> l -> d

        self.direction = new_dir

        x = self.head.x
        y = self.head.y
        if self.direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif self.direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif self.direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif self.direction == Direction.UP:
            y -= BLOCK_SIZE

        self.head = Point(x, y)

    def _is_danger_alert(self, pt=None):

        # beside boundary
        if pt.x == self.w - (BLOCK_SIZE + 1) or pt.x == 1 or pt.y == self.h - (BLOCK_SIZE + 1) or pt.y == 0:
            return True

    def _calculate_area(self):
        # Area = width / block_size
        pass