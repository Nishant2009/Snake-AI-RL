import pygame
import random
from enum import Enum
from collections import namedtuple
import numpy as np

pygame.init()
font = pygame.font.Font('arial.ttf', 25)

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

Point = namedtuple('Point', 'x, y')

# rgb colors
WHITE = (255, 255, 255)
RED = (200,0,0)
BLACK = (0,0,0)
GREY = (25, 25, 25)
BROWN = (165, 42, 42)

BLOCK_SIZE = 20
SPEED = 40

class SnakeGameAI:

    def __init__(self, w=640, h=480):
        self.w = w
        self.h = h
        # init display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Reinforcement Learning Snake Game')
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


    def _place_food(self):
        x = random.randint(0, (self.w-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE
        y = random.randint(0, (self.h-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE
        self.food = Point(x, y)
        if self.food in self.snake:
            self._place_food()


    def play_step(self, action):
        self.frame_iteration += 1
        # 1. collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        
        # 2. move
        self._move(action) # update the head
        self.snake.insert(0, self.head)
        
        # 3. check if game over
        reward = 0
        game_over = False
        if (self.frame_iteration > 100*len(self.snake)) or self.is_collision():
            game_over = True
            reward = -10
            return reward, game_over, self.score


        # 4. place new food or just move
        if self.head == self.food:
            self.score += 1
            reward = 20
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
        # hits itself
        if pt in self.snake[1:]:
            return True

        return False


    def _update_ui(self):
        self.display.fill(WHITE)

        for i, pt in enumerate(self.snake):
            if i == 0:
                pygame.draw.rect(self.display, BROWN, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
                eye_radius = 3
                eye_offset = 6
                if self.direction == Direction.RIGHT:
                    pygame.draw.circle(self.display, BLACK, (pt.x + BLOCK_SIZE - eye_offset, pt.y + eye_offset), eye_radius)
                    pygame.draw.circle(self.display, BLACK, (pt.x + BLOCK_SIZE - eye_offset, pt.y + BLOCK_SIZE - eye_offset), eye_radius)
                if self.direction == Direction.LEFT:
                    pygame.draw.circle(self.display, BLACK, (pt.x + eye_offset, pt.y + eye_offset), eye_radius)
                    pygame.draw.circle(self.display, BLACK, (pt.x + eye_offset, pt.y + BLOCK_SIZE - eye_offset), eye_radius)
                if self.direction == Direction.UP:
                    pygame.draw.circle(self.display, BLACK, (pt.x + eye_offset, pt.y + eye_offset), eye_radius)
                    pygame.draw.circle(self.display, BLACK, (pt.x + BLOCK_SIZE - eye_offset, pt.y + eye_offset), eye_radius)
                if self.direction == Direction.DOWN:
                    pygame.draw.circle(self.display, BLACK, (pt.x + eye_offset, pt.y + BLOCK_SIZE - eye_offset), eye_radius)
                    pygame.draw.circle(self.display, BLACK, (pt.x + BLOCK_SIZE - eye_offset, pt.y + BLOCK_SIZE - eye_offset), eye_radius)

            else:
                pygame.draw.rect(self.display, BLACK, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
                pygame.draw.rect(self.display, GREY, pygame.Rect(pt.x+4, pt.y+4, 12, 12))

        pygame.draw.circle(self.display, RED, (self.food.x + BLOCK_SIZE // 2, self.food.y + BLOCK_SIZE // 2), BLOCK_SIZE // 2)

        text = font.render("Score: " + str(self.score), True, BLACK)
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