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

# --- ESTILO CSS PARA MÁXIMA VISIBILIDADE EM TODOS OS BOTÕES ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    
    /* 1. TEXTOS E LABELS */
    label, p, span, h3 {
        color: #FFFFFF !important;
        font-weight: 800 !important;
        font-size: 1.1rem !important;
    }

    /* 2. CAMPOS DE DIGITAÇÃO (INPUTS) */
    input, textarea, [data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        font-weight: bold !important;
    }

    /* 3. TODOS OS BOTÕES (CLICAR) */
    .stButton>button {
        width: 100%;
        background-color: #f1c40f !important; /* Amarelo */
        color: #000000 !important; /* Letra Preta */
        font-weight: 900 !important;
        height: 45px !important;
        border: 2px solid #ffffff !important;
    }
    .stButton>button:hover {
        background-color: #ffffff !important;
        color: #000000 !important;
    }

    /* 4. QUADRADINHOS DE MARCAR (CHECKBOXES) */
    [data-testid="stCheckbox"] > label > div:first-child {
        background-color: #ffffff !important; /* Fundo branco no quadrado */
        border: 2px solid #f1c40f !important;
    }

    /* 5. ABAS (TABS) NO TOPO */
    button[data-baseweb="tab"] {
        background-color: #1c202a !important;
        color: #ffffff !important;
        border-radius: 5px 5px 0 0 !important;
        margin-right: 5px !important;
        padding: 10px 20px !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: #f1c40f !important;
        color: #000000 !important;
        font-weight: bold !important;
    }

    /* 6. BARRA LATERAL (SIDEBAR) */
    [data-testid="stSidebar"] { background-color: #161a24 !important; border-right: 2px solid #f1c40f; }
    
    /* 7. EXPANDERS (CARDS DOS MOTORES) */
    .streamlit-expanderHeader {
        background-color: #1c202a !important;
        color: #f1c40f !important;
        font-size: 1.2rem !important;
        border: 1px solid #34495e !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- BARRA LATERAL ---
with st.sidebar:
    st.markdown("### 🔐 ACESSO ADMIN")
    senha_admin = st.text_input("Senha para Liberar Painel", type="password")
    e_admin = (senha_admin == "pablo123")

st.markdown("<h1 style='text-align: center; color: #f1c40f;'>⚙️ PABLO MOTORES</h1>", unsafe_allow_html=True)

# --- CARREGAR DADOS ---
if os.path.exists(ARQUIVO_CSV):
    df = pd.read_csv(ARQUIVO_CSV, sep=';', encoding='utf-8-sig').fillna("---").replace("None", "---")
else:
    df = pd.DataFrame()

opcoes_esquemas = [f.replace(".png", "").replace(".jpg", "") for f in os.listdir(PASTA_ESQUEMAS) if f.endswith(('.png', '.jpg'))]

# --- NAVEGAÇÃO ---
abas_nomes = ["🔍 CONSULTA", "➕ NOVO CADASTRO", "🖼️ ESQUEMAS"] if e_admin else ["🔍 CONSULTA"]
tabs = st.tabs(abas_nomes)

# --- ABA 1: CONSULTA E EDIÇÃO ---
with tabs[0]:
    busca = st.text_input("🔍 Pesquisar no Banco de Dados...")
    df_f = df[df.astype(str).apply(lambda x: busca.lower() in x.str.lower().any(), axis=1)] if (not df.empty and busca) else df

    for idx, row in df_f.iterrows():
        with st.expander(f"📦 {row.get('Marca')} | {row.get('Potencia_CV')} CV | {row.get('RPM')} RPM"):
            c1, c2, c3 = st.columns(3)
            with c1:
                st.write(f"**Polos:** {row.get('Polaridade')}")
                st.write(f"**Volt:** {row.get('Voltagem')}")
                st.write(f"**Amp:** {row.get('Amperagem')}")
            with c2:
                st.markdown(f"**Principal:**\n\n{row.get('Bobina_Principal')}\n\n{row.get('Fio_Principal')}")
            with c3:
                st.markdown(f"**Auxiliar:**\n\n{row.get('Bobina_Auxiliar')}\n\n{row.get('Fio_Auxiliar')}")
            
            # Imagens
            ligs_lista = str(row.get('Esquema_Marcado')).split(" / ")
            img_cols = st.columns(4)
            for i, nome_lig in enumerate(ligs_lista):
                path = os.path.join(PASTA_ESQUEMAS, f"{nome_lig}.png")
                if os.path.exists(path):
                    img_cols[i % 4].image(path, caption=nome_lig, use_container_width=True)

            if e_admin:
                st.divider()
                if st.checkbox(f"📝 Abrir Painel de Edição para este motor", key=f"check_ed_{idx}"):
                    with st.form(f"form_ed_{idx}"):
                        st.write("### ✏️ Alterar Informações")
                        ce1, ce2, ce3 = st.columns(3)
                        with ce1:
                            m = st.text_input("Marca", value=row.get('Marca'))
                            p = st.text_input("CV", value=row.get('Potencia_CV'))
                            v = st.text_input("Voltagem", value=row.get('Voltagem'))
                        with ce2:
                            bp = st.text_input("Bobina Principal", value=row.get('Bobina_Principal'))
                            fp = st.text_input("Fio Principal", value=row.get('Fio_Principal'))
                        with ce3:
                            ba = st.text_input("Bobina Auxiliar", value=row.get('Bobina_Auxiliar'))
                            fa = st.text_input("Fio Auxiliar", value=row.get('Fio_Auxiliar'))
                        
                        st.write("**Ligações:**")
                        ed_ligs = {opt: st.checkbox(opt, value=(opt in str(row.get('Esquema_Marcado'))), key=f"e_{idx}_{opt}") for opt in opcoes_esquemas}
                        
                        if st.form_submit_button("💾 SALVAR ALTERAÇÕES"):
                            sel = [n for n, v in ed_ligs.items() if v]
                            df.at[idx, 'Marca'], df.at[idx, 'Potencia_CV'], df.at[idx, 'Voltagem'] = m, p, v
                            df.at[idx, 'Bobina_Principal'], df.at[idx, 'Fio_Principal'] = bp, fp
                            df.at[idx, 'Bobina_Auxiliar'], df.at[idx, 'Fio_Auxiliar'] = ba, fa
                            df.at[idx, 'Esquema_Marcado'] = " / ".join(sel) if sel else "---"
                            df.to_csv(ARQUIVO_CSV, index=False, sep=';', encoding='utf-8-sig')
                            st.rerun()
                
                if st.button(f"🗑️ EXCLUIR ESTE MOTOR", key=f"del_{idx}"):
                    df.drop(idx).to_csv(ARQUIVO_CSV, index=False, sep=';', encoding='utf-8-sig')
                    st.rerun()

# --- ABA 2: NOVO CADASTRO ---
if e_admin:
    with tabs[1]:
        st.write("### ➕ Cadastrar Novo Motor")
        with st.form("form_novo", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                marca = st.text_input("Marca")
                potencia = st.text_input("Potência (CV)")
                polos = st.selectbox("Polos", ["2", "4", "6", "8", "12"])
                volt = st.text_input("Voltagem (V)")
            with col2:
                b_p = st.text_input("Grupo Principal")
                f_p = st.text_input("Fio Principal")
                b_a = st.text_input("Grupo Auxiliar")
                f_a = st.text_input("Fio Auxiliar")
            with col3:
                st.write("**Ligações Técnicas:**")
                novas_ligs = {opt: st.checkbox(opt, key=f"n_{opt}") for opt in opcoes_esquemas}
            
            if st.form_submit_button("💾 FINALIZAR CADASTRO"):
                sel_l = [n for n, v in novas_ligs.items() if v]
                novo_m = {
                    'Marca': marca, 'Potencia_CV': potencia, 'Polaridade': polos, 'Voltagem': volt,
                    'Bobina_Principal': b_p, 'Fio_Principal': f_p, 'Bobina_Auxiliar': b_a, 'Fio_Auxiliar': f_a,
                    'Esquema_Marcado': " / ".join(sel_l) if sel_l else "---"
                }
                pd.DataFrame([novo_m]).to_csv(ARQUIVO_CSV, mode='a', header=not os.path.exists(ARQUIVO_CSV), index=False, sep=';', encoding='utf-8-sig')
                st.success("Motor adicionado com sucesso!")
                st.rerun()

# --- ABA 3: ESQUEMAS ---
if e_admin:
    with tabs[2]:
        st.write("### 🖼️ Banco de Imagens (Esquemas)")
        with st.form("form_esquema"):
            up = st.file_uploader("Escolher Imagem (Paint)", type=['png', 'jpg'])
            nome_esq = st.text_input("Nome da Ligação")
            if st.form_submit_button("📁 SALVAR IMAGEM"):
                if up and nome_esq:
                    Image.open(up).save(os.path.join(PASTA_ESQUEMAS, f"{nome_esq}.png"))
                    st.rerun()
        
        st.divider()
        if opcoes_esquemas:
            for f in opcoes_esquemas:
                c_img, c_del = st.columns([4, 1])
                c_img.image(os.path.join(PASTA_ESQUEMAS, f"{f}.png"), caption=f, width=150)
                if c_del.button(f"Remover {f}", key=f"del_img_{f}"):
                    os.remove(os.path.join(PASTA_ESQUEMAS, f"{f}.png"))
                    st.rerun()

st.markdown("<p style='text-align:center; color:#555; margin-top:50px;'>Pablo Motores © 2026</p>", unsafe_allow_html=True)
