import pygame
import socket
import pickle 
import os

#  CONFIGURAÇÃO INICIAL DE CONEXÃO
# Limpa o terminal para facilitar a leitura
os.system('cls' if os.name == 'nt' else 'clear')

print("="*50)
print("       BEM-VINDO AO PONG MULTIPLAYER")
print("="*50)
print("Para jogar LOCAL (sozinho), apenas aperte ENTER.")
print("Para jogar ONLINE, cole o endereço do Ngrok (ex: 0.tcp.sa.ngrok.io:12345).")
print("-" * 50)

server_ip = input("Digite o IP do Servidor: ").strip()

# Definição de IP e Porta baseada na entrada
if not server_ip:
    server_ip = '127.0.0.1'
    port = 5555
    print(f"-> Modo Local selecionado: {server_ip}:{port}")
else:
    # Tratamento para endereços do Ngrok (host:porta)
    if ':' in server_ip:
        try:
            ip_part, port_part = server_ip.split(':')
            server_ip = ip_part
            port = int(port_part)
            print(f"-> Modo Online selecionado: {server_ip}:{port}")
        except:
            print("Formato inválido! Usando padrão local.")
            server_ip = '127.0.0.1'
            port = 5555
    else:
        port = 5555

print("="*50)
print("Iniciando o jogo...")

# Inicialização Gráfica
pygame.init()
screen_width = 1280
screen_height = 700
screen = pygame.display.set_mode((screen_width, screen_height))
# Atualiza o título da janela para mostrar onde estamos conectados
pygame.display.set_caption(f"Pong Multiplayer - Conectado a {server_ip}:{port}")

clock = pygame.time.Clock()

# Definição de fontes para diferentes estados do jogo
font = pygame.font.Font(None, 100)
victory_font = pygame.font.Font(None, 80)
ranking_font = pygame.font.Font(None, 40)
lobby_font = pygame.font.Font(None, 60)
restart_font = pygame.font.Font(None, 50)

# CARREGAMENTO DE SPRITES
using_sprites = False
has_background = False

try:
    # 1. Carrega a imagem da pasta assets
    try:
        original_ball_img = pygame.image.load('assets/ball.png')
        # Redimensiona para 50x50 (O tamanho que definimos no server.py)
        ball_sprite = pygame.transform.scale(original_ball_img, (50, 50)).convert_alpha()
        using_sprites = True
        print("Sprite da bola carregado com sucesso!")
    except Exception as e:
        print(f"Aviso: Não foi possível carregar 'bola.png'. Erro: {e}")

    # 2. Carrega o Background
    try:
        original_bg_img = pygame.image.load('assets/background.png')
        bg_sprite = pygame.transform.scale(original_bg_img, (screen_width, screen_height)).convert()
        has_background = True
        print("Background carregado!")
    except Exception as e:
        print(f"Aviso: 'assets/background.png' não encontrado. Usando fundo preto.")

except Exception as e:
    print(f"Erro geral assets: {e}")
    using_sprites = False

# Configuração de Rede 
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    # Conecta ao servidor usando as variáveis definidas no início (Local ou Ngrok)
    client_socket.connect((server_ip, port))
    print("Conectado ao servidor com sucesso.")
except Exception as e:
    print(f"Falha na conexão com {server_ip}:{port}")
    print(f"Erro detalhado: {e}")
    input("Pressione ENTER para sair...")
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
            
            # Só envia RESET se apertar ESPAÇO
            if event.key == pygame.K_SPACE:
                client_socket.send("RESET".encode())

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
            
            # Pisca o texto ou apenas mostra estático
            text_restart = restart_font.render("Pressione ESPAÇO para jogar novamente", True, "cyan")
            rect_restart = text_restart.get_rect(center=(screen_width/2, screen_height - 100))
            screen.blit(text_restart, rect_restart)

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