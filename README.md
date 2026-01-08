# 🪐 Pong Multiplayer - Galactic Arcade Edition

> Um sistema distribuído de jogo em tempo real utilizando Sockets (TCP/UDP), Arquitetura Cliente-Servidor e Persistência de Dados.

![Status](https://img.shields.io/badge/Status-Finalizado-green)
![Python](https://img.shields.io/badge/Python-3.x-blue)
![Lib](https://img.shields.io/badge/Lib-Pygame-yellow)
![Architecture](https://img.shields.io/badge/Architecture-Client--Server-red)

## 🌌 Sobre o Projeto

Este projeto é uma implementação avançada do clássico Pong, desenvolvida como requisito da disciplina de **Redes de Computadores**. 

O foco principal não é apenas a jogabilidade, mas a engenharia de redes por trás dela. O sistema utiliza uma **Arquitetura Autoritativa**, onde o servidor detém o estado global da física, prevenindo trapaças e garantindo sincronização entre clientes em diferentes redes.

### ✨ Diferenciais Técnicos

* **📡 Protocolo Híbrido (TCP + UDP):**
    * **TCP (Porta 5555):** Garante a entrega confiável do estado do jogo (posição da bola, placar).
    * **UDP (Porta 5556):** Utilizado para **Service Discovery**. O cliente realiza um *Broadcast* na rede local para encontrar o servidor automaticamente, sem necessidade de configurar IPs manualmente.
* **💾 Persistência e Leaderboard:** Sistema de "Hall of Fame" estilo Arcade. Os dados de vitórias são persistidos em arquivo (`ranking.txt`) e exibidos no final da partida.
* **🎭 Modo Espectador:** O servidor suporta múltiplas conexões. Se um 3º cliente se conectar, ele entra automaticamente como espectador (recebe o estado do jogo, mas não interfere nos controles).
* **🏎️ Física Progressiva & Rally:** A bola acelera a cada rebatida. Um contador de "Rally" visual indica a intensidade da troca de bolas.
* **🌍 Suporte WAN (Ngrok):** O cliente possui um parser inteligente para endereços do Ngrok, permitindo partidas via internet através de túneis HTTP/TCP.

---

## 🛠️ Arquitetura e Tecnologias

O código foi refatorado utilizando **Programação Orientada a Objetos (POO)** para melhor encapsulamento e manutenção.

* **Linguagem:** Python 3.
* **Bibliotecas:** `socket` (Networking), `threading` (Concorrência), `pickle` (Serialização de Objetos), `pygame` (Renderização).
* **Fluxo de Dados:**
    1. O **Cliente** envia inputs (Teclas UP/DOWN).
    2. O **Servidor** processa a física, colisão e regras (Vitória por 5 pontos + 2 de diferença).
    3. O **Servidor** serializa o objeto `GameState` com `pickle`.
    4. O **Broadcast** envia o estado atualizado para todos os clientes conectados (60 ticks/s).

---

## 📦 Instalação e Execução

O projeto conta com um script de automação para Windows (`.bat`) que gerencia dependências e execução.

### Pré-requisitos
* Python 3.x instalado e adicionado ao PATH.

### 🚀 Como Rodar (Modo Automático)

1. Clone o repositório.
2. Execute o arquivo **`start_game.bat`**.
    * Ele verificará se o `pygame` está instalado (e instalará se necessário).
    * Iniciará o Servidor e dois Clientes automaticamente para teste local.

### 🎮 Como Jogar (Modo Manual/Rede)

**1. No Computador do Servidor (Host):**
```bash
python server.py