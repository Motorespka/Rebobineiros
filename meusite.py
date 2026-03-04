import streamlit as st
import pandas as pd
import os
from datetime import datetime
from PIL import Image

# --- CONFIGURAÇÕES ---
ARQUIVO_CSV = 'meubancodedados.csv'
PASTA_ESQUEMAS = 'esquemas_fotos'

if not os.path.exists(PASTA_ESQUEMAS): os.makedirs(PASTA_ESQUEMAS)

st.set_page_config(page_title="Pablo Motores | Gestão Completa", layout="wide")

# --- FUNÇÃO DE CARREGAMENTO ---
def carregar_dados():
    if os.path.exists(ARQUIVO_CSV):
        return pd.read_csv(ARQUIVO_CSV, sep=';', encoding='utf-8-sig').fillna("---").replace("None", "---")
    return pd.DataFrame()

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("🔐 ACESSO")
    senha = st.text_input("Senha Admin", type="password")
    e_admin = (senha == "pablo123")
    
    menu = ["🔍 CONSULTA"]
    if e_admin:
        menu = ["🔍 CONSULTA", "➕ NOVO CADASTRO", "🖼️ ADICIONAR FOTO", "🗑️ LIXEIRA"]
    escolha = st.radio("Ir para:", menu)

# --- ABA 1: CONSULTA ---
if escolha == "🔍 CONSULTA":
    st.markdown("<h1 style='text-align: center; color: #f1c40f;'>⚙️ PABLO MOTORES</h1>", unsafe_allow_html=True)
    df = carregar_dados()
    busca = st.text_input("🔍 Pesquisar motor...")
    
    if not df.empty:
        df_f = df[df.astype(str).apply(lambda x: busca.lower() in x.str.lower().any(), axis=1)] if busca else df
        for idx, row in df_f.iterrows():
            with st.expander(f"📦 {row.get('Marca')} | {row.get('Potencia_CV')} CV | {row.get('RPM')} RPM"):
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.write(f"**Polos:** {row.get('Polaridade')}")
                    st.write(f"**Volt:** {row.get('Voltagem')}")
                    st.write(f"**Amp:** {row.get('Amperagem')}")
                with col2:
                    st.write(f"**Fio Principal:** {row.get('Fio_Principal')}")
                    st.write(f"**Camas Princ.:** {row.get('Bobina_Principal')}")
                    st.write(f"**Rolamentos:** {row.get('Rolamentos')}")
                with col3:
                    st.write(f"**Fio Auxiliar:** {row.get('Fio_Auxiliar')}")
                    st.write(f"**Camas Aux.:** {row.get('Bobina_Auxiliar')}")
                    st.write(f"**Capacitor:** {row.get('Capacitor')}")
                with col4:
                    lig = str(row.get('Esquema_Marcado'))
                    st.info(f"Ligação: {lig}")
                    for n in lig.split(" / "):
                        for ext in [".png", ".jpg"]:
                            p = os.path.join(PASTA_ESQUEMAS, f"{n.strip()}{ext}")
                            if os.path.exists(p): st.image(p)

# --- ABA 2: NOVO CADASTRO (COM TODAS AS INFORMAÇÕES) ---
elif escolha == "➕ NOVO CADASTRO":
    st.markdown("## ➕ Cadastrar Novo Motor")
    
    # Lista de fotos disponíveis para os quadrados
    lista_fotos = [f.split(".")[0] for f in os.listdir(PASTA_ESQUEMAS) if f.endswith(('.png', '.jpg'))]
    
    with st.form("cadastro_completo"):
        c1, c2, c3 = st.columns(3)
        
        with c1:
            st.markdown("### 📊 Geral")
            marca = st.text_input("Marca")
            cv = st.text_input("Potência (CV)")
            rpm = st.text_input("RPM")
            pol = st.text_input("Polaridade (Polos)")
            volt = st.text_input("Voltagem")
            amp = st.text_input("Amperagem")
            
        with c2:
            st.markdown("### 🌀 Principal")
            fio_p = st.text_input("Fio Principal")
            camas_p = st.text_input("Camas (Principal)")
            rolam = st.text_input("Rolamentos")
            
        with c3:
            st.markdown("### ⚡ Auxiliar")
            fio_a = st.text_input("Fio Auxiliar")
            camas_a = st.text_input("Camas (Auxiliar)")
            capac = st.text_input("Capacitor")
            eixo = st.text_input("Eixo (X x Y)")

        st.divider()
        st.markdown("### 🖼️ SELECIONE OS ESQUEMAS DE LIGAÇÃO")
        
        # Quadrados de seleção (Checkboxes)
        selecionados = []
        if lista_fotos:
            cols_check = st.columns(4)
            for i, foto in enumerate(lista_fotos):
                if cols_check[i % 4].checkbox(foto, key=f"add_{foto}"):
                    selecionados.append(foto)
        else:
            st.warning("Nenhuma foto encontrada na pasta de esquemas. Adicione fotos primeiro!")

        if st.form_submit_button("💾 SALVAR MOTOR"):
            nova_lig = " / ".join(selecionados) if selecionados else "---"
            novo_motor = {
                'Marca': marca, 'Potencia_CV': cv, 'RPM': rpm, 'Polaridade': pol,
                'Voltagem': volt, 'Amperagem': amp, 'Fio_Principal': fio_p,
                'Bobina_Principal': camas_p, 'Rolamentos': rolam, 
                'Fio_Auxiliar': fio_a, 'Bobina_Auxiliar': camas_a,
                'Capacitor': capac, 'Eixo_X_Y': eixo, 'Esquema_Marcado': nova_lig
            }
            df_novo = pd.DataFrame([novo_motor])
            df_novo.to_csv(ARQUIVO_CSV, mode='a', header=not os.path.exists(ARQUIVO_CSV), index=False, sep=';', encoding='utf-8-sig')
            st.success(f"Motor {marca} cadastrado com sucesso!")

# --- ABA 3: ADICIONAR FOTO ---
elif escolha == "🖼️ ADICIONAR FOTO":
    st.markdown("## 🖼️ Enviar Novo Esquema")
    arq = st.file_uploader("Escolha a imagem", type=['png', 'jpg'])
    nome_arq = st.text_input("Nome do Esquema (Ex: Estrela 12 Pontas)")
    if st.button("Salvar Imagem") and arq and nome_arq:
        Image.open(arq).save(os.path.join(PASTA_ESQUEMAS, f"{nome_arq}.png"))
        st.success(f"Esquema '{nome_arq}' pronto para uso no cadastro!")
