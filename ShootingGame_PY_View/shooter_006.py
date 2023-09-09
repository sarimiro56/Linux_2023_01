import pygame
from pygame import mixer
import os
import random
import csv
import button

mixer.init()
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
ROWS = 16
COLS = 150
SCROLL_THRESH = 200
screen_scroll = 0
bg_scroll = 0
MAX_LEVELS = 3

TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPE = 21
level = 1 
start_game = False

# load audio
pygame.mixer.music.load('audio/music2.mp3')
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1, 0.0, 5000)
jump_fx = pygame.mixer.Sound('audio/jump.wav')
jump_fx.set_volume(0.2)
shot_fx = pygame.mixer.Sound('audio/shot.wav')
shot_fx.set_volume(0.2)
grenade_fx = pygame.mixer.Sound('audio/grenade.wav')
grenade_fx.set_volume(0.6)

#load image
start_img = pygame.image.load('img/start_btn.png').convert_alpha()
exit_img = pygame.image.load('img/exit_btn.png').convert_alpha()
restart_img = pygame.image.load('img/restart_btn.png').convert_alpha()
sky_img = pygame.image.load('img/background/sky_cloud.png').convert_alpha()
mountain_img = pygame.image.load('img/background/mountain.png').convert_alpha()
pine1_img = pygame.image.load('img/background/pine1.png').convert_alpha()
pine2_img = pygame.image.load('img/background/pine2.png').convert_alpha()

# 타일 이미지들을 리스트에 저장
img_list = []
for x in range(TILE_TYPE):
    img = pygame.image.load(f'img/tile/{x}.png')
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)

#bullet
bullet_img = pygame.image.load("img/icons/bullet.png").convert_alpha()
#Grenade
grenade_img = pygame.image.load("img/icons/grenade.png").convert_alpha()
#pick up boxs
health_box_img = pygame.image.load("img/icons/health_box.png").convert_alpha()
ammo_box_img = pygame.image.load("img/icons/ammo_box.png").convert_alpha()
grenade_box_img = pygame.image.load("img/icons/grenade_box.png").convert_alpha()

item_boxes = { 'Health' : health_box_img,
               'Ammo' : ammo_box_img,
               'Grenade' : grenade_box_img
               }
#define colours
BG = (100, 100, 200)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

#폰트 정의
font = pygame.font.SysFont('Futura', 30)

def draw_text(text, font, text_col, x, y):
    img = font.render(text,True, text_col)
    screen.blit(img, (x,y))

def draw_bg():
    screen.fill(BG)
#    pygame.draw.line(screen, RED, (0,300), (SCREEN_WIDTH, 300))
    width = sky_img.get_width()
    for x in range(6):
        screen.blit(sky_img, ((x*width)-bg_scroll * 0.5,0))
        screen.blit(mountain_img, ((x*width)-bg_scroll * 0.6, SCREEN_HEIGHT- mountain_img.get_height() - 300))
        screen.blit(pine1_img, ((x*width)-bg_scroll * 0.7, SCREEN_HEIGHT- pine1_img.get_height() - 200))
        screen.blit(pine2_img, ((x*width)-bg_scroll * 0.8, SCREEN_HEIGHT- pine2_img.get_height()))
def reset_level():
    bullet_group.empty()
    grenade_group.empty()
    explosion_group.empty()
    enemy_group.empty()
    item_box_group.empty()
    water_group.empty()
    decoration_group.empty()
    gameexit_group.empty()

    data = []
    for row in range(ROWS):
        r = [-1]*COLS
        data.append(r)

    return data

