import streamlit as st
import pandas as pd
import os
import google.generativeai as genai
from PIL import Image

# --- CONFIGURAÇÃO DA IA (GEMINI) ---
CHAVE_API = "AIzaSyBcwcsk-wcOGIeHZAuEoGjx4LkNQA5CCF4"
genai.configure(api_key=CHAVE_API)
model = genai.GenerativeModel('gemini-1.5-flash')

# Configuração da página
st.set_page_config(page_title="Oficina Pablo - Motores", layout="wide")

# CSS para esconder a câmera em telas grandes (PCs) e melhorar o visual no celular
st.markdown("""
    <style>
    @media (min-width: 1024px) {
        .camera-off-pc { display: none; }
    }
    .stButton>button { width: 100%; }
    </style>
    """, unsafe_allow_html=True)

st.title("🔌 Consulta de Motores - Oficina Pablo")

# Variável para armazenar o que foi lido na foto
texto_da_foto = ""

# --- SEÇÃO ADICIONAR (BOTÃO) ---
st.markdown("---")

# No PC, mostramos um aviso. No celular, o botão funciona.
if st.button("➕ Adicionar / Ler Placa via Foto"):
    # Esta div ajuda o CSS a esconder o componente no PC
    st.markdown('<div class="camera-off-pc">', unsafe_allow_html=True)
    foto = st.camera_input("Tire foto da placa do motor")
    st.markdown('</div>', unsafe_allow_html=True)

    if foto:
        with st.spinner('O Gemini está lendo a placa...'):
            img = Image.open(foto)
            prompt = "Extraia apenas os dados principais desta placa de motor: Marca, CV e RPM. Seja direto e curto."
            response = model.generate_content([prompt, img])
            texto_da_foto = response.text
            st.success(f"Identificado: {texto_da_foto}")
    
    # Se o usuário estiver no PC, avisamos que a câmera foi bloqueada pelo sistema
    if st.session_state.get('viewport_width', 1100) > 1024:
         st.warning("Abertura de câmera bloqueada no Computador. Use o Celular para esta função.")

st.markdown("---")

# --- LÓGICA DE BUSCA E BANCO DE DADOS ---
ARQUIVO_CSV = 'meubancodedados.csv' 

if os.path.exists(ARQUIVO_CSV):
    try:
        # Lendo o CSV com o separador correto
        df = pd.read_csv(ARQUIVO_CSV, sep=';', encoding='utf-8-sig')
        
        # O campo de busca recebe o texto da foto se houver
        valor_busca = texto_da_foto if texto_da_foto else ""
        busca = st.text_input("🔍 Buscar por Marca, CV ou Fio", value=valor_busca)
        
        if busca:
            mask = df.astype(str).apply(lambda x: x.str.contains(busca, case=False, na=False)).any(axis=1)
            df_filtrado = df[mask]
        else:
            df_filtrado = df

        st.write(f"Exibindo **{len(df_filtrado)}** motores encontrados.")

        # Exibição em cards
        for index, row in df_filtrado.iterrows():
            titulo = f"📦 {row.get('Marca', 'S/M')} | {row.get('Motor_CV', 'N/A')} CV"
            with st.expander(titulo):
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.markdown("### 📋 Placa")
                    st.write(f"**RPM:** {row.get('RPM', 'N/A')}")
                    st.write(f"**Polos:** {row.get('Polos', 'N/A')}")
                with c2:
                    st.markdown("### 🛠️ Bobina Principal")
                    st.write(f"**Fio:** {row.get('Fio_Princ', 'N/A')}")
                    st.write(f"**Passo:** {row.get('Passo_Princ', 'N/A')}")
                with c3:
                    st.markdown("### ⚡ Bobina Auxiliar")
                    st.write(f"**Fio Aux:** {row.get('Fio_Aux', 'N/A')}")
                    st.write(f"**Capacitor:** {row.get('Capacitores', 'N/A')}")

    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
else:
    st.info("Aguardando o arquivo 'meubancodedados.csv' no GitHub...")
