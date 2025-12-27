import socket
import threading
import pygame
import pickle 

# Configurações do Servidor
screen_width = 1280
screen_height = 700

# Inicializa Pygame apenas para uso das classes matemáticas (Rect), sem janela gráfica.
pygame.init()

# Estado do Jogo (Game State)
# Centraliza a posição de todos os objetos e pontuação.
ball = pygame.Rect(0,0,30,30)
ball.center = (screen_width/2, screen_height/2)

cpu = pygame.Rect(0,0,20,100) 
cpu.centery = screen_height/2

player = pygame.Rect(0,0,20,100) 
player.midright = (screen_width, screen_height/2)

ball_speed_x = 6
ball_speed_y = 6
player_speed = 0
cpu_speed = 0 

cpu_points, player_points = 0, 0

# Lista para armazenar sockets de clientes conectados para broadcast.
clients = []

# Lógica do Jogo
def reset_ball():
    global ball_speed_x, ball_speed_y
    ball.center = (screen_width/2, screen_height/2)
    ball_speed_x *= -1

def animate_ball():
    global ball_speed_x, ball_speed_y, player_points, cpu_points
    ball.x += ball_speed_x
    ball.y += ball_speed_y

    # Colisão com bordas superior/inferior
    if ball.bottom >= screen_height or ball.top <= 0:
        ball_speed_y *= -1
    
    # Sistema de Pontuação
    if ball.right >= screen_width:
        cpu_points += 1
        reset_ball()
    if ball.left <= 0:
        player_points += 1
        reset_ball()

    # Colisão com as raquetes (Paddles)
    if ball.colliderect(player) or ball.colliderect(cpu):
        ball_speed_x *= -1

def game_loop():
    """ Loop principal de processamento do servidor (Física + Broadcast) """
    clock = pygame.time.Clock()
    while True:
        # 1. Atualiza a física do jogo
        animate_ball()
        
        # 2. Prepara o pacote de dados (Estado atual do jogo)
        game_state = {
            'ball': ball,
            'player': player,
            'cpu': cpu,
            'score': [cpu_points, player_points]
        }
        
        # 3. Serialização e Broadcast
        # Transforma o dicionário em bytes e envia para todos os clientes conectados.
        data = pickle.dumps(game_state)
        
        for client in clients:
            try:
                client.send(data)
            except:
                # Remove cliente se a conexão cair
                clients.remove(client)

        clock.tick(60) # Mantém a taxa de atualização lógica a 60 FPS

# Configuração de Rede
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Bind 0.0.0.0 permite conexões locais e externas
    server.bind(('0.0.0.0', 5555))
    server.listen(2) # Limita a fila de conexões
    print("Servidor iniciado. Aguardando conexões na porta 5555...")

    # Inicia o loop de jogo em uma thread separada para não bloquear a aceitação de novas conexões
    threading.Thread(target=game_loop).start()

    while True:
        conn, addr = server.accept()
        print(f"Nova conexão estabelecida: {addr}")
        clients.append(conn) 

if __name__ == '__main__':
    start_server()