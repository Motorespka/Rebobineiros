import streamlit as st
import pandas as pd
import os
import google.generativeai as genai
from PIL import Image
from datetime import datetime

# --- CONFIGURAÇÃO DA IA ---
CHAVE_API = "AIzaSyBcwcsk-wcOGIeHZAuEoGjx4LkNQA5CCF4"
genai.configure(api_key=CHAVE_API)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Pablo Motores | Gestão Pro", layout="wide")

# --- ESTILO CSS PROFISSIONAL ---
st.markdown("""
    <style>
    .stApp { background-color: #121212; color: #e0e0e0; }
    .main-header {
        background: linear-gradient(90deg, #1e1e1e 0%, #333333 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border-bottom: 4px solid #f1c40f;
        margin-bottom: 2rem;
        text-align: center;
    }
    .motor-card {
        background-color: #ffffff;
        color: #121212;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 8px solid #f1c40f;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #1e1e1e;
        border-radius: 5px;
        color: white;
        padding: 10px 20px;
    }
    @media (min-width: 1024px) { .camera-off-pc { display: none; } }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="main-header"><h1 style="color:#f1c40f; margin:0;">PABLO MOTORES</h1><p style="margin:0; color:#bbb;">Engenharia de Rebobinagem e Dados</p></div>', unsafe_allow_html=True)

# --- NAVEGAÇÃO POR ABAS ---
tab1, tab2, tab3 = st.tabs(["🔍 CONSULTA RÁPIDA", "➕ ADICIONAR CÁLCULO", "📚 ESQUEMAS"])

ARQUIVO_CSV = 'meubancodedados.csv'

# --- ABA 1: CONSULTA ---
with tab1:
    with st.expander("📸 Escanear com IA (Celular)"):
        st.markdown('<div class="camera-off-pc">', unsafe_allow_html=True)
        foto = st.camera_input("Focar na placa")
        st.markdown('</div>', unsafe_allow_html=True)
        if foto:
            img = Image.open(foto)
            response = model.generate_content(["Identifique Marca e CV da placa. Retorne apenas o texto principal.", img])
            st.session_state.busca_ia = response.text

    busca = st.text_input("Buscar motor no banco...", value=st.session_state.get('busca_ia', ""))
    
    if os.path.exists(ARQUIVO_CSV):
        df = pd.read_csv(ARQUIVO_CSV, sep=';', encoding='utf-8-sig')
        if busca:
            df_filtrado = df[df.astype(str).apply(lambda x: busca.lower() in x.str.lower().any(), axis=1)]
        else:
            df_filtrado = df

        for _, row in df_filtrado.iterrows():
            st.markdown(f"""
            <div class="motor-card">
                <h3 style="margin:0;">{row.get('Marca', 'MOTOR')} | {row.get('Motor_CV', '-')} CV</h3>
                <p style="color:#555; margin-bottom:10px;">RPM: {row.get('RPM', '-')} | Polos: {row.get('Polos', '-')}</p>
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 0.9rem;">
                    <div><b>🧵 Princ:</b> Fio {row.get('Fio_Princ', '-')} | Passo {row.get('Passo_Princ', '-')}</div>
                    <div><b>⚡ Aux:</b> Fio {row.get('Fio_Aux', '-')} | Cap: {row.get('Capacitores', '-')}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"VER LIGAÇÃO", key=f"btn_{row.name}"):
                st.info(f"Mostrando esquema de {row.get('Polos', '-')} polos...")

# --- ABA 2: ADICIONAR NOVO CÁLCULO ---
with tab2:
    st.subheader("📝 Cadastrar Novo Motor")
    st.write("Preencha os dados do motor que você acabou de cortar/calcular.")
    
    with st.form("form_adicionar", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            marca = st.text_input("Marca do Motor")
            cv = st.text_input("Potência (CV)")
            rpm = st.text_input("RPM")
            polos = st.selectbox("Polos", ["2", "4", "6", "8", "12"])
        with c2:
            fio_p = st.text_input("Fio Principal")
            passo_p = st.text_input("Passo Principal")
            fio_a = st.text_input("Fio Auxiliar")
            cap = st.text_input("Capacitor")
        
        obs = st.text_area("Observações Técnicas (Ex: Esquema de ligação especial)")
        
        enviar = st.form_submit_button("💾 SALVAR NO BANCO DE DADOS")
        
        if enviar:
            novo_dado = {
                'Marca': marca, 'Motor_CV': cv, 'RPM': rpm, 'Polos': polos,
                'Fio_Princ': fio_p, 'Passo_Princ': passo_p, 'Fio_Aux': fio_a, 'Capacitores': cap
            }
            
            # Lógica para salvar no CSV
            df_novo = pd.DataFrame([novo_dado])
            if os.path.exists(ARQUIVO_CSV):
                df_novo.to_csv(ARQUIVO_CSV, mode='a', header=False, index=False, sep=';', encoding='utf-8-sig')
            else:
                df_novo.to_csv(ARQUIVO_CSV, index=False, sep=';', encoding='utf-8-sig')
            
            st.success("✅ Motor cadastrado com sucesso e salvo no arquivo!")

# --- ABA 3: ESQUEMAS ---
with tab3:
    st.subheader("📚 Biblioteca de Esquemas")
    
    st.write("Em breve: Carregue suas fotos de ligações aqui.")

st.markdown("<br><p style='text-align:center; color:#555;'>Pablo Motores © 2026</p>", unsafe_allow_html=True)
