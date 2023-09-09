import pygame
import os

pygame.init()

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Shooter")

#set frame rate
clock = pygame.time.Clock()
FPS = 60
#define game variables
GRAVITY = 0.75

#define colours
BG = (155,200,120)
RED = (255, 0, 0)
def draw_bg():
    screen.fill(BG)
    pygame.draw.line(screen, RED, (0,300), (SCREEN_WIDTH, 300))

class Soldier(pygame.sprite.Sprite):
    def __init__(self, char_type, x,y, scale, speed):
        self.char_type = char_type
        self.alive = True
        pygame.sprite.Sprite.__init__(self)
        self.animation_list = []
        self.frame_index = 0
        self.jump = False
        self.in_air = False
        temp_list = []
        self.action = 0
        self.vel_y = 0
        self.speed = speed
        #load all images for the players
        animation_types = ["Idle", "Run", "Jump"]
        for animation in animation_types:
            #reset temp_list
            temp_list = []
            #COUNT NUMBER OF FILES IN THE DIRECTORY
            num_of_frames = len(os.listdir(f"img/{self.char_type}/{animation}"))

            for i in range(num_of_frames):    #Idle
                img = pygame.image.load(f"img/{self.char_type}/{animation}/{i}.png")
                img = pygame.transform.scale(img,(int(img.get_width()*scale),int(img.get_height()*scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.direction = 1
        self.flip = False
        self.update_time = pygame.time.get_ticks()

    def move(self, move_left, move_right):
        dx = 0
        dy = 0

        if move_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if move_right:
            dx = self.speed
            self.flip = False
            self.direction = 1
        #jump
        if self.jump and self.in_air == False:
            self.vel_y = -11
            self.jump = False
            self.in_air = True
        self.vel_y += GRAVITY
        if self.vel_y > 11:
            self.vel_y = 11
        dy += self.vel_y

        # check collision with floor
        if self.rect.bottom + dy > 300:
            dy = 300 - self.rect.bottom
            self.in_air = False
        self.rect.x += dx
        self.rect.y += int(dy)

    def update_animation(self):
        #update animation
        ANIMATION_COOLDOWN = 100
        #update image depending on current frame
        self.image = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN :
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
            if self.frame_index >= len(self.animation_list[self.action]):
                self.frame_index = 0

    def update_action(self, new_action):
        #Check if the new action is different to the previous one
        if new_action != self.action:
            self.action = new_action
            #update the animation settings
            self.frame_index = 0;
            self.update_time = pygame.time.get_ticks()

    def draw(self):
        screen.blit(pygame.transform.flip(self.image,self.flip, False),self.rect)

player = Soldier("player", 200,200, 3, 5)
enemy = Soldier("enemy", 500, 200, 3, 2)

#player action variables
move_left = False
move_right = False

run = True

while run:
    clock.tick(FPS)
    draw_bg()
    player.update_animation()
    player.draw()
    enemy.draw()
    if player.alive :
        if player.in_air:
            player.update_action(2) #2 jump
        elif move_left or move_right:
            player.update_action(1)  #run
        else:
            player.update_action(0)  #Idle

        player.move(move_left, move_right)
        
    for event in pygame.event.get():

        #게임중지 하기 위하여 마우스로 창을 닫아주세요
        if event.type == pygame.QUIT:
            run = False

        #키보드를 눌렀을 때
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                run = False
            if event.key == pygame.K_a:
                move_left = True
            if event.key == pygame.K_d:
                move_right = True
            if event.key == pygame.K_w and player.alive:
               player.jump = True

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                move_left = False
            if event.key == pygame.K_d:
                move_right = False
            if event.key == pygame.K_w:
                player.jump = False
    pygame.display.update()


pygame.quit()

