import streamlit as st
import pandas as pd
import os
import hashlib
from PIL import Image

# --- 1. CONFIGURAÇÕES ---
ARQUIVO_USUARIOS = 'usuarios.csv'
ARQUIVO_CSV = 'meubancodedados.csv'
LINK_SHEETS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTFbH81UYKGJ6dQvKotxdv4hDxecLmiGUPHN46iexbw8NeS8_e2XdyZnZ8WJnL2XRTLCbFDbBKo_NGE/pub?output=csv"
PASTA_ESQUEMAS = 'esquemas_fotos'
CHAVE_MESTRA_CHEFIA = "PABLO2026"

if not os.path.exists(PASTA_ESQUEMAS): os.makedirs(PASTA_ESQUEMAS)

# --- 2. FUNÇÕES DE SEGURANÇA (VERSÃO CORRIGIDA) ---
def hash_senha(senha):
    return hashlib.sha256(str.encode(senha)).hexdigest()

def criar_csv_correto():
    """Força a criação do arquivo com o cabeçalho que o Pandas entende"""
    df = pd.DataFrame(columns=['usuario', 'senha', 'funcoes', 'perfil'])
    df.to_csv(ARQUIVO_USUARIOS, index=False, sep=';', encoding='utf-8-sig')
    return df

def salvar_usuario(usuario, senha, funcoes, perfil):
    # Se o arquivo não existir ou se estiver vazio/errado, recriamos
    if not os.path.exists(ARQUIVO_USUARIOS):
        df = criar_csv_correto()
    else:
        try:
            df = pd.read_csv(ARQUIVO_USUARIOS, sep=';', encoding='utf-8-sig')
            if 'usuario' not in df.columns:
                df = criar_csv_correto()
        except:
            df = criar_csv_correto()

    # Verifica se o nome de usuário já existe
    if usuario.lower() in df['usuario'].astype(str).str.lower().values:
        return False
    
    funcoes_str = "|".join(funcoes)
    novo_u = pd.DataFrame([{
        'usuario': usuario.lower(), 
        'senha': hash_senha(senha), 
        'funcoes': funcoes_str, 
        'perfil': perfil
    }])
    
    # Adiciona o novo usuário ao arquivo
    novo_u.to_csv(ARQUIVO_USUARIOS, mode='a', header=False, index=False, sep=';', encoding='utf-8-sig')
    return True

def validar_login(usuario, senha):
    if not os.path.exists(ARQUIVO_USUARIOS):
        return False
    try:
        df = pd.read_csv(ARQUIVO_USUARIOS, sep=';', encoding='utf-8-sig')
        senha_h = hash_senha(senha)
        u_check = df[(df['usuario'].astype(str).str.lower() == usuario.lower()) & (df['senha'] == senha_h)]
        if not u_check.empty:
            return u_check.iloc[0].to_dict()
    except:
        pass
    return False

# --- 3. INTERFACE DE ENTRADA ---
st.set_page_config(page_title="Pablo União", layout="wide", page_icon="⚙️")

if 'user_data' not in st.session_state:
    st.session_state['user_data'] = None

if not st.session_state['user_data']:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center; color: #f1c40f;'>🛠️ PABLO UNIÃO</h1>", unsafe_allow_html=True)
        tab_login, tab_cad = st.tabs(["🔐 ACESSAR", "📝 CADASTRAR-SE"])
        
        with tab_login:
            u = st.text_input("Usuário", key="login_u")
            s = st.text_input("Senha", type="password", key="login_s")
            if st.button("ENTRAR 🚀", use_container_width=True):
                dados = validar_login(u, s)
                if dados:
                    st.session_state['user_data'] = dados
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos.")

        with tab_cad:
            nu = st.text_input("Escolha um Usuário", key="cad_u")
            ns = st.text_input("Escolha uma Senha", type="password", key="cad_s")
            st.markdown("---")
            st.write("📂 **Suas áreas de atuação:**")
            fm = st.checkbox("Mecânica 🔧")
            fr = st.checkbox("Rebobinagem ⚡")
            fc = st.checkbox("Chefia / Admin 👑")
            
            chave = ""
            if fc:
                chave = st.text_input("Chave de Acesso Chefia", type="password")
            
            if st.button("FINALIZAR CADASTRO ✅", use_container_width=True):
                f_list = []
                if fm: f_list.append("mecanica")
                if fr: f_list.append("rebobinagem")
                if fc: f_list.append("chefia")
                
                if not f_list:
                    st.warning("Selecione pelo menos uma função.")
                elif fc and chave != CHAVE_MESTRA_CHEFIA:
                    st.error("Chave de Chefia incorreta!")
                elif nu and ns:
                    perf = "admin" if fc else "mecanico"
                    if salvar_usuario(nu, ns, f_list, perf):
                        st.success("Conta criada! Vá na aba ACESSAR.")
                    else:
                        st.error("Esse usuário já existe.")
    st.stop()

# --- 4. ÁREA DO SISTEMA (PÓS-LOGIN) ---
user = st.session_state['user_data']
funcoes_liberadas = str(user['funcoes']).split("|")

st.sidebar.title("🛠️ PABLO UNIÃO")
st.sidebar.write(f"👤 Olá, **{user['usuario'].upper()}**")
if st.sidebar.button("Sair"):
    st.session_state['user_data'] = None
    st.rerun()

# Criar abas baseadas no que o usuário marcou no cadastro
abas_visiveis = []
if "mecanica" in funcoes_liberadas or user['perfil'] == "admin":
    abas_visiveis.append("🔧 MECÂNICA")
if "rebobinagem" in funcoes_liberadas or user['perfil'] == "admin":
    abas_visiveis.append("⚡ REBOBINAGEM")
if user['perfil'] == "admin":
    abas_visiveis.append("📊 ADMINISTRAÇÃO")

if abas_visiveis:
    tabs = st.tabs(abas_visiveis)
    for i, nome_tab in enumerate(abas_visiveis):
        with tabs[i]:
            if "MECÂNICA" in nome_tab:
                st.subheader("Setor Mecânico")
                st.info("Aqui entrarão os dados de rolamentos e medidas de eixos.")
            if "REBOBINAGEM" in nome_tab:
                st.subheader("Setor de Rebobinagem")
                st.info("Aqui você acessa os esquemas e o simulador de fios.")
            if "ADMINISTRAÇÃO" in nome_tab:
                st.subheader("Painel da Chefia")
                st.warning("Acesso restrito para gestão de dados.")
