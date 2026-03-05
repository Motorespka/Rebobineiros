import streamlit as st
import pandas as pd
import os
import re
import urllib.parse
import random
import string
from datetime import datetime, timedelta

# --- 1. CONFIGURAÇÕES DE SEGURANÇA E ARQUIVOS ---
# Altere os tokens abaixo conforme desejar
TOKEN_PRO = "PABLO123"      # Acesso para Wesley/Pablo
TOKEN_MESTRE = "MESTRE99"   # Acesso Total para o Chefe

ARQUIVO_CSV = 'meubancodedados.csv'
ARQUIVO_FOTOS = 'biblioteca_fotos.csv'
PASTA_UPLOADS = 'uploads_ligacoes'

if not os.path.exists(PASTA_UPLOADS):
    os.makedirs(PASTA_UPLOADS)

# --- INICIALIZAÇÃO DE SESSÃO ---
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False
if 'perfil' not in st.session_state:
    st.session_state['perfil'] = None 
if 'db_os' not in st.session_state:
    st.session_state['db_os'] = []

# --- 2. BANCO TÉCNICO AWG ---
TABELA_AWG_TECNICA = {
    '4/0': 107.0, '3/0': 85.0, '2/0': 67.4, '1/0': 53.5,
    '1': 42.41, '2': 33.63, '3': 26.67, '4': 21.147, '5': 16.764,
    '6': 13.299, '7': 10.55, '8': 8.367, '9': 6.633, '10': 5.26,
    '11': 4.169, '12': 3.307, '13': 2.627, '14': 2.082, '15': 1.651,
    '16': 1.307, '17': 1.04, '18': 0.8235, '19': 0.6533, '20': 0.5191,
    '21': 0.4117, '22': 0.3247, '23': 0.2588, '24': 0.2051, '25': 0.1626,
    '26': 0.1282, '27': 0.1024, '28': 0.0804, '29': 0.0647, '30': 0.0507,
    '31': 0.0401, '32': 0.0324, '33': 0.0254, '34': 0.0201
}

# --- 3. FUNÇÕES DE APOIO ---
def carregar_dados(arq, colunas):
    if not os.path.exists(arq) or os.stat(arq).st_size == 0:
        return pd.DataFrame(columns=colunas)
    df = pd.read_csv(arq, sep=';', encoding='utf-8-sig', dtype=str).fillna("")
    for col in colunas:
        if col not in df.columns: df[col] = ""
    return df

def salvar_dados(df, arq):
    df.fillna("").to_csv(arq, index=False, sep=';', encoding='utf-8-sig')

def calcular_area_mm2(texto_fio):
    try:
        if not texto_fio or str(texto_fio).lower() in ["nan", ""]: return 0.0
        texto = str(texto_fio).lower().replace('awg', '').strip()
        if 'x' in texto:
            partes = texto.split('x')
            qtd = int(re.findall(r'\d+', partes[0])[0])
            bitola = partes[1].strip()
            return qtd * TABELA_AWG_TECNICA.get(bitola, 0.0)
        bitolas = re.findall(r'\d+', texto)
        return TABELA_AWG_TECNICA.get(bitolas[0], 0.0) if bitolas else 0.0
    except: return 0.0

