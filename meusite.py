import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ---------------- CONFIG ----------------

ARQUIVO_MOTORES = "motores.csv"
ARQUIVO_CLIENTES = "clientes.csv"
ARQUIVO_OS = "ordens_servico.csv"
ARQUIVO_FOTOS = "biblioteca_ligacoes.csv"

PASTA_UPLOADS = "uploads"

TOKEN_PRO = "PABLO123"
TOKEN_MESTRE = "MESTRE99"

if not os.path.exists(PASTA_UPLOADS):
    os.makedirs(PASTA_UPLOADS)

# ---------------- FUNÇÕES ----------------

def carregar(arq, colunas):
    if not os.path.exists(arq):
        return pd.DataFrame(columns=colunas)
    df = pd.read_csv(arq, sep=";", dtype=str).fillna("")
    for c in colunas:
        if c not in df.columns:
            df[c] = ""
    return df

def salvar(df, arq):
    df.to_csv(arq, index=False, sep=";")

# ---------------- COLUNAS ----------------

COL_MOTORES = [

"Marca",
"Modelo",

"Potencia_CV",
"Potencia_W",

"RPM",
"Frequencia",

"Voltagem",
"Amperagem",

"Numero_Polos",
"Tipo_Motor",

"Bobina_Principal",
"Fio_Principal",
"Passo_P",

"Bobina_Auxiliar",
"Fio_Auxiliar",
"Passo_A",

"Numero_Ranhuras",
"Passo_Ranhura",

"Tipo_Enrolamento",

"Tipo_Ligacao",
"Ligacao_Interna",

"Capacitor",
"Capacitor_Partida",
"Capacitor_Permanente",

"Rolamentos",
"Selo_Mecanico",

"Eixo_X",
"Eixo_Y",

"Sentido_Rotacao",

"Classe_Isolacao",
"Temperatura_Max",

"Obs",

"status"
]

COL_CLIENTES = [
"nome",
"telefone",
"cidade",
"email",
"data"
]

COL_OS = [
"numero",
"cliente",
"telefone",
"motor",
"problema",
"valor",
"status",
"data"
]

COL_FOTOS = [
"nome_ligacao",
"caminho"
]

# ---------------- CARREGAR BANCOS ----------------

df_motores = carregar(ARQUIVO_MOTORES, COL_MOTORES)
df_clientes = carregar(ARQUIVO_CLIENTES, COL_CLIENTES)
df_os = carregar(ARQUIVO_OS, COL_OS)
df_fotos = carregar(ARQUIVO_FOTOS, COL_FOTOS)

# ---------------- MOTOR TESTE ----------------

if df_motores.empty:

    motor = {
        "Marca":"WEG",
        "Modelo":"W22",

        "Potencia_CV":"1",
        "Potencia_W":"750",

        "RPM":"3450",
        "Frequencia":"60Hz",

        "Voltagem":"127/220",
        "Amperagem":"6.8",

        "Numero_Polos":"2",
        "Tipo_Motor":"Monofásico",

        "Bobina_Principal":"120",
        "Fio_Principal":"18 AWG",
        "Passo_P":"1-6",

        "Bobina_Auxiliar":"90",
        "Fio_Auxiliar":"20 AWG",
        "Passo_A":"1-5",

        "Numero_Ranhuras":"24",
        "Passo_Ranhura":"1-6",

        "Tipo_Enrolamento":"Concêntrico",

        "Tipo_Ligacao":"Paralelo",
        "Ligacao_Interna":"U1 U2 Z1 Z2",

        "Capacitor":"25uF",
        "Capacitor_Partida":"80uF",
        "Capacitor_Permanente":"25uF",

        "Rolamentos":"6203 / 6202",
        "Selo_Mecanico":"12mm",

        "Eixo_X":"15",
        "Eixo_Y":"40",

        "Sentido_Rotacao":"Horário",

        "Classe_Isolacao":"F",
        "Temperatura_Max":"155°C",

        "Obs":"Motor teste sistema",

        "status":"ativo"
    }

    df_motores = pd.concat([df_motores,pd.DataFrame([motor])],ignore_index=True)

    salvar(df_motores,ARQUIVO_MOTORES)

# ---------------- LOGIN ----------------

if "logado" not in st.session_state:

    st.session_state["logado"] = False
    st.session_state["perfil"] = ""

if not st.session_state["logado"]:

    st.title("⚙ Sistema Pablo Motores")

    tipo = st.selectbox(
        "Entrar como",
        ["Cliente","Profissional","Mestre"]
    )

    if tipo == "Cliente":

        if st.button("Entrar"):

            st.session_state["logado"] = True
            st.session_state["perfil"] = "cliente"
            st.rerun()

    else:

        token = st.text_input("Token", type="password")

        if st.button("Entrar"):

            if tipo == "Profissional" and token == TOKEN_PRO:

                st.session_state["logado"] = True
                st.session_state["perfil"] = "pro"
                st.rerun()

            elif tipo == "Mestre" and token == TOKEN_MESTRE:

                st.session_state["logado"] = True
                st.session_state["perfil"] = "mestre"
                st.rerun()

            else:

                st.error("Token incorreto")

    st.stop()

# ---------------- MENU ----------------

st.set_page_config(layout="wide")

with st.sidebar:

    st.title("Menu")

    if st.button("Sair"):
        st.session_state["logado"] = False
        st.rerun()

    menu = st.radio(

        "Opções",

        [
        "Consulta Motores",
        "Cadastrar Motor",
        "Clientes",
        "Ordem de Serviço",
        "Biblioteca de Ligações"
        ]

    )

# ---------------- CONSULTA ----------------

