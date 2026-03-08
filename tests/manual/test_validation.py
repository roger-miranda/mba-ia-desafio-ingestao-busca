#!/usr/bin/env python3
"""
Script de Validação e Teste de Consistência
==========================================

Este script unifica todos os testes de validação em um único comando configurável:

1. Validação rápida (quick) - Testa conexão e algumas empresas
2. Teste de consistência (consistency) - Testa N empresas aleatórias
3. Relatórios detalhados com métricas e logs

Uso:
    python test_validation.py [modo] [quantidade]

Exemplos:
    python test_validation.py quick                    # Validação rápida
    python test_validation.py consistency 50           # 50 empresas aleatórias
    python test_validation.py consistency 1000         # 1000 empresas (padrão)
"""

import sys
import os
import random
import re
import time
import argparse
from datetime import datetime
from typing import List, Optional
import psycopg2
from dataclasses import dataclass

# Adicionar o diretório raiz do projeto ao path
script_dir = os.path.dirname(os.path.abspath(__file__))  # tests/manual/
project_root = os.path.dirname(os.path.dirname(script_dir))  # raiz do projeto
sys.path.insert(0, project_root)

from src.search import search_prompt
from src.config import load_config

@dataclass
class Empresa:
    nome: str
    faturamento: str
    ano: int
    faturamento_numerico: float

@dataclass
class TesteResultado:
    empresa: str
    pergunta: str
    resposta_esperada: str
    resposta_obtida: str
    sucesso: bool
    tempo_resposta: float
    erro: Optional[str] = None

