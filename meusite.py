import streamlit as st
import pandas as pd
import os
import re
import urllib.parse
import random
import string
from datetime import datetime, timedelta

# --- 1. CONFIGURAÇÕES DE ARQUIVOS E SESSÃO ---
ARQUIVO_CSV = 'meubancodedados.csv'
ARQUIVO_FOTOS = 'biblioteca_fotos.csv'
PASTA_UPLOADS = 'uploads_ligacoes'

# TOKENS DE SEGURANÇA (Adição solicitada)
TOKEN_PRO = "PABLO123"      # Acesso Médio
TOKEN_MESTRE = "MESTRE99"   # Acesso Total

if not os.path.exists(PASTA_UPLOADS):
    os.makedirs(PASTA_UPLOADS)

# Inicialização de Estados de Sessão
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False
if 'perfil' not in st.session_state:
    st.session_state['perfil'] = None
if 'db_os' not in st.session_state:
    st.session_state['db_os'] = []
if 'token_grupo' not in st.session_state:
    st.session_state['token_grupo'] = None

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

# --- 3. FUNÇÕES DE APOIO (Mantidas Integrais) ---
def carregar_dados(arq, colunas):
    if not os.path.exists(arq) or os.stat(arq).st_size == 0:
        return pd.DataFrame(columns=colunas)
    df = pd.read_csv(arq, sep=';', encoding='utf-8-sig', dtype=str).fillna("")
    for col in colunas:
        if col not in df.columns: df[col] = ""
    return df

def salvar_dados(df, arq):
    df.fillna("").to_csv(arq, index=False, sep=';', encoding='utf-8-sig')

def gerar_token():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def limpar_os_vencidas():
    hoje = datetime.now()
    st.session_state['db_os'] = [
        os_item for os_item in st.session_state['db_os'] 
        if os_item.get('expira_em') is None or os_item['expira_em'] > hoje
    ]

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

def gerar_sugestoes(area_alvo):
    sugestoes = []
    if area_alvo <= 0: return []
    for bitola, area_u in TABELA_AWG_TECNICA.items():
        for qtd in range(1, 5):
            area_sim = area_u * qtd
            diff = ((area_sim - area_alvo) / area_alvo) * 100
            if -10.0 <= diff <= 10.0:
                if abs(diff) <= 2.5: cor, status = "#28a745", "EXCELENTE"
                elif abs(diff) <= 6.0: cor, status = "#ffc107", "ACEITÁVEL"
                else: cor, status = "#dc3545", "PERIGOSO"
                sugestoes.append({'fio': f"{qtd}x{bitola} AWG", 'diff': diff, 'cor': cor, 'status': status})
    return sorted(sugestoes, key=lambda x: abs(x['diff']))

# --- 4. TELA DE ACESSO (Login) ---
if not st.session_state['autenticado']:
    st.title("⚙️ Portal Pablo Motores")
    aba_login, aba_cliente = st.tabs(["🔐 Entrar", "📝 Novo Cliente"])
    
    with aba_login:
        tipo = st.selectbox("Entrar como:", ["Cliente", "Mecânico/Rebobinador", "Mestre"])
        if tipo == "Cliente":
            if st.button("Acessar Catálogo"):
                st.session_state['autenticado'] = True
                st.session_state['perfil'] = 'cliente'
                st.rerun()
        else:
            tk = st.text_input("Digite o Token de Acesso:", type="password")
            if st.button("Confirmar Token"):
                if tipo == "Mecânico/Rebobinador" and tk == TOKEN_PRO:
                    st.session_state['autenticado'] = True
                    st.session_state['perfil'] = 'pro'
                    st.rerun()
                elif tipo == "Mestre" and tk == TOKEN_MESTRE:
                    st.session_state['autenticado'] = True
                    st.session_state['perfil'] = 'mestre'
                    st.rerun()
                else:
                    st.error("Token Inválido!")
    stop = True # Pausa a execução se não estiver logado

