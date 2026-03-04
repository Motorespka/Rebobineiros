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

# --- ESTILO CSS PARA CONTRASTE MÁXIMO ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    
    /* Forçar Branco em Tudo */
    h1, h2, h3, p, span, li, label, .stMarkdown {
        color: #FFFFFF !important;
        text-shadow: 1px 1px 2px black;
    }
    
    /* Amarelo para Destaques */
    strong, b { color: #f1c40f !important; }
    
    /* Estilo do Expander (Caixa do Motor) */
    .streamlit-expanderHeader {
        background-color: #1e2130 !important;
        color: #f1c40f !important;
        border: 1px solid #34495e !important;
    }
    
    /* Inputs Brancos para leitura fácil */
    input { background-color: #ffffff !important; color: #000000 !important; }
    
    /* Ajuste para o texto dentro do expander não sumir */
    .st-expanderContent { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #f1c40f;'>⚙️ PABLO MOTORES</h1>", unsafe_allow_html=True)

# --- NAVEGAÇÃO ---
if e_admin:
    abas = ["🔍 CONSULTA RÁPIDA", "➕ NOVO CADASTRO", "🖼️ ESQUEMAS (ADMIN)"]
else:
    abas = ["🔍 CONSULTA RÁPIDA"]
tabs = st.tabs(abas)

# --- ABA 1: CONSULTA ---
with tabs[0]:
    busca = st.text_input("🔍 Procure por Marca, CV ou Modelo...")
    
    if os.path.exists(ARQUIVO_CSV):
        # Carrega o banco e limpa valores vazios
        df = pd.read_csv(ARQUIVO_CSV, sep=';', encoding='utf-8-sig').fillna("---")
        
        if busca:
            df_filtrado = df[df.astype(str).apply(lambda x: busca.lower() in x.str.lower().any(), axis=1)]
        else:
            df_filtrado = df

        for idx, row in df_filtrado.iterrows():
            with st.expander(f"📦 {row.get('Marca')} | {row.get('Potencia_CV')} CV"):
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.markdown(f"**RPM:** {row.get('RPM')}")
                    st.markdown(f"**Polos:** {row.get('Polaridade')}")
                    st.markdown(f"**Voltagem:** {row.get('Voltagem')}")
                    st.markdown(f"**Amperagem:** {row.get('Amperagem')}")
                with c2:
                    st.markdown(f"**Fio Principal:** {row.get('Fio_Principal')}")
                    st.markdown(f"**Fio Auxiliar:** {row.get('Fio_Auxiliar')}")
                    st.markdown(f"**Capacitor:** {row.get('Capacitor')}")
                    st.markdown(f"**Rolamentos:** {row.get('Rolamentos')}")
                with c3:
                    st.markdown(f"**Eixo X:** {row.get('Eixo_X')}")
                    st.markdown(f"**Eixo Y:** {row.get('Eixo_Y')}")
                    st.markdown(f"<div style='background: #f1c40f; color: black; padding: 5px; border-radius: 5px; font-weight: bold;'>🔗 LIGAÇÕES: {row.get('Esquema_Marcado')}</div>", unsafe_allow_html=True)
                
                if e_admin:
                    if st.button(f"🗑️ Excluir {idx}", key=f"del_{idx}"):
                        df.drop(idx).to_csv(ARQUIVO_CSV, index=False, sep=';', encoding='utf-8-sig')
                        st.rerun()

# --- ABA 2: CADASTRO (SÓ ADMIN) ---
if e_admin:
    with tabs[1]:
        st.subheader("📝 Cadastrar Dados do Motor")
        with st.form("cadastro_pablo", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                marca = st.text_input("Marca do Motor")
                potencia = st.text_input("Potência (CV)")
                rpm = st.text_input("RPM")
                polos = st.selectbox("Polaridade (Polos)", ["2", "4", "6", "8", "12"])
                amp = st.text_input("Amperagem (A)")
                volt = st.text_input("Voltagem (V)")
            with col2:
                f_p = st.text_input("Fio Principal")
                f_a = st.text_input("Fio Auxiliar")
                cap = st.text_input("Capacitor")
                rol = st.text_input("Rolamentos")
                b_p = st.text_input("Bobina Princ. (Espiras)")
                b_a = st.text_input("Bobina Aux. (Espiras)")
            with col3:
                ex = st.text_input("Tamanho Eixo X")
                ey = st.text_input("Tamanho Eixo Y")
                st.write("Marque as Ligações:")
                l1 = st.checkbox("Estrela (Y)")
                l2 = st.checkbox("Triângulo (Δ)")
                l3 = st.checkbox("Série")
                l4 = st.checkbox("Paralelo")

            if st.form_submit_button("💾 SALVAR DADOS NO BANCO"):
                ligs = []
                if l1: ligs.append("Estrela")
                if l2: ligs.append("Triângulo")
                if l3: ligs.append("Série")
                if l4: ligs.append("Paralelo")
                
                novo_dado = {
                    'Marca': marca, 'Potencia_CV': potencia, 'RPM': rpm, 'Polaridade': polos,
                    'Amperagem': amp, 'Voltagem': volt, 'Fio_Principal': f_p, 'Fio_Auxiliar': f_a,
                    'Capacitor': cap, 'Rolamentos': rol, 'Eixo_X': ex, 'Eixo_Y': ey,
                    'Esquema_Marcado': ", ".join(ligs) if ligs else "Nenhuma"
                }
                
                df_novo = pd.DataFrame([novo_dado])
                df_novo.to_csv(ARQUIVO_CSV, mode='a', header=not os.path.exists(ARQUIVO_CSV), index=False, sep=';', encoding='utf-8-sig')
                st.success("✅ Motor cadastrado com sucesso!")

    # --- ABA 3: ESQUEMAS (SÓ ADMIN) ---
    with tabs[2]:
        st.subheader("🖼️ Galeria de Esquemas (Zoom)")
        up = st.file_uploader("Upload do Paint", type=['png', 'jpg'])
        if up:
            nome_f = st.text_input("Nome do arquivo")
            if st.button("Salvar Foto"):
                Image.open(up).save(os.path.join(PASTA_ESQUEMAS, f"{nome_f}.png"))
                st.rerun()
        
        st.divider()
        fotos = [f for f in os.listdir(PASTA_ESQUEMAS) if f.endswith(('.png', '.jpg'))]
        if fotos:
            escolha = st.selectbox("Abrir desenho:", fotos)
            st.image(os.path.join(PASTA_ESQUEMAS, escolha), caption="Clique nas setas no canto da imagem para Zoom", use_container_width=True)

st.markdown("<br><p style='text-align:center; color:#555;'>Pablo Motores © 2026</p>", unsafe_allow_html=True)
