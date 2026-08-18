# 🦠 COVID-19 Worldwide Dashboard

Análise exploratória e dashboard interativo em **Streamlit** sobre a situação global da COVID-19, cobrindo 221 países e territórios: casos, mortes, recuperações, casos ativos e testes realizados — em números absolutos e ajustados por população.

> 🖼️ *Adicione aqui 1-2 screenshots do dashboard depois de rodá-lo localmente ou fazer o deploy (aba "Visão Geral" e aba "Rankings" costumam ficar bem no README).*

---

## 🎯 Objetivo do projeto

Ir além do "quadro geral" da pandemia e responder, com dados, perguntas que costumam ser respondidas de forma superficial — em especial a diferença entre **números absolutos** (que favorecem países grandes) e **números per capita** (que mostram severidade relativa real).

## ❓ Perguntas que o projeto responde

1. Quais países tiveram o maior número **absoluto** de casos e de mortes?
2. Quais países tiveram o maior número de casos e mortes **por 1 milhão de habitantes**?
3. Quais países têm a **maior e a menor taxa de mortalidade** (mortes / casos confirmados)?
4. Como os **continentes** se comparam entre si em casos e mortes?
5. Existe relação entre o **volume de testagem** de um país e o número de casos que ele detecta?
6. Quais países apresentam **dados inconsistentes ou possivelmente subnotificados**?

## 🔎 Principais descobertas

- **Volume absoluto ≠ severidade relativa.** EUA, Índia, França, Alemanha e Brasil lideram em casos absolutos — mas ao ajustar por população, o ranking muda por completo: Coreia do Sul, Áustria e Eslovênia lideram em casos/1M hab., e **Peru, Bulgária e Hungria** lideram em mortes/1M hab. (nenhum desses aparece no top 10 absoluto).
- **Testagem influencia os números oficiais.** Há correlação moderada (≈0,5) entre testes por habitante e casos detectados por habitante — países que testam mais, encontram mais casos. Comparações diretas entre países com políticas de testagem muito diferentes exigem cautela.
- **Taxas de mortalidade muito altas podem indicar subnotificação, não gravidade clínica.** Iêmen (18%), Sudão (7,9%) e Síria (5,5%) têm as maiores taxas de mortalidade do dataset e, ao mesmo tempo, estão entre os países com menor testagem per capita — sinal de que só os casos mais graves chegaram a ser confirmados.
- **Qualidade de dados importa.** A Coreia do Norte reporta 4,77 milhões de casos e apenas 74 mortes (mortalidade ≈0%), sem nenhum dado de testagem — um padrão estatisticamente incompatível com o resto do dataset, tratado como outlier na análise.
- A mortalidade global agregada no snapshot é de aproximadamente **1%** (6,9M mortes em 695M casos confirmados).

📓 A análise completa, com todos os gráficos e o raciocínio por trás de cada resposta, está em [`notebooks/01_covid_eda.ipynb`](notebooks/01_covid_eda.ipynb).

## 🖥️ O dashboard

Construído em Streamlit + Plotly, com 4 seções:

| Aba | Conteúdo |
|---|---|
| 🌍 Visão Geral | Mapa mundial coroplético, distribuição por continente, KPIs globais |
| 🏆 Rankings | Top/bottom N países por qualquer métrica, com opção de excluir microestados dos rankings per capita |
| 🔗 Correlações | Dispersão testes × casos por 1M hab., matriz de correlação entre indicadores |
| 🔍 Explorar por País | Detalhamento de um país específico (composição de casos, testes, taxas) |

Filtros disponíveis na barra lateral: continente, população mínima (para evitar que microestados distorçam rankings per capita), métrica de ranking e quantidade de países exibidos.

## 📁 Estrutura do projeto

```
covid_dashboard/
├── app.py                        # Dashboard Streamlit
├── requirements.txt              # Dependências para rodar o dashboard
├── requirements-notebook.txt     # Dependências extras para rodar o notebook de EDA
├── data/
│   ├── worldwide_covid_data.csv  # Dataset original
│   └── continent_mapping.json    # País -> continente/ISO-3 (enriquecimento)
├── notebooks/
│   └── 01_covid_eda.ipynb        # Análise exploratória completa
└── README.md
```

## 📚 Dicionário de dados

| Coluna original | Descrição |
|---|---|
| `Country/Other` | Nome do país ou território |
| `Total Cases` | Total de casos confirmados de COVID-19 |
| `Total Deaths` | Total de mortes |
| `Total Recovered` | Total de casos recuperados |
| `Active Cases` | Total de casos ativos |
| `Tot Cases/ 1M pop` | Casos totais por 1 milhão de habitantes |
| `Deaths/ 1M pop` | Mortes totais por 1 milhão de habitantes |
| `Total Tests` | Total de testes de COVID-19 realizados |
| `Tests/ 1M pop` | Testes por 1 milhão de habitantes |
| `Population` | População do país |

O dataset é um **snapshot agregado** (uma foto no tempo, não uma série temporal com datas).

## 🧹 Qualidade e tratamento dos dados

- **Sem duplicatas** de países e **sem valores negativos** em nenhuma coluna numérica.
- **Consistência interna validada:** `Total Cases = Total Deaths + Total Recovered + Active Cases` para 100% das linhas com dados completos.
- **Valores ausentes:** `Total Recovered`/`Active Cases` faltam em 20 países e `Total Tests`/`Tests per 1M` em 10 países — mantidos como `NaN` (não preenchidos com 0) para não distorcer médias e rankings.
- **Enriquecimento:** coluna de continente e código ISO-3 adicionada via `pycountry`/`pycountry-convert`, com aliases manuais para nomes não padronizados no dataset (`USA`, `UK`, `S. Korea`, `DPRK`, `DRC`, `CAR`, etc.) — ver `data/continent_mapping.json`.
- **Rankings per capita** (casos/mortes por 1M hab., taxas em %) podem, opcionalmente, excluir países com população abaixo de um limiar (padrão 1M) para evitar que microestados dominem os extremos por efeito estatístico de amostra pequena.

## ⚠️ Limitações

- Dataset é um **snapshot único**, não permite análise de evolução temporal (picos, ondas, tendências).
- Números de casos/testes dependem de **capacidade e política de testagem de cada país** — comparações diretas entre países subestimam a real disseminação onde a testagem foi baixa.
- Ao menos um país (Coreia do Norte) tem dados incompatíveis com o restante do dataset e deve ser interpretado com cautela em qualquer agregação.
- "País/território" inclui algumas entidades não soberanas (ex. Hong Kong, Macao, Channel Islands) — tratadas como unidades geográficas independentes, seguindo a granularidade original do dataset.

## 🚀 Como rodar localmente

```bash
# Clone o repositório
git clone <url-do-repositorio>
cd covid_dashboard

# Crie um ambiente virtual (recomendado)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instale as dependências do dashboard
pip install -r requirements.txt

# Rode o dashboard
streamlit run app.py
```

Para rodar o notebook de EDA:

```bash
pip install -r requirements-notebook.txt
jupyter notebook notebooks/01_covid_eda.ipynb
```

## 🛠️ Tecnologias

- **Python** (pandas, numpy)
- **Streamlit** — dashboard interativo
- **Plotly** — visualizações interativas (mapa coroplético, dispersão, matriz de correlação)
- **Matplotlib / Seaborn** — visualizações estáticas no notebook de EDA
- **pycountry / pycountry-convert** — enriquecimento geográfico (continente, ISO-3)

## ✍️ Autor

*[seu nome]* — Data Scientist / Data Analyst
[LinkedIn](#) · [GitHub](#)
