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
    .calc-box { background-color: #1e1e1e; padding: 15px; border-radius: 10px; border-left: 5px solid #007bff; border: 1px solid #333; }
    .badge { padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 12px; }
    </style>
""", unsafe_allow_html=True)

COL_MOTORES = [
    'Marca', 'Potencia_CV', 'RPM', 'Voltagem', 'Amperagem', 'Polaridade', 
    'Bobina_Principal', 'Fio_Principal', 'Bobina_Auxiliar', 'Fio_Auxiliar', 
    'Tipo_Ligacao', 'Rolamentos', 'Eixo_X', 'Eixo_Y', 'Capacitor', 'status'
]
df_motores = carregar_dados(ARQUIVO_CSV, COL_MOTORES)
df_fotos = carregar_dados(ARQUIVO_FOTOS, ['nome_ligacao', 'caminho_arquivo'])
lista_ligacoes = [""] + df_fotos['nome_ligacao'].tolist()

with st.sidebar:
    st.title("⚙️ PABLO MOTORES")
    menu = st.radio("Menu Principal", ["🔍 CONSULTA", "➕ NOVO MOTOR", "🖼️ BIBLIOTECA", "🗑️ LIXEIRA"])
    st.divider()
    st.subheader("📏 Consulta AWG")
    fio_q = st.text_input("Bitola (ex: 20):")
    if fio_q in TABELA_AWG_TECNICA:
        st.success(f"**{fio_q} AWG** = {TABELA_AWG_TECNICA[fio_q]} mm²")

# --- ABA CONSULTA ---
if menu == "🔍 CONSULTA":
    st.header("🔍 Banco de Dados Técnico")
    busca = st.text_input("Filtrar motor (Marca, CV, RPM...)")
    
    df_f = df_motores[df_motores['status'] != 'deletado']
    if busca:
        df_f = df_f[df_f.apply(lambda r: r.astype(str).str.contains(busca, case=False).any(), axis=1)]

    for idx, row in df_f.iterrows():
        area_ref = calcular_area_mm2(row['Fio_Principal'])
        
        label = f"📦 {row['Marca']} | {row['Potencia_CV']} CV | {row['RPM']} RPM"
        
        with st.expander(label):
            tab1, tab2, tab3 = st.tabs(["📋 DADOS GERAIS", "⚙️ ÁREA TÉCNICA", "👑 PAINEL CHEFE"])
            
            with tab1:
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.markdown("#### ⚡ Elétrica")
                    st.write(f"**Fio Principal:** `{row['Fio_Principal']}`")
                    st.write(f"**Fio Auxiliar:** {row['Fio_Auxiliar']}")
                    st.write(f"**Amperagem:** {row['Amperagem']}")
                    st.write(f"**Voltagem:** {row['Voltagem']} V")
                    st.write(f"**Pólos:** {row['Polaridade']}")
                with c2:
                    st.markdown("#### 🔧 Mecânica e Grupos")
                    # Lógica de exibição de Passos e Espiras
                    conteudo_bobina = str(row['Bobina_Principal'])
                    if "PASSOS:" in conteudo_bobina:
                        st.info(conteudo_bobina.replace(" | ", "\n\n"))
                    else:
                        st.write(f"**Grupos (P/A):** {row['Bobina_Principal']} / {row['Bobina_Auxiliar']}")
                    
                    st.write(f"**Capacitor:** {row['Capacitor']}")
                    st.write(f"**Rolamentos:** {row['Rolamentos']}")
                    st.write(f"**Eixo:** {row['Eixo_X']}mm x {row['Eixo_Y']}mm")
                with c3:
                    st.markdown("#### 🖼️ Esquema")
                    tipo = row['Tipo_Ligacao']
                    if tipo and tipo in df_fotos['nome_ligacao'].values:
                        img_path = df_fotos[df_fotos['nome_ligacao'] == tipo]['caminho_arquivo'].values[0]
                        st.image(img_path, use_container_width=True)
                    else: st.caption("Sem esquema cadastrado.")

            with tab2:
                st.subheader("🛠️ Cálculos de Rebobinagem")
                with st.container(border=True):
                    st.markdown("### 🔌 Conversor de Tensão e Bitola")
                    v1, v2 = st.columns(2)
                    ten_orig = v1.number_input("Tensão Original (V):", value=220.0, key=f"v1_{idx}")
                    ten_nova = v2.number_input("Nova Tensão (V):", value=380.0, key=f"v2_{idx}")
                    
                    fator = ten_nova / ten_orig if ten_orig > 0 else 1
                    
                    # Extração de espiras numéricas para cálculo
                    espiras_detectadas = re.findall(r'\d+', str(row['Bobina_Principal']))
                    
                    res1, res2 = st.columns(2)
                    with res1:
                        if espiras_detectadas:
                            novas = [str(round(int(e) * fator)) for e in espiras_detectadas]
                            st.metric("Novas Espiras (Aprox.)", f"{'/'.join(novas)}")
                        st.caption(f"Fator de correção aplicado: {fator:.2f}x")
                    
                    with res2:
                        nova_secao = area_ref / fator
                        st.metric("Nova Seção de Fio", f"{nova_secao:.4f} mm²")

                    st.markdown("#### 💡 Sugestões de Bitola AWG:")
                    sugest_awg = gerar_sugestoes(nova_secao)
                    if sugest_awg:
                        cols_sug = st.columns(3)
                        for i, s in enumerate(sugest_awg[:3]):
                            cols_sug[i].markdown(f"<div style='background:{s['cor']};color:white;padding:10px;border-radius:5px;text-align:center'><b>{s['fio']}</b><br>{s['status']}</div>", unsafe_allow_html=True)

            with tab3:
                st.subheader("📝 Edição Técnica")
                with st.form(f"edit_form_{idx}"):
                    ed1, ed2, ed3 = st.columns(3)
                    with ed1:
                        m_m = st.text_input("Marca", row['Marca'])
                        m_p = st.text_input("Potência CV", row['Potencia_CV'])
                        m_v = st.text_input("Voltagem", row['Voltagem'])
                    with ed2:
                        m_fp = st.text_input("Fio Principal", row['Fio_Principal'])
                        m_bp = st.text_input("Passos e Espiras", row['Bobina_Principal'])
                    with ed3:
                        m_cap = st.text_input("Capacitor", row['Capacitor'])
                        m_lig = st.selectbox("Ligação", lista_ligacoes, index=lista_ligacoes.index(row['Tipo_Ligacao']) if row['Tipo_Ligacao'] in lista_ligacoes else 0)
                    
                    if st.form_submit_button("💾 ATUALIZAR DADOS"):
                        df_motores.loc[idx, ['Marca', 'Potencia_CV', 'Voltagem', 'Fio_Principal', 'Bobina_Principal', 'Capacitor', 'Tipo_Ligacao']] = [m_m, m_p, m_v, m_fp, m_bp, m_cap, m_lig]
                        salvar_dados(df_motores, ARQUIVO_CSV)
                        st.success("Dados salvos!")
                        st.rerun()
                
                if st.button("🗑️ EXCLUIR", key=f"del_{idx}"):
                    df_motores.at[idx, 'status'] = 'deletado'
                    salvar_dados(df_motores, ARQUIVO_CSV)
                    st.rerun()

elif menu == "➕ NOVO MOTOR":
    st.header("➕ Cadastro de Novo Motor")
    
    with st.form("novo_motor"):
        c1, c2, c3 = st.columns(3)
        with c1:
            m = st.text_input("Marca"); cv = st.text_input("CV"); rpm = st.text_input("RPM")
            vol = st.text_input("Voltagem (V)"); amp = st.text_input("Amperagem (A)"); pol = st.text_input("Pólos")
        with c2:
            f_p = st.text_input("Fio Principal (ex: 2x17)")
            passos = st.text_input("Passos (ex: 6,8,10,12)")
            espiras = st.text_input("Espiras (ex: 18,22,28,32)")
            f_a = st.text_input("Fio Auxiliar"); g_a = st.text_input("Grupo Auxiliar")
            lig = st.selectbox("Ligação", lista_ligacoes)
        with c3:
            rol = st.text_input("Rolamentos"); ex_x = st.text_input("Eixo X"); ex_y = st.text_input("Eixo Y"); cap = st.text_input("Capacitor")
        
        if st.form_submit_button("✅ SALVAR MOTOR NO BANCO"):
            # Salvando passos e espiras formatados
            bobina_formatada = f"PASSOS: {passos} | ESPIRAS: {espiras}"
            novo = {'Marca': m, 'Potencia_CV': cv, 'RPM': rpm, 'Voltagem': vol, 'Amperagem': amp, 'Polaridade': pol,
                    'Fio_Principal': f_p, 'Bobina_Principal': bobina_formatada, 'Fio_Auxiliar': f_a, 'Bobina_Auxiliar': g_a,
                    'Tipo_Ligacao': lig, 'Rolamentos': rol, 'Eixo_X': ex_x, 'Eixo_Y': ex_y, 'Capacitor': cap, 'status': 'ativo'}
            df_motores = pd.concat([df_motores, pd.DataFrame([novo])], ignore_index=True)
            salvar_dados(df_motores, ARQUIVO_CSV); st.success("Motor cadastrado!"); st.rerun()

elif menu == "🖼️ BIBLIOTECA":
    st.header("🖼️ Biblioteca de Esquemas")
    with st.form("upload_foto"):
        nome_f = st.text_input("Nome da Ligação"); arq_f = st.file_uploader("Arquivo", type=['png','jpg','jpeg'])
        if st.form_submit_button("📤 SUBIR FOTO"):
            if nome_f and arq_f:
                path = os.path.join(PASTA_UPLOADS, arq_f.name)
                with open(path, "wb") as f: f.write(arq_f.getbuffer())
                df_fotos = pd.concat([df_fotos, pd.DataFrame([{'nome_ligacao': nome_f, 'caminho_arquivo': path}])], ignore_index=True)
                salvar_dados(df_fotos, ARQUIVO_FOTOS); st.rerun()
    st.divider()
    cols = st.columns(4)
    for i, r in df_fotos.iterrows():
        with cols[i % 4]:
            st.image(r['caminho_arquivo'], use_container_width=True)
            st.caption(r['nome_ligacao'])
            if st.button("Remover", key=f"fdel_{i}"):
                df_fotos = df_fotos.drop(i); salvar_dados(df_fotos, ARQUIVO_FOTOS); st.rerun()

elif menu == "🗑️ LIXEIRA":
    st.header("🗑️ Lixeira")
    deletados = df_motores[df_motores['status'] == 'deletado']
    for idx, r in deletados.iterrows():
        col_r1, col_r2 = st.columns([4, 1])
        col_r1.write(f"Motor: {r['Marca']} - {r['Potencia_CV']} CV")
        if col_r2.button("Restaurar", key=f"rest_{idx}"):
            df_motores.at[idx, 'status'] = 'ativo'
            salvar_dados(df_motores, ARQUIVO_CSV)
            st.rerun()
