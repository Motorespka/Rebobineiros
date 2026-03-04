# --- CONFIGURAÇÕES ---
ARQUIVO_CSV = 'meubancodedados.csv'
# Link fornecido pelo usuário
LINK_SHEETS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTFbH81UYKGJ6dQvKotxdv4hDxecLmiGUPHN46iexbw8NeS8_e2XdyZnZ8WJnL2XRTLCbFDbBKo_NGE/pub?output=csv"
PASTA_ESQUEMAS = 'esquemas_fotos'

# --- FUNÇÃO DE CARREGAMENTO (HÍBRIDA: LOCAL + NUVEM) ---
def carregar_dados():
    dfs = []
    
    # 1. Tenta carregar do Google Sheets (Nuvem)
    try:
        # Lemos do link direto. O pandas aceita a URL como caminho.
        # Nota: O link do Sheets usa vírgula (,) como separador padrão.
        df_nuvem = pd.read_csv(LINK_SHEETS, dtype=str)
        if not df_nuvem.empty:
            dfs.append(df_nuvem)
    except Exception as e:
        st.error(f"Erro ao acessar Google Sheets: {e}")

    # 2. Tenta carregar do CSV Local (GitHub/Local)
    if os.path.exists(ARQUIVO_CSV):
        try:
            # O seu arquivo local usa ponto e vírgula (;) conforme seu código base.
            df_local = pd.read_csv(ARQUIVO_CSV, sep=';', encoding='utf-8-sig', dtype=str)
            if not df_local.empty:
                dfs.append(df_local)
        except Exception as e:
            st.error(f"Erro ao acessar CSV Local: {e}")

    # Se não encontrar dados em nenhum lugar, retorna vazio
    if not dfs:
        return pd.DataFrame()

    # 3. UNE OS DADOS E REMOVE DUPLICADOS
    df_geral = pd.concat(dfs, ignore_index=True).fillna("None")
    
    # Critério para não repetir: Marca, Potência e RPM devem ser únicos.
    # Se houver duas linhas iguais nestes 3 campos, ele mantém apenas a primeira que encontrar.
    colunas_chave = ['Marca', 'Potencia_CV', 'RPM']
    
    # Verifica se as colunas existem antes de aplicar a limpeza
    colunas_presentes = [c for c in colunas_chave if c in df_geral.columns]
    if colunas_presentes:
        df_geral = df_geral.drop_duplicates(subset=colunas_presentes, keep='first')

    return df_geral
