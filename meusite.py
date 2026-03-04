import streamlit as st
import pandas as pd
import os
from PIL import Image

# --- CONFIGURAÇÕES DE DIRETÓRIOS ---
ARQUIVO_CSV = 'meubancodedados.csv'
PASTA_ESQUEMAS = 'esquemas_fotos'
if not os.path.exists(PASTA_ESQUEMAS):
    os.makedirs(PASTA_ESQUEMAS)

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Pablo Motores | Gestão Pro", layout="wide")

# --- LOGIN DE ADMIN NO SIDEBAR ---
st.sidebar.title("🔐 Acesso Restrito")
senha_admin = st.sidebar.text_input("Senha do Admin", type="password")
# VOCÊ PODE MUDAR A SENHA ABAIXO
SENHA_CORRETA = "pablo123" 

e_admin = (senha_admin == SENHA_CORRETA)

# --- ESTILO CSS ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #1e272e 0%, #000000 100%); color: #ffffff; }
    .main-header { background: rgba(255, 255, 255, 0.05); padding: 1.5rem; border-radius: 15px; border-bottom: 4px solid #f1c40f; margin-bottom: 2rem; text-align: center; }
    label { color: #f1c40f !important; font-weight: bold !important; }
    .motor-card { background: #ffffff; color: #1a1a1a; padding: 1.5rem; border-radius: 15px; margin-bottom: 1rem; border-left: 10px solid #f1c40f; }
    .stTextInput>div>div>input { background-color: #ffffff !important; color: #000000 !important; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="main-header"><h1 style="color:#f1c40f; margin:0;">⚙️ PABLO MOTORES</h1></div>', unsafe_allow_html=True)

# --- NAVEGAÇÃO DINÂMICA ---
# Se for admin, mostra 3 abas. Se não for, mostra apenas a consulta.
if e_admin:
    abas = ["🔍 CONSULTA", "➕ NOVO CADASTRO", "🖼️ ESQUEMAS (ADMIN)"]
else:
    abas = ["🔍 CONSULTA"]

tabs = st.tabs(abas)

# --- ABA 1: CONSULTA (Sempre Visível) ---
with tabs[0]:
    busca = st.text_input("Filtrar motor...")
    if os.path.exists(ARQUIVO_CSV):
        df = pd.read_csv(ARQUIVO_CSV, sep=';', encoding='utf-8-sig')
        df_filtrado = df[df.astype(str).apply(lambda x: busca.lower() in x.str.lower().any(), axis=1)] if busca else df
        for _, row in df_filtrado.iterrows():
            st.markdown(f"""
            <div class="motor-card">
                <h2 style="margin:0;">{row.get('Marca', 'MOTOR')} - {row.get('Potencia_CV', '-')} CV</h2>
                <p><b>RPM:</b> {row.get('RPM', '-')} | <b>Polos:</b> {row.get('Polaridade', '-')} | <b>Ligação:</b> {row.get('Esquema_Marcado', 'N/A')}</p>
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 0.9rem;">
                    <div>🧵 <b>Fio Princ:</b> {row.get('Fio_Principal', '-')} | <b>Fio Aux:</b> {row.get('Fio_Auxiliar', '-')}</div>
                    <div>📐 <b>Eixo X:</b> {row.get('Eixo_X', '-')} | <b>Eixo Y:</b> {row.get('Eixo_Y', '-')}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# --- ABAS DE ADMIN (Só aparecem se a senha estiver correta) ---
if e_admin:
    # ABA 2: CADASTRO
    with tabs[1]:
        st.markdown("### 📝 Cadastro de Novo Motor")
        with st.form("form_cadastro"):
            c1, c2, c3 = st.columns(3)
            with c1:
                marca = st.text_input("Marca")
                potencia = st.text_input("Potência (CV)")
                rpm = st.text_input("RPM")
                polaridade = st.selectbox("Polos", ["2", "4", "6", "8"])
            with c2:
                f_p = st.text_input("Fio Principal")
                f_a = st.text_input("Fio Auxiliar")
                cap = st.text_input("Capacitor")
                rol = st.text_input("Rolamentos")
            with c3:
                e_x = st.text_input("Eixo X")
                e_y = st.text_input("Eixo Y")
                st.markdown("**Ligações:**")
                l1 = st.checkbox("Estrela (Y)")
                l2 = st.checkbox("Triângulo (Δ)")
                l3 = st.checkbox("Série")
                l4 = st.checkbox("Paralelo")

            if st.form_submit_button("💾 SALVAR"):
                # Lógica de salvar simplificada para o exemplo
                st.success("Motor salvo no banco de dados!")

    # ABA 3: ESQUEMAS
    with tabs[2]:
        st.markdown("### 🖼️ Sua Biblioteca Particular de Esquemas")
        up = st.file_uploader("Upload de Esquema (Paint)", type=['png', 'jpg'])
        if up:
            nome_foto = st.text_input("Nome do arquivo")
            if st.button("Confirmar Upload"):
                Image.open(up).save(os.path.join(PASTA_ESQUEMAS, f"{nome_foto}.png"))
                st.rerun()
        
        st.divider()
        fotos = [f for f in os.listdir(PASTA_ESQUEMAS) if f.endswith(('.png', '.jpg'))]
        if fotos:
            escolha = st.selectbox("Ver Esquema:", fotos)
            st.image(os.path.join(PASTA_ESQUEMAS, escolha), use_container_width=True)
else:
    st.sidebar.warning("Digite a senha para liberar o Cadastro e Esquemas.")

st.markdown("<br><p style='text-align:center; color:#555;'>Pablo Motores © 2026</p>", unsafe_allow_html=True)
