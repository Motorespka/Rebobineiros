import streamlit as st
import pandas as pd
import os
import random
import string
import hashlib
from PIL import Image

# --- 1. CONFIGURAÇÕES DE ARQUIVOS ---
ARQUIVO_USUARIOS = 'usuarios.csv'
ARQUIVO_CSV = 'meubancodedados.csv'
LINK_SHEETS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTFbH81UYKGJ6dQvKotxdv4hDxecLmiGUPHN46iexbw8NeS8_e2XdyZnZ8WJnL2XRTLCbFDbBKo_NGE/pub?output=csv"
PASTA_ESQUEMAS = 'esquemas_fotos'

if not os.path.exists(PASTA_ESQUEMAS): os.makedirs(PASTA_ESQUEMAS)

# Tabela de referência para o Simulador
TABELA_AWG = {
    10: 5.26, 11: 4.17, 12: 3.31, 13: 2.63, 14: 2.08, 15: 1.65, 16: 1.31,
    17: 1.04, 18: 0.823, 19: 0.653, 20: 0.518, 21: 0.410, 22: 0.326,
    23: 0.258, 24: 0.205, 25: 0.162, 26: 0.129
}

# --- 2. FUNÇÕES DE SEGURANÇA E DADOS ---
def hash_senha(senha):
    return hashlib.sha256(str.encode(senha)).hexdigest()

def salvar_usuario(usuario, senha, perfil="mecanico"):
    df = pd.read_csv(ARQUIVO_USUARIOS) if os.path.exists(ARQUIVO_USUARIOS) else pd.DataFrame(columns=['usuario', 'senha', 'perfil'])
    if usuario in df['usuario'].values:
        return False
    novo_u = pd.DataFrame([{'usuario': usuario.lower(), 'senha': hash_senha(senha), 'perfil': perfil}])
    novo_u.to_csv(ARQUIVO_USUARIOS, mode='a', header=not os.path.exists(ARQUIVO_USUARIOS), index=False)
    return True

def validar_login(usuario, senha):
    if not os.path.exists(ARQUIVO_USUARIOS): return False
    df = pd.read_csv(ARQUIVO_USUARIOS)
    senha_h = hash_senha(senha)
    user_check = df[(df['usuario'] == usuario.lower()) & (df['senha'] == senha_h)]
    if not user_check.empty:
        return user_check.iloc[0]['perfil']
    return False

@st.cache_data(ttl=60)
def carregar_dados_motores():
    dfs = []
    try:
        df_n = pd.read_csv(LINK_SHEETS, dtype=str)
        if not df_n.empty: dfs.append(df_n)
    except: pass
    if os.path.exists(ARQUIVO_CSV):
        try:
            df_l = pd.read_csv(ARQUIVO_CSV, sep=';', encoding='utf-8-sig', dtype=str)
            if not df_l.empty: dfs.append(df_l)
        except: pass
    return pd.concat(dfs, ignore_index=True).drop_duplicates() if dfs else pd.DataFrame()

# --- 3. INTERFACE DE ENTRADA (PABLO UNIÃO) ---
st.set_page_config(page_title="Pablo União", layout="wide")

if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

if not st.session_state['autenticado']:
    st.markdown("<h1 style='text-align: center; color: #f1c40f;'>🛠️ PABLO UNIÃO</h1>", unsafe_allow_html=True)
    
    col_login, col_espaco, col_cad = st.columns([2, 1, 2])
    
    with col_login:
        st.subheader("Entrar")
        u_login = st.text_input("Usuário", key="u_login")
        s_login = st.text_input("Senha", type="password", key="s_login")
        if st.button("Acessar Sistema", use_container_width=True):
            perfil = validar_login(u_login, s_login)
            if perfil:
                st.session_state['autenticado'] = True
                st.session_state['usuario'] = u_login
                st.session_state['perfil'] = perfil
                st.rerun()
            else:
                st.error("Usuário ou senha inválidos.")
                
    with col_cad:
        st.subheader("Criar Conta")
        u_novo = st.text_input("Novo Usuário")
        s_nova = st.text_input("Nova Senha", type="password")
        if st.button("Cadastrar Usuário", use_container_width=True):
            if u_novo and s_nova:
                if salvar_usuario(u_novo, s_nova):
                    st.success("Cadastro realizado! Agora faça o login.")
                else:
                    st.error("Usuário já existe.")
            else:
                st.warning("Preencha todos os campos.")
    st.stop()

