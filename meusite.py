import streamlit as st
import pandas as pd
import os
from PIL import Image

# --- CONFIGURAÇÕES ---
ARQUIVO_CSV = 'meubancodedados.csv'
PASTA_ESQUEMAS = 'esquemas_fotos'
if not os.path.exists(PASTA_ESQUEMAS):
    os.makedirs(PASTA_ESQUEMAS)

st.set_page_config(page_title="Pablo Motores | Gestão Pro", layout="wide")

# --- LOGIN ADMIN ---
st.sidebar.title("🔐 Acesso Admin")
senha_admin = st.sidebar.text_input("Senha", type="password")
e_admin = (senha_admin == "pablo123") # Altere sua senha aqui

# --- ESTILO CSS PARA ACABAR COM LETRAS ESCURAS ---
st.markdown("""
    <style>
    /* Fundo e Texto Geral */
    .stApp { background-color: #0e1117; color: #FFFFFF !important; }
    
    /* Forçar todos os textos de labels e spans a serem brancos/amarelos */
    label, p, span, .stMarkdown, .stText {
        color: #FFFFFF !important;
        font-weight: 500 !important;
    }
    
    /* Títulos dos campos de entrada */
    .stTextInput label, .stSelectbox label {
        color: #f1c40f !important; /* Amarelo para destacar */
        font-size: 1.1rem !important;
    }

    /* Estilo do Card do Motor na Consulta */
    .motor-info-card {
        background-color: #1e2130;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #34495e;
        margin-bottom: 10px;
    }
    
    /* Deixar o fundo dos inputs branco para leitura fácil */
    input { background-color: #ffffff !important; color: #000000 !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("⚙️ PABLO MOTORES - SISTEMA TÉCNICO")

# --- ABAS ---
if e_admin:
    abas = ["🔍 CONSULTA RÁPIDA", "➕ NOVO CADASTRO", "🖼️ ESQUEMAS (ADMIN)"]
else:
    abas = ["🔍 CONSULTA RÁPIDA"]
tabs = st.tabs(abas)

# --- ABA 1: CONSULTA ---
with tabs[0]:
    busca = st.text_input("🔍 Digite a Marca ou CV para buscar...")
    if os.path.exists(ARQUIVO_CSV):
        df = pd.read_csv(ARQUIVO_CSV, sep=';', encoding='utf-8-sig')
        df_filtrado = df[df.astype(str).apply(lambda x: busca.lower() in x.str.lower().any(), axis=1)] if busca else df
        
        for idx, row in df_filtrado.iterrows():
            with st.expander(f"📦 {row.get('Marca', 'MOTOR')} | {row.get('Potencia_CV', '-')} CV"):
                # Layout dentro do expander
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"**RPM:** {row.get('RPM')}")
                    st.markdown(f"**Polos:** {row.get('Polaridade')}")
                    st.markdown(f"**Voltagem:** {row.get('Voltagem')}V")
                with col2:
                    st.markdown(f"**Fio Principal:** {row.get('Fio_Principal')}")
                    st.markdown(f"**Fio Auxiliar:** {row.get('Fio_Auxiliar')}")
                    st.markdown(f"**Capacitor:** {row.get('Capacitor')}")
                with col3:
                    st.markdown(f"**Eixo X:** {row.get('Eixo_X')}")
                    st.markdown(f"**Eixo Y:** {row.get('Eixo_Y')}")
                    st.success(f"🔗 Ligações: {row.get('Esquema_Marcado')}")

# --- ABA 2: CADASTRO (ADMIN) ---
if e_admin:
    with tabs[1]:
        st.subheader("📝 Cadastrar Dados do Motor")
        with st.form("cadastro_pablo"):
            c1, c2, c3 = st.columns(3)
            with c1:
                marca = st.text_input("Marca do Motor")
                potencia = st.text_input("Potência (CV)")
                polos = st.selectbox("Polos", [2, 4, 6, 8, 12])
            with c2:
                f_p = st.text_input("Fio Principal")
                f_a = st.text_input("Fio Auxiliar")
                rol = st.text_input("Rolamentos")
            with c3:
                ex = st.text_input("Eixo X")
                ey = st.text_input("Eixo Y")
                st.write("Marque as Ligações:")
                l_y = st.checkbox("Estrela (Y)")
                l_d = st.checkbox("Triângulo (Δ)")

            if st.form_submit_button("💾 SALVAR MOTOR"):
                ligs = []
                if l_y: ligs.append("Estrela")
                if l_d: ligs.append("Triângulo")
                
                novo = {'Marca': marca, 'Potencia_CV': potencia, 'Polaridade': polos, 
                        'Fio_Principal': f_p, 'Fio_Auxiliar': f_a, 'Eixo_X': ex, 'Eixo_Y': ey,
                        'Esquema_Marcado': ", ".join(ligs)}
                
                pd.DataFrame([novo]).to_csv(ARQUIVO_CSV, mode='a', header=not os.path.exists(ARQUIVO_CSV), index=False, sep=';')
                st.success("Salvo!")

    # --- ABA 3: ESQUEMAS COM ZOOM ---
    with tabs[2]:
        st.subheader("🖼️ Galeria de Esquemas (Zoom Disponível)")
        up = st.file_uploader("Subir foto do Paint", type=['png', 'jpg'])
        if up:
            nome = st.text_input("Nome do Esquema")
            if st.button("Gravar Foto"):
                Image.open(up).save(os.path.join(PASTA_ESQUEMAS, f"{nome}.png"))
                st.rerun()

        st.divider()
        fotos = [f for f in os.listdir(PASTA_ESQUEMAS) if f.endswith(('.png', '.jpg'))]
        if fotos:
            escolha = st.selectbox("Escolha o esquema para ver detalhes:", fotos)
            img_aberta = Image.open(os.path.join(PASTA_ESQUEMAS, escolha))
            
            # O Streamlit já permite clicar na imagem para expandir (zoom) nativamente
            st.image(img_aberta, caption="Clique na imagem para expandir (Zoom)", use_container_width=True)
