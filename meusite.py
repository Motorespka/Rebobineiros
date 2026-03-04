import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
from PIL import Image

# --- CONFIGURAÇÕES DE ARQUIVOS ---
ARQUIVO_CSV = 'meubancodedados.csv'
ARQUIVO_LIXEIRA = 'lixeira_motores.csv'
PASTA_ESQUEMAS = 'esquemas_fotos'

if not os.path.exists(PASTA_ESQUEMAS): os.makedirs(PASTA_ESQUEMAS)

st.set_page_config(page_title="Pablo Motores", layout="wide")

# --- FUNÇÃO PARA CARREGAR DADOS COM SEGURANÇA ---
def carregar_dados_seguro(caminho):
    if os.path.exists(caminho):
        try:
            temp_df = pd.read_csv(caminho, sep=';', encoding='utf-8-sig')
            # Lista de colunas que OBRIGATORIAMENTE devem existir
            colunas_necessarias = [
                'Marca', 'Potencia_CV', 'RPM', 'Polaridade', 'Voltagem', 
                'Amperagem', 'Fio_Principal', 'Bobina_Principal', 
                'Fio_Auxiliar', 'Bobina_Auxiliar', 'Eixo_X', 'Eixo_Y', 
                'Esquema_Marcado', 'Capacitor', 'Rolamentos'
            ]
            # Se faltar alguma coluna no arquivo, o código cria ela vazia agora:
            for col in colunas_necessarias:
                if col not in temp_df.columns:
                    temp_df[col] = "---"
            return temp_df.fillna("---").replace("None", "---")
        except Exception as e:
            st.error(f"Erro ao ler arquivo: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

# --- CSS (MANTIDO) ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    .titulo-secao { color: #f1c40f !important; font-size: 1.2rem !important; font-weight: bold; border-bottom: 2px solid #f1c40f; margin-bottom: 10px; }
    .label-fixo { color: #f1c40f !important; font-weight: bold; }
    .valor-fixo { color: #ffffff !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN E NAVEGAÇÃO ---
with st.sidebar:
    st.markdown("### 🔐 ACESSO")
    senha = st.text_input("Senha Admin", type="password")
    e_admin = (senha == "pablo123")
    
    opcoes = ["🔍 CONSULTA"]
    if e_admin:
        opcoes = ["🔍 CONSULTA", "➕ NOVO MOTOR", "🖼️ ADICIONAR ESQUEMA", "🗑️ LIXEIRA"]
    
    aba = st.radio("Menu:", opcoes)

df = carregar_dados_seguro(ARQUIVO_CSV)

# --- ABA 1: CONSULTA ---
if aba == "🔍 CONSULTA":
    busca = st.text_input("🔎 Pesquisar no Banco de Dados...")
    if not df.empty:
        df_f = df[df.astype(str).apply(lambda x: busca.lower() in x.str.lower().any(), axis=1)] if busca else df
        for idx, row in df_f.iterrows():
            # Use .get() para evitar o erro KeyError se a coluna sumir
            marca = row.get('Marca', 'S/M')
            cv = row.get('Potencia_CV', '---')
            rpm = row.get('RPM', '---')
            
            with st.expander(f"📦 {marca} | {cv} CV | {rpm} RPM"):
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    st.markdown('<div class="titulo-secao">📊 DADOS</div>', unsafe_allow_html=True)
                    st.write(f"**Polos:** {row.get('Polaridade')}")
                    st.write(f"**Volt:** {row.get('Voltagem')}")
                with c2:
                    st.markdown('<div class="titulo-secao">🌀 PRINCIPAL</div>', unsafe_allow_html=True)
                    st.write(f"**Fio:** {row.get('Fio_Principal')}")
                with c3:
                    st.markdown('<div class="titulo-secao">⚡ AUXILIAR</div>', unsafe_allow_html=True)
                    st.write(f"**Fio:** {row.get('Fio_Auxiliar')}")
                with c4:
                    st.markdown('<div class="titulo-secao">🔗 LIGAÇÃO</div>', unsafe_allow_html=True)
                    lig = row.get('Esquema_Marcado', '---')
                    st.info(lig)
                    # Mostrar Imagem
                    for ext in [".png", ".jpg"]:
                        p = os.path.join(PASTA_ESQUEMAS, f"{lig.strip()}{ext}")
                        if os.path.exists(p): st.image(p)

# --- ABA 2: NOVO MOTOR (RESTAURADA) ---
elif aba == "➕ NOVO MOTOR":
    st.markdown("### ➕ Cadastrar Motor")
    with st.form("cadastro"):
        m = st.text_input("Marca")
        p = st.text_input("Potencia_CV")
        r = st.text_input("RPM")
        e_marcado = st.text_input("Nome do Esquema (Ex: Estrela)")
        if st.form_submit_button("SALVAR"):
            novo = pd.DataFrame([{'Marca': m, 'Potencia_CV': p, 'RPM': r, 'Esquema_Marcado': e_marcado}])
            novo.to_csv(ARQUIVO_CSV, mode='a', header=not os.path.exists(ARQUIVO_CSV), index=False, sep=';', encoding='utf-8-sig')
            st.success("Salvo!")

# --- ABA 3: ADICIONAR ESQUEMA (RESTAURADA) ---
elif aba == "🖼️ ADICIONAR ESQUEMA":
    st.markdown("### 🖼️ Enviar Novo Esquema de Ligação")
    arquivo = st.file_uploader("Escolha a foto", type=['png', 'jpg'])
    nome_foto = st.text_input("Nome do Esquema (Igual ao que você digita no cadastro)")
    if st.button("Gravar Foto") and arquivo and nome_foto:
        img = Image.open(arquivo)
        img.save(os.path.join(PASTA_ESQUEMAS, f"{nome_foto}.png"))
        st.success(f"Esquema '{nome_foto}' adicionado!")

# --- ABA 4: LIXEIRA ---
elif aba == "🗑️ LIXEIRA":
    st.write("Acesso à lixeira...")
    # (Código da lixeira que enviamos antes)