# --- 4. ÁREA LOGADA (SISTEMA DE MOTORES) ---
with st.sidebar:
    st.markdown(f"### Bem-vindo, **{st.session_state['usuario'].upper()}**")
    st.caption(f"Perfil: {st.session_state['perfil']}")
    if st.button("Sair / Logout"):
        st.session_state['autenticado'] = False
        st.rerun()

tab_cons, tab_cad, tab_sim = st.tabs(["🔍 CONSULTA", "➕ NOVO MOTOR", "🧪 SIMULADOR AWG"])

# ABA CONSULTA
with tab_cons:
    st.subheader("Pesquisar no Banco de Dados")
    df_motores = carregar_dados_motores()
    busca = st.text_input("🔍 Digite Marca, CV ou Fio para buscar...")
    
    if not df_motores.empty:
        df_f = df_motores[df_motores.apply(lambda row: row.astype(str).str.contains(busca, case=False).any(), axis=1)] if busca else df_motores
        for idx, row in df_f.iterrows():
            with st.expander(f"📦 {row.get('Marca', 'S/M')} | {row.get('Potencia_CV', '0')} CV | {row.get('RPM', '0')} RPM"):
                c1, c2 = st.columns(2)
                c1.write(f"**Fio Principal:** {row.get('Fio_Principal')}")
                c1.write(f"**Fio Auxiliar:** {row.get('Fio_Auxiliar')}")
                c2.write(f"**Esquema:** {row.get('Esquema_Marcado')}")
                
                lig = str(row.get('Esquema_Marcado'))
                if lig != "None":
                    for n in lig.split(" / "):
                        for ext in [".png", ".jpg", ".jpeg"]:
                            p = os.path.join(PASTA_ESQUEMAS, f"{n.strip()}{ext}")
                            if os.path.exists(p): st.image(p, width=400)

# ABA NOVO MOTOR
with tab_cad:
    if st.session_state['usuario'].lower() == "pablo" or st.session_state['perfil'] == "admin":
        st.subheader("Cadastrar Novo Motor no Banco Local")
        with st.form("form_motor"):
            c1, c2 = st.columns(2)
            marca = c1.text_input("Marca")
            pot = c2.text_input("Potência (CV)")
            f_p = c1.text_input("Fio Principal")
            f_a = c2.text_input("Fio Auxiliar")
            esq = st.text_input("Nome do Esquema (conforme arquivo de imagem)")
            
            if st.form_submit_button("💾 Salvar Motor"):
                novo_motor = {'Marca': marca, 'Potencia_CV': pot, 'Fio_Principal': f_p, 'Fio_Auxiliar': f_a, 'Esquema_Marcado': esq}
                pd.DataFrame([novo_motor]).to_csv(ARQUIVO_CSV, mode='a', header=not os.path.exists(ARQUIVO_CSV), index=False, sep=';', encoding='utf-8-sig')
                st.success("Motor salvo com sucesso!")
                st.cache_data.clear()
    else:
        st.warning("Apenas o Administrador pode cadastrar motores.")

# ABA SIMULADOR
with tab_sim:
    st.subheader("🧪 Equivalência de Fios (AWG)")
    col1, col2 = st.columns(2)
    
    with col1:
        fio_orig = st.selectbox("Fio Original", list(TABELA_AWG.keys()))
        qtd_orig = st.number_input("Quantidade de fios originais", min_value=1, value=1)
        area_total = TABELA_AWG[fio_orig] * qtd_orig
        st.info(f"Área Total: **{area_total:.3f} mm²**")
        
    with col2:
        fio_sub = st.selectbox("Substituir por Fio", list(TABELA_AWG.keys()))
        qtd_necessaria = area_total / TABELA_AWG[fio_sub]
