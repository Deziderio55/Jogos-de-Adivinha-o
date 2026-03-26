import random
import json
import os
from abc import ABC, abstractmethod
from datetime import datetime


class Jogo(ABC):
    @abstractmethod
    def iniciar(self):
        pass

    @abstractmethod
    def jogar(self):
        pass


class Ranking:
    ARQUIVO_RANKING = "ranking.json"

    def __init__(self):
        self.__jogadores = self.__carregar_ranking()

    def __carregar_ranking(self):
        if os.path.exists(self.ARQUIVO_RANKING):
            with open(self.ARQUIVO_RANKING, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def __salvar_ranking(self):
        with open(self.ARQUIVO_RANKING, "w", encoding="utf-8") as f:
            json.dump(self.__jogadores, f, ensure_ascii=False, indent=2)

    def registrar(self, nome: str, pontuacao: int, tentativas: int, modalidade: str):
        entrada = {
            "nome": nome,
            "pontuacao": pontuacao,
            "tentativas": tentativas,
            "modalidade": modalidade,
            "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
        }
        self.__jogadores.append(entrada)
        self.__salvar_ranking()

    def exibir(self):
        if not self.__jogadores:
            print("\nO ranking ainda esta vazio.")
            return

        ordenado = sorted(
            self.__jogadores,
            key=lambda x: (-x["pontuacao"], x["tentativas"])
        )

        print("\n" + "=" * 62)
        print("RANKING DOS JOGADORES")
        print("=" * 62)
        print(f"{'Pos':<5} {'Nome':<18} {'Modalidade':<18} {'Pontos':<9} {'Tent.':<7} {'Data'}")
        print("-" * 62)

        for pos, j in enumerate(ordenado, start=1):
            posicao = {1: "1o", 2: "2o", 3: "3o"}.get(pos, f"{pos}o")
            print(
                f"{posicao:<6} {j['nome']:<18} {j['modalidade']:<18} "
                f"{j['pontuacao']:<9} {j['tentativas']:<7} {j['data']}"
            )
        print("=" * 62)


class JogoAdivinhacao(Jogo):
    LIMITE_TENTATIVAS = 10

    def __init__(self, nome_jogador: str, ranking: Ranking):
        self.__numero_secreto = random.randint(1, 100)
        self.__tentativas = 0
        self.__limite = self.LIMITE_TENTATIVAS
        self.__nome_jogador = nome_jogador
        self.__ranking = ranking
        self.__acertou = False

    def __calcular_pontuacao(self) -> int:
        if not self.__acertou:
            return 0
        pontos = 1000 - (self.__tentativas - 1) * 80
        return max(pontos, 100)

    def iniciar(self):
        print("\n" + "=" * 50)
        print("JOGO DA ADIVINHACAO - NUMEROS")
        print(f"   Bem-vindo(a), {self.__nome_jogador}!")
        print("=" * 50)
        print(f"Tente adivinhar o numero entre 1 e 100.")
        print(f"Voce tem {self.__limite} tentativas.\n")

    def jogar(self):
        while self.__tentativas < self.__limite:
            tentativas_restantes = self.__limite - self.__tentativas
            print(f"[Tentativas restantes: {tentativas_restantes}]")

            try:
                palpite = int(input("Digite seu palpite: "))
            except ValueError:
                print("Por favor, digite um numero inteiro valido.\n")
                continue

            if not (1 <= palpite <= 100):
                print("O numero deve estar entre 1 e 100.\n")
                continue

            self.__tentativas += 1

            if palpite == self.__numero_secreto:
                self.__acertou = True
                pontuacao = self.__calcular_pontuacao()
                print(f"\nParabens, {self.__nome_jogador}! Voce acertou em {self.__tentativas} tentativa(s)!")
                print(f"Pontuacao: {pontuacao} pontos\n")
                self.__ranking.registrar(self.__nome_jogador, pontuacao, self.__tentativas, "Numeros")
                return
            elif palpite < self.__numero_secreto:
                print("O numero secreto e MAIOR\n")
            else:
                print("O numero secreto e MENOR\n")

        print(f"\nQue pena, {self.__nome_jogador}! Voce usou todas as tentativas.")
        print(f"   O numero secreto era: {self.__numero_secreto}")
        print("   Pontuacao: 0 pontos\n")
        self.__ranking.registrar(self.__nome_jogador, 0, self.__tentativas, "Numeros")


class JogoAdivinhacaoCartas(Jogo):
    NAIPES = ["Espadas", "Copas", "Ouros", "Paus"]
    VALORES = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
    LIMITE_TENTATIVAS = 6

    def __init__(self, nome_jogador: str, ranking: Ranking):
        self.__baralho = [
            f"{valor} de {naipe}"
            for naipe in self.NAIPES
            for valor in self.VALORES
        ]
        self.__carta_secreta = random.choice(self.__baralho)
        self.__valor_secreto, self.__naipe_secreto = self.__desmontar(self.__carta_secreta)
        self.__tentativas = 0
        self.__limite = self.LIMITE_TENTATIVAS
        self.__nome_jogador = nome_jogador
        self.__ranking = ranking
        self.__acertou = False

    def __desmontar(self, carta: str):
        partes = carta.split(" de ")
        return partes[0], partes[1]

    def __calcular_pontuacao(self) -> int:
        if not self.__acertou:
            return 0
        pontos = 1200 - (self.__tentativas - 1) * 150
        return max(pontos, 100)

    def __dica_valor(self, valor_chute: str) -> str:
        ordem = self.VALORES
        if valor_chute not in ordem:
            return ""
        idx_chute = ordem.index(valor_chute)
        idx_secreto = ordem.index(self.__valor_secreto)
        if idx_chute < idx_secreto:
            return f"   O valor da carta e MAIOR que {valor_chute}."
        elif idx_chute > idx_secreto:
            return f"   O valor da carta e MENOR que {valor_chute}."
        return "   Valor correto! Mas o naipe esta errado."

    def iniciar(self):
        print("\n" + "=" * 50)
        print("JOGO DA ADIVINHACAO - CARTAS")
        print(f"   Bem-vindo(a), {self.__nome_jogador}!")
        print("=" * 50)
        print("Uma carta foi sorteada do baralho.")
        print(f"Voce tem {self.__limite} tentativas para adivinhar qual e.")
        print("\nValores possiveis : A 2 3 4 5 6 7 8 9 10 J Q K")
        print("Naipes possiveis  : Espadas  Copas  Ouros  Paus")
        print("\nFormato da resposta: <Valor> <Naipe>  (ex: A Copas  /  10 Espadas)\n")

    def jogar(self):
        while self.__tentativas < self.__limite:
            tentativas_restantes = self.__limite - self.__tentativas
            print(f"[Tentativas restantes: {tentativas_restantes}]")

            entrada = input("Digite sua tentativa: ").strip()
            partes = entrada.split()

            if len(partes) < 2:
                print("Digite o valor e o naipe separados por espaco. Ex: J Paus\n")
                continue

            valor_chute = partes[0].upper()
            naipe_chute = partes[1].capitalize()

            naipe_valido = next((n for n in self.NAIPES if naipe_chute in n), None)
            if valor_chute not in self.VALORES or not naipe_valido:
                print("Valor ou naipe invalido. Verifique e tente novamente.\n")
                continue

            self.__tentativas += 1
            carta_chute = f"{valor_chute} de {naipe_valido}"

            if carta_chute == self.__carta_secreta:
                self.__acertou = True
                pontuacao = self.__calcular_pontuacao()
                print(f"\nIncrivel, {self.__nome_jogador}! A carta era {self.__carta_secreta}!")
                print(f"   Voce acertou em {self.__tentativas} tentativa(s).")
                print(f"   Pontuacao: {pontuacao} pontos\n")
                self.__ranking.registrar(self.__nome_jogador, pontuacao, self.__tentativas, "Cartas")
                return

            dica = self.__dica_valor(valor_chute)

            if valor_chute == self.__valor_secreto:
                print(f"Quase! O valor {valor_chute} esta certo, mas o naipe esta errado.")
                print(f"   O naipe correto comeca com '{self.__naipe_secreto[0]}'.\n")
            elif naipe_valido == self.__naipe_secreto:
                print(f"O naipe {naipe_valido} esta certo, mas o valor esta errado.")
                print(dica + "\n")
            else:
                print("Valor e naipe incorretos.")
                print(dica + "\n")

        print(f"\nQue pena, {self.__nome_jogador}! Voce usou todas as tentativas.")
        print(f"   A carta secreta era: {self.__carta_secreta}")
        print("   Pontuacao: 0 pontos\n")
        self.__ranking.registrar(self.__nome_jogador, 0, self.__tentativas, "Cartas")


def executar_jogo(jogo: Jogo):
    jogo.iniciar()
    jogo.jogar()


def main():
    ranking = Ranking()

    while True:
        print("\n" + "=" * 50)
        print("         MENU PRINCIPAL")
        print("=" * 50)
        print("1 - Jogar: Adivinhacao de Numeros")
        print("2 - Jogar: Adivinhacao de Cartas")
        print("3 - Ver Ranking")
        print("4 - Sair")
        print("-" * 50)

        opcao = input("Escolha uma opcao: ").strip()

        if opcao in ("1", "2"):
            nome = input("\nDigite seu nome: ").strip()
            if not nome:
                nome = "Anonimo"

            if opcao == "1":
                jogo = JogoAdivinhacao(nome, ranking)
            else:
                jogo = JogoAdivinhacaoCartas(nome, ranking)

            executar_jogo(jogo)

        elif opcao == "3":
            ranking.exibir()

        elif opcao == "4":
            print("\nAte a proxima!\n")
            break

        else:
            print("Opcao invalida. Tente novamente.")
main()

# Eu modifiquei o código colocando um rank que fica ligado ao nome que pessoa colocou no jogo e no próprio rank mostra o rank da pessoa
# Separada por jogo e adicionei outro jogo de adivinhação com cartas de Baralho