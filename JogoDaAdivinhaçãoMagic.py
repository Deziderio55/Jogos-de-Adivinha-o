import json
import os
import time
import requests
from abc import ABC, abstractmethod
from datetime import datetime

TITULO = "☀️💧☠️🔥🌳 MAGIC: THE GATHERING"


class Jogo(ABC):
    @abstractmethod
    def iniciar(self):
        pass

    @abstractmethod
    def jogar(self):
        pass


class Ranking:
    ARQUIVO_RANKING = "ranking_magic.json"

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

    def registrar(self, nome: str, pontuacao: int, tentativas: int, carta: str):
        entrada = {
            "nome": nome,
            "pontuacao": pontuacao,
            "tentativas": tentativas,
            "carta": carta,
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

        print("\n" + "=" * 70)
        print("RANKING - " + TITULO)
        print("=" * 70)
        print(f"{'Pos':<5} {'Nome':<18} {'Carta Acertada':<25} {'Pontos':<9} {'Tent.':<7} {'Data'}")
        print("-" * 70)

        for pos, j in enumerate(ordenado, start=1):
            posicao = {1: "1o", 2: "2o", 3: "3o"}.get(pos, f"{pos}o")
            print(
                f"{posicao:<6} {j['nome']:<18} {j['carta']:<25} "
                f"{j['pontuacao']:<9} {j['tentativas']:<7} {j['data']}"
            )
        print("=" * 70)


class ScryfallAPI:
    BASE_URL = "https://api.scryfall.com"
    HEADERS = {
        "User-Agent": "MagicGuessingGame/1.0",
        "Accept": "application/json"
    }

    @staticmethod
    def __requisitar(url: str, params: dict = None) -> dict | None:
        try:
            time.sleep(0.1)
            resposta = requests.get(url, headers=ScryfallAPI.HEADERS, params=params, timeout=10)
            resposta.raise_for_status()
            return resposta.json()
        except requests.RequestException:
            return None

    @staticmethod
    def carta_aleatoria() -> dict | None:
        dados = ScryfallAPI.__requisitar(
            f"{ScryfallAPI.BASE_URL}/cards/random",
            params={"q": "lang:pt OR lang:en -layout:transform -layout:modal_dfc -layout:meld"}
        )
        if not dados:
            return None
        return {
            "nome":        dados.get("name", "Desconhecida"),
            "custo":       dados.get("mana_cost", "N/A"),
            "cmc":         int(dados.get("cmc", 0)),
            "tipo":        dados.get("type_line", "N/A"),
            "cor":         ScryfallAPI.__traduzir_cores(dados.get("colors", [])),
            "raridade":    ScryfallAPI.__traduzir_raridade(dados.get("rarity", "N/A")),
            "conjunto":    dados.get("set_name", "N/A"),
            "texto":       dados.get("oracle_text", ""),
            "poder":       dados.get("power", None),
            "resistencia": dados.get("toughness", None),
            "imagem":      dados.get("image_uris", {}).get("normal", None),
        }

    @staticmethod
    def autocomplete(prefixo: str) -> list[str]:
        dados = ScryfallAPI.__requisitar(
            f"{ScryfallAPI.BASE_URL}/cards/autocomplete",
            params={"q": prefixo}
        )
        if dados and "data" in dados:
            return dados["data"]
        return []

    @staticmethod
    def listar_colecoes() -> list[dict]:
        dados = ScryfallAPI.__requisitar(f"{ScryfallAPI.BASE_URL}/sets")
        if dados and "data" in dados:
            return [{"codigo": s["code"], "nome": s["name"]} for s in dados["data"]]
        return []

    @staticmethod
    def carta_aleatoria_de_colecao(codigo_set: str) -> dict | None:
        dados = ScryfallAPI.__requisitar(
            f"{ScryfallAPI.BASE_URL}/cards/random",
            params={"q": f"e:{codigo_set} (lang:pt OR lang:en) -layout:transform -layout:modal_dfc -layout:meld"}
        )
        if not dados:
            return None
        return {
            "nome":        dados.get("name", "Desconhecida"),
            "custo":       dados.get("mana_cost", "N/A"),
            "cmc":         int(dados.get("cmc", 0)),
            "tipo":        dados.get("type_line", "N/A"),
            "cor":         ScryfallAPI.__traduzir_cores(dados.get("colors", [])),
            "raridade":    ScryfallAPI.__traduzir_raridade(dados.get("rarity", "N/A")),
            "conjunto":    dados.get("set_name", "N/A"),
            "texto":       dados.get("oracle_text", ""),
            "poder":       dados.get("power", None),
            "resistencia": dados.get("toughness", None),
            "imagem":      dados.get("image_uris", {}).get("normal", None),
        }

    @staticmethod
    def buscar_data_set(codigo_set: str) -> str | None:
        # Busca a data de lançamento de um set pelo código
        dados = ScryfallAPI.__requisitar(f"{ScryfallAPI.BASE_URL}/sets/{codigo_set}")
        if dados and "released_at" in dados:
            return dados["released_at"]  # formato: "2021-07-09"
        return None

    @staticmethod
    def carta_aleatoria_entre_colecoes(set_inicio: str, set_fim: str) -> dict | None:
        # Busca as datas dos dois sets e filtra as cartas pelo período
        data_inicio = ScryfallAPI.buscar_data_set(set_inicio)
        data_fim = ScryfallAPI.buscar_data_set(set_fim)

        if not data_inicio or not data_fim:
            print("Nao foi possivel encontrar um ou ambos os sets informados.")
            return None

        dados = ScryfallAPI.__requisitar(
            f"{ScryfallAPI.BASE_URL}/cards/random",
            params={"q": f"date>={data_inicio} date<={data_fim} (lang:pt OR lang:en) -layout:transform -layout:modal_dfc -layout:meld"}
        )
        if not dados:
            return None
        return {
            "nome":        dados.get("name", "Desconhecida"),
            "custo":       dados.get("mana_cost", "N/A"),
            "cmc":         int(dados.get("cmc", 0)),
            "tipo":        dados.get("type_line", "N/A"),
            "cor":         ScryfallAPI.__traduzir_cores(dados.get("colors", [])),
            "raridade":    ScryfallAPI.__traduzir_raridade(dados.get("rarity", "N/A")),
            "conjunto":    dados.get("set_name", "N/A"),
            "texto":       dados.get("oracle_text", ""),
            "poder":       dados.get("power", None),
            "resistencia": dados.get("toughness", None),
            "imagem":      dados.get("image_uris", {}).get("normal", None),
        }

    @staticmethod
    def __traduzir_cores(cores: list) -> str:
        mapa = {"W": "Branco", "U": "Azul", "B": "Preto", "R": "Vermelho", "G": "Verde"}
        if not cores:
            return "Incolor"
        return ", ".join(mapa.get(c, c) for c in cores)

    @staticmethod
    def __traduzir_raridade(raridade: str) -> str:
        mapa = {
            "common":   "Comum",
            "uncommon": "Incomum",
            "rare":     "Rara",
            "mythic":   "Mitica",
            "special":  "Especial",
            "bonus":    "Bonus",
        }
        return mapa.get(raridade.lower(), raridade.capitalize())


class JogoMagic(Jogo):
    LIMITE_TENTATIVAS = 8

    DICAS_ORDEM = [
        "cor",
        "tipo",
        "raridade",
        "cmc",
        "conjunto",
        "poder_resistencia",
        "texto_parcial",
        "imagem",
    ]

    def __init__(self, nome_jogador: str, ranking: Ranking, modo_set: dict = None):
        self.__nome_jogador = nome_jogador
        self.__ranking = ranking
        self.__carta = None
        self.__tentativas = 0
        self.__limite = self.LIMITE_TENTATIVAS
        self.__acertou = False
        self.__dicas_dadas = []
        self.__modo_set = modo_set

    def __carregar_carta(self) -> bool:
        print("\nBuscando uma carta no Scryfall...")

        if self.__modo_set is None:
            carta = ScryfallAPI.carta_aleatoria()
        elif self.__modo_set["tipo"] == "especifica":
            carta = ScryfallAPI.carta_aleatoria_de_colecao(self.__modo_set["set"])
        elif self.__modo_set["tipo"] == "intervalo":
            carta = ScryfallAPI.carta_aleatoria_entre_colecoes(
                self.__modo_set["inicio"], self.__modo_set["fim"]
            )
        else:
            carta = ScryfallAPI.carta_aleatoria()

        if not carta:
            print("Nao foi possivel buscar uma carta. Verifique o codigo do set ou sua conexao.")
            return False
        self.__carta = carta
        return True

    def __calcular_pontuacao(self) -> int:
        if not self.__acertou:
            return 0
        pontos = 1000 - (self.__tentativas - 1) * 80 - len(self.__dicas_dadas) * 40
        return max(pontos, 50)

    def __mostrar_dica(self):
        proximas = [d for d in self.DICAS_ORDEM if d not in self.__dicas_dadas]
        if not proximas:
            print("   Nao ha mais dicas disponiveis.")
            return

        dica = proximas[0]
        self.__dicas_dadas.append(dica)
        c = self.__carta

        print("\n   DICA:")
        if dica == "cor":
            print(f"      Cor(es): {c['cor']}")
        elif dica == "tipo":
            print(f"      Tipo: {c['tipo']}")
        elif dica == "raridade":
            print(f"      Raridade: {c['raridade']}")
        elif dica == "cmc":
            print(f"      Custo de mana convertido (CMC): {c['cmc']}")
        elif dica == "conjunto":
            print(f"      Conjunto: {c['conjunto']}")
        elif dica == "poder_resistencia":
            if c["poder"] and c["resistencia"]:
                print(f"      Poder / Resistencia: {c['poder']} / {c['resistencia']}")
            else:
                print("      Esta carta nao e uma criatura (sem Poder/Resistencia).")
        elif dica == "texto_parcial":
            texto = c["texto"]
            if texto:
                palavras = texto.split()
                trecho = " ".join(palavras[:12]) + ("..." if len(palavras) > 12 else "")
                nome_oculto = trecho.replace(c["nome"], "?????")
                print(f"      Trecho do texto: \"{nome_oculto}\"")
            else:
                print("      Esta carta nao possui texto de regras.")
        elif dica == "imagem":
            if c["imagem"]:
                print(f"      Imagem da carta: {c['imagem']}")
            else:
                print("      Imagem nao disponivel para esta carta.")
        print()

    def __sugerir_nomes(self, prefixo: str) -> list[str]:
        if len(prefixo) < 2:
            return []
        return ScryfallAPI.autocomplete(prefixo)

    def iniciar(self):
        print("\n" + "=" * 55)
        print(TITULO)
        print(f"   Bem-vindo(a), {self.__nome_jogador}!")
        print("=" * 55)
        print("Uma carta foi sorteada do Scryfall.")
        print(f"Voce tem {self.__limite} tentativas para adivinhar o nome.")
        print("A cada erro, uma nova dica sera revelada.")
        print("\nComandos especiais durante o jogo:")
        print("  !dica     -> pedir uma dica antecipada (custa pontos)")
        print("  !desistir -> revelar a carta e encerrar\n")

    def jogar(self):
        if not self.__carregar_carta():
            return

        print(f"\nCarta carregada! Boa sorte, {self.__nome_jogador}!\n")

        while self.__tentativas < self.__limite:
            restantes = self.__limite - self.__tentativas
            print(f"[Tentativas restantes: {restantes} | Dicas usadas: {len(self.__dicas_dadas)}]")

            entrada = input("Nome da carta (ou !dica / !desistir): ").strip()

            if entrada.lower() == "!desistir":
                print(f"\nVoce desistiu. A carta era: {self.__carta['nome']}")
                if self.__carta["imagem"]:
                    print(f"   Imagem: {self.__carta['imagem']}")
                self.__ranking.registrar(self.__nome_jogador, 0, self.__tentativas, self.__carta["nome"])
                return

            if entrada.lower() == "!dica":
                self.__mostrar_dica()
                continue

            if not entrada:
                print("Digite um nome ou comando.\n")
                continue

            sugestoes = self.__sugerir_nomes(entrada)
            if sugestoes and entrada.lower() not in [s.lower() for s in sugestoes]:
                print(f"   Voce quis dizer: {', '.join(sugestoes[:5])}?")

            self.__tentativas += 1

            if entrada.lower() == self.__carta["nome"].lower():
                self.__acertou = True
                pontuacao = self.__calcular_pontuacao()
                print(f"\nParabens, {self.__nome_jogador}! Era \"{self.__carta['nome']}\"!")
                print(f"   Acertou em {self.__tentativas} tentativa(s) com {len(self.__dicas_dadas)} dica(s).")
                print(f"   Pontuacao: {pontuacao} pontos")
                if self.__carta["imagem"]:
                    print(f"   Imagem: {self.__carta['imagem']}\n")
                self.__ranking.registrar(self.__nome_jogador, pontuacao, self.__tentativas, self.__carta["nome"])
                return
            else:
                print(f"Errado. Nao e \"{entrada}\".\n")
                self.__mostrar_dica()

        print(f"\nSuas tentativas acabaram, {self.__nome_jogador}!")
        print(f"   A carta era: {self.__carta['nome']}")
        if self.__carta["imagem"]:
            print(f"   Imagem: {self.__carta['imagem']}")
        print("   Pontuacao: 0 pontos\n")
        self.__ranking.registrar(self.__nome_jogador, 0, self.__tentativas, self.__carta["nome"])


def executar_jogo(jogo: Jogo):
    jogo.iniciar()
    jogo.jogar()


def selecionar_modo_set() -> dict | None:
    print("\nModo de colecao:")
    print("  1 - Qualquer carta (padrao)")
    print("  2 - Colecao especifica")
    print("  3 - Intervalo entre colecoes")

    opcao = input("Escolha: ").strip()

    if opcao == "2":
        codigo = input("Codigo da colecao (ex: dsk, mkm, ltr): ").strip().lower()
        return {"tipo": "especifica", "set": codigo}

    elif opcao == "3":
        print("Use os codigos de set do Scryfall (ex: m21, znr, mid)")
        inicio = input("Set inicial: ").strip().lower()
        fim    = input("Set final:   ").strip().lower()
        return {"tipo": "intervalo", "inicio": inicio, "fim": fim}

    return None


def main():
    ranking = Ranking()

    while True:
        print("\n" + "=" * 55)
        print("MENU PRINCIPAL - " + TITULO)
        print("=" * 55)
        print("1 - Jogar")
        print("2 - Ver Ranking")
        print("3 - Sair")
        print("-" * 55)

        opcao = input("Escolha uma opcao: ").strip()

        if opcao == "1":
            nome = input("\nDigite seu nome: ").strip()
            if not nome:
                nome = "Anonimo"
            modo = selecionar_modo_set()
            jogo = JogoMagic(nome, ranking, modo_set=modo)
            executar_jogo(jogo)

        elif opcao == "2":
            ranking.exibir()

        elif opcao == "3":
            print("\nAte a proxima, Planeswalker!\n")
            break


if __name__ == "__main__":
    main()


def selecionar_modo_set() -> dict | None:
    print("\nModo de colecao:")
    print("  1 - Qualquer carta (padrao)")
    print("  2 - Colecao especifica")
    print("  3 - Intervalo entre colecoes")

    opcao = input("Escolha: ").strip()

    if opcao == "2":
        codigo = input("Codigo da colecao (ex: dsk, mkm, ltr): ").strip().lower()
        return {"tipo": "especifica", "set": codigo}

    elif opcao == "3":
        print("Use os codigos de set do Scryfall (ex: m21, znr, mid)")
        inicio = input("Set inicial: ").strip().lower()
        fim    = input("Set final:   ").strip().lower()
        return {"tipo": "intervalo", "inicio": inicio, "fim": fim}

    return None


def main():
    ranking = Ranking()

    while True:
        print("\n" + "=" * 55)
        print("MENU PRINCIPAL - " + TITULO)
        print("=" * 55)
        print("1 - Jogar")
        print("2 - Ver Ranking")
        print("3 - Sair")
        print("-" * 55)

        opcao = input("Escolha uma opcao: ").strip()

        if opcao == "1":
            nome = input("\nDigite seu nome: ").strip()
            if not nome:
                nome = "Anonimo"
            modo = selecionar_modo_set()
            jogo = JogoMagic(nome, ranking, modo_set=modo)
            executar_jogo(jogo)

        elif opcao == "2":
            ranking.exibir()

        elif opcao == "3":
            print("\nAte a proxima, Planeswalker!\n")
            break

        else:
            print("Opcao invalida. Tente novamente.")
    main()