import pygame

pygame.init()

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Shooter")

#set frame rate
clock = pygame.time.Clock()
FPS = 60

#define colours
BG = (155,200,120)
def draw_bg():
    screen.fill(BG)

class Soldier(pygame.sprite.Sprite):
    def __init__(self, x,y, scale, speed):

        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load("img/player/Idle/0.png")
        self.img = pygame.transform.scale(img,(int(img.get_width()*scale),int(img.get_height()*scale)))
        self.rect = img.get_rect()
        self.rect.center = (x,y)
        self.speed = speed
        self.direction = 1
        self.flip = False
    def move(self, move_left, move_right):
        dx = 0
        dy = 0

        if move_left:
            dx = -self.speed
        if move_right:
            dx = self.speed

        self.rect.x += dx
        self.rect.y += dy

    def draw(self):
        screen.blit(pygame.transform.flip(self.img, self.flip, False),self.rect)

player = Soldier(200,200,3,5)

#player action variables
move_left = False
move_right = False

run = True

while run:
    clock.tick(FPS)
    draw_bg()
    player.move(move_left, move_right)
    player.draw()
    

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

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                move_left = False
            if event.key == pygame.K_d:
                move_right = False
    pygame.display.update()


pygame.quit()

