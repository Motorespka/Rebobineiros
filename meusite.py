import streamlit as st
import pandas as pd
import os
import re

# --- 1. CONFIGURAÇÕES DE ARQUIVOS ---
ARQUIVO_CSV = 'meubancodedados.csv'
ARQUIVO_FOTOS = 'biblioteca_fotos.csv'
PASTA_UPLOADS = 'uploads_ligacoes'

if not os.path.exists(PASTA_UPLOADS):
    os.makedirs(PASTA_UPLOADS)

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

# --- 4. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Pablo Motores Pro", layout="wide")

st.markdown("""
    <style>
    .stExpander { border: 1px solid #444 !important; border-radius: 8px !important; margin-bottom: 10px !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [data-baseweb="tab"] { background-color: #1e1e1e; border-radius: 4px; padding: 10px 20px; color: white; }
    .stTabs [aria-selected="true"] { background-color: #ff4b4b !important; }
    </style>
""", unsafe_allow_html=True)

COL_MOTORES = [
    'Marca', 'Potencia_CV', 'RPM', 'Voltagem', 'Amperagem', 'Polaridade', 
    'Bobina_Principal', 'Fio_Principal', 'Bobina_Auxiliar', 'Fio_Auxiliar', 
    'Tipo_Ligacao', 'Rolamentos', 'Eixo_X', 'Eixo_Y', 'Capacitor', 'status'
]
COL_FOTOS = ['nome_ligacao', 'caminho_arquivo']

if 'user_data' not in st.session_state: st.session_state['user_data'] = {'usuario': 'admin', 'perfil': 'admin'}

df_motores = carregar_dados(ARQUIVO_CSV, COL_MOTORES)
df_fotos = carregar_dados(ARQUIVO_FOTOS, COL_FOTOS)
lista_ligacoes = [""] + df_fotos['nome_ligacao'].tolist()

with st.sidebar:
    st.title("⚙️ PABLO MOTORES")
    menu = st.radio("Menu Principal", ["🔍 CONSULTA", "➕ NOVO MOTOR", "🖼️ BIBLIOTECA", "🗑️ LIXEIRA"])
    st.divider()
    # Adicionando um simulador público rápido no Sidebar
    st.subheader("🛠️ Dúvida Rápida")
    fio_rapido = st.text_input("Consultar bitola AWG:", placeholder="Ex: 18")
    if fio_rapido in TABELA_AWG_TECNICA:
        st.success(f"{fio_rapido} AWG = {TABELA_AWG_TECNICA[fio_rapido]} mm²")

# --- ABA CONSULTA ---
if menu == "🔍 CONSULTA":
    st.header("🔍 Banco de Dados Técnico")
    busca = st.text_input("Filtrar motor...", placeholder="Marca, CV, RPM ou Fio...")
    
    df_f = df_motores[df_motores['status'] != 'deletado']
    if busca:
        df_f = df_f[df_f.apply(lambda r: r.astype(str).str.contains(busca, case=False).any(), axis=1)]

    for idx, row in df_f.iterrows():
        area_ref = calcular_area_mm2(row['Fio_Principal'])
        label = f"📦 {row['Marca']} | {row['Potencia_CV']} CV | {row['RPM']} RPM"
        
        with st.expander(label):
            # DIVISÃO POR NÍVEIS DE ACESSO (TABS)
            tab1, tab2, tab3 = st.tabs(["📋 DADOS GERAIS", "⚙️ ÁREA TÉCNICA", "👑 PAINEL CHEFE"])
            
            with tab1:
                col1, col2, col3 = st.columns([1, 1, 1.2])
                with col1:
                    st.markdown("#### ⚡ Elétrica")
                    st.write(f"**Fio Principal:** `{row['Fio_Principal']}`")
                    st.write(f"**Amperagem:** {row['Amperagem']} A")
                    st.write(f"**Capacitor:** {row['Capacitor']}")
                with col2:
                    st.markdown("#### 🔧 Mecânica")
                    st.write(f"**Rolamentos:** {row['Rolamentos']}")
                    st.write(f"**Eixos:** {row['Eixo_X']} / {row['Eixo_Y']}")
                with col3:
                    tipo = row['Tipo_Ligacao']
                    if tipo and tipo in df_fotos['nome_ligacao'].values:
                        img_path = df_fotos[df_fotos['nome_ligacao'] == tipo]['caminho_arquivo'].values[0]
                        st.image(img_path, use_container_width=True)
                    else: st.caption("Sem esquema.")

            with tab2:
                st.subheader("Mudança de Características e Cálculos")
                c_bt1, c_bt2, c_bt3 = st.columns(3)
                if c_bt1.button("🔄 SIMULAR BITOLAS", key=f"c_{idx}"):
                    st.session_state[f"sc_{idx}"] = not st.session_state.get(f"sc_{idx}", False)
                
                # NOVO: Calculadora de Tensão (Exclusivo Profissional)
                with st.expander("🔌 Conversor de Voltagem (Ex: 220V -> 380V)"):
                    v_orig = st.number_input("Tensão Original (V)", value=220, key=f"vo_{idx}")
                    v_nova = st.number_input("Nova Tensão desejada (V)", value=380, key=f"vn_{idx}")
                    if v_orig > 0:
                        fator = v_nova / v_orig
                        st.info(f"O novo enrolamento deve ter **{fator:.2f}x** mais espiras.")
                        st.warning(f"A bitola do fio deve ser reduzida para suportar a nova tensão.")

                if st.session_state.get(f"sc_{idx}"):
                    # Lógica de cálculo avançado que você já tinha
                    fio_teste = st.text_input("Fio para teste (Ex: 2x18):", key=f"input_t_{idx}")
                    if fio_teste:
                        area_n = calcular_area_mm2(fio_teste)
                        diff = ((area_n - area_ref) / area_ref) * 100 if area_ref > 0 else 0
                        m1, m2, m3 = st.columns(3)
                        m1.metric("Diferença", f"{diff:.1f}%")
                        m2.metric("Aquecimento", "Normal" if diff >= -3 else "Alto")
                        m3.metric("Torque", "Original" if diff >= -2 else "Perda")

            with tab3:
                st.subheader("Análise de Custo e Precisão (Admin)")
                preco_cobre = st.number_input("Preço do Cobre (Kg)", value=65.0, key=f"pr_{idx}")
                peso_est = st.number_input("Peso estimado de cobre (Kg)", value=1.5, key=f"pe_{idx}")
                st.metric("Custo estimado de material", f"R$ {preco_cobre * peso_est:.2f}")
                
                st.divider()
                if st.button("📝 EDITAR MOTOR", key=f"e_{idx}", use_container_width=True):
                    st.session_state[f"se_{idx}"] = not st.session_state.get(f"se_{idx}", False)
                if st.button("🗑️ EXCLUIR REGISTRO", key=f"d_{idx}", use_container_width=True):
                    df_motores.at[idx, 'status'] = 'deletado'
                    salvar_dados(df_motores, ARQUIVO_CSV); st.rerun()

            # --- FORMULÁRIO DE EDIÇÃO (Abaixo das abas se ativado) ---
            if st.session_state.get(f"se_{idx}"):
                with st.form(f"f_ed_{idx}"):
                    st.write("### Modo Edição Master")
                    ed_fp = st.text_input("Fio Principal", value=row['Fio_Principal'])
                    ed_amp = st.text_input("Amperagem", value=row['Amperagem'])
                    if st.form_submit_button("Confirmar Alterações"):
                        df_motores.at[idx, 'Fio_Principal'] = ed_fp
                        df_motores.at[idx, 'Amperagem'] = ed_amp
                        salvar_dados(df_motores, ARQUIVO_CSV); st.rerun()

