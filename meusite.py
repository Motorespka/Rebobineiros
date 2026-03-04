import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime

# --- 1. CONFIGURAÇÕES DE ARQUIVOS E PASTAS ---
ARQUIVO_CSV = 'meubancodedados.csv'
ARQUIVO_FOTOS = 'biblioteca_fotos.csv'
PASTA_UPLOADS = 'uploads_ligacoes'

if not os.path.exists(PASTA_UPLOADS):
    os.makedirs(PASTA_UPLOADS)

# --- 2. BANCO TÉCNICO AWG (DA SUA IMAGEM) ---
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

# --- 3. FUNÇÕES DE CÁLCULO E DADOS ---
def carregar_dados(arq):
    if not os.path.exists(arq): return pd.DataFrame()
    return pd.read_csv(arq, sep=';', encoding='utf-8-sig', dtype=str)

def salvar_dados(df, arq):
    df.to_csv(arq, index=False, sep=';', encoding='utf-8-sig')

def calcular_area_mm2(texto_fio):
    try:
        if not texto_fio or str(texto_fio) == "nan": return 0.0
        texto = str(texto_fio).lower().replace('awg', '').strip()
        if 'x' in texto:
            partes = texto.split('x')
            qtd = int(re.findall(r'\d+', partes[0])[0])
            bitola = partes[1].strip()
            return qtd * TABELA_AWG_TECNICA.get(bitola, 0.0)
        bitolas = re.findall(r'\d+', texto)
        return TABELA_AWG_TECNICA.get(bitolas[0], 0.0) if bitolas else 0.0
    except: return 0.0

def gerar_opcoes_calculadas(area_alvo):
    sugestoes = []
    if area_alvo <= 0: return []
    for bitola, area_u in TABELA_AWG_TECNICA.items():
        for qtd in range(1, 5):
            area_sim = area_u * qtd
            diff = ((area_sim - area_alvo) / area_alvo) * 100
            if -12.0 <= diff <= 12.0:
                if abs(diff) <= 2.5: cor, status = "#2ecc71", "SEGURA (Verde)"
                elif 2.5 < diff <= 7.5 or -7.5 <= diff < -2.5: cor, status = "#f1c40f", "ALERTA (Amarelo)"
                else: cor, status = "#e74c3c", "ARRISCADA (Vermelho)"
                sugestoes.append({'fio': f"{qtd}x{bitola} AWG", 'diff': diff, 'cor': cor, 'status': status})
    return sorted(sugestoes, key=lambda x: abs(x['diff']))

# --- 4. INTERFACE PRINCIPAL ---
st.set_page_config(page_title="Pablo Motores Pro", layout="wide")

if 'user_data' not in st.session_state: st.session_state['user_data'] = None

# Lógica de Login (Substitua pela sua se necessário)
if not st.session_state['user_data']:
    st.title("🔐 Acesso Pablo Motores")
    with st.form("login"):
        u = st.text_input("Usuário")
        p = st.text_input("Senha", type="password")
        if st.form_submit_button("Entrar"):
            if u == "admin" and p == "pablo2026":
                st.session_state['user_data'] = {'usuario': u, 'perfil': 'admin'}
                st.rerun()
            else: st.error("Incorreto")
