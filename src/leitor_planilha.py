import pandas as pd
from tkinter import Tk
from tkinter.filedialog import askopenfilename


def selecionar_planilha():
    """
    Abre uma janela para o usuário selecionar a planilha do simulado ou prova ENAMED.
    Aceita arquivos .xlsx e .xls.
    """

    janela = Tk()
    janela.withdraw()

    caminho_arquivo = askopenfilename(
        title="Selecione a planilha do simulado ou prova ENAMED",
        filetypes=[
            ("Planilhas Excel", "*.xlsx *.xls"),
            ("Todos os arquivos", "*.*")
        ]
    )

    if not caminho_arquivo:
        raise FileNotFoundError("Nenhuma planilha foi selecionada.")

    return caminho_arquivo


def carregar_planilha(caminho_arquivo):
    """
    Carrega a planilha selecionada em um DataFrame pandas.
    """

    try:
        df = pd.read_excel(caminho_arquivo)
    except Exception as erro:
        raise RuntimeError(f"Erro ao carregar a planilha: {erro}")

    if df.empty:
        raise ValueError("A planilha selecionada está vazia.")

    return df


def padronizar_colunas(df):
    """
    Padroniza os nomes das colunas para facilitar a análise.
    """

    df = df.copy()

    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
        .str.replace(" ", "_")
        .str.replace("-", "_")
        .str.replace("/", "_")
        .str.lower()
    )

    return df


def validar_colunas_obrigatorias(df):
    """
    Verifica se a planilha possui as colunas mínimas necessárias.
    """

    colunas_obrigatorias = [
        "aluno",
        "turma",
        "periodo",
        "acertos"
    ]

    colunas_faltantes = [
        coluna for coluna in colunas_obrigatorias
        if coluna not in df.columns
    ]

    if colunas_faltantes:
        raise ValueError(
            "A planilha não possui as colunas obrigatórias: "
            + ", ".join(colunas_faltantes)
        )

    return True


def preparar_dados():
    """
    Fluxo completo:
    1. Seleciona planilha.
    2. Carrega dados.
    3. Padroniza colunas.
    4. Valida colunas obrigatórias.
    """

    caminho = selecionar_planilha()
    df = carregar_planilha(caminho)
    df = padronizar_colunas(df)
    validar_colunas_obrigatorias(df)

    return df, caminho