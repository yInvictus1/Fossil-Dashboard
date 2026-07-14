"""
src/process.py
==============
Pipeline completo de limpeza e enriquecimento do dataset de
ocorrencias de dinossauros (Tarefas 3.1 a 3.4).

Etapas:
  3.1  Normalizar coordenadas geograficas
  3.2  Padronizar intervalos de tempo geologico  -> coluna `era`
  3.3  Enriquecer com pais, continente e familia
  3.4  Tratar valores ausentes + relatorio de qualidade

Entrada : data/raw/ocorrencias_completas.json
          data/raw/taxonomia.json
Saida   : data/processed/ocorrencias_clean.csv   (pos 3.1)
          data/processed/ocorrencias_final.csv   (pos 3.4)
          docs/qualidade_dados.md
"""

import json
import pathlib
from datetime import datetime, timezone

import pandas as pd

# ── Caminhos ────────────────────────────────────────────────────────
ROOT = pathlib.Path(__file__).resolve().parent.parent
RAW_OCORRENCIAS = ROOT / "data" / "raw" / "ocorrencias_completas.json"
RAW_TAXONOMIA = ROOT / "data" / "raw" / "taxonomia.json"
OUT_CLEAN = ROOT / "data" / "processed" / "ocorrencias_clean.csv"
OUT_FINAL = ROOT / "data" / "processed" / "ocorrencias_final.csv"
OUT_QUALIDADE = ROOT / "docs" / "qualidade_dados.md"

# ── Mapeamento de estagios geologicos para eras ────────────────────
# Fonte: Escala ICS + nomes usados pela PBDB (sub-estagios, NALMAs)

_TRIASSIC_STAGES = {
    "Anisian", "Carnian", "Ladinian", "Norian", "Olenekian", "Rhaetian",
    "Triassic",
    # sub-estagios PBDB
    "Alaunian", "Lacian", "Longobardian", "Sevatian", "Smithian", "Tuvalian",
}

_JURASSIC_STAGES = {
    "Aalenian", "Bajocian", "Bathonian", "Callovian", "Hettangian",
    "Kimmeridgian", "Oxfordian", "Pliensbachian", "Sinemurian",
    "Tithonian", "Toarcian", "Jurassic",
    # sub-estagios PBDB
    "Puaroan", "Tenuicostatum",
}

_CRETACEOUS_STAGES = {
    "Albian", "Aptian", "Barremian", "Berriasian", "Campanian",
    "Cenomanian", "Coniacian", "Hauterivian", "Maastrichtian",
    "Santonian", "Turonian", "Valanginian", "Cretaceous",
    # NALMAs / nomes PBDB
    "Edmontonian", "Gallic", "Judithian", "Lancian", "Neocomian", "Senonian",
}


def _build_interval_map() -> dict[str, str]:
    """
    Constroi o dicionario completo de mapeamento early_interval -> era.
    Inclui prefixos Early/Middle/Late para cada estagio.
    """
    mapping: dict[str, str] = {}

    for stage_set, era in [
        (_TRIASSIC_STAGES, "Triassic"),
        (_JURASSIC_STAGES, "Jurassic"),
        (_CRETACEOUS_STAGES, "Cretaceous"),
    ]:
        for stage in stage_set:
            mapping[stage] = era
            for prefix in ("Early", "Middle", "Late"):
                mapping[f"{prefix} {stage}"] = era

    return mapping


INTERVAL_MAP = _build_interval_map()


# =====================================================================
# Tarefa 3.1 — Normalizar coordenadas geograficas
# =====================================================================

def carregar_ocorrencias(caminho: pathlib.Path) -> pd.DataFrame:
    """Carrega o JSON bruto e retorna um DataFrame com os registros."""
    with open(caminho, encoding="utf-8") as f:
        dados = json.load(f)
    return pd.DataFrame(dados["records"])


def normalizar_coordenadas(df: pd.DataFrame) -> pd.DataFrame:
    """
    1. Converte lat / lng para float.
    2. Remove registros sem coordenadas.
    3. Filtra valores impossiveis.
    """
    total_inicial = len(df)
    print(f"  {'Registros iniciais':<40} {total_inicial:>7}")

    df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    df["lng"] = pd.to_numeric(df["lng"], errors="coerce")

    antes = len(df)
    df = df.dropna(subset=["lat", "lng"])
    sem_coord = antes - len(df)
    print(f"  {'Removidos sem coordenadas (NaN)':<40} {sem_coord:>7}")

    antes = len(df)
    mascara = df["lat"].between(-90, 90) & df["lng"].between(-180, 180)
    df = df[mascara].copy()
    fora = antes - len(df)
    print(f"  {'Removidos com valores impossiveis':<40} {fora:>7}")

    total_removido = total_inicial - len(df)
    print(f"  {'Total removidos':<40} {total_removido:>7}")
    print(f"  {'Registros finais':<40} {len(df):>7}")
    return df


# =====================================================================
# Tarefa 3.2 — Padronizar intervalos de tempo geologico
# =====================================================================

