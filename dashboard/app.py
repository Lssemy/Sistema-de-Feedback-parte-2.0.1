import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import os
from datetime import datetime

API_URL = os.environ.get("API_URL", "http://api:8000")

st.set_page_config(
    page_title="Dashboard de Análise de Feedback",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 Dashboard de Análise de Feedback - Cursos Livres")
st.caption("Monitoramento interativo da satisfação e qualidade dos cursos oferecidos.")

@st.cache_data(ttl=300)
def carregar_feedbacks():
    response = requests.get(f"{API_URL}/feedbacks")
    response.raise_for_status()
    return pd.DataFrame(response.json())

@st.cache_data(ttl=300)
def carregar_analise():
    response = requests.get(f"{API_URL}/feedbacks/analise")
    response.raise_for_status()
    return pd.DataFrame(response.json())

def inserir_feedback(dados):
    response = requests.post(f"{API_URL}/feedbacks", json=dados)
    response.raise_for_status()
    return True

try:
    df_feedbacks = carregar_feedbacks()
    df_analise = carregar_analise()

    if not df_feedbacks.empty:
        df_feedbacks = df_feedbacks.rename(columns={
            'id_curso': 'Curso',
            'data_feedback': 'Data',
            'recomendacao': 'Recomendação',
            'comentario': 'Comentário',
            'qualidade_conteudo': 'Qualidade do Conteúdo',
            'qualidade_instrutor': 'Qualidade do Instrutor'
        })
        df_feedbacks['Data'] = pd.to_datetime(df_feedbacks['Data'])
        df_feedbacks['Qualidade do Conteúdo (★)'] = df_feedbacks['Qualidade do Conteúdo'].apply(lambda x: '★' * int(round(x)))
        df_feedbacks['Qualidade do Instrutor (★)'] = df_feedbacks['Qualidade do Instrutor'].apply(lambda x: '★' * int(round(x)))

    if not df_analise.empty:
        df_analise = df_analise.rename(columns={
            'curso': 'Curso',
            'total_avaliacoes': 'Total de Avaliações',
            'media_conteudo': 'Média de Conteúdo',
            'media_instrutor': 'Média do Instrutor',
            'percentual_sim': '% Recomendação Positiva'
        })

    tab1, tab2 = st.tabs(["📈 Análise de Dados", "📝 Novo Feedback"])

    with tab1:
        st.markdown("### 📍 Visão Geral")

        total_avaliacoes = df_analise['Total de Avaliações'].sum() if not df_analise.empty else 0
        media_conteudo_geral = df_analise['Média de Conteúdo'].mean() if not df_analise.empty else 0
        media_instrutor_geral = df_analise['Média do Instrutor'].mean() if not df_analise.empty else 0

        if total_avaliacoes > 0:
            percentual_sim_geral = (
                (df_analise['Total de Avaliações'] * (df_analise['% Recomendação Positiva'] / 100)).sum()
                / total_avaliacoes * 100
            )
        else:
            percentual_sim_geral = 0

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total de Avaliações", f"{total_avaliacoes}")
        col2.metric("Média de Conteúdo (★)", f"{media_conteudo_geral:.2f}")
        col3.metric("Média do Instrutor (★)", f"{media_instrutor_geral:.2f}")
        col4.metric("% Recomendação Positiva", f"{percentual_sim_geral:.1f}%")

        st.markdown("---")

        cursos = ["Todos"] + sorted(df_analise["Curso"].unique().tolist()) if not df_analise.empty else ["Todos"]
        curso_selecionado = st.selectbox("Filtrar por Curso:", cursos)

        st.markdown("---")

        col_g1, col_g2 = st.columns(2)

        with col_g1:
            st.subheader("📊 Médias por Curso")
            if not df_analise.empty:
                df_chart = df_analise.sort_values(by="Média de Conteúdo", ascending=False)
                fig_bar = px.bar(
                    df_chart,
                    x="Curso",
                    y=["Média de Conteúdo", "Média do Instrutor"],
                    barmode="group",
                    title="Média de Avaliação por Curso",
                    color_discrete_sequence=px.colors.sequential.Blues_r
                )
                fig_bar.update_layout(yaxis_range=[1, 5])
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("Sem dados disponíveis para gerar gráfico de médias.")

        with col_g2:
            st.subheader("🟢 Proporção de Avaliações por Curso")
            if not df_analise.empty:
                fig_pie = px.pie(
                    df_analise,
                    names="Curso",
                    values="Total de Avaliações",
                    color="Curso",
                    title="Distribuição de Avaliações por Curso",
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("Sem dados para gerar gráfico de proporção.")

        st.markdown("---")

        if not df_feedbacks.empty:
            if curso_selecionado != "Todos":
                df_filtrado = df_feedbacks[df_feedbacks["Curso"] == curso_selecionado]
            else:
                df_filtrado = df_feedbacks

            col_g3, col_g4 = st.columns([2, 1])

            with col_g3:
                st.subheader("📈 Evolução da Qualidade Média")
                df_por_data = (
                    df_filtrado.groupby("Data")
                    .agg({"Qualidade do Conteúdo": "mean", "Qualidade do Instrutor": "mean"})
                    .reset_index()
                )
                if not df_por_data.empty:
                    fig_line = px.line(
                        df_por_data,
                        x="Data",
                        y=["Qualidade do Conteúdo", "Qualidade do Instrutor"],
                        markers=True,
                        title=f"Evolução Temporal - {curso_selecionado if curso_selecionado != 'Todos' else 'Todos os Cursos'}"
                    )
                    fig_line.update_layout(yaxis_range=[1, 5])
                    st.plotly_chart(fig_line, use_container_width=True)
                else:
                    st.info("Nenhum dado temporal disponível.")

            with col_g4:
                st.subheader("🧾 Dados Recentes")
                st.dataframe(
                    df_filtrado[['Curso', 'Data', 'Qualidade do Conteúdo (★)', 'Qualidade do Instrutor (★)', 'Recomendação', 'Comentário']],
                    use_container_width=True,
                    hide_index=True
                )
        else:
            st.warning("Nenhum feedback encontrado.")

    with tab2:
        st.markdown("### ✍️ Adicionar Novo Feedback")

        cursos_disponiveis = df_analise["Curso"].unique().tolist() if not df_analise.empty else ["Curso Padrão"]

        with st.form("form_feedback"):
            data_feedback = st.date_input("Data do Feedback", datetime.now().date())
            curso = st.selectbox("Selecione o Curso:", cursos_disponiveis)
            qualidade_conteudo = st.slider("Qualidade do Conteúdo (1-5)", 1.0, 5.0, 5.0, 0.5)
            qualidade_instrutor = st.slider("Qualidade do Instrutor (1-5)", 1.0, 5.0, 5.0, 0.5)
            recomendacao = st.radio("Recomendaria este curso?", ["Sim", "Não", "Talvez"])
            comentario = st.text_area("Comentário (opcional):")

            enviado = st.form_submit_button("💾 Enviar")

            if enviado:
                novo_feedback = {
                    "data_feedback": data_feedback.isoformat(),
                    "id_curso": curso,
                    "qualidade_conteudo": qualidade_conteudo,
                    "qualidade_instrutor": qualidade_instrutor,
                    "recomendacao": recomendacao,
                    "comentario": comentario
                }
                try:
                    if inserir_feedback(novo_feedback):
                        st.success("Feedback adicionado com sucesso!")
                        carregar_feedbacks.clear()
                        carregar_analise.clear()
                        st.rerun()
                except requests.exceptions.RequestException as e:
                    st.error(f"Erro ao enviar feedback: {e}")

except requests.exceptions.RequestException as e:
    st.error(f"Erro de comunicação com a API: {e}")
except Exception as e:
    st.error(f"Erro inesperado: {e}")
