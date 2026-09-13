from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
from src.analysis import RAW_DATA, calculate_kpis, category_summary, load_and_clean_data, monthly_summary, product_summary, rfm_summary, state_summary

st.set_page_config(page_title="Radar de Vendas", page_icon="📊", layout="wide")

st.markdown("""
<style>
:root { --ink:#f5f7ff; --muted:#aab4d5; --canvas:#0b1030; --surface:#171d50; }
.stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"] { background:radial-gradient(circle at 75% 0%,#20216b 0%,#0b1030 48%,#070b26 100%); color:var(--ink); }
[data-testid="stHeader"] { background:#090d2a; } [data-testid="stSidebar"] { background:#10154a; border-right:1px solid #313a82; }
[data-testid="stSidebar"] * { color:#f5f7ff; } [data-testid="stMain"] h1,[data-testid="stMain"] h2,[data-testid="stMain"] h3,[data-testid="stMain"] p,[data-testid="stMain"] label { color:var(--ink); }
[data-testid="stMain"] h1 { font-weight:800; text-shadow:0 2px 24px #3c44a8; } [data-testid="stMain"] hr { border-color:#30376f; }
.kpi { min-height:104px; background:linear-gradient(135deg,#19215d,#121741); border:1px solid #303b86; border-top:4px solid #16d9ff; padding:14px 18px; border-radius:6px; box-shadow:0 10px 28px #00000033; }
.kpi-label { color:#aab4d5; font-size:.78rem; text-transform:uppercase; letter-spacing:.06em; } .kpi-value { color:#fff; font-size:1.55rem; font-weight:800; margin-top:6px; }
[data-testid="stSidebar"] [data-baseweb="select"] > div,[data-testid="stSidebar"] [data-testid="stDateInput"] { background:#090d28; border-color:#3b4694; }
[data-testid="stExpander"] { background:#111640; border-color:#303b86; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def get_data(): return load_and_clean_data()

def money(value): return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def chart_layout(figure, height):
    figure.update_layout(template="plotly_dark", font=dict(color="#f5f7ff"), paper_bgcolor="#0b1030", plot_bgcolor="#141a4b", height=height, margin=dict(l=10,r=10,t=20,b=10))
    return figure

data, quality = get_data()
st.title("Radar de Vendas")
st.caption("Análise de desempenho do e-commerce | base tratada com pandas")
with st.sidebar:
    st.header("Filtros")
    dates = st.date_input("Período", value=(data.order_date.min().date(), data.order_date.max().date()))
    categories = st.multiselect("Categorias", sorted(data.category.unique()), default=sorted(data.category.unique()))
    states = st.multiselect("Estados", sorted(data.state.unique()), default=sorted(data.state.unique()))
    completed_only = st.checkbox("Somente pedidos concluídos", value=True)
filtered = data.copy()
if len(dates) == 2: filtered = filtered[filtered.order_date.dt.date.between(dates[0], dates[1])]
filtered = filtered[filtered.category.isin(categories) & filtered.state.isin(states)]
if completed_only: filtered = filtered[filtered.is_completed]
metrics = calculate_kpis(filtered)
columns = st.columns(5)
for column, (label, value) in zip(columns, [("Receita líquida",money(metrics["revenue"])),("Pedidos",f"{metrics['orders']:,}"),("Clientes",f"{metrics['customers']:,}"),("Ticket médio",money(metrics["average_ticket"])),("Satisfação",f"{metrics['satisfaction']:.2f} / 5")]):
    column.markdown(f'<div class="kpi"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div></div>', unsafe_allow_html=True)
st.divider()
left, right = st.columns([1.5,1])
with left:
    st.subheader("Evolução mensal")
    monthly = monthly_summary(filtered); figure = px.line(monthly,x="month",y="revenue",markers=True,labels={"month":"Mês","revenue":"Receita"}); figure.update_traces(line_color="#16d9ff",line_width=3); st.plotly_chart(chart_layout(figure,350),width="stretch")
with right:
    st.subheader("Mix por categoria")
    figure = px.pie(category_summary(filtered),values="revenue",names="category",hole=.55,color_discrete_sequence=["#16d6a4","#f59e0b","#2563eb","#f52bbf","#7c3aed"]); st.plotly_chart(chart_layout(figure,350),width="stretch")
st.subheader("Onde está o resultado?")
left, right = st.columns(2)
with left:
    products = product_summary(filtered); figure = px.bar(products.sort_values("revenue"),x="revenue",y="product",color="category",orientation="h",labels={"revenue":"Receita","product":"Produto"}); figure.update_layout(yaxis=dict(categoryorder="total ascending"),xaxis_tickprefix="R$ "); st.plotly_chart(chart_layout(figure,380),width="stretch")
with right:
    regions = state_summary(filtered).head(10); figure = px.bar(regions.sort_values("revenue"),x="revenue",y="state",text="city",orientation="h",color="revenue",color_continuous_scale="Teal"); figure.update_layout(yaxis=dict(categoryorder="total ascending"),xaxis_tickprefix="R$ ",showlegend=False); st.plotly_chart(chart_layout(figure,380),width="stretch")
st.subheader("Segmentação de clientes (RFM)")
rfm = rfm_summary(filtered); left, right = st.columns([1,1.4])
with left: st.dataframe(rfm.segment.value_counts().rename_axis("segment").reset_index(name="customers"),hide_index=True,width="stretch")
with right:
    figure = px.scatter(rfm,x="recency",y="monetary",size="frequency",color="segment",hover_name="customer_id",labels={"recency":"Recência (dias)","monetary":"Valor gasto"}); st.plotly_chart(chart_layout(figure,300),width="stretch")
with st.expander("Qualidade e download"):
    st.write(f"A base bruta tinha **{quality['raw_rows']}** linhas. Foram removidas **{quality['duplicates_removed']}** duplicatas e preenchidas **{quality['missing_ages_filled']}** idades ausentes.")
    st.download_button("Baixar dados tratados",filtered.to_csv(index=False).encode("utf-8"),"vendas_tratadas_filtradas.csv","text/csv")
    st.download_button("Baixar CSV bruto",Path(RAW_DATA).read_bytes(),"vendas_ecommerce.csv","text/csv")
