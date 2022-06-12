import pygame
from pygame.locals import *
import tkinter as tk
from tkinter import messagebox
import random
import sys
import time
from collections import deque


SCREEN_WIDTH = 570
SCREEN_HEIGHT = 700
BOX_WIDTH = 30
HEADER_HEIGHT = int(SCREEN_HEIGHT/4.5)

SCREEN_WIDTH = max(SCREEN_WIDTH, 400)
SCREEN_WIDTH -= SCREEN_WIDTH % BOX_WIDTH
SCREEN_HEIGHT -= SCREEN_HEIGHT % BOX_WIDTH
HEADER_HEIGHT -= HEADER_HEIGHT % BOX_WIDTH

FONT_SIZE = HEADER_HEIGHT // 4

COLS = SCREEN_WIDTH / BOX_WIDTH
ROWS = (SCREEN_HEIGHT-HEADER_HEIGHT) / BOX_WIDTH



class Block:
    def __init__(self, x, y):
        self.x = x
        self.y = y


    def display(self, surface, color):
        x_coor = self.x*BOX_WIDTH + 1
        y_coor = HEADER_HEIGHT + self.y*BOX_WIDTH + 1
        width = BOX_WIDTH - 2
        pygame.draw.rect(surface, color, (x_coor, y_coor, width, width))



class Snake:
    def __init__(self, head_pos=(2, 2)):
        self.head = Block(*head_pos)
        self.body = deque([self.head])
        self.dx = 0
        self.dy = 0


    def move(self, can_pass_walls=False):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_LEFT:
                    if self.dx == 0:
                        self.dx = -1
                        self.dy = 0
                if event.key == pygame.K_RIGHT:
                    if self.dx == 0:
                        self.dx = 1
                        self.dy = 0
                if event.key == pygame.K_UP:
                    if self.dy == 0:
                        self.dx = 0
                        self.dy = -1
                if event.key == pygame.K_DOWN:
                    if self.dy == 0:
                        self.dx = 0
                        self.dy = 1
        
        tail = self.body[-1]
        tail.x = self.head.x + self.dx
        tail.y = self.head.y + self.dy
        if can_pass_walls:
            tail.x %= COLS
            tail.y %= ROWS
        self.head = self.body.pop()
        self.body.appendleft(self.head)


    def grow(self):
        # move() method will take care of its position
        self.body.append(Block(-1, -1))


    def display(self, surface):
        for block in self.body:
            block.display(surface, (200, 200, 200))
        self.head.display(surface, (0, 0, 0))



class Food(Block):
    def randomize_position(self, snake):
        self.x = random.randint(2, COLS-3)
        self.y = random.randint(2, ROWS-3)
        found = False
        
        while not found:
            for block in snake.body:
                if block.x == self.x and block.y == self.y:
                    self.x = random.randint(2, COLS-3)
                    self.y = random.randint(2, ROWS-3)
                    break
            else:
                found = True

        return found



def can_pass_through_walls():
    root = tk.Tk()

    # destroying the unwanted main window
    root.overrideredirect(1)
    root.withdraw()

    can_pass_walls = messagebox.askyesno(
        title="Pass through walls", 
        message="Do you want the snake to pass through the walls ?"
    )
    
    root.destroy()
    root.mainloop()

    return can_pass_walls



def redraw_window(surface, snake, food, score, high_score):
    surface.fill((100, 100, 225))
    
    # Draws the borders of each boxes in the surface
    for x in range(0, SCREEN_WIDTH, BOX_WIDTH):
        for y in range(0, SCREEN_HEIGHT, BOX_WIDTH):
            rect = (x, y, BOX_WIDTH, BOX_WIDTH)
            pygame.draw.rect(surface, (0, 0, 0), rect, width=1)

    food.display(surface, (0, 200, 0))
    snake.display(surface)

    # Background color for the header
    surface.fill((200, 200, 200), (0, 0, SCREEN_WIDTH, HEADER_HEIGHT))

    font = pygame.font.Font('freesansbold.ttf', FONT_SIZE)
    space_around = HEADER_HEIGHT - 2*FONT_SIZE

    score_text = font.render(f"SCORE: {score}", True, (0, 0, 0))
    score_pos = (50, space_around*1/3)
    surface.blit(score_text, score_pos)

    high_score_text = font.render(f"HIGH SCORE: {high_score}", True, (0, 0, 0))
    high_score_pos = (50, space_around*2/3 + FONT_SIZE)
    surface.blit(high_score_text, high_score_pos)

    pygame.display.update()



def play_game():
    pygame.init()
    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    snake = Snake()
    can_pass_walls = can_pass_through_walls()
    
    score = 0
    try:
        with open("high_score.txt", "r") as file:
            high_score = int(file.readline().strip())
    except:
        high_score = 0

    game_over = False

    food = Food(-1, -1)
    food.randomize_position(snake)
    
    while not game_over:
        snake.move(can_pass_walls)

        if snake.head.x == food.x and snake.head.y == food.y:
            score += 1
            snake.grow()
            food.randomize_position(snake)

        high_score = max(high_score, score)

        if not 0 <= snake.head.x < COLS or not 0 <= snake.head.y < ROWS:
            game_over = True
        else:
            for i in range(1, len(snake.body)):
                block = snake.body[i]
                if block.x == snake.head.x and block.y == snake.head.y:
                    game_over = True

        if not game_over:
            redraw_window(screen, snake, food, score, high_score)
        
        clock.tick(10)

    # Saving the new high score
    with open("high_score.txt", "w") as file:
        file.write(str(high_score))

    ask_for_retry()



def ask_for_retry():
    root = tk.Tk()

    # destroying the unwanted main window
    root.overrideredirect(1)
    root.withdraw()

    want_retry = messagebox.askretrycancel(
        title="Game Over!", 
        message="Sorry! Unfortunately, You lost the game.\nDo you want to retry ?"
    )

    root.destroy()
    root.mainloop()

    if want_retry:
        play_game()

    pygame.quit()
    sys.exit()



if __name__ == "__main__":
    play_game()


