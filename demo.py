import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import main

print("\n" + "=" * 80)
print("1. APRESENTAÇÃO DO CABEÇALHO E MENU PRINCIPAL")
print("=" * 80)
main.cabecalho_jogo()

print("\n" + "=" * 80)
print("2. TABELA DE ATRIBUTOS (PANTEÃO E BESTIÁRIO)")
print("=" * 80)
main.exibir_tabela_atributos()

print("\n" + "=" * 80)
print("3. DEMONSTRAÇÃO DE DUELO 1v1 (AQUILES VS MINOTAURO)")
print("=" * 80)
herois = main.criar_elenco_herois()
monstros = main.criar_elenco_monstros()
# Aquiles (Guerreiro) vs Astérion (Minotauro)
main.simular_combate_1v1(herois[0], monstros[0], interativo=False, delay=0.05)

print("\n" + "=" * 80)
print("4. DEMONSTRAÇÃO DE BATALHA EM EQUIPE 3v3")
print("=" * 80)
# Trio: Guerreiro, Mago, Arqueiro vs Minotauro, Cérbero, Medusa
time_h = [herois[0], herois[1], herois[2]]
time_m = [monstros[0], monstros[1], monstros[2]]
main.simular_combate_3v3(time_h, time_m, interativo=False, delay=0.05)
