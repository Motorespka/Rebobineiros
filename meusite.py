import streamlit as st
import pandas as pd
import os
from datetime import datetime
from PIL import Image

# --- CONFIGURAÇÕES ---
ARQUIVO_CSV = 'meubancodedados.csv'
PASTA_ESQUEMAS = 'esquemas_fotos'

if not os.path.exists(PASTA_ESQUEMAS): os.makedirs(PASTA_ESQUEMAS)

st.set_page_config(page_title="Pablo Motores", layout="wide")

# --- FUNÇÃO DE CARREGAMENTO SEGURO ---
def carregar_dados():
    if os.path.exists(ARQUIVO_CSV):
        try:
            # Forçamos o pandas a ler tudo como string para evitar erros de tipo
            df = pd.read_csv(ARQUIVO_CSV, sep=';', encoding='utf-8-sig', dtype=str).fillna("---")
            return df
        except:
            return pd.DataFrame()
    return pd.DataFrame()

# --- LOGIN E NAVEGAÇÃO ---
with st.sidebar:
    st.header("🔐 ACESSO")
    senha = st.text_input("Senha Admin", type="password")
    e_admin = (senha == "pablo123")
    
    menu = ["🔍 CONSULTA"]
    if e_admin:
        menu = ["🔍 CONSULTA", "➕ NOVO CADASTRO", "🖼️ ADICIONAR FOTO", "🗑️ LIXEIRA"]
    escolha = st.radio("Ir para:", menu)

# --- ABA 1: CONSULTA (CORRIGIDA) ---
if escolha == "🔍 CONSULTA":
    st.markdown("<h1 style='text-align: center; color: #f1c40f;'>⚙️ PABLO MOTORES</h1>", unsafe_allow_html=True)
    df = carregar_dados()
    
    busca = st.text_input("🔍 Pesquisar por Marca, CV ou qualquer detalhe...")
    
    if not df.empty:
        # NOVA LÓGICA DE BUSCA: Mais simples e sem erros de tipo
        if busca:
            # Filtra se o termo de busca aparece em qualquer célula da linha
            df_f = df[df.apply(lambda row: row.astype(str).str.contains(busca, case=False).any(), axis=1)]
        else:
            df_f = df

        for idx, row in df_f.iterrows():
            with st.expander(f"📦 {row.get('Marca')} | {row.get('Potencia_CV')} CV | {row.get('RPM')} RPM"):
                # ... (O resto do código de exibição permanece o mesmo)
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    st.write(f"**Polos:** {row.get('Polaridade')}")
                    st.write(f"**Volt:** {row.get('Voltagem')}")
                with c2:
                    st.write(f"**Fio Principal:** {row.get('Fio_Principal')}")
                with c3:
                    st.write(f"**Capacitor:** {row.get('Capacitor')}")
                with c4:
                    lig = str(row.get('Esquema_Marcado'))
                    st.info(f"Ligação: {lig}")
                    for n in lig.split(" / "):
                        for ext in [".png", ".jpg"]:
                            p = os.path.join(PASTA_ESQUEMAS, f"{n.strip()}{ext}")
                            if os.path.exists(p): st.image(p)

# --- ABA 2: NOVO CADASTRO (RESTAURADO COM TODOS OS CAMPOS) ---
elif escolha == "➕ NOVO CADASTRO":
    st.markdown("## ➕ Cadastrar Novo Motor")
    lista_fotos = [f.split(".")[0] for f in os.listdir(PASTA_ESQUEMAS) if f.endswith(('.png', '.jpg'))]
    
    with st.form("cadastro_pablo"):
        c1, c2, c3 = st.columns(3)
        with c1:
            marca = st.text_input("Marca")
            cv = st.text_input("Potência (CV)")
            rpm = st.text_input("RPM")
            pol = st.text_input("Polaridade")
        with c2:
            volt = st.text_input("Voltagem")
            amp = st.text_input("Amperagem")
            fio_p = st.text_input("Fio Principal")
            camas_p = st.text_input("Camas Principal")
        with c3:
            fio_a = st.text_input("Fio Auxiliar")
            camas_a = st.text_input("Camas Auxiliar")
            capac = st.text_input("Capacitor")
            rolam = st.text_input("Rolamentos")
            eixo = st.text_input("Eixo")

        st.write("### 🖼️ Marque as Ligações")
        selecionados = []
        if lista_fotos:
            cols = st.columns(4)
            for i, foto in enumerate(lista_fotos):
                if cols[i % 4].checkbox(foto): selecionados.append(foto)
        
        if st.form_submit_button("💾 SALVAR MOTOR"):
            nova_lig = " / ".join(selecionados) if selecionados else "---"
            novo_motor = {
                'Marca': marca, 'Potencia_CV': cv, 'RPM': rpm, 'Polaridade': pol,
                'Voltagem': volt, 'Amperagem': amp, 'Fio_Principal': fio_p,
                'Bobina_Principal': camas_p, 'Rolamentos': rolam, 
                'Fio_Auxiliar': fio_a, 'Bobina_Auxiliar': camas_a,
                'Capacitor': capac, 'Eixo': eixo, 'Esquema_Marcado': nova_lig
            }
            df_n = pd.DataFrame([novo_motor])
            df_n.to_csv(ARQUIVO_CSV, mode='a', header=not os.path.exists(ARQUIVO_CSV), index=False, sep=';', encoding='utf-8-sig')
            st.success("Salvo!")

# --- ABA 3: ADICIONAR FOTO ---
elif escolha == "🖼️ ADICIONAR FOTO":
    st.markdown("## 🖼️ Enviar Novo Esquema")
    arq = st.file_uploader("Foto", type=['png', 'jpg'])
    nome_f = st.text_input("Nome (Ex: Estrela)")
    if st.button("Gravar") and arq and nome_f:
        Image.open(arq).save(os.path.join(PASTA_ESQUEMAS, f"{nome_f}.png"))
        st.success("Foto salva!")
