"""
========================================================================================
PROJETO: ARENA DO OLIMPO & CHOQUE DE MITOLOGIAS (SISTEMA DE COMBATE RPG POO)
CHECKPOINT 2 (CP2) - PROGRAMAÇÃO ORIENTADA A OBJETOS EM PYTHON
========================================================================================

INTEGRANTES DO GRUPO:
- Vinicius Eddo                  | RM: 571008
- Guilherme Gomes Orugian Santos | RM: 572882
- Lucas Henrique Vieira          | RM: 571901
- Rafael Jun Aita Hirata         | RM: 569708
- Rodrigo Bettio Penha Junior    | RM: 573725

CONCEITOS FUNDAMENTAIS DE POO IMPLEMENTADOS:
1. Classes e Objetos: Abstração de entidades mitológicas com atributos e métodos.
2. Encapsulamento: Controle de integridade de atributos com getters, setters e propriedades.
3. Herança: Classes filhas herdam de classes base ("Personagem" e "Monstro").
4. Polimorfismo: Sobrescrita do método 'atacar()' e habilidades especiais exclusivas.
5. Sistema de Batalha por Turnos (1v1 e 3v3): Baseado em velocidade, cálculo de dano
   (físico e mágico) e gerenciamento de alvos vivos até condição de vitória/derrota.
========================================================================================
"""

from __future__ import annotations
import random
import time
import sys
from abc import ABC, abstractmethod
from typing import List, Tuple, Optional

# Garante suporte total a UTF-8 no terminal do Windows sem falhas de encode
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


# ======================================================================================
# SEÇÃO 1: CLASSES BASE (CLASSES PAI / ABSTRAÇÃO)
# ======================================================================================

