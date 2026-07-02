"""
src/fetch_pbdb.py
=================
Coleta o dataset completo de ocorrências de Dinosauria
contornando o limite de 5 000 registros por requisição.

Estratégia: uma requisição por período geológico
    • Triassic   (~235 – 201 Ma)
    • Jurassic   (~201 – 145 Ma)
    • Cretaceous (~145 –  66 Ma)

Os resultados são concatenados e deduplicados por
occurrence_no (campo "oid") antes de serem salvos em
    data/raw/ocorrencias_completas.json
"""

import json
import os
import sys
import time

import requests

# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------
BASE_URL    = "https://paleobiodb.org/data1.2"
ENDPOINT    = f"{BASE_URL}/occs/list.json"

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR   = os.path.join(PROJECT_ROOT, "data", "raw")
OUTPUT_FILE  = os.path.join(OUTPUT_DIR, "ocorrencias_completas.json")

# Campos obrigatórios para validação
COLUNAS_OBRIGATORIAS = {"lat", "lng", "oei", "oid"}

# Parâmetros-base (comuns a todos os períodos)
BASE_PARAMS = {
    "base_name": "Dinosauria",
    "show":      "coords,coll,time",
    "limit":     "all",
}

# Períodos geológicos a coletar
PERIODOS = ["Triassic", "Jurassic", "Cretaceous"]


# ---------------------------------------------------------------------------
# Funções auxiliares
# ---------------------------------------------------------------------------

def _separador(titulo: str = "") -> None:
    linha = "=" * 60
    if titulo:
        print(f"\n{linha}")
        print(f"  {titulo}")
        print(linha)
    else:
        print(linha)


def fetch_periodo(periodo: str, tentativas: int = 3, espera: int = 10) -> list:
    """
    Faz a requisição para um único período geológico.
    Retorna a lista de registros (records).
    Tenta novamente até `tentativas` vezes em caso de erro de rede.
    """
    params = {**BASE_PARAMS, "interval": periodo}
    _separador(f"Período: {periodo}")
    print(f"  Endpoint : {ENDPOINT}")
    print(f"  Parâmetros: {params}")

    for tentativa in range(1, tentativas + 1):
        try:
            resp = requests.get(ENDPOINT, params=params, timeout=180)
            resp.raise_for_status()
            dados = resp.json()
            registros = dados.get("records", [])
            total = len(registros)
            print(f"  [OK] Status {resp.status_code} — {total} registros retornados")
            return registros

        except requests.RequestException as exc:
            print(f"  [ERRO] Tentativa {tentativa}/{tentativas}: {exc}")
            if tentativa < tentativas:
                print(f"  Aguardando {espera}s antes de tentar novamente...")
                time.sleep(espera)
            else:
                print(f"  [FALHA] Não foi possível coletar {periodo}. Abortando.")
                sys.exit(1)

    return []


def deduplicar(registros: list) -> list:
    """
    Remove duplicatas mantendo a primeira ocorrência de cada `oid`
    (occurrence_no no formato 'occ:XXXXXX').
    """
    vistos = set()
    unicos = []
    for rec in registros:
        oid = rec.get("oid", "")
        if oid not in vistos:
            vistos.add(oid)
            unicos.append(rec)
    return unicos


def validar(registros: list) -> None:
    """
    Verifica se as colunas obrigatórias estão presentes.
    Encerra o script se alguma estiver faltando.
    """
    if not registros:
        print("[AVISO] Nenhum registro após deduplicação. Abortando.")
        sys.exit(1)

    colunas = set(registros[0].keys())
    faltando = COLUNAS_OBRIGATORIAS - colunas
    if faltando:
        print(f"[ERRO] Colunas obrigatórias ausentes: {faltando}")
        sys.exit(1)

    print(f"  [OK] Colunas obrigatórias presentes: {sorted(COLUNAS_OBRIGATORIAS)}")
    print(f"  [OK] Todas as colunas disponíveis : {sorted(colunas)}")


# ---------------------------------------------------------------------------
# Ponto de entrada
# ---------------------------------------------------------------------------

def main() -> None:
    _separador("Coleta completa de Dinosauria — PBDB v1.2")
    print("  Estratégia: uma requisição por período geológico")
    print("  Períodos   : " + ", ".join(PERIODOS))
    print("  Saída      : " + OUTPUT_FILE)

    # ------------------------------------------------------------------
    # 1. Coleta por período
    # ------------------------------------------------------------------
    todos = []
    contagem_por_periodo = {}

    for periodo in PERIODOS:
        registros = fetch_periodo(periodo)
        contagem_por_periodo[periodo] = len(registros)
        todos.extend(registros)
        time.sleep(1)   # pausa cortês entre requisições

    _separador("Resumo da coleta")
    for periodo, n in contagem_por_periodo.items():
        print(f"  {periodo:<12} {n:>6} registros")
    print(f"  {'TOTAL (bruto)':<12} {len(todos):>6} registros")

    # ------------------------------------------------------------------
    # 2. Deduplicação
    # ------------------------------------------------------------------
    unicos = deduplicar(todos)
    duplicatas = len(todos) - len(unicos)
    print(f"\n  Duplicatas removidas : {duplicatas}")
    print(f"  Registros únicos     : {len(unicos)}")

    # ------------------------------------------------------------------
    # 3. Validação
    # ------------------------------------------------------------------
    _separador("Validação")
    validar(unicos)

    # ------------------------------------------------------------------
    # 4. Salvar JSON consolidado
    # ------------------------------------------------------------------
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    payload = {
        "records_by_period": contagem_por_periodo,
        "total_bruto":       len(todos),
        "total_unicos":      len(unicos),
        "duplicatas":        duplicatas,
        "records":           unicos,
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    tamanho_mb = os.path.getsize(OUTPUT_FILE) / (1024 * 1024)
    _separador("Concluído")
    print(f"  Arquivo  : {OUTPUT_FILE}")
    print(f"  Tamanho  : {tamanho_mb:.1f} MB")
    print(f"  Registros: {len(unicos)}")


if __name__ == "__main__":
    main()
