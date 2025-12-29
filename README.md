# 🏓 Pong Multiplayer - Galactic Edition

> Um jogo multiplayer em tempo real desenvolvido em Python, utilizando arquitetura Cliente-Servidor (TCP Sockets) e Pygame.

![Status](https://img.shields.io/badge/Status-Finalizado-green)
![Python](https://img.shields.io/badge/Python-3.x-blue)
![Lib](https://img.shields.io/badge/Lib-Pygame-yellow)

## 🌌 Sobre o Projeto

Este projeto é uma releitura moderna do clássico Pong, implementada com uma arquitetura de redes robusta. Diferente de jogos simples, este projeto utiliza um **Servidor Autoritativo**, garantindo que a física e as regras sejam processadas centralmente, prevenindo trapaças e dessincronização.

O jogo suporta partidas em **Rede Local (LAN)** e **Online (WAN)** através de tunelamento via Ngrok.

### ✨ Principais Funcionalidades

* **Multiplayer Real-Time:** Sincronização de posição e estados via Sockets TCP.
* **Física Progressiva:** A bola acelera 10% a cada rebatida, tornando o jogo dinâmico.
* **Conexão Híbrida:** Suporte para IP Local (`127.0.0.1`) ou IP Externo (Ngrok).
* **Persistência:** Ranking de vitórias salvo automaticamente em arquivo (`ranking.txt`).
* **Lobby System:** O jogo aguarda a conexão de dois jogadores antes de iniciar.
* **Arte Galáctica:** Sprites personalizados para bola e cenário espacial.
* **Auto-Instalação:** Script inteligente que instala as dependências automaticamente.

---

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3
* **Engine Gráfica:** Pygame
* **Rede:** Biblioteca nativa `socket` (TCP/IP)
* **Serialização:** Biblioteca `pickle` (Protocolo binário)
* **Concorrência:** `threading` para gerenciamento de múltiplos clientes.

---

## 📦 Instalação

Não é necessário ser um expert em Python para rodar! O cliente possui um sistema de **auto-instalação**.

1.  Certifique-se de ter o [Python](https://www.python.org/) instalado.
2.  Clone ou baixe este repositório.
3.  Execute o jogo. Se você não tiver o `pygame` instalado, o script baixará automaticamente na primeira execução.

---

## 🚀 Como Jogar

### 🏠 Opção 1: Modo Local (Teste Rápido)
Ideal para testar sozinho ou em rede LAN.

1.  Execute o script de automação:
    * Clique duas vezes em `start_game.bat` (Windows).
2.  Três janelas abrirão (1 Servidor + 2 Clientes).
3.  Nas janelas dos clientes, quando pedir o IP, apenas pressione **ENTER**.

### 🌍 Opção 2: Modo Online (Com um Amigo)
Para jogar com alguém em outra casa/cidade.

**Para o HOST (Você):**
1.  Inicie o servidor: `python server.py`.
2.  Abra o [Ngrok](https://ngrok.com/) e digite: `ngrok tcp 5555`.
3.  Copie o endereço gerado (ex: `0.tcp.sa.ngrok.io:12345`).
4.  Envie este endereço para seu amigo.
5.  Abra seu cliente, dê Enter (jogue localmente conectado ao seu server).

**Para o CLIENTE (Seu amigo):**
1.  Ele abre o `client.py`.
2.  Quando perguntar o IP, ele cola o endereço do Ngrok (ex: `0.tcp.sa.ngrok.io:12345`) e aperta Enter.

---

## 🎮 Controles

| Ação | Tecla |
| :--- | :---: |
| **Mover para Cima** | ⬆️ Seta Cima |
| **Mover para Baixo** | ⬇️ Seta Baixo |
| **Jogar Novamente** | Espaço (Na tela de vitória) |
| **Sair** | ESC ou Fechar Janela |

---

## 📂 Estrutura de Arquivos

```bash
/Pong-Multiplayer
│
├── server.py        # O Cérebro: Gerencia física, regras e conexões.
├── client.py        # O Visual: Renderiza o jogo e envia inputs.
├── start_game.bat   # Ferramenta: Script para abrir 3 terminais de uma vez.
├── ranking.txt      # Dados: Histórico de vitórias (gerado automaticamente).
├── README.md        # Documentação.
└── /assets          # Recursos Visuais
    ├── ball.png     # Sprite da bola
    └── background.png # Fundo galáctico