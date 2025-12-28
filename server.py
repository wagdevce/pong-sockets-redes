import socket
import threading
import pygame
import pickle 
import random
from datetime import datetime 

# Configurações Gerais 
screen_width = 1280
screen_height = 700
Winning_Score = 5 
Initial_Speed = 6 
Max_Speed = 15 

# Inicialização do Pygame (utilizado apenas para cálculos geométricos da classe Rect)
pygame.init()

# Estado Global do Jogo
# Definição das coordenadas e dimensões dos objetos (Bola e Raquetes)
ball = pygame.Rect(0,0,50,50)
ball.center = (screen_width/2, screen_height/2)

cpu = pygame.Rect(0,0,20,100) 
cpu.centery = screen_height/2

player = pygame.Rect(0,0,20,100) 
player.midright = (screen_width, screen_height/2)

# Variáveis de controle de física e velocidade
ball_speed_x = 6
ball_speed_y = 6
player_speed = 0
cpu_speed = 0 

# Variáveis de pontuação e gerenciamento de sessão
cpu_points, player_points = 0, 0
clients = []    
winner = None   

# Persistência de Dados
def save_score(winner_name):
    """ Registra o vencedor e o timestamp no arquivo de log (ranking.txt). """
    try:
        with open("ranking.txt", "a") as f:
            timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
            f.write(f"{timestamp} - Vencedor: {winner_name}\n")
        print(f"Log de vitória registrado: {winner_name}")
    except Exception as e:
        print(f"Erro ao gravar arquivo de ranking: {e}")

# Lógica de Física e Regras
def reset_ball():
    #Reinicia a posição da bola no centro da tela e inverte a direção horizontal
    global ball_speed_x, ball_speed_y
    ball.center = (screen_width/2, screen_height/2)
    
    # Define a direção aleatória onde a bola vai no começo (esquerda ou direita)
    direction_x = random.choice([1, -1])
    direction_y = random.choice([1 ,-1])

    # Reseta para a velocidade inicial
    ball_speed_x = Initial_Speed * direction_x
    ball_speed_y = Initial_Speed * direction_y

def animate_ball():
    """ Calcula a movimentação da bola, colisões com bordas/raquetes e pontuação. """
    global ball_speed_x, ball_speed_y, player_points, cpu_points, winner
    
    # Interrompe cálculos se houver um vencedor
    if winner is not None:
        return

    # Atualização de posição
    ball.x += ball_speed_x
    ball.y += ball_speed_y

    # Colisão vertical (Teto e Chão)
    if ball.bottom >= screen_height or ball.top <= 0:
        ball_speed_y *= -1
    
    # Verificação de Pontuação e Condição de Vitória
    if ball.right >= screen_width:
        cpu_points += 1
        if cpu_points >= Winning_Score:
            winner = "Jogador 2 (Esq)"
            save_score(winner)
        reset_ball()
        
    if ball.left <= 0:
        player_points += 1
        if player_points >= Winning_Score:
            winner = "Jogador 1 (Dir)"
            save_score(winner)
        reset_ball()

    # Colisão com as Raquetes
    if ball.colliderect(player) or ball.colliderect(cpu):
        ball_speed_x *= -1

        #Aumenta velocidade em 10% toda vez que a bola bater na raquete
        ball_speed_x *= 1.1
        ball_speed_y *= 1.1

        ball_speed_x = max(-Max_Speed, min(ball_speed_x, Max_Speed))
        ball_speed_y = max(-Max_Speed, min(ball_speed_y, Max_Speed))

def reset_game():
    """ Zera o placar e reinicia a partida """
    global cpu_points, player_points, winner
    cpu_points = 0
    player_points = 0
    winner = None
    reset_ball()
    print("Jogo reiniciado por solicitação de um jogador.")

def game_loop():
    """ 
    Thread Principal: Gerencia o fluxo do jogo (Lobby/Partida), 
    executa a física e realiza o broadcast do estado para os clientes.
    """
    global player_speed, cpu_speed, latest_ranking, winner
    clock = pygame.time.Clock()
    latest_ranking = []

    while True:
        # 1. Controle de Lobby: Aguarda conexão de 2 jogadores
        if len(clients) < 2:
            current_status = "WAITING"
        else:
            current_status = "PLAYING"

        # 2. Execução da Física (apenas se o status for PLAYING)
        if current_status == "PLAYING":
            animate_ball()
            
            # Carrega o ranking do disco apenas na conclusão da partida
            if winner is not None and not latest_ranking:
                 try:
                    with open("ranking.txt", "r") as f:
                        latest_ranking = [line.strip() for line in f.readlines()[-5:]]
                 except:
                    latest_ranking = ["Nenhum registro encontrado."]

            # Lógica de reinício de rodada/partida
            if winner is None:
                latest_ranking = []
                player.y += player_speed
                cpu.y += cpu_speed
                
                # Restrição de limites da tela para as raquetes
                if player.top <= 0: player.top = 0
                if player.bottom >= screen_height: player.bottom = screen_height
                if cpu.top <= 0: cpu.top = 0
                if cpu.bottom >= screen_height: cpu.bottom = screen_height
        
        # 3. Serialização e Broadcast
        # Monta o dicionário com o estado completo do jogo
        game_state = {
            'ball': ball,
            'player': player,
            'cpu': cpu,
            'score': [cpu_points, player_points],
            'winner': winner,
            'ranking': latest_ranking,
            'status': current_status 
        }
        
        # Converte para bytes e envia para todos os clientes conectados
        data = pickle.dumps(game_state)
        for client in clients:
            try:
                client.send(data)
            except:
                # Remove cliente da lista em caso de falha de envio
                clients.remove(client)

        clock.tick(60) # Mantém a taxa de atualização a 60 FPS

def handle_client_input(client_socket, player_id):
    """ Thread dedicada para processar os inputs (comandos) de um cliente específico. """
    global player_speed, cpu_speed
    while True:
        try:
            # Recebe comandos de texto do cliente
            request = client_socket.recv(1024).decode()
            if not request: break
            
            #Verifica comando de RESET 
            if request == "RESET":
                reset_game()
            
            # Processa movimento apenas se não houver vencedor
            if winner is None:
                if player_id == 0: 
                    if request == "UP": player_speed = -6
                    elif request == "DOWN": player_speed = 6
                    elif request == "STOP": player_speed = 0
                elif player_id == 1: 
                    if request == "UP": cpu_speed = -6
                    elif request == "DOWN": cpu_speed = 6
                    elif request == "STOP": cpu_speed = 0
        except:
            break
    client_socket.close()

def start_server():
    """ Inicializa o socket TCP, realiza o bind e aceita novas conexões. """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 5555)) 
    server.listen(2)
    print("Servidor iniciado na porta 5555. Aguardando conexões...")

    # Inicia o loop lógico do jogo em uma thread separada
    threading.Thread(target=game_loop).start()

    while True:
        conn, addr = server.accept()
        current_player_id = len(clients)
        print(f"Nova conexão estabelecida: {addr} - ID Atribuído: {current_player_id}")
        
        clients.append(conn)
        # Inicia thread de input para o novo cliente
        threading.Thread(target=handle_client_input, args=(conn, current_player_id)).start()

if __name__ == '__main__':
    start_server()