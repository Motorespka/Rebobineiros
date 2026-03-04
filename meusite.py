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

st.set_page_config(page_title="Pablo Motores", layout="wide")

# --- 2. FUNÇÕES DE DADOS ---
def carregar_dados():
    if not os.path.exists(ARQUIVO_CSV):
        return pd.DataFrame()
    try:
        df = pd.read_csv(ARQUIVO_CSV, sep=';', encoding='utf-8-sig', dtype=str)
        df.columns = df.columns.str.strip()
        return df
    except:
        return pd.DataFrame()

def salvar_dados(df):
    df.to_csv(ARQUIVO_CSV, index=False, sep=';', encoding='utf-8-sig')
    st.cache_data.clear()

# --- 3. LOGIN (ESTRUTURA BASE) ---
if 'user_data' not in st.session_state:
    st.session_state['user_data'] = None

# [O código de login permanece o mesmo da sua base]
# ...

if st.session_state['user_data']:
    user = st.session_state['user_data']
    e_admin = (user.get('perfil') == 'admin')
    
    with st.sidebar:
        st.markdown(f"### 👤 {user['usuario'].upper()}")
        menu = ["🔍 CONSULTA"]
        if e_admin: menu += ["➕ NOVO CADASTRO", "🖼️ ADICIONAR FOTO", "🗑️ LIXEIRA"]
        escolha = st.radio("Navegação:", menu)
        if st.button("Sair"):
            st.session_state['user_data'] = None
            st.rerun()

    # --- ABA: CONSULTA (EDITAR E ALTERAR) ---
    if escolha == "🔍 CONSULTA":
        st.title("⚙️ CONSULTA E CÁLCULOS")
        df = carregar_dados()
        busca = st.text_input("🔍 Pesquisar...")

        if not df.empty:
            # Filtro para usuários não verem excluídos
            if not e_admin:
                df = df[df.get('status', 'ativo') != 'deletado']
            
            df_f = df[df.apply(lambda row: row.astype(str).str.contains(busca, case=False).any(), axis=1)] if busca else df
            
            for idx, row in df_f.iterrows():
                marca = row.get('Marca', 'Sem Marca')
                potencia = row.get('Potencia_CV', row.get('Potencia', 'N/A'))
                is_del = row.get('status') == 'deletado'
                
                label = f"📦 {marca} | {potencia} CV" + (" (LIXEIRA)" if is_del else "")
                
                with st.expander(label):
                    col_info, col_botoes = st.columns([2, 1])
                    
                    with col_info:
                        st.write(f"**Amperagem:** {row.get('Amperagem', '---')}")
                        st.write(f"**Fio Principal:** {row.get('Fio_Principal', '---')}")
                        st.write(f"**Rolamentos:** {row.get('Rolamentos', '---')}")
                        st.write(f"**Eixos:** {row.get('Eixo_X', '---')} / {row.get('Eixo_Y', '---')}")

                    with col_botoes:
                        # 1. BOTÃO ALTERAR (GERA CÓPIA VISUAL)
                        if st.button("🔄 Alterar (Cópia)", key=f"alt_{idx}"):
                            st.session_state[f"view_copy_{idx}"] = True
                        
                        # 2. BOTÃO EDITAR (SÓ ADMIN - MUDA ORIGINAL)
                        if e_admin:
                            if st.button("📝 Editar Original", key=f"edit_{idx}"):
                                st.session_state[f"mode_edit_{idx}"] = True
                            
                            if st.button("🗑️ Excluir", key=f"del_{idx}"):
                                df.at[idx, 'status'] = 'deletado'
                                df.at[idx, 'data_expiracao'] = (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d')
                                salvar_dados(df)
                                st.rerun()

                    # --- INTERFACE DA CÓPIA (VISUALIZAÇÃO) ---
                    if st.session_state.get(f"view_copy_{idx}"):
                        st.info("📋 **MODO ALTERAR (CÓPIA TEMPORÁRIA)**")
                        st.caption("Esta alteração não será salva no banco de dados.")
                        fio_alt = st.text_input("Simular Fio Novo", value=row.get('Fio_Principal'), key=f"f_alt_{idx}")
                        st.success(f"DADOS PARA FOTO: Fio {fio_alt} | Potência {potencia}")
                        if st.button("Fechar Cópia", key=f"cls_copy_{idx}"):
                            del st.session_state[f"view_copy_{idx}"]
                            st.rerun()

                    # --- INTERFACE DE EDIÇÃO (ADMIN - ALTERA O BANCO) ---
                    if e_admin and st.session_state.get(f"mode_edit_{idx}"):
                        with st.form(f"form_edit_{idx}"):
                            st.warning("⚠️ VOCÊ ESTÁ EDITANDO O CÁLCULO ORIGINAL")
                            new_fio = st.text_input("Novo Fio Principal", value=row.get('Fio_Principal'))
                            new_amp = st.text_input("Nova Amperagem", value=row.get('Amperagem'))
                            if st.form_submit_button("SALVAR ALTERAÇÕES DEFINITIVAS"):
                                df.at[idx, 'Fio_Principal'] = new_fio
                                df.at[idx, 'Amperagem'] = new_amp
                                salvar_dados(df)
                                del st.session_state[f"mode_edit_{idx}"]
                                st.rerun()

    # --- ABA: NOVO CADASTRO (TODOS OS CAMPOS) ---
    elif escolha == "➕ NOVO CADASTRO" and e_admin:
        st.title("➕ Novo Motor")
        with st.form("form_novo"):
            c1, c2, c3 = st.columns(3)
            with c1:
                marca = st.text_input("Marca"); cv = st.text_input("Potencia_CV"); rpm = st.text_input("RPM")
                pol = st.text_input("Polaridade"); volt = st.text_input("Voltagem"); amp = st.text_input("Amperagem")
            with c2:
                g_p = st.text_input("Grupo Principal"); f_p = st.text_input("Fio Principal")
                rol = st.text_input("Rolamentos"); ex_x = st.text_input("Eixo X")
            with c3:
                g_a = st.text_input("Grupo Auxiliar"); f_a = st.text_input("Fio Auxiliar")
                cap = st.text_input("Capacitor"); ex_y = st.text_input("Eixo Y")
            
            if st.form_submit_button("CADASTRAR"):
                # Lógica para salvar motor com status 'ativo'
                pass

    # --- ABA: LIXEIRA (ADM) ---
    elif escolha == "🗑️ LIXEIRA" and e_admin:
        st.title("🗑️ Lixeira")
        df = carregar_dados()
        if not df.empty:
            excluidos = df[df['status'] == 'deletado']
            for i, r in excluidos.iterrows():
                expira = datetime.strptime(r['data_expiracao'], '%Y-%m-%d')
                if datetime.now() > expira:
                    df.drop(i, inplace=True)
                    salvar_dados(df)
                    st.rerun()
                else:
                    st.error(f"{r['Marca']} - {r['Potencia_CV']} CV (Expira em: {r['data_expiracao']})")
                    if st.button(f"Restaurar {i}"):
                        df.at[i, 'status'] = 'ativo'
                        salvar_dados(df)
                        st.rerun()
