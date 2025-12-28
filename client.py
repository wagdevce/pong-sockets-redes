import pygame
import socket
import pickle 

# Configurações Visuais 
pygame.init()
screen_width = 1280
screen_height = 700
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Pong Multiplayer - Cliente")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 100)

# Conexão de Rede 
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    # Conecta ao servidor local (localhost)
    client_socket.connect(('127.0.0.1', 5555))
    print("Conectado ao servidor.")
except Exception as e:
    print(f"Erro ao conectar: {e}")
    exit()

# Loop Principal
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
            
        # Envio de Comandos (Input)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                client_socket.send("UP".encode())
            if event.key == pygame.K_DOWN:
                client_socket.send("DOWN".encode())
        
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                client_socket.send("STOP".encode())

    try:
        # 1. Recebimento do Estado do Jogo
        data = client_socket.recv(2048) 
        if not data:
            print("Conexão perdida.")
            break

        # 2. Deserialização (Bytes -> Dicionário)
        game_state = pickle.loads(data)
        
        # Recupera os objetos
        ball_rect = game_state['ball']
        player_rect = game_state['player'] # Raquete Direita
        cpu_rect = game_state['cpu']       # Raquete Esquerda
        scores = game_state['score'] 

        # 3. Renderização
        screen.fill('black')
        
        # Placar
        cpu_text = font.render(str(scores[0]), True, "white") # Pontos Esq
        player_text = font.render(str(scores[1]), True, "white") # Pontos Dir
        screen.blit(cpu_text, (screen_width/4, 20))
        screen.blit(player_text, (3*screen_width/4, 20))

        # Desenha Elementos
        pygame.draw.aaline(screen, 'white', (screen_width/2, 0), (screen_width/2, screen_height))
        pygame.draw.ellipse(screen, 'white', ball_rect)
        pygame.draw.rect(screen, 'white', cpu_rect)
        pygame.draw.rect(screen, 'white', player_rect)
        
        pygame.display.update()

    except Exception as e:
        print(f"Erro: {e}")
        break

client_socket.close()