class Soldier(pygame.sprite.Sprite):
    def __init__(self, char_type, x,y, scale, speed, ammo, grenades):
        self.char_type = char_type
        self.alive = True
        pygame.sprite.Sprite.__init__(self)
        self.animation_list = []
        self.frame_index = 0
        self.jump = False
        self.shoot_cooldown = 0
        self.ammo = ammo
        self.start_ammo = ammo
        self.grenades = grenades
        self.health = 100
        self.max_health = self.health
        self.in_air = False
        temp_list = []
        self.action = 0
        self.vel_y = 0
        self.speed = speed
        #AI관련 변수
        self.move_counter = 0
        self.idling = False
        self.idling_counter = 0
        self.vision = pygame.Rect(0, 0, 150, 20)

        #load all images for the players
        animation_types = ["Idle", "Run", "Jump", "Death"]
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

    def update(self):
        self.update_animation()
        self.check_alive()
        #update cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -=1

    def move(self, move_left, move_right):
        dx = 0
        dy = 0
        screen_scroll = 0
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
            self.vel_y = -15
            self.jump = False
            self.in_air = True
        self.vel_y += GRAVITY
        if self.vel_y > 11:
            self.vel_y = 11
        dy += self.vel_y

        # check collision
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.rect.width, self.rect.height):
                dx = 0
                # if the AI has hit awall then make it turn around
                if self.char_type == 'enemy':
                    self.direction *= -1
                    self.move_count = 0
            # check for collision in the y direction
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.rect.width, self.rect.height):
                #check if below the ground, i.e. jumping
                if self.vel_y <0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom
        # check for collision with water
        if pygame.sprite.spritecollide(self,water_group,False):
            self.health = 0

        #check for collision with exit
        level_complete = False
        if pygame.sprite.spritecollide(self, gameexit_group, False):
            level_complete = True

        # check if fallen off the map
        if self.rect.bottom > SCREEN_HEIGHT:
            self.health = 0

        #check if going off the edges of the screen
        if self.char_type == 'player':
            if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
                dx = 0

        self.rect.x += dx
        self.rect.y += int(dy)

        #update scroll based on player position
        if self.char_type == 'player':
            if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESH and bg_scroll < (world.level_length * TILE_SIZE) - SCREEN_WIDTH) or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
                self.rect.x -= dx
                screen_scroll = -dx
        return screen_scroll, level_complete

    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0 :
            self.shoot_cooldown = 20
            bullet = Bullet(self.rect.centerx + int(0.65* player.rect.size[0]*self.direction), self.rect.centery, self.direction)
            bullet_group.add(bullet)
            #reduce ammo
            self.ammo -= 1
            shot_fx.play()
    
    def ai(self):
        if self.alive and player.alive:
            if self.idling == False and random.randint(1, 100) == 1:
                self.update_action(0) # Idle
                self.idling = True
                self.idling_counter = 50
            if self.vision.colliderect(player.rect):
                # 움직이는 것을 멈추고 플레이어에게 총알을 발사
                self.update_action(0)
                self.shoot()
            else:
                if self.idling == False:
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1)
                    self.move_counter += 1
                    self.vision.center = (self.rect.centerx + 75*self.direction, self.rect.centery)
                    if self.move_counter > TILE_SIZE:
                        self.direction *= -1
                        self.move_counter *= -1
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False

        #scroll
        self.rect.x += screen_scroll

    def update_animation(self):
        #update animation
        ANIMATION_COOLDOWN = 100
        #update image depending on current frame
        self.image = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN :
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
            if self.frame_index >= len(self.animation_list[self.action]):
                if self.action == 3:
                    self.frame_index = len(self.animation_list[self.action]) - 1
                else:
                    self.frame_index = 0

    def update_action(self, new_action):
        #Check if the new action is different to the previous one
        if new_action != self.action:
            self.action = new_action
            #update the animation settings
            self.frame_index = 0;
            self.update_time = pygame.time.get_ticks()


    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)

    def draw(self):
        screen.blit(pygame.transform.flip(self.image,self.flip, False),self.rect)
        #pygame.draw.rect(screen,RED,self.rect,1)
        #pygame.draw.rect(screen, RED, self.vision, 1)

