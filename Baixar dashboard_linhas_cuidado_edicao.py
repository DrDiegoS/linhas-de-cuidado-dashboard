
import streamlit as st
import pandas as pd
import plotly.express as px

CAMINHO_ARQUIVO = "dashacompanhamento.xlsx"

# Carregar os dados
@st.cache_data
def carregar_dados():
    return pd.read_excel(CAMINHO_ARQUIVO)

def salvar_dados(df):
    df.to_excel(CAMINHO_ARQUIVO, index=False)

df = carregar_dados()

st.title("📊 Dashboard de Linhas de Cuidado")

# Filtros
st.sidebar.header("🔍 Filtros")
linhas = st.sidebar.multiselect("Linha de Cuidado", options=df["Linha de Cuidado"].unique(), default=df["Linha de Cuidado"].unique())
fases = st.sidebar.multiselect("Fase", options=df["Fase"].unique(), default=df["Fase"].unique())
status_sel = st.sidebar.multiselect("Status", options=df["Status"].unique(), default=df["Status"].unique())

df_filtrado = df[
    (df["Linha de Cuidado"].isin(linhas)) &
    (df["Fase"].isin(fases)) &
    (df["Status"].isin(status_sel))
]

st.markdown("### 📋 Tabela de Tarefas Filtradas")
st.dataframe(df_filtrado, use_container_width=True)

# Gráfico de barras
st.markdown("### 📊 Distribuição de Status")
fig_status = px.histogram(df_filtrado, x="Status", color="Status", barmode="group", text_auto=True)
st.plotly_chart(fig_status, use_container_width=True)

# Gráfico sunburst
st.markdown("### 🧩 Proporção de Status por Linha de Cuidado")
fig_pizza = px.sunburst(df_filtrado, path=["Linha de Cuidado", "Status"], values=None, color="Status")
st.plotly_chart(fig_pizza, use_container_width=True)

# Progresso por linha de cuidado
st.markdown("### 📈 Progresso por Linha de Cuidado")
df_prog = df_filtrado.copy()
df_prog["Concluído"] = df_prog["Status"].apply(lambda x: 1 if x.lower() == "concluído" else 0)
df_avanco = df_prog.groupby("Linha de Cuidado")["Concluído"].mean().reset_index()
df_avanco["% Concluído"] = (df_avanco["Concluído"] * 100).round(1)
fig_avanco = px.bar(df_avanco, x="Linha de Cuidado", y="% Concluído", text="% Concluído", color="% Concluído", color_continuous_scale="greens")
st.plotly_chart(fig_avanco, use_container_width=True)

# Edição de tarefas
st.markdown("### ✏️ Atualizar Status e Observações")

with st.form("form_edicao"):
    col1, col2, col3 = st.columns(3)
    with col1:
        linha_selecionada = st.selectbox("Linha de Cuidado", df["Linha de Cuidado"].unique())
    with col2:
        fase_selecionada = st.selectbox("Fase", df[df["Linha de Cuidado"] == linha_selecionada]["Fase"].unique())
    with col3:
        tarefa_selecionada = st.selectbox("Tarefa", df[(df["Linha de Cuidado"] == linha_selecionada) & (df["Fase"] == fase_selecionada)]["Tarefa"].unique())

    novo_status = st.selectbox("Novo Status", ["Pendente", "Em andamento", "Concluído"])
    nova_obs = st.text_area("Observações (exibido apenas se não concluído)", height=100)

    submitted = st.form_submit_button("💾 Salvar Alterações")

    if submitted:
        idx = df[
            (df["Linha de Cuidado"] == linha_selecionada) &
            (df["Fase"] == fase_selecionada) &
            (df["Tarefa"] == tarefa_selecionada)
        ].index

        if not idx.empty:
            df.loc[idx, "Status"] = novo_status
            if "Observações" not in df.columns:
                df["Observações"] = ""
            if novo_status != "Concluído":
                df.loc[idx, "Observações"] = nova_obs
            else:
                df.loc[idx, "Observações"] = ""
            salvar_dados(df)
            st.success("Atualização salva com sucesso!")
        else:
            st.error("Tarefa não encontrada.")

# Exportação
st.markdown("### 📥 Exportar dados")
csv = df_filtrado.to_csv(index=False).encode('utf-8')
st.download_button("📤 Baixar CSV filtrado", data=csv, file_name="tarefas_filtradas.csv", mime="text/csv")
