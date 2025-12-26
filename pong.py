import pygame, sys

pygame.init()

screen_width = 1280
screen_height = 700

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Meu jogo pong")

clock = pygame.time.Clock()

ball = pygame.Rect(0,0,30,30)
ball.center = (screen_width/2, screen_height/2)

cpu = pygame.Rect(0,0,20,100)
cpu.centery = screen_height/2

player = pygame.Rect(0,0,20,100)
player.midright = (screen_width, screen_height/2)

ball_speed_x = 6
ball_speed_y = 6
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()  

    #Muda as posições dos objetos do game
    ball.x += ball_speed_x
    ball.y += ball_speed_y

    #Desenha os objetos do game
    pygame.draw.aaline(screen,'white',(screen_width/2,0), (screen_width/2, screen_height))
    pygame.draw.ellipse(screen,'white',ball)
    pygame.draw.rect(screen,'white',cpu)
    pygame.draw.rect(screen,'white',player)
   
   
    #Update o display
    pygame.display.update()
    clock.tick(60)
        