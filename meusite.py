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

# --- LOGIN DE ADMIN NO SIDEBAR ---
st.sidebar.title("🔐 Acesso Restrito")
senha_admin = st.sidebar.text_input("Senha do Admin", type="password")
SENHA_CORRETA = "pablo123" 
e_admin = (senha_admin == SENHA_CORRETA)

# --- ESTILO CSS ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #1e272e 0%, #000000 100%); color: #ffffff; }
    .main-header { background: rgba(255, 255, 255, 0.05); padding: 1.5rem; border-radius: 15px; border-bottom: 4px solid #f1c40f; margin-bottom: 2rem; text-align: center; }
    label { color: #f1c40f !important; font-weight: bold !important; }
    /* Estilo para os Expanders ficarem visíveis no fundo escuro */
    .streamlit-expanderHeader { background-color: rgba(255, 255, 255, 0.1) !important; color: #f1c40f !important; border-radius: 10px !important; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="main-header"><h1 style="color:#f1c40f; margin:0;">⚙️ PABLO MOTORES</h1></div>', unsafe_allow_html=True)

# --- NAVEGAÇÃO ---
if e_admin:
    abas = ["🔍 CONSULTA RÁPIDA", "➕ NOVO CADASTRO", "🖼️ ESQUEMAS (ADMIN)"]
else:
    abas = ["🔍 CONSULTA RÁPIDA"]

tabs = st.tabs(abas)

# --- ABA 1: CONSULTA (INTERATIVA) ---
with tabs[0]:
    busca = st.text_input("Pesquise por Marca ou Potência (CV)...").lower()
    
    if os.path.exists(ARQUIVO_CSV):
        df = pd.read_csv(ARQUIVO_CSV, sep=';', encoding='utf-8-sig')
        
        # Filtro de busca
        if busca:
            df_filtrado = df[df.astype(str).apply(lambda x: busca in x.str.lower().any(), axis=1)]
        else:
            df_filtrado = df

        if df_filtrado.empty:
            st.info("Nenhum motor encontrado com esse nome.")
        else:
            for index, row in df_filtrado.iterrows():
                # Criando o cabeçalho do motor que pode ser clicado
                titulo = f"🏷️ {row.get('Marca', 'MOTOR')} | {row.get('Potencia_CV', '-')} CV | {row.get('RPM', '-')} RPM"
                
                with st.expander(titulo):
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.write(f"**Polaridade:** {row.get('Polaridade', '-')} Polos")
                        st.write(f"**Voltagem:** {row.get('Voltagem', '-')} V")
                        st.write(f"**Amperagem:** {row.get('Amperagem', '-')} A")
                    with c2:
                        st.write(f"**Fio Principal:** {row.get('Fio_Principal', '-')}")
                        st.write(f"**Fio Auxiliar:** {row.get('Fio_Auxiliar', '-')}")
                        st.write(f"**Capacitor:** {row.get('Capacitor', '-')}")
                    with c3:
                        st.write(f"**Eixo X:** {row.get('Eixo_X', '-')}")
                        st.write(f"**Eixo Y:** {row.get('Eixo_Y', '-')}")
                        st.warning(f"**Ligações:** {row.get('Esquema_Marcado', 'Nenhuma')}")
                    
                    if e_admin:
                        if st.button(f"🗑️ Excluir registro {index}", key=f"del_{index}"):
                            df = df.drop(index)
                            df.to_csv(ARQUIVO_CSV, index=False, sep=';', encoding='utf-8-sig')
                            st.rerun()

# --- ABA 2: CADASTRO (Só Admin) ---
if e_admin:
    with tabs[1]:
        st.markdown("### 📝 Cadastro de Novo Motor")
        with st.form("form_cadastro", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                marca = st.text_input("Marca do Motor")
                potencia = st.text_input("Potência (CV)")
                rpm = st.text_input("RPM")
                polos = st.selectbox("Polos", ["2", "4", "6", "8"])
                amp = st.text_input("Amperagem")
                volt = st.text_input("Voltagem")
            with col2:
                b_p = st.text_input("Bobina Principal")
                f_p = st.text_input("Fio Principal")
                b_a = st.text_input("Bobina Auxiliar")
                f_a = st.text_input("Fio Auxiliar")
                cap = st.text_input("Capacitor")
                rol = st.text_input("Rolamentos")
            with col3:
                ex = st.text_input("Tamanho Eixo X")
                ey = st.text_input("Tamanho Eixo Y")
                st.write("**Ligações:**")
                l1 = st.checkbox("Estrela (Y)")
                l2 = st.checkbox("Triângulo (Δ)")
                l3 = st.checkbox("Série")
                l4 = st.checkbox("Paralelo")
            
            if st.form_submit_button("💾 SALVAR MOTOR"):
                links = []
                if l1: links.append("Y")
                if l2: links.append("Δ")
                if l3: links.append("Série")
                if l4: links.append("Paralelo")
                
                novo_dado = {
                    'Marca': marca, 'Potencia_CV': potencia, 'RPM': rpm, 'Polaridade': polos,
                    'Fio_Principal': f_p, 'Fio_Auxiliar': f_a, 'Amperagem': amp, 'Voltagem': volt,
                    'Capacitor': cap, 'Rolamentos': rol, 'Eixo_X': ex, 'Eixo_Y': ey,
                    'Esquema_Marcado': ", ".join(links)
                }
                
                df_novo = pd.DataFrame([novo_dado])
                df_novo.to_csv(ARQUIVO_CSV, mode='a', header=not os.path.exists(ARQUIVO_CSV), index=False, sep=';', encoding='utf-8-sig')
                st.success("Motor salvo com sucesso!")

    # ABA 3: ESQUEMAS (Só Admin)
    with tabs[2]:
        st.subheader("🖼️ Galeria de Fotos do Paint")
        up = st.file_uploader("Arraste sua foto aqui", type=['png', 'jpg'])
        nome_f = st.text_input("Nome do Esquema")
        if st.button("Salvar Esquema") and up and nome_f:
            Image.open(up).save(os.path.join(PASTA_ESQUEMAS, f"{nome_f}.png"))
            st.rerun()
            
        st.divider()
        fotos = [f for f in os.listdir(PASTA_ESQUEMAS) if f.endswith(('.png', '.jpg'))]
        if fotos:
            escolha = st.selectbox("Selecione para abrir:", fotos)
            st.image(os.path.join(PASTA_ESQUEMAS, escolha), use_container_width=True)

st.markdown("<br><p style='text-align:center; color:#555;'>Pablo Motores © 2026</p>", unsafe_allow_html=True)
