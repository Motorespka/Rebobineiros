import streamlit as st
import pandas as pd
import os
import random
import string
from datetime import datetime
from PIL import Image

# --- 1. CONFIGURAÇÕES INICIAIS ---
ARQUIVO_CSV = 'meubancodedados.csv'
LINK_SHEETS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTFbH81UYKGJ6dQvKotxdv4hDxecLmiGUPHN46iexbw8NeS8_e2XdyZnZ8WJnL2XRTLCbFDbBKo_NGE/pub?output=csv"
PASTA_ESQUEMAS = 'esquemas_fotos'

if not os.path.exists(PASTA_ESQUEMAS): os.makedirs(PASTA_ESQUEMAS)

st.set_page_config(page_title="Pablo Motores | Gestão Profissional", layout="wide")

# --- 2. SISTEMA DE LOGIN ---
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

def realizar_login():
    st.markdown("<h1 style='text-align: center;'>🔐 Acesso Restrito</h1>", unsafe_allow_html=True)
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            usuario = st.text_input("Usuário")
            senha = st.text_input("Senha", type="password")
            if st.button("Entrar", use_container_width=True):
                # Defina aqui seus usuários e senhas
                if usuario == "pablo" and senha == "pablo123":
                    st.session_state['autenticado'] = True
                    st.session_state['perfil'] = "admin"
                    st.rerun()
                elif usuario == "wesley" and senha == "oficina":
                    st.session_state['autenticado'] = True
                    st.session_state['perfil'] = "mecanico"
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos")

if not st.session_state['autenticado']:
    realizar_login()
    st.stop() # Interrompe o código aqui se não estiver logado

# --- 3. DADOS E FUNÇÕES (SÓ RODA SE LOGADO) ---
TABELA_AWG = {
    10: 5.26, 12: 3.31, 14: 2.08, 15: 1.65, 16: 1.31, 17: 1.04, 
    18: 0.823, 19: 0.653, 20: 0.518, 21: 0.410, 22: 0.326, 23: 0.258
}

if 'db_os' not in st.session_state: st.session_state['db_os'] = []
if 'token_grupo' not in st.session_state: st.session_state['token_grupo'] = None

@st.cache_data(ttl=60)
def carregar_dados():
    dfs = []
    try:
        df_nuvem = pd.read_csv(LINK_SHEETS, dtype=str)
        if not df_nuvem.empty: dfs.append(df_nuvem)
    except: pass
    if os.path.exists(ARQUIVO_CSV):
        try:
            df_local = pd.read_csv(ARQUIVO_CSV, sep=';', encoding='utf-8-sig', dtype=str)
            if not df_local.empty: dfs.append(df_local)
        except: pass
    return pd.concat(dfs, ignore_index=True).drop_duplicates() if dfs else pd.DataFrame()

# --- 4. BARRA LATERAL ---
with st.sidebar:
    st.title(f"Olá, {st.session_state['perfil'].capitalize()}!")
    if st.button("Sair / Logout"):
        st.session_state['autenticado'] = False
        st.rerun()
    
    st.divider()
    st.header("👥 CONEXÃO DE EQUIPE")
    if not st.session_state['token_grupo']:
        if st.button("Gerar Código de Grupo"):
            st.session_state['token_grupo'] = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            st.rerun()
    else:
        st.success(f"Grupo: {st.session_state['token_grupo']}")

# --- 5. INTERFACE DE ABAS ---
tab_consulta, tab_cadastro, tab_simulador = st.tabs(["🔍 CONSULTA", "➕ NOVO CADASTRO", "🧪 SIMULADOR"])

with tab_consulta:
    st.markdown("<h2 style='color: #f1c40f;'>⚙️ PABLO MOTORES - CONSULTA</h2>", unsafe_allow_html=True)
    df = carregar_dados()
    busca = st.text_input("🔍 Buscar no banco de dados...")
    
    if not df.empty:
        df_f = df[df.apply(lambda row: row.astype(str).str.contains(busca, case=False).any(), axis=1)] if busca else df
        for idx, row in df_f.iterrows():
            with st.expander(f"📦 {row.get('Marca')} | {row.get('Potencia_CV')} CV"):
                st.write(f"**Fio Principal:** {row.get('Fio_Principal')} | **Esquema:** {row.get('Esquema_Marcado')}")

with tab_cadastro:
    # Apenas Admin (Pablo) pode cadastrar novos motores
    if st.session_state['perfil'] == "admin":
        st.subheader("Cadastrar Novo Motor")
        with st.form("cadastro"):
            c1, c2 = st.columns(2)
            marca = c1.text_input("Marca")
            cv = c2.text_input("CV")
            if st.form_submit_button("Salvar Motor"):
                st.success("Dados salvos com sucesso!")
    else:
        st.warning("Apenas o Administrador pode realizar novos cadastros.")

with tab_simulador:
    st.subheader("🧪 Simulador AWG")
    fio = st.selectbox("Fio Original", list(TABELA_AWG.keys()))
    st.write(f"Área: {TABELA_AWG[fio]} mm²")