else:
    user = st.session_state['user_data']
    e_admin = (user['perfil'] == 'admin')
    df_motores = carregar_dados(ARQUIVO_CSV)
    df_fotos = carregar_dados(ARQUIVO_FOTOS)
    lista_ligacoes = ["Nenhuma"] + df_fotos['nome_ligacao'].tolist() if not df_fotos.empty else ["Nenhuma"]

    with st.sidebar:
        st.header(f"Olá, {user['usuario'].upper()}")
        menu = ["🔍 CONSULTAR", "➕ NOVO MOTOR", "🖼️ BIBLIOTECA DE LIGAÇÕES", "🗑️ LIXEIRA"]
        escolha = st.radio("Selecione:", menu if e_admin else ["🔍 CONSULTAR"])
        if st.button("Sair"):
            st.session_state['user_data'] = None
            st.rerun()

    # --- ABA: BIBLIOTECA (NOVA) ---
    if escolha == "🖼️ BIBLIOTECA DE LIGAÇÕES":
        st.title("🖼️ Biblioteca de Esquemas de Ligação")
        with st.form("form_biblioteca"):
            nome_lig = st.text_input("Nome da Ligação (ex: Série, Paralelo 12 Cabos)")
            arq_foto = st.file_uploader("Upload da Imagem", type=['png', 'jpg', 'jpeg'])
            if st.form_submit_button("Salvar na Biblioteca"):
                if nome_lig and arq_foto:
                    caminho = os.path.join(PASTA_UPLOADS, arq_foto.name)
                    with open(caminho, "wb") as f: f.write(arq_foto.getbuffer())
                    nova_foto = {'nome_ligacao': nome_lig, 'caminho_arquivo': caminho}
                    df_fotos = pd.concat([df_fotos, pd.DataFrame([nova_foto])], ignore_index=True)
                    salvar_dados(df_fotos, ARQUIVO_FOTOS)
                    st.success("Salvo!"); st.rerun()
        
        if not df_fotos.empty:
            for i, r in df_fotos.iterrows():
                with st.expander(f"Esquema: {r['nome_ligacao']}"):
                    st.image(r['caminho_arquivo'], width=300)
                    if st.button("Excluir Esquema", key=f"del_lib_{i}"):
                        df_fotos = df_fotos.drop(i); salvar_dados(df_fotos, ARQUIVO_FOTOS); st.rerun()

    # --- ABA: CONSULTA (COMPLETA) ---
    elif escolha == "🔍 CONSULTAR":
        st.title("🔍 Consulta Técnica")
        busca = st.text_input("Buscar motor...")
        if not df_motores.empty:
            if not e_admin: df_motores = df_motores[df_motores.get('status', 'ativo') != 'deletado']
            df_f = df_motores[df_motores.apply(lambda row: row.astype(str).str.contains(busca, case=False).any(), axis=1)] if busca else df_motores

            for idx, row in df_f.iterrows():
                area_base = calcular_area_mm2(row.get('Fio_Principal'))
                with st.expander(f"📦 {row.get('Marca')} | {row.get('Potencia_CV')} CV | {row.get('RPM')} RPM"):
                    c1, c2, c3 = st.columns([1.5, 1, 1])
                    with c1:
                        st.write(f"**Fio Principal:** {row.get('Fio_Principal')} ({area_base:.3f} mm²)")
                        st.write(f"**Amperagem:** {row.get('Amperagem')} | **Voltagem:** {row.get('Voltagem')}")
                        st.write(f"**Pólos:** {row.get('Polaridade')} | **Capacitor:** {row.get('Capacitor')}")
                        st.write(f"**Rolamentos:** {row.get('Rolamentos')} | **Eixos:** {row.get('Eixo_X')}/{row.get('Eixo_Y')}")
                    
                    with c2:
                        st.write(f"**Ligação Selecionada:** {row.get('Tipo_Ligacao', 'Nenhuma')}")
                        tipo = row.get('Tipo_Ligacao')
                        if tipo in df_fotos['nome_ligacao'].values:
                            img_p = df_fotos[df_fotos['nome_ligacao'] == tipo]['caminho_arquivo'].values[0]
                            st.image(img_p, caption=f"Esquema {tipo}")
                        
                    
                    with c3:
                        if st.button("🔄 CALCULAR ALTERAÇÃO", key=f"btn_alt_{idx}"):
                            st.session_state[f"aba_alt_{idx}"] = not st.session_state.get(f"aba_alt_{idx}", False)
                        if e_admin:
                            if st.button("📝 EDITAR MOTOR", key=f"btn_ed_{idx}"):
                                st.session_state[f"aba_ed_{idx}"] = not st.session_state.get(f"aba_ed_{idx}", False)
                            if st.button("🗑️ EXCLUIR", key=f"btn_del_{idx}"):
                                df_motores.at[idx, 'status'] = 'deletado'; salvar_dados(df_motores, ARQUIVO_CSV); st.rerun()

                    if st.session_state.get(f"aba_alt_{idx}"):
                        st.markdown("---")
                        opcoes = gerar_opcoes_calculadas(area_base)
                        for op in opcoes[:10]:
                            st.markdown(f"<div style='border-left:10px solid {op['cor']}; background:#f8f9fa; padding:10px; margin-bottom:5px; color:black;'><b>{op['fio']}</b> ({op['diff']:.2f}%) - {op['status']}</div>", unsafe_allow_html=True)

                    if e_admin and st.session_state.get(f"aba_ed_{idx}"):
                        with st.form(f"form_ed_{idx}"):
                            st.info("Editando Motor")
                            # TODOS OS CAMPOS PARA NÃO DIMINUIR O CÓDIGO
                            ed_m = st.text_input("Marca", value=row.get('Marca'))
                            ed_cv = st.text_input("CV", value=row.get('Potencia_CV'))
                            ed_fp = st.text_input("Fio Principal", value=row.get('Fio_Principal'))
                            ed_lig = st.selectbox("Ligação", lista_ligacoes, index=lista_ligacoes.index(row.get('Tipo_Ligacao', 'Nenhuma')) if row.get('Tipo_Ligacao') in lista_ligacoes else 0)
                            ed_amp = st.text_input("Amperagem", value=row.get('Amperagem'))
                            ed_rol = st.text_input("Rolamentos", value=row.get('Rolamentos'))
                            ed_ex = st.text_input("Eixo X", value=row.get('Eixo_X'))
                            if st.form_submit_button("✅ SALVAR E FECHAR"):
                                df_motores.at[idx, 'Marca'] = ed_m
                                df_motores.at[idx, 'Potencia_CV'] = ed_cv
                                df_motores.at[idx, 'Fio_Principal'] = ed_fp
                                df_motores.at[idx, 'Tipo_Ligacao'] = ed_lig
                                df_motores.at[idx, 'Amperagem'] = ed_amp
                                df_motores.at[idx, 'Rolamentos'] = ed_rol
                                df_motores.at[idx, 'Eixo_X'] = ed_ex
                                salvar_dados(df_motores, ARQUIVO_CSV)
                                st.session_state[f"aba_ed_{idx}"] = False; st.rerun()

    # --- ABA: NOVO MOTOR (COMPLETO) ---
    elif escolha == "➕ NOVO MOTOR":
        st.title("➕ Cadastrar Novo Motor")
        with st.form("n_mot"):
            c1, c2, c3 = st.columns(3)
            with c1:
                m = st.text_input("Marca"); cv = st.text_input("CV"); r = st.text_input("RPM")
                v = st.text_input("Voltagem"); a = st.text_input("Amperagem"); pol = st.text_input("Pólos")
            with c2:
                fp = st.text_input("Fio Principal"); gp = st.text_input("Grupo Principal")
                fa = st.text_input("Fio Auxiliar"); ga = st.text_input("Grupo Auxiliar")
                lig = st.selectbox("Esquema de Ligação", lista_ligacoes)
            with c3:
                rol = st.text_input("Rolamentos"); ex_x = st.text_input("Eixo X"); ex_y = st.text_input("Eixo Y")
                cap = st.text_input("Capacitor")
            
            if st.form_submit_button("SALVAR MOTOR"):
                novo = {'Marca': m, 'Potencia_CV': cv, 'RPM': r, 'Voltagem': v, 'Amperagem': a, 'Polaridade': pol,
                        'Fio_Principal': fp, 'Bobina_Principal': gp, 'Fio_Auxiliar': fa, 'Bobina_Auxiliar': ga,
                        'Tipo_Ligacao': lig, 'Rolamentos': rol, 'Eixo_X': ex_x, 'Eixo_Y': ex_y, 'Capacitor': cap, 'status': 'ativo'}
                df_motores = pd.concat([df_motores, pd.DataFrame([novo])], ignore_index=True)
                salvar_dados(df_motores, ARQUIVO_CSV); st.success("Cadastrado!"); st.rerun()

    # --- ABA: LIXEIRA ---
    elif escolha == "🗑️ LIXEIRA":
        st.title("🗑️ Lixeira")
        deletados = df_motores[df_motores.get('status') == 'deletado']
        for i, r in deletados.iterrows():
            st.error(f"{r['Marca']} - {r['Potencia_CV']} CV")
            if st.button(f"Restaurar #{i}"):
                df_motores.at[i, 'status'] = 'ativo'; salvar_dados(df_motores, ARQUIVO_CSV); st.rerun()
