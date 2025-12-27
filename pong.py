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
player_speed = 0 #  Inicialização da velocidade do player
cpu_speed = 6

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

def animate_player():
    player.y += player_speed
     # Mantém o jogador dentro da tela
    if player.top <= 0:
        player.top = 0
   
    if player.bottom >= screen_height:
        player.bottom = screen_height

def animate_cpu():
    cpu.y += cpu_speed

    if ball.centery <= cpu.centery:
        cpu_speed = -6
    if ball.centery >= cpu.centery:
        cpu_speed = 6

    if cpu.top <= 0:
        cpu.top = 0
    if cpu.bottom >= screen_height:
        cpu.bottom = screen_height

# 4. Loop Principal
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()  
    
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                player_speed = -7
            if event.key == pygame.K_DOWN:
                player_speed = 7
    
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_UP:
                player_speed = 0
            if event.key == pygame.K_DOWN:
                player_speed = 0       

    animate_ball() #Chamada de função animação da bola
    animate_player() # Chamada da função de animação do player
    cpu.y += cpu_speed

    if ball.centery <= cpu.centery:
        cpu_speed = -6 
    if ball.centery >= cpu.centery:
        cpu_speed = 6
    
    if cpu.top <= 0:
        cpu.top = 0
    if cpu.bottom >= screen_height:
        cpu.bottom = screen_height

    screen.fill('black')
    pygame.draw.aaline(screen,'white',(screen_width/2,0), (screen_width/2, screen_height))
    pygame.draw.ellipse(screen,'white',ball)
    pygame.draw.rect(screen,'white',cpu)
    pygame.draw.rect(screen,'white',player)
    
    pygame.display.update()
    clock.tick(60)