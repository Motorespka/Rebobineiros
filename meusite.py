import streamlit as st
import pandas as pd
import math
import os

st.set_page_config(page_title="Sistema de Rebobinagem", layout="wide")

ARQUIVO_MOTORES = "motores.csv"

SENHA_MESTRE = "1234"

COLUNAS = [
"modelo",
"fabricante",
"potencia_cv",
"tensao",
"corrente",
"rpm",
"frequencia",
"polos",
"ranhuras",
"bobinas",
"espiras",
"fio_mm",
"ligacao",
"observacoes"
]

def carregar():
    if os.path.exists(ARQUIVO_MOTORES):
        return pd.read_csv(ARQUIVO_MOTORES)
    else:
        df = pd.DataFrame(columns=COLUNAS)

        exemplo = {
        "modelo":"WEG W22",
        "fabricante":"WEG",
        "potencia_cv":5,
        "tensao":220,
        "corrente":14.2,
        "rpm":1750,
        "frequencia":60,
        "polos":4,
        "ranhuras":36,
        "bobinas":12,
        "espiras":40,
        "fio_mm":1.25,
        "ligacao":"Delta",
        "observacoes":"Motor exemplo para testes"
        }

        df.loc[len(df)] = exemplo
        df.to_csv(ARQUIVO_MOTORES,index=False)

        return df

def salvar(df):
    df.to_csv(ARQUIVO_MOTORES,index=False)

df = carregar()

menu = st.sidebar.selectbox(
"Menu",
[
"Dashboard",
"Consultar motor",
"Cadastrar motor",
"Simulador de rebobinagem",
"Modo mestre"
]
)

def calcular_comprimento(espiras,bobinas,ranhuras):
    perimetro = ranhuras * 0.02
    return espiras * bobinas * perimetro

def calcular_peso(fio,comprimento):

    area = math.pi*(fio/2)**2
    volume = area * comprimento
    peso = volume * 8.96
    return peso

if menu == "Dashboard":

    st.title("Painel do Sistema")

    c1,c2,c3 = st.columns(3)

    c1.metric("Motores cadastrados",len(df))

    if len(df)>0:
        c2.metric("Potência média CV",round(df["potencia_cv"].mean(),2))
        c3.metric("RPM médio",round(df["rpm"].mean(),0))

    st.dataframe(df)

if menu == "Consultar motor":

    st.title("Consulta de motores")

    busca = st.text_input("Buscar modelo")

    resultado = df[df["modelo"].str.contains(busca,case=False,na=False)]

    st.dataframe(resultado)

    if len(resultado)>0:

        motor = resultado.iloc[0]

        st.subheader("Dados técnicos")

        col1,col2,col3 = st.columns(3)

        col1.write("Potência CV:",motor["potencia_cv"])
        col1.write("Tensão:",motor["tensao"])
        col1.write("Corrente:",motor["corrente"])

        col2.write("RPM:",motor["rpm"])
        col2.write("Frequência:",motor["frequencia"])
        col2.write("Polos:",motor["polos"])

        col3.write("Ranhuras:",motor["ranhuras"])
        col3.write("Bobinas:",motor["bobinas"])
        col3.write("Espiras:",motor["espiras"])

        comprimento = calcular_comprimento(
        motor["espiras"],
        motor["bobinas"],
        motor["ranhuras"]
        )

        peso = calcular_peso(
        motor["fio_mm"],
        comprimento
        )

        st.subheader("Cálculos estimados")

        st.write("Comprimento fio (m):",round(comprimento,2))
        st.write("Peso cobre (g):",round(peso,2))

if menu == "Cadastrar motor":

    st.title("Cadastro de motor")

    with st.form("cadastro"):

        modelo = st.text_input("Modelo")
        fabricante = st.text_input("Fabricante")

        c1,c2,c3 = st.columns(3)

        potencia = c1.number_input("Potência CV",0.0)
        tensao = c1.number_input("Tensão",0)

        corrente = c2.number_input("Corrente",0.0)
        rpm = c2.number_input("RPM",0)

        frequencia = c3.number_input("Frequência",60)
        polos = c3.number_input("Polos",4)

        ranhuras = st.number_input("Ranhuras",0)
        bobinas = st.number_input("Bobinas",0)
        espiras = st.number_input("Espiras",0)

        fio = st.number_input("Bitola fio mm",0.0)

        ligacao = st.selectbox("Ligação",["Estrela","Delta"])

        obs = st.text_area("Observações")

        enviar = st.form_submit_button("Salvar")

        if enviar:

            novo = {
            "modelo":modelo,
            "fabricante":fabricante,
            "potencia_cv":potencia,
            "tensao":tensao,
            "corrente":corrente,
            "rpm":rpm,
            "frequencia":frequencia,
            "polos":polos,
            "ranhuras":ranhuras,
            "bobinas":bobinas,
            "espiras":espiras,
            "fio_mm":fio,
            "ligacao":ligacao,
            "observacoes":obs
            }

            df.loc[len(df)] = novo

            salvar(df)

            st.success("Motor cadastrado")

if menu == "Simulador de rebobinagem":

    st.title("Simulador de alteração")

    modelo = st.selectbox("Motor base",df["modelo"])

    motor = df[df["modelo"]==modelo].iloc[0]

    espiras = st.number_input(
    "Espiras",
    value=int(motor["espiras"])
    )

    fio = st.number_input(
    "Fio mm",
    value=float(motor["fio_mm"])
    )

    bobinas = st.number_input(
    "Bobinas",
    value=int(motor["bobinas"])
    )

    comprimento = calcular_comprimento(
    espiras,
    bobinas,
    motor["ranhuras"]
    )

    peso = calcular_peso(
    fio,
    comprimento
    )

    st.subheader("Resultado da simulação")

    st.write("Comprimento fio:",round(comprimento,2))
    st.write("Peso cobre:",round(peso,2))

    st.info("Simulação não salva no banco")

if menu == "Modo mestre":

    st.title("Modo mestre")

    senha = st.text_input("Senha",type="password")

    if senha == SENHA_MESTRE:

        st.success("Acesso liberado")

        motor = st.selectbox("Motor",df["modelo"])

        indice = df[df["modelo"]==motor].index[0]

        novo_modelo = st.text_input(
        "Modelo",
        df.loc[indice,"modelo"]
        )

        nova_pot = st.number_input(
        "Potência",
        value=float(df.loc[indice,"potencia_cv"])
        )

        if st.button("Salvar edição"):

            df.loc[indice,"modelo"] = novo_modelo
            df.loc[indice,"potencia_cv"] = nova_pot

            salvar(df)

            st.success("Editado")

        if st.button("Excluir motor"):

            df.drop(indice,inplace=True)

            salvar(df)

            st.success("Motor excluído")

    else:
        st.warning("Acesso restrito")
        