# --- 4. TELA DE LOGIN ---
def tela_login():
    st.markdown("<h1 style='text-align: center;'>⚙️ Pablo Motores - Portal</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        aba_log, aba_cad = st.tabs(["🔐 Entrar", "📝 Cadastro Cliente"])
        
        with aba_log:
            perfil_sel = st.selectbox("Tipo de Acesso", ["👤 Cliente", "🛠️ Profissional (Wesley/Pablo)", "🧠 Mestre (Chefe)"])
            
            if perfil_sel == "👤 Cliente":
                user = st.text_input("Utilizador")
                senha = st.text_input("Palavra-passe", type="password")
                if st.button("Aceder ao Catálogo"):
                    st.session_state['autenticado'] = True
                    st.session_state['perfil'] = 'cliente'
                    st.rerun()
            
            elif perfil_sel == "🛠️ Profissional (Wesley/Pablo)":
                tk = st.text_input("Token da Oficina", type="password")
                if st.button("Entrar na Oficina"):
                    if tk == TOKEN_PRO:
                        st.session_state['autenticado'] = True
                        st.session_state['perfil'] = 'pro'
                        st.rerun()
                    else: st.error("Token incorreto")

            elif perfil_sel == "🧠 Mestre (Chefe)":
                tk_m = st.text_input("Token Mestre", type="password")
                if st.button("Acesso Administrativo"):
                    if tk_m == TOKEN_MESTRE:
                        st.session_state['autenticado'] = True
                        st.session_state['perfil'] = 'mestre'
                        st.rerun()
                    else: st.error("Acesso Negado")

        with aba_cad:
            st.write("Crie a sua conta de cliente para consultar ligações.")
            st.text_input("Nome Completo", key="cad_nome")
            st.text_input("Palavra-passe", type="password", key="cad_pass")
            if st.button("Confirmar Registo"):
                st.success("Conta criada com sucesso!")

# --- 5. INTERFACE PRINCIPAL ---
if not st.session_state['autenticado']:
    tela_login()
else:
    st.set_page_config(page_title="Pablo Motores Pro", layout="wide")
    
    COL_MOTORES = [
        'Marca', 'Potencia_CV', 'RPM', 'Voltagem', 'Amperagem', 'Polaridade', 
        'Bobina_Principal', 'Fio_Principal', 'Bobina_Auxiliar', 'Fio_Auxiliar', 
        'Tipo_Ligacao', 'Rolamentos', 'Eixo_X', 'Eixo_Y', 'Capacitor', 'status'
    ]
    df_motores = carregar_dados(ARQUIVO_CSV, COL_MOTORES)
    df_fotos = carregar_dados(ARQUIVO_FOTOS, ['nome_ligacao', 'caminho_arquivo'])
    lista_ligacoes = [""] + df_fotos['nome_ligacao'].tolist()

    with st.sidebar:
        st.title(f"Perfil: {st.session_state['perfil'].upper()}")
        if st.button("🚪 Sair"):
            st.session_state['autenticado'] = False
            st.rerun()
        
        st.divider()
        menu_items = ["🔍 CONSULTAR MOTORES"]
        if st.session_state['perfil'] in ['pro', 'mestre']:
            menu_items += ["➕ NOVO MOTOR"]
        if st.session_state['perfil'] == 'mestre':
            menu_items += ["🖼️ BIBLIOTECA", "🗑️ LIXEIRA"]
        
        menu = st.radio("Menu", menu_items)

    # --- ABA CONSULTA ---
    if menu == "🔍 CONSULTAR MOTORES":
        st.header("🔍 Catálogo Técnico")
        busca = st.text_input("Pesquisar motor (ex: WEG 1CV)...")
        
        df_exibir = df_motores[df_motores['status'] != 'deletado']
        if busca:
            df_exibir = df_exibir[df_exibir.apply(lambda r: r.astype(str).str.contains(busca, case=False).any(), axis=1)]

        for idx, row in df_exibir.iterrows():
            with st.expander(f"📦 {row['Marca']} | {row['Potencia_CV']} CV | {row['RPM']} RPM"):
                
                # ABAS HIERARQUICAS
                abas_visiveis = ["🟢 BÁSICO"]
                if st.session_state['perfil'] in ['pro', 'mestre']: abas_visiveis.append("🛠️ PROFISSIONAL")
                if st.session_state['perfil'] == 'mestre': abas_visiveis.append("🧠 MESTRE")
                
                tabs = st.tabs(abas_visiveis)
                
                # TAB CLIENTE
                with tabs[0]:
                    st.subheader("Informações para Ligação")
                    col_b1, col_b2 = st.columns(2)
                    with col_b1:
                        st.info(f"**Voltagem:** {row['Voltagem']}")
                        st.warning(f"**Amperagem:** {row['Amperagem']} A")
                        st.success(f"**Capacitor:** {row['Capacitor']}")
                    with col_b2:
                        tipo = row['Tipo_Ligacao']
                        if tipo in df_fotos['nome_ligacao'].values:
                            st.image(df_fotos[df_fotos['nome_ligacao'] == tipo]['caminho_arquivo'].values[0], use_container_width=True)
                        else: st.write("Esquema de ligação não disponível.")

                # TAB PROFISSIONAL
                if "🛠️ PROFISSIONAL" in abas_visiveis:
                    with tabs[1]:
                        st.subheader("Dados Técnicos de Bancada")
                        col_p1, col_p2 = st.columns(2)
                        with col_p1:
                            st.write(f"**Fio Principal:** {row['Fio_Principal']}")
                            st.write(f"**Espiras:** {row['Bobina_Principal']}")
                        with col_p2:
                            st.write(f"**Rolamentos:** {row['Rolamentos']}")
                        
                        if st.button("✈️ Enviar OS por WhatsApp", key=f"z_{idx}"):
                            txt = f"*PABLO MOTORES*\nMotor: {row['Marca']} {row['Potencia_CV']}CV\nFio: {row['Fio_Principal']}\nRolamentos: {row['Rolamentos']}"
                            st.markdown(f"[CLIQUE PARA ENVIAR](https://wa.me/?text={urllib.parse.quote(txt)})")

                # TAB MESTRE
                if "🧠 MESTRE" in abas_visiveis:
                    with tabs[-1]:
                        st.subheader("Ferramentas de Engenharia e Gestão")
                        col_m1, col_m2 = st.columns(2)
                        with col_m1:
                            st.markdown("##### 📐 Conversor Alumínio p/ Cobre")
                            f_al = st.text_input("Fio Alumínio Original:", "2x21", key=f"al_{idx}")
                            area_al = calcular_area_mm2(f_al)
                            st.code(f"Área Cobre Sugerida: {area_al * 0.82:.4f} mm²")
                        
                        with col_m2:
                            if st.button("🗑️ Excluir permanentemente", key=f"del_{idx}"):
                                df_motores.at[idx, 'status'] = 'deletado'
                                salvar_dados(df_motores, ARQUIVO_CSV)
                                st.rerun()

    # --- ABA NOVO MOTOR ---
    elif menu == "➕ NOVO MOTOR":
        st.header("➕ Cadastrar Novo Motor")
        with st.form("form_add", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            with c1:
                m = st.text_input("Marca"); cv = st.text_input("Potência (CV)"); r = st.text_input("RPM")
            with c2:
                fp = st.text_input("Fio Principal"); gp = st.text_input("Espiras Principal")
                v = st.text_input("Voltagem")
            with c3:
                rol = st.text_input("Rolamentos"); cap = st.text_input("Capacitor"); lig = st.selectbox("Ligação", lista_ligacoes)
            
            if st.form_submit_button("✅ GUARDAR"):
                novo = {'Marca': m, 'Potencia_CV': cv, 'RPM': r, 'Voltagem': v, 'Fio_Principal': fp, 'Bobina_Principal': gp, 'Rolamentos': rol, 'Capacitor': cap, 'Tipo_Ligacao': lig, 'status': 'ativo'}
                df_motores = pd.concat([df_motores, pd.DataFrame([novo])], ignore_index=True)
                salvar_dados(df_motores, ARQUIVO_CSV)
                st.success("Motor adicionado com sucesso!")

    # --- BIBLIOTECA E LIXEIRA (RESTRITO MESTRE) ---
    elif menu == "🖼️ BIBLIOTECA":
        st.header("🖼️ Gestão de Esquemas")
        # Lógica de upload...
    
    elif menu == "🗑️ LIXEIRA":
        st.header("🗑️ Arquivo de Excluídos")
        # Lógica de restauro...
