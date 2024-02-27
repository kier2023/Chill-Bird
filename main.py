import pygame
import random
import asyncio
import threading
from pygame.locals import *

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

CLOCK = pygame.time.Clock()
fps = 60

WIDTH = 864
HEIGHT = 936

SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chill Bird")

font = pygame.font.Font('font/Chewy-Regular.ttf', 50)
white = (255, 255, 255)

GROUND_SCROLL = 0
SCROLL_SPEED = 4
FLYING = False
GAME_OVER = False
PIPE_GAP = 150
PIPE_FREQ = 1500 
LAST_PIPE = pygame.time.get_ticks() - PIPE_FREQ
SCORE = 0
PASS_PIPE = False
DEV_TEXT = "© BLUGAME DEVELOPMENT"
DEV_TEXT_POSITION = (WIDTH - 170, HEIGHT - 10)
DEV_FONT_SIZE = 15
SUCCESS_SOUND = pygame.mixer.Sound('sounds/success.wav')
bg_music = pygame.mixer.music.load('sounds/bg_music.wav')
pygame.mixer.music.set_volume(0.1)

bg = pygame.image.load("images/bg.png")
ground = pygame.image.load("images/ground.png")
button_img = pygame.image.load("images/restart.png")
click_me = pygame.image.load("images/clickstart.png")

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    SCREEN.blit(img, (x, y))

class BIRD(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        for num in range(1, 4):
            img = pygame.image.load(f"images/bird{num}.png")
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.vel = 0
        self.clicked = False
    
    def update(self):
        if FLYING == True:
            self.vel += 0.5
            if self.vel > 8:
                self.vel = 8
            if self.rect.bottom < 768:
                self.rect.y += int(self.vel)

        if GAME_OVER == False:
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                self.vel = -10
            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False

            self.counter += 1
            flap_cooldown = 5

            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
            self.image = self.images[self.index]

            self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)
        else: 
            self.image = pygame.transform.rotate(self.images[self.index], -90)

class PIPE(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("images/pipe.png")
        self.rect = self.image.get_rect()
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(PIPE_GAP / 2)]
        if position == -1:
            self.rect.topleft = [x, y + int(PIPE_GAP / 2)]

    def update(self):
        if not GAME_OVER:
            self.rect.x -= SCROLL_SPEED
            if self.rect.right < 0:
                self.kill()

class BUTTON():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self):
        action = False
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True
        SCREEN.blit(self.image, (self.rect.x, self.rect.y))
        return action

    def reset_game():
        pipe_group.empty()
        flappy.rect.x = 100
        flappy.rect.y = int(HEIGHT / 2)
        SCORE = 0
        return SCORE

bird_group = pygame.sprite.Group()
flappy = BIRD(100, (HEIGHT / 2))
bird_group.add(flappy)
pipe_group = pygame.sprite.Group()
button = BUTTON(WIDTH // 2 - button_img.get_width() // 2, HEIGHT // 2 - button_img.get_height() // 2, button_img)
run = True

pygame.mixer.music.play(-1) 

async def main_loop():
    global run, GROUND_SCROLL, SCORE, FLYING, GAME_OVER, LAST_PIPE, PASS_PIPE
    while run:
        CLOCK.tick(fps)
        SCREEN.blit(bg, (0, 0))
        bird_group.draw(SCREEN)
        bird_group.update()
        pipe_group.draw(SCREEN)
        pipe_group.update()
        SCREEN.blit(ground, (GROUND_SCROLL, 768))

        if len(pipe_group) > 0:
            if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right and PASS_PIPE == False:
                PASS_PIPE = True
            if PASS_PIPE == True:
                if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                    SCORE += 1
                    PASS_PIPE = False
                    SUCCESS_SOUND.play() 
            
        draw_text(str(SCORE), font, white, int(WIDTH / 2), 20)

        if not FLYING and not GAME_OVER:
            SCREEN.blit(click_me, (WIDTH // 2 - click_me.get_width() // 2, HEIGHT // 2 - click_me.get_height() // 2))

        if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0:
            GAME_OVER = True

        if flappy.rect.bottom > 768:
            GAME_OVER = True
            FLYING = False
        
        if GAME_OVER == False and FLYING == True:
            time_now = pygame.time.get_ticks()
            if time_now - LAST_PIPE > PIPE_FREQ:
                pipe_height = random.randint(-100, 100)
                btm_pipe = PIPE(WIDTH, (HEIGHT / 2) + pipe_height, -1)
                top_pipe = PIPE(WIDTH, (HEIGHT / 2) + pipe_height, 1)
                pipe_group.add(btm_pipe, top_pipe)
                LAST_PIPE = time_now

            GROUND_SCROLL -= SCROLL_SPEED
            if abs(GROUND_SCROLL) > 35:
                GROUND_SCROLL = 0

        if GAME_OVER == True:
            if button.draw() == True:
                GAME_OVER = False
                SCORE = BUTTON.reset_game()

        draw_text(DEV_TEXT, pygame.font.Font('font/Chewy-Regular.ttf', DEV_FONT_SIZE), (25, 25, 112), DEV_TEXT_POSITION[0], DEV_TEXT_POSITION[1] - DEV_FONT_SIZE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN and FLYING == False and GAME_OVER == False:
                FLYING = True

        pygame.display.update()
        await asyncio.sleep(0)

    pygame.mixer.music.stop()
    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main_loop())
