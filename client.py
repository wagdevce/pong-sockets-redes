import pygame 
import socket 
import pickle 
import os 
import time

# Configurações Globais
W, H = 1280, 700
TCP_PORT, UDP_PORT = 5555, 5556

def get_user_info():
    """ Menu inicial para Nickname e Conexão """
    os.system('cls' if os.name == 'nt' else 'clear')
    print("==================================================")
    print(" 🏓 PONG MULTIPLAYER - GALACTIC ARCADE 🏓")
    print("==================================================")
    
    # Pede o Nickname
    while True:
        nick = input("Digite seu NICK (Max 8 letras): ").strip().upper()
        if 0 < len(nick) <= 8: break
        print("Nome invalido! Tente de novo.")
    
    print("\nSelecione o modo de conexao:")
    print("[1] Rede Local (Discovery Automatico)")
    print("[2] Endereco Remoto (IP Manual / Ngrok)")
    print("[3] Localhost (Teste Loopback)")
    
    choice = input("\n> Opcao [1-3]: ").strip()
    
    ip_destino = '127.0.0.1'
    
    if choice == '1':
        print("\n[INFO] Buscando servidor na rede...")
        udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        udp.settimeout(20)
        try:
            udp.sendto(b"DISCOVER_PONG_SERVER", ('<broadcast>', UDP_PORT))
            start = time.time()
            found = False
            while time.time() - start < 20:
                try:
                    msg, addr = udp.recvfrom(1024)
                    if msg == b"PONG_HERE": 
                        print(f"[SUCESSO] Servidor encontrado: {addr[0]}")
                        ip_destino = addr[0]
                        found = True
                        time.sleep(1)
                        break
                except: pass
            if not found:
                print("[AVISO] Nao encontrado. Indo para manual.")
                choice = '2'
        except: pass

    if choice == '2':
        print("\nDigite o IP ou Ngrok (ex: 0.tcp.sa.ngrok.io:12345)")
        val = input("> Host: ").strip()
        if val: ip_destino = val

    return nick, ip_destino

def load_asset(path, size=None):
    try:
        img = pygame.image.load(path)
        if size: img = pygame.transform.scale(img, size)
        return img.convert_alpha() if size else img.convert()
    except: return None

# Inicialização 
nickname, server_ip = get_user_info()

pygame.init()
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption(f"Pong - Jogador: {nickname}")
clock = pygame.time.Clock()

sprites = {
    'ball': load_asset('assets/ball.png', (50, 50)),
    'bg': load_asset('assets/background.png', (W, H))
}
fonts = {
    'big': pygame.font.Font(None, 100),
    'med': pygame.font.Font(None, 60),
    'small': pygame.font.Font(None, 40)
}

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    port = 5555
    if server_ip != '127.0.0.1' and ':' in server_ip:
         parts = server_ip.split(':')
         server_ip = parts[0]
         port = int(parts[1])
         
    sock.connect((server_ip, port))
    
    #  Envia o Nickname assim que conecta 
    sock.send(f"NICK:{nickname}".encode())
   
    
except Exception as e:
    print(f"[ERRO] Falha na conexao: {e}"); input(); exit()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP: sock.send(b"UP")
            if event.key == pygame.K_DOWN: sock.send(b"DOWN")
            if event.key == pygame.K_SPACE: sock.send(b"RESET")
        if event.type == pygame.KEYUP and event.key in [pygame.K_UP, pygame.K_DOWN]:
            sock.send(b"STOP")

    try:
        data = sock.recv(4096)
        if not data: break
        state = pickle.loads(data)
    except: break

    if sprites['bg']: screen.blit(sprites['bg'], (0,0))
    else: screen.fill('black')

    if state['status'] == "WAITING":
        text = fonts['med'].render("Aguardando Oponente...", True, "cyan")
        screen.blit(text, text.get_rect(center=(W//2, H//2)))
        
        # Mostra o Nick no Lobby
        t_nick = fonts['small'].render(f"Voce e: {nickname}", True, "white")
        screen.blit(t_nick, t_nick.get_rect(center=(W//2, H//2 + 50)))
    
    elif state['winner']:
        texts = [
            (fonts['big'].render("FIM DE JOGO!", True, "yellow"), 80),
            (fonts['big'].render(f"Venceu: {state['winner']}", True, "green"), 160),
            (fonts['small'].render("Espaco p/ Reiniciar", True, "white"), H-50)
        ]
        for t, y in texts: screen.blit(t, t.get_rect(center=(W//2, y)))
        
        # Hall of Fame 
        for i, line in enumerate(state['ranking']):
            color = "yellow" if i == 0 else "white" # Título em amarelo
            if i > 0: color = "gray" # Itens em cinza
            
            t = fonts['small'].render(line, True, color)
            screen.blit(t, t.get_rect(center=(W//2, 250 + i*40)))
    else:
        screen.blit(fonts['big'].render(str(state['score'][0]), True, "white"), (W//4, 20))
        screen.blit(fonts['big'].render(str(state['score'][1]), True, "white"), (3*W//4, 20))
        
        rally_val = state.get('rally', 0)
        if rally_val > 0:
            color = "white"
            if rally_val > 5: color = "yellow"
            if rally_val > 10: color = "red"
            t_rally = fonts['small'].render(f"RALLY: {rally_val}", True, color)
            screen.blit(t_rally, t_rally.get_rect(center=(W//2, 50)))

        if sprites['ball']: screen.blit(sprites['ball'], state['ball'])
        else: pygame.draw.ellipse(screen, 'white', state['ball'])
        
        pygame.draw.rect(screen, 'white', state['cpu'])
        pygame.draw.rect(screen, 'white', state['player'])

    pygame.display.update()
    clock.tick(60)