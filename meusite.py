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

# --- CSS DE ALTO CONTRASTE (PARA ENXERGAR TUDO) ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; }
    
    /* Força títulos e labels em Amarelo Vibrante */
    label, .stMarkdown h3, .stMarkdown b, p {
        color: #f1c40f !important;
        font-weight: 800 !important;
        font-size: 1.1rem !important;
    }

    /* Campos de entrada Brancos com Letra Preta */
    input, textarea, [data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #000000 !important;
        font-weight: bold !important;
        border: 2px solid #f1c40f !important;
    }

    /* Botões Amarelos com letra preta */
    .stButton>button {
        background-color: #f1c40f !important;
        color: #000000 !important;
        font-weight: 900 !important;
        border: 2px solid #ffffff !important;
    }

    /* Ajuste para as abas (Tabs) */
    button[data-baseweb="tab"] { color: #ffffff !important; }
    button[data-baseweb="tab"][aria-selected="true"] { color: #f1c40f !important; border-bottom-color: #f1c40f !important; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN ADMIN ---
with st.sidebar:
    st.markdown("### 🔐 PAINEL ADMIN")
    senha = st.text_input("Senha Admin", type="password")
    e_admin = (senha == "pablo123")

st.markdown("<h1 style='text-align: center; color: #f1c40f;'>⚙️ PABLO MOTORES</h1>", unsafe_allow_html=True)

# --- CARREGAR DADOS ---
if os.path.exists(ARQUIVO_CSV):
    df = pd.read_csv(ARQUIVO_CSV, sep=';', encoding='utf-8-sig').fillna("---").replace("None", "---")
else:
    df = pd.DataFrame()

opcoes_esquemas = [f.replace(".png", "").replace(".jpg", "") for f in os.listdir(PASTA_ESQUEMAS) if f.endswith(('.png', '.jpg'))]

# --- NAVEGAÇÃO ---
abas = ["🔍 CONSULTA", "➕ NOVO CADASTRO", "🖼️ ESQUEMAS"] if e_admin else ["🔍 CONSULTA"]
tabs = st.tabs(abas)

# --- ABA 1: CONSULTA (COM TODAS AS INFORMAÇÕES) ---
with tabs[0]:
    busca = st.text_input("🔎 Pesquisar por Marca ou Potência...")
    if not df.empty:
        df_f = df[df.astype(str).apply(lambda x: busca.lower() in x.str.lower().any(), axis=1)] if busca else df
        for idx, row in df_f.iterrows():
            with st.expander(f"📦 {row.get('Marca')} | {row.get('Potencia_CV')} CV | {row.get('RPM')} RPM"):
                # Layout em 4 colunas para caber tudo na mesma linha no PC
                c1, c2, c3, c4 = st.columns([1, 1, 1, 1.5])
                
                with c1:
                    st.markdown("### 📊 GERAL")
                    st.write(f"**Polos:** {row.get('Polaridade')}")
                    st.write(f"**Volt:** {row.get('Voltagem')}")
                    st.write(f"**Amp:** {row.get('Amperagem')}")
                    st.write(f"**Capacitor:** {row.get('Capacitor')}")

                with c2:
                    st.markdown("### 🌀 PRINCIPAL")
                    st.write(f"**Bobinas:** {row.get('Bobina_Principal')}")
                    st.write(f"**Fio:** {row.get('Fio_Principal')}")
                    st.write(f"**Rolam.:** {row.get('Rolamentos')}")

                with c3:
                    st.markdown("### ⚡ AUXILIAR")
                    st.write(f"**Bobinas:** {row.get('Bobina_Auxiliar')}")
                    st.write(f"**Fio:** {row.get('Fio_Auxiliar')}")
                    st.write(f"**Eixo:** {row.get('Eixo_X')} x {row.get('Eixo_Y')}")

                with c4:
                    st.markdown("### 🔗 LIGAÇÕES")
                    ligs = str(row.get('Esquema_Marcado'))
                    st.info(ligs)
                    # Mostrar fotos
                    lista_ligs = ligs.split(" / ")
                    imgs_cols = st.columns(len(lista_ligs) if len(lista_ligs) > 0 else 1)
                    for i, nome_lig in enumerate(lista_ligs):
                        path = os.path.join(PASTA_ESQUEMAS, f"{nome_lig}.png")
                        if os.path.exists(path):
                            imgs_cols[i].image(path, use_container_width=True)

# --- ABA 2: NOVO CADASTRO (TODOS OS CAMPOS DE VOLTA) ---
if e_admin:
    with tabs[1]:
        st.markdown("### ➕ NOVO CADASTRO TÉCNICO")
        with st.form("form_pablo", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("### 📝 INFORMAÇÕES")
                marca = st.text_input("Marca")
                cv = st.text_input("Potência (CV)")
                rpm = st.text_input("RPM")
                polos = st.selectbox("Polos", ["2", "4", "6", "8"])
                volt = st.text_input("Voltagem")
                amp = st.text_input("Amperagem")
            with col2:
                st.markdown("### 🧵 DADOS DOS FIOS")
                b_p = st.text_input("Bobina Principal")
                f_p = st.text_input("Fio Principal")
                b_a = st.text_input("Bobina Auxiliar")
                f_a = st.text_input("Fio Auxiliar")
                cap = st.text_input("Capacitor")
            with col3:
                st.markdown("### ⚙️ MECÂNICA E LIGAÇÃO")
                rol = st.text_input("Rolamentos")
                ex = st.text_input("Eixo X")
                ey = st.text_input("Eixo Y")
                st.write("**Marque as Ligações:**")
                checks = {opt: st.checkbox(opt, key=f"n_{opt}") for opt in opcoes_esquemas}

            if st.form_submit_button("💾 SALVAR MOTOR"):
                sel = [n for n, v in checks.items() if v]
                novo = {
                    'Marca': marca, 'Potencia_CV': cv, 'RPM': rpm, 'Polaridade': polos,
                    'Voltagem': volt, 'Amperagem': amp, 'Bobina_Principal': b_p, 'Fio_Principal': f_p,
                    'Bobina_Auxiliar': b_a, 'Fio_Auxiliar': f_a, 'Capacitor': cap, 
                    'Rolamentos': rol, 'Eixo_X': ex, 'Eixo_Y': ey, 
                    'Esquema_Marcado': " / ".join(sel) if sel else "---"
                }
                pd.DataFrame([novo]).to_csv(ARQUIVO_CSV, mode='a', header=not os.path.exists(ARQUIVO_CSV), index=False, sep=';', encoding='utf-8-sig')
                st.success("✅ Motor salvo com sucesso!")
                st.rerun()

# --- ABA 3: ESQUEMAS (RESTAURADA) ---
if e_admin:
    with tabs[2]:
        st.markdown("### 🖼️ GERENCIAR ESQUEMAS")
        up = st.file_uploader("Upload da Foto", type=['png', 'jpg'])
        n_esq = st.text_input("Nome (Ex: Estrela, 2 Polos)")
        if st.button("Gravar Nova Opção") and up and n_esq:
            Image.open(up).save(os.path.join(PASTA_ESQUEMAS, f"{n_esq}.png"))
            st.rerun()
