# 🪐 Pong Multiplayer - Galactic Arcade Edition

> Uma recriação moderna do clássico Pong com suporte a Multiplayer Online, LAN automática e persistência de dados.

![Status](https://img.shields.io/badge/Status-Finalizado-green)
![Python](https://img.shields.io/badge/Python-3.x-blue)
![Network](https://img.shields.io/badge/Network-TCP%2FUDP-orange)

## 🎮 Como Jogar (Guia Rápido)

Este jogo foi projetado para ser fácil de iniciar. Siga os passos abaixo:

### 1. Início Rápido (Automação)
Para rodar sem complicações, basta executar o arquivo de lote:
* **Windows:** Clique duas vezes em `start_game.bat`.
    * *Este script verifica se você tem Python e Pygame instalados. Se não tiver, ele instala automaticamente e abre o jogo.*

---

### 2. O Menu Inicial
Ao abrir o jogo, você encontrará um terminal interativo.
1.  **Digite seu Nickname:** Escolha um nome de até 8 letras (ex: `WAGNER`).
2.  **Escolha o Modo de Conexão:**
    * `[1] Rede Local (Automático)`: O jogo usa um "sonar" (UDP Broadcast) para encontrar o servidor sozinho na sua rede Wi-Fi/Cabo.
    * `[2] Online (Manual)`: Ideal para jogar via internet (usando Ngrok). Você precisará digitar o endereço que o Host te mandar.
    * `[3] Localhost`: Para testar sozinho no mesmo computador.

---

### 3. Regras da Partida
O jogo segue regras competitivas estilo Vôlei/Tênis:
* **Vitória:** Ganha quem chegar a **5 Pontos** primeiro.
* **Diferença de 2:** É necessário abrir 2 pontos de vantagem para fechar o jogo (ex: se estiver 4x4, o jogo vai a 6, e assim por diante).
* **Rally:** Quanto mais a bola troca de lado sem cair, mais o contador de "Rally" sobe e muda de cor (Branco -> Amarelo -> Vermelho).
* **Velocidade Progressiva:** A cada batida na raquete, a bola fica 10% mais rápida.

---

### 4. Controles

| Ação | Tecla |
| :--- | :---: |
| **Mover Cima** | ⬆️ Seta Direcional Cima |
| **Mover Baixo** | ⬇️ Seta Direcional Baixo |
| **Parar** | Soltar a tecla |
| **Reiniciar Jogo** | **ESPAÇO** (Apenas na tela de vitória) |
| **Sair** | Fechar a janela |

---

## 🌍 Jogando Online (Via Internet)

Para jogar com amigos em outras casas, utilizamos o **Ngrok** para criar um túnel seguro.

**Passo A: O Host (Quem cria o jogo)**
1.  Inicie o `server.py` (ou use o `.bat`).
2.  Abra o Ngrok e digite: `ngrok tcp 5555`.
3.  Copie o endereço gerado (ex: `0.tcp.sa.ngrok.io:12345`).
4.  Envie para o amigo.

**Passo B: O Cliente (Seu amigo)**
1.  Abra o jogo e escolha a opção **[2] Online**.
2.  Cole o endereço que o Host enviou.
3.  Pronto!

---

## 🛠️ Tecnologias e Funcionalidades

Este projeto vai além do básico, implementando conceitos avançados de Redes e Engenharia de Software:

* **📡 Arquitetura Híbrida (TCP + UDP):**
    * **TCP (5555):** Garante a sincronização perfeita da física e placar.
    * **UDP (5556):** Usado para *Service Discovery*. O cliente "grita" na rede local perguntando onde está o servidor, eliminando a necessidade de configurar IPs manualmente em LAN.
* **💾 Persistência (Leaderboard):**
    * O servidor mantém um arquivo `ranking.txt`.
    * Ao final de cada partida, um "Hall of Fame" é exibido mostrando os 5 jogadores com mais vitórias na história do servidor.
* **🛡️ Modo Espectador:**
    * O servidor suporta múltiplas conexões. Se um 3º usuário entrar, ele é automaticamente colocado como **Espectador** (assiste à partida em tempo real, mas seus inputs são bloqueados).
* **💻 Código Profissional:**
    * Refatorado com **Orientação a Objetos (POO)**.
    * Uso de `Pickle` para serialização complexa de dados.
    * Multithreading para gerenciar física e rede simultaneamente.

---

## 📂 Estrutura de Arquivos

* `server.py`: O "cérebro". Gerencia física, regras, ranking e conexões.
* `client.py`: A "interface". Gerencia input do usuário e renderização gráfica.
* `start_game.bat`: Script de automação para Windows.
* `assets/`: Contém os sprites (bola e background).

---

## 👨‍💻 Autor

Desenvolvido para a disciplina de **Redes de Computadores**.git add README.md