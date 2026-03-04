import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime, timedelta

# --- 1. BANCO DE DADOS TÉCNICO (CONFORME SUA IMAGEM) ---
# Tabela de Conversão AWG para mm²
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

# --- 2. FUNÇÕES DE CÁLCULO DE ÁREA E RISCO ---
def calcular_area_mm2(texto_fio):
    """Converte strings como '2x18' ou '1x20' na área total em mm²"""
    try:
        if not texto_fio or str(texto_fio) == "None": return 0.0
        texto = str(texto_fio).lower().replace('awg', '').strip()
        if 'x' in texto:
            qtd, bitola = texto.split('x')
            return int(re.findall(r'\d+', qtd)[0]) * TABELA_AWG_TECNICA.get(bitola.strip(), 0.0)
        bitola = re.findall(r'\d+', texto)[0]
        return TABELA_AWG_TECNICA.get(bitola, 0.0)
    except: return 0.0

def definir_status_risco(area_orig, area_sim):
    if area_orig <= 0: return "#7f8c8d", "DADOS INCOMPLETOS", "Cadastre o fio original para calcular."
    diff = ((area_sim - area_orig) / area_orig) * 100
    
    if abs(diff) <= 2.5:
        return "#2ecc71", "EXCELENTE (VERDE)", "Troca segura. O motor manterá o desempenho original."
    elif 2.5 < diff <= 7.0:
        return "#f1c40f", "BOM / ALERTA (AMARELO)", "Motor terá leve ganho de força, mas o fio ocupará mais espaço."
    elif -7.0 <= diff < -2.5:
        return "#e67e22", "REGULAR / PERDA (LARANJA)", "Motor perderá torque e poderá aquecer acima do normal."
    else:
        return "#e74c3c", "PERIGOSO / RUIM (VERMELHO)", "Risco de queima! Diferença de bitola muito alta."

# --- 3. GESTÃO DE DADOS ---
ARQUIVO_CSV = 'meubancodedados.csv'

def carregar_dados():
    if not os.path.exists(ARQUIVO_CSV): return pd.DataFrame()
    df = pd.read_csv(ARQUIVO_CSV, sep=';', encoding='utf-8-sig', dtype=str)
    df.columns = df.columns.str.strip()
    return df

def salvar_dados(df):
    df.to_csv(ARQUIVO_CSV, index=False, sep=';', encoding='utf-8-sig')

# --- 4. INTERFACE ---
st.set_page_config(page_title="Pablo Motores | Gestão Técnica", layout="wide")

if 'user_data' in st.session_state and st.session_state['user_data']:
    user = st.session_state['user_data']
    e_admin = user.get('perfil') == 'admin'
    
    escolha = st.sidebar.radio("Navegação:", ["🔍 CONSULTA", "➕ NOVO CADASTRO", "🗑️ LIXEIRA"])

    if escolha == "🔍 CONSULTA":
        st.title("🔍 Consulta de Cálculos")
        df = carregar_dados()
        busca = st.text_input("Pesquisar por Marca, CV ou Dados Técnicos...")

        if not df.empty:
            if not e_admin: df = df[df.get('status', 'ativo') != 'deletado']
            df_f = df[df.apply(lambda row: row.astype(str).str.contains(busca, case=False).any(), axis=1)] if busca else df

            for idx, row in df_f.iterrows():
                area_base = calcular_area_mm2(row.get('Fio_Principal'))
                
                with st.expander(f"📦 {row.get('Marca')} | {row.get('Potencia_CV')} CV | {row.get('RPM')} RPM"):
                    col_f, col_s = st.columns(2)
                    
                    with col_f:
                        st.subheader("📊 Dados de Fábrica")
                        st.write(f"**Fio Original:** {row.get('Fio_Principal')}")
                        st.write(f"**Área do Cobre:** {area_base:.3f} mm²")
                        st.write(f"**Esquema:** {row.get('Esquema_Marcado', 'N/A')}")
                        
                        if e_admin:
                            if st.button("🗑️ Excluir", key=f"del_{idx}"):
                                df.at[idx, 'status'] = 'deletado'
                                df.at[idx, 'data_del'] = datetime.now().strftime('%Y-%m-%d')
                                salvar_dados(df); st.rerun()

                    with col_s:
                        st.subheader("🛠️ Simulador de Alteração")
                        c_q, c_b = st.columns(2)
                        q_sim = c_q.number_input("Qtd Fios", 1, 6, 1, key=f"q_{idx}")
                        b_sim = c_b.selectbox("Bitola AWG", list(TABELA_AWG_TECNICA.keys()), index=15, key=f"b_{idx}")
                        
                        area_sim = q_sim * TABELA_AWG_TECNICA[b_sim]
                        cor, status, msg = definir_status_risco(area_base, area_sim)
                        
                        st.markdown(f"""
                            <div style="background-color: {cor}; padding: 15px; border-radius: 8px; color: white; text-align: center;">
                                <h3 style="margin:0;">{status}</h3>
                                <p style="margin:5px 0;">Área Calculada: {area_sim:.3f} mm²</p>
                                <hr style="border: 0.5px solid rgba(255,255,255,0.3);">
                                <small>{msg}</small>
                            </div>
                        """, unsafe_allow_html=True)

    # --- ABA: NOVO CADASTRO (COM OS CAMPOS SOLICITADOS) ---
    elif escolha == "➕ NOVO CADASTRO" and e_admin:
        st.title("➕ Cadastrar Novo Motor")
        with st.form("form_novo"):
            c1, c2, c3 = st.columns(3)
            with c1:
                marca = st.text_input("Marca"); cv = st.text_input("Potência (CV)"); rpm = st.text_input("RPM")
                pol = st.text_input("Polaridade"); volt = st.text_input("Voltagem"); amp = st.text_input("Amperagem")
            with c2:
                g_p = st.text_input("Grupo Principal"); f_p = st.text_input("Fio Principal (Ex: 2x18)")
                rol = st.text_input("Rolamentos"); ex_x = st.text_input("Eixo X")
            with c3:
                g_a = st.text_input("Grupo Auxiliar"); f_a = st.text_input("Fio Auxiliar")
                cap = st.text_input("Capacitor"); ex_y = st.text_input("Eixo Y")
            
            if st.form_submit_button("SALVAR NO BANCO DE DADOS"):
                novo = {
                    'Marca': marca, 'Potencia_CV': cv, 'RPM': rpm, 'Polaridade': pol, 'Voltagem': volt,
                    'Amperagem': amp, 'Bobina_Principal': g_p, 'Fio_Principal': f_p, 'Rolamentos': rol,
                    'Eixo_X': ex_x, 'Bobina_Auxiliar': g_a, 'Fio_Auxiliar': f_a, 'Capacitor': cap,
                    'Eixo_Y': ex_y, 'status': 'ativo', 'data_del': ''
                }
                df_novo = pd.concat([carregar_dados(), pd.DataFrame([novo])], ignore_index=True)
                salvar_dados(df_novo); st.success("Motor cadastrado com sucesso!")
