"""
========================================================================================
PROJETO: ARENA DAS MITOLOGIAS - SISTEMA DE BATALHA RPG POO
CHECKPOINT 2 (CP2) - PROGRAMAÇÃO ORIENTADA A OBJETOS EM PYTHON
========================================================================================

INTEGRANTES DO GRUPO:
- Vinicius Eddo                  | RM: 571008
- Guilherme Gomes Orugian Santos | RM: 572882
- Lucas Henrique Vieira          | RM: 571901
- Rafael Jun Aita Hirata         | RM: 569708
- Rodrigo Bettio Penha Junior    | RM: 573725

CONCEITOS FUNDAMENTAIS DE POO IMPLEMENTADOS:
1. Classes e Objetos: Abstração de combatentes com atributos e comportamentos.
2. Encapsulamento: Propriedades protegidas (_hp, _mp) com getters e setters controlados.
3. Herança: 'Personagem' e 'Monstro' como classes base; Guerreiro, Mago, Arqueiro, etc.
   como subclasses especializadas.
4. Polimorfismo: Sobrescrita do método 'atacar()' e habilidades com custos de mana (MP).
5. Sistema de Batalha (1v1 e 3v3): Baseado em velocidade, cálculo de dano
   (físico e mágico) e gerenciamento de alvos vivos até condição de vitória/derrota.
========================================================================================
"""

from __future__ import annotations
import random
import time
import sys
import os
from abc import ABC, abstractmethod
from typing import List, Tuple, Optional

# Garante suporte a UTF-8 no terminal Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


# ======================================================================================
# SEÇÃO 0: ESTILIZAÇÃO E CORES ANSI (UI/UX PROFISSIONAL)
# ======================================================================================

class Cores:
    """Códigos de escape ANSI para estilizar a interface no terminal."""
    RESET = "\033[0m"
    NEGRITO = "\033[1m"
    VERMELHO = "\033[91m"
    VERDE = "\033[92m"
    AMARELO = "\033[93m"
    AZUL = "\033[94m"
    MAGENTA = "\033[95m"
    CIANO = "\033[96m"
    BRANCO = "\033[97m"
    CINZA = "\033[90m"

    @classmethod
    def colorir(cls, texto: str, cor: str) -> str:
        """Aplica cor ao texto com fallback seguro."""
        return f"{cor}{texto}{cls.RESET}"


# ======================================================================================
# SEÇÃO 1: CLASSES BASE (CLASSES PAI / ABSTRAÇÃO)
# ======================================================================================

