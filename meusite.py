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

# --- LOGIN ADMIN ---
senha_admin = st.sidebar.text_input("Senha Admin", type="password")
e_admin = (senha_admin == "pablo123")

# --- ESTILO CSS AVANÇADO PARA PC (LEITURA FÁCIL) ---
st.markdown("""
    <style>
    /* Fundo Escuro Profundo */
    .stApp { background-color: #0b0e14; }
    
    /* Forçar Texto Branco em Tudo com contraste máximo */
    h1, h2, h3, p, span, label, div {
        color: #FFFFFF !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Destaques em Amarelo Pablo */
    strong, b, .yellow-text { color: #f1c40f !important; font-size: 1.1rem; }

    /* Compactar o Expander para não espalhar no PC */
    .streamlit-expanderHeader {
        background-color: #1c202a !important;
        border: 2px solid #34495e !important;
        border-radius: 8px !important;
        padding: 10px !important;
    }

    /* Estilo de "Etiqueta" para os dados do motor */
    .motor-card {
        background-color: #161a24;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #f1c40f;
        margin-bottom: 10px;
    }

    /* Melhorar leitura dos inputs */
    input { 
        background-color: #ffffff !important; 
        color: #000000 !important; 
        font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #f1c40f;'>⚙️ PABLO MOTORES - SISTEMA DE GESTÃO</h1>", unsafe_allow_html=True)

# --- CARREGAR DADOS ---
if os.path.exists(ARQUIVO_CSV):
    df = pd.read_csv(ARQUIVO_CSV, sep=';', encoding='utf-8-sig').fillna("---").replace("None", "---")
else:
    df = pd.DataFrame()

# Esquemas disponíveis
opcoes_esquemas = [f.replace(".png", "").replace(".jpg", "") for f in os.listdir(PASTA_ESQUEMAS) if f.endswith(('.png', '.jpg'))]

# --- NAVEGAÇÃO ---
abas = ["🔍 CONSULTA", "➕ NOVO CADASTRO", "🖼️ ESQUEMAS"] if e_admin else ["🔍 CONSULTA"]
tabs = st.tabs(abas)

# --- ABA 1: CONSULTA (OTIMIZADA PARA PC) ---
with tabs[0]:
    # Limita a largura da busca no PC para não ficar esticado
    _, col_central_busca, _ = st.columns([1, 2, 1])
    with col_central_busca:
        busca = st.text_input("🔍 Digite Marca, CV ou Modelo...")

    if not df.empty:
        # Filtro de busca
        df_filtrado = df[df.astype(str).apply(lambda x: busca.lower() in x.str.lower().any(), axis=1)] if busca else df
        
        # Centraliza os resultados
        _, col_corpo, _ = st.columns([0.1, 5, 0.1])
        
        with col_corpo:
            for idx, row in df_filtrado.iterrows():
                with st.expander(f"📦 {row.get('Marca')} | {row.get('Potencia_CV')} CV | {row.get('RPM')} RPM"):
                    
                    # Grade compacta de 4 colunas para PC
                    c1, c2, c3, c4 = st.columns([1, 1, 1, 1.5])
                    
                    with c1:
                        st.markdown("<b class='yellow-text'>📊 TÉCNICO</b>", unsafe_allow_html=True)
                        st.write(f"Polos: {row.get('Polaridade')}")
                        st.write(f"Volt: {row.get('Voltagem')}")
                        st.write(f"Amp: {row.get('Amperagem')}")
                    
                    with c2:
                        st.markdown("<b class='yellow-text'>🌀 PRINCIPAL</b>", unsafe_allow_html=True)
                        st.write(f"Grupo: {row.get('Bobina_Principal')}")
                        st.write(f"Fio: {row.get('Fio_Principal')}")
                    
                    with c3:
                        st.markdown("<b class='yellow-text'>⚡ AUXILIAR</b>", unsafe_allow_html=True)
                        st.write(f"Grupo: {row.get('Bobina_Auxiliar')}")
                        st.write(f"Fio: {row.get('Fio_Auxiliar')}")
                    
                    with c4:
                        st.markdown("<b class='yellow-text'>🔗 LIGAÇÕES</b>", unsafe_allow_html=True)
                        ligs = str(row.get('Esquema_Marcado'))
                        st.markdown(f"<div style='background:#f1c40f; color:black; padding:5px; border-radius:5px; font-weight:bold; text-align:center;'>{ligs}</div>", unsafe_allow_html=True)
                        
                        # Mostrar as fotos das ligações lado a lado
                        lista_ligs = ligs.split(" / ")
                        imgs_cols = st.columns(len(lista_ligs) if len(lista_ligs) > 0 else 1)
                        for i, nome_lig in enumerate(lista_ligs):
                            path = os.path.join(PASTA_ESQUEMAS, f"{nome_lig}.png")
                            if os.path.exists(path):
                                imgs_cols[i].image(path, use_container_width=True)

                    # ÁREA DE ADMIN (EDIÇÃO/EXCLUSÃO)
                    if e_admin:
                        st.markdown("---")
                        ca1, ca2 = st.columns(2)
                        if ca1.button(f"🗑️ Excluir Motor", key=f"del_{idx}"):
                            df.drop(idx).to_csv(ARQUIVO_CSV, index=False, sep=';', encoding='utf-8-sig')
                            st.rerun()
                        
                        if ca2.checkbox(f"📝 Editar Dados", key=f"ed_{idx}"):
                            with st.form(f"f_ed_{idx}"):
                                fe1, fe2 = st.columns(2)
                                n_marca = fe1.text_input("Marca", value=row.get('Marca'))
                                n_fio = fe2.text_input("Fio Principal", value=row.get('Fio_Principal'))
                                if st.form_submit_button("Confirmar Alteração"):
                                    df.at[idx, 'Marca'] = n_marca
                                    df.at[idx, 'Fio_Principal'] = n_fio
                                    df.to_csv(ARQUIVO_CSV, index=False, sep=';', encoding='utf-8-sig')
                                    st.rerun()

# --- ABAS DE CADASTRO E ESQUEMAS SEGUEM A MESMA LÓGICA ANTERIOR ---
# (Omitidas aqui para focar no ajuste visual solicitado, mas mantidas no seu arquivo final)
