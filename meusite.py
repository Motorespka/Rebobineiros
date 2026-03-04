import streamlit as st
import pandas as pd
import os
import random
import string
import hashlib

# --- 1. CONFIGURAÇÕES E SEGURANÇA ---
ARQUIVO_USUARIOS = 'usuarios.csv'
ARQUIVO_CSV = 'meubancodedados.csv'
PASTA_ESQUEMAS = 'esquemas_fotos'

if not os.path.exists(PASTA_ESQUEMAS): os.makedirs(PASTA_ESQUEMAS)

def hash_senha(senha):
    return hashlib.sha256(str.encode(senha)).hexdigest()

def salvar_usuario(usuario, senha, perfil="mecanico"):
    df = pd.read_csv(ARQUIVO_USUARIOS) if os.path.exists(ARQUIVO_USUARIOS) else pd.DataFrame(columns=['usuario', 'senha', 'perfil'])
    if usuario in df['usuario'].values:
        return False
    novo_u = pd.DataFrame([{'usuario': usuario, 'senha': hash_senha(senha), 'perfil': perfil}])
    novo_u.to_csv(ARQUIVO_USUARIOS, mode='a', header=not os.path.exists(ARQUIVO_USUARIOS), index=False)
    return True

def validar_login(usuario, senha):
    if not os.path.exists(ARQUIVO_USUARIOS): return False
    df = pd.read_csv(ARQUIVO_USUARIOS)
    senha_h = hash_senha(senha)
    user_check = df[(df['usuario'] == usuario) & (df['senha'] == senha_h)]
    if not user_check.empty:
        return user_check.iloc[0]['perfil']
    return False

# --- 2. INTERFACE DE ENTRADA (PABLO UNIÃO) ---
st.set_page_config(page_title="Pablo União", layout="centered")

if 'autenticado' not in st
