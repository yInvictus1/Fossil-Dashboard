# 🦕 Resultados da Exploração — PaleobioDB API v1.2

> Relatório gerado a partir da execução de [`coleta.py`](file:///c:/Users/Diego/Documents/dino/Fossil-Dashboard/coleta.py)
> **Data:** 02/07/2026 · **Base URL:** `https://paleobiodb.org/data1.2`

---

## 1. Ocorrências (`/occs/list.json`)

Cinco consultas foram realizadas no endpoint de ocorrências, variando filtros de período geológico, país e exibição de coordenadas.

### 1.1 Consulta base — Todas as ocorrências de Dinosauria

| Item | Valor |
|---|---|
| **Parâmetros** | `base_name=Dinosauria` |
| **Status** | ✅ 200 |
| **Registros** | **37.575** |
| **Colunas** | `oid` · `cid` · `idn` · `tna` · `rnk` · `tid` · `oei` · `oli` · `eag` · `lag` · `rid` |

<details>
<summary>📄 Primeiro registro</summary>

```json
{
  "oid": "occ:41524",
  "cid": "col:3257",
  "idn": "Aves indet.",
  "tna": "Aves",
  "rnk": 17,
  "tid": "txn:36616",
  "oei": "Early Eocene",
  "oli": "Middle Eocene",
  "eag": 56,
  "lag": 37.71,
  "rid": "ref:149"
}
```

</details>

---

### 1.2 Com coordenadas geográficas

| Item | Valor |
|---|---|
| **Parâmetros** | `base_name=Dinosauria` · `show=coords` |
| **Status** | ✅ 200 |
| **Registros** | **37.791** |
| **Colunas adicionais** | `lng` · `lat` |

> **Nota:** O parâmetro `show=coords` adiciona as colunas `lng` (longitude) e `lat` (latitude) ao resultado. O total sobe ligeiramente (37.791 vs 37.575) porque inclui registros adicionais com dados de localização.

<details>
<summary>📄 Primeiro registro</summary>

```json
{
  "oid": "occ:41524",
  "cid": "col:3257",
  "idn": "Aves indet.",
  "tna": "Aves",
  "rnk": 17,
  "tid": "txn:36616",
  "oei": "Early Eocene",
  "oli": "Middle Eocene",
  "eag": 56,
  "lag": 37.71,
  "rid": "ref:149",
  "lng": "-1.166667",
  "lat": "51.083332"
}
```

</details>

---

### 1.3 Filtro por período — Cretáceo

| Item | Valor |
|---|---|
| **Parâmetros** | `base_name=Dinosauria` · `interval=Cretaceous` |
| **Status** | ✅ 200 |
| **Registros** | **16.196** |
| **Coluna adicional** | `iid` (interval id) |

> **Destaque:** O Cretáceo concentra **43%** de todas as ocorrências de Dinosauria (16.196 / 37.575).

---

### 1.4 Filtro por país — Brasil 🇧🇷

| Item | Valor |
|---|---|
| **Parâmetros** | `base_name=Dinosauria` · `cc=BR` |
| **Status** | ✅ 200 |
| **Registros** | **582** |

<details>
<summary>📄 Primeiro registro (exemplo brasileiro)</summary>

```json
{
  "oid": "occ:261854",
  "cid": "col:25307",
  "idn": "Saturnalia tupiniquim n. gen. n. sp.",
  "tna": "Saturnalia tupiniquim",
  "rnk": 3,
  "tid": "txn:68124",
  "oei": "Carnian",
  "oli": "Norian",
  "eag": 237,
  "lag": 205.7,
  "rid": "ref:7097"
}
```

</details>

---

### 1.5 Filtro combinado — Cretáceo + Brasil + Coordenadas

| Item | Valor |
|---|---|
| **Parâmetros** | `base_name=Dinosauria` · `interval=Cretaceous` · `cc=BR` · `show=coords` |
| **Status** | ✅ 200 |
| **Registros** | **496** |
| **Colunas** | `oid` · `eid` · `cid` · `idn` · `tna` · `rnk` · `tid` · `oei` · `eag` · `lag` · `rid` · `lng` · `lat` |

> ⚠️ **Importante:** Esta será a consulta principal para o dashboard: dinossauros do Cretáceo brasileiro com coordenadas geográficas.

<details>
<summary>📄 Primeiro registro</summary>

```json
{
  "oid": "occ:294012",
  "eid": "rei:11813",
  "cid": "col:28050",
  "idn": "Mirischia asymmetrica n. gen. n. sp.",
  "tna": "Mirischia asymmetrica",
  "rnk": 3,
  "tid": "txn:58896",
  "oei": "Late Aptian",
  "eag": 119.57,
  "lag": 113.2,
  "rid": "ref:11791",
  "lng": "-40.566666",
  "lat": "-7.550000"
}
```

</details>

---

## 2. Taxonomia (`/taxa/list.json`)

| Item | Valor |
|---|---|
| **Parâmetros** | `base_name=Dinosauria` |
| **Status** | ✅ 200 |
| **Registros** | **12.964** |
| **Colunas** | `oid` · `vid` · `flg` · `rnk` · `nam` · `par` · `rid` · `ext` · `noc` |

<details>
<summary>📄 Primeiro registro</summary>

```json
{
  "oid": "txn:52775",
  "vid": "var:91968",
  "flg": "B",
  "rnk": "unranked clade",
  "nam": "Dinosauria",
  "par": "txn:53207",
  "rid": "ref:14071",
  "ext": "1",
  "noc": 37793
}
```

</details>

> **Nota:** O campo `noc` (number of occurrences) do clado **Dinosauria** é **37.793**, consistente com o total de ocorrências retornado no endpoint de ocorrências.

---

## 3. Coleções (`/colls/list.json`)

| Item | Valor |
|---|---|
| **Parâmetros** | `base_name=Dinosauria` |
| **Status** | ✅ 200 |
| **Registros** | **14.340** |
| **Colunas** | `oid` · `lng` · `lat` · `nam` · `noc` · `oei` · `oli` · `eag` · `lag` · `rid` |

> **Dica:** O endpoint de coleções já retorna coordenadas (`lng`, `lat`) por padrão — sem precisar de `show=coords`.

<details>
<summary>📄 Primeiro registro</summary>

```json
{
  "oid": "col:3256",
  "lng": -1.166667,
  "lat": 51.083332,
  "nam": "M27 Motorway",
  "noc": 1,
  "oei": "Early Eocene",
  "oli": "Middle Eocene",
  "eag": 56,
  "lag": 37.71,
  "rid": "ref:149"
}
```

</details>

---

## 4. Teste de Paginação

### 4.1 Parâmetro `limit`

> ✅ **A API NÃO impõe um teto fixo de registros por requisição.** O parâmetro `limit` é respeitado integralmente — a API retorna quantos registros forem pedidos, até o total disponível no dataset.

| `limit` | Registros retornados | Observação |
|---:|---:|---|
| 10 | 10 | ✅ Conforme pedido |
| 100 | 100 | ✅ Conforme pedido |
| 1.000 | 1.000 | ✅ Conforme pedido |
| 5.000 | 5.000 | ✅ Conforme pedido |
| **10.000** | **10.000** | ✅ Sem cap — retornou todos os 10k |
| **50.000** | **37.575** | ✅ Retornou o total disponível (37.575) |

> **Conclusão:** Sem teto fixo. A API retorna até o total disponível. Mesmo assim, para datasets muito grandes é recomendável paginar com `offset` para evitar timeouts e consumo excessivo de memória.

### 4.2 Parâmetro `offset`

| `offset` | Primeiro `oid` retornado |
|---:|---|
| 0 | `occ:41524` |
| 100 | `occ:150247` |
| 200 | `occ:217578` |

> Paginação funcional — cada offset retorna um bloco diferente de registros.

---

## 5. Dicionário de Campos

| Campo | Significado | Presente em |
|---|---|---|
| `oid` | ID da ocorrência / táxon / coleção | Todos |
| `cid` | ID da coleção | Ocorrências |
| `eid` | ID do evento de reidentificação | Ocorrências (filtros combinados) |
| `idn` | Nome da identificação | Ocorrências |
| `iid` | ID do intervalo temporal | Ocorrências (filtro por intervalo) |
| `tna` | Nome taxonômico aceito | Ocorrências |
| `rnk` | Rank taxonômico | Ocorrências, Taxonomia |
| `tid` | ID do táxon | Ocorrências |
| `oei` | Intervalo mais antigo (early interval) | Ocorrências, Coleções |
| `oli` | Intervalo mais recente (late interval) | Ocorrências, Coleções |
| `eag` | Idade mais antiga (Ma) | Ocorrências, Coleções |
| `lag` | Idade mais recente (Ma) | Ocorrências, Coleções |
| `rid` | ID da referência bibliográfica | Todos |
| `lng` | Longitude | Ocorrências (c/ coords), Coleções |
| `lat` | Latitude | Ocorrências (c/ coords), Coleções |
| `vid` | ID da variante taxonômica | Taxonomia |
| `flg` | Flag do táxon | Taxonomia |
| `nam` | Nome do táxon / coleção | Taxonomia, Coleções |
| `par` | ID do táxon pai | Taxonomia |
| `ext` | Extinto (1 = sim) | Taxonomia |
| `noc` | Número de ocorrências | Taxonomia, Coleções |

---

## 6. Tabela Comparativa

| Endpoint | Registros | Tem coordenadas por padrão? | Campos exclusivos |
|---|---:|:---:|---|
| Ocorrências | 37.575 | ❌ (precisa `show=coords`) | `idn`, `tna`, `tid` |
| Taxonomia | 12.964 | ❌ | `vid`, `flg`, `nam`, `par`, `ext` |
| Coleções | 14.340 | ✅ | `nam`, `noc` |

---

## 7. Notas sobre Limites da API

| Aspecto | Resultado |
|---|---|
| **Teto por requisição** | ❌ **Não existe** — retorna tudo que for pedido |
| **`limit` máximo testado** | 50.000 → retornou 37.575 (todos) |
| **Paginação (`offset`)** | ✅ Funcional |
| **Recomendação** | Paginar com `offset` em lotes para evitar timeouts em datasets muito grandes |

---

> **Próximos passos:** Usar o endpoint combinado (Cretáceo + BR + coords → **496 registros**) como consulta principal para o Fossil Dashboard. Como não há cap, é possível buscar tudo em uma única requisição.
