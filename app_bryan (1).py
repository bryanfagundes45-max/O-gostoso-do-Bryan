
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import io

# ---------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# ---------------------------------------------------------
st.set_page_config(
    page_title="bryan gostoso - Curvas de Calibração",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Variável de memória para saber se o botão de gerar gráfico foi clicado
if 'grafico_gerado' not in st.session_state:
    st.session_state['grafico_gerado'] = False

# ---------------------------------------------------------
# TÍTULO E CABEÇALHO
# ---------------------------------------------------------
st.title("🔬 App dos Estudantes Da UFRGS - Análise Avançada")
st.subheader("Aplicativo interativo e profissional para criação de **Curvas de Calibração**.")

with st.expander("ℹ️ **Guia Rápido (Clique para ler)**"):
    st.markdown("**Como usar:**\n1. No **Menu Lateral (⬅️)**, você pode renomear suas amostras e o eixo X.\n2. Vá na aba **📝 Meus Dados** e preencha sua tabela com os valores.\n3. No **Menu Lateral**, escolha o que vai no eixo X e Y, e defina as **Cores**.\n4. Vá na aba **📊 Gráfico Visual** e clique em **Gerar Gráfico**.\n5. Calcule novas amostras na aba **🧮 Resultados e Amostras**.")

st.divider()

# ---------------------------------------------------------
# BARRA LATERAL (MENU) - PARTE 1: Nomes das Amostras
# ---------------------------------------------------------
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3281/3281307.png", width=80)
st.sidebar.header("⚙️ Configurações Iniciais")

st.sidebar.markdown("**Renomear Colunas da Tabela**")
nome_eixo_x_tabela = st.sidebar.text_input("Nome da Coluna X", value="Concentração (mg/L)")
nome_amostra_1 = st.sidebar.text_input("Nome da 1ª Amostra", value="Amostra A (Abs)")
nome_amostra_2 = st.sidebar.text_input("Nome da 2ª Amostra", value="Amostra B (Abs)")

# ---------------------------------------------------------
# DADOS DA TABELA (Usando os nomes definidos pelo usuário)
# ---------------------------------------------------------
dados_iniciais = pd.DataFrame({
    nome_eixo_x_tabela: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    nome_amostra_1: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    nome_amostra_2: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
})

# ---------------------------------------------------------
# NAVEGAÇÃO POR ABAS (TABS) - Iniciamos a Tabela aqui para pegar as colunas
# ---------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["📝 1. Meus Dados", "📊 2. Gráfico Visual", "🧮 3. Resultados e Amostras"])

with tab1:
    st.subheader("Insira os dados da sua Curva de Calibração abaixo")
    st.info("💡 **Dica:** Os nomes das colunas podem ser alterados no Menu Lateral à esquerda.")
    df = st.data_editor(dados_iniciais, num_rows="dynamic", use_container_width=True, height=300)
    colunas_reais = df.columns.tolist()

# ---------------------------------------------------------
# BARRA LATERAL (MENU) - PARTE 2: Configurações do Gráfico
# ---------------------------------------------------------
st.sidebar.divider()
st.sidebar.header("⚙️ Configurações da Calibração")

coluna_x = st.sidebar.selectbox("📍 Eixo X (Referência/Concentração)", colunas_reais, index=0)

modo_grafico_qtd = st.sidebar.radio("Modo de Análise", ["Uma Única Curva", "Múltiplas Curvas"])

if modo_grafico_qtd == "Uma Única Curva":
    coluna_y = st.sidebar.selectbox("📍 Eixo Y (Sinal Analítico)", colunas_reais, index=1 if len(colunas_reais)>1 else 0)
    colunas_y = [coluna_y]
else:
    colunas_y = st.sidebar.multiselect("📍 Eixo Y (Curvas a comparar)", colunas_reais, default=colunas_reais[1:] if len(colunas_reais)>1 else colunas_reais)

st.sidebar.divider()
st.sidebar.subheader("🎨 Aparência do Gráfico")

# SELEÇÃO DE CORES PARA AS CURVAS
cores_escolhidas = {}
paleta_padrao = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2']

st.sidebar.markdown("**Cores das Curvas**")
for i, col in enumerate(colunas_y):
    cor_padrao = paleta_padrao[i % len(paleta_padrao)]
    cores_escolhidas[col] = st.sidebar.color_picker(f"Cor para '{col}'", cor_padrao)

tipo_grafico = st.sidebar.selectbox("Estilo do Gráfico", ["Dispersão (Pontos)", "Linha com Pontos", "Apenas Linha", "Barras"])

st.sidebar.markdown("**Personalizar Eixo X**")
nome_eixo_x = st.sidebar.text_input("Nome Eixo X no Gráfico", value=coluna_x)
unidade_x = st.sidebar.selectbox("Unidade Eixo X", ["Nenhuma", "mg/L", "mol/L", "ppm", "ppb", "Å (Angstrom)", "nm", "cm"])

st.sidebar.markdown("**Personalizar Eixo Y**")
nome_eixo_y = st.sidebar.text_input("Nome Eixo Y no Gráfico", value="Sinal Analítico")
unidade_y = st.sidebar.selectbox("Unidade Eixo Y", ["Nenhuma", "u.a.", "Abs", "mV", "%", "cps"])

st.sidebar.divider()
st.sidebar.subheader("📈 Matemática da Calibração")
incluir_tendencia = st.sidebar.toggle("Ativar Linha de Tendência", value=True)
mostrar_equacao = st.sidebar.checkbox("Mostrar Equação/R² no Gráfico", value=True)

# Opção para modo Automático ou Manual
modo_equacao = "Automático"
coeficientes_manuais = {}

if incluir_tendencia:
    modo_equacao = st.sidebar.radio("Modo da Equação da Reta", ["Automático (Regressão)", "Manual (Inserir valores)"])
    
    if modo_equacao == "Manual (Inserir valores)":
        st.sidebar.markdown("**Defina y = ax + b**")
        for col in colunas_y:
            st.sidebar.markdown(f"**{col}**")
            col1, col2 = st.sidebar.columns(2)
            with col1:
                a_man = st.number_input(f"a (Inclinação)", value=1.0000, format="%.4f", key=f"a_{col}")
            with col2:
                b_man = st.number_input(f"b (Intersecção)", value=0.0000, format="%.4f", key=f"b_{col}")
            coeficientes_manuais[col] = {'a': a_man, 'b': b_man}

equacoes = {}

with tab2:
    st.subheader("Gráfico da Curva de Calibração")

    # Botão para gerar o gráfico
    if st.button("🚀 Gerar / Atualizar Gráfico", type="primary", use_container_width=True):
        st.session_state['grafico_gerado'] = True

    if not st.session_state['grafico_gerado']:
        st.info("👆 Preencha seus dados na aba 'Meus Dados' e configure as opções ao lado. Depois clique no botão acima para visualizar o gráfico.")
    else:
        fig, ax = plt.subplots(figsize=(8, 5)) # Tamanho reajustado

        colunas_y_validas = [col for col in colunas_y if col in colunas_reais]

        if not colunas_y_validas:
            st.warning("⚠️ Por favor, selecione colunas válidas no Menu Lateral.")
        else:
            label_x = f"{nome_eixo_x} ({unidade_x})" if unidade_x != "Nenhuma" else nome_eixo_x
            label_y = f"{nome_eixo_y} ({unidade_y})" if unidade_y != "Nenhuma" else nome_eixo_y

            text_lines = []
            max_y_value = 0 # Para calcular o limite superior do eixo Y

            for col_y in colunas_y_validas:
                cor = cores_escolhidas.get(col_y, '#000000') # Pega a cor escolhida pelo usuário
                df_clean = df.dropna(subset=[coluna_x, col_y])
                x = df_clean[coluna_x].astype(float)
                y = df_clean[col_y].astype(float)

                if len(y) > 0 and max(y) > max_y_value:
                    max_y_value = max(y)

                if tipo_grafico == "Linha com Pontos":
                    ax.plot(x, y, marker='o', color=cor, linestyle='-', alpha=0.6, label=f'{col_y} (Dados)')
                elif tipo_grafico == "Apenas Linha":
                    ax.plot(x, y, color=cor, linestyle='-', linewidth=2, alpha=0.7, label=f'{col_y} (Dados)')
                elif tipo_grafico == "Barras":
                    ax.bar(x, y, color=cor, alpha=0.5, label=f'{col_y} (Dados)', width=(max(x)-min(x))/(len(x)*2) if len(x)>1 else 1)
                else:
                    ax.scatter(x, y, color=cor, marker='o', s=60, alpha=0.7, label=f'{col_y} (Dados)')

                if incluir_tendencia and len(x) > 1:
                    if modo_equacao == "Automático (Regressão)":
                        coef = np.polyfit(x, y, 1)
                        coef_a, coef_b = coef[0], coef[1]
                    else:
                        coef_a = coeficientes_manuais[col_y]['a']
                        coef_b = coeficientes_manuais[col_y]['b']

                    poly1d_fn = np.poly1d([coef_a, coef_b])
                    yhat = poly1d_fn(x)
                    ybar = np.sum(y) / len(y)
                    ssreg = np.sum((yhat - ybar)**2)
                    sstot = np.sum((y - ybar)**2)
                    r_squared = ssreg / sstot if sstot != 0 else 0
                    
                    equacoes[col_y] = {'a': coef_a, 'b': coef_b, 'r2': r_squared}
                    
                    # Gera pontos X suficientes para traçar a reta bonita
                    x_plot = np.linspace(min(x), max(x), 100)
                    ax.plot(x_plot, poly1d_fn(x_plot), color=cor, linestyle='--', linewidth=2, label=f'{col_y} (Tendência)')

                    if mostrar_equacao:
                        sinal = "+" if coef_b >= 0 else "-"
                        text_lines.append(f"{col_y} ➔ y = {coef_a:.4f}x {sinal} {abs(coef_b):.4f}  |  R² = {r_squared:.4f}")

            # Adicionar as equações destacadas em uma caixa de texto elaborada no gráfico
            if mostrar_equacao and text_lines:
                text_str = '\n'.join(text_lines)
                props = dict(boxstyle='round,pad=0.8', facecolor='#f8f9fa', alpha=0.9, edgecolor='#ced4da', linewidth=1.5)
                # Usando coordenadas relativas para sempre ficar no topo esquerdo (0.05, 0.95)
                ax.text(0.03, 0.97, text_str, transform=ax.transAxes, fontsize=11, fontweight='500',
                        verticalalignment='top', bbox=props, color='#212529')

            ax.set_xlim(0, 10) # Limite fixo de 0 a 10 no Eixo X
            ax.set_ylim(bottom=0, top=max_y_value * 1.35 if max_y_value > 0 else 1) # Espaço extra de 35% no topo para não bater na caixa de texto

            ax.set_xlabel(label_x, fontsize=12, fontweight='bold')
            ax.set_ylabel(label_y, fontsize=12, fontweight='bold')
            ax.grid(True, linestyle='--', alpha=0.6)
            ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left', frameon=True, fontsize=10)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)

            st.pyplot(fig)

            buf = io.BytesIO()
            fig.savefig(buf, format="png", dpi=300, bbox_inches="tight")
            buf.seek(0)
            st.download_button("📥 Baixar Gráfico Profissional em PNG", data=buf, file_name="curva_de_calibracao.png", mime="image/png", type="primary")

with tab3:
    if st.session_state['grafico_gerado'] and incluir_tendencia and equacoes:
        st.subheader("📊 Parâmetros da Calibração Obtidos")
        cols_eq = st.columns(len(equacoes))
        for idx, (nome, eq) in enumerate(equacoes.items()):
            with cols_eq[idx]:
                st.info(f"**{nome}**")
                st.latex(f"y = {eq['a']:.4f}x {'+' if eq['b'] >= 0 else ''} {eq['b']:.4f}")
                st.latex(f"R^2 = {eq['r2']:.5f}")

        st.divider()
        st.subheader("🧪 Interpolação de Amostras")
        st.write("Calcule a concentração (Eixo X) de uma amostra desconhecida a partir do sinal medido (Eixo Y).")

        col_calc1, col_calc2 = st.columns(2)
        with col_calc1:
            curva_escolhida = st.selectbox("Qual curva de calibração deseja utilizar?", list(equacoes.keys()))
            y_amostra = st.number_input("Sinal Medido (Y):", format="%.4f")

        with col_calc2:
            st.write(" ")
            st.write(" ")
            if st.button("Calcular Concentração", type="primary", use_container_width=True):
                eq_ref = equacoes[curva_escolhida]
                if eq_ref['a'] != 0:
                    x_calc = (y_amostra - eq_ref['b']) / eq_ref['a']
                    st.success(f"### Concentração Calculada: **{x_calc:.4f}**")
                else:
                    st.error("Erro: A inclinação da reta é zero.")
    else:
        st.warning("⚠️ Para ver os resultados, primeiro gere o gráfico na aba 'Gráfico Visual' com a **Linha de Tendência** ativada.")