class ValidadorUnificado:
    """Classe principal para todos os tipos de validação."""

    def __init__(self):
        self.config = load_config()
        self.db_url = self.config.get("DATABASE_URL")
        self.empresas = []
        self.resultados = []
        # Definir diretório de logs
        self.logs_dir = os.path.join(os.path.dirname(__file__), 'logs')
        os.makedirs(self.logs_dir, exist_ok=True)

    def conectar_banco(self):
        """Conecta ao banco PostgreSQL."""
        try:
            return psycopg2.connect(self.db_url)
        except Exception as e:
            print(f"❌ Erro ao conectar no banco: {e}")
            return None

    def testar_conexao_banco(self):
        """Testa a conexão com o banco e configuração."""
        print("🔍 Testando conexão com banco...")

        if not self.db_url:
            print("❌ DATABASE_URL não configurada!")
            return False

        conn = self.conectar_banco()
        if not conn:
            return False

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM langchain_pg_embedding;")
            total_chunks = cursor.fetchone()[0]
            print(f"✅ Conexão OK! {total_chunks} chunks encontrados no banco")

            cursor.close()
            conn.close()
            return True
        except Exception as e:
            print(f"❌ Erro ao consultar banco: {e}")
            return False

    def obter_todas_empresas(self) -> List[Empresa]:
        """Obtém todas as empresas do banco, processando chunks."""
        conn = self.conectar_banco()
        if not conn:
            return []

        try:
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
                        faturamento_str = match.group(2)
                        ano = int(match.group(3))

                        # Evitar duplicatas
                        if nome not in empresas:
                            try:
                                faturamento_numerico = float(faturamento_str.replace('.', '').replace(',', '.'))
                                empresas[nome] = Empresa(
                                    nome=nome,
                                    faturamento=f"R$ {faturamento_str}",
                                    ano=ano,
                                    faturamento_numerico=faturamento_numerico
                                )
                            except ValueError:
                                continue

            cursor.close()
            conn.close()

            empresas_lista = list(empresas.values())
            print(f"✅ Encontradas {len(empresas_lista)} empresas únicas")
            return empresas_lista

        except Exception as e:
            print(f"❌ Erro ao extrair empresas: {e}")
            return []

    def testar_funcionalidade_search(self):
        """Testa algumas perguntas básicas para validar a funcionalidade."""
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

    def validacao_rapida(self):
        """Executa validação rápida do sistema."""
        print("🚀 VALIDAÇÃO RÁPIDA DO SISTEMA")
        print("=" * 50)

        # 1. Testar conexão
        if not self.testar_conexao_banco():
            return False

        # 2. Obter algumas empresas para teste
        print("\n📊 Obtendo empresas de teste...")
        todas_empresas = self.obter_todas_empresas()

        if not todas_empresas:
            print("❌ Não foi possível obter empresas do banco!")
            return False

        # 3. Testar funcionalidade básica
        self.testar_funcionalidade_search()

        # 4. Testar 5 empresas específicas
        print("\n🎯 Testando empresas específicas...")
        empresas_teste = random.sample(todas_empresas, min(5, len(todas_empresas)))

        sucessos = 0
        for i, empresa in enumerate(empresas_teste, 1):
            print(f"\n{i}. Testando: {empresa.nome}")

            # Teste faturamento
            pergunta_fat = f"Qual o faturamento da empresa {empresa.nome}?"
            try:
                resposta_fat = search_prompt(pergunta_fat)
                fat_ok = empresa.faturamento.replace('.', '').replace(',', '') in resposta_fat.replace('.', '').replace(',', '')
                print(f"   💰 Esperado: {empresa.faturamento}")
                print(f"   💰 Obtido: {resposta_fat[:50]}...")
                print(f"   Status Faturamento: {'✅' if fat_ok else '❌'}")

                if fat_ok:
                    sucessos += 1
            except Exception as e:
                print(f"   ❌ Erro faturamento: {e}")

        taxa_sucesso = (sucessos / len(empresas_teste)) * 100
        print(f"\n📊 Taxa de sucesso: {sucessos}/{len(empresas_teste)} ({taxa_sucesso:.1f}%)")

        if taxa_sucesso >= 80:
            print("✅ Sistema funcionando corretamente!")
        else:
            print("⚠️ Sistema pode ter problemas. Execute teste completo.")

        return True

    def normalizar_faturamento(self, valor: str) -> str:
        """Normaliza formato do faturamento para comparação."""
        if not valor:
            return ""

        valor_limpo = re.sub(r'[R$\s]', '', valor)

        if ',' in valor_limpo:
            partes = valor_limpo.split(',')
            if len(partes) == 2 and len(partes[1]) <= 2:
                inteiro = partes[0].replace('.', '')
                return f"R$ {inteiro},{partes[1]}"

        valor_limpo = valor_limpo.replace('.', '')
        return f"R$ {valor_limpo}"

    def extrair_valor_resposta(self, resposta: str, tipo: str) -> Optional[str]:
        """Extrai valor específico da resposta do LLM."""
        resposta_lower = resposta.lower()

        if "não tenho informações" in resposta_lower:
            return None

        if tipo == "faturamento":
            match = re.search(r'r\$\s*([\d.,]+)', resposta_lower)
            if match:
                return f"R$ {match.group(1)}"

        elif tipo == "ano":
            match = re.search(r'\b(19\d{2}|20\d{2})\b', resposta)
            if match:
                return match.group(1)

        return None

    def validar_resposta(self, empresa: Empresa, pergunta: str, resposta: str) -> bool:
        """Valida se a resposta está correta."""
        if "faturamento" in pergunta.lower():
            valor_extraido = self.extrair_valor_resposta(resposta, "faturamento")
            if not valor_extraido:
                return False

            esperado = self.normalizar_faturamento(empresa.faturamento)
            obtido = self.normalizar_faturamento(valor_extraido)
            return esperado == obtido

        elif "ano" in pergunta.lower() or "fundada" in pergunta.lower():
            ano_extraido = self.extrair_valor_resposta(resposta, "ano")
            if not ano_extraido:
                return False

            return str(empresa.ano) == ano_extraido

        return False

    def testar_empresa(self, empresa: Empresa) -> List[TesteResultado]:
        """Testa uma empresa específica com múltiplas perguntas."""
        perguntas = [
            f"Qual o faturamento da empresa {empresa.nome}?",
            f"Em que ano foi fundada a empresa {empresa.nome}?",
        ]

        resultados = []

        for pergunta in perguntas:
            tempo_inicio = time.time()

            try:
                resposta = search_prompt(pergunta)
                tempo_resposta = time.time() - tempo_inicio

                if "faturamento" in pergunta.lower():
                    resposta_esperada = empresa.faturamento
                else:
                    resposta_esperada = str(empresa.ano)

                sucesso = self.validar_resposta(empresa, pergunta, resposta)

                resultado = TesteResultado(
                    empresa=empresa.nome,
                    pergunta=pergunta,
                    resposta_esperada=resposta_esperada,
                    resposta_obtida=resposta,
                    sucesso=sucesso,
                    tempo_resposta=tempo_resposta
                )

                resultados.append(resultado)

            except Exception as e:
                tempo_resposta = time.time() - tempo_inicio

                resultado = TesteResultado(
                    empresa=empresa.nome,
                    pergunta=pergunta,
                    resposta_esperada="N/A",
                    resposta_obtida="ERRO",
                    sucesso=False,
                    tempo_resposta=tempo_resposta,
                    erro=str(e)
                )

                resultados.append(resultado)

        return resultados

    def teste_consistencia(self, quantidade: int = 100):
        """Executa teste completo de consistência."""
        print(f"🧪 TESTE DE CONSISTÊNCIA - {quantidade} EMPRESAS")
        print("=" * 60)

        # 1. Extrair empresas do banco
        print("1. Extraindo empresas do banco de dados...")
        self.empresas = self.obter_todas_empresas()

        if not self.empresas:
            print("❌ Nenhuma empresa encontrada!")
            return

        # 2. Selecionar empresas aleatórias
        print("2. Selecionando empresas aleatórias...")
        if len(self.empresas) < quantidade:
            print(f"⚠️ Apenas {len(self.empresas)} empresas disponíveis, testando todas.")
            empresas_teste = self.empresas
            quantidade = len(self.empresas)
        else:
            empresas_teste = random.sample(self.empresas, quantidade)

        print(f"✅ Selecionadas {len(empresas_teste)} empresas para teste")

        # 3. Executar testes
        print("3. Executando testes...")
        print(f"   Testando {len(empresas_teste)} empresas (2 perguntas cada)")
        print(f"   Total de {len(empresas_teste) * 2} perguntas")

        # Preparar log no diretório logs
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        arquivo_log = os.path.join(self.logs_dir, f"teste_consistencia_{timestamp}.txt")

        with open(arquivo_log, 'w', encoding='utf-8') as log:
            log.write(f"TESTE DE CONSISTÊNCIA - {datetime.now()}\n")
            log.write("=" * 60 + "\n\n")
            log.write(f"Quantidade de empresas testadas: {quantidade}\n\n")

            for i, empresa in enumerate(empresas_teste, 1):
                print(f"   [{i}/{quantidade}] {empresa.nome[:40]}...")

                resultados_empresa = self.testar_empresa(empresa)
                self.resultados.extend(resultados_empresa)

                # Log detalhado
                log.write(f"{i}. {empresa.nome}\n")
                for resultado in resultados_empresa:
                    if "faturamento" in resultado.pergunta.lower():
                        log.write(f"   Faturamento - Esperado: {resultado.resposta_esperada}\n")
                        log.write(f"   Faturamento - Obtido: {resultado.resposta_obtida[:100]}...\n")
                        log.write(f"   Faturamento - {'✅' if resultado.sucesso else '❌'}\n")
                    else:
                        log.write(f"   Ano - Esperado: {resultado.resposta_esperada}\n")
                        log.write(f"   Ano - Obtido: {resultado.resposta_obtida[:100]}...\n")
                        log.write(f"   Ano - {'✅' if resultado.sucesso else '❌'}\n")
                log.write("\n")

                # Progresso a cada 25 empresas
                if i % 25 == 0 or i == quantidade:
                    sucessos = sum(1 for r in self.resultados if r.sucesso)
                    taxa_sucesso = (sucessos / len(self.resultados)) * 100
                    print(f"   ✅ Progresso: {i}/{quantidade} empresas - {taxa_sucesso:.1f}% sucesso")

        # 4. Gerar relatório final
        self.gerar_relatorio_final(arquivo_log)

    def gerar_relatorio_final(self, arquivo_log: str):
        """Gera relatório final com métricas detalhadas."""
        if not self.resultados:
            print("❌ Nenhum resultado para relatório!")
            return

        # Métricas gerais
        total = len(self.resultados)
        sucessos = sum(1 for r in self.resultados if r.sucesso)
        erros = sum(1 for r in self.resultados if r.erro)
        taxa_sucesso = (sucessos / total) * 100 if total > 0 else 0

        # Métricas por tipo
        fat_total = sum(1 for r in self.resultados if "faturamento" in r.pergunta.lower())
        fat_sucesso = sum(1 for r in self.resultados if "faturamento" in r.pergunta.lower() and r.sucesso)
        taxa_fat = (fat_sucesso / fat_total) * 100 if fat_total > 0 else 0

        ano_total = sum(1 for r in self.resultados if "ano" in r.pergunta.lower() or "fundada" in r.pergunta.lower())
        ano_sucesso = sum(1 for r in self.resultados if ("ano" in r.pergunta.lower() or "fundada" in r.pergunta.lower()) and r.sucesso)
        taxa_ano = (ano_sucesso / ano_total) * 100 if ano_total > 0 else 0

        # Tempo médio
        tempos = [r.tempo_resposta for r in self.resultados if r.tempo_resposta > 0]
        tempo_medio = sum(tempos) / len(tempos) if tempos else 0

        # Resultados na tela
        print("\n" + "=" * 60)
        print("📊 RESULTADOS FINAIS")
        print("=" * 60)
        print(f"🎯 Taxa Sucesso Geral: {sucessos}/{total} ({taxa_sucesso:.1f}%)")
        print(f"💰 Taxa Sucesso Faturamento: {fat_sucesso}/{fat_total} ({taxa_fat:.1f}%)")
        print(f"📅 Taxa Sucesso Ano: {ano_sucesso}/{ano_total} ({taxa_ano:.1f}%)")
        print(f"⏱️ Tempo Médio: {tempo_medio:.2f}s/pergunta")
        print(f"🚨 Erros Técnicos: {erros}")
        print(f"📄 Log detalhado: {os.path.relpath(arquivo_log)}")

        # Avaliação final
        if taxa_sucesso >= 90:
            print("🎉 EXCELENTE! Sistema muito consistente!")
        elif taxa_sucesso >= 75:
            print("✅ BOM! Sistema razoavelmente consistente.")
        elif taxa_sucesso >= 50:
            print("⚠️ REGULAR. Sistema precisa de melhorias.")
        else:
            print("❌ CRÍTICO! Sistema inconsistente.")

def main():
    """Função principal com argumentos de linha de comando."""
    parser = argparse.ArgumentParser(
        description="Script de Validação e Teste de Consistência",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  %(prog)s quick                    # Validação rápida
  %(prog)s consistency 50           # Teste de consistência com 50 empresas
  %(prog)s consistency 1000         # Teste de consistência com 1000 empresas
  %(prog)s consistency              # Teste de consistência padrão (100 empresas)
        """)

    parser.add_argument('modo', nargs='?', default='consistency',
                       choices=['quick', 'consistency'],
                       help='Modo de operação (padrão: consistency)')

    parser.add_argument('quantidade', nargs='?', type=int, default=100,
                       help='Número de empresas para teste (padrão: 100)')

    args = parser.parse_args()

    # Configurar seed para reproduzibilidade
    random.seed(42)

    validador = ValidadorUnificado()

    if args.modo == 'quick':
        print("Executando validação rápida...")
        validador.validacao_rapida()

    elif args.modo == 'consistency':
        print(f"Executando teste de consistência com {args.quantidade} empresas...")
        validador.teste_consistencia(args.quantidade)

    print("\n🎯 Teste concluído!")

if __name__ == "__main__":
    main()