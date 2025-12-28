import pygame
import socket
import pickle 

# Configurações Visuais 
pygame.init()
screen_width = 1280
screen_height = 700
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Pong Multiplayer")

clock = pygame.time.Clock()
font = pygame.font.Font(None, 100)
victory_font = pygame.font.Font(None, 80)
ranking_font = pygame.font.Font(None, 40)

# Conexão de Rede 
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    # Conecta ao servidor (Alterar IP conforme necessário)
    client_socket.connect(('127.0.0.1', 5555))
    print("Conectado ao servidor.")
except Exception as e:
    print(f"Erro de conexão: {e}")
    exit()

# Loop Principal 
while True:
    # 1. Tratamento de Eventos e Input
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        
        # Envia comandos de movimento
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                client_socket.send("UP".encode())
            if event.key == pygame.K_DOWN:
                client_socket.send("DOWN".encode())
        
        # Envia comando de parada
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                client_socket.send("STOP".encode())

    try:
        # 2. Recebimento de Dados
        data = client_socket.recv(4096) 
        if not data: break

        # Deserialização do estado do jogo
        game_state = pickle.loads(data)
        
        winner = game_state.get('winner')
        scores = game_state['score'] 
        ranking_list = game_state.get('ranking', [])

        # 3. Renderização
        screen.fill('black')
        
        if winner:
            # Tela de Fim de Jogo
            text_win = victory_font.render(f"FIM DE JOGO!", True, "yellow")
            text_name = victory_font.render(f"Vencedor: {winner}", True, "green")
            
            rect_win = text_win.get_rect(center=(screen_width/2, 100))
            screen.blit(text_win, rect_win)
            
            rect_name = text_name.get_rect(center=(screen_width/2, 180))
            screen.blit(text_name, rect_name)

            # Renderiza histórico do ranking
            text_rank = ranking_font.render("--- Histórico Recente ---", True, "white")
            screen.blit(text_rank, (screen_width/2 - 150, 250))
            
            y_pos = 300
            for line in ranking_list:
                line_surf = ranking_font.render(line, True, "gray")
                rect_line = line_surf.get_rect(center=(screen_width/2, y_pos))
                screen.blit(line_surf, rect_line)
                y_pos += 40

        else:
            # Tela de Jogo Normal
            # Extrai posições do pacote recebido
            ball_rect = game_state['ball']
            player_rect = game_state['player']
            cpu_rect = game_state['cpu']
            
            # Renderiza Placar
            cpu_text = font.render(str(scores[0]), True, "white")
            player_text = font.render(str(scores[1]), True, "white")
            screen.blit(cpu_text, (screen_width/4, 20))
            screen.blit(player_text, (3*screen_width/4, 20))

            # Renderiza Objetos
            pygame.draw.aaline(screen, 'white', (screen_width/2, 0), (screen_width/2, screen_height))
            pygame.draw.ellipse(screen, 'white', ball_rect)
            pygame.draw.rect(screen, 'white', cpu_rect)
            pygame.draw.rect(screen, 'white', player_rect)
        
        pygame.display.update()

    except Exception as e:
        print(f"Erro durante execução: {e}")
        break

client_socket.close()