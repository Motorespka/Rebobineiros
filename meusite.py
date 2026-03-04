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

# --- 2. FUNÇÕES DE SEGURANÇA E DADOS ---
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