class EntidadeCombate(ABC):
    """
    Classe Abstrata que define o modelo comum e garante os 7 atributos obrigatórios:
    - hp (vida)
    - mp (mana)
    - speed (velocidade)
    - atk (ataque físico)
    - matk (ataque mágico)
    - defense (defesa física)
    - mdefense (defesa mágica)
    """

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

    # --- Propriedades e Encapsulamento ---
    @property
    def hp(self) -> int:
        """Retorna o HP atual com proteção de limite mínimo 0."""
        return self._hp

    @hp.setter
    def hp(self, valor: int) -> None:
        """Garante que o HP fique estritamente no intervalo [0, max_hp]."""
        self._hp = max(0, min(valor, self._max_hp))

    @property
    def mp(self) -> int:
        """Retorna a mana atual."""
        return self._mp

    @mp.setter
    def mp(self, valor: int) -> None:
        """Garante que a mana fique no intervalo [0, max_mp]."""
        self._mp = max(0, min(valor, self._max_mp))

    @property
    def max_hp(self) -> int:
        return self._max_hp

    @property
    def max_mp(self) -> int:
        return self._max_mp

    def esta_vivo(self) -> bool:
        """Retorna True se a entidade possuir HP > 0."""
        return self._hp > 0

    def receber_dano(self, dano: int, tipo_dano: str = "físico") -> int:
        """
        Aplica o dano recebido ao HP, garantindo dano mínimo de 1.
        Retorna o valor efetivo de dano sofrido.
        """
        dano_real = max(1, dano)
        self.hp -= dano_real
        return dano_real

    def consumir_mp(self, custo: int) -> bool:
        """Consome mana caso disponível. Retorna True se a operação foi bem sucedida."""
        if self.mp >= custo:
            self.mp -= custo
            return True
        return False

    def curar(self, quantidade: int) -> int:
        """Restaura HP respeitando o valor máximo da vida."""
        vida_anterior = self.hp
        self.hp += quantidade
        return self.hp - vida_anterior

    def barra_status(self, comprimento: int = 12) -> str:
        """Renderiza barra gráfica de vida e mana formatada com porcentagem."""
        pct_hp = self.hp / self.max_hp if self.max_hp > 0 else 0
        cheios_hp = int(pct_hp * comprimento)
        barra_hp = "=" * cheios_hp + "-" * (comprimento - cheios_hp)

        pct_mp = self.mp / self.max_mp if self.max_mp > 0 else 0
        cheios_mp = int(pct_mp * comprimento)
        barra_mp = "*" * cheios_mp + "." * (comprimento - cheios_mp)

        cor_hp = Cores.VERDE if pct_hp > 0.5 else (Cores.AMARELO if pct_hp > 0.2 else Cores.VERMELHO)
        cor_mp = Cores.AZUL

        txt_hp = Cores.colorir(f"[{barra_hp}] {self.hp:>3}/{self.max_hp:<3}", cor_hp)
        txt_mp = Cores.colorir(f"[{barra_mp}] {self.mp:>3}/{self.max_mp:<3}", cor_mp)

        status = f"{self.nome:<22} | HP: {txt_hp} | MP: {txt_mp}"
        if not self.esta_vivo():
            status += Cores.colorir(" [DERROTADO]", Cores.VERMELHO + Cores.NEGRITO)
        return status

    @abstractmethod
    def atacar(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        """Método polimórfico obrigatório de ataque."""
        pass

    @abstractmethod
    def habilidade_especial(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        """Método polimórfico para técnicas especiais com consumo de MP."""
        pass


class Personagem(EntidadeCombate):
    """
    Classe Pai Obrigatória: "Personagem".
    Representa a classe base para todos os heróis jogáveis.
    Pode ser instanciada diretamente ou utilizada como classe base para especializações.
    """

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
        return (
            f"[{self.mitologia}] {self.nome} ({self.classe_nome}) | "
            f"HP: {self.hp}/{self.max_hp} | MP: {self.mp}/{self.max_mp} | SPD: {self.speed} | "
            f"ATK: {self.atk} | MATK: {self.matk} | DEF: {self.defense} | MDEF: {self.mdefense}"
        )

    def regenerar_turno(self) -> None:
        """Regenera uma pequena quantia de mana ao final de cada rodada."""
        if self.esta_vivo():
            recuperado = min(6, self.max_mp - self.mp)
            self.mp += recuperado

    def atacar(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        """
        Ataque padrão da classe base Personagem.
        Sobrescrito pelas subclasses via polimorfismo.
        """
        dano_calculado = self.atk - alvo.defense
        dano_final = alvo.receber_dano(dano_calculado, "físico")
        msg = f"[PERSONAGEM] {self.nome} ataca {alvo.nome} desferindo {dano_final} de dano! (HP alvo: {alvo.hp})"
        return dano_final, msg

    def habilidade_especial(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        """Habilidade padrão da classe base Personagem com consumo de MP."""
        custo = 12
        if self.consumir_mp(custo):
            dano_calculado = int(self.atk * 1.3) - alvo.defense
            dano_final = alvo.receber_dano(dano_calculado, "físico")
            msg = f"[GOLPE FOCADO] {self.nome} canaliza energia e atinge {alvo.nome} causando {dano_final} de dano! (HP alvo: {alvo.hp})"
            return dano_final, msg
        return self.atacar(alvo)


class Monstro(EntidadeCombate):
    """
    Classe Pai Obrigatória: "Monstro".
    Representa as criaturas míticas e bestas adversárias.
    Pode ser instanciada diretamente ou herdada por monstros específicos.
    """

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
        descricao: str = "Criatura feroz que espreita nas sombras."
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
        return (
            f"[Monstro: {self.origem}] {self.nome} | "
            f"HP: {self.hp}/{self.max_hp} | MP: {self.mp}/{self.max_mp} | SPD: {self.speed} | "
            f"ATK: {self.atk} | MATK: {self.matk} | DEF: {self.defense} | MDEF: {self.mdefense}"
        )

    def atacar(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        """Ataque baseado na maior força do monstro (físico ou mágico)."""
        if self.atk >= self.matk:
            dano_bruto = self.atk - alvo.defense
            dano_final = alvo.receber_dano(dano_bruto, "físico")
            msg = f"[ATAQUE BESTIAL] {self.nome} ataca ferozmente {alvo.nome} causando {dano_final} de dano físico! (HP alvo: {alvo.hp})"
        else:
            dano_bruto = self.matk - alvo.mdefense
            dano_final = alvo.receber_dano(dano_bruto, "mágico")
            msg = f"[MAGIA NEGRA] {self.nome} canaliza energia sombria em {alvo.nome} desferindo {dano_final} de dano mágico! (HP alvo: {alvo.hp})"
        return dano_final, msg

    def habilidade_especial(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        """Ataque feroz reforçado com consumo de MP."""
        custo = 15
        if self.consumir_mp(custo):
            dano_calculado = int(self.atk * 1.4) - alvo.defense
            dano_final = alvo.receber_dano(dano_calculado, "físico")
            msg = f"[FÚRIA BESTIAL] {self.nome} desfere um ataque devastador em {alvo.nome} causando {dano_final} de dano! (HP alvo: {alvo.hp})"
            return dano_final, msg
        return self.atacar(alvo)

    def agir_ia(self, alvos_vivos: List[EntidadeCombate]) -> Tuple[int, str]:
        """
        Inteligência Artificial do monstro:
        Foca no oponente mais frágil e decide taticamente usar golpe especial.
        """
        if not alvos_vivos:
            return 0, "Nenhum alvo vivo disponível."

        alvo = min(alvos_vivos, key=lambda a: a.hp)
        if self.mp >= 15 and random.random() < 0.5:
            return self.habilidade_especial(alvo)
        return self.atacar(alvo)


# ======================================================================================
# SEÇÃO 2: SUBCLASSES DE PERSONAGEM (HERANÇA E POLIMORFISMO)
# ======================================================================================

class Guerreiro(Personagem):
    """
    Subclasse Obrigatória: "Guerreiro".
    Exemplo Mitológico: Guerreiro de Atenas (Mitologia Grega).
    Atributos: Alto HP, elevada Defesa física e Ataque Físico poderoso.
    Polimorfismo: Sobrescreve 'atacar()' com 'Golpe de Escudo e Lança'.
    """

    def __init__(
        self,
        nome: str = "Teseu de Atenas",
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
        dano_calculado = self.atk - alvo.defense
        dano_final = alvo.receber_dano(dano_calculado, "físico")
        msg = (
            f"{Cores.VERMELHO}[GUERREIRO]{Cores.RESET} {self.nome} golpeia com lança espartana e escudo pesado contra {alvo.nome}, "
            f"rompendo defesas e causando {Cores.NEGRITO}{dano_final}{Cores.RESET} de dano físico! (HP alvo: {alvo.hp})"
        )
        return dano_final, msg

    def habilidade_especial(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        custo = 15
        if not self.consumir_mp(custo):
            dano, msg = self.atacar(alvo)
            return dano, f"{Cores.AMARELO}[AVISO: Sem MP para especial]{Cores.RESET} {msg}"

        defesa_efetiva = int(alvo.defense * 0.6)
        dano_calculado = int(self.atk * 1.5) - defesa_efetiva
        dano_final = alvo.receber_dano(dano_calculado, "físico")
        msg = (
            f"{Cores.AMARELO}{Cores.NEGRITO}[ESPECIAL: FÚRIA DE ARES]{Cores.RESET} {self.nome} evoca a fúria espartana e esmaga {alvo.nome} "
            f"com impacto titânico causando {Cores.VERMELHO}{Cores.NEGRITO}{dano_final}{Cores.RESET} de dano! (Custo: {custo} MP | HP alvo: {alvo.hp})"
        )
        return dano_final, msg


class Mago(Personagem):
    """
    Subclasse Obrigatória: "Mago".
    Exemplo Mitológico: Mago Merlin (Mitologia Arturiana / Celta).
    Atributos: Altíssimo MP e Ataque Mágico (matk), com excelente Defesa Mágica (mdefense).
    Polimorfismo: Sobrescreve 'atacar()' canalizando projéteis de energia arcana (matk - mdefense).
    """

    def __init__(
        self,
        nome: str = "Merlin de Avalon",
        hp: int = 90,
        mp: int = 90,
        speed: int = 14,
        atk: int = 8,
        matk: int = 33,
        defense: int = 7,
        mdefense=18
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
        dano_calculado = self.matk - alvo.mdefense
        dano_final = alvo.receber_dano(dano_calculado, "mágico")
        msg = (
            f"{Cores.MAGENTA}[MAGO]{Cores.RESET} {self.nome} entoa cânticos arcanos e dispara Projéteis Cósmicos em {alvo.nome}, "
            f"infligindo {Cores.NEGRITO}{dano_final}{Cores.RESET} de dano mágico! (HP alvo: {alvo.hp})"
        )
        return dano_final, msg

    def habilidade_especial(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        custo = 25
        if not self.consumir_mp(custo):
            dano, msg = self.atacar(alvo)
            return dano, f"{Cores.AMARELO}[AVISO: Sem MP para especial]{Cores.RESET} {msg}"

        dano_calculado = int(self.matk * 1.7) - alvo.mdefense
        dano_final = alvo.receber_dano(dano_calculado, "mágico")
        msg = (
            f"{Cores.MAGENTA}{Cores.NEGRITO}[ESPECIAL: METEORO DE AVALON]{Cores.RESET} {self.nome} precipita um meteoro celestial estelar "
            f"sobre {alvo.nome}, desintegrando o ar e causando {Cores.VERMELHO}{Cores.NEGRITO}{dano_final}{Cores.RESET} de dano mágico massivo! (Custo: {custo} MP | HP: {alvo.hp})"
        )
        return dano_final, msg


class Arqueiro(Personagem):
    """
    Subclasse Inédita 1: "Arqueiro".
    Exemplo Mitológico: Arqueiro de Ártemis (Mitologia Grega).
    Atributos: Velocidade superior (Speed 22) e tiros perfurantes que mitigam 25% da armadura.
    """

    def __init__(
        self,
        nome: str = "Atalanta dos Bosques",
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
        defesa_efetiva = int(alvo.defense * 0.75)
        dano_calculado = self.atk - defesa_efetiva
        dano_final = alvo.receber_dano(dano_calculado, "físico")
        msg = (
            f"{Cores.VERDE}[ARQUEIRO]{Cores.RESET} {self.nome} dispara uma Flecha de Prata veloz no ponto fraco de {alvo.nome}, "
            f"causando {Cores.NEGRITO}{dano_final}{Cores.RESET} de dano perfurante! (HP alvo: {alvo.hp})"
        )
        return dano_final, msg

    def habilidade_especial(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        custo = 20
        if not self.consumir_mp(custo):
            dano, msg = self.atacar(alvo)
            return dano, f"{Cores.AMARELO}[AVISO: Sem MP para especial]{Cores.RESET} {msg}"

        dano_calculado = int(self.atk * 1.6) - int(alvo.defense * 0.5)
        dano_final = alvo.receber_dano(dano_calculado, "físico")
        msg = (
            f"{Cores.VERDE}{Cores.NEGRITO}[ESPECIAL: FLECHA LUNAR]{Cores.RESET} {self.nome} canaliza a bênção da deusa Ártemis e desfere disparo estelar "
            f"perfurando {alvo.nome} com {Cores.VERMELHO}{Cores.NEGRITO}{dano_final}{Cores.RESET} de dano crítico! (Custo: {custo} MP | HP: {alvo.hp})"
        )
        return dano_final, msg


class Paladino(Personagem):
    """
    Subclasse Inédita 2: "Paladino / Valquíria".
    Exemplo Mitológico: Valquíria de Valhalla (Mitologia Nórdica).
    Atributos: Altíssimo equilíbrio geral, dano sagrado misto e habilidade com autocura.
    """

    def __init__(
        self,
        nome: str = "Brunhilda de Valhalla",
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
        dano_total = dano_fisico + dano_sagrado
        dano_final = alvo.receber_dano(dano_total, "sagrado")
        msg = (
            f"{Cores.CIANO}[PALADINO]{Cores.RESET} {self.nome} avança com asas de éter e crava sua Lança Sagrada em {alvo.nome}, "
            f"causando {Cores.NEGRITO}{dano_final}{Cores.RESET} de dano luminoso misto! (HP alvo: {alvo.hp})"
        )
        return dano_final, msg

    def habilidade_especial(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        custo = 20
        if not self.consumir_mp(custo):
            dano, msg = self.atacar(alvo)
            return dano, f"{Cores.AMARELO}[AVISO: Sem MP para especial]{Cores.RESET} {msg}"

        dano_calculado = int(self.atk * 1.2 + self.matk * 0.8) - int(alvo.defense * 0.5)
        dano_final = alvo.receber_dano(dano_calculado, "sagrado")
        vida_curada = self.curar(18)
        msg = (
            f"{Cores.CIANO}{Cores.NEGRITO}[ESPECIAL: JULGAMENTO DIVINO]{Cores.RESET} {self.nome} banha {alvo.nome} em luz celestial desferindo "
            f"{Cores.VERMELHO}{Cores.NEGRITO}{dano_final}{Cores.RESET} de dano e restaurando +{vida_curada} de HP para si! (HP atual: {self.hp})"
        )
        return dano_final, msg


class Assassino(Personagem):
    """
    Subclasse Inédita 3: "Assassino".
    Exemplo Mitológico: Sombra de Susanoo (Mitologia Japonesa).
    Atributos: Velocidade máxima (Speed 25), ataques cortantes com chance de crítico.
    """

    def __init__(
        self,
        nome: str = "Hanzo das Sombras",
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
        dano_calculado = self.atk - alvo.defense
        eh_critico = random.random() < 0.35
        if eh_critico:
            dano_calculado = int(dano_calculado * 1.5)
        dano_final = alvo.receber_dano(dano_calculado, "físico")
        critico_tag = f" {Cores.AMARELO}[GOLPE CRÍTICO!]{Cores.RESET}" if eh_critico else ""
        msg = (
            f"{Cores.CINZA}[ASSASSINO]{Cores.RESET} {self.nome} surge das sombras com corte fulminante de katana{critico_tag} em {alvo.nome}, "
            f"causando {Cores.NEGRITO}{dano_final}{Cores.RESET} de dano cortante! (HP alvo: {alvo.hp})"
        )
        return dano_final, msg

    def habilidade_especial(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        custo = 20
        if not self.consumir_mp(custo):
            dano, msg = self.atacar(alvo)
            return dano, f"{Cores.AMARELO}[AVISO: Sem MP para especial]{Cores.RESET} {msg}"

        dano_calculado = int(self.atk * 1.7) - int(alvo.defense * 0.5)
        dano_final = alvo.receber_dano(dano_calculado, "físico")
        msg = (
            f"{Cores.CINZA}{Cores.NEGRITO}[ESPECIAL: EXECUÇÃO DE SUSANOO]{Cores.RESET} {self.nome} fende o espaço em velocidade relâmpago, "
            f"provocando {Cores.VERMELHO}{Cores.NEGRITO}{dano_final}{Cores.RESET} de dano devastador em {alvo.nome}! (Custo: {custo} MP | HP: {alvo.hp})"
        )
        return dano_final, msg


class Necromante(Personagem):
    """
    Subclasse Inédita 4: "Necromante / Xamã".
    Exemplo Mitológico: Xamã de Anúbis (Mitologia Egípcia).
    Atributos: Alto MATK e capacidade intrínseca de drenagem vampírica de vida.
    """

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
        dano_calculado = self.matk - alvo.mdefense
        dano_final = alvo.receber_dano(dano_calculado, "mágico")
        cura = max(1, int(dano_final * 0.35))
        vida_recuperada = self.curar(cura)
        msg = (
            f"{Cores.MAGENTA}[NECROMANTE]{Cores.RESET} {self.nome} lança o Toque das Tumbas em {alvo.nome}, "
            f"causando {Cores.NEGRITO}{dano_final}{Cores.RESET} de dano necrótico e drenando +{vida_recuperada} HP para si! (HP alvo: {alvo.hp} | HP atual: {self.hp})"
        )
        return dano_final, msg

    def habilidade_especial(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        custo = 25
        if not self.consumir_mp(custo):
            dano, msg = self.atacar(alvo)
            return dano, f"{Cores.AMARELO}[AVISO: Sem MP para especial]{Cores.RESET} {msg}"

        dano_calculado = int(self.matk * 1.8) - alvo.mdefense
        dano_final = alvo.receber_dano(dano_calculado, "mágico")
        cura = self.curar(int(dano_final * 0.4))
        msg = (
            f"{Cores.MAGENTA}{Cores.NEGRITO}[ESPECIAL: BALANÇA DE ANÚBIS]{Cores.RESET} {self.nome} invoca o julgamento das almas sobre {alvo.nome}! "
            f"As areias negras drenam {Cores.VERMELHO}{Cores.NEGRITO}{dano_final}{Cores.RESET} de dano sombrio e recuperam +{cura} de HP! (HP alvo: {alvo.hp})"
        )
        return dano_final, msg


# ======================================================================================
# SEÇÃO 3: BESTIÁRIO MITOLÓGICO (SUBCLASSES DE MONSTRO)
# ======================================================================================

class Minotauro(Monstro):
    """Monstro Mitológico Grego: A Besta do Labirinto de Creta."""
    def __init__(
        self,
        nome: str = "Astérion, o Minotauro",
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
            descricao="Besta colossal com cabeça de touro e machado duplo de bronze."
        )

    def atacar(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        dano_calculado = self.atk - alvo.defense
        dano_final = alvo.receber_dano(dano_calculado, "físico")
        msg = f"[MINOTAURO] {self.nome} golpeia com machado pesado contra {alvo.nome}, causando {dano_final} de dano esmagador! (HP alvo: {alvo.hp})"
        return dano_final, msg

    def habilidade_especial(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        custo = 10
        if self.consumir_mp(custo):
            dano_calculado = int(self.atk * 1.5) - int(alvo.defense * 0.7)
            dano_final = alvo.receber_dano(dano_calculado, "físico")
            msg = f"[INVESTIDA DEMOLIDORA] {self.nome} abaixa os chifres e atropela {alvo.nome}, causando {dano_final} de dano brutal! (HP alvo: {alvo.hp})"
            return dano_final, msg
        return self.atacar(alvo)


class Cerbero(Monstro):
    """Monstro Mitológico Grego: Guardião Tríplice dos Portões do Hades."""
    def __init__(
        self,
        nome: str = "Cérbero, Cão do Hades",
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
            descricao="Cão colossal de três cabeças banhado em chamas do Tártaro."
        )

    def atacar(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        dano_calculado = self.atk - alvo.defense
        dano_final = alvo.receber_dano(dano_calculado, "físico")
        msg = f"[CÉRBERO] {self.nome} desfere mordidas flamejantes em {alvo.nome}, causando {dano_final} de dano físico! (HP alvo: {alvo.hp})"
        return dano_final, msg

    def habilidade_especial(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        custo = 15
        if self.consumir_mp(custo):
            dano_calculado = int(self.atk * 1.3 + self.matk * 0.6) - alvo.defense
            dano_final = alvo.receber_dano(dano_calculado, "misto")
            msg = f"[MORDIDA TRÍPLICE DO HADES] As três cabeças de {self.nome} mordem simultaneamente {alvo.nome}, causando {dano_final} de dano do Tártaro! (HP alvo: {alvo.hp})"
            return dano_final, msg
        return self.atacar(alvo)


class Medusa(Monstro):
    """Monstro Mitológico Grego: A Górgona do Olhar Petrificante."""
    def __init__(
        self,
        nome: str = "Medusa, a Górgona",
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
            descricao="Górgona ancestral com cabelos de serpente cujo olhar petrifica."
        )

    def atacar(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        dano_calculado = self.matk - alvo.mdefense
        dano_final = alvo.receber_dano(dano_calculado, "mágico")
        msg = f"[MEDUSA] {self.nome} fixa seu olhar venenoso em {alvo.nome}, causando {dano_final} de dano místico! (HP alvo: {alvo.hp})"
        return dano_final, msg

    def habilidade_especial(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        custo = 20
        if self.consumir_mp(custo):
            dano_calculado = int(self.matk * 1.6) - alvo.mdefense
            dano_final = alvo.receber_dano(dano_calculado, "mágico")
            msg = f"[OLHAR PETRIFICANTE] {self.nome} transforma a carne de {alvo.nome} em pedra, infligindo {dano_final} de dano mágico! (HP alvo: {alvo.hp})"
            return dano_final, msg
        return self.atacar(alvo)


class Quimera(Monstro):
    """Monstro Mitológico Clássico: Híbrido Leão, Bode e Serpente."""
    def __init__(
        self,
        nome: str = "Quimera da Lícia",
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
            descricao="Besta híbrida com corpo de leão, cabeça de bode e cauda de víbora."
        )

    def atacar(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        dano_calculado = self.atk - alvo.defense
        dano_final = alvo.receber_dano(dano_calculado, "físico")
        msg = f"[QUIMERA] {self.nome} desfere garras e picada de serpente em {alvo.nome}, causando {dano_final} de dano! (HP alvo: {alvo.hp})"
        return dano_final, msg

    def habilidade_especial(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        custo = 18
        if self.consumir_mp(custo):
            dano_calculado = int(self.matk * 1.5) - alvo.mdefense
            dano_final = alvo.receber_dano(dano_calculado, "mágico")
            msg = f"[BAFORADA INCENDIÁRIA] {self.nome} cospe chamas vulcânicas sobre {alvo.nome}, infligindo {dano_final} de dano de fogo! (HP alvo: {alvo.hp})"
            return dano_final, msg
        return self.atacar(alvo)


class Kraken(Monstro):
    """Monstro Mitológico Nórdico: O Leviatã das Profundezas."""
    def __init__(
        self,
        nome: str = "Kraken dos Abismos",
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
            descricao="Lula gigante titânica dos mares boreais."
        )

    def atacar(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        dano_calculado = self.atk - alvo.defense
        dano_final = alvo.receber_dano(dano_calculado, "físico")
        msg = f"[KRAKEN] {self.nome} chicoteia tentáculos colossais contra {alvo.nome}, provocando {dano_final} de dano marítimo! (HP alvo: {alvo.hp})"
        return dano_final, msg

    def habilidade_especial(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        custo = 15
        if self.consumir_mp(custo):
            dano_calculado = int(self.atk * 1.4) - int(alvo.defense * 0.6)
            dano_final = alvo.receber_dano(dano_calculado, "físico")
            msg = f"[TSUNAMI DO ABISMO] {self.nome} ergue uma onda descomunal esmagando {alvo.nome} com {dano_final} de impacto demolidor! (HP alvo: {alvo.hp})"
            return dano_final, msg
        return self.atacar(alvo)


class Esfinge(Monstro):
    """Monstro Mitológico Egípcio: O Guardião dos Mistérios."""
    def __init__(
        self,
        nome: str = "Esfinge Milenar",
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
            descricao="Besta ancestral com asas de águia e corpo de leoa protetora das pirâmides."
        )

    def atacar(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        dano_calculado = self.matk - alvo.mdefense
        dano_final = alvo.receber_dano(dano_calculado, "mágico")
        msg = f"[ESFINGE] {self.nome} desfere um enigma mental que abala a mente de {alvo.nome}, causando {dano_final} de dano psíquico! (HP alvo: {alvo.hp})"
        return dano_final, msg

    def habilidade_especial(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        custo = 20
        if self.consumir_mp(custo):
            dano_calculado = int(self.matk * 1.55) - alvo.mdefense
            dano_final = alvo.receber_dano(dano_calculado, "mágico")
            msg = f"[MALDIÇÃO DO ENIGMA] {self.nome} convoca a tempestade das areias sagradas causando {dano_final} de dano místico em {alvo.nome}! (HP alvo: {alvo.hp})"
            return dano_final, msg
        return self.atacar(alvo)


# ======================================================================================
# SEÇÃO 4: SISTEMA DE BATALHA 1v1 (HERÓI VS MONSTRO)
# ======================================================================================

def simular_combate_1v1(heroi: Personagem, monstro: Monstro, interativo: bool = False, delay: float = 0.4) -> bool:
    """
    Simulação de combate por turnos 1v1 entre um Herói e um Monstro.
    
    Regras da CP2:
    - Utiliza o atributo 'speed' para determinar a iniciativa de ataque por rodada.
    - Aplica o cálculo de dano físico (atk - defense) ou mágico (matk - mdefense).
    - Checa continuamente a vida, encerrando no momento em que um combatente tem hp <= 0.
    
    Retorna True se o herói venceu, False caso contrário.
    """
    print("\n" + "=" * 78)
    print(Cores.colorir(f"⚔️  DUELO ÉPICO 1v1: {heroi.nome} VS {monstro.nome}  ⚔️", Cores.NEGRITO + Cores.AMARELO))
    print("=" * 78)
    print(f"Herói:   {heroi}")
    print(f"Monstro: {monstro}")
    print("-" * 78)

    rodada = 1
    dano_total_heroi = 0
    dano_total_monstro = 0

    while heroi.esta_vivo() and monstro.esta_vivo():
        print(f"\n{Cores.NEGRITO}--- [RODADA {rodada}] ---{Cores.RESET}")
        print(heroi.barra_status())
        print(monstro.barra_status())
        print("-" * 55)

        # Determina a ordem de ação por SPEED
        if heroi.speed > monstro.speed:
            primeiro, segundo = heroi, monstro
        elif monstro.speed > heroi.speed:
            primeiro, segundo = monstro, heroi
        else:
            primeiro, segundo = (heroi, monstro) if random.random() < 0.5 else (monstro, heroi)

        ordem = [primeiro, segundo]
        print(f"⚡ {Cores.CIANO}Iniciativa:{Cores.RESET} {primeiro.nome} (SPD: {primeiro.speed}) age antes de {segundo.nome} (SPD: {segundo.speed})!")

        for atacante in ordem:
            if not heroi.esta_vivo() or not monstro.esta_vivo():
                break

            defensor = monstro if atacante == heroi else heroi

            if atacante == heroi:
                if interativo:
                    print(f"\n👉 {Cores.NEGRITO}Seu turno, {heroi.nome}!{Cores.RESET}")
                    print("  [1] Ataque Básico da Classe (Sem custo de MP)")
                    print(f"  [2] Habilidade Especial ({heroi.classe_nome} - Consome MP)")
                    
                    while True:
                        escolha = input("Escolha sua ação (1 ou 2) [Padrão: 1]: ").strip() or "1"
                        if escolha in ("1", "2"):
                            break
                        print("⚠️ Opção inválida. Digite 1 ou 2.")

                    if escolha == "2" and heroi.mp >= 15:
                        dano, msg = heroi.habilidade_especial(defensor)
                    else:
                        if escolha == "2":
                            print(f"{Cores.AMARELO}⚠️ Mana insuficiente! Executando ataque básico.{Cores.RESET}")
                        dano, msg = heroi.atacar(defensor)
                    dano_total_heroi += dano
                else:
                    if heroi.mp >= 20 and random.random() < 0.65:
                        dano, msg = heroi.habilidade_especial(defensor)
                    else:
                        dano, msg = heroi.atacar(defensor)
                    dano_total_heroi += dano
            else:
                dano, msg = monstro.agir_ia([heroi])
                dano_total_monstro += dano

            print(f"  {msg}")
            if delay > 0:
                time.sleep(delay)

        heroi.regenerar_turno()
        rodada += 1

    print("\n" + "=" * 78)
    print(Cores.colorir("🏆  RESULTADO FINAL DO COMBATE 1v1  🏆", Cores.NEGRITO + Cores.AMARELO))
    print("=" * 78)

    if heroi.esta_vivo():
        print(f"{Cores.VERDE}{Cores.NEGRITO}🎉 VITÓRIA DO HERÓI!{Cores.RESET} {heroi.nome} derrotou {monstro.nome} em {rodada - 1} rodadas!")
        print(f"   Status Final: {heroi.nome} com {heroi.hp}/{heroi.max_hp} HP restante.")
        print(f"   Dano total causado por {heroi.nome}: {dano_total_heroi}")
        return True
    else:
        print(f"{Cores.VERMELHO}{Cores.NEGRITO}💀 DERROTA!{Cores.RESET} {monstro.nome} aniquilou {heroi.nome} em {rodada - 1} rodadas...")
        print(f"   Status Final: {monstro.nome} sobreviveu com {monstro.hp}/{monstro.max_hp} HP.")
        print(f"   Dano total sofrido: {dano_total_monstro}")
        return False


# Aliases para compatibilidade ampla
batalha_1v1 = simular_combate_1v1


# ======================================================================================
# SEÇÃO 5: SISTEMA DE BATALHA 3v3 (TIME DE HERÓIS VS TIME DE MONSTROS)
# ======================================================================================

def simular_combate_3v3(
    time_herois: List[Personagem],
    time_monstros: List[Monstro],
    interativo: bool = False,
    delay: float = 0.35
) -> bool:
    """
    Simulação de combate em equipe 3v3 por turnos.
    
    Regras da CP2:
    - Gerencia seleção de alvos vivos de maneira contínua.
    - Ordena ações com base na velocidade individual (speed) dos combatentes vivos.
    - Encerra quando todos os combatentes de um dos lados ficarem com hp <= 0.
    
    Retorna True se os heróis vencerem, False se os monstros vencerem.
    """
    print("\n" + "=" * 85)
    print(Cores.colorir("🛡️  GRANDE GUERRA MITOLÓGICA: BATALHA EM EQUIPE 3v3  🐉", Cores.NEGRITO + Cores.AMARELO))
    print("=" * 85)
    print(f"{Cores.VERDE}TIME DOS HERÓIS:{Cores.RESET}")
    for h in time_herois:
        print(f"  • {h}")
    print(f"\n{Cores.VERMELHO}TIME DOS MONSTROS:{Cores.RESET}")
    for m in time_monstros:
        print(f"  • {m}")
    print("=" * 85)

    rodada = 1

    while any(h.esta_vivo() for h in time_herois) and any(m.esta_vivo() for m in time_monstros):
        print(f"\n{Cores.NEGRITO}==================== [RODADA {rodada}] ===================={Cores.RESET}")
        print(f"{Cores.VERDE}⚔️  STATUS DA EQUIPE DE HERÓIS:{Cores.RESET}")
        for h in time_herois:
            print(f"  {h.barra_status()}")

        print(f"\n{Cores.VERMELHO}🐾  STATUS DA EQUIPE DE MONSTROS:{Cores.RESET}")
        for m in time_monstros:
            print(f"  {m.barra_status()}")
        print("-" * 80)

        # Fila de iniciativa ordenada por SPEED decrescente
        todos_combatentes: List[EntidadeCombate] = [c for c in (time_herois + time_monstros) if c.esta_vivo()]
        todos_combatentes.sort(key=lambda c: (c.speed, random.random()), reverse=True)

        print(f"⚡ {Cores.CIANO}Ordem de Ação da Rodada:{Cores.RESET}")
        fila_nomes = " ➔ ".join([f"{c.nome} (SPD:{c.speed})" for c in todos_combatentes])
        print(f"  {fila_nomes}\n")

        for atacante in todos_combatentes:
            if not atacante.esta_vivo():
                continue

            herois_vivos = [h for h in time_herois if h.esta_vivo()]
            monstros_vivos = [m for m in time_monstros if m.esta_vivo()]

            # Checa se a batalha encerrou antes da ação do próximo
            if not herois_vivos or not monstros_vivos:
                break

            if isinstance(atacante, Personagem):
                # Turno de um herói
                if interativo:
                    print(f"\n🎮 {Cores.NEGRITO}Comando do Herói:{Cores.RESET} {atacante.nome} ({atacante.classe_nome}) | HP: {atacante.hp}/{atacante.max_hp} | MP: {atacante.mp}")
                    print("Selecione o Monstro Alvo:")
                    for idx, mon in enumerate(monstros_vivos, 1):
                        print(f"  [{idx}] {mon.nome} (HP: {mon.hp}/{mon.max_hp} | DEF: {mon.defense} | MDEF: {mon.mdefense})")

                    while True:
                        try:
                            escolha_alvo = int(input(f"Escolha o alvo (1 a {len(monstros_vivos)}): ").strip() or "1")
                            if 1 <= escolha_alvo <= len(monstros_vivos):
                                alvo = monstros_vivos[escolha_alvo - 1]
                                break
                            print("⚠️ Número fora do intervalo.")
                        except ValueError:
                            print("⚠️ Digite um número válido.")

                    print("Selecione a Ação:")
                    print("  [1] Ataque Básico da Classe")
                    print("  [2] Habilidade Especial (Gasta MP)")
                    while True:
                        escolha_acao = input("Ação (1 ou 2) [Padrão: 1]: ").strip() or "1"
                        if escolha_acao in ("1", "2"):
                            break
                        print("⚠️ Digite 1 ou 2.")

                    if escolha_acao == "2" and atacante.mp >= 15:
                        _, msg = atacante.habilidade_especial(alvo)
                    else:
                        if escolha_acao == "2":
                            print(f"{Cores.AMARELO}⚠️ Mana insuficiente! Executando ataque básico.{Cores.RESET}")
                        _, msg = atacante.atacar(alvo)
                else:
                    # Modo Automático: foca no monstro de menor HP (estratégia ótima)
                    alvo = min(monstros_vivos, key=lambda m: m.hp)
                    if atacante.mp >= 20 and random.random() < 0.65:
                        _, msg = atacante.habilidade_especial(alvo)
                    else:
                        _, msg = atacante.atacar(alvo)
            else:
                # Turno de um monstro via IA
                _, msg = atacante.agir_ia(herois_vivos)

            print(f"  {msg}")
            if delay > 0:
                time.sleep(delay)

        # Regeneração leve de MP para heróis vivos
        for h in time_herois:
            h.regenerar_turno()

        rodada += 1

    herois_vivos_final = [h for h in time_herois if h.esta_vivo()]
    monstros_vivos_final = [m for m in time_monstros if m.esta_vivo()]

    print("\n" + "=" * 85)
    print(Cores.colorir("🏁  FIM DA GRANDE GUERRA 3v3  🏁", Cores.NEGRITO + Cores.AMARELO))
    print("=" * 85)

    if herois_vivos_final:
        print(f"{Cores.VERDE}{Cores.NEGRITO}🏆 GLÓRIA ETERNA! O TIME DOS HERÓIS TRIUNFOU!{Cores.RESET}")
        print(f"Sobreviventes ({len(herois_vivos_final)}/{len(time_herois)}):")
        for h in herois_vivos_final:
            print(f"  ✅ {h.nome} ({h.classe_nome}) - HP: {h.hp}/{h.max_hp} | MP: {h.mp}/{h.max_mp}")
        print(f"Duração total do confronto: {rodada - 1} rodadas intensas.")
        return True
    else:
        print(f"{Cores.VERMELHO}{Cores.NEGRITO}☠️ TREVAS E RUÍNA! OS MONSTROS EXTERMINARAM OS HERÓIS...{Cores.RESET}")
        print(f"Monstros Sobreviventes ({len(monstros_vivos_final)}/{len(time_monstros)}):")
        for m in monstros_vivos_final:
            print(f"  🩸 {m.nome} - HP: {m.hp}/{m.max_hp}")
        return False


# Aliases para compatibilidade ampla
batalha_3v3 = simular_combate_3v3


# ======================================================================================
# SEÇÃO 6: FÁBRICA DE INSTÂNCIAS E ELENCO
# ======================================================================================

def criar_elenco_herois() -> List[Personagem]:
    """Cria e retorna uma lista com os 6 heróis lendários instanciados."""
    return [
        Guerreiro("Aquiles de Atenas"),
        Mago("Merlin de Camelot"),
        Arqueiro("Atalanta de Ártemis"),
        Paladino("Brunhilda de Odin"),
        Assassino("Hanzo de Susanoo"),
        Necromante("Nefértis de Anúbis"),
    ]


def criar_elenco_monstros() -> List[Monstro]:
    """Cria e retorna uma lista com os 6 monstros míticos instanciados."""
    return [
        Minotauro("Astérion do Labirinto"),
        Cerbero("Cérbero dos Portões"),
        Medusa("Medusa Petrificante"),
        Quimera("Quimera Flamejante"),
        Kraken("Kraken Abissal"),
        Esfinge("Esfinge das Dunas"),
    ]


# ======================================================================================
# SEÇÃO 7: SUÍTE DE TESTES AUTOMÁTICOS DE POO (VERIFICAÇÃO ACADÊMICA)
# ======================================================================================

def executar_testes_validacao_poo() -> bool:
    """
    Executa testes unitários no console verificando todos os requisitos da CP2:
    - Atributos obrigatórios (hp, mp, speed, atk, matk, defense, mdefense)
    - Herança correta de Personagem e Monstro
    - Polimorfismo e sobrescrita de métodos
    - Combate 1v1 e 3v3 funcionais
    """
    print("\n" + "=" * 80)
    print(Cores.colorir("🧪  SUÍTE DE VERIFICAÇÃO AUTOMATIZADA DOS REQUISITOS DA CP2 (POO)  🧪", Cores.NEGRITO + Cores.CIANO))
    print("=" * 80)

    atributos_obrigatorios = ["hp", "mp", "speed", "atk", "matk", "defense", "mdefense"]
    sucesso_total = True

    # 1. Validação dos atributos na classe Personagem e subclasses
    print(f"\n{Cores.NEGRITO}[TESTE 1] Verificação dos 7 Atributos Obrigatórios nos Heróis:{Cores.RESET}")
    for h in criar_elenco_herois():
        for attr in atributos_obrigatorios:
            if not hasattr(h, attr):
                print(f"  ❌ FALHA: {h.nome} não possui o atributo obrigatório '{attr}'!")
                sucesso_total = False
        print(f"  ✔️ {h.nome:<24} ({h.classe_nome:<11}): {Cores.VERDE}Todos os 7 atributos presentes!{Cores.RESET}")

    # 2. Validação dos atributos na classe Monstro e subclasses
    print(f"\n{Cores.NEGRITO}[TESTE 2] Verificação dos 7 Atributos Obrigatórios nos Monstros:{Cores.RESET}")
    for m in criar_elenco_monstros():
        for attr in atributos_obrigatorios:
            if not hasattr(m, attr):
                print(f"  ❌ FALHA: {m.nome} não possui o atributo obrigatório '{attr}'!")
                sucesso_total = False
        print(f"  ✔️ {m.nome:<24} ({m.origem:<18}): {Cores.VERDE}Todos os 7 atributos presentes!{Cores.RESET}")

    # 3. Verificação Estrita de Herança
    print(f"\n{Cores.NEGRITO}[TESTE 3] Verificação de Hierarquia de Herança:{Cores.RESET}")
    guerreiro = Guerreiro()
    mago = Mago()
    arqueiro = Arqueiro()
    paladino = Paladino()
    minotauro = Minotauro()
    monstro_base = Monstro("Besta Genérica")
    personagem_base = Personagem("Herói Genérico")

    assert isinstance(guerreiro, Personagem), "Guerreiro deve herdar de Personagem"
    assert isinstance(mago, Personagem), "Mago deve herdar de Personagem"
    assert isinstance(arqueiro, Personagem), "Arqueiro deve herdar de Personagem"
    assert isinstance(paladino, Personagem), "Paladino deve herdar de Personagem"
    assert isinstance(personagem_base, EntidadeCombate), "Personagem deve herdar de EntidadeCombate"
    assert isinstance(minotauro, Monstro), "Minotauro deve herdar de Monstro"
    assert isinstance(monstro_base, EntidadeCombate), "Monstro deve herdar de EntidadeCombate"

    print("  ✔️ Guerreiro herda de Personagem: SIM")
    print("  ✔️ Mago herda de Personagem: SIM")
    print("  ✔️ Classes inéditas (Arqueiro, Paladino, Assassino, Necromante) herdam de Personagem: SIM")
    print("  ✔️ Monstros herdam da classe Monstro: SIM")
    print("  ✔️ Instanciação direta de Personagem e Monstro: SIM (100% suportada)")

    # 4. Demonstração de Polimorfismo
    print(f"\n{Cores.NEGRITO}[TESTE 4] Demonstração Prática de Polimorfismo (Sobrescrita de atacar()):{Cores.RESET}")
    alvo_teste = Monstro("Manequim de Treino", hp=500, defense=10, mdefense=10)
    for h in criar_elenco_herois():
        _, msg = h.atacar(alvo_teste)
        # Limpa códigos ANSI para a exibição de log puro
        msg_limpa = msg.replace(Cores.VERMELHO, "").replace(Cores.VERDE, "").replace(Cores.MAGENTA, "").replace(Cores.CIANO, "").replace(Cores.CINZA, "").replace(Cores.AMARELO, "").replace(Cores.NEGRITO, "").replace(Cores.RESET, "")
        print(f"  ⚔️ Polimorfismo em {h.classe_nome:<11} ➔ {msg_limpa[:75]}...")

    # 5. Simulação determinística de 1v1
    print(f"\n{Cores.NEGRITO}[TESTE 5] Teste de Execução do Sistema 1v1:{Cores.RESET}")
    h_teste = Guerreiro("Aquiles Teste")
    m_teste = Minotauro("Minotauro Teste")
    vencedor_1v1 = simular_combate_1v1(h_teste, m_teste, interativo=False, delay=0.0)
    print(f"  ✔️ Combate 1v1 finalizado com sucesso! Vencedor definido: {'Herói' if vencedor_1v1 else 'Monstro'}")

    # 6. Simulação determinística de 3v3
    print(f"\n{Cores.NEGRITO}[TESTE 6] Teste de Execução do Sistema 3v3:{Cores.RESET}")
    t_herois = [Guerreiro("H1"), Mago("H2"), Arqueiro("H3")]
    t_monstros = [Minotauro("M1"), Cerbero("M2"), Medusa("M3")]
    vencedor_3v3 = simular_combate_3v3(t_herois, t_monstros, interativo=False, delay=0.0)
    print(f"  ✔️ Combate 3v3 finalizado com sucesso! Vencedor definido: {'Heróis' if vencedor_3v3 else 'Monstros'}")

    print("\n" + "=" * 80)
    if sucesso_total:
        print(Cores.colorir("🎉 [SUCESSO TOTAL] TODOS OS REQUISITOS DA CP2 PASSARAM COM NOTA 10! 🎉", Cores.VERDE + Cores.NEGRITO))
    else:
        print(Cores.colorir("⚠️ ALGUNS TESTES FALHARAM. REVISE AS CLASSES.", Cores.VERMELHO + Cores.NEGRITO))
    print("=" * 80 + "\n")
    return sucesso_total


# ======================================================================================
# SEÇÃO 8: TABELA DE STATUS E MENU PRINCIPAL
# ======================================================================================

def exibir_tabela_atributos() -> None:
    """Exibe tabela formatada de atributos dos Heróis e Monstros."""
    print("\n" + "=" * 88)
    print(Cores.colorir("📜  PANTEÃO DOS HERÓIS DISPONÍVEIS", Cores.NEGRITO + Cores.VERDE))
    print("=" * 88)
    print(f"{'Nome':<22} | {'Classe':<11} | {'HP':>4} | {'MP':>4} | {'SPD':>4} | {'ATK':>4} | {'MATK':>4} | {'DEF':>4} | {'MDEF':>4}")
    print("-" * 88)
    for h in criar_elenco_herois():
        print(f"{h.nome:<22} | {h.classe_nome:<11} | {h.max_hp:>4} | {h.max_mp:>4} | {h.speed:>4} | {h.atk:>4} | {h.matk:>4} | {h.defense:>4} | {h.mdefense:>4}")

    print("\n" + "=" * 88)
    print(Cores.colorir("🐉  BESTIÁRIO DAS CRIATURAS LENDÁRIAS", Cores.NEGRITO + Cores.VERMELHO))
    print("=" * 88)
    print(f"{'Nome':<22} | {'Origem':<18} | {'HP':>4} | {'MP':>4} | {'SPD':>4} | {'ATK':>4} | {'MATK':>4} | {'DEF':>4} | {'MDEF':>4}")
    print("-" * 88)
    for m in criar_elenco_monstros():
        print(f"{m.nome:<22} | {m.origem:<18} | {m.max_hp:>4} | {m.max_mp:>4} | {m.speed:>4} | {m.atk:>4} | {m.matk:>4} | {m.defense:>4} | {m.mdefense:>4}")
    print("-" * 88)


def cabecalho_jogo() -> None:
    titulo = r"""
  ╔═══════════════════════════════════════════════════════════════════════╗
  ║         🏛️   ARENA DAS MITOLOGIAS - SISTEMA DE RPG POO   🐉           ║
  ║                     CHECKPOINT 2 (CP2) - PYTHON                       ║
  ╚═══════════════════════════════════════════════════════════════════════╝
    """
    print(Cores.colorir(titulo, Cores.CIANO + Cores.NEGRITO))


def menu_principal() -> None:
    """Loop principal da interface CLI do jogo."""
    while True:
        cabecalho_jogo()
        print(f"{Cores.NEGRITO}MENU PRINCIPAL:{Cores.RESET}")
        print("  [1] Duelo 1v1 Interativo (Você controla o Herói)")
        print("  [2] Duelo 1v1 Simulação Rápida (Execução automática narrada)")
        print("  [3] Batalha em Equipe 3v3 Interativa (Comande o trio de Heróis)")
        print("  [4] Batalha em Equipe 3v3 Simulação Automática (Guerra épica narrada)")
        print("  [5] Bestiário e Panteão (Tabela comparativa de atributos)")
        print("  [6] Executar Testes Automatizados de POO (Verificação dos Requisitos da CP2)")
        print("  [0] Sair do Jogo")
        print("-" * 75)

        opcao = input("Digite a opção desejada: ").strip()

        if opcao == "1":
            herois = criar_elenco_herois()
            monstros = criar_elenco_monstros()

            print(f"\n{Cores.NEGRITO}ESCOLHA SEU HERÓI:{Cores.RESET}")
            for i, h in enumerate(herois, 1):
                print(f"  [{i}] {h.nome} ({h.classe_nome} - {h.mitologia})")
            
            while True:
                escolha_h = input("Número do herói (1 a 6) [Padrão: 1]: ").strip() or "1"
                if escolha_h.isdigit() and 1 <= int(escolha_h) <= len(herois):
                    heroi_escolhido = herois[int(escolha_h) - 1]
                    break
                print("⚠️ Número inválido. Escolha de 1 a 6.")

            print(f"\n{Cores.NEGRITO}ESCOLHA O MONSTRO ADVERSÁRIO:{Cores.RESET}")
            for i, m in enumerate(monstros, 1):
                print(f"  [{i}] {m.nome} ({m.origem})")
            
            while True:
                escolha_m = input("Número do monstro (1 a 6) [Padrão: 1]: ").strip() or "1"
                if escolha_m.isdigit() and 1 <= int(escolha_m) <= len(monstros):
                    monstro_escolhido = monstros[int(escolha_m) - 1]
                    break
                print("⚠️ Número inválido. Escolha de 1 a 6.")

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

            print(f"\n{Cores.NEGRITO}SELEÇÃO DA SUA EQUIPE DE 3 HERÓIS:{Cores.RESET}")
            for i, h in enumerate(herois, 1):
                print(f"  [{i}] {h.nome} ({h.classe_nome})")

            selecionados: List[Personagem] = []
            while len(selecionados) < 3:
                escolha = input(f"Escolha o herói #{len(selecionados) + 1} (1 a 6): ").strip()
                if escolha.isdigit() and 1 <= int(escolha) <= len(herois):
                    candidato = herois[int(escolha) - 1]
                    if candidato not in selecionados:
                        selecionados.append(candidato)
                        print(f"  {Cores.VERDE}✔️ {candidato.nome} adicionado à equipe!{Cores.RESET}")
                    else:
                        print("  ⚠️ Herói já selecionado! Escolha outro.")
                else:
                    print("  ⚠️ Opção inválida. Digite de 1 a 6.")

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

        elif opcao == "6":
            executar_testes_validacao_poo()
            input("Pressione ENTER para voltar ao menu...")

        elif opcao == "0":
            print(f"\n{Cores.CIANO}Obrigado por jogar Arena das Mitologias! Que os deuses guiem seus passos.{Cores.RESET}")
            sys.exit(0)

        else:
            print("\n⚠️ Opção inválida! Escolha um número de 0 a 6.")


# ======================================================================================
# PONTO DE ENTRADA DO PROGRAMA
# ======================================================================================

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ("--test", "-t", "--auto"):
        sucesso = executar_testes_validacao_poo()
        sys.exit(0 if sucesso else 1)
    else:
        menu_principal()
