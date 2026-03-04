import streamlit as st
import pandas as pd
import easyocr
import re
import os
from PIL import Image
import numpy as np

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Oficina Pablo - Motores", layout="wide")

# Carrega a IA apenas uma vez (para não travar o celular)
@st.cache_resource
def carregar_ia():
    return easyocr.Reader(['pt', 'en'], gpu=False)

reader = carregar_ia()

st.title("🔌 Oficina Pablo - Cadastro e Consulta")

# --- ABA DE NAVEGAÇÃO ---
aba1, aba2 = st.tabs(["📷 Cadastrar Novo", "🔍 Consultar Banco"])

with aba1:
    st.header("Novo Motor")
    foto = st.camera_input("Tire foto da placa ou do cálculo")

    if foto:
        with st.spinner('IA Analisando...'):
            # Converte a foto para texto
            img = Image.open(foto)
            img_array = np.array(img)
            resultado = reader.readtext(img_array, detail=0)
            texto_todo = " ".join(resultado).upper()

            # Lógica de extração rápida
            rpm_detectado = re.search(r'\b(\d{3,4})\b', texto_todo)
            fio_detectado = re.search(r'(?:FIO|AWG)\s*(\d{1,2})', texto_todo)

            st.success("Leitura feita! Ajuste os dados se necessário:")

            # Formulario para você alterar o que estiver errado
            with st.form("form_motor"):
                c1, c2 = st.columns(2)
                with c1:
                    marca = st.text_input("Marca", value="WEG" if "WEG" in texto_todo else "S/M")
                    cv = st.text_input("Potência (CV)")
                    rpm = st.text_input("RPM", value=rpm_detectado.group(1) if rpm_detectado else "")
                with c2:
                    fio = st.text_input("Fio (Bob. Principal)", value=fio_detectado.group(1) if fio_detectado else "")
                    passo = st.text_input("Passo Principal")
                    espiras = st.text_input("Espiras")

                if st.form_submit_button("💾 Salvar Motor"):
                    # Aqui você pode enviar para uma planilha Google ou apenas exibir
                    st.balloons()
                    st.info("Para salvar direto no banco de dados pelo celular, precisamos conectar com o Google Sheets!")

with aba2:
    ARQUIVO_CSV = 'meubancodedados.csv' 
    if os.path.exists(ARQUIVO_CSV):
        df = pd.read_csv(ARQUIVO_CSV, sep=';', encoding='utf-8-sig')
        busca = st.text_input("🔍 Buscar Motor")
        
        # Filtro de busca
        df_filtrado = df[df.astype(str).apply(lambda x: busca.lower() in x.str.lower().any(), axis=1)] if busca else df

        for index, row in df_filtrado.iterrows():
            titulo = f"📦 {row.get('Marca', 'S/M')} | {row.get('Motor_CV', 'N/A')} CV"
            with st.expander(titulo):
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.markdown("### 📋 Placa")
                    st.write(f"**RPM:** {row.get('RPM', 'N/A')}")
                    st.write(f"**Tensão:** {row.get('Tensao', 'N/A')}")
                with c2:
                    st.markdown("### 🛠️ Principal")
                    st.write(f"**Fio:** {row.get('Fio_Princ', 'N/A')}")
                    st.write(f"**Passo:** {row.get('Passo_Princ', 'N/A')}")
                with c3:
                    st.markdown("### ⚡ Auxiliar")
                    st.write(f"**Fio Aux:** {row.get('Fio_Aux', 'N/A')}")

    else:
        st.warning("Banco de dados não encontrado.")