def padronizar_era(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """
    Mapeia oei (early_interval) para a coluna `era`.
    Retorna o DataFrame atualizado e a lista de valores nao mapeados.
    """
    df["era"] = df["oei"].map(INTERVAL_MAP)
    nao_mapeados = sorted(df.loc[df["era"].isna(), "oei"].dropna().unique().tolist())

    if nao_mapeados:
        print(f"  [AVISO] {len(nao_mapeados)} intervalos nao mapeados:")
        for v in nao_mapeados:
            n = (df["oei"] == v).sum()
            print(f"    - '{v}' ({n} registros)")

    df["era"] = df["era"].fillna("Desconhecido")
    contagem = df["era"].value_counts()
    print(f"  Distribuicao por era:")
    for era_val, n in contagem.items():
        print(f"    {era_val:<15} {n:>6}")

    return df, nao_mapeados


# =====================================================================
# Tarefa 3.3 — Enriquecer com pais, continente e familia
# =====================================================================

def enriquecer_geo(df: pd.DataFrame) -> pd.DataFrame:
    """
    Usa reverse_geocoder para obter country code (cc) a partir de lat/lng,
    depois pycountry-convert para obter nome do pais e continente.
    """
    import reverse_geocoder as rg
    import pycountry_convert as pc

    print("  Geocodificacao reversa (reverse_geocoder)...")
    coords = list(zip(df["lat"], df["lng"]))
    results = rg.search(coords)

    df["cc"] = [r["cc"] for r in results]

    # Mapear cc -> nome do pais
    def _country_name(cc: str) -> str:
        try:
            return pc.country_alpha2_to_country_name(cc)
        except (KeyError, ValueError):
            return "Desconhecido"

    # Mapear cc -> continente
    _CONTINENT_NAMES = {
        "AF": "Africa",
        "AN": "Antarctica",
        "AS": "Asia",
        "EU": "Europe",
        "NA": "North America",
        "SA": "South America",
        "OC": "Oceania",
    }

    def _continent(cc: str) -> str:
        try:
            cont_code = pc.country_alpha2_to_continent_code(cc)
            return _CONTINENT_NAMES.get(cont_code, cont_code)
        except (KeyError, ValueError):
            return "Desconhecido"

    df["pais"] = df["cc"].map(_country_name)
    df["continente"] = df["cc"].map(_continent)

    print(f"  Paises unicos   : {df['pais'].nunique()}")
    print(f"  Continentes     : {sorted(df['continente'].unique().tolist())}")

    return df


def _build_family_map(tax_path: pathlib.Path) -> dict[str, str]:
    """
    Constroi um dicionario {nome_taxon: nome_familia}
    percorrendo a arvore taxonomica do PBDB.
    """
    with open(tax_path, encoding="utf-8") as f:
        recs = json.load(f)["records"]

    # Indexar por oid
    by_oid: dict[str, dict] = {r["oid"]: r for r in recs}
    by_name: dict[str, dict] = {r["nam"]: r for r in recs}

    cache: dict[str, str] = {}

    def _find_family(taxon_name: str) -> str:
        if taxon_name in cache:
            return cache[taxon_name]

        rec = by_name.get(taxon_name)
        if not rec:
            cache[taxon_name] = "Desconhecido"
            return "Desconhecido"

        # Percorrer ancestrais
        visited: set[str] = set()
        cur = rec
        while cur:
            oid = cur["oid"]
            if oid in visited:
                break
            visited.add(oid)

            if cur.get("rnk") == "family":
                familia = cur["nam"]
                # Cachear todo o caminho
                cache[taxon_name] = familia
                return familia

            parent_oid = cur.get("par")
            if not parent_oid or parent_oid not in by_oid:
                break
            cur = by_oid[parent_oid]

        cache[taxon_name] = "Desconhecido"
        return "Desconhecido"

    # Pre-computar para todos os taxa
    for rec in recs:
        _find_family(rec["nam"])

    return cache


def enriquecer_familia(df: pd.DataFrame) -> pd.DataFrame:
    """Adiciona coluna `familia` mapeando tna -> familia taxonomica."""
    print("  Mapeando taxonomia -> familia...")
    family_map = _build_family_map(RAW_TAXONOMIA)

    df["familia"] = df["tna"].map(family_map).fillna("Desconhecido")

    n_desc = (df["familia"] == "Desconhecido").sum()
    print(f"  Familias unicas : {df['familia'].nunique()}")
    print(f"  Sem familia     : {n_desc} registros")
    print(f"  Top 10 familias :")
    for fam, n in df["familia"].value_counts().head(10).items():
        print(f"    {fam:<30} {n:>5}")

    return df


# =====================================================================
# Tarefa 3.4 — Tratar valores ausentes e relatorio de qualidade
# =====================================================================

def tratar_nulos(df: pd.DataFrame) -> pd.DataFrame:
    """Preenche nulos em colunas de filtro com 'Desconhecido'."""
    colunas_filtro = ["era", "pais", "continente", "familia"]
    for col in colunas_filtro:
        nulos = df[col].isna().sum()
        if nulos > 0:
            print(f"  {col}: {nulos} nulos -> 'Desconhecido'")
            df[col] = df[col].fillna("Desconhecido")
    return df


def gerar_relatorio_qualidade(
    df: pd.DataFrame,
    nao_mapeados: list[str],
    caminho: pathlib.Path,
) -> None:
    """Gera docs/qualidade_dados.md com estatisticas de completude."""
    total = len(df)
    agora = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    linhas = [
        "# Relatorio de Qualidade dos Dados",
        "",
        f"> Gerado automaticamente em {agora} por `src/process.py`",
        "",
        "---",
        "",
        "## Resumo",
        "",
        f"- **Total de registros**: {total:,}",
        f"- **Fonte**: `data/raw/ocorrencias_completas.json`",
        f"- **Saida**: `data/processed/ocorrencias_final.csv`",
        "",
        "---",
        "",
        "## Completude por coluna",
        "",
        "| Coluna | Preenchidos | Ausentes | Completude (%) |",
        "|--------|------------|----------|----------------|",
    ]

    for col in df.columns:
        preenchidos = df[col].notna().sum()
        ausentes = total - preenchidos
        pct = (preenchidos / total * 100) if total > 0 else 0
        linhas.append(f"| `{col}` | {preenchidos:,} | {ausentes:,} | {pct:.1f}% |")

    linhas += [
        "",
        "---",
        "",
        "## Colunas de filtro — valores 'Desconhecido'",
        "",
        "| Coluna | Total 'Desconhecido' | % do total |",
        "|--------|---------------------|------------|",
    ]

    for col in ["era", "pais", "continente", "familia"]:
        n_desc = (df[col] == "Desconhecido").sum()
        pct = (n_desc / total * 100) if total > 0 else 0
        linhas.append(f"| `{col}` | {n_desc:,} | {pct:.1f}% |")

    linhas += [
        "",
        "---",
        "",
        "## Distribuicao por era geologica",
        "",
        "| Era | Registros | % do total |",
        "|-----|----------|------------|",
    ]
    for era_val, n in df["era"].value_counts().items():
        pct = (n / total * 100) if total > 0 else 0
        linhas.append(f"| {era_val} | {n:,} | {pct:.1f}% |")

    linhas += [
        "",
        "---",
        "",
        "## Distribuicao por continente",
        "",
        "| Continente | Registros | % do total |",
        "|-----------|----------|------------|",
    ]
    for cont, n in df["continente"].value_counts().items():
        pct = (n / total * 100) if total > 0 else 0
        linhas.append(f"| {cont} | {n:,} | {pct:.1f}% |")

    if nao_mapeados:
        linhas += [
            "",
            "---",
            "",
            "## Intervalos geologicos nao mapeados",
            "",
            "Os seguintes valores de `oei` (early_interval) nao foram mapeados "
            "para nenhuma era e receberam `Desconhecido`:",
            "",
        ]
        for v in nao_mapeados:
            linhas.append(f"- `{v}`")

    linhas.append("")

    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text("\n".join(linhas), encoding="utf-8")
    print(f"  [OK] Relatorio salvo em {caminho}")


# =====================================================================
# Pipeline principal
# =====================================================================

def _sep(titulo: str) -> None:
    print(f"\n{'=' * 55}")
    print(f"  {titulo}")
    print("=" * 55)


def main() -> None:
    _sep("PIPELINE DE PROCESSAMENTO — Fossil Dashboard")
    print(f"  Fonte      : {RAW_OCORRENCIAS}")
    print(f"  Taxonomia  : {RAW_TAXONOMIA}")
    print(f"  Saida clean: {OUT_CLEAN}")
    print(f"  Saida final: {OUT_FINAL}")
    print(f"  Relatorio  : {OUT_QUALIDADE}")

    # ── 3.1 Coordenadas ──────────────────────────────────────────
    _sep("3.1 — Normalizar coordenadas geograficas")
    df = carregar_ocorrencias(RAW_OCORRENCIAS)
    df = normalizar_coordenadas(df)

    OUT_CLEAN.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_CLEAN, index=False)
    print(f"  [OK] Salvo em {OUT_CLEAN}")

    # ── 3.2 Era geologica ────────────────────────────────────────
    _sep("3.2 — Padronizar intervalos de tempo geologico")
    df, nao_mapeados = padronizar_era(df)

    # ── 3.3 Pais, continente, familia ────────────────────────────
    _sep("3.3 — Enriquecer com pais, continente e familia")
    df = enriquecer_geo(df)
    df = enriquecer_familia(df)

    # ── 3.4 Nulos + relatorio ────────────────────────────────────
    _sep("3.4 — Tratar valores ausentes e relatorio de qualidade")
    df = tratar_nulos(df)

    OUT_FINAL.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_FINAL, index=False)
    print(f"  [OK] Dataset final salvo em {OUT_FINAL}")

    gerar_relatorio_qualidade(df, nao_mapeados, OUT_QUALIDADE)

    _sep("PIPELINE CONCLUIDO")
    print(f"  Registros finais: {len(df):,}")
    print(f"  Colunas         : {list(df.columns)}")


if __name__ == "__main__":
    main()
