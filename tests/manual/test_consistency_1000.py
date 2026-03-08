#!/usr/bin/env python3
"""
Script de teste de consistência para 1000 empresas aleatórias.

Este script:
1. Obtém todas as empresas do banco de dados
2. Seleciona 1000 empresas aleatoriamente
3. Testa perguntas sobre faturamento e ano de fundação
4. Valida consistência das respostas
5. Gera relatório detalhado com métricas
"""

import sys
import os
import random
import re
import time
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import psycopg2
from dataclasses import dataclass

# Adicionar src ao path
sys.path.append('src')

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

class TestadorConsistencia:
    def __init__(self):
        self.config = load_config()
        self.db_url = self.config.get("DATABASE_URL")
        self.empresas = []
        self.resultados = []

    def conectar_banco(self):
        """Conecta ao banco PostgreSQL."""
        try:
            return psycopg2.connect(self.db_url)
        except Exception as e:
            print(f"❌ Erro ao conectar no banco: {e}")
            return None

    def extrair_empresas(self) -> List[Empresa]:
        """Extrai todas as empresas do banco de dados."""
        conn = self.conectar_banco()
        if not conn:
            return []

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT document FROM langchain_pg_embedding;")

            empresas = []
            pattern = r'^(.+?)\s+R\$\s*([\d.,]+)\s+(\d{4})$'

            for row in cursor.fetchall():
                documento = row[0].strip()

                # Pular cabeçalhos
                if 'Nome da empresa' in documento or 'Faturamento' in documento:
                    continue

                match = re.match(pattern, documento)
                if match:
                    nome = match.group(1).strip()
                    faturamento_str = match.group(2)
                    ano = int(match.group(3))

                    # Converter faturamento para float
                    faturamento_numerico = float(faturamento_str.replace('.', '').replace(',', '.'))

                    empresas.append(Empresa(
                        nome=nome,
                        faturamento=f"R$ {faturamento_str}",
                        ano=ano,
                        faturamento_numerico=faturamento_numerico
                    ))

            cursor.close()
            conn.close()

            # Remover duplicatas por nome
            empresas_unicas = {}
            for empresa in empresas:
                if empresa.nome not in empresas_unicas:
                    empresas_unicas[empresa.nome] = empresa

            print(f"✅ Extraídas {len(empresas_unicas)} empresas únicas do banco")
            return list(empresas_unicas.values())

        except Exception as e:
            print(f"❌ Erro ao extrair empresas: {e}")
            return []

    def selecionar_empresas_aleatorias(self, quantidade: int = 1000) -> List[Empresa]:
        """Seleciona empresas aleatórias para teste."""
        if len(self.empresas) < quantidade:
            print(f"⚠️ Apenas {len(self.empresas)} empresas disponíveis, testando todas.")
            return self.empresas

        empresas_selecionadas = random.sample(self.empresas, quantidade)
        print(f"✅ Selecionadas {len(empresas_selecionadas)} empresas para teste")
        return empresas_selecionadas

    def extrair_valor_resposta(self, resposta: str, tipo: str) -> Optional[str]:
        """Extrai valor específico da resposta do LLM."""
        resposta_lower = resposta.lower()

        if "não tenho informações" in resposta_lower:
            return None

        if tipo == "faturamento":
            # Procurar por padrão R$ valor
            match = re.search(r'r\$\s*([\d.,]+)', resposta_lower)
            if match:
                return f"R$ {match.group(1)}"

        elif tipo == "ano":
            # Procurar por ano (4 dígitos)
            match = re.search(r'\b(19\d{2}|20\d{2})\b', resposta)
            if match:
                return match.group(1)

        return None

    def normalizar_faturamento(self, valor: str) -> str:
        """Normaliza formato do faturamento para comparação."""
        if not valor:
            return ""

        # Remove R$ e espaços, mantém apenas números, pontos e vírgulas
        valor_limpo = re.sub(r'[R$\s]', '', valor)

        # Padronizar formato: usar ponto para milhares e vírgula para decimais
        # Se tem vírgula no final, é decimal
        if ',' in valor_limpo:
            partes = valor_limpo.split(',')
            if len(partes) == 2 and len(partes[1]) <= 2:
                # É decimal, converter . para separador de milhares
                inteiro = partes[0].replace('.', '')
                return f"R$ {inteiro},{partes[1]}"

        # Sem vírgula decimal, apenas separadores de milhares
        valor_limpo = valor_limpo.replace('.', '')
        return f"R$ {valor_limpo}"

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

                # Determinar resposta esperada
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

    def executar_teste_completo(self, quantidade: int = 1000):
        """Executa teste completo de consistência."""
        print("🧪 INICIANDO TESTE DE CONSISTÊNCIA")
        print("=" * 60)

        # 1. Extrair empresas do banco
        print("1. Extraindo empresas do banco de dados...")
        self.empresas = self.extrair_empresas()

        if not self.empresas:
            print("❌ Nenhuma empresa encontrada!")
            return

        # 2. Selecionar empresas aleatórias
        print("2. Selecionando empresas aleatórias...")
        empresas_teste = self.selecionar_empresas_aleatorias(quantidade)

        # 3. Executar testes
        print("3. Executando testes...")
        print(f"   Testando {len(empresas_teste)} empresas (2 perguntas cada)")
        print(f"   Total de {len(empresas_teste) * 2} perguntas")

        total_testes = len(empresas_teste) * 2
        contador = 0

        for i, empresa in enumerate(empresas_teste, 1):
            print(f"   [{i}/{len(empresas_teste)}] Testando: {empresa.nome[:30]}...")

            resultados_empresa = self.testar_empresa(empresa)
            self.resultados.extend(resultados_empresa)

            contador += len(resultados_empresa)

            # Progresso a cada 50 empresas
            if i % 50 == 0:
                sucessos = sum(1 for r in self.resultados if r.sucesso)
                taxa_sucesso = (sucessos / len(self.resultados)) * 100
                print(f"   ✅ Progresso: {i}/{len(empresas_teste)} empresas - {taxa_sucesso:.1f}% sucesso")

        # 4. Gerar relatório
        print("4. Gerando relatório...")
        self.gerar_relatorio()

    def gerar_relatorio(self):
        """Gera relatório detalhado dos resultados."""
        if not self.resultados:
            print("❌ Nenhum resultado para relatório!")
            return

        # Métricas gerais
        total = len(self.resultados)
        sucessos = sum(1 for r in self.resultados if r.sucesso)
        erros = sum(1 for r in self.resultados if r.erro)
        taxa_sucesso = (sucessos / total) * 100 if total > 0 else 0

        # Métricas por tipo de pergunta
        faturamento_total = sum(1 for r in self.resultados if "faturamento" in r.pergunta.lower())
        faturamento_sucesso = sum(1 for r in self.resultados if "faturamento" in r.pergunta.lower() and r.sucesso)
        taxa_faturamento = (faturamento_sucesso / faturamento_total) * 100 if faturamento_total > 0 else 0

        ano_total = sum(1 for r in self.resultados if "ano" in r.pergunta.lower() or "fundada" in r.pergunta.lower())
        ano_sucesso = sum(1 for r in self.resultados if ("ano" in r.pergunta.lower() or "fundada" in r.pergunta.lower()) and r.sucesso)
        taxa_ano = (ano_sucesso / ano_total) * 100 if ano_total > 0 else 0

        # Tempo médio de resposta
        tempos = [r.tempo_resposta for r in self.resultados if r.tempo_resposta > 0]
        tempo_medio = sum(tempos) / len(tempos) if tempos else 0

        # Gerar arquivo de relatório
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        arquivo_relatorio = f"relatorio_consistencia_{timestamp}.txt"

        relatorio = f"""
🧪 RELATÓRIO DE TESTE DE CONSISTÊNCIA
{'='*60}
Data/Hora: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Total de empresas testadas: {total // 2}
Total de perguntas: {total}

📊 MÉTRICAS GERAIS
{'='*30}
✅ Sucessos: {sucessos}/{total} ({taxa_sucesso:.1f}%)
❌ Falhas: {total - sucessos}/{total} ({100 - taxa_sucesso:.1f}%)
🚨 Erros técnicos: {erros}
⏱️ Tempo médio por pergunta: {tempo_medio:.2f}s

📋 MÉTRICAS POR TIPO DE PERGUNTA
{'='*40}
💰 Faturamento: {faturamento_sucesso}/{faturamento_total} ({taxa_faturamento:.1f}%)
📅 Ano de Fundação: {ano_sucesso}/{ano_total} ({taxa_ano:.1f}%)

🔍 EXEMPLOS DE FALHAS
{'='*25}
"""

        # Adicionar exemplos de falhas
        falhas = [r for r in self.resultados if not r.sucesso][:10]

        for i, falha in enumerate(falhas, 1):
            relatorio += f"""
{i}. Empresa: {falha.empresa}
   Pergunta: {falha.pergunta}
   Esperado: {falha.resposta_esperada}
   Obtido: {falha.resposta_obtida[:100]}...
   {'Erro: ' + falha.erro if falha.erro else ''}
"""

        # Adicionar exemplos de sucessos
        relatorio += f"\n\n✅ EXEMPLOS DE SUCESSOS\n{'='*25}\n"
        sucessos_exemplos = [r for r in self.resultados if r.sucesso][:5]

        for i, sucesso in enumerate(sucessos_exemplos, 1):
            relatorio += f"""
{i}. Empresa: {sucesso.empresa}
   Pergunta: {sucesso.pergunta}
   Resposta: {sucesso.resposta_obtida[:100]}...
"""

        # Salvar relatório
        with open(arquivo_relatorio, 'w', encoding='utf-8') as f:
            f.write(relatorio)

        # Imprimir resumo na tela
        print("\n" + "="*60)
        print("📊 RESUMO DOS RESULTADOS")
        print("="*60)
        print(f"✅ Taxa de Sucesso Geral: {taxa_sucesso:.1f}%")
        print(f"💰 Taxa Sucesso (Faturamento): {taxa_faturamento:.1f}%")
        print(f"📅 Taxa Sucesso (Ano): {taxa_ano:.1f}%")
        print(f"⏱️ Tempo Médio: {tempo_medio:.2f}s/pergunta")
        print(f"📄 Relatório detalhado salvo: {arquivo_relatorio}")

        if taxa_sucesso >= 90:
            print("🎉 EXCELENTE! Sistema muito consistente!")
        elif taxa_sucesso >= 75:
            print("✅ BOM! Sistema razoavelmente consistente.")
        elif taxa_sucesso >= 50:
            print("⚠️ REGULAR. Precisa de melhorias.")
        else:
            print("❌ CRÍTICO! Sistema inconsistente.")

def main():
    if len(sys.argv) > 1:
        try:
            quantidade = int(sys.argv[1])
        except ValueError:
            print("❌ Quantidade deve ser um número inteiro!")
            return
    else:
        quantidade = 1000

    print(f"🚀 Iniciando teste de consistência para {quantidade} empresas...")

    # Definir seed para reproduzibilidade
    random.seed(42)

    testador = TestadorConsistencia()
    testador.executar_teste_completo(quantidade)

if __name__ == "__main__":
    main()