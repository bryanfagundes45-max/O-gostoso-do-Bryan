import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

# Configuração da página
st.set_page_config(page_title="App do Bryan V4", page_icon="🌟", layout="centered")
st.title("Gerador de Gráficos do Bryan 4.0 🌟")

st.write("Edite seus dados e personalize os textos e nomes dos eixos do seu gráfico!")

# Dados padrão baseados no seu exemplo (Concentração x Absorbância)
dados_iniciais = pd.DataFrame({
    'Concentração': [0.1, 0.2, 0.3, 0.4, 0.5],
    'Absorbância': [0.05, 0.12, 0.25, 0.31, 0.44]
})

st.subheader("📝 Edite seus dados aqui:")
df = st.data_editor(dados_iniciais, num_rows="dynamic")
colunas = df.columns.tolist()

st.write("--- ")
st.subheader("⚙️ Configurações de Dados e Cores")

col1, col2 = st.columns(2)
with col1:
    coluna_x = st.selectbox("Quais dados vão no Eixo X?", colunas, index=0)
    tipo_grafico = st.selectbox("Tipo de Gráfico", ["Linha", "Barra", "Dispersão (Pontos)"])
with col2:
    coluna_y = st.selectbox("Quais dados vão no Eixo Y?", colunas, index=1 if len(colunas) > 1 else 0)
    cor_grafico = st.color_picker("Escolha a cor do gráfico", "#FF4B4B") # Começa vermelho

st.write("--- ")
st.subheader("✍️ Personalizar Textos do Gráfico")
st.write("Digite o que você quer que apareça escrito no gráfico:")

# Novos campos para o usuário digitar os nomes!
col3, col4 = st.columns(2)
with col3:
    nome_eixo_x = st.text_input("Nome para o Eixo X (Linha de baixo)", value=coluna_x)
    nome_eixo_y = st.text_input("Nome para o Eixo Y (Linha do lado)", value=coluna_y)
with col4:
    titulo_grafico = st.text_input("Título Principal do Gráfico", value=f"{coluna_y} por {coluna_x}")

if st.button("Gerar Gráfico e Preparar Download"):
    fig, ax = plt.subplots(figsize=(8, 4))

    if tipo_grafico == "Linha":
        ax.plot(df[coluna_x], df[coluna_y], marker='o', color=cor_grafico, linestyle='-')
    elif tipo_grafico == "Barra":
        ax.bar(df[coluna_x], df[coluna_y], color=cor_grafico)
    elif tipo_grafico == "Dispersão (Pontos)":
        ax.scatter(df[coluna_x], df[coluna_y], color=cor_grafico)

    # Aqui usamos as palavras que você digitou nas caixas de texto!
    ax.set_xlabel(nome_eixo_x)
    ax.set_ylabel(nome_eixo_y)
    ax.set_title(titulo_grafico)

    ax.grid(True, linestyle='--', alpha=0.6)

    st.pyplot(fig)

    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)

    st.download_button(
        label="📥 Baixar Gráfico Personalizado (PNG)",
        data=buf,
        file_name="grafico_bryan_v4.png",
        mime="image/png"
    )
