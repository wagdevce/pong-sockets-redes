import pygame
import socket
import pickle 

# Inicialização Gráfica
pygame.init()
screen_width = 1280
screen_height = 700
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Pong Multiplayer")

clock = pygame.time.Clock()
# Definição de fontes para diferentes estados do jogo
font = pygame.font.Font(None, 100)
victory_font = pygame.font.Font(None, 80)
ranking_font = pygame.font.Font(None, 40)
lobby_font = pygame.font.Font(None, 60)

# CARREGAMENTO DE SPRITES
try:
    # 1. Carrega a imagem da pasta assets
    original_ball_img = pygame.image.load('assets/ball.png')
    original_bg_img = pygame.image.load('assets/background.png')
    
    # 2. Redimensiona para 50x50 (O tamanho que definimos no server.py)
    # O .convert_alpha() ajuda a manter a transparência e melhora a velocidade
    ball_sprite = pygame.transform.scale(original_ball_img, (50, 50)).convert_alpha()
    bg_sprite = pygame.transform.scale(original_bg_img, (screen_width, screen_height)).convert()
    print("Background carregado!")
    has_background = True
    
    print("Sprite da bola carregado com sucesso!")
    using_sprites = True
except Exception as e:
    print("Aviso: 'assets/background.png' não encontrado. Usando fundo preto.")
    has_background = False
    print(f"Aviso: Não foi possível carregar 'bola.png'. Usando bolinha branca padrão. Erro: {e}")
    using_sprites = False

# Configuração de Rede 
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    # Conexão TCP com o servidor (IP local hardcoded para testes)
    client_socket.connect(('127.0.0.1', 5555))
    print("Conectado ao servidor com sucesso.")
except Exception as e:
    print(f"Falha na conexão: {e}")
    exit()

# Loop Principal 
while True:
    # 1. Captura de Eventos (Input do Usuário)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        
        # Envio de comandos de movimentação via socket
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                client_socket.send("UP".encode())
            if event.key == pygame.K_DOWN:
                client_socket.send("DOWN".encode())
        
        # Envio de comando de parada ao soltar a tecla
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                client_socket.send("STOP".encode())

    try:
        # 2. Recebimento e Deserialização de Dados
        data = client_socket.recv(4096) 
        if not data: break

        game_state = pickle.loads(data)
        
        # Extração das variáveis de estado do pacote recebido
        status = game_state.get('status', 'PLAYING') 
        winner = game_state.get('winner')
        scores = game_state['score'] 
        ranking_list = game_state.get('ranking', [])

        # 1. DESENHA O FUNDO (A primeira camada)
        if has_background and using_sprites:
            # Desenha a imagem do espaço na posição (0,0)
            screen.blit(bg_sprite, (0,0))
        else:
            # Se não tiver imagem, pinta de preto (fallback)
            screen.fill('black')
        # 3. Renderização Condicional (Máquina de Estados Visual)
        
        if status == "WAITING":
            # Estado: LOBBY (Aguardando segundo jogador)
            text_wait = lobby_font.render("Aguardando Oponente...", True, "cyan")
            rect_wait = text_wait.get_rect(center=(screen_width/2, screen_height/2))
            
            text_p1 = ranking_font.render("Conectado. Aguardando início da partida.", True, "gray")
            rect_p1 = text_p1.get_rect(center=(screen_width/2, screen_height/2 + 50))

            screen.blit(text_wait, rect_wait)
            screen.blit(text_p1, rect_p1)
        
        elif winner:
            # Estado: FIM DE JOGO (Exibe vencedor e ranking)
            text_win = victory_font.render(f"FIM DE JOGO!", True, "yellow")
            text_name = victory_font.render(f"Vencedor: {winner}", True, "green")
            
            rect_win = text_win.get_rect(center=(screen_width/2, 100))
            screen.blit(text_win, rect_win)
            
            rect_name = text_name.get_rect(center=(screen_width/2, 180))
            screen.blit(text_name, rect_name)

            text_rank = ranking_font.render("--- Histórico Recente ---", True, "white")
            screen.blit(text_rank, (screen_width/2 - 150, 250))
            
            y_pos = 300
            for line in ranking_list:
                line_surf = ranking_font.render(line, True, "gray")
                rect_line = line_surf.get_rect(center=(screen_width/2, y_pos))
                screen.blit(line_surf, rect_line)
                y_pos += 40

        else:
            # Estado: JOGO EM ANDAMENTO (Renderização padrão)
            ball_rect = game_state['ball']
            player_rect = game_state['player']
            cpu_rect = game_state['cpu']
            
            cpu_text = font.render(str(scores[0]), True, "white")
            player_text = font.render(str(scores[1]), True, "white")
            screen.blit(cpu_text, (screen_width/4, 20))
            screen.blit(player_text, (3*screen_width/4, 20))


            pygame.draw.aaline(screen, 'white', (screen_width/2, 0), (screen_width/2, screen_height))
            if using_sprites:
                # Desenha a IMAGEM (Sprite)
                screen.blit(ball_sprite, ball_rect)
            else:
                # Desenha a FORMA (Caso a imagem tenha falhado)
                pygame.draw.ellipse(screen, 'white', ball_rect)
            pygame.draw.rect(screen, 'white', cpu_rect)
            pygame.draw.rect(screen, 'white', player_rect)
        
        pygame.display.update()

    except Exception as e:
        print(f"Erro de execução: {e}")
        break

client_socket.close()