#!/usr/bin/env python3
"""
Script CORRIGIDO de teste de consistência para 1000 empresas aleatórias.
Versão otimizada para o formato real dos dados (chunks com múltiplas empresas).
"""

import sys
import random
import re
import time
import psycopg2
from datetime import datetime

sys.path.append('src')
from src.search import search_prompt
from src.config import load_config

def obter_todas_empresas():
    """Obtém todas as empresas do banco, processando chunks."""
    config = load_config()
    conn = psycopg2.connect(config['DATABASE_URL'])
    cursor = conn.cursor()
    cursor.execute("SELECT document FROM langchain_pg_embedding;")

    empresas = {}
    pattern = r'^(.+?)\s+R\$\s*([\d.,]+)\s+(\d{4})$'

    for row in cursor.fetchall():
        chunk = row[0]
        linhas = chunk.split('\n')

        for linha in linhas:
            linha = linha.strip()
            if not linha or 'Nome da empresa' in linha or 'Faturamento' in linha:
                continue

            match = re.match(pattern, linha)
            if match:
                nome = match.group(1).strip()
                faturamento = match.group(2)
                ano = int(match.group(3))

                # Evitar duplicatas
                if nome not in empresas:
                    empresas[nome] = {
                        'faturamento': f"R$ {faturamento}",
                        'ano': ano
                    }

    cursor.close()
    conn.close()

    print(f"✅ Encontradas {len(empresas)} empresas únicas")
    return empresas

def testar_empresas(empresas_dict, quantidade=100):
    """Testa empresas selecionadas aleatoriamente."""
    empresas_nomes = list(empresas_dict.keys())
    if len(empresas_nomes) < quantidade:
        quantidade = len(empresas_nomes)

    empresas_teste = random.sample(empresas_nomes, quantidade)

    sucessos_fat = 0
    sucessos_ano = 0
    total_testes = quantidade * 2

    print(f"🧪 Testando {quantidade} empresas ({total_testes} perguntas)...")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    arquivo_log = f"teste_log_{timestamp}.txt"

    with open(arquivo_log, 'w', encoding='utf-8') as log:
        log.write(f"TESTE DE CONSISTÊNCIA - {datetime.now()}\n")
        log.write("=" * 60 + "\n\n")

        for i, nome in enumerate(empresas_teste, 1):
            empresa_data = empresas_dict[nome]

            print(f"[{i}/{quantidade}] {nome[:40]}...")

            # Teste 1: Faturamento
            pergunta_fat = f"Qual o faturamento da empresa {nome}?"
            resposta_fat = search_prompt(pergunta_fat)

            fat_esperado = empresa_data['faturamento']
            fat_ok = fat_esperado.replace('.', '').replace(',', '') in resposta_fat.replace('.', '').replace(',', '')
            if fat_ok:
                sucessos_fat += 1

            # Teste 2: Ano
            pergunta_ano = f"Em que ano foi fundada a empresa {nome}?"
            resposta_ano = search_prompt(pergunta_ano)

            ano_esperado = str(empresa_data['ano'])
            ano_ok = ano_esperado in resposta_ano
            if ano_ok:
                sucessos_ano += 1

            # Log detalhado
            log.write(f"{i}. {nome}\n")
            log.write(f"   Faturamento - Esperado: {fat_esperado}\n")
            log.write(f"   Faturamento - Obtido: {resposta_fat[:100]}...\n")
            log.write(f"   Faturamento - {'✅' if fat_ok else '❌'}\n")
            log.write(f"   Ano - Esperado: {ano_esperado}\n")
            log.write(f"   Ano - Obtido: {resposta_ano[:100]}...\n")
            log.write(f"   Ano - {'✅' if ano_ok else '❌'}\n\n")

            # Progresso a cada 25 empresas
            if i % 25 == 0:
                taxa_fat = (sucessos_fat / i) * 100
                taxa_ano = (sucessos_ano / i) * 100
                print(f"   Progresso: Faturamento {taxa_fat:.1f}% | Ano {taxa_ano:.1f}%")

    # Resultados finais
    taxa_fat_final = (sucessos_fat / quantidade) * 100
    taxa_ano_final = (sucessos_ano / quantidade) * 100
    taxa_geral = ((sucessos_fat + sucessos_ano) / total_testes) * 100

    print("\n" + "=" * 60)
    print("📊 RESULTADOS FINAIS")
    print("=" * 60)
    print(f"💰 Taxa Sucesso Faturamento: {sucessos_fat}/{quantidade} ({taxa_fat_final:.1f}%)")
    print(f"📅 Taxa Sucesso Ano: {sucessos_ano}/{quantidade} ({taxa_ano_final:.1f}%)")
    print(f"🎯 Taxa Sucesso Geral: {sucessos_fat + sucessos_ano}/{total_testes} ({taxa_geral:.1f}%)")
    print(f"📄 Log detalhado: {arquivo_log}")

    if taxa_geral >= 90:
        print("🎉 EXCELENTE! Sistema muito consistente!")
    elif taxa_geral >= 75:
        print("✅ BOM! Sistema razoavelmente consistente.")
    else:
        print("⚠️ Precisa melhorias. Verifique o log para detalhes.")

def main():
    quantidade = int(sys.argv[1]) if len(sys.argv) > 1 else 100

    print(f"🚀 TESTE DE CONSISTÊNCIA - {quantidade} EMPRESAS")
    print("=" * 60)

    random.seed(42)  # Para reproduzibilidade

    print("1. Obtendo empresas do banco...")
    empresas = obter_todas_empresas()

    if not empresas:
        print("❌ Nenhuma empresa encontrada!")
        return

    print("2. Executando testes...")
    testar_empresas(empresas, quantidade)

if __name__ == "__main__":
    main()