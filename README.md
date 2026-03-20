# Jogos de Adivinhação — Coleção Python

Uma coleção de dois projetos de jogos de adivinhação desenvolvidos em Python, com ranking persistente e mecânicas distintas.

---

## Projetos
 Adivinhação Clássica = `JogoDaAdivinhaçãoCartaz.py` / Adivinhe números (1–100) ou cartas de baralho
 Magic: The Gathering = `JogoDaAdivinhaçãoMagic.py` / Adivinhe cartas reais do MTG via API Scryfall(Scryfall é um banco de dados onde armazenam todas as cartas do magic)

---

## Projeto 1 — Adivinhação de 

### Sobre
Dois modos de jogo em um único arquivo, ambos com sistema de ranking salvo localmente em `ranking.json`.

### Modos de Jogo

**1. Adivinhação de Números**
- Um número aleatório entre 1 e 100 é sorteado
- O jogador tem até **10 tentativas**
- A cada erro, o jogo indica se o número secreto é maior ou menor
- Pontuação máxima: **1000 pontos** (diminui 80 por tentativa extra)

**2. Adivinhação de Cartas de Baralho**
- Uma carta de um baralho padrão (52 cartas) é sorteada
- O jogador tem até **6 tentativas**
- A cada erro, o jogo informa se o valor é maior/menor e dá dica sobre o naipe
- Pontuação máxima: **1200 pontos** (diminui 150 por tentativa extra)

### Como Jogar
```bash
python jogo_classico.py
```

**Formato de entrada para cartas:**
```
<Valor> <Naipe>   →   ex: A Copas  /  10 Espadas  /  J Paus
```

### Ranking
O ranking é salvo em `ranking.json` e exibido ordenado por pontuação (maior primeiro) e tentativas (menor primeiro). Mostra: posição, nome, modalidade, pontos, tentativas e data.

---

## ☀️💧☠️🔥🌳 Projeto 2 — Magic: The Gathering

### Sobre
Jogo de adivinhação usando cartas **reais** do MTG, buscadas em tempo real via [API Scryfall](https://scryfall.com/docs/api). O ranking é salvo localmente em `ranking_magic.json`.

### Dependências
```bash
pip install requests
```

> ⚠️ Requer conexão com a internet para buscar as cartas.

### Como Jogar
```bash
python jogo_magic.py
```

### Mecânica
- Uma carta aleatória é sorteada do Scryfall
- O jogador tem até **8 tentativas** para adivinhar o nome completo da carta
- A cada erro, uma **dica automática** é revelada na seguinte ordem:

### Ordem / Dica Revelada 

 1ª = Cor(es) da carta |
 2ª = Tipo (Criatura, Feitiço, etc.) |
 3ª = Raridade |
 4ª = Custo de mana convertido (CMC) |
 5ª = Conjunto (set) |
 6ª = Poder / Resistência (se for criatura) |
 7ª = Trecho do texto de regras |
 8ª = Link da imagem da carta |

### Comandos Especiais

 Comando / Efeito

 `!dica` = Solicita uma dica antecipada (reduz pontuação)
 `!desistir` = Revela a carta e encerra a partida com 0 pontos

O jogo também oferece **sugestões de autocomplete** enquanto o jogador digita o nome da carta.

### Pontuação
```
Pontos = 1000 − (tentativas − 1) × 80 − dicas_usadas × 40
Mínimo: 50 pontos
```

### Ranking
Salvo em `ranking_magic.json`, ordenado por pontuação. Exibe: posição, nome, carta acertada, pontos, tentativas e data.

---

## Estrutura Técnica

Ambos os projetos seguem os mesmos princípios de design orientado a objetos:

- **Classe abstrata `Jogo`** — define a interface `iniciar()` e `jogar()` para todos os modos
- **Classe `Ranking`** — gerencia persistência em JSON, registro e exibição formatada
- **Encapsulamento** — atributos privados com `__` em todas as classes de jogo
- **Função `executar_jogo(jogo: Jogo)`** — aplica polimorfismo para rodar qualquer modo de jogo

O projeto Magic ainda conta com a classe **`ScryfallAPI`**, que encapsula todas as chamadas HTTP ao Scryfall (carta aleatória e autocomplete de nomes).

---

## 📋 Requisitos

 Projeto / Python / Dependências externas 

 Adivinhação Clássica / 3.8+ / Nenhuma (só stdlib) 
 Magic: The Gathering / 3.10+ / `requests` 

---

##  Arquivos Gerados

```
ranking.json          ← histórico de partidas do Jogo Clássico
ranking_magic.json    ← histórico de partidas do Jogo Magic
```
