import socket
import threading
import pygame
import pickle 
import random
from collections import Counter 
from datetime import datetime 

class PongServer:
    def __init__(self):
        self.W, self.H = 1280, 700
        self.TCP_PORT, self.UDP_PORT = 5555, 5556
        self.clients = []
        self.client_nicks = {} 
        
        self.ball = pygame.Rect(self.W//2, self.H//2, 50, 50)
        self.players = [pygame.Rect(0, self.H//2, 20, 100), pygame.Rect(self.W-20, self.H//2, 20, 100)] 
        self.speeds = [0, 0]
        self.score = [0, 0]
        self.ball_vel = [8, 8]
        self.winner = None
        self.ranking = []
        self.rally = 0 
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(('0.0.0.0', self.TCP_PORT))
        self.sock.listen(2)
        print(f"[INFO] Servidor Online na porta TCP {self.TCP_PORT}")

        # Carrega o ranking inicial ao ligar
        self.update_leaderboard()

    def discovery_listener(self):
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
        self.ball_vel = [8 * random.choice([1,-1]), 8 * random.choice([1,-1])]
        self.rally = 0
    
    def physics_loop(self):
        clock = pygame.time.Clock()
        while True:
            if len(self.clients) >= 2 and not self.winner:
                self.ball.x += self.ball_vel[0]
                self.ball.y += self.ball_vel[1]

                if self.ball.top <= 0 or self.ball.bottom >= self.H: self.ball_vel[1] *= -1
                
                if self.ball.colliderect(self.players[0]) or self.ball.colliderect(self.players[1]):
                    self.ball_vel[0] *= -1.1
                    self.ball_vel[1] *= 1.1
                    self.ball_vel = [max(-18, min(v, 18)) for v in self.ball_vel]
                    self.rally += 1

                # Pontuação (Passa o ID do jogador que fez ponto)
                if self.ball.left <= 0: self.score_point(1) # P1 (Dir) fez ponto
                if self.ball.right >= self.W: self.score_point(0) # CPU/P2 (Esq) fez ponto

                for i in range(2):
                    self.players[i].y += self.speeds[i]
                    self.players[i].clamp_ip(pygame.Rect(0, 0, self.W, self.H))

            state = {
                'ball': self.ball, 'cpu': self.players[0], 'player': self.players[1],
                'score': self.score, 'winner': self.winner, 'ranking': self.ranking,
                'status': "PLAYING" if len(self.clients) >= 2 else "WAITING",
                'rally': self.rally
            }
            data = pickle.dumps(state)
            
            for c in self.clients[:]:
                try: c.send(data)
                except: self.clients.remove(c)
            
            clock.tick(60)

    def score_point(self, player_idx):
        self.score[player_idx] += 1
        self.reset_ball()
        pontos_p1 = self.score[0]
        pontos_p2 = self.score[1]
        diff = abs(pontos_p1 - pontos_p2)
        
        # Lógica de Vitória 
        if self.score[player_idx] >= 5 and diff >= 2:
            winner_id = 0 if player_idx == 1 else 1
            winner_name = self.client_nicks.get(winner_id, f"Player {winner_id+1}")
            self.winner = winner_name
            self.save_win(winner_name)

    def save_win(self, name):
        """ Salva a vitória no arquivo """
        try:
            with open("ranking.txt", "a") as f:
                f.write(f"{name}\n") # Salva apenas o nome para facilitar contagem
            self.update_leaderboard()
        except: pass

    def update_leaderboard(self):
        """ Lê o arquivo, conta vitórias e gera o TOP 5 """
        try:
            with open("ranking.txt", "r") as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]
            
            if not lines:
                self.ranking = ["Nenhum registro ainda."]
                return

            # Conta quantas vezes cada nome aparece
            counts = Counter(lines)
            # Pega os 5 mais comuns
            top5 = counts.most_common(5)
            
            # Formata para exibição
            self.ranking = ["=== HALL OF FAME ==="]
            for i, (name, wins) in enumerate(top5):
                self.ranking.append(f"{i+1}. {name} - {wins} vitorias")
                
        except: 
            self.ranking = ["Erro ao ler ranking."]

    def handle_client(self, conn, p_id):
        cmd_map = {"UP": -8, "DOWN": 8, "STOP": 0}
        
        # Handshake do Nickname 
        try:
            # O primeiro pacote recebido deve ser o Nickname
            initial_msg = conn.recv(1024).decode()
            if initial_msg.startswith("NICK:"):
                nickname = initial_msg.split(":")[1]
                self.client_nicks[p_id] = nickname[:10] # Limita a 10 letras
                print(f"[GAME] Jogador {p_id} definiu nick: {nickname}")
            else:
                self.client_nicks[p_id] = f"Player {p_id+1}"
        except:
            self.client_nicks[p_id] = f"Player {p_id+1}"
        # -----------------------------------

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
        threading.Thread(target=self.discovery_listener, daemon=True).start()
        threading.Thread(target=self.physics_loop, daemon=True).start()
        
        while True:
            conn, addr = self.sock.accept()
            print(f"[NET] Nova conexao: {addr}")
            self.clients.append(conn)
            threading.Thread(target=self.handle_client, args=(conn, len(self.clients)-1)).start()

if __name__ == '__main__':
    PongServer().start()