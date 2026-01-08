import socket
import threading
import pygame
import pickle 
import random
from datetime import datetime 

class PongServer:
    def __init__(self):
        # Configurações
        self.W, self.H = 1280, 700
        self.TCP_PORT, self.UDP_PORT = 5555, 5556
        self.clients = []
        
        # Estado do Jogo
        self.ball = pygame.Rect(self.W//2, self.H//2, 50, 50)
        # players[0] é CPU (Esq), players[1] é Player (Dir)
        self.players = [pygame.Rect(0, self.H//2, 20, 100), pygame.Rect(self.W-20, self.H//2, 20, 100)] 
        self.speeds = [0, 0] # Velocidade vertical dos jogadores
        self.score = [0, 0]
        self.ball_vel = [6, 6]
        self.winner = None
        self.ranking = []
        
        # Inicializa socket TCP
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(('0.0.0.0', self.TCP_PORT))
        self.sock.listen(2)
        print(f"[INFO] Servidor Online na porta TCP {self.TCP_PORT}")

    def discovery_listener(self):
        # Escuta UDP para descoberta automática
        udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp.bind(('0.0.0.0', self.UDP_PORT))
        print(f"[INFO] Discovery Service (UDP) ativo na porta {self.UDP_PORT}")
        while True:
            try:
                msg, addr = udp.recvfrom(1024)
                if msg == b"DISCOVER_PONG_SERVER": udp.sendto(b"PONG_HERE", addr)
            except: pass

    def reset_ball(self):
        self.ball.center = (self.W//2, self.H//2)
        # Reinicia com direção aleatória
        self.ball_vel = [6 * random.choice([1,-1]), 6 * random.choice([1,-1])]

    def physics_loop(self):
        clock = pygame.time.Clock()
        while True:
            if len(self.clients) >= 2 and not self.winner:
                # Movimento Bola
                self.ball.x += self.ball_vel[0]
                self.ball.y += self.ball_vel[1]

                # Colisão Parede (Teto/Chão)
                if self.ball.top <= 0 or self.ball.bottom >= self.H: self.ball_vel[1] *= -1
                
                # Colisão Raquetes (Com aceleração progressiva)
                if self.ball.colliderect(self.players[0]) or self.ball.colliderect(self.players[1]):
                    self.ball_vel[0] *= -1.1
                    self.ball_vel[1] *= 1.1
                    # Limita velocidade máxima (Clamp)
                    self.ball_vel = [max(-15, min(v, 15)) for v in self.ball_vel]

                # Pontuação
                if self.ball.left <= 0: self.score_point(1, "Jogador 1 (Dir)")
                if self.ball.right >= self.W: self.score_point(0, "Jogador 2 (Esq)")

                # Movimento Jogadores
                for i in range(2):
                    self.players[i].y += self.speeds[i]
                    self.players[i].clamp_ip(pygame.Rect(0, 0, self.W, self.H))

            # Broadcast (Envia estado para todos)
            state = {
                'ball': self.ball, 'cpu': self.players[0], 'player': self.players[1],
                'score': self.score, 'winner': self.winner, 'ranking': self.ranking,
                'status': "PLAYING" if len(self.clients) >= 2 else "WAITING"
            }
            data = pickle.dumps(state)
            
            # Envia para a lista de clientes
            for c in self.clients[:]:
                try: c.send(data)
                except: self.clients.remove(c)
            
            clock.tick(60)

    def score_point(self, player_idx, name):
        self.score[player_idx] += 1
        self.reset_ball()
        if self.score[player_idx] >= 5:
            self.winner = name
            self.save_ranking(name)

    def save_ranking(self, name):
        try:
            with open("ranking.txt", "a") as f:
                f.write(f"{datetime.now().strftime('%d/%m %H:%M')} - {name}\n")
            with open("ranking.txt", "r") as f: 
                self.ranking = [x.strip() for x in f.readlines()[-5:]]
        except: self.ranking = []

    def handle_client(self, conn, p_id):
        # Mapa de comandos para velocidade
        cmd_map = {"UP": -6, "DOWN": 6, "STOP": 0}
        while True:
            try:
                req = conn.recv(1024).decode()
                if not req: break
                
                if req == "RESET": 
                    self.score = [0,0]; self.winner = None; self.reset_ball()
                elif self.winner is None and req in cmd_map:
                    target_idx = 1 if p_id == 0 else 0
                    self.speeds[target_idx] = cmd_map[req]
            except: break
        conn.close()

    def start(self):
        # Inicia threads em background (daemon)
        threading.Thread(target=self.discovery_listener, daemon=True).start()
        threading.Thread(target=self.physics_loop, daemon=True).start()
        
        while True:
            conn, addr = self.sock.accept()
            print(f"[NET] Nova conexao estabelecida: {addr}")
            self.clients.append(conn)
            threading.Thread(target=self.handle_client, args=(conn, len(self.clients)-1)).start()

if __name__ == '__main__':
    PongServer().start()