import pygame, sys

# 1. Inicia o Pygame e Configurações 
pygame.init()
screen_width = 1280
screen_height = 700

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Meu jogo pong")
clock = pygame.time.Clock()

# 2. Criação dos Objetos
ball = pygame.Rect(0,0,30,30)
ball.center = (screen_width/2, screen_height/2)

cpu = pygame.Rect(0,0,20,100)
cpu.centery = screen_height/2

player = pygame.Rect(0,0,20,100)
player.midright = (screen_width, screen_height/2)

ball_speed_x = 6
ball_speed_y = 6

# 3. Animações e física
def animate_ball():
    global ball_speed_x, ball_speed_y
    
    # Move a bola
    ball.x += ball_speed_x
    ball.y += ball_speed_y

    # Física: Bater em cima e embaixo 
    if ball.bottom >= screen_height or ball.top <= 0:
        ball_speed_y *= -1
    
    # Física: Bater nos lados
    if ball.right >= screen_width or ball.left <= 0:
        ball_speed_x *= -1

# 4. Loop Principal
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()  

    animate_ball() 
    
    screen.fill('black')
    pygame.draw.aaline(screen,'white',(screen_width/2,0), (screen_width/2, screen_height))
    pygame.draw.ellipse(screen,'white',ball)
    pygame.draw.rect(screen,'white',cpu)
    pygame.draw.rect(screen,'white',player)
    
    pygame.display.update()
    clock.tick(60)