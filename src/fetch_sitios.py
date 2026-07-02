"""
src/fetch_sitios.py
===================
Busca os sítios de escavação (collections) de Dinosauria
na API PaleobioDB v1.2.

Endpoint : /colls/list.json
Parâmetros: base_name=Dinosauria, show=coords,stratext,paleoloc

Os campos extras enriquecem o dataset com:
  • coords    → lat/lng de cada sítio
  • stratext  → formação geológica (formation, member, lithology)
  • paleoloc  → ambiente de deposição (environment, paleolat, paleolng)

Salva o resultado em data/raw/sitios.json.
"""

import json
import os
import sys

import requests

# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------
BASE_URL   = "https://paleobiodb.org/data1.2"
ENDPOINT   = f"{BASE_URL}/colls/list.json"

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR   = os.path.join(PROJECT_ROOT, "data", "raw")
OUTPUT_FILE  = os.path.join(OUTPUT_DIR, "sitios.json")

PARAMS = {
    "base_name": "Dinosauria",
    "show":      "coords,stratext,paleoloc",
    "limit":     "all",
}

# Colunas mínimas esperadas
COLUNAS_OBRIGATORIAS = {"lat", "lng", "oid"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _sep(titulo: str = "") -> None:
    linha = "=" * 60
    if titulo:
        print(f"\n{linha}\n  {titulo}\n{linha}")
    else:
        print(linha)


def validar(registros: list) -> set:
    """Verifica colunas obrigatórias; retorna o conjunto de colunas disponíveis."""
    if not registros:
        print("[AVISO] Nenhum registro retornado.")
        sys.exit(1)

    colunas = set(registros[0].keys())
    faltando = COLUNAS_OBRIGATORIAS - colunas
    if faltando:
        print(f"[ERRO] Colunas obrigatórias ausentes: {sorted(faltando)}")
        sys.exit(1)

    return colunas


# ---------------------------------------------------------------------------
# Coleta principal
# ---------------------------------------------------------------------------

def fetch() -> None:
    _sep("Sítios de escavação — Dinosauria  PBDB v1.2")
    print(f"  Endpoint  : {ENDPOINT}")
    print(f"  Parâmetros: {PARAMS}")

    resp = requests.get(ENDPOINT, params=PARAMS, timeout=180)
    resp.raise_for_status()

    dados     = resp.json()
    registros = dados.get("records", [])
    total     = len(registros)

    print(f"\n  [OK] Status  : {resp.status_code}")
    print(f"  [DADOS] Total: {total} sítios")

    # ------------------------------------------------------------------
    # Validação
    # ------------------------------------------------------------------
    _sep("Validação")
    colunas = validar(registros)
    print(f"  [OK] Colunas obrigatórias : {sorted(COLUNAS_OBRIGATORIAS)}")
    print(f"  [OK] Todas as colunas     : {sorted(colunas)}")

    # ------------------------------------------------------------------
    # Estatísticas rápidas
    # ------------------------------------------------------------------
    _sep("Estatísticas")

    # Distribuição por tipo de depósito (campo "ssc" = litho scale)
    sscs: dict = {}
    for r in registros:
        ssc = r.get("ssc", "desconhecido") or "desconhecido"
        sscs[ssc] = sscs.get(ssc, 0) + 1

    print("  Tipo de depósito — ssc (top 10):")
    for ssc, n in sorted(sscs.items(), key=lambda x: -x[1])[:10]:
        print(f"    {ssc:<35} {n:>5}")

    # Distribuição por formação geológica (campo "sfm")
    fms: dict = {}
    for r in registros:
        fm = r.get("sfm", "desconhecida") or "desconhecida"
        fms[fm] = fms.get(fm, 0) + 1

    print(f"\n  Formações geológicas distintas (sfm): {len(fms)}")
    print("  Formações mais frequentes (top 10):")
    for fm, n in sorted(fms.items(), key=lambda x: -x[1])[:10]:
        print(f"    {fm:<35} {n:>5}")

    # Distribuição por grupo estratigráfico (campo "sgr")
    sgrs: dict = {}
    for r in registros:
        sgr = r.get("sgr", "desconhecido") or "desconhecido"
        sgrs[sgr] = sgrs.get(sgr, 0) + 1

    print(f"\n  Grupos estratigráficos distintos (sgr): {len(sgrs)}")
    print("  Grupos mais frequentes (top 10):")
    for sgr, n in sorted(sgrs.items(), key=lambda x: -x[1])[:10]:
        print(f"    {sgr:<35} {n:>5}")

    # ------------------------------------------------------------------
    # Salvar
    # ------------------------------------------------------------------
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    payload = {
        "total":   total,
        "records": registros,
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    tamanho_mb = os.path.getsize(OUTPUT_FILE) / (1024 * 1024)

    _sep("Concluído")
    print(f"  Arquivo  : {OUTPUT_FILE}")
    print(f"  Tamanho  : {tamanho_mb:.1f} MB")
    print(f"  Registros: {total}")


if __name__ == "__main__":
    fetch()
