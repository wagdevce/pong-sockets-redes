import pygame
import socket
import pickle 

# Configurações Visuais e Inicialização
pygame.init()
screen_width = 1280
screen_height = 700
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Pong Multiplayer - Cliente TCP")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 100)

# Conexão de Rede
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    # Conecta ao IP local (localhost). Mude para o IP do servidor se estiver em outra máquina.
    client_socket.connect(('127.0.0.1', 5555))
    print("Conectado ao servidor com sucesso.")
except Exception as e:
    print(f"Erro ao conectar ao servidor: {e}")
    exit()

# Loop Principal do Cliente
while True:
    # Tratamento de eventos (Input e Fechamento de janela)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        # Envia comandos para o servidor quando teclas são pressionadas
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                client_socket.send("UP".encode()) # Envia "UP" em bytes
            if event.key == pygame.K_DOWN:
                client_socket.send("DOWN".encode()) # Envia "DOWN" em bytes
        
        # Envia comando de PARAR quando a tecla é solta
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                client_socket.send("STOP".encode())
    

    try:
        # 1. Recebimento de Dados
        # O buffer de 2048 bytes é suficiente para o estado atual do jogo.
        data = client_socket.recv(2048) 
        
        if not data:
            print("Conexão perdida com o servidor.")
            break

        # 2. Deserialização
        game_state = pickle.loads(data)
        
        # Extrai os objetos do estado do jogo
        ball_rect = game_state['ball']
        player_rect = game_state['player']
        cpu_rect = game_state['cpu']
        scores = game_state['score'] 

        # 3. Renderização (Desenho na tela)
        screen.fill('black')
        
        # Renderiza o placar
        cpu_text = font.render(str(scores[0]), True, "white")
        player_text = font.render(str(scores[1]), True, "white")
        screen.blit(cpu_text, (screen_width/4, 20))
        screen.blit(player_text, (3*screen_width/4, 20))

        # Renderiza os elementos do jogo nas posições informadas pelo servidor
        pygame.draw.aaline(screen, 'white', (screen_width/2, 0), (screen_width/2, screen_height))
        pygame.draw.ellipse(screen, 'white', ball_rect)
        pygame.draw.rect(screen, 'white', cpu_rect)
        pygame.draw.rect(screen, 'white', player_rect)
        
        pygame.display.update()

    except Exception as e:
        print(f"Erro durante a execução: {e}")
        break

client_socket.close()