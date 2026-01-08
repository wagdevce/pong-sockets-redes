import pygame, socket, pickle, os, time

# Configurações Globais
W, H = 1280, 700
TCP_PORT, UDP_PORT = 5555, 5556

def find_server():
    """ Menu inicial para escolher o modo de conexão """
    os.system('cls' if os.name == 'nt' else 'clear')
    print("==================================================")
    print(" PONG MULTIPLAYER - CLIENTE")
    print("==================================================")
    print("Selecione o modo de conexao:")
    print("[1] Rede Local (Discovery Automatico)")
    print("[2] Endereco Remoto (IP Manual / Ngrok)")
    print("[3] Localhost (Teste Loopback)")
    
    choice = input("\n> Opcao [1-3]: ").strip()
    
    # OPÇÃO 1: Busca Automática (UDP)
    if choice == '1':
        print("\n[INFO] Iniciando varredura UDP na porta 5556...")
        udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        udp.settimeout(20)
        try:
            udp.sendto(b"DISCOVER_PONG_SERVER", ('<broadcast>', UDP_PORT))
            start = time.time()
            while time.time() - start < 20:
                msg, addr = udp.recvfrom(1024)
                if msg == b"PONG_HERE": 
                    print(f"[SUCESSO] Servidor encontrado: {addr[0]}")
                    time.sleep(1)
                    return addr[0]
        except: pass
        print("[AVISO] Nenhum servidor encontrado. Alternando para manual.")
        choice = '2'

    # OPÇÃO 2: Manual (Ngrok)
    if choice == '2':
        print("\nDigite o endereco IP ou Host do Ngrok (ex: 0.tcp.sa.ngrok.io:12345)")
        ip = input("> Host: ").strip()
        return ip if ip else '127.0.0.1'

    # OPÇÃO 3: Padrão (Localhost)
    return '127.0.0.1'

def load_asset(path, size=None):
    """ Helper para carregar imagens com segurança """
    try:
        img = pygame.image.load(path)
        if size: img = pygame.transform.scale(img, size)
        return img.convert_alpha() if size else img.convert()
    except: return None

# --- Inicialização ---
server_ip = find_server()
pygame.init()
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption(f"Pong Client - Connected to {server_ip}")
clock = pygame.time.Clock()

# Assets (Dicionários para organização)
sprites = {
    'ball': load_asset('assets/ball.png', (50, 50)),
    'bg': load_asset('assets/background.png', (W, H))
}
fonts = {
    'big': pygame.font.Font(None, 100),
    'med': pygame.font.Font(None, 60),
    'small': pygame.font.Font(None, 40)
}

# Conexão TCP
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    port = 5555
    # Se for ngrok (tem ':' e não é localhost), tenta extrair a porta
    if server_ip != '127.0.0.1' and ':' in server_ip:
         parts = server_ip.split(':')
         server_ip = parts[0]
         port = int(parts[1])
         
    sock.connect((server_ip, port))
except Exception as e:
    print(f"[ERRO] Falha na conexao: {e}"); input(); exit()

# --- Game Loop ---
running = True
while running:
    # 1. Inputs e Eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP: sock.send(b"UP")
            if event.key == pygame.K_DOWN: sock.send(b"DOWN")
            if event.key == pygame.K_SPACE: sock.send(b"RESET")
            
        if event.type == pygame.KEYUP and event.key in [pygame.K_UP, pygame.K_DOWN]:
            sock.send(b"STOP")

    # 2. Rede (Receber Estado)
    try:
        data = sock.recv(4096)
        if not data: break
        state = pickle.loads(data)
    except: break

    # 3. Renderização
    if sprites['bg']: screen.blit(sprites['bg'], (0,0))
    else: screen.fill('black')

    if state['status'] == "WAITING":
        text = fonts['med'].render("Aguardando Oponente...", True, "cyan")
        screen.blit(text, text.get_rect(center=(W//2, H//2)))
    
    elif state['winner']:
        # Tela de Vitória
        texts = [
            (fonts['big'].render("FIM DE JOGO!", True, "yellow"), 100),
            (fonts['big'].render(f"Vencedor: {state['winner']}", True, "green"), 180),
            (fonts['small'].render("Espaco p/ Reiniciar", True, "white"), H-100)
        ]
        for t, y in texts: screen.blit(t, t.get_rect(center=(W//2, y)))
        
        # Histórico
        for i, line in enumerate(state['ranking']):
            t = fonts['small'].render(line, True, "gray")
            screen.blit(t, t.get_rect(center=(W//2, 300 + i*40)))
    else:
        # Partida Rodando
        # Placar
        screen.blit(fonts['big'].render(str(state['score'][0]), True, "white"), (W//4, 20))
        screen.blit(fonts['big'].render(str(state['score'][1]), True, "white"), (3*W//4, 20))
        
        # Bola
        if sprites['ball']: screen.blit(sprites['ball'], state['ball'])
        else: pygame.draw.ellipse(screen, 'white', state['ball'])
        
        # Raquetes
        pygame.draw.rect(screen, 'white', state['cpu'])
        pygame.draw.rect(screen, 'white', state['player'])

    pygame.display.update()
    clock.tick(60)