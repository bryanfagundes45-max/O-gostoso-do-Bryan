import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import io

# ---------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# ---------------------------------------------------------
st.set_page_config(
    page_title="bryan gostoso",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# TÍTULO E INSTRUÇÕES
# ---------------------------------------------------------
st.title("🔬 bryan gostoso")
st.markdown("Crie, compare e analise múltiplas curvas de calibração em poucos cliques.")

with st.expander("📖 **Como usar este aplicativo (Clique para abrir)**"):
    st.markdown(
        "**Bem-vindo ao Gerador de Gráficos Analíticos!**\n\n"
        "1. **Dados:** Logo abaixo, você verá uma tabela. Você pode digitar seus dados diretamente nela, adicionar novas linhas no final ou colar valores do Excel.\n"
        "   - *Para adicionar uma nova curva, basta criar uma nova coluna clicando no cabeçalho da tabela.*\n"
        "2. **Configurações (Menu Lateral):** Use a barra escura à esquerda para escolher qual coluna será o Eixo X (Concentração) e quais serão o Eixo Y (Sinal Analítico/Absorbância).\n"
        "3. **Regressão Linear:** Ative a opção na barra lateral para calcular automaticamente a equação da reta ($y = ax + b$) e o $R^2$.\n"
        "4. **Amostra Desconhecida:** Role até a seção de Resultados para calcular a concentração de uma amostra a partir do seu sinal."
    )

st.divider()

# ---------------------------------------------------------
# DADOS DA TABELA
# ---------------------------------------------------------
st.subheader("📝 1. Insira ou Edite seus Dados")
st.info("Dica: Dê um duplo clique nas células para editar. Você pode adicionar mais colunas para comparar mais amostras!")

# Dados iniciais padrão
dados_iniciais = pd.DataFrame({
    'Concentração (mg/L)': [0.0, 2.0, 4.0, 6.0, 8.0, 10.0],
    'Amostra A (Abs)': [0.005, 0.120, 0.245, 0.360, 0.485, 0.590],
    'Amostra B (Abs)': [0.010, 0.150, 0.300, 0.450, 0.600, 0.750]
})

df = st.data_editor(dados_iniciais, num_rows="dynamic", use_container_width=True)
colunas = df.columns.tolist()

# ---------------------------------------------------------
# BARRA LATERAL (SIDEBAR)
# ---------------------------------------------------------
st.sidebar.header("⚙️ Configurações do Gráfico")

coluna_x = st.sidebar.selectbox("Eixo X (Referência)", colunas, index=0)
colunas_y = st.sidebar.multiselect("Eixo Y (Curvas a plotar)", colunas, default=colunas[1:] if len(colunas)>1 else colunas)

st.sidebar.divider()
st.sidebar.subheader("🎨 Estilo")
tipo_grafico = st.sidebar.radio("Estilo dos Pontos", ["Linha com Pontos", "Apenas Pontos"])
nome_eixo_x = st.sidebar.text_input("Nome Eixo X no gráfico", value=coluna_x)
nome_eixo_y = st.sidebar.text_input("Nome Eixo Y no gráfico", value="Sinal Analítico")

st.sidebar.divider()
st.sidebar.subheader("📈 Matemática")
incluir_tendencia = st.sidebar.checkbox("Mostrar Retas de Regressão Linear", value=True)

# ---------------------------------------------------------
# ÁREA PRINCIPAL - GRÁFICO E RESULTADOS
# ---------------------------------------------------------
st.divider()

col_grafico, col_resultados = st.columns([2, 1])
equacoes = {}

with col_grafico:
    st.subheader("📊 2. Gráfico Gerado")
    fig, ax = plt.subplots(figsize=(10, 6))
    cores = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2']

    if not colunas_y:
        st.warning("⚠️ Por favor, selecione pelo menos uma coluna para o Eixo Y na barra lateral.")
    else:
        for i, col_y in enumerate(colunas_y):
            cor = cores[i % len(cores)]
            df_clean = df.dropna(subset=[coluna_x, col_y])
            x = df_clean[coluna_x].astype(float)
            y = df_clean[col_y].astype(float)

            if tipo_grafico == "Linha com Pontos":
                ax.plot(x, y, marker='o', color=cor, linestyle='-', alpha=0.5, label=f'{col_y} (Pontos)')
            else:
                ax.scatter(x, y, color=cor, marker='o', s=60, alpha=0.7, label=f'{col_y} (Pontos)')

            if incluir_tendencia and len(x) > 1:
                coef = np.polyfit(x, y, 1)
                coef_a, coef_b = coef[0], coef[1]
                poly1d_fn = np.poly1d(coef)

                yhat = poly1d_fn(x)
                ybar = np.sum(y) / len(y)
                ssreg = np.sum((yhat - ybar)**2)
                sstot = np.sum((y - ybar)**2)
                r_squared = ssreg / sstot if sstot != 0 else 0

                equacoes[col_y] = {'a': coef_a, 'b': coef_b, 'r2': r_squared}
                ax.plot(x, poly1d_fn(x), color=cor, linestyle='--', linewidth=2, label=f'{col_y} (Reta)')

        ax.set_xlabel(nome_eixo_x, fontsize=12, fontweight='bold')
        ax.set_ylabel(nome_eixo_y, fontsize=12, fontweight='bold')
        ax.set_title("Curvas de Calibração Analítica", fontsize=15, fontweight='bold', pad=15)
        ax.grid(True, linestyle=':', alpha=0.7)
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', frameon=True, shadow=True)

        st.pyplot(fig)

        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=300, bbox_inches="tight")
        buf.seek(0)
        st.download_button("📥 Baixar Gráfico em Alta Resolução (PNG)", data=buf, file_name="grafico_calibracao.png", mime="image/png", use_container_width=True)

with col_resultados:
    st.subheader("🧮 3. Resultados")
    if incluir_tendencia and equacoes:
        st.markdown("**Equações da Reta Obtidas:**")
        for nome, eq in equacoes.items():
            with st.container():
                st.markdown(f"<span style='color:#1f77b4; font-weight:bold;'>{nome}</span>", unsafe_allow_html=True)
                st.latex(f"y = {eq['a']:.4f}x {'+' if eq['b'] >= 0 else ''} {eq['b']:.4f}")
                st.latex(f"R^2 = {eq['r2']:.5f}")

        st.divider()
        st.markdown("### 🧪 Prever Amostra Desconhecida")
        st.markdown("<small>Use a equação da reta para descobrir a concentração.</small>", unsafe_allow_html=True)

        curva_escolhida = st.selectbox("1. Qual curva usar?", list(equacoes.keys()))
        y_amostra = st.number_input("2. Digite o Sinal Medido (Y):", format="%.4f")

        if st.button("Calcular Concentração", type="primary", use_container_width=True):
            eq_ref = equacoes[curva_escolhida]
            if eq_ref['a'] != 0:
                x_calc = (y_amostra - eq_ref['b']) / eq_ref['a']
                st.success(f"A concentração calculada é:\n### **{x_calc:.4f}**")
            else:
                st.error("Erro: A inclinação da reta é zero.")
    else:
        st.info("👈 Ative a opção **Mostrar Retas de Regressão Linear** na barra lateral para ver as equações e usar a calculadora de amostras.")
