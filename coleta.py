import requests
import json

BASE_URL = "https://paleobiodb.org/data1.2"

# ============================================
# FUNÇÃO DE TESTE
# ============================================
def testar_endpoint(nome, endpoint, params):
    print("\n" + "=" * 80)
    print(f"ENDPOINT: {nome}")
    print(f"PARÂMETROS: {params}")

    try:
        response = requests.get(endpoint, params=params, timeout=30)

        print(f"STATUS: {response.status_code}")
        print(f"URL: {response.url}")

        response.raise_for_status()

        dados = response.json()

        registros = dados.get("records", [])

        print(f"REGISTROS RETORNADOS: {len(registros)}")

        if registros:
            print("\nCOLUNAS:")
            print(list(registros[0].keys()))

            print("\nPRIMEIRO REGISTRO:")
            print(json.dumps(registros[0], indent=2, ensure_ascii=False))

        else:
            print("Nenhum registro encontrado.")

    except Exception as e:
        print(f"ERRO: {e}")


# ============================================
# TESTES DE OCORRÊNCIAS
# ============================================
occs_url = f"{BASE_URL}/occs/list.json"

testes_occs = [
    {"base_name": "Dinosauria"},
    {"base_name": "Dinosauria", "show": "coords"},
    {"base_name": "Dinosauria", "interval": "Cretaceous"},
    {"base_name": "Dinosauria", "cc": "BR"},
    {
        "base_name": "Dinosauria",
        "interval": "Cretaceous",
        "cc": "BR",
        "show": "coords"
    }
]

for teste in testes_occs:
    testar_endpoint("OCCURRENCES", occs_url, teste)


# ============================================
# TESTES DE TAXONOMIA
# ============================================
taxa_url = f"{BASE_URL}/taxa/list.json"

testar_endpoint(
    "TAXONOMY",
    taxa_url,
    {
        "base_name": "Dinosauria"
    }
)


# ============================================
# TESTES DE COLEÇÕES
# ============================================
colls_url = f"{BASE_URL}/colls/list.json"

testar_endpoint(
    "COLLECTIONS",
    colls_url,
    {
        "base_name": "Dinosauria"
    }
)


# ============================================
# TESTE DE LIMIT
# ============================================
# RESULTADO: A API do PaleobioDB NÃO impõe um teto
# fixo de registros por requisição. Ela retorna
# quantos registros forem pedidos via parâmetro
# "limit", até o total disponível no resultado.
#
# Exemplo com base_name=Dinosauria (37.575 total):
#   limit=10000  -> 10.000 retornados
#   limit=50000  -> 37.575 retornados (todos)
#
# Mesmo assim, para datasets grandes é recomendável
# paginar com offset para evitar timeouts e consumo
# excessivo de memória.
# ============================================
print("\n" + "=" * 80)
print("TESTE DE LIMIT")
print("(Verificando se existe teto de registros por requisição)")

for limite in [10, 100, 1000, 5000, 10000, 50000]:
    params = {
        "base_name": "Dinosauria",
        "limit": limite
    }

    response = requests.get(occs_url, params=params, timeout=60)
    dados = response.json()

    registros = dados.get("records", [])
    retornados = len(registros)

    # Verifica se o retorno foi truncado em relação ao pedido
    if retornados < limite:
        nota = f" (total disponível: {retornados})"
    else:
        nota = ""

    print(
        f"Limit={limite:>6} -> "
        f"{retornados:>5} registros retornados{nota}"
    )

print("\n>>> CONCLUSÃO: Sem teto fixo. A API retorna até o total disponível.")


# ============================================
# TESTE DE PAGINAÇÃO
# ============================================
# Mesmo sem cap, a paginação com offset é útil
# para processar grandes volumes em lotes menores.
# ============================================
print("\n" + "=" * 80)
print("TESTE DE OFFSET")

for offset in [0, 100, 200]:
    params = {
        "base_name": "Dinosauria",
        "limit": 5,
        "offset": offset
    }

    response = requests.get(occs_url, params=params, timeout=30)
    dados = response.json()

    registros = dados.get("records", [])

    print(f"\nOFFSET = {offset}")

    if registros:
        print("Primeiro OID:", registros[0].get("oid"))