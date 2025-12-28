import socket
import threading
import pygame
import pickle 
from datetime import datetime 

# Configurações 
screen_width = 1280
screen_height = 700
WINNING_SCORE = 5 

# Inicializa módulos do Pygame (necessário para classes Rect)
pygame.init()

# Estado do Jogo 
# Posições e objetos globais mantidos pelo servidor
ball = pygame.Rect(0,0,30,30)
ball.center = (screen_width/2, screen_height/2)

cpu = pygame.Rect(0,0,20,100) 
cpu.centery = screen_height/2

player = pygame.Rect(0,0,20,100) 
player.midright = (screen_width, screen_height/2)

# Variáveis de controle de movimento
ball_speed_x = 6
ball_speed_y = 6
player_speed = 0
cpu_speed = 0 

# Pontuação e Gerenciamento de Conexões
cpu_points, player_points = 0, 0
clients = []    # Lista de sockets conectados
winner = None   # Armazena o vencedor atual (None se em andamento)

# Persistência (Ranking) 
def save_score(winner_name):
    """ Salva o vencedor e data no arquivo ranking.txt """
    try:
        with open("ranking.txt", "a") as f:
            timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
            f.write(f"{timestamp} - Vencedor: {winner_name}\n")
        print(f"Ranking atualizado: {winner_name}")
    except Exception as e:
        print(f"Erro ao salvar ranking: {e}")

# Física do Jogo 
def reset_ball():
    """ Reinicia a posição da bola no centro """
    global ball_speed_x, ball_speed_y
    ball.center = (screen_width/2, screen_height/2)
    ball_speed_x *= -1

def animate_ball():
    """ Calcula movimento da bola, colisões e pontuação """
    global ball_speed_x, ball_speed_y, player_points, cpu_points, winner
    
    if winner is not None:
        return

    # Movimentação
    ball.x += ball_speed_x
    ball.y += ball_speed_y

    # Colisão com bordas superior/inferior
    if ball.bottom >= screen_height or ball.top <= 0:
        ball_speed_y *= -1
    
    # Pontuação e Condição de Vitória
    if ball.right >= screen_width:
        cpu_points += 1
        if cpu_points >= WINNING_SCORE:
            winner = "Jogador 2 (Esq)"
            save_score(winner)
        reset_ball()
        
    if ball.left <= 0:
        player_points += 1
        if player_points >= WINNING_SCORE:
            winner = "Jogador 1 (Dir)"
            save_score(winner)
        reset_ball()

    # Colisão com raquetes
    if ball.colliderect(player) or ball.colliderect(cpu):
        ball_speed_x *= -1

def game_loop():
    """ Thread principal: Atualiza física e realiza broadcast do estado """
    global player_speed, cpu_speed, latest_ranking, winner
    clock = pygame.time.Clock()
    latest_ranking = []

    while True:
        animate_ball()
        
        # Carrega ranking do disco apenas ao finalizar a partida
        if winner is not None and not latest_ranking:
             try:
                with open("ranking.txt", "r") as f:
                    latest_ranking = [line.strip() for line in f.readlines()[-5:]]
             except:
                latest_ranking = ["Sem registros."]

        # Reinício de partida: Limpa cache e atualiza posições
        if winner is None:
            latest_ranking = []
            player.y += player_speed
            cpu.y += cpu_speed
            
            # Restrição de limites da tela
            if player.top <= 0: player.top = 0
            if player.bottom >= screen_height: player.bottom = screen_height
            if cpu.top <= 0: cpu.top = 0
            if cpu.bottom >= screen_height: cpu.bottom = screen_height
        
        # Prepara pacote de dados (Estado do Jogo)
        game_state = {
            'ball': ball,
            'player': player,
            'cpu': cpu,
            'score': [cpu_points, player_points],
            'winner': winner,
            'ranking': latest_ranking 
        }
        
        # Serialização e Envio (Broadcast)
        data = pickle.dumps(game_state)
        for client in clients:
            try:
                client.send(data)
            except:
                clients.remove(client)

        clock.tick(60)

def handle_client_input(client_socket, player_id):
    """ Thread individual para processar inputs de cada cliente """
    global player_speed, cpu_speed
    while True:
        try:
            request = client_socket.recv(1024).decode()
            if not request: break
            
            if winner is None:
                # Mapeia ID do jogador para a raquete correspondente
                if player_id == 0: # Jogador 1 (Direita)
                    if request == "UP": player_speed = -6
                    elif request == "DOWN": player_speed = 6
                    elif request == "STOP": player_speed = 0
                elif player_id == 1: # Jogador 2 (Esquerda)
                    if request == "UP": cpu_speed = -6
                    elif request == "DOWN": cpu_speed = 6
                    elif request == "STOP": cpu_speed = 0
        except:
            break
    client_socket.close()

def start_server():
    """ Configuração inicial do socket e loop de aceitação """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 5555)) # Aceita conexões de qualquer interface
    server.listen(2)
    print("Servidor iniciado na porta 5555.")

    threading.Thread(target=game_loop).start()

    while True:
        conn, addr = server.accept()
        current_player_id = len(clients)
        print(f"Conexão: {addr} - ID Atribuído: {current_player_id}")
        
        clients.append(conn)
        threading.Thread(target=handle_client_input, args=(conn, current_player_id)).start()

if __name__ == '__main__':
    start_server()