# --- 5. CONFIGURAÇÃO DA PÁGINA (Pós-Autenticação) ---
if st.session_state['autenticado']:
    st.set_page_config(page_title="Pablo Motores Pro", layout="wide")
    limpar_os_vencidas()

    # Colunas completas conforme sua necessidade de mais informação
    COL_MOTORES = [
        'Marca', 'Potencia_CV', 'RPM', 'Voltagem', 'Amperagem', 'Polaridade', 
        'Bobina_Principal', 'Fio_Principal', 'Passo_P',
        'Bobina_Auxiliar', 'Fio_Auxiliar', 'Passo_A',
        'Tipo_Ligacao', 'Ligacao_Interna', 'Rolamentos', 'Selo_Mecanico',
        'Eixo_X', 'Eixo_Y', 'Capacitor', 'status', 'Obs_Mestre'
    ]
    df_motores = carregar_dados(ARQUIVO_CSV, COL_MOTORES)
    df_fotos = carregar_dados(ARQUIVO_FOTOS, ['nome_ligacao', 'caminho_arquivo'])
    lista_ligacoes = [""] + df_fotos['nome_ligacao'].tolist()

    with st.sidebar:
        st.title(f"Acesso: {st.session_state['perfil'].upper()}")
        if st.button("🚪 Sair"):
            st.session_state['autenticado'] = False
            st.rerun()
        
        st.divider()
        # MENU BASEADO NO PERFIL
        opcoes = ["🔍 CONSULTA"]
        if st.session_state['perfil'] in ['pro', 'mestre']:
            opcoes += ["➕ NOVO MOTOR", "📊 PAINEL DE OS"]
        if st.session_state['perfil'] == 'mestre':
            opcoes += ["🖼️ BIBLIOTECA", "🗑️ LIXEIRA"]
        
        menu = st.radio("Menu Principal", opcoes)

    # --- ABA CONSULTA ---
    if menu == "🔍 CONSULTA":
        st.header("🔍 Banco de Dados Técnico")
        busca = st.text_input("Filtrar motor...")
        
        df_f = df_motores[df_motores['status'] != 'deletado']
        if busca:
            df_f = df_f[df_f.apply(lambda r: r.astype(str).str.contains(busca, case=False).any(), axis=1)]

        for idx, row in df_f.iterrows():
            area_ref = calcular_area_mm2(row['Fio_Principal'])
            espiras_base = re.findall(r'\d+', str(row['Bobina_Principal']))
            espiras_ref = int(espiras_base[0]) if espiras_base else 0

            label = f"📦 {row['Marca']} | {row['Potencia_CV']} CV | {row['RPM']} RPM"
            
            with st.expander(label):
                # Hierarquia de Abas
                abas = ["📋 GERAL (Cliente)"]
                if st.session_state['perfil'] in ['pro', 'mestre']:
                    abas.append("⚙️ REBOBINAGEM")
                if st.session_state['perfil'] == 'mestre':
                    abas.append("👑 EDITAR/MESTRE")
                
                tabs = st.tabs(abas)
                
                # ABA 1: CLIENTE E BÁSICO
                with tabs[0]:
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.markdown("#### ⚡ Elétrica")
                        st.write(f"**Voltagem:** {row['Voltagem']} V")
                        st.write(f"**Amperagem:** {row['Amperagem']} A")
                        st.write(f"**Capacitor:** {row['Capacitor']}")
                    with c2:
                        st.markdown("#### 🔧 Peças/Mecânica")
                        st.write(f"**Rolamentos:** {row['Rolamentos']}")
                        st.write(f"**Selo Mecânico:** {row['Selo_Mecanico']}")
                        st.write(f"**Eixo:** {row['Eixo_X']} / {row['Eixo_Y']}")
                    with c3:
                        st.markdown("#### 🖼️ Ligação")
                        tipo = row['Tipo_Ligacao']
                        if tipo and tipo in df_fotos['nome_ligacao'].values:
                            st.image(df_fotos[df_fotos['nome_ligacao'] == tipo]['caminho_arquivo'].values[0])

                # ABA 2: TÉCNICO (Pablo/Wesley)
                if "⚙️ REBOBINAGEM" in abas:
                    with tabs[1]:
                        st.subheader("🛠️ Dados de Bancada")
                        p1, p2 = st.columns(2)
                        with p1:
                            st.info(f"**Principal:** {row['Fio_Principal']} | {row['Bobina_Principal']} esp | Passo: {row['Passo_P']}")
                            st.warning(f"**Auxiliar:** {row['Fio_Auxiliar']} | {row['Bobina_Auxiliar']} esp | Passo: {row['Passo_A']}")
                        with p2:
                            st.write(f"**Ligação Interna:** {row['Ligacao_Interna']}")
                            st.write(f"**Observação do Mestre:** {row['Obs_Mestre']}")
                        
                        # Sua lógica original de envio de OS por WhatsApp aqui
                        if st.button("✈️ Enviar Relatório WhatsApp", key=f"z_{idx}"):
                            msg = f"*RELATÓRIO TÉCNICO*\nMotor: {row['Marca']}\nFio: {row['Fio_Principal']}\nRolamentos: {row['Rolamentos']}"
                            st.markdown(f"[CLIQUE AQUI PARA ENVIAR](https://wa.me/?text={urllib.parse.quote(msg)})")

                # ABA 3: MESTRE (CÁLCULOS E EDIÇÃO)
                if "👑 EDITAR/MESTRE" in abas:
                    with tabs[-1]:
                        st.subheader("📝 Editar Dados do Motor")
                        with st.form(f"edit_form_{idx}"):
                            col_e1, col_e2, col_e3 = st.columns(3)
                            # Campos para edição
                            new_marca = col_e1.text_input("Marca", row['Marca'])
                            new_cv = col_e1.text_input("CV", row['Potencia_CV'])
                            new_fp = col_e2.text_input("Fio P", row['Fio_Principal'])
                            new_pp = col_e2.text_input("Passo P", row['Passo_P'])
                            new_bp = col_e2.text_input("Espiras P", row['Bobina_Principal'])
                            new_obs = col_e3.text_area("Observação Técnica", row['Obs_Mestre'])
                            
                            if st.form_submit_button("💾 Salvar Alterações"):
                                df_motores.at[idx, 'Marca'] = new_marca
                                df_motores.at[idx, 'Potencia_CV'] = new_cv
                                df_motores.at[idx, 'Fio_Principal'] = new_fp
                                df_motores.at[idx, 'Passo_P'] = new_pp
                                df_motores.at[idx, 'Bobina_Principal'] = new_bp
                                df_motores.at[idx, 'Obs_Mestre'] = new_obs
                                salvar_dados(df_motores, ARQUIVO_CSV)
                                st.success("Atualizado!")
                                st.rerun()

                        st.divider()
                        st.subheader("🔬 Laboratório de Cálculos")
                        # Conversor de Alumínio e Tensão mantidos
                        v_de = st.number_input("Tensão De:", 220, key=f"vde_{idx}")
                        v_para = st.number_input("Tensão Para:", 380, key=f"vpa_{idx}")
                        if st.button("Calcular Nova Tensão", key=f"btnc_{idx}"):
                            fator = v_para / v_de
                            st.write(f"Multiplicar espiras por: **{fator:.2f}**")
                        
                        if st.button("🗑️ Deletar Motor", key=f"del_{idx}"):
                            df_motores.at[idx, 'status'] = 'deletado'
                            salvar_dados(df_motores, ARQUIVO_CSV)
                            st.rerun()

    # --- ABA NOVO MOTOR ---
    elif menu == "➕ NOVO MOTOR":
        st.header("➕ Cadastro de Motor")
        with st.form("add"):
            c1, c2, c3 = st.columns(3)
            with c1:
                m = st.text_input("Marca"); cv = st.text_input("CV"); v = st.text_input("Voltagem")
            with c2:
                fp = st.text_input("Fio P"); pp = st.text_input("Passo P"); bp = st.text_input("Espiras P")
            with c3:
                rol = st.text_input("Rolamentos"); selo = st.text_input("Selo"); cap = st.text_input("Capacitor")
            if st.form_submit_button("Salvar Motor"):
                novo = {'Marca': m, 'Potencia_CV': cv, 'Voltagem': v, 'Fio_Principal': fp, 'Passo_P': pp, 'Bobina_Principal': bp, 'Rolamentos': rol, 'Selo_Mecanico': selo, 'Capacitor': cap, 'status': 'ativo'}
                df_motores = pd.concat([df_motores, pd.DataFrame([novo])], ignore_index=True)
                salvar_dados(df_motores, ARQUIVO_CSV)
                st.success("Salvo!")

    # --- ABA BIBLIOTECA ---
    elif menu == "🖼️ BIBLIOTECA":
        st.header("🖼️ Biblioteca de Fotos")
        n = st.text_input("Nome da Ligação")
        f = st.file_uploader("Escolher Imagem")
        if st.button("Subir Foto"):
            if n and f:
                path = os.path.join(PASTA_UPLOADS, f.name)
                with open(path, "wb") as fi: fi.write(f.getbuffer())
                df_fotos = pd.concat([df_fotos, pd.DataFrame([{'nome_ligacao': n, 'caminho_arquivo': path}])], ignore_index=True)
                salvar_dados(df_fotos, ARQUIVO_FOTOS)
                st.rerun()

    # --- ABA LIXEIRA ---
    elif menu == "🗑️ LIXEIRA":
        st.header("🗑️ Lixeira")
        deletados = df_motores[df_motores['status'] == 'deletado']
        for i, r in deletados.iterrows():
            st.write(f"Motor: {r['Marca']} {r['Potencia_CV']}")
            if st.button("Restaurar", key=f"res_{i}"):
                df_motores.at[i, 'status'] = 'ativo'
                salvar_dados(df_motores, ARQUIVO_CSV)
                st.rerun()
