"""
Arena das Mitologias - Sistema de Combate RPG
Checkpoint 2 (CP2) - Programacao Orientada a Objetos em Python

Integrantes:
- Vinicius Eddo                  | RM: 571008
- Guilherme Gomes Orugian Santos | RM: 572882
- Lucas Henrique Vieira          | RM: 571901
- Rafael Jun Aita Hirata         | RM: 569708
- Rodrigo Bettio Penha Junior    | RM: 573725
"""

from __future__ import annotations
import random
import time
import sys
from abc import ABC, abstractmethod
from typing import List, Tuple

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


class Cores:
    RESET = "\033[0m"
    NEGRITO = "\033[1m"
    VERMELHO = "\033[91m"
    VERDE = "\033[92m"
    AMARELO = "\033[93m"
    AZUL = "\033[94m"
    MAGENTA = "\033[95m"
    CIANO = "\033[96m"
    CINZA = "\033[90m"

    @classmethod
    def aplicar(cls, texto: str, cor: str) -> str:
        return f"{cor}{texto}{cls.RESET}"


class EntidadeCombate(ABC):
    def __init__(
        self,
        nome: str,
        hp: int,
        mp: int,
        speed: int,
        atk: int,
        matk: int,
        defense: int,
        mdefense: int
    ) -> None:
        self.nome = nome
        self._max_hp = max(1, hp)
        self._hp = self._max_hp
        self._max_mp = max(0, mp)
        self._mp = self._max_mp
        self.speed = speed
        self.atk = atk
        self.matk = matk
        self.defense = defense
        self.mdefense = mdefense

    @property
    def hp(self) -> int:
        return self._hp

    @hp.setter
    def hp(self, valor: int) -> None:
        self._hp = max(0, min(valor, self._max_hp))

    @property
    def mp(self) -> int:
        return self._mp

    @mp.setter
    def mp(self, valor: int) -> None:
        self._mp = max(0, min(valor, self._max_mp))

    @property
    def max_hp(self) -> int:
        return self._max_hp

    @property
    def max_mp(self) -> int:
        return self._max_mp

    def esta_vivo(self) -> bool:
        return self._hp > 0

    def receber_dano(self, dano: int, tipo_dano: str = "físico") -> int:
        dano_real = max(1, dano)
        self.hp -= dano_real
        return dano_real

    def consumir_mp(self, custo: int) -> bool:
        if self.mp >= custo:
            self.mp -= custo
            return True
        return False

    def curar(self, quantidade: int) -> int:
        vida_anterior = self.hp
        self.hp += quantidade
        return self.hp - vida_anterior

    def barra_status(self, comprimento: int = 12) -> str:
        pct_hp = self.hp / self.max_hp if self.max_hp > 0 else 0
        cheios_hp = int(pct_hp * comprimento)
        barra_hp = "=" * cheios_hp + "-" * (comprimento - cheios_hp)

        pct_mp = self.mp / self.max_mp if self.max_mp > 0 else 0
        cheios_mp = int(pct_mp * comprimento)
        barra_mp = "*" * cheios_mp + "." * (comprimento - cheios_mp)

        cor_hp = Cores.VERDE if pct_hp > 0.5 else (Cores.AMARELO if pct_hp > 0.2 else Cores.VERMELHO)
        txt_hp = Cores.aplicar(f"[{barra_hp}] {self.hp:>3}/{self.max_hp:<3}", cor_hp)
        txt_mp = Cores.aplicar(f"[{barra_mp}] {self.mp:>3}/{self.max_mp:<3}", Cores.AZUL)

        status = f"{self.nome:<22} | HP: {txt_hp} | MP: {txt_mp}"
        if not self.esta_vivo():
            status += Cores.aplicar(" [DERROTADO]", Cores.VERMELHO + Cores.NEGRITO)
        return status

    @abstractmethod
    def atacar(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        pass

    @abstractmethod
    def habilidade_especial(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        pass


class Personagem(EntidadeCombate):
    def __init__(
        self,
        nome: str,
        hp: int = 120,
        mp: int = 40,
        speed: int = 15,
        atk: int = 24,
        matk: int = 12,
        defense: int = 12,
        mdefense: int = 10,
        classe_nome: str = "Aventureiro",
        mitologia: str = "Mitologia Clássica"
    ) -> None:
        super().__init__(
            nome=nome,
            hp=hp,
            mp=mp,
            speed=speed,
            atk=atk,
            matk=matk,
            defense=defense,
            mdefense=mdefense
        )
        self.classe_nome = classe_nome
        self.mitologia = mitologia

    def __str__(self) -> str:
        return f"[{self.mitologia}] {self.nome} ({self.classe_nome}) | HP: {self.hp}/{self.max_hp} | MP: {self.mp}/{self.max_mp} | SPD: {self.speed}"

    def regenerar_turno(self) -> None:
        if self.esta_vivo():
            self.mp += min(6, self.max_mp - self.mp)

    def atacar(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        dano = alvo.receber_dano(self.atk - alvo.defense, "físico")
        return dano, f"{self.nome} ataca {alvo.nome} causando {dano} de dano físico."

    def habilidade_especial(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        custo = 12
        if self.consumir_mp(custo):
            dano = alvo.receber_dano(int(self.atk * 1.3) - alvo.defense, "físico")
            return dano, f"{self.nome} usa um golpe focado em {alvo.nome} causando {dano} de dano."
        return self.atacar(alvo)


class Monstro(EntidadeCombate):
    def __init__(
        self,
        nome: str,
        hp: int = 130,
        mp: int = 30,
        speed: int = 12,
        atk: int = 25,
        matk: int = 14,
        defense: int = 12,
        mdefense: int = 10,
        origem: str = "Besta Selvagem",
        descricao: str = "Criatura feroz das sombras."
    ) -> None:
        super().__init__(
            nome=nome,
            hp=hp,
            mp=mp,
            speed=speed,
            atk=atk,
            matk=matk,
            defense=defense,
            mdefense=mdefense
        )
        self.origem = origem
        self.descricao = descricao

    def __str__(self) -> str:
        return f"[{self.origem}] {self.nome} | HP: {self.hp}/{self.max_hp} | MP: {self.mp}/{self.max_mp} | SPD: {self.speed}"

    def atacar(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        if self.atk >= self.matk:
            dano = alvo.receber_dano(self.atk - alvo.defense, "físico")
            msg = f"{self.nome} avança ferozmente contra {alvo.nome} causando {dano} de dano físico."
        else:
            dano = alvo.receber_dano(self.matk - alvo.mdefense, "mágico")
            msg = f"{self.nome} canaliza energia sombria em {alvo.nome} desferindo {dano} de dano mágico."
        return dano, msg

    def habilidade_especial(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        custo = 15
        if self.consumir_mp(custo):
            dano = alvo.receber_dano(int(self.atk * 1.4) - alvo.defense, "físico")
            return dano, f"[FÚRIA] {self.nome} desfere um ataque brutal em {alvo.nome} causando {dano} de dano!"
        return self.atacar(alvo)

    def agir_ia(self, alvos_vivos: List[EntidadeCombate]) -> Tuple[int, str]:
        if not alvos_vivos:
            return 0, "Sem alvos vivos."
        alvo = min(alvos_vivos, key=lambda a: a.hp)
        if self.mp >= 15 and random.random() < 0.5:
            return self.habilidade_especial(alvo)
        return self.atacar(alvo)


# --- Subclasses de Personagens ---

class Guerreiro(Personagem):
    def __init__(
        self,
        nome: str = "Aquiles de Atenas",
        hp: int = 145,
        mp: int = 30,
        speed: int = 12,
        atk: int = 28,
        matk: int = 6,
        defense: int = 17,
        mdefense: int = 8
    ) -> None:
        super().__init__(
            nome=nome,
            hp=hp,
            mp=mp,
            speed=speed,
            atk=atk,
            matk=matk,
            defense=defense,
            mdefense=mdefense,
            classe_nome="Guerreiro",
            mitologia="Mitologia Grega"
        )

    def atacar(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        dano = alvo.receber_dano(self.atk - alvo.defense, "físico")
        msg = (
            f"{Cores.VERMELHO}[GUERREIRO]{Cores.RESET} {self.nome} golpeia com lança espartana e escudo contra {alvo.nome}, "
            f"causando {Cores.NEGRITO}{dano}{Cores.RESET} de dano físico! (HP alvo: {alvo.hp})"
        )
        return dano, msg

    def habilidade_especial(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        custo = 15
        if not self.consumir_mp(custo):
            dano, msg = self.atacar(alvo)
            return dano, f"{Cores.AMARELO}[Sem MP]{Cores.RESET} {msg}"

        defesa_reduzida = int(alvo.defense * 0.6)
        dano = alvo.receber_dano(int(self.atk * 1.5) - defesa_reduzida, "físico")
        msg = (
            f"{Cores.AMARELO}{Cores.NEGRITO}[FÚRIA DE ARES]{Cores.RESET} {self.nome} avança em fúria e atinge {alvo.nome} "
            f"com impacto demolidor causando {Cores.VERMELHO}{Cores.NEGRITO}{dano}{Cores.RESET} de dano! (HP alvo: {alvo.hp})"
        )
        return dano, msg


class Mago(Personagem):
    def __init__(
        self,
        nome: str = "Merlin de Camelot",
        hp: int = 90,
        mp: int = 90,
        speed: int = 14,
        atk: int = 8,
        matk: int = 33,
        defense: int = 7,
        mdefense: int = 18
    ) -> None:
        super().__init__(
            nome=nome,
            hp=hp,
            mp=mp,
            speed=speed,
            atk=atk,
            matk=matk,
            defense=defense,
            mdefense=mdefense,
            classe_nome="Mago",
            mitologia="Mitologia Arturiana"
        )

    def atacar(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        dano = alvo.receber_dano(self.matk - alvo.mdefense, "mágico")
        msg = (
            f"{Cores.MAGENTA}[MAGO]{Cores.RESET} {self.nome} dispara Projéteis Cósmicos em {alvo.nome}, "
            f"causando {Cores.NEGRITO}{dano}{Cores.RESET} de dano mágico! (HP alvo: {alvo.hp})"
        )
        return dano, msg

    def habilidade_especial(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        custo = 25
        if not self.consumir_mp(custo):
            dano, msg = self.atacar(alvo)
            return dano, f"{Cores.AMARELO}[Sem MP]{Cores.RESET} {msg}"

        dano = alvo.receber_dano(int(self.matk * 1.7) - alvo.mdefense, "mágico")
        msg = (
            f"{Cores.MAGENTA}{Cores.NEGRITO}[METEORO DE AVALON]{Cores.RESET} {self.nome} conjura um meteoro estelar sobre {alvo.nome}, "
            f"causando {Cores.VERMELHO}{Cores.NEGRITO}{dano}{Cores.RESET} de dano mágico massivo! (HP alvo: {alvo.hp})"
        )
        return dano, msg


class Arqueiro(Personagem):
    def __init__(
        self,
        nome: str = "Atalanta de Ártemis",
        hp: int = 105,
        mp: int = 45,
        speed: int = 22,
        atk: int = 27,
        matk: int = 10,
        defense: int = 10,
        mdefense: int = 11
    ) -> None:
        super().__init__(
            nome=nome,
            hp=hp,
            mp=mp,
            speed=speed,
            atk=atk,
            matk=matk,
            defense=defense,
            mdefense=mdefense,
            classe_nome="Arqueiro",
            mitologia="Mitologia Grega"
        )

    def atacar(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        defesa_reduzida = int(alvo.defense * 0.75)
        dano = alvo.receber_dano(self.atk - defesa_reduzida, "físico")
        msg = (
            f"{Cores.VERDE}[ARQUEIRO]{Cores.RESET} {self.nome} dispara uma flecha veloz no ponto fraco de {alvo.nome}, "
            f"causando {Cores.NEGRITO}{dano}{Cores.RESET} de dano perfurante! (HP alvo: {alvo.hp})"
        )
        return dano, msg

    def habilidade_especial(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        custo = 20
        if not self.consumir_mp(custo):
            dano, msg = self.atacar(alvo)
            return dano, f"{Cores.AMARELO}[Sem MP]{Cores.RESET} {msg}"

        dano = alvo.receber_dano(int(self.atk * 1.6) - int(alvo.defense * 0.5), "físico")
        msg = (
            f"{Cores.VERDE}{Cores.NEGRITO}[FLECHA LUNAR]{Cores.RESET} {self.nome} canaliza a luz da lua e dispara em {alvo.nome}, "
            f"perfurando armaduras com {Cores.VERMELHO}{Cores.NEGRITO}{dano}{Cores.RESET} de dano! (HP alvo: {alvo.hp})"
        )
        return dano, msg


class Paladino(Personagem):
    def __init__(
        self,
        nome: str = "Brunhilda de Odin",
        hp: int = 135,
        mp: int = 50,
        speed: int = 15,
        atk: int = 22,
        matk: int = 18,
        defense: int = 14,
        mdefense: int = 14
    ) -> None:
        super().__init__(
            nome=nome,
            hp=hp,
            mp=mp,
            speed=speed,
            atk=atk,
            matk=matk,
            defense=defense,
            mdefense=mdefense,
            classe_nome="Paladino",
            mitologia="Mitologia Nórdica"
        )

    def atacar(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        dano_fisico = max(1, self.atk - alvo.defense)
        dano_sagrado = max(1, int(self.matk * 0.4) - int(alvo.mdefense * 0.3))
        dano = alvo.receber_dano(dano_fisico + dano_sagrado, "sagrado")
        msg = (
            f"{Cores.CIANO}[PALADINO]{Cores.RESET} {self.nome} crava sua lança sagrada em {alvo.nome}, "
            f"causando {Cores.NEGRITO}{dano}{Cores.RESET} de dano luminoso! (HP alvo: {alvo.hp})"
        )
        return dano, msg

    def habilidade_especial(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        custo = 20
        if not self.consumir_mp(custo):
            dano, msg = self.atacar(alvo)
            return dano, f"{Cores.AMARELO}[Sem MP]{Cores.RESET} {msg}"

        dano = alvo.receber_dano(int(self.atk * 1.2 + self.matk * 0.8) - int(alvo.defense * 0.5), "sagrado")
        cura = self.curar(18)
        msg = (
            f"{Cores.CIANO}{Cores.NEGRITO}[JULGAMENTO DIVINO]{Cores.RESET} {self.nome} atinge {alvo.nome} com luz sagrada "
            f"causando {Cores.VERMELHO}{Cores.NEGRITO}{dano}{Cores.RESET} de dano e restaurando +{cura} de HP! (HP atual: {self.hp})"
        )
        return dano, msg


class Assassino(Personagem):
    def __init__(
        self,
        nome: str = "Hanzo de Susanoo",
        hp: int = 100,
        mp: int = 40,
        speed: int = 25,
        atk: int = 30,
        matk: int = 12,
        defense: int = 9,
        mdefense: int = 9
    ) -> None:
        super().__init__(
            nome=nome,
            hp=hp,
            mp=mp,
            speed=speed,
            atk=atk,
            matk=matk,
            defense=defense,
            mdefense=mdefense,
            classe_nome="Assassino",
            mitologia="Mitologia Japonesa"
        )

    def atacar(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        dano_base = self.atk - alvo.defense
        critico = random.random() < 0.35
        dano_final = int(dano_base * 1.5) if critico else dano_base
        dano = alvo.receber_dano(dano_final, "físico")
        critico_tag = f" {Cores.AMARELO}[CRÍTICO!]{Cores.RESET}" if critico else ""
        msg = (
            f"{Cores.CINZA}[ASSASSINO]{Cores.RESET} {self.nome} desfere corte rápido de lâmina{critico_tag} em {alvo.nome}, "
            f"causando {Cores.NEGRITO}{dano}{Cores.RESET} de dano cortante! (HP alvo: {alvo.hp})"
        )
        return dano, msg

    def habilidade_especial(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        custo = 20
        if not self.consumir_mp(custo):
            dano, msg = self.atacar(alvo)
            return dano, f"{Cores.AMARELO}[Sem MP]{Cores.RESET} {msg}"

        dano = alvo.receber_dano(int(self.atk * 1.7) - int(alvo.defense * 0.5), "físico")
        msg = (
            f"{Cores.CINZA}{Cores.NEGRITO}[EXECUÇÃO DE SUSANOO]{Cores.RESET} {self.nome} corta o vento em velocidade máxima, "
            f"atingindo {alvo.nome} com {Cores.VERMELHO}{Cores.NEGRITO}{dano}{Cores.RESET} de dano letal! (HP alvo: {alvo.hp})"
        )
        return dano, msg


class Necromante(Personagem):
    def __init__(
        self,
        nome: str = "Nefértis de Anúbis",
        hp: int = 95,
        mp: int = 80,
        speed: int = 13,
        atk: int = 10,
        matk: int = 31,
        defense: int = 8,
        mdefense: int = 17
    ) -> None:
        super().__init__(
            nome=nome,
            hp=hp,
            mp=mp,
            speed=speed,
            atk=atk,
            matk=matk,
            defense=defense,
            mdefense=mdefense,
            classe_nome="Necromante",
            mitologia="Mitologia Egípcia"
        )

    def atacar(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        dano = alvo.receber_dano(self.matk - alvo.mdefense, "mágico")
        cura = self.curar(max(1, int(dano * 0.35)))
        msg = (
            f"{Cores.MAGENTA}[NECROMANTE]{Cores.RESET} {self.nome} usa o Toque das Tumbas em {alvo.nome}, "
            f"causando {Cores.NEGRITO}{dano}{Cores.RESET} de dano e drenando +{cura} HP para si! (HP atual: {self.hp})"
        )
        return dano, msg

    def habilidade_especial(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        custo = 25
        if not self.consumir_mp(custo):
            dano, msg = self.atacar(alvo)
            return dano, f"{Cores.AMARELO}[Sem MP]{Cores.RESET} {msg}"

        dano = alvo.receber_dano(int(self.matk * 1.8) - alvo.mdefense, "mágico")
        cura = self.curar(int(dano * 0.4))
        msg = (
            f"{Cores.MAGENTA}{Cores.NEGRITO}[BALANÇA DE ANÚBIS]{Cores.RESET} {self.nome} evoca a pesagem das almas sobre {alvo.nome}, "
            f"drenando {Cores.VERMELHO}{Cores.NEGRITO}{dano}{Cores.RESET} de dano e recuperando +{cura} de HP! (HP alvo: {alvo.hp})"
        )
        return dano, msg


# --- Subclasses de Monstros ---

class Minotauro(Monstro):
    def __init__(
        self,
        nome: str = "Astérion do Labirinto",
        hp: int = 165,
        mp: int = 20,
        speed: int = 10,
        atk: int = 31,
        matk: int = 5,
        defense: int = 15,
        mdefense: int = 6
    ) -> None:
        super().__init__(
            nome=nome,
            hp=hp,
            mp=mp,
            speed=speed,
            atk=atk,
            matk=matk,
            defense=defense,
            mdefense=mdefense,
            origem="Mitologia Grega",
            descricao="Besta colossal com cabeça de touro e machado duplo."
        )

    def atacar(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        dano = alvo.receber_dano(self.atk - alvo.defense, "físico")
        return dano, f"[MINOTAURO] {self.nome} golpeia com machado pesado contra {alvo.nome}, causando {dano} de dano! (HP alvo: {alvo.hp})"

    def habilidade_especial(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        if self.consumir_mp(10):
            dano = alvo.receber_dano(int(self.atk * 1.5) - int(alvo.defense * 0.7), "físico")
            return dano, f"[INVESTIDA] {self.nome} abaixa os chifres e atropela {alvo.nome}, causando {dano} de dano! (HP alvo: {alvo.hp})"
        return self.atacar(alvo)


class Cerbero(Monstro):
    def __init__(
        self,
        nome: str = "Cérbero dos Portões",
        hp: int = 135,
        mp: int = 35,
        speed: int = 18,
        atk: int = 26,
        matk: int = 15,
        defense: int = 12,
        mdefense: int = 12
    ) -> None:
        super().__init__(
            nome=nome,
            hp=hp,
            mp=mp,
            speed=speed,
            atk=atk,
            matk=matk,
            defense=defense,
            mdefense=mdefense,
            origem="Mitologia Grega",
            descricao="Cão de três cabeças banhado em chamas do Tártaro."
        )

    def atacar(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        dano = alvo.receber_dano(self.atk - alvo.defense, "físico")
        return dano, f"[CÉRBERO] {self.nome} desfere mordidas flamejantes em {alvo.nome}, causando {dano} de dano! (HP alvo: {alvo.hp})"

    def habilidade_especial(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        if self.consumir_mp(15):
            dano = alvo.receber_dano(int(self.atk * 1.3 + self.matk * 0.6) - alvo.defense, "misto")
            return dano, f"[MORDIDA TRÍPLICE] As três cabeças de {self.nome} cravam presas em {alvo.nome}, causando {dano} de dano! (HP alvo: {alvo.hp})"
        return self.atacar(alvo)


class Medusa(Monstro):
    def __init__(
        self,
        nome: str = "Medusa Petrificante",
        hp: int = 110,
        mp: int = 70,
        speed: int = 16,
        atk: int = 12,
        matk: int = 32,
        defense: int = 10,
        mdefense: int = 16
    ) -> None:
        super().__init__(
            nome=nome,
            hp=hp,
            mp=mp,
            speed=speed,
            atk=atk,
            matk=matk,
            defense=defense,
            mdefense=mdefense,
            origem="Mitologia Grega",
            descricao="Górgona com cabelos de serpente e olhar de pedra."
        )

    def atacar(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        dano = alvo.receber_dano(self.matk - alvo.mdefense, "mágico")
        return dano, f"[MEDUSA] {self.nome} lança seu olhar venenoso em {alvo.nome}, causando {dano} de dano místico! (HP alvo: {alvo.hp})"

    def habilidade_especial(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        if self.consumir_mp(20):
            dano = alvo.receber_dano(int(self.matk * 1.6) - alvo.mdefense, "mágico")
            return dano, f"[OLHAR PETRIFICANTE] {self.nome} transforma a carne de {alvo.nome} em pedra, causando {dano} de dano mágico! (HP alvo: {alvo.hp})"
        return self.atacar(alvo)


class Quimera(Monstro):
    def __init__(
        self,
        nome: str = "Quimera Flamejante",
        hp: int = 125,
        mp: int = 40,
        speed: int = 15,
        atk: int = 24,
        matk: int = 20,
        defense: int = 11,
        mdefense: int = 11
    ) -> None:
        super().__init__(
            nome=nome,
            hp=hp,
            mp=mp,
            speed=speed,
            atk=atk,
            matk=matk,
            defense=defense,
            mdefense=mdefense,
            origem="Mitologia Clássica",
            descricao="Híbrido de leão, bode e cauda de serpente."
        )

    def atacar(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        dano = alvo.receber_dano(self.atk - alvo.defense, "físico")
        return dano, f"[QUIMERA] {self.nome} ataca com garras e picada de serpente em {alvo.nome}, causando {dano} de dano! (HP alvo: {alvo.hp})"

    def habilidade_especial(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        if self.consumir_mp(18):
            dano = alvo.receber_dano(int(self.matk * 1.5) - alvo.mdefense, "mágico")
            return dano, f"[BAFORADA] {self.nome} cospe fogo sobre {alvo.nome}, causando {dano} de dano de chamas! (HP alvo: {alvo.hp})"
        return self.atacar(alvo)


class Kraken(Monstro):
    def __init__(
        self,
        nome: str = "Kraken Abissal",
        hp: int = 175,
        mp: int = 30,
        speed: int = 9,
        atk: int = 27,
        matk: int = 16,
        defense: int = 16,
        mdefense: int = 10
    ) -> None:
        super().__init__(
            nome=nome,
            hp=hp,
            mp=mp,
            speed=speed,
            atk=atk,
            matk=matk,
            defense=defense,
            mdefense=mdefense,
            origem="Mitologia Nórdica",
            descricao="Leviatã titânico das profundezas oceânicas."
        )

    def atacar(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        dano = alvo.receber_dano(self.atk - alvo.defense, "físico")
        return dano, f"[KRAKEN] {self.nome} chicoteia tentáculos colossais contra {alvo.nome}, causando {dano} de dano marítimo! (HP alvo: {alvo.hp})"

    def habilidade_especial(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        if self.consumir_mp(15):
            dano = alvo.receber_dano(int(self.atk * 1.4) - int(alvo.defense * 0.6), "físico")
            return dano, f"[TSUNAMI] {self.nome} ergue uma onda descomunal esmagando {alvo.nome} com {dano} de impacto! (HP alvo: {alvo.hp})"
        return self.atacar(alvo)


class Esfinge(Monstro):
    def __init__(
        self,
        nome: str = "Esfinge das Dunas",
        hp: int = 120,
        mp: int = 60,
        speed: int = 13,
        atk: int = 18,
        matk: int = 29,
        defense: int = 13,
        mdefense: int = 18
    ) -> None:
        super().__init__(
            nome=nome,
            hp=hp,
            mp=mp,
            speed=speed,
            atk=atk,
            matk=matk,
            defense=defense,
            mdefense=mdefense,
            origem="Mitologia Egípcia",
            descricao="Guardiã ancestral com corpo de leoa e asas de falcão."
        )

    def atacar(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        dano = alvo.receber_dano(self.matk - alvo.mdefense, "mágico")
        return dano, f"[ESFINGE] {self.nome} desfere um enigma mental contra {alvo.nome}, causando {dano} de dano psíquico! (HP alvo: {alvo.hp})"

    def habilidade_especial(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        if self.consumir_mp(20):
            dano = alvo.receber_dano(int(self.matk * 1.55) - alvo.mdefense, "mágico")
            return dano, f"[ENIGMA ANCESTRAL] {self.nome} paralisa a alma de {alvo.nome} com as areias sagradas causando {dano} de dano! (HP alvo: {alvo.hp})"
        return self.atacar(alvo)


# --- Sistema de Batalha 1v1 ---

def simular_combate_1v1(heroi: Personagem, monstro: Monstro, interativo: bool = False, delay: float = 0.4) -> bool:
    print("\n" + "=" * 78)
    print(Cores.aplicar(f"DUELO 1v1: {heroi.nome} VS {monstro.nome}", Cores.NEGRITO + Cores.AMARELO))
    print("=" * 78)
    print(f"Herói:   {heroi}")
    print(f"Monstro: {monstro}")
    print("-" * 78)

    rodada = 1

    while heroi.esta_vivo() and monstro.esta_vivo():
        print(f"\n{Cores.NEGRITO}--- [RODADA {rodada}] ---{Cores.RESET}")
        print(heroi.barra_status())
        print(monstro.barra_status())
        print("-" * 55)

        if heroi.speed > monstro.speed:
            primeiro, segundo = heroi, monstro
        elif monstro.speed > heroi.speed:
            primeiro, segundo = monstro, heroi
        else:
            primeiro, segundo = (heroi, monstro) if random.random() < 0.5 else (monstro, heroi)

        ordem = [primeiro, segundo]
        print(f"Iniciativa: {primeiro.nome} (SPD: {primeiro.speed}) age antes de {segundo.nome} (SPD: {segundo.speed})!")

        for atacante in ordem:
            if not heroi.esta_vivo() or not monstro.esta_vivo():
                break

            defensor = monstro if atacante == heroi else heroi

            if atacante == heroi:
                if interativo:
                    print(f"\nSeu turno, {heroi.nome}:")
                    print("  [1] Ataque Básico")
                    print(f"  [2] Habilidade Especial ({heroi.classe_nome} - gasta MP)")
                    while True:
                        escolha = input("Ação (1 ou 2) [Padrão: 1]: ").strip() or "1"
                        if escolha in ("1", "2"):
                            break
                        print("Opção inválida. Digite 1 ou 2.")

                    if escolha == "2" and heroi.mp >= 15:
                        _, msg = heroi.habilidade_especial(defensor)
                    else:
                        if escolha == "2":
                            print(f"{Cores.AMARELO}Sem MP suficiente! Realizando ataque básico.{Cores.RESET}")
                        _, msg = heroi.atacar(defensor)
                else:
                    if heroi.mp >= 20 and random.random() < 0.65:
                        _, msg = heroi.habilidade_especial(defensor)
                    else:
                        _, msg = heroi.atacar(defensor)
            else:
                _, msg = monstro.agir_ia([heroi])

            print(f"  {msg}")
            if delay > 0:
                time.sleep(delay)

        heroi.regenerar_turno()
        rodada += 1

    print("\n" + "=" * 78)
    print(Cores.aplicar("RESULTADO DO DUELO 1v1", Cores.NEGRITO + Cores.AMARELO))
    print("=" * 78)

    if heroi.esta_vivo():
        print(f"{Cores.VERDE}{Cores.NEGRITO}Vitória do Herói!{Cores.RESET} {heroi.nome} derrotou {monstro.nome} em {rodada - 1} rodadas.")
        print(f"Status Final: {heroi.nome} com {heroi.hp}/{heroi.max_hp} HP restante.")
        return True
    else:
        print(f"{Cores.VERMELHO}{Cores.NEGRITO}Derrota!{Cores.RESET} {monstro.nome} derrotou {heroi.nome} em {rodada - 1} rodadas.")
        print(f"Status Final: {monstro.nome} sobreviveu com {monstro.hp}/{monstro.max_hp} HP.")
        return False


batalha_1v1 = simular_combate_1v1


# --- Sistema de Batalha 3v3 ---

def simular_combate_3v3(
    time_herois: List[Personagem],
    time_monstros: List[Monstro],
    interativo: bool = False,
    delay: float = 0.35
) -> bool:
    print("\n" + "=" * 85)
    print(Cores.aplicar("BATALHA EM EQUIPE 3v3", Cores.NEGRITO + Cores.AMARELO))
    print("=" * 85)
    print(f"{Cores.VERDE}EQUIPE DOS HERÓIS:{Cores.RESET}")
    for h in time_herois:
        print(f"  • {h}")
    print(f"\n{Cores.VERMELHO}EQUIPE DOS MONSTROS:{Cores.RESET}")
    for m in time_monstros:
        print(f"  • {m}")
    print("=" * 85)

    rodada = 1

    while any(h.esta_vivo() for h in time_herois) and any(m.esta_vivo() for m in time_monstros):
        print(f"\n{Cores.NEGRITO}==================== [RODADA {rodada}] ===================={Cores.RESET}")
        print(f"{Cores.VERDE}Status dos Heróis:{Cores.RESET}")
        for h in time_herois:
            print(f"  {h.barra_status()}")

        print(f"\n{Cores.VERMELHO}Status dos Monstros:{Cores.RESET}")
        for m in time_monstros:
            print(f"  {m.barra_status()}")
        print("-" * 80)

        todos_combatentes: List[EntidadeCombate] = [c for c in (time_herois + time_monstros) if c.esta_vivo()]
        todos_combatentes.sort(key=lambda c: (c.speed, random.random()), reverse=True)

        fila_nomes = " ➔ ".join([f"{c.nome} (SPD:{c.speed})" for c in todos_combatentes])
        print(f"Iniciativa: {fila_nomes}\n")

        for atacante in todos_combatentes:
            if not atacante.esta_vivo():
                continue

            herois_vivos = [h for h in time_herois if h.esta_vivo()]
            monstros_vivos = [m for m in time_monstros if m.esta_vivo()]

            if not herois_vivos or not monstros_vivos:
                break

            if isinstance(atacante, Personagem):
                if interativo:
                    print(f"\nComando: {atacante.nome} ({atacante.classe_nome}) | HP: {atacante.hp}/{atacante.max_hp} | MP: {atacante.mp}")
                    print("Escolha o Monstro Alvo:")
                    for idx, mon in enumerate(monstros_vivos, 1):
                        print(f"  [{idx}] {mon.nome} (HP: {mon.hp}/{mon.max_hp} | DEF: {mon.defense} | MDEF: {mon.mdefense})")

                    while True:
                        try:
                            escolha_alvo = int(input(f"Alvo (1 a {len(monstros_vivos)}): ").strip() or "1")
                            if 1 <= escolha_alvo <= len(monstros_vivos):
                                alvo = monstros_vivos[escolha_alvo - 1]
                                break
                            print("Número fora da lista.")
                        except ValueError:
                            print("Entrada inválida.")

                    print("Ação:")
                    print("  [1] Ataque Básico")
                    print("  [2] Habilidade Especial (gasta MP)")
                    while True:
                        escolha_acao = input("Opção (1 ou 2) [Padrão: 1]: ").strip() or "1"
                        if escolha_acao in ("1", "2"):
                            break
                        print("Digite 1 ou 2.")

                    if escolha_acao == "2" and atacante.mp >= 15:
                        _, msg = atacante.habilidade_especial(alvo)
                    else:
                        if escolha_acao == "2":
                            print(f"{Cores.AMARELO}Sem MP suficiente! Realizando ataque básico.{Cores.RESET}")
                        _, msg = atacante.atacar(alvo)
                else:
                    alvo = min(monstros_vivos, key=lambda m: m.hp)
                    if atacante.mp >= 20 and random.random() < 0.65:
                        _, msg = atacante.habilidade_especial(alvo)
                    else:
                        _, msg = atacante.atacar(alvo)
            else:
                _, msg = atacante.agir_ia(herois_vivos)

            print(f"  {msg}")
            if delay > 0:
                time.sleep(delay)

        for h in time_herois:
            h.regenerar_turno()

        rodada += 1

    herois_vivos_final = [h for h in time_herois if h.esta_vivo()]
    monstros_vivos_final = [m for m in time_monstros if m.esta_vivo()]

    print("\n" + "=" * 85)
    print(Cores.aplicar("FIM DA BATALHA 3v3", Cores.NEGRITO + Cores.AMARELO))
    print("=" * 85)

    if herois_vivos_final:
        print(f"{Cores.VERDE}{Cores.NEGRITO}Vitória dos Heróis!{Cores.RESET}")
        print(f"Sobreviventes ({len(herois_vivos_final)}/{len(time_herois)}):")
        for h in herois_vivos_final:
            print(f"  - {h.nome} ({h.classe_nome}) | HP: {h.hp}/{h.max_hp} | MP: {h.mp}/{h.max_mp}")
        print(f"Duração total: {rodada - 1} rodadas.")
        return True
    else:
        print(f"{Cores.VERMELHO}{Cores.NEGRITO}Os monstros venceram o confronto...{Cores.RESET}")
        print(f"Monstros Sobreviventes ({len(monstros_vivos_final)}/{len(time_monstros)}):")
        for m in monstros_vivos_final:
            print(f"  - {m.nome} | HP: {m.hp}/{m.max_hp}")
        return False


batalha_3v3 = simular_combate_3v3


# --- Fábricas de Personagens e Monstros ---

def criar_elenco_herois() -> List[Personagem]:
    return [
        Guerreiro("Aquiles de Atenas"),
        Mago("Merlin de Camelot"),
        Arqueiro("Atalanta de Ártemis"),
        Paladino("Brunhilda de Odin"),
        Assassino("Hanzo de Susanoo"),
        Necromante("Nefértis de Anúbis"),
    ]


def criar_elenco_monstros() -> List[Monstro]:
    return [
        Minotauro("Astérion do Labirinto"),
        Cerbero("Cérbero dos Portões"),
        Medusa("Medusa Petrificante"),
        Quimera("Quimera Flamejante"),
        Kraken("Kraken Abissal"),
        Esfinge("Esfinge das Dunas"),
    ]


# --- Interface de Console ---

def exibir_tabela_atributos() -> None:
    print("\n" + "=" * 88)
    print(Cores.aplicar("PANTEÃO DOS HERÓIS", Cores.NEGRITO + Cores.VERDE))
    print("=" * 88)
    print(f"{'Nome':<22} | {'Classe':<11} | {'HP':>4} | {'MP':>4} | {'SPD':>4} | {'ATK':>4} | {'MATK':>4} | {'DEF':>4} | {'MDEF':>4}")
    print("-" * 88)
    for h in criar_elenco_herois():
        print(f"{h.nome:<22} | {h.classe_nome:<11} | {h.max_hp:>4} | {h.max_mp:>4} | {h.speed:>4} | {h.atk:>4} | {h.matk:>4} | {h.defense:>4} | {h.mdefense:>4}")

    print("\n" + "=" * 88)
    print(Cores.aplicar("BESTIÁRIO DE MONSTROS", Cores.NEGRITO + Cores.VERMELHO))
    print("=" * 88)
    print(f"{'Nome':<22} | {'Origem':<18} | {'HP':>4} | {'MP':>4} | {'SPD':>4} | {'ATK':>4} | {'MATK':>4} | {'DEF':>4} | {'MDEF':>4}")
    print("-" * 88)
    for m in criar_elenco_monstros():
        print(f"{m.nome:<22} | {m.origem:<18} | {m.max_hp:>4} | {m.max_mp:>4} | {m.speed:>4} | {m.atk:>4} | {m.matk:>4} | {m.defense:>4} | {m.mdefense:>4}")
    print("-" * 88)


def cabecalho_jogo() -> None:
    titulo = r"""
  ╔═══════════════════════════════════════════════════════════════════════╗
  ║            ARENA DAS MITOLOGIAS - SISTEMA DE RPG (CP2)                ║
  ╚═══════════════════════════════════════════════════════════════════════╝
    """
    print(Cores.aplicar(titulo, Cores.CIANO + Cores.NEGRITO))


def menu_principal() -> None:
    while True:
        cabecalho_jogo()
        print(f"{Cores.NEGRITO}MENU PRINCIPAL:{Cores.RESET}")
        print("  [1] Duelo 1v1 Interativo (Você controla o Herói)")
        print("  [2] Duelo 1v1 Simulação Rápida (Execução automática narrada)")
        print("  [3] Batalha em Equipe 3v3 Interativa (Comande os 3 Heróis)")
        print("  [4] Batalha em Equipe 3v3 Simulação Rápida (Guerra épica narrada)")
        print("  [5] Panteão e Bestiário (Ver atributos de todos os combatentes)")
        print("  [0] Sair do Jogo")
        print("-" * 75)

        opcao = input("Digite a opção desejada: ").strip()

        if opcao == "1":
            herois = criar_elenco_herois()
            monstros = criar_elenco_monstros()

            print(f"\n{Cores.NEGRITO}Escolha seu herói:{Cores.RESET}")
            for i, h in enumerate(herois, 1):
                print(f"  [{i}] {h.nome} ({h.classe_nome} - {h.mitologia})")
            
            while True:
                escolha_h = input("Número do herói (1 a 6) [Padrão: 1]: ").strip() or "1"
                if escolha_h.isdigit() and 1 <= int(escolha_h) <= len(herois):
                    heroi_escolhido = herois[int(escolha_h) - 1]
                    break
                print("Escolha um número entre 1 e 6.")

            print(f"\n{Cores.NEGRITO}Escolha o monstro oponente:{Cores.RESET}")
            for i, m in enumerate(monstros, 1):
                print(f"  [{i}] {m.nome} ({m.origem})")
            
            while True:
                escolha_m = input("Número do monstro (1 a 6) [Padrão: 1]: ").strip() or "1"
                if escolha_m.isdigit() and 1 <= int(escolha_m) <= len(monstros):
                    monstro_escolhido = monstros[int(escolha_m) - 1]
                    break
                print("Escolha um número entre 1 e 6.")

            simular_combate_1v1(heroi_escolhido, monstro_escolhido, interativo=True, delay=0.3)
            input("\nPressione ENTER para voltar ao menu...")

        elif opcao == "2":
            herois = criar_elenco_herois()
            monstros = criar_elenco_monstros()
            h_auto = random.choice(herois)
            m_auto = random.choice(monstros)
            simular_combate_1v1(h_auto, m_auto, interativo=False, delay=0.3)
            input("\nPressione ENTER para voltar ao menu...")

        elif opcao == "3":
            herois = criar_elenco_herois()
            monstros = criar_elenco_monstros()

            print(f"\n{Cores.NEGRITO}Selecione os 3 heróis da sua equipe:{Cores.RESET}")
            for i, h in enumerate(herois, 1):
                print(f"  [{i}] {h.nome} ({h.classe_nome})")

            selecionados: List[Personagem] = []
            while len(selecionados) < 3:
                escolha = input(f"Herói #{len(selecionados) + 1} (1 a 6): ").strip()
                if escolha.isdigit() and 1 <= int(escolha) <= len(herois):
                    candidato = herois[int(escolha) - 1]
                    if candidato not in selecionados:
                        selecionados.append(candidato)
                        print(f"  {Cores.VERDE}{candidato.nome} adicionado.{Cores.RESET}")
                    else:
                        print("  Herói já escolhido. Escolha outro.")
                else:
                    print("  Digite um número entre 1 e 6.")

            monstros_desafiantes = random.sample(monstros, 3)
            simular_combate_3v3(selecionados, monstros_desafiantes, interativo=True, delay=0.3)
            input("\nPressione ENTER para voltar ao menu...")

        elif opcao == "4":
            herois = criar_elenco_herois()
            monstros = criar_elenco_monstros()
            t_herois = random.sample(herois, 3)
            t_monstros = random.sample(monstros, 3)
            simular_combate_3v3(t_herois, t_monstros, interativo=False, delay=0.35)
            input("\nPressione ENTER para voltar ao menu...")

        elif opcao == "5":
            exibir_tabela_atributos()
            input("\nPressione ENTER para voltar ao menu...")

        elif opcao == "0":
            print(f"\n{Cores.CIANO}Encerrando o jogo. Até a próxima!{Cores.RESET}")
            sys.exit(0)

        else:
            print("\nOpção inválida. Digite um número de 0 a 5.")


if __name__ == "__main__":
    menu_principal()
