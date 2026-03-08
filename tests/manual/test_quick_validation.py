#!/usr/bin/env python3
"""
Script de validação rápida para testar o sistema antes do teste de 1000 empresas.
"""

import sys
sys.path.append('src')

import psycopg2
import re
from src.config import load_config
from src.search import search_prompt

def testar_conexao_banco():
    """Testa conexão com o banco e extrai algumas empresas."""
    print("🔍 Testando conexão com banco...")

    config = load_config()
    db_url = config.get("DATABASE_URL")

    try:
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()

        # Obter 10 primeiras empresas
        cursor.execute("SELECT document FROM langchain_pg_embedding LIMIT 10;")

        empresas = []
        pattern = r'^(.+?)\s+R\$\s*([\d.,]+)\s+(\d{4})$'

        for row in cursor.fetchall():
            documento = row[0].strip()
            if 'Nome da empresa' not in documento:
                match = re.match(pattern, documento)
                if match:
                    nome = match.group(1).strip()
                    faturamento = f"R$ {match.group(2)}"
                    ano = match.group(3)
                    empresas.append((nome, faturamento, ano))

        cursor.close()
        conn.close()

        print(f"✅ Encontradas {len(empresas)} empresas de teste")
        return empresas[:5]  # Retornar apenas 5 para teste

    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return []

def testar_funcionalidade_search():
    """Testa algumas perguntas básicas."""
    print("\n🧪 Testando funcionalidade search_prompt...")

    perguntas_teste = [
        "Qual o faturamento da empresa Pacto IA?",
        "Em que ano foi fundada a Pacto IA?",
        "Qual o CEO da Pacto IA?",  # Deve rejeitar
    ]

    for pergunta in perguntas_teste:
        print(f"\n   Pergunta: {pergunta}")
        try:
            resposta = search_prompt(pergunta)
            status = "✅ OK" if len(resposta) > 10 else "⚠️ Resposta curta"
            print(f"   {status}: {resposta[:80]}...")
        except Exception as e:
            print(f"   ❌ ERRO: {e}")

def testar_empresas_especificas(empresas):
    """Testa empresas específicas do banco."""
    print("\n🎯 Testando empresas específicas do banco...")

    for i, (nome, faturamento_esperado, ano_esperado) in enumerate(empresas, 1):
        print(f"\n{i}. Testando: {nome}")

        # Teste faturamento
        pergunta_fat = f"Qual o faturamento da empresa {nome}?"
        resposta_fat = search_prompt(pergunta_fat)

        # Teste ano
        pergunta_ano = f"Em que ano foi fundada a empresa {nome}?"
        resposta_ano = search_prompt(pergunta_ano)

        print(f"   💰 Esperado: {faturamento_esperado}")
        print(f"   💰 Obtido: {resposta_fat[:50]}...")

        print(f"   📅 Esperado: {ano_esperado}")
        print(f"   📅 Obtido: {resposta_ano[:50]}...")

        # Validação simples
        fat_ok = faturamento_esperado.replace('.', '').replace(',', '') in resposta_fat.replace('.', '').replace(',', '')
        ano_ok = ano_esperado in resposta_ano

        print(f"   Status: {'✅' if fat_ok else '❌'} Faturamento | {'✅' if ano_ok else '❌'} Ano")

def main():
    print("🚀 VALIDAÇÃO RÁPIDA DO SISTEMA")
    print("=" * 50)

    # 1. Testar conexão e extrair empresas
    empresas = testar_conexao_banco()

    if not empresas:
        print("❌ Não foi possível obter empresas do banco!")
        return

    # 2. Testar funcionalidade básica
    testar_funcionalidade_search()

    # 3. Testar empresas específicas
    testar_empresas_especificas(empresas)

    print("\n" + "=" * 50)
    print("✅ Validação concluída!")
    print("\nPara executar o teste completo de 1000 empresas:")
    print("python test_consistency_1000.py 1000")
    print("\nPara teste menor (50 empresas):")
    print("python test_consistency_1000.py 50")

if __name__ == "__main__":
    main()