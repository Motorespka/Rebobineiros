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
st.sidebar.markdown("<h2 style='color: #f1c40f;'>🔐 Acesso Admin</h2>", unsafe_allow_html=True)
senha_admin = st.sidebar.text_input("Senha", type="password")
e_admin = (senha_admin == "pablo123")

# --- ESTILO CSS PARA COMPACTAR O LAYOUT E CLAREAR TEXTO ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    
    /* Forçar cores claras em todos os textos */
    h1, h2, h3, p, span, li, label, div {
        color: #FFFFFF !important;
    }
    
    /* Destaque em Amarelo */
    strong, b { color: #f1c40f !important; }

    /* Compactar os Expanders (Cards de Motor) */
    .streamlit-expanderHeader {
        background-color: #1e2130 !important;
        color: #f1c40f !important;
        border: 1px solid #34495e !important;
        padding: 0.5rem 1rem !important;
    }

    /* Reduzir o espaçamento entre colunas e linhas */
    [data-testid="stVerticalBlock"] {
        gap: 0.5rem !important;
    }
    
    /* Estilo para as caixas de texto (Inputs) ficarem legíveis */
    input { 
        background-color: #ffffff !important; 
        color: #000000 !important; 
        height: 35px !important;
    }

    /* Caixa de Ligação compacta */
    .caixa-ligacao {
        background-color: #f1c40f;
        color: #000000 !important;
        padding: 5px 10px;
        border-radius: 5px;
        font-weight: bold;
        display: inline-block;
        margin-top: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #f1c40f; margin-bottom: 0;'>⚙️ PABLO MOTORES</h1>", unsafe_allow_html=True)

# --- NAVEGAÇÃO ---
if e_admin:
    abas = ["🔍 CONSULTA", "➕ NOVO CADASTRO", "🖼️ ESQUEMAS"]
else:
    abas = ["🔍 CONSULTA"]
tabs = st.tabs(abas)

# --- ABA 1: CONSULTA (MAIS COMPACTA) ---
with tabs[0]:
    # Centralizar a busca para não ficar espalhada
    _, col_busca, _ = st.columns([1, 2, 1])
    with col_busca:
        busca = st.text_input("🔍 Buscar por Marca ou CV...")
    
    if os.path.exists(ARQUIVO_CSV):
        # Carrega dados e limpa os 'None/nan'
        df = pd.read_csv(ARQUIVO_CSV, sep=';', encoding='utf-8-sig').fillna("---")
        df = df.replace("None", "---")
        
        df_filtrado = df[df.astype(str).apply(lambda x: busca.lower() in x.str.lower().any(), axis=1)] if busca else df

        # Container centralizado para os resultados
        _, col_central, _ = st.columns([0.2, 5, 0.2])
        with col_central:
            for idx, row in df_filtrado.iterrows():
                with st.expander(f"📦 {row.get('Marca')} | {row.get('Potencia_CV')} CV | {row.get('RPM')} RPM"):
                    # Colunas mais próximas uma da outra
                    c1, c2, c3, c4 = st.columns([1.2, 1.5, 1.5, 1.2])
                    
                    with c1:
                        st.write("**DADOS GERAIS**")
                        st.write(f"Polos: {row.get('Polaridade')}")
                        st.write(f"Voltagem: {row.get('Voltagem')}")
                        st.write(f"Amperagem: {row.get('Amperagem')}")
                    
                    with c2:
                        st.write("**PRINCIPAL**")
                        st.write(f"🔢 {row.get('Bobina_Principal')}")
                        st.write(f"🧵 {row.get('Fio_Principal')}")
                    
                    with c3:
                        st.write("**AUXILIAR**")
                        st.write(f"🔢 {row.get('Bobina_Auxiliar')}")
                        st.write(f"🧵 {row.get('Fio_Auxiliar')}")
                    
                    with c4:
                        st.write("**EXTRAS**")
                        st.write(f"🔋 Cap: {row.get('Capacitor')}")
                        st.write(f"⚙️ Rol: {row.get('Rolamentos')}")
                        st.write(f"📐 {row.get('Eixo_X')} x {row.get('Eixo_Y')}")
                        st.markdown(f"<div class='caixa-ligacao'>🔗 {row.get('Esquema_Marcado')}</div>", unsafe_allow_html=True)
                    
                    if e_admin:
                        if st.button(f"🗑️ Apagar", key=f"del_{idx}"):
                            df.drop(idx).to_csv(ARQUIVO_CSV, index=False, sep=';', encoding='utf-8-sig')
                            st.rerun()

# --- ABA 2: CADASTRO ---
if e_admin:
    with tabs[1]:
        st.subheader("📝 Novo Cadastro")
        with st.form("form_pablo", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                marca = st.text_input("Marca")
                potencia = st.text_input("Potência (CV)")
                rpm = st.text_input("RPM")
                polos = st.selectbox("Polos", ["2", "4", "6", "8"])
                volt = st.text_input("Voltagem (Ex: 110/220)")
                amp = st.text_input("Amperagem")
            with col2:
                b_p = st.text_input("Bobina Principal (Grupo)")
                f_p = st.text_input("Fio Principal")
                b_a = st.text_input("Bobina Auxiliar (Grupo)")
                f_a = st.text_input("Fio Auxiliar")
                cap = st.text_input("Capacitor")
                rol = st.text_input("Rolamentos")
            with col3:
                ex = st.text_input("Eixo X")
                ey = st.text_input("Eixo Y")
                st.write("**Ligações:**")
                l1 = st.checkbox("Estrela (Y)")
                l2 = st.checkbox("Triângulo (Δ)")
                l3 = st.checkbox("Série")
                l4 = st.checkbox("Paralelo")

            if st.form_submit_button("💾 SALVAR DADOS"):
                ligs = [n for c, n in zip([l1, l2, l3, l4], ["Estrela", "Triângulo", "Série", "Paralelo"]) if c]
                novo = {
                    'Marca': marca, 'Potencia_CV': potencia, 'RPM': rpm, 'Polaridade': polos,
                    'Voltagem': volt, 'Amperagem': amp, 'Bobina_Principal': b_p, 'Fio_Principal': f_p,
                    'Bobina_Auxiliar': b_a, 'Fio_Auxiliar': f_a, 'Capacitor': cap, 'Rolamentos': rol,
                    'Eixo_X': ex, 'Eixo_Y': ey, 'Esquema_Marcado': "/".join(ligs) if ligs else "---"
                }
                pd.DataFrame([novo]).to_csv(ARQUIVO_CSV, mode='a', header=not os.path.exists(ARQUIVO_CSV), index=False, sep=';', encoding='utf-8-sig')
                st.success("Salvo com sucesso!")

# --- ABA 3: ESQUEMAS ---
if e_admin:
    with tabs[2]:
        st.subheader("🖼️ Galeria de Esquemas")
        up = st.file_uploader("Subir do Paint", type=['png', 'jpg'])
        if up:
            n = st.text_input("Nome do desenho")
            if st.button("Gravar Imagem"):
                Image.open(up).save(os.path.join(PASTA_ESQUEMAS, f"{n}.png"))
                st.rerun()
        
        fotos = [f for f in os.listdir(PASTA_ESQUEMAS) if f.endswith(('.png', '.jpg'))]
        if fotos:
            escolha = st.selectbox("Ver Esquema:", fotos)
            st.image(os.path.join(PASTA_ESQUEMAS, escolha), use_container_width=True)

st.markdown("<p style='text-align:center; color:#444; margin-top:50px;'>Pablo Motores © 2026</p>", unsafe_allow_html=True)
