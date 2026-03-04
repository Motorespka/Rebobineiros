import streamlit as st
import pandas as pd
import os
import hashlib
from datetime import datetime, timedelta
from PIL import Image

# --- 1. CONFIGURAÇÕES E PASTAS ---
ARQUIVO_USUARIOS = 'usuarios.csv'
ARQUIVO_CSV = 'meubancodedados.csv'
LINK_SHEETS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTFbH81UYKGJ6dQvKotxdv4hDxecLmiGUPHN46iexbw8NeS8_e2XdyZnZ8WJnL2XRTLCbFDbBKo_NGE/pub?output=csv"
PASTA_ESQUEMAS = 'esquemas_fotos'
CHAVE_MESTRA_CHEFIA = "PABLO2026"

if not os.path.exists(PASTA_ESQUEMAS): os.makedirs(PASTA_ESQUEMAS)

st.set_page_config(page_title="Pablo Motores | Gestão & Engenharia", layout="wide")

# --- 2. FUNÇÕES DE APOIO ---
def carregar_dados():
    if not os.path.exists(ARQUIVO_CSV):
        return pd.DataFrame()
    return pd.read_csv(ARQUIVO_CSV, sep=';', encoding='utf-8-sig', dtype=str)

def salvar_dados(df):
    df.to_csv(ARQUIVO_CSV, index=False, sep=';', encoding='utf-8-sig')
    st.cache_data.clear()

# --- 3. ÁREA DE LOGIN (Mantida conforme sua base) ---
if 'user_data' not in st.session_state: st.session_state['user_data'] = None

# ... (Lógica de login e cadastro de usuários omitida para focar nas novas funções) ...

if st.session_state['user_data']:
    user = st.session_state['user_data']
    e_admin = (user['perfil'] == 'admin')
    
    with st.sidebar:
        st.markdown(f"### 👤 {user['usuario'].upper()}")
        menu = ["🔍 CONSULTA"]
        if e_admin: menu += ["➕ NOVO CADASTRO", "🖼️ ADICIONAR FOTO", "🗑️ LIXEIRA"]
        escolha = st.radio("Navegação:", menu)
        if st.button("Sair / Logoff"):
            st.session_state['user_data'] = None
            st.rerun()

    # --- ABA: CONSULTA (EDIÇÃO, CÓPIA E EXCLUSÃO) ---
    if escolha == "🔍 CONSULTA":
        st.title("⚙️ CONSULTA DE MOTORES")
        df = carregar_dados()
        busca = st.text_input("🔍 Pesquisar motor...")

        if not df.empty:
            # Filtrar para não mostrar excluídos (status 'deletado') para usuários comuns
            if not e_admin:
                df = df[df['status'] != 'deletado']
            
            df_f = df[df.apply(lambda row: row.astype(str).str.contains(busca, case=False).any(), axis=1)] if busca else df
            
            for idx, row in df_f.iterrows():
                cor_borda = "red" if row.get('status') == 'deletado' else "#f1c40f"
                with st.expander(f"📦 {row.get('Marca')} | {row.get('Potencia_CV')} CV | {row.get('RPM')} RPM"):
                    if row.get('status') == 'deletado':
                        st.warning(f"🚫 ESTE CÁLCULO ESTÁ NA LIXEIRA (Exclusão definitiva em: {row.get('data_expiracao')})")

                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.write(f"**Amperagem:** {row.get('Amperagem')} | **Volt:** {row.get('Voltagem')}")
                        st.write(f"**Fio Principal:** {row.get('Fio_Principal')} | **Fio Aux:** {row.get('Fio_Auxiliar')}")
                        st.write(f"**Rolamentos:** {row.get('Rolamentos')}")
                        st.write(f"**Eixos:** X: {row.get('Eixo_X')} / Y: {row.get('Eixo_Y')}")

                    with col2:
                        # BOTÃO CÓPIA (ALTERAR SEM MUDAR O ORIGINAL)
                        if st.button("📝 Criar Cópia (Alterar)", key=f"copy_{idx}"):
                            st.session_state[f"edit_copia_{idx}"] = True
                        
                        if e_admin:
                            if st.button("🗑️ Excluir", key=f"del_{idx}"):
                                df.at[idx, 'status'] = 'deletado'
                                df.at[idx, 'data_expiracao'] = (datetime.now() + timedelta(days=5)).strftime('%d/%m/%Y')
                                salvar_dados(df)
                                st.rerun()

                    # ÁREA DA CÓPIA EDITÁVEL (Não salva no CSV)
                    if st.session_state.get(f"edit_copia_{idx}"):
                        st.info("🛠️ **MODO CÓPIA:** Altere os dados abaixo para tirar foto ou imprimir. O original não será afetado.")
                        temp_fio = st.text_input("Alterar Fio para Rebobinagem", value=row.get('Fio_Principal'), key=f"f_{idx}")
                        temp_obs = st.text_area("Observações da Gambiarra", key=f"obs_{idx}")
                        if st.button("Fechar Cópia", key=f"close_{idx}"):
                            del st.session_state[f"edit_copia_{idx}"]
                            st.rerun()

    # --- ABA: NOVO CADASTRO (COM TODOS OS CAMPOS) ---
    elif escolha == "➕ NOVO CADASTRO" and e_admin:
        st.title("➕ Cadastrar Novo Motor")
        with st.form("cadastro_completo"):
            c1, c2, c3 = st.columns(3)
            with c1:
                marca = st.text_input("Marca"); cv = st.text_input("Potência (CV)"); rpm = st.text_input("RPM")
                pol = st.text_input("Polaridade"); volt = st.text_input("Voltagem"); amp = st.text_input("Amperagem")
            with c2:
                g_p = st.text_input("Grupo Principal"); f_p = st.text_input("Fio Principal")
                rol = st.text_input("Rolamentos"); ex_x = st.text_input("Eixo X")
            with c3:
                g_a = st.text_input("Grupo Auxiliar"); f_a = st.text_input("Fio Auxiliar")
                cap = st.text_input("Capacitor"); ex_y = st.text_input("Eixo Y")
            
            if st.form_submit_button("💾 SALVAR MOTOR"):
                novo = {
                    'Marca': marca, 'Potencia_CV': cv, 'RPM': rpm, 'Polaridade': pol, 'Voltagem': volt, 
                    'Amperagem': amp, 'Bobina_Principal': g_p, 'Fio_Principal': f_p, 'Rolamentos': rol, 
                    'Eixo_X': ex_x, 'Bobina_Auxiliar': g_a, 'Fio_Auxiliar': f_a, 'Capacitor': cap, 
                    'Eixo_Y': ex_y, 'status': 'ativo', 'data_expiracao': 'None'
                }
                df_novo = pd.concat([carregar_dados(), pd.DataFrame([novo])], ignore_index=True)
                salvar_dados(df_novo)
                st.success("Motor cadastrado com sucesso!")

    # --- ABA: LIXEIRA (ADM APENAS) ---
    elif escolha == "🗑️ LIXEIRA" and e_admin:
        st.title("🗑️ Lixeira Técnica")
        df = carregar_dados()
        if not df.empty:
            excluidos = df[df['status'] == 'deletado']
            if excluidos.empty:
                st.write("Lixeira vazia.")
            else:
                for idx, r in excluidos.iterrows():
                    st.error(f"Motor: {r['Marca']} - {r['Potencia_CV']} CV (Exclui em: {r['data_expiracao']})")
                    if st.button(f"Restaurar {idx}", key=f"res_{idx}"):
                        df.at[idx, 'status'] = 'ativo'
                        salvar_dados(df)
                        st.rerun()
