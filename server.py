import socket
import threading
import pygame
import pickle 

# Configurações do Servidor 
screen_width = 1280
screen_height = 700
pygame.init()

# Estado do Jogo (Game State) 
ball = pygame.Rect(0,0,30,30)
ball.center = (screen_width/2, screen_height/2)

# Oponente/Jogador 2 (Esquerda)
cpu = pygame.Rect(0,0,20,100) 
cpu.centery = screen_height/2

# Jogador 1 (Direita)
player = pygame.Rect(0,0,20,100) 
player.midright = (screen_width, screen_height/2)

# Variáveis de Movimento
ball_speed_x = 6
ball_speed_y = 6
player_speed = 0 # Velocidade do Jogador 1 (Direita)
cpu_speed = 0    # Velocidade do Jogador 2 (Esquerda)

# Pontuação e Clientes
cpu_points, player_points = 0, 0
clients = [] # Lista de sockets conectados

# Lógica de Física do Jogo 
def reset_ball():
    global ball_speed_x, ball_speed_y
    ball.center = (screen_width/2, screen_height/2)
    ball_speed_x *= -1

def animate_ball():
    global ball_speed_x, ball_speed_y, player_points, cpu_points
    ball.x += ball_speed_x
    ball.y += ball_speed_y

    # Colisão com topo e base
    if ball.bottom >= screen_height or ball.top <= 0:
        ball_speed_y *= -1
    
    # Pontuação
    if ball.right >= screen_width:
        cpu_points += 1
        reset_ball()
    if ball.left <= 0:
        player_points += 1
        reset_ball()

    # Colisão com as raquetes
    if ball.colliderect(player) or ball.colliderect(cpu):
        ball_speed_x *= -1

def game_loop():
    """ Thread principal que atualiza a física e envia o estado para todos """
    global player_speed, cpu_speed
    clock = pygame.time.Clock()
    
    while True:
        # 1. Atualiza Posição da Bola
        animate_ball()
        
        # 2. Atualiza Posição das Raquetes (Baseado no Input das Threads de Cliente)
        player.y += player_speed
        cpu.y += cpu_speed

        # Restrição de bordas (Não sair da tela)
        if player.top <= 0: player.top = 0
        if player.bottom >= screen_height: player.bottom = screen_height
        
        if cpu.top <= 0: cpu.top = 0
        if cpu.bottom >= screen_height: cpu.bottom = screen_height
        
        # 3. Empacotamento de Dados (Game State)
        game_state = {
            'ball': ball,
            'player': player,
            'cpu': cpu,
            'score': [cpu_points, player_points]
        }
        
        # 4. Broadcast (Envio para todos os clientes)
        data = pickle.dumps(game_state)
        for client in clients:
            try:
                client.send(data)
            except:
                clients.remove(client)

        clock.tick(60)

# Tratamento de Input Individual 
def handle_client_input(client_socket, player_id):
    """ Recebe comandos de um cliente específico e atualiza a variável correspondente """
    global player_speed, cpu_speed
    
    print(f"Iniciando thread de input para Jogador {player_id}")
    
    while True:
        try:
            # Recebe o comando (UP, DOWN, STOP)
            request = client_socket.recv(1024).decode()
            if not request: break
            
            # Lógica de Controle: Define quem controla qual raquete
            
            # Se for o Jogador 1 (Primeiro a conectar - ID 0) -> Controla a DIREITA ('player')
            if player_id == 0:
                if request == "UP": player_speed = -6
                elif request == "DOWN": player_speed = 6
                elif request == "STOP": player_speed = 0
            
            # Se for o Jogador 2 (Segundo a conectar - ID 1) -> Controla a ESQUERDA ('cpu')
            elif player_id == 1:
                if request == "UP": cpu_speed = -6
                elif request == "DOWN": cpu_speed = 6
                elif request == "STOP": cpu_speed = 0
                
        except:
            break
    
    print(f"Jogador {player_id} desconectou.")
    client_socket.close()

# Inicialização do Servidor
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 5555))
    server.listen(2) # Aceita até 2 conexões na fila
    print("Servidor iniciado na porta 5555. Aguardando jogadores...")

    # Inicia o Loop do Jogo em paralelo
    threading.Thread(target=game_loop).start()

    while True:
        conn, addr = server.accept()
        
        # Define o ID do jogador baseado na ordem de chegada
        # 0 = Player 1, 1 = Player 2
        current_player_id = len(clients)
        
        print(f"Nova conexão: {addr} - Atribuído ID: {current_player_id}")
        clients.append(conn)
        
        # Cria uma thread dedicada para escutar este cliente
        threading.Thread(target=handle_client_input, args=(conn, current_player_id)).start()

if __name__ == '__main__':
    start_server()