if menu == "Consulta Motores":

    st.title("Consulta de Motores")

    busca = st.text_input("Buscar motor")

    df = df_motores[df_motores["status"]!="deletado"]

    if busca:

        df = df[df.apply(

            lambda r: r.astype(str).str.contains(busca,case=False).any(),

            axis=1

        )]

    for i,r in df.iterrows():

        with st.expander(f"{r['Marca']} {r['Modelo']} | {r['Potencia_CV']}CV"):

            c1,c2,c3 = st.columns(3)

            with c1:

                st.write("Voltagem:",r["Voltagem"])
                st.write("Amperagem:",r["Amperagem"])
                st.write("RPM:",r["RPM"])
                st.write("Polos:",r["Numero_Polos"])

            with c2:

                st.write("Fio P:",r["Fio_Principal"])
                st.write("Espiras P:",r["Bobina_Principal"])
                st.write("Passo P:",r["Passo_P"])

                st.write("Fio A:",r["Fio_Auxiliar"])
                st.write("Espiras A:",r["Bobina_Auxiliar"])

            with c3:

                st.write("Rolamentos:",r["Rolamentos"])
                st.write("Capacitor:",r["Capacitor"])
                st.write("Classe isolação:",r["Classe_Isolacao"])
                st.write("Temperatura:",r["Temperatura_Max"])

            st.write("Observações:",r["Obs"])

# ---------------- CADASTRO MOTOR ----------------

elif menu == "Cadastrar Motor":

    st.title("Cadastro Motor")

    with st.form("motor"):

        c1,c2,c3 = st.columns(3)

        marca = c1.text_input("Marca")
        modelo = c1.text_input("Modelo")

        cv = c1.text_input("Potência CV")
        w = c1.text_input("Potência W")

        rpm = c2.text_input("RPM")
        freq = c2.text_input("Frequência")

        vol = c2.text_input("Voltagem")
        amp = c2.text_input("Amperagem")

        polos = c3.text_input("Número Polos")

        fio = c1.text_input("Fio principal")
        esp = c1.text_input("Espiras principal")
        passo = c1.text_input("Passo principal")

        rol = c2.text_input("Rolamentos")
        selo = c2.text_input("Selo mecânico")

        capacitor = c3.text_input("Capacitor")

        obs = st.text_area("Observações")

        if st.form_submit_button("Salvar"):

            novo = {

            "Marca":marca,
            "Modelo":modelo,

            "Potencia_CV":cv,
            "Potencia_W":w,

            "RPM":rpm,
            "Frequencia":freq,

            "Voltagem":vol,
            "Amperagem":amp,

            "Numero_Polos":polos,

            "Fio_Principal":fio,
            "Bobina_Principal":esp,
            "Passo_P":passo,

            "Rolamentos":rol,
            "Selo_Mecanico":selo,

            "Capacitor":capacitor,

            "Obs":obs,

            "status":"ativo"
            }

            df_motores = pd.concat([df_motores,pd.DataFrame([novo])],ignore_index=True)

            salvar(df_motores,ARQUIVO_MOTORES)

            st.success("Motor cadastrado")

# ---------------- CLIENTES ----------------

elif menu == "Clientes":

    st.title("Cadastro Clientes")

    with st.form("cliente"):

        c1,c2 = st.columns(2)

        nome = c1.text_input("Nome")
        telefone = c1.text_input("Telefone")

        cidade = c2.text_input("Cidade")
        email = c2.text_input("Email")

        if st.form_submit_button("Cadastrar"):

            novo = {

            "nome":nome,
            "telefone":telefone,
            "cidade":cidade,
            "email":email,
            "data":datetime.now().strftime("%d/%m/%Y")

            }

            df_clientes = pd.concat([df_clientes,pd.DataFrame([novo])],ignore_index=True)

            salvar(df_clientes,ARQUIVO_CLIENTES)

            st.success("Cliente cadastrado")

    st.dataframe(df_clientes)

# ---------------- ORDEM SERVIÇO ----------------

elif menu == "Ordem de Serviço":

    st.title("Ordem de Serviço")

    with st.form("os"):

        cliente = st.selectbox(

            "Cliente",

            df_clientes["nome"] if not df_clientes.empty else []

        )

        telefone = st.text_input("Telefone")

        motor = st.text_input("Motor")

        problema = st.text_area("Problema")

        valor = st.text_input("Valor")

        if st.form_submit_button("Abrir OS"):

            numero = str(len(df_os)+1)

            nova = {

            "numero":numero,
            "cliente":cliente,
            "telefone":telefone,
            "motor":motor,
            "problema":problema,
            "valor":valor,
            "status":"aberta",
            "data":datetime.now().strftime("%d/%m/%Y")

            }

            df_os = pd.concat([df_os,pd.DataFrame([nova])],ignore_index=True)

            salvar(df_os,ARQUIVO_OS)

            st.success("OS criada")

    st.dataframe(df_os)

# ---------------- BIBLIOTECA ----------------

elif menu == "Biblioteca de Ligações":

    st.title("Biblioteca Esquemas")

    with st.form("foto"):

        nome = st.text_input("Nome ligação")

        file = st.file_uploader("Imagem")

        if st.form_submit_button("Enviar"):

            if file:

                path = os.path.join(PASTA_UPLOADS,file.name)

                with open(path,"wb") as f:

                    f.write(file.getbuffer())

                novo = {

                "nome_ligacao":nome,
                "caminho":path

                }

                df_fotos = pd.concat([df_fotos,pd.DataFrame([novo])],ignore_index=True)

                salvar(df_fotos,ARQUIVO_FOTOS)

                st.success("Imagem salva")

    for i,r in df_fotos.iterrows():

        st.image(r["caminho"],caption=r["nome_ligacao"])