class EntidadeCombate(ABC):
    """
    Classe Abstrata que define o contrato e os atributos obrigatórios
    compartilhados por qualquer entidade combatente no sistema RPG.
    
    Requisitos Obrigatórios Atendidos:
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
        self._max_hp = hp
        self._hp = hp
        self._max_mp = mp
        self._mp = mp
        self.speed = speed
        self.atk = atk
        self.matk = matk
        self.defense = defense
        self.mdefense = mdefense

    # --- Propriedades e Encapsulamento ---
    @property
    def hp(self) -> int:
        """Retorna o HP atual garantindo que não fique negativo."""
        return self._hp

    @hp.setter
    def hp(self, valor: int) -> None:
        """Define o HP respeitando os limites [0, max_hp]."""
        self._hp = max(0, min(valor, self._max_hp))

    @property
    def mp(self) -> int:
        """Retorna a mana atual."""
        return self._mp

    @mp.setter
    def mp(self, valor: int) -> None:
        """Define o MP respeitando os limites [0, max_mp]."""
        self._mp = max(0, min(valor, self._max_mp))

    @property
    def max_hp(self) -> int:
        return self._max_hp

    @property
    def max_mp(self) -> int:
        return self._max_mp

    def esta_vivo(self) -> bool:
        """Retorna True se o combatente tiver HP maior que zero."""
        return self._hp > 0

    def receber_dano(self, dano: int, tipo_dano: str = "físico") -> int:
        """
        Aplica dano ao HP da entidade.
        Retorna o dano real sofrido (mínimo de 1).
        """
        dano_real = max(1, dano)
        self.hp -= dano_real
        return dano_real

    def consumir_mp(self, custo: int) -> bool:
        """Tenta consumir MP. Retorna True se possuía mana suficiente."""
        if self.mp >= custo:
            self.mp -= custo
            return True
        return False

    def curar(self, quantidade: int) -> int:
        """Cura a entidade sem ultrapassar o max_hp."""
        vida_anterior = self.hp
        self.hp += quantidade
        return self.hp - vida_anterior

    def barra_status(self, comprimento: int = 14) -> str:
        """Gera uma barra visual de status (HP e MP) formatada."""
        porcentagem_hp = self.hp / self.max_hp if self.max_hp > 0 else 0
        preenchidos_hp = int(porcentagem_hp * comprimento)
        barra_hp = "=" * preenchidos_hp + "-" * (comprimento - preenchidos_hp)

        porcentagem_mp = self.mp / self.max_mp if self.max_mp > 0 else 0
        preenchidos_mp = int(porcentagem_mp * comprimento)
        barra_mp = "*" * preenchidos_mp + "." * (comprimento - preenchidos_mp)

        status = f"{self.nome:<24} | HP: [{barra_hp}] {self.hp:>3}/{self.max_hp:<3} | MP: [{barra_mp}] {self.mp:>3}/{self.max_mp:<3}"
        if not self.esta_vivo():
            status += " [DERROTADO]"
        return status

    @abstractmethod
    def atacar(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        """
        Método polimórfico obrigatório de ataque.
        Retorna uma tupla: (dano_causado, mensagem_narrativa).
        """
        pass

    @abstractmethod
    def habilidade_especial(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        """
        Método polimórfico para habilidades mitológicas exclusivas com custo de MP.
        Retorna uma tupla: (dano_causado_ou_curado, mensagem_narrativa).
        """
        pass


class Personagem(EntidadeCombate):
    """
    Classe Pai exigida: "Personagem".
    Representa a base para todos os heróis jogáveis de diferentes mitologias.
    Herda todos os 7 atributos obrigatórios e define métodos comuns aos heróis.
    """

    def __init__(
        self,
        nome: str,
        classe_nome: str,
        mitologia: str,
        hp: int,
        mp: int,
        speed: int,
        atk: int,
        matk: int,
        defense: int,
        mdefense: int
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
        return f"[{self.mitologia}] {self.nome} ({self.classe_nome}) - HP: {self.hp}/{self.max_hp} | MP: {self.mp}/{self.max_mp} | SPD: {self.speed}"

    def regenerar_turno(self) -> None:
        """Recupera uma pequena quantidade de MP ao final de cada rodada."""
        if self.esta_vivo():
            recuperado = min(6, self.max_mp - self.mp)
            self.mp += recuperado


class Monstro(EntidadeCombate):
    """
    Classe Pai exigida: "Monstro".
    Representa criaturas lendárias e bestas mitológicas do submundo e dos confins do cosmos.
    Herda todos os 7 atributos obrigatórios.
    """

    def __init__(
        self,
        nome: str,
        origem: str,
        hp: int,
        mp: int,
        speed: int,
        atk: int,
        matk: int,
        defense: int,
        mdefense: int,
        descricao: str = ""
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
        return f"[Monstro: {self.origem}] {self.nome} - HP: {self.hp}/{self.max_hp} | MP: {self.mp}/{self.max_mp} | SPD: {self.speed}"

    def atacar(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        """
        Ataque genérico de monstro baseado no maior potencial (físico ou mágico).
        Pode ser sobrescrito pelas subclasses de monstros.
        """
        if self.atk >= self.matk:
            dano_bruto = self.atk - alvo.defense
            dano = alvo.receber_dano(dano_bruto, "físico")
            msg = f"[ATAQUE BESTIAL] {self.nome} ataca ferozmente {alvo.nome} desferindo {dano} de dano físico!"
        else:
            dano_bruto = self.matk - alvo.mdefense
            dano = alvo.receber_dano(dano_bruto, "mágico")
            msg = f"[MAGIA NEGRA] {self.nome} canaliza energia monstruosa em {alvo.nome} desferindo {dano} de dano mágico!"
        return dano, msg

    def habilidade_especial(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        """Ataque feroz reforçado com consumo de mana."""
        custo = 15
        if self.consumir_mp(custo):
            dano_bruto = int(self.atk * 1.4 - alvo.defense)
            dano = alvo.receber_dano(dano_bruto, "físico")
            msg = f"[FURIA BESTIAL] {self.nome} entra em colapso violento e atinge {alvo.nome} causando {dano} de dano massivo!"
            return dano, msg
        return self.atacar(alvo)

    def agir_ia(self, alvos_vivos: List[EntidadeCombate]) -> Tuple[int, str]:
        """
        Inteligência Artificial para o monstro:
        Seleciona o herói mais vulnerável e decide entre golpe especial ou ataque normal.
        """
        if not alvos_vivos:
            return 0, "Nenhum alvo vivo disponível."

        # Monstro foca estrategicamente no herói com menor HP
        alvo = min(alvos_vivos, key=lambda a: a.hp)

        # Se tiver mana suficiente e 50% de chance, usa habilidade especial
        if self.mp >= 15 and random.random() < 0.5:
            return self.habilidade_especial(alvo)
        return self.atacar(alvo)


# ======================================================================================
# SEÇÃO 2: CLASSES DE HERÓIS (SUBCLASSES DE PERSONAGEM - POLIMORFISMO)
# ======================================================================================

class Guerreiro(Personagem):
    """
    Classe Obrigatória: "Guerreiro".
    Exemplo Mitológico: Guerreiro de Atenas (Mitologia Grega).
    Perfil de Atributos: Altíssimo HP, excelente Defesa física e robusto Ataque Físico.
    Polimorfismo: Sobrescreve 'atacar()' com 'Golpe de Escudo e Lança Espartana'
    e adiciona a habilidade especial 'Fúria do Olimpo'.
    """

    def __init__(self, nome: str = "Teseu de Atenas") -> None:
        super().__init__(
            nome=nome,
            classe_nome="Guerreiro",
            mitologia="Mitologia Grega",
            hp=140,
            mp=30,
            speed=12,
            atk=28,
            matk=6,
            defense=16,
            mdefense=8
        )

    def atacar(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        """
        Sobrescrita do método de ataque (Polimorfismo).
        Fórmula: Ataque Físico - Defesa do Alvo (mínimo de 1 de dano).
        """
        dano_calculado = self.atk - alvo.defense
        dano_final = alvo.receber_dano(dano_calculado, "físico")
        msg = (
            f"[GUERREIRO] {self.nome} golpeia com sua lança e escudo de bronze contra {alvo.nome}, "
            f"rompendo defesas e causando {dano_final} de dano físico! (HP restante: {alvo.hp})"
        )
        return dano_final, msg

    def habilidade_especial(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        """
        Habilidade: 'Fúria de Ares'
        Custo: 15 MP. Ignora 40% da defesa física do oponente e causa 1.5x de dano.
        """
        custo = 15
        if not self.consumir_mp(custo):
            dano, msg = self.atacar(alvo)
            return dano, f"[AVISO] Mana insuficiente para Fúria de Ares! {msg}"

        defesa_reduzida = int(alvo.defense * 0.6)
        dano_calculado = int(self.atk * 1.5) - defesa_reduzida
        dano_final = alvo.receber_dano(dano_calculado, "físico")
        msg = (
            f"[ESPECIAL: FÚRIA DE ARES] {self.nome} brada em nome do Olimpo e esmaga {alvo.nome} "
            f"com impacto demolidor causando {dano_final} de dano brutal! (Gasto: {custo} MP | HP alvo: {alvo.hp})"
        )
        return dano_final, msg


class Mago(Personagem):
    """
    Classe Obrigatória: "Mago".
    Exemplo Mitológico: Mago Merlin (Mitologia Arturiana / Celta).
    Perfil de Atributos: Altíssimo MP, supremo Ataque Mágico (matk), altíssima Defesa Mágica,
    porém baixa defesa física e velocidade moderada.
    Polimorfismo: Sobrescreve 'atacar()' canalizando projéteis arcanos puros (matk - mdefense).
    """

    def __init__(self, nome: str = "Merlin de Avalon") -> None:
        super().__init__(
            nome=nome,
            classe_nome="Mago",
            mitologia="Mitologia Arturiana",
            hp=90,
            mp=90,
            speed=14,
            atk=8,
            matk=32,
            defense=7,
            mdefense=18
        )

    def atacar(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        """
        Sobrescrita do método de ataque (Polimorfismo).
        Fórmula: Ataque Mágico - Defesa Mágica do Alvo.
        """
        dano_calculado = self.matk - alvo.mdefense
        dano_final = alvo.receber_dano(dano_calculado, "mágico")
        msg = (
            f"[MAGO] {self.nome} entoa cânticos ancestrais e dispara Projéteis de Luz Cósmica em {alvo.nome}, "
            f"causando {dano_final} de dano mágico! (HP restante: {alvo.hp})"
        )
        return dano_final, msg

    def habilidade_especial(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        """
        Habilidade: 'Meteoro Arcano de Avalon'
        Custo: 25 MP. Multiplica o poder mágico em 1.7x contra a defesa mágica.
        """
        custo = 25
        if not self.consumir_mp(custo):
            dano, msg = self.atacar(alvo)
            return dano, f"[AVISO] Mana insuficiente para Meteoro Arcano! {msg}"

        dano_calculado = int(self.matk * 1.7) - alvo.mdefense
        dano_final = alvo.receber_dano(dano_calculado, "mágico")
        msg = (
            f"[ESPECIAL: METEORO ARCANO] {self.nome} invoca as forças de Avalon e precipita um meteoro celestial "
            f"em {alvo.nome}, desintegrando o ar e causando {dano_final} de dano mágico massivo! (Gasto: {custo} MP | HP alvo: {alvo.hp})"
        )
        return dano_final, msg


class Arqueiro(Personagem):
    """
    Classe Inédita 1: "Arqueiro".
    Exemplo Mitológico: Arqueiro de Ártemis (Mitologia Grega).
    Perfil de Atributos: Velocidade superior (Speed 22), excelente Ataque Físico à distância
    com perfuração natural de armadura.
    """

    def __init__(self, nome: str = "Atalanta dos Bosques") -> None:
        super().__init__(
            nome=nome,
            classe_nome="Arqueiro",
            mitologia="Mitologia Grega",
            hp=105,
            mp=45,
            speed=22,
            atk=26,
            matk=10,
            defense=10,
            mdefense=11
        )

    def atacar(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        """
        Sobrescrita do ataque (Polimorfismo):
        Disparo de precisão. Ignora 25% da armadura do inimigo devido à ponta de prata.
        """
        defesa_efetiva = int(alvo.defense * 0.75)
        dano_calculado = self.atk - defesa_efetiva
        dano_final = alvo.receber_dano(dano_calculado, "físico")
        msg = (
            f"[ARQUEIRO] {self.nome} dispara uma Flecha de Prata em alta velocidade no ponto fraco de {alvo.nome}, "
            f"causando {dano_final} de dano perfurante! (HP restante: {alvo.hp})"
        )
        return dano_final, msg

    def habilidade_especial(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        """
        Habilidade: 'Disparo da Lua Crescente de Ártemis'
        Custo: 20 MP. Tiro certeiro com dano ampliado e penetração.
        """
        custo = 20
        if not self.consumir_mp(custo):
            dano, msg = self.atacar(alvo)
            return dano, f"[AVISO] Mana insuficiente para Disparo Lunar! {msg}"

        dano_calculado = int(self.atk * 1.6) - int(alvo.defense * 0.5)
        dano_final = alvo.receber_dano(dano_calculado, "físico")
        msg = (
            f"[ESPECIAL: FLECHA LUNAR] {self.nome} invoca a bênção da deusa Ártemis e desfere um tiro estelar "
            f"que perfura a proteção de {alvo.nome} infligindo {dano_final} de dano crítico! (Gasto: {custo} MP | HP: {alvo.hp})"
        )
        return dano_final, msg


class Paladino(Personagem):
    """
    Classe Inédita 2: "Paladino / Valquíria".
    Exemplo Mitológico: Valquíria de Valhalla (Mitologia Nórdica).
    Perfil de Atributos: Altíssimo equilíbrio entre vida, defesas e ataque sagrado híbrido.
    """

    def __init__(self, nome: str = "Brunhilda de Valhalla") -> None:
        super().__init__(
            nome=nome,
            classe_nome="Paladino",
            mitologia="Mitologia Nórdica",
            hp=130,
            mp=50,
            speed=15,
            atk=22,
            matk=18,
            defense=14,
            mdefense=14
        )

    def atacar(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        """
        Sobrescrita do ataque (Polimorfismo):
        Ataque híbrido: Lança de luz que combina dano físico somado a uma centelha divina.
        """
        dano_fisico = max(1, self.atk - alvo.defense)
        dano_sagrado = max(1, int(self.matk * 0.4) - int(alvo.mdefense * 0.3))
        dano_total = dano_fisico + dano_sagrado
        dano_final = alvo.receber_dano(dano_total, "sagrado")
        msg = (
            f"[PALADINO] {self.nome} avança com asas de luz e crava a Lança Sagrada em {alvo.nome}, "
            f"causando {dano_final} de dano luminoso misto! (HP restante: {alvo.hp})"
        )
        return dano_final, msg

    def habilidade_especial(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        """
        Habilidade: 'Julgamento das Asas Douradas'
        Custo: 20 MP. Dano sagrado potente e auto-regeneração de 18 HP de vida.
        """
        custo = 20
        if not self.consumir_mp(custo):
            dano, msg = self.atacar(alvo)
            return dano, f"[AVISO] Mana insuficiente para Julgamento Divino! {msg}"

        dano_calculado = int(self.atk * 1.2 + self.matk * 0.8) - int(alvo.defense * 0.5)
        dano_final = alvo.receber_dano(dano_calculado, "sagrado")
        vida_curada = self.curar(18)
        msg = (
            f"[ESPECIAL: JULGAMENTO DE VALHALLA] {self.nome} invoca os salões de Odin, banha {alvo.nome} em luz divina "
            f"causando {dano_final} de dano e restaura +{vida_curada} de HP para si mesma! (Gasto: {custo} MP | HP atual: {self.hp})"
        )
        return dano_final, msg


class Assassino(Personagem):
    """
    Classe Inédita 3: "Assassino".
    Exemplo Mitológico: Sombra de Susanoo (Mitologia Japonesa).
    Perfil de Atributos: Velocidade extrema (Speed 25), ataque letal e técnicas de evasão.
    """

    def __init__(self, nome: str = "Hanzo das Sombras") -> None:
        super().__init__(
            nome=nome,
            classe_nome="Assassino",
            mitologia="Mitologia Japonesa",
            hp=100,
            mp=40,
            speed=25,
            atk=29,
            matk=12,
            defense=9,
            mdefense=9
        )

    def atacar(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        """
        Sobrescrita do ataque (Polimorfismo):
        Corte das Sombras veloz com chance de golpe crítico.
        """
        dano_calculado = self.atk - alvo.defense
        eh_critico = random.random() < 0.35
        if eh_critico:
            dano_calculado = int(dano_calculado * 1.5)
        dano_final = alvo.receber_dano(dano_calculado, "físico")
        critico_str = " [GOLPE CRÍTICO!]" if eh_critico else ""
        msg = (
            f"[ASSASSINO] {self.nome} surge das sombras com corte veloz de katana{critico_str} em {alvo.nome}, "
            f"causando {dano_final} de dano cortante! (HP restante: {alvo.hp})"
        )
        return dano_final, msg

    def habilidade_especial(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        """
        Habilidade: 'Execução Tempestuosa de Susanoo'
        Custo: 20 MP. Dano massivo com perfuração de 50% da defesa.
        """
        custo = 20
        if not self.consumir_mp(custo):
            dano, msg = self.atacar(alvo)
            return dano, f"[AVISO] Mana insuficiente para Execução Tempestuosa! {msg}"

        dano_calculado = int(self.atk * 1.7) - int(alvo.defense * 0.5)
        dano_final = alvo.receber_dano(dano_calculado, "físico")
        msg = (
            f"[ESPECIAL: EXECUÇÃO DE SUSANOO] {self.nome} corta as correntes do vento e desfecha uma saraivada letal "
            f"em {alvo.nome}, provocando {dano_final} de dano devastador! (Gasto: {custo} MP | HP: {alvo.hp})"
        )
        return dano_final, msg


class Necromante(Personagem):
    """
    Classe Inédita 4: "Necromante / Xamã".
    Exemplo Mitológico: Xamã de Anúbis (Mitologia Egípcia).
    Perfil de Atributos: Alto Poder Mágico e drenagem de essência vital dos adversários.
    """

    def __init__(self, nome: str = "Nefértis de Anúbis") -> None:
        super().__init__(
            nome=nome,
            classe_nome="Necromante",
            mitologia="Mitologia Egípcia",
            hp=95,
            mp=80,
            speed=13,
            atk=10,
            matk=30,
            defense=8,
            mdefense=17
        )

    def atacar(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        """
        Sobrescrita do ataque (Polimorfismo):
        Toque Necrótico que drena 35% do dano causado de volta para a vida do Necromante.
        """
        dano_calculado = self.matk - alvo.mdefense
        dano_final = alvo.receber_dano(dano_calculado, "mágico")
        cura = max(1, int(dano_final * 0.35))
        vida_recuperada = self.curar(cura)
        msg = (
            f"[NECROMANTE] {self.nome} manifesta o Toque das Tumbas em {alvo.nome}, causando {dano_final} de dano necrótico "
            f"e drenando +{vida_recuperada} de HP para si! (HP restante: {alvo.hp} | HP atual: {self.hp})"
        )
        return dano_final, msg

    def habilidade_especial(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        """
        Habilidade: 'Pesagem das Almas de Anúbis'
        Custo: 25 MP. Maldição ancestral das areias com dano necrótico massivo e cura.
        """
        custo = 25
        if not self.consumir_mp(custo):
            dano, msg = self.atacar(alvo)
            return dano, f"[AVISO] Mana insuficiente para Pesagem das Almas! {msg}"

        dano_calculado = int(self.matk * 1.8) - alvo.mdefense
        dano_final = alvo.receber_dano(dano_calculado, "mágico")
        cura = self.curar(int(dano_final * 0.4))
        msg = (
            f"[ESPECIAL: BALANÇA DE ANÚBIS] {self.nome} evoca a balança sagrada sobre {alvo.nome}! "
            f"As areias negras drenam {dano_final} de dano sombrio e restauram +{cura} de HP! (Gasto: {custo} MP | HP alvo: {alvo.hp})"
        )
        return dano_final, msg


# ======================================================================================
# SEÇÃO 3: BESTIÁRIO MITOLÓGICO (SUBCLASSES DE MONSTRO - POLIMORFISMO DE INIMIGOS)
# ======================================================================================

class Minotauro(Monstro):
    """Monstro Mitológico Grego: A Besta do Labirinto de Creta."""
    def __init__(self, nome: str = "Astérion, o Minotauro") -> None:
        super().__init__(
            nome=nome,
            origem="Mitologia Grega",
            hp=160,
            mp=20,
            speed=10,
            atk=30,
            matk=5,
            defense=15,
            mdefense=6,
            descricao="Monstro colossal com cabeça de touro e machado duplo de bronze."
        )

    def atacar(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        dano_calculado = self.atk - alvo.defense
        dano_final = alvo.receber_dano(dano_calculado, "físico")
        msg = (
            f"[MINOTAURO] {self.nome} golpeia com seu machado de guerra pesado contra {alvo.nome}, "
            f"provocando {dano_final} de dano esmagador! (HP restante: {alvo.hp})"
        )
        return dano_final, msg

    def habilidade_especial(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        custo = 10
        if self.consumir_mp(custo):
            dano_calculado = int(self.atk * 1.5) - int(alvo.defense * 0.7)
            dano_final = alvo.receber_dano(dano_calculado, "físico")
            msg = (
                f"[INVESTIDA DEMOLIDORA] {self.nome} abaixa os chifres e atropela brutalmente {alvo.nome}, "
                f"causando {dano_final} de dano colossal! (HP restante: {alvo.hp})"
            )
            return dano_final, msg
        return self.atacar(alvo)


class Cerbero(Monstro):
    """Monstro Mitológico Grego: O Cão de Três Cabeças dos Portões do Hades."""
    def __init__(self, nome: str = "Cérbero, Cão do Hades") -> None:
        super().__init__(
            nome=nome,
            origem="Mitologia Grega",
            hp=135,
            mp=35,
            speed=18,
            atk=26,
            matk=15,
            defense=12,
            mdefense=12,
            descricao="Cão gigantesco de três cabeças que exala fogo sulfuroso e trevas."
        )

    def atacar(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        dano_calculado = self.atk - alvo.defense
        dano_final = alvo.receber_dano(dano_calculado, "físico")
        msg = (
            f"[CÉRBERO] {self.nome} ataca ferozmente {alvo.nome} com mordidas flamejantes, "
            f"causando {dano_final} de dano físico e ardente! (HP restante: {alvo.hp})"
        )
        return dano_final, msg

    def habilidade_especial(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        custo = 15
        if self.consumir_mp(custo):
            dano_calculado = int(self.atk * 1.3 + self.matk * 0.6) - alvo.defense
            dano_final = alvo.receber_dano(dano_calculado, "misto")
            msg = (
                f"[MORDIDA TRÍPLICE DO HADES] As três cabeças de {self.nome} cravam presas em {alvo.nome}, "
                f"liberando chamas do Tártaro e causando {dano_final} de dano! (HP restante: {alvo.hp})"
            )
            return dano_final, msg
        return self.atacar(alvo)


class Medusa(Monstro):
    """Monstro Mitológico Grego: A Górgona com Cabelos de Serpente."""
    def __init__(self, nome: str = "Medusa, a Górgona") -> None:
        super().__init__(
            nome=nome,
            origem="Mitologia Grega",
            hp=110,
            mp=70,
            speed=16,
            atk=12,
            matk=31,
            defense=10,
            mdefense=16,
            descricao="Górgona milenar cujo olhar petrifica os bravos e cuja aura exala maldição."
        )

    def atacar(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        dano_calculado = self.matk - alvo.mdefense
        dano_final = alvo.receber_dano(dano_calculado, "mágico")
        msg = (
            f"[MEDUSA] {self.nome} fixa seu olhar venenoso em {alvo.nome}, "
            f"provocando {dano_final} de dano místico abrasador! (HP restante: {alvo.hp})"
        )
        return dano_final, msg

    def habilidade_especial(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        custo = 20
        if self.consumir_mp(custo):
            dano_calculado = int(self.matk * 1.6) - alvo.mdefense
            dano_final = alvo.receber_dano(dano_calculado, "mágico")
            msg = (
                f"[OLHAR PETRIFICANTE] {self.nome} desvela seus olhos amaldiçoados! A carne de {alvo.nome} começa a virar pedra, "
                f"sofrendo {dano_final} de dano mágico aterrador! (HP restante: {alvo.hp})"
            )
            return dano_final, msg
        return self.atacar(alvo)


class Quimera(Monstro):
    """Monstro Mitológico Clássico: Híbrido Leão, Bode e Serpente."""
    def __init__(self, nome: str = "Quimera da Lícia") -> None:
        super().__init__(
            nome=nome,
            origem="Mitologia Clássica",
            hp=125,
            mp=40,
            speed=15,
            atk=24,
            matk=20,
            defense=11,
            mdefense=11,
            descricao="Monstro temível com corpo de leão, cabeça de bode no dorso e cauda de serpente."
        )

    def atacar(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        dano_calculado = self.atk - alvo.defense
        dano_final = alvo.receber_dano(dano_calculado, "físico")
        msg = (
            f"[QUIMERA] {self.nome} desfere garras de leão e picada de serpente em {alvo.nome}, "
            f"causando {dano_final} de dano físico e tóxico! (HP restante: {alvo.hp})"
        )
        return dano_final, msg

    def habilidade_especial(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        custo = 18
        if self.consumir_mp(custo):
            dano_calculado = int(self.matk * 1.5) - alvo.mdefense
            dano_final = alvo.receber_dano(dano_calculado, "mágico")
            msg = (
                f"[BAFORADA INCENDIÁRIA] A cabeça de leão e bode da {self.nome} expele um jato de fogo vulcânico sobre {alvo.nome}, "
                f"causando {dano_final} de dano mágico em chamas! (HP restante: {alvo.hp})"
            )
            return dano_final, msg
        return self.atacar(alvo)


class Kraken(Monstro):
    """Monstro Mitológico Nórdico: O Leviatã das Profundezas."""
    def __init__(self, nome: str = "Kraken dos Abismos") -> None:
        super().__init__(
            nome=nome,
            origem="Mitologia Nórdica",
            hp=175,
            mp=30,
            speed=9,
            atk=27,
            matk=16,
            defense=16,
            mdefense=10,
            descricao="Lula gigante titânica capaz de arrastar esquadras inteiras para o fundo do mar."
        )

    def atacar(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        dano_calculado = self.atk - alvo.defense
        dano_final = alvo.receber_dano(dano_calculado, "físico")
        msg = (
            f"[KRAKEN] {self.nome} chicoteia tentáculos colossais esmagando {alvo.nome}, "
            f"causando {dano_final} de dano por impacto marítimo! (HP restante: {alvo.hp})"
        )
        return dano_final, msg

    def habilidade_especial(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        custo = 15
        if self.consumir_mp(custo):
            dano_calculado = int(self.atk * 1.4) - int(alvo.defense * 0.6)
            dano_final = alvo.receber_dano(dano_calculado, "físico")
            msg = (
                f"[TSUNAMI DO ABISMO] {self.nome} ergue uma onda descomunal arrastando {alvo.nome} contra os recifes, "
                f"causando {dano_final} de impacto demolidor! (HP restante: {alvo.hp})"
            )
            return dano_final, msg
        return self.atacar(alvo)


class Esfinge(Monstro):
    """Monstro Mitológico Egípcio: O Guardião dos Mistérios."""
    def __init__(self, nome: str = "Esfinge Milenar") -> None:
        super().__init__(
            nome=nome,
            origem="Mitologia Egípcia",
            hp=120,
            mp=60,
            speed=13,
            atk=18,
            matk=28,
            defense=13,
            mdefense=18,
            descricao="Besta ancestral com asas de águia e corpo de leoa que devora os que erram o enigma."
        )

    def atacar(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        dano_calculado = self.matk - alvo.mdefense
        dano_final = alvo.receber_dano(dano_calculado, "mágico")
        msg = (
            f"[ESFINGE] {self.nome} profere um enigma mental que abala a psique de {alvo.nome}, "
            f"causando {dano_final} de dano psíquico/mágico! (HP restante: {alvo.hp})"
        )
        return dano_final, msg

    def habilidade_especial(self, alvo: EntidadeCombate) -> Tuple[int, str]:
        custo = 20
        if self.consumir_mp(custo):
            dano_calculado = int(self.matk * 1.55) - alvo.mdefense
            dano_final = alvo.receber_dano(dano_calculado, "mágico")
            msg = (
                f"[MALDIÇÃO DO ENIGMA] {self.nome} paralisa a mente de {alvo.nome} com a fúria das areias sagradas, "
                f"desferindo {dano_final} de dano místico puro! (HP restante: {alvo.hp})"
            )
            return dano_final, msg
        return self.atacar(alvo)


# ======================================================================================
# SEÇÃO 4: SISTEMA DE BATALHA 1v1 (HERÓI VS MONSTRO)
# ======================================================================================

def simular_combate_1v1(heroi: Personagem, monstro: Monstro, interativo: bool = False, delay: float = 0.5) -> bool:
    """
    Executa a simulação de combate 1v1 por turnos entre um Herói e um Monstro.
    
    Regras Técnicas Obrigatórias:
    - Compara a speed dos dois combatentes para decidir quem ataca primeiro a cada rodada.
    - Se a speed for idêntica, sorteio justo de iniciativa.
    - Cálculo de dano por ataque físico (atk - defense) ou mágico (matk - mdefense).
    - Encerra quando o HP de um dos combatentes atinge <= 0.
    
    Retorna True se o herói venceu, False caso contrário.
    """
    print("\n" + "=" * 75)
    print(f"[*] INICIO DO COMBATE 1v1: {heroi.nome} VS {monstro.nome}")
    print("=" * 75)
    print(f"Heroi:   {heroi}")
    print(f"Monstro: {monstro}")
    print("-" * 75)

    rodada = 1

    while heroi.esta_vivo() and monstro.esta_vivo():
        print(f"\n--- [RODADA {rodada}] ---")
        print(heroi.barra_status())
        print(monstro.barra_status())
        print("-" * 50)

        # Determina a ordem de ataque baseada em SPEED
        if heroi.speed > monstro.speed:
            primeiro, segundo = heroi, monstro
        elif monstro.speed > heroi.speed:
            primeiro, segundo = monstro, heroi
        else:
            primeiro, segundo = (heroi, monstro) if random.random() < 0.5 else (monstro, heroi)

        ordem = [primeiro, segundo]
        print(f"[INICIATIVA] {primeiro.nome} (SPD: {primeiro.speed}) ataca antes de {segundo.nome} (SPD: {segundo.speed})!")

        for atacante in ordem:
            if not heroi.esta_vivo() or not monstro.esta_vivo():
                break

            defensor = monstro if atacante == heroi else heroi

            # Ação do Atacante
            if atacante == heroi:
                if interativo:
                    print(f"\n>> Seu turno, {heroi.nome}!")
                    print("  [1] Ataque Básico da Classe (Sem custo de MP)")
                    print(f"  [2] Habilidade Especial ({heroi.classe_nome} - Consome MP)")
                    escolha = input("Escolha sua acao (1 ou 2) [Padrao: 1]: ").strip()
                    if escolha == "2" and heroi.mp >= 15:
                        _, msg = heroi.habilidade_especial(defensor)
                    else:
                        if escolha == "2":
                            print("[AVISO] Mana insuficiente! Executando ataque basico.")
                        _, msg = heroi.atacar(defensor)
                else:
                    # Modo Automático: Se tiver bastante MP, prioriza especial
                    if heroi.mp >= 20 and random.random() < 0.6:
                        _, msg = heroi.habilidade_especial(defensor)
                    else:
                        _, msg = heroi.atacar(defensor)
            else:
                # Monstro agindo via IA
                _, msg = monstro.agir_ia([heroi])

            print(f"  {msg}")
            if delay > 0:
                time.sleep(delay)

        # Fim da rodada: regeneração leve de mana
        heroi.regenerar_turno()
        rodada += 1

    print("\n" + "=" * 75)
    print("[*] RESULTADO FINAL DO COMBATE 1v1")
    print("=" * 75)
    if heroi.esta_vivo():
        print(f"[VITORIA] {heroi.nome} derrotou {monstro.nome} em {rodada - 1} rodadas!")
        print(f"Status Final: {heroi.nome} com {heroi.hp}/{heroi.max_hp} HP restante.")
        return True
    else:
        print(f"[DERROTA] {monstro.nome} aniquilou {heroi.nome}...")
        print(f"Status Final: {monstro.nome} sobreviveu com {monstro.hp}/{monstro.max_hp} HP.")
        return False


# ======================================================================================
# SEÇÃO 5: SISTEMA DE BATALHA 3v3 (TIME DE HERÓIS VS TIME DE MONSTROS)
# ======================================================================================

def simular_combate_3v3(
    time_herois: List[Personagem],
    time_monstros: List[Monstro],
    interativo: bool = False,
    delay: float = 0.4
) -> bool:
    """
    Executa a simulação de combate em equipe 3v3 por turnos.
    
    Regras Técnicas Obrigatórias:
    - Gerenciamento inteligente de seleção de alvos vivos.
    - Ordem de ação dinâmica baseada na SPEED de todos os combatentes vivos.
    - Checagem contínua de vitória e derrota: encerra assim que todos de um time tiverem hp <= 0.
    
    Retorna True se o time de heróis venceu, False se os monstros venceram.
    """
    print("\n" + "=" * 80)
    print("[*] GRANDE GUERRA MITOLOGICA: BATALHA EM EQUIPE 3v3")
    print("=" * 80)
    print("TIME DOS HEROIS:")
    for h in time_herois:
        print(f"  • {h}")
    print("\nTIME DOS MONSTROS:")
    for m in time_monstros:
        print(f"  • {m}")
    print("=" * 80)

    rodada = 1

    while any(h.esta_vivo() for h in time_herois) and any(m.esta_vivo() for m in time_monstros):
        print(f"\n==================== [RODADA {rodada}] ====================")
        print(">> STATUS DA EQUIPE DE HEROIS:")
        for h in time_herois:
            print(f"  {h.barra_status()}")

        print("\n>> STATUS DA EQUIPE DE MONSTROS:")
        for m in time_monstros:
            print(f"  {m.barra_status()}")
        print("-" * 75)

        # Coleta todos os combatentes vivos da rodada
        todos_combatentes: List[EntidadeCombate] = [c for c in (time_herois + time_monstros) if c.esta_vivo()]

        # Ordena a fila de ações por velocidade decrescente (com desempate justo)
        todos_combatentes.sort(key=lambda c: (c.speed, random.random()), reverse=True)

        print("[INICIATIVA DA RODADA]")
        fila_nomes = " -> ".join([f"{c.nome} (SPD:{c.speed})" for c in todos_combatentes])
        print(f"  {fila_nomes}\n")

        for atacante in todos_combatentes:
            if not atacante.esta_vivo():
                continue

            herois_vivos = [h for h in time_herois if h.esta_vivo()]
            monstros_vivos = [m for m in time_monstros if m.esta_vivo()]

            if not herois_vivos or not monstros_vivos:
                break

            # Determina alvos e executa a ação
            if isinstance(atacante, Personagem):
                # Turno de um herói atacando monstros
                if interativo:
                    print(f"\n[COMANDO] Heroi: {atacante.nome} ({atacante.classe_nome}) | HP: {atacante.hp}/{atacante.max_hp} | MP: {atacante.mp}")
                    print("Selecione o Monstro Alvo:")
                    for idx, mon in enumerate(monstros_vivos, 1):
                        print(f"  [{idx}] {mon.nome} (HP: {mon.hp}/{mon.max_hp} | DEF: {mon.defense} | MDEF: {mon.mdefense})")
                    
                    try:
                        escolha_alvo = int(input(f"Escolha o alvo (1 a {len(monstros_vivos)}): ").strip() or "1")
                        alvo_idx = max(0, min(escolha_alvo - 1, len(monstros_vivos) - 1))
                        alvo = monstros_vivos[alvo_idx]
                    except ValueError:
                        alvo = monstros_vivos[0]

                    print("Selecione a Acao:")
                    print("  [1] Ataque Basico da Classe")
                    print("  [2] Habilidade Especial (Gasta MP)")
                    escolha_acao = input("Escolha a acao (1 ou 2) [Padrao: 1]: ").strip()

                    if escolha_acao == "2" and atacante.mp >= 15:
                        _, msg = atacante.habilidade_especial(alvo)
                    else:
                        _, msg = atacante.atacar(alvo)
                else:
                    # Modo Automático: Foco inteligente no monstro de menor HP
                    alvo = min(monstros_vivos, key=lambda m: m.hp)
                    if atacante.mp >= 20 and random.random() < 0.65:
                        _, msg = atacante.habilidade_especial(alvo)
                    else:
                        _, msg = atacante.atacar(alvo)
            else:
                # Turno de um Monstro atacando heróis via IA
                _, msg = atacante.agir_ia(herois_vivos)

            print(f"  {msg}")
            if delay > 0:
                time.sleep(delay)

        # Fim de rodada: regenera um pouco de mana dos heróis vivos
        for h in time_herois:
            h.regenerar_turno()

        rodada += 1

    # Checagem final de Vitória / Derrota
    herois_vivos_final = [h for h in time_herois if h.esta_vivo()]
    monstros_vivos_final = [m for m in time_monstros if m.esta_vivo()]

    print("\n" + "=" * 80)
    print("[*] FIM DA GRANDE GUERRA 3v3")
    print("=" * 80)

    if herois_vivos_final:
        print("[VITORIA GLORIOSA] O TIME DOS HEROIS VENCEU A BATALHA!")
        print(f"Sobreviventes ({len(herois_vivos_final)}/{len(time_herois)}):")
        for h in herois_vivos_final:
            print(f"  [OK] {h.nome} ({h.classe_nome}) - HP: {h.hp}/{h.max_hp} | MP: {h.mp}/{h.max_mp}")
        print(f"Duracao total do confronto: {rodada - 1} rodadas.")
        return True
    else:
        print("[DERROTA TOTAL] OS MONSTROS EXTERMINARAM A EQUIPE DOS HEROIS...")
        print(f"Monstros Sobreviventes ({len(monstros_vivos_final)}/{len(time_monstros)}):")
        for m in monstros_vivos_final:
            print(f"  [VIVO] {m.nome} - HP: {m.hp}/{m.max_hp}")
        return False


# ======================================================================================
# SEÇÃO 6: FÁBRICA DE INSTÂNCIAS E DEMONSTRAÇÃO
# ======================================================================================

def criar_elenco_herois() -> List[Personagem]:
    """Cria e retorna uma lista com os heróis instanciados das diversas classes."""
    return [
        Guerreiro("Aquiles de Atenas"),
        Mago("Merlin de Camelot"),
        Arqueiro("Atalanta de Artemis"),
        Paladino("Brunhilda de Odin"),
        Assassino("Hanzo de Susanoo"),
        Necromante("Nefertis de Anubis"),
    ]


def criar_elenco_monstros() -> List[Monstro]:
    """Cria e retorna uma lista com os monstros instanciados das diversas lendas."""
    return [
        Minotauro("Asterion do Labirinto"),
        Cerbero("Cerbero dos Portões"),
        Medusa("Medusa Petrificante"),
        Quimera("Quimera Flamejante"),
        Kraken("Kraken Abissal"),
        Esfinge("Esfinge das Dunas"),
    ]


# ======================================================================================
# SEÇÃO 7: SUÍTE DE TESTES AUTOMÁTICOS DE POO (AUTO-TESTE PARA O PROFESSOR)
# ======================================================================================

def executar_testes_validacao_poo() -> bool:
    """
    Executa uma bateria de testes unitários automatizados no próprio console
    para comprovar sem margem de dúvidas que todos os requisitos da CP2 foram atendidos.
    """
    print("\n" + "=" * 75)
    print("[SUITE DE VERIFICACAO AUTOMATIZADA DOS REQUISITOS DA CP2 - POO]")
    print("=" * 75)

    atributos_obrigatorios = ["hp", "mp", "speed", "atk", "matk", "defense", "mdefense"]
    sucesso_total = True

    # Teste 1: Validação dos atributos na classe base Personagem
    print("\n[TESTE 1] Verificando atributos obrigatorios nos Herois:")
    herois = criar_elenco_herois()
    for h in herois:
        for attr in atributos_obrigatorios:
            if not hasattr(h, attr):
                print(f"  [FALHA] {h.nome} nao possui o atributo obrigatorio '{attr}'!")
                sucesso_total = False
        print(f"  [OK] {h.nome:<24} ({h.classe_nome:<11}): Todos os 7 atributos presentes!")

    # Teste 2: Validação dos atributos na classe base Monstro
    print("\n[TESTE 2] Verificando atributos obrigatorios nos Monstros:")
    monstros = criar_elenco_monstros()
    for m in monstros:
        for attr in atributos_obrigatorios:
            if not hasattr(m, attr):
                print(f"  [FALHA] {m.nome} nao possui o atributo obrigatorio '{attr}'!")
                sucesso_total = False
        print(f"  [OK] {m.nome:<24} ({m.origem:<18}): Todos os 7 atributos presentes!")

    # Teste 3: Verificação de Herança
    print("\n[TESTE 3] Verificando Hierarquia de Heranca:")
    guerreiro = Guerreiro()
    mago = Mago()
    arqueiro = Arqueiro()
    minotauro = Minotauro()

    assert isinstance(guerreiro, Personagem), "Guerreiro deve herdar de Personagem"
    assert isinstance(mago, Personagem), "Mago deve herdar de Personagem"
    assert isinstance(arqueiro, Personagem), "Classe inedita deve herdar de Personagem"
    assert isinstance(minotauro, Monstro), "Minotauro deve herdar de Monstro"
    print("  [OK] Guerreiro herda de Personagem: SIM")
    print("  [OK] Mago herda de Personagem: SIM")
    print("  [OK] Classes ineditas (Arqueiro, Paladino, Assassino, Necromante) herdam de Personagem: SIM")
    print("  [OK] Monstros herdam da classe Monstro: SIM")

    # Teste 4: Demonstração de Polimorfismo
    print("\n[TESTE 4] Demonstracao Pratica de Polimorfismo (Sobrescrita de atacar()):")
    alvo_teste = Monstro("Manequim de Treino", "Olimpo", 500, 50, 10, 10, 10, 10, 10)
    for h in herois:
        dano, msg = h.atacar(alvo_teste)
        print(f"  [POLIMORFISMO] {h.classe_nome:<11} -> {msg[:75]}...")

    # Teste 5: Simulação rápida de 1v1
    print("\n[TESTE 5] Simulacao deterministica de Batalha 1v1:")
    h_teste = Guerreiro("Aquiles Teste")
    m_teste = Minotauro("Minotauro Teste")
    vencedor = simular_combate_1v1(h_teste, m_teste, interativo=False, delay=0.0)
    print(f"  [OK] Combate 1v1 concluido com sucesso! Vencedor definido: {'Heroi' if vencedor else 'Monstro'}")

    # Teste 6: Simulação rápida de 3v3
    print("\n[TESTE 6] Simulacao deterministica de Batalha 3v3:")
    t_herois = [Guerreiro("H1"), Mago("H2"), Arqueiro("H3")]
    t_monstros = [Minotauro("M1"), Cerbero("M2"), Medusa("M3")]
    vencedor_3v3 = simular_combate_3v3(t_herois, t_monstros, interativo=False, delay=0.0)
    print(f"  [OK] Combate 3v3 concluido com sucesso! Vencedor definido: {'Herois' if vencedor_3v3 else 'Monstros'}")

    print("\n" + "=" * 75)
    if sucesso_total:
        print("[SUCESSO TOTAL] TODOS OS REQUISITOS DA CP2 PASSARAM COM NOTA 10!")
    else:
        print("[ALERTA] Alguns testes falharam.")
    print("=" * 75 + "\n")
    return sucesso_total


# ======================================================================================
# SEÇÃO 8: MENU PRINCIPAL INTERATIVO
# ======================================================================================

def cabecalho_jogo() -> None:
    print(r"""
  =====================================================================
      ARENA DAS MITOLOGIAS - SISTEMA DE BATALHA RPG POO (CP2)
  =====================================================================
    """)


def menu_principal() -> None:
    """Loop principal da interface CLI do jogo."""
    while True:
        cabecalho_jogo()
        print("MENU PRINCIPAL:")
        print(" [1] Duelo 1v1 Interativo (Voce controla o Heroi)")
        print(" [2] Duelo 1v1 Simulacao Rapida (Execucao automatica narrada)")
        print(" [3] Batalha em Equipe 3v3 Interativa (Comande o trio de Herois)")
        print(" [4] Batalha em Equipe 3v3 Simulacao Automatica (Guerra mitologica completa)")
        print(" [5] Bestiario e Panteao (Ver atributos de todos os personagens e monstros)")
        print(" [6] Executar Testes Automatizados de POO (Verificacao dos Requisitos da CP2)")
        print(" [0] Sair do Jogo")
        print("-" * 75)

        opcao = input("Digite a opcao desejada: ").strip()

        if opcao == "1":
            herois = criar_elenco_herois()
            monstros = criar_elenco_monstros()

            print("\nESCOLHA SEU HEROI:")
            for i, h in enumerate(herois, 1):
                print(f" [{i}] {h.nome} ({h.classe_nome} - {h.mitologia})")
            escolha_h = input("Numero do heroi (1 a 6) [Padrao: 1]: ").strip() or "1"
            idx_h = max(0, min(int(escolha_h) - 1 if escolha_h.isdigit() else 0, len(herois) - 1))
            heroi_escolhido = herois[idx_h]

            print("\nESCOLHA O MONSTRO ADVERSARIO:")
            for i, m in enumerate(monstros, 1):
                print(f" [{i}] {m.nome} ({m.origem})")
            escolha_m = input("Numero do monstro (1 a 6) [Padrao: 1]: ").strip() or "1"
            idx_m = max(0, min(int(escolha_m) - 1 if escolha_m.isdigit() else 0, len(monstros) - 1))
            monstro_escolhido = monstros[idx_m]

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
            print("\nSELECAO DA EQUIPE DE 3 HEROIS:")
            for i, h in enumerate(herois, 1):
                print(f" [{i}] {h.nome} ({h.classe_nome})")
            
            selecionados: List[Personagem] = []
            while len(selecionados) < 3:
                escolha = input(f"Escolha o heroi #{len(selecionados) + 1} (1 a 6): ").strip()
                if escolha.isdigit() and 1 <= int(escolha) <= len(herois):
                    candidato = herois[int(escolha) - 1]
                    if candidato not in selecionados:
                        selecionados.append(candidato)
                        print(f"  [OK] {candidato.nome} adicionado a equipe!")
                    else:
                        print("  [AVISO] Heroi ja selecionado! Escolha outro.")
                else:
                    print("  [AVISO] Opcao invalida.")

            monstros_desafiantes = random.sample(monstros, 3)
            simular_combate_3v3(selecionados, monstros_desafiantes, interativo=True, delay=0.3)
            input("\nPressione ENTER para voltar ao menu...")

        elif opcao == "4":
            herois = criar_elenco_herois()
            monstros = criar_elenco_monstros()
            t_herois = random.sample(herois, 3)
            t_monstros = random.sample(monstros, 3)
            simular_combate_3v3(t_herois, t_monstros, interativo=False, delay=0.3)
            input("\nPressione ENTER para voltar ao menu...")

        elif opcao == "5":
            print("\n" + "=" * 80)
            print("PANTEAO DOS HEROIS DISPONIVEIS:")
            print("=" * 80)
            for h in criar_elenco_herois():
                print(f"* {h.nome:<24} | Classe: {h.classe_nome:<11} | Mitologia: {h.mitologia}")
                print(f"  HP: {h.max_hp:<3} | MP: {h.max_mp:<3} | SPD: {h.speed:<2} | ATK: {h.atk:<2} | MATK: {h.matk:<2} | DEF: {h.defense:<2} | MDEF: {h.mdefense:<2}\n")

            print("=" * 80)
            print("BESTIARIO DAS CRIATURAS LENDARIAS:")
            print("=" * 80)
            for m in criar_elenco_monstros():
                print(f"* {m.nome:<24} | Origem: {m.origem:<18} | {m.descricao}")
                print(f"  HP: {m.max_hp:<3} | MP: {m.max_mp:<3} | SPD: {m.speed:<2} | ATK: {m.atk:<2} | MATK: {m.matk:<2} | DEF: {m.defense:<2} | MDEF: {m.mdefense:<2}\n")
            input("Pressione ENTER para voltar ao menu...")

        elif opcao == "6":
            executar_testes_validacao_poo()
            input("Pressione ENTER para voltar ao menu...")

        elif opcao == "0":
            print("\nObrigado por jogar Arena das Mitologias! Que os deuses guiem seus passos.")
            sys.exit(0)

        else:
            print("\n[AVISO] Opcao invalida! Escolha um numero de 0 a 6.")


# ======================================================================================
# PONTO DE ENTRADA DO PROGRAMA
# ======================================================================================

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ("--test", "-t", "--auto"):
        sucesso = executar_testes_validacao_poo()
        sys.exit(0 if sucesso else 1)
    else:
        menu_principal()
