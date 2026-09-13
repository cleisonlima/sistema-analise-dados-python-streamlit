# Radar de Vendas

Projeto de análise de dados de e-commerce com Python, pandas, NumPy, Matplotlib, Plotly e Streamlit. A aplicação transforma uma base transacional bruta em indicadores comerciais, visualizações interativas e segmentação de clientes.

## Acesso ao dashboard

**[Abrir dashboard online](https://laughing-space-waddle-pq45qqjx75hq7p-8501.app.github.dev/)**

O endereço acima aponta para a página do dashboard, não para o repositório. Ele fica disponível enquanto o Codespace e o servidor Streamlit estiverem ativos.

## Resumo executivo

Com a base demonstrativa tratada, o painel apresenta:

- **R$ 172.100,04** em receita líquida de pedidos concluídos;
- **445 pedidos** concluídos;
- **203 clientes** identificados;
- **R$ 386,74** de ticket médio;
- **3,86 / 5** de satisfação média;
- **61,81%** de participação de pedidos concluídos na base original.

Esses números são demonstrativos, pois o conjunto de dados é sintético. O objetivo é mostrar um fluxo completo e reproduzível de análise, e não representar resultados reais de uma empresa.

## O que foi feito

### 1. Geração e auditoria da base

O arquivo `data/raw/vendas_ecommerce.csv` contém pedidos de e-commerce entre 2024 e 2025. Cada linha representa um pedido e possui data, cliente, localização, categoria, produto, quantidade, preço, desconto, meio de pagamento, status e satisfação.

A base foi construída com problemas intencionais que aparecem em projetos reais: 723 linhas brutas, 3 pedidos duplicados, 29 idades ausentes, diferenças de capitalização e espaços em campos categóricos, além de pedidos concluídos, cancelados e em processamento.

### 2. Tratamento dos dados

O módulo `src/analysis.py` executa o pipeline de preparação:

1. remove duplicidades pelo identificador do pedido;
2. converte datas e colunas numéricas;
3. padroniza campos categóricos e textos;
4. preenche idades ausentes pela mediana;
5. elimina registros sem campos essenciais ou com valores inválidos;
6. calcula receita bruta, desconto, receita líquida e mês de competência;
7. salva o resultado em `data/processed/vendas_tratadas.csv`.

As métricas financeiras usadas no painel são:

```text
receita bruta = quantidade x preço unitário
valor do desconto = receita bruta x percentual de desconto
receita líquida = receita bruta - valor do desconto
ticket médio = receita líquida / quantidade de pedidos concluídos
```

### 3. Análise exploratória

O script `scripts/run_analysis.py` gera uma visão geral com Matplotlib contendo evolução mensal da receita, receita por categoria, ranking dos dez produtos mais relevantes e relação entre quantidade e receita líquida.

### 4. Dashboard interativo

O `app.py` apresenta uma camada executiva com tema escuro e alto contraste. Os filtros permitem explorar período, categorias, estados e pedidos concluídos.

Os gráficos disponíveis são evolução mensal, mix por categoria, ranking de produtos, ranking de estados e cidades, segmentação RFM, tabela de qualidade da base e downloads dos CSVs.

## Como interpretar o painel

### KPIs

Use receita líquida para avaliar o valor efetivamente gerado após descontos. Compare pedidos, clientes e ticket médio para distinguir crescimento por volume de crescimento por valor. A satisfação ajuda a identificar categorias ou períodos que merecem investigação operacional.

### Evolução mensal

Picos indicam períodos de maior demanda e podem orientar estoque, campanhas e capacidade de atendimento. Uma queda persistente deve ser comparada com descontos, categorias, regiões e status dos pedidos antes de qualquer conclusão.

### Categorias, produtos e estados

Uma categoria com alta receita não é necessariamente a mais eficiente: combine receita com quantidade, pedidos e satisfação. O ranking regional mostra onde concentrar campanhas e estoque, mas diferenças de volume precisam ser analisadas junto ao ticket médio.

### Segmentação RFM

O modelo RFM usa três dimensões por cliente:

- **Recência:** dias desde o último pedido;
- **Frequência:** quantidade de pedidos;
- **Monetário:** total gasto.

Os segmentos representam clientes fieis, clientes de alto valor, clientes em risco, clientes inativos e oportunidades de desenvolvimento. Essa segmentação pode orientar retenção, recuperação e ofertas personalizadas.

## Estrutura do projeto

```text
app.py                              Dashboard Streamlit
src/analysis.py                     Tratamento, KPIs e análises
scripts/generate_dataset.py         Geração reproduzível do CSV
scripts/run_analysis.py             Análise exploratória Matplotlib
data/raw/vendas_ecommerce.csv      Base bruta
data/processed/vendas_tratadas.csv Base processada
requirements.txt                    Dependências
```

## Execução local

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/generate_dataset.py
python scripts/run_analysis.py
streamlit run app.py
```

Depois, abra o endereço exibido pelo Streamlit, normalmente `http://localhost:8501`.

## Limitações e próximos passos

Este projeto usa dados sintéticos e não inclui custo de aquisição, margem por produto, estoque ou metas comerciais. Em uma aplicação real, os próximos passos seriam integrar uma fonte oficial, criar testes automatizados, adicionar controle de acesso, acompanhar margem e CAC, e publicar o Streamlit em uma infraestrutura persistente.