# --- ABA NOVO MOTOR ---
elif menu == "➕ NOVO MOTOR":
    st.header("➕ Cadastro de Novo Motor")
    with st.form("add_motor"):
        c1, c2, c3 = st.columns(3)
        with c1:
            m = st.text_input("Marca"); cv = st.text_input("CV"); r = st.text_input("RPM")
            v = st.text_input("Voltagem"); a = st.text_input("Amperagem"); pol = st.text_input("Pólos")
        with c2:
            fp = st.text_input("Fio Principal"); gp = st.text_input("Grupo Principal")
            fa = st.text_input("Fio Auxiliar"); ga = st.text_input("Grupo Auxiliar")
            lig = st.selectbox("Ligação", lista_ligacoes)
        with c3:
            rol = st.text_input("Rolamentos"); ex = st.text_input("Eixo X"); ey = st.text_input("Eixo Y"); cap = st.text_input("Capacitor")
        
        if st.form_submit_button("💾 SALVAR DADOS NO SISTEMA"):
            novo = {'Marca': m, 'Potencia_CV': cv, 'RPM': r, 'Voltagem': v, 'Amperagem': a, 'Polaridade': pol,
                    'Fio_Principal': fp, 'Bobina_Principal': gp, 'Fio_Auxiliar': fa, 'Bobina_Auxiliar': ga,
                    'Tipo_Ligacao': lig, 'Rolamentos': rol, 'Eixo_X': ex, 'Eixo_Y': ey, 'Capacitor': cap, 'status': 'ativo'}
            df_motores = pd.concat([df_motores, pd.DataFrame([novo])], ignore_index=True)
            salvar_dados(df_motores, ARQUIVO_CSV); st.success("Motor salvo com sucesso!"); st.rerun()

elif menu == "🖼️ BIBLIOTECA":
    st.header("🖼️ Biblioteca de Esquemas")
    with st.form("lib"):
        n = st.text_input("Nome"); f = st.file_uploader("Foto", type=['png','jpg','jpeg'])
        if st.form_submit_button("Subir Foto"):
            if n and f:
                path = os.path.join(PASTA_UPLOADS, f.name)
                with open(path, "wb") as fi: fi.write(f.getbuffer())
                df_f_new = pd.DataFrame([{'nome_ligacao': n, 'caminho_arquivo': path}])
                df_fotos = pd.concat([df_fotos, df_f_new], ignore_index=True)
                salvar_dados(df_fotos, ARQUIVO_FOTOS); st.rerun()
    st.divider()
    cols = st.columns(4)
    for i, r in df_fotos.iterrows():
        with cols[i % 4]:
            st.image(r['caminho_arquivo'], use_container_width=True)
            st.caption(r['nome_ligacao'])
            if st.button("Remover", key=f"rm_{i}"):
                df_fotos = df_fotos.drop(i); salvar_dados(df_fotos, ARQUIVO_FOTOS); st.rerun()

elif menu == "🗑️ LIXEIRA":
    st.header("🗑️ Lixeira")
    deletados = df_motores[df_motores['status'] == 'deletado']
    for i, r in deletados.iterrows():
        col_l1, col_l2 = st.columns([3, 1])
        col_l1.write(f"Motor: {r['Marca']} {r['Potencia_CV']} CV")
        if col_l2.button("Restaurar", key=f"res_{i}"):
            df_motores.at[i, 'status'] = 'ativo'; salvar_dados(df_motores, ARQUIVO_CSV); st.rerun()