class World():
    def __init__(self):
        self.obstacle_list = []

    def process_data(self, data):
        self.level_length = len(data[0])
        #맵 데이터 파일에 있는 타이리의 값을 불러와서 처리
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x*TILE_SIZE
                    img_rect.y = y*TILE_SIZE
                    tile_data = (img, img_rect)
                    if tile >= 0 and tile <= 8:
                        self.obstacle_list.append(tile_data)
                    elif tile >= 9 and tile <= 10:
                        water = Water(img, x * TILE_SIZE, y * TILE_SIZE)
                        water_group.add(water)
                    elif tile >= 11 and tile <= 14:
                        # Decoration
                        decoration = Decoration(img, x*TILE_SIZE, y*TILE_SIZE)
                        decoration_group.add(decoration)
                    elif tile == 15: 
                        # 플레이어 생성
                        player = Soldier("player", x * TILE_SIZE, y * TILE_SIZE, 1.65, 5, 20, 5)
                        health_bar = HealthBar(10, 10, player.health, player.health)
                    elif tile == 16:
                        # 적군 생성
                        enemy = Soldier("enemy", x * TILE_SIZE, y * TILE_SIZE, 1.65, 2, 20, 0)
                        enemy_group.add(enemy)
                    elif tile == 17:
                        # 탄약 아이템 생성
                        item_box = ItemBox('Ammo', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 18: 
                        # 수류탄 아이템 생성
                        item_box = ItemBox('Grenade', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 19: 
                        # 핼스 아이템 생성
                        item_box = ItemBox('Health', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 20:
                        #레벨 끝내고 다음 레벨로 진행
                        gameexit = Exit(img, x*TILE_SIZE, y*TILE_SIZE)
                        gameexit_group.add(gameexit)
                        pass

        return player, health_bar

    def draw(self):
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1])
            
class Decoration(pygame.sprite.Sprite):
    def __init__(self,img, x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE//2, y + (TILE_SIZE-self.image.get_height()))
    def update(self):
        self.rect.x += screen_scroll

class Water(pygame.sprite.Sprite):
    def __init__(self,img, x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE//2, y + (TILE_SIZE-self.image.get_height()))
    def update(self):
        self.rect.x += screen_scroll

class Exit(pygame.sprite.Sprite):
    def __init__(self,img, x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE//2, y + (TILE_SIZE-self.image.get_height()))
    def update(self):
        self.rect.x += screen_scroll

class ItemBox(pygame.sprite.Sprite):
    def __init__(self,item_type, x,y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE//2, y + (TILE_SIZE-self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll
        #Check if player has picked up the box
        if pygame.sprite.collide_rect(self,player):
            #check what kind of box it was
            if self.item_type == 'Health':
                player.health += 25
                if player.health > player.max_health:
                    player.health = player.max_health
            elif self.item_type == 'Ammo' :
                player.ammo += 15
            elif self.item_type == 'Grenade' :
                player.grenades += 3
            #delete the item box
            self.kill()

class HealthBar():
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        #새로운 핼스 값으로 업데이트
        self.health = health
        #최대치에 비례하는 비율 계산
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 24))
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150*ratio, 20))

class Bullet(pygame.sprite.Sprite):
    def __init__(self,x,y,direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 8
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.direction = direction

    def update(self):
        #총알 이동
        self.rect.x += (self.direction * self.speed) + screen_scroll
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH :
            self.kill()
        
        #총알이 장애물과 충돌하는지 체크
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()
        #캐릭터와의 총알의 충돌 테스트
        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                player.health -= 5
                self.kill()
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.alive:
                    enemy.health -= 25
                    self.kill()

class Grenade(pygame.sprite.Sprite):
    def __init__(self,x,y,direction):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100
        self.vel_y = -11
        self.speed = 5
        self.image = grenade_img
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.direction = direction
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        self.vel_y += GRAVITY
        dx = self.direction * self.speed
        dy = self.vel_y

        #장애물과의 충돌 점검
        for tile in world.obstacle_list:
            #장애물 벽들과 충돌점검
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                self.direction *= -1
                dx = self.direction * self.speed
            # y 방향 충돌 점검
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                self.speed = 0
                #폭탄이 위에 있는 타일의 밑부분에 충돌 여부 (위로 던져지는 상황)
                if self.vel_y < 0 :
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                # 아래도 떨어지는 중 바닥에 도착 여부
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    dy = tile[1].top - self.rect.bottom

        # Check collision with walls
        #if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
        #    self.direction *= -1
        #    dx = self.direction * self.speed

        #update grenade position
        self.rect.x += dx + screen_scroll
        self.rect.y += dy

        #countdown timer
        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            grenade_fx.play()
            explosion = Explosion(self.rect.x, self.rect.y, 0.8)
            explosion_group.add(explosion)
            # Do damage to anyone that is nearby
            if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE*2 and abs(self.rect.centery-player.rect.centery) <TILE_SIZE*2:
                player.health -= 30

            for enemy in enemy_group:
                if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE*2 and abs(self.rect.centery-enemy.rect.centery) <TILE_SIZE*2:
                    enemy.health -= 50
                
class Explosion(pygame.sprite.Sprite):
    def __init__(self,x,y,scale):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1,6):
            img = pygame.image.load(f'img/explosion/exp{num}.png').convert_alpha()
            img = pygame.transform.scale(img,(int((img.get_width()*scale)),int((img.get_height()*scale))))
            self.images.append(img)
        self.frame_index = 0
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.counter = 0

    def update(self):
        #screen_scroll
        self.rect.x += screen_scroll
        EXPLOSION_SPEED = 7
        #update explosion animation
        self.counter += 1
        if self.counter >= EXPLOSION_SPEED:
            self.counter = 0
            self.frame_index += 1
            # if the animation is complate delete the explosion
            if self.frame_index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame_index]
