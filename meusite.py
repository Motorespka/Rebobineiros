import streamlit as st
import pandas as pd
import os
import hashlib
from PIL import Image

# --- 1. CONFIGURAÇÕES ---
ARQUIVO_USUARIOS = 'usuarios.csv'
ARQUIVO_CSV = 'meubancodedados.csv'
LINK_SHEETS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTFbH81UYKGJ6dQvKotxdv4hDxecLmiGUPHN46iexbw8NeS8_e2XdyZnZ8WJnL2XRTLCbFDbBKo_NGE/pub?output=csv"
CHAVE_MESTRA_CHEFIA = "PABLO2026" # Chave para validar quem é Chefia

# --- 2. FUNÇÕES DE SEGURANÇA ---
def hash_senha(senha):
    return hashlib.sha256(str.encode(senha)).hexdigest()

def salvar_usuario(usuario, senha, funcoes, perfil):
    df = pd.read_csv(ARQUIVO_USUARIOS) if os.path.exists(ARQUIVO_USUARIOS) else pd.DataFrame(columns=['usuario', 'senha', 'funcoes', 'perfil'])
    if usuario.lower() in df['usuario'].str.lower().values:
        return False
    novo_u = pd.DataFrame([{'usuario': usuario.lower(), 'senha': hash_senha(senha), 'funcoes': ",".join(funcoes), 'perfil': perfil}])
    novo_u.to_csv(ARQUIVO_USUARIOS, mode='a', header=not os.path.exists(ARQUIVO_USUARIOS), index=False)
    return True

def validar_login(usuario, senha):
    if not os.path.exists(ARQUIVO_USUARIOS): return False
    df = pd.read_csv(ARQUIVO_USUARIOS)
    senha_h = hash_senha(senha)
    u_check = df[(df['usuario'] == usuario.lower()) & (df['senha'] == senha_h)]
    if not u_check.empty:
        return u_check.iloc[0].to_dict()
    return False

# --- 3. INTERFACE DE ENTRADA ---
st.set_page_config(page_title="Pablo União", layout="centered", page_icon="⚙️")

if 'user_data' not in st.session_state:
    st.session_state['user_data'] = None

if not st.session_state['user_data']:
    st.markdown("<h1 style='text-align: center; color: #f1c40f;'>🛠️ PABLO UNIÃO</h1>", unsafe_allow_html=True)
    
    t_login, t_cad = st.tabs(["🔐 ACESSAR", "📝 CADASTRAR-SE"])
    
    with t_login:
        u = st.text_input("Usuário", key="login_u")
        s = st.text_input("Senha", type="password", key="login_s")
        if st.button("ENTRAR 🚀", use_container_width=True):
            dados = validar_login(u, s)
            if dados:
                st.session_state['user_data'] = dados
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos.")

    with t_cad:
        new_u = st.text_input("Novo Usuário")
        new_s = st.text_input("Nova Senha", type="password")
        
        st.markdown("---")
        st.subheader("📋 Suas Funções")
        f_mec = st.checkbox("Mecânica")
        f_reb = st.checkbox("Rebobinagem")
        f_che = st.checkbox("Chefia (Admin)")
        
        perfil_final = "mecanico"
        chave_validacao = ""
        
        if f_che:
            chave_validacao = st.text_input("Chave de Liberação Chefia", type="password")
            perfil_final = "admin"
        
        if st.button("FINALIZAR CADASTRO ✅", use_container_width=True):
            funcoes_list = []
            if f_mec: funcoes_list.append("mecanica")
            if f_reb: funcoes_list.append("rebobinagem")
            if f_che: funcoes_list.append("chefia")
            
            if not funcoes_list:
                st.warning("Selecione pelo menos uma função.")
            elif f_che and chave_validacao != CHAVE_MESTRA_CHEFIA:
                st.error("Chave de Chefia inválida!")
            elif new_u and new_s:
                if salvar_usuario(new_u, new_s, funcoes_list, perfil_final):
                    st.success("Cadastro realizado! Faça login.")
                else:
                    st.error("Usuário já existe.")
    st.stop()

# --- 4. ÁREA LOGADA (PABLO UNIÃO) ---
user = st.session_state['user_data']
funcoes_usuario = user['funcoes'].split(",")

st.sidebar.title("🛠️ PABLO UNIÃO")
st.sidebar.write(f"👤 Usuário: **{user['usuario'].upper()}**")
if st.sidebar.button("Sair"):
    st.session_state['user_data'] = None
    st.rerun()

# --- DEFINIÇÃO DINÂMICA DE ABAS ---
abas_disponiveis = []
if "mecanica" in funcoes_usuario or user['perfil'] == "admin":
    abas_disponiveis.append("🔧 MECÂNICA")
if "rebobinagem" in funcoes_usuario or user['perfil'] == "admin":
    abas_disponiveis.append("⚡ REBOBINAGEM")
if user['perfil'] == "admin":
    abas_disponiveis.append("📊 ADMINISTRAÇÃO")

tabs = st.tabs(abas_disponiveis)

# Lógica para cada aba
for i, nome_tab in enumerate(abas_disponiveis):
    with tabs[i]:
        if "MECÂNICA" in nome_tab:
            st.header("Ferramentas de Mecânica")
            st.info("Acesso a rolamentos, eixos e orçamentos mecânicos.")
            # Aqui entra o seu formulário de mecânica
            
        if "REBOBINAGEM" in nome_tab:
            st.header("Dados de Rebobinagem")
            st.write("Consulta de Fios, Esquemas e Simulador AWG.")
            # Aqui entra a consulta de motores e simulador
            
        if "ADMINISTRAÇÃO" in nome_tab:
            st.header("Painel da Chefia")
            st.warning("Acesso restrito: Gestão de usuários e banco de dados completo.")
