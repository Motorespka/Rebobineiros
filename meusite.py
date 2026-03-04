import streamlit as st
import pandas as pd
import os
from PIL import Image

# --- CONFIGURAÇÕES DE DIRETÓRIOS ---
ARQUIVO_CSV = 'meubancodedados.csv'
PASTA_ESQUEMAS = 'esquemas_fotos' # Onde você salvará as fotos "2.png", "4.png", etc.
if not os.path.exists(PASTA_ESQUEMAS):
    os.makedirs(PASTA_ESQUEMAS)

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Pablo Motores | Gestão Pro", layout="wide")

# --- LOGIN ADMIN ---
senha_admin = st.sidebar.text_input("Senha Admin", type="password")
e_admin = (senha_admin == "pablo123")

# --- ESTILO CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    h1, h2, h3, p, span, label { color: #FFFFFF !important; }
    strong, b { color: #f1c40f !important; }
    .streamlit-expanderHeader { background-color: #1e2130 !important; border: 1px solid #34495e !important; }
    input { background-color: #ffffff !important; color: #000000 !important; }
    .caixa-ligacao { background-color: #f1c40f; color: #000000 !important; padding: 5px; border-radius: 5px; font-weight: bold; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #f1c40f;'>⚙️ PABLO MOTORES</h1>", unsafe_allow_html=True)

# --- NAVEGAÇÃO ---
abas = ["🔍 CONSULTA", "➕ NOVO CADASTRO", "🖼️ ESQUEMAS"] if e_admin else ["🔍 CONSULTA"]
tabs = st.tabs(abas)

# --- ABA 1: CONSULTA (COM IMAGEM AUTOMÁTICA) ---
with tabs[0]:
    _, col_busca, _ = st.columns([1, 2, 1])
    with col_busca:
        busca = st.text_input("🔍 Buscar motor...")
    
    if os.path.exists(ARQUIVO_CSV):
        df = pd.read_csv(ARQUIVO_CSV, sep=';', encoding='utf-8-sig').fillna("---").replace("None", "---")
        df_filtrado = df[df.astype(str).apply(lambda x: busca.lower() in x.str.lower().any(), axis=1)] if busca else df

        for idx, row in df_filtrado.iterrows():
            with st.expander(f"📦 {row.get('Marca')} | {row.get('Potencia_CV')} CV | {row.get('RPM')} RPM"):
                # Ajuste de colunas para caber a imagem técnica no canto
                c1, c2, c3, c4, c5 = st.columns([1, 1.2, 1.2, 1, 1.5])
                
                with c1:
                    st.write("**DADOS**")
                    st.write(f"Polos: {row.get('Polaridade')}")
                    st.write(f"Volt: {row.get('Voltagem')}")
                    st.write(f"Amp: {row.get('Amperagem')}")
                
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
                    st.write(f"🔋 {row.get('Capacitor')}")
                    st.write(f"⚙️ {row.get('Rolamentos')}")
                    st.write(f"📐 {row.get('Eixo_X')}x{row.get('Eixo_Y')}")
                    st.markdown(f"<div class='caixa-ligacao'>🔗 {row.get('Esquema_Marcado')}</div>", unsafe_allow_html=True)

                with c5:
                    # --- LÓGICA DA IMAGEM AUTOMÁTICA ---
                    polos_valor = str(row.get('Polaridade')).strip()
                    caminho_foto = os.path.join(PASTA_ESQUEMAS, f"{polos_valor}.png")
                    
                    if os.path.exists(caminho_foto):
                        st.image(caminho_foto, caption=f"Esquema {polos_valor} Polos", use_container_width=True)
                    else:
                        st.caption("🖼️ Foto do esquema não cadastrada")

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
                polos = st.selectbox("Polaridade", ["2", "4", "6", "8", "12"])
                volt = st.text_input("Voltagem")
                amp = st.text_input("Amperagem")
            with col2:
                b_p = st.text_input("Bobina Principal")
                f_p = st.text_input("Fio Principal")
                b_a = st.text_input("Bobina Auxiliar")
                f_a = st.text_input("Fio Auxiliar")
                cap = st.text_input("Capacitor")
                rol = st.text_input("Rolamentos")
            with col3:
                ex = st.text_input("Eixo X")
                ey = st.text_input("Eixo Y")
                st.write("**Ligações:**")
                l1 = st.checkbox("Y")
                l2 = st.checkbox("Δ")
                l3 = st.checkbox("Série")
                l4 = st.checkbox("Paralelo")

            if st.form_submit_button("💾 SALVAR"):
                ligs = [n for c, n in zip([l1, l2, l3, l4], ["Y", "Δ", "Série", "Paralelo"]) if c]
                novo = {
                    'Marca': marca, 'Potencia_CV': potencia, 'RPM': rpm, 'Polaridade': polos,
                    'Voltagem': volt, 'Amperagem': amp, 'Bobina_Principal': b_p, 'Fio_Principal': f_p,
                    'Bobina_Auxiliar': b_a, 'Fio_Auxiliar': f_a, 'Capacitor': cap, 'Rolamentos': rol,
                    'Eixo_X': ex, 'Eixo_Y': ey, 'Esquema_Marcado': "/".join(ligs) if ligs else "---"
                }
                pd.DataFrame([novo]).to_csv(ARQUIVO_CSV, mode='a', header=not os.path.exists(ARQUIVO_CSV), index=False, sep=';', encoding='utf-8-sig')
                st.success("Salvo!")

# --- ABA 3: ESQUEMAS ---
if e_admin:
    with tabs[2]:
        st.subheader("🖼️ Galeria Técnica")
        st.info("Para o sistema mostrar a foto automática, salve o arquivo com o número de polos (Ex: 2, 4, 6)")
        up = st.file_uploader("Subir do Paint", type=['png', 'jpg'])
        n = st.text_input("Nome (ex: 2 para motor de 2 polos)")
        if st.button("Gravar") and up and n:
            Image.open(up).save(os.path.join(PASTA_ESQUEMAS, f"{n}.png"))
            st.rerun()