#create buttons
start_button = button.Button(SCREEN_WIDTH // 2 - 130 , SCREEN_HEIGHT // 2 - 150, start_img, 1)
exit_button = button.Button(SCREEN_WIDTH // 2 - 110 , SCREEN_HEIGHT // 2 + 50, exit_img, 1)
restart_button = button.Button(SCREEN_WIDTH // 2 - 70 , SCREEN_HEIGHT // 2 - 50, restart_img, 1)

# create sprite groups
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
gameexit_group = pygame.sprite.Group()
# Temphe


#player action variables
move_left = False
move_right = False
shoot = False
grenade = False
grenade_thrown = False

#빈 타일 목록(맵) 만들기
world_data = []
for row in range(ROWS):
    r = [-1] * COLS
    world_data.append(r)
#맵(레벨)데이터를 읽어서 월드맵을 만들기
with open(f'level{level}_data.csv', newline = '') as csvfile:
    reader = csv.reader(csvfile, delimiter = ',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)
#print(world_data)
world = World()
player, health_bar = world.process_data(world_data)

run = True

while run:
    clock.tick(FPS)

    if start_game == False:
        # draw main menu
        screen.fill(BG)
        if start_button.draw(screen):
            start_game = True
        if exit_button.draw(screen):
            run = False
    else :

        draw_bg()
        world.draw()
        #플레이어 핼스 보여주기
        health_bar.draw(player.health)
        #Ammo 보여주기
        draw_text(f'AMMO:', font, WHITE, 10, 35)
        for x in range(player.ammo):
            screen.blit(bullet_img, (90+(x*10),40))
        # 수류탄 개수 보이기
        draw_text(f'GRENADES:', font, WHITE, 10, 70)
        for x in range(player.grenades):
            screen.blit(grenade_img, (150+(x*15),70))

        player.update()
        player.draw()
        for enemy in enemy_group:
            enemy.ai()
            enemy.update()
            enemy.draw()

        #update and draw groups
        bullet_group.update()
        grenade_group.update()
        explosion_group.update()
        item_box_group.update()
        decoration_group.update()
        water_group.update()
        gameexit_group.update()
        bullet_group.draw(screen)
        grenade_group.draw(screen)
        explosion_group.draw(screen)
        item_box_group.draw(screen)
        decoration_group.draw(screen)
        water_group.draw(screen)
        gameexit_group.draw(screen)

        if player.alive :
            if shoot :
                player.shoot()
            elif grenade and grenade_thrown == False and player.grenades > 0:
                grenade = Grenade(player.rect.centerx + (0.5*player.rect.size[0]*player.direction), player.rect.top, player.direction)
                grenade_group.add(grenade)
                grenade_thrown = True
                player.grenades -= 1
            if player.in_air:
                player.update_action(2) #2 jump
            elif move_left or move_right:
                player.update_action(1)  #run
            else:
                player.update_action(0)  #Idle

            screen_scroll, level_complete = player.move(move_left, move_right)
            #print(level_complete)
            bg_scroll -= screen_scroll
            # check if player has completed level
            if level_complete:
                level += 1
                bg_scroll = 0
                world_data = reset_level()
                if level <= MAX_LEVELS:
                    #맵(레벨)데이터를 읽어서 월드맵을 만들기
                    with open(f'level{level}_data.csv', newline = '') as csvfile:
                        reader = csv.reader(csvfile, delimiter = ',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)
                    world = World()
                    player, health_bar = world.process_data(world_data)

        else:
            screen_scroll = 0
            if restart_button.draw(screen):
                bg_scroll = 0
                world_data = reset_level()

                #맵(레벨)데이터를 읽어서 월드맵을 만들기
                with open(f'level{level}_data.csv', newline = '') as csvfile:
                    reader = csv.reader(csvfile, delimiter = ',')
                    for x, row in enumerate(reader):
                        for y, tile in enumerate(row):
                            world_data[x][y] = int(tile)
                #print(world_data)
                world = World()
                player, health_bar = world.process_data(world_data)
            
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
            if event.key == pygame.K_SPACE:
                shoot = True
            if event.key == pygame.K_q:
                grenade = True
            if event.key == pygame.K_w and player.alive:
               player.jump = True
               jump_fx.play()

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                move_left = False
            if event.key == pygame.K_d:
                move_right = False
            if event.key == pygame.K_SPACE:
                shoot = False
            if event.key == pygame.K_q:
                grenade = False
                grenade_thrown = False
            if event.key == pygame.K_w:
                player.jump = False
    pygame.display.update()


pygame.quit()

