import re
import pandas as pd
from tkinter import Tk
from tkinter.filedialog import askopenfilename


def selecionar_planilha():
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
    try:
        df = pd.read_excel(caminho_arquivo)
    except Exception as erro:
        raise RuntimeError(f"Erro ao carregar a planilha: {erro}")

    if df.empty:
        raise ValueError("A planilha selecionada está vazia.")

    return df


def padronizar_nome_coluna(coluna):
    coluna = str(coluna).strip().lower()

    substituicoes = {
        "á": "a",
        "à": "a",
        "ã": "a",
        "â": "a",
        "é": "e",
        "ê": "e",
        "í": "i",
        "ó": "o",
        "ô": "o",
        "õ": "o",
        "ú": "u",
        "ç": "c"
    }

    for antigo, novo in substituicoes.items():
        coluna = coluna.replace(antigo, novo)

    coluna = coluna.replace("/", "_")
    coluna = coluna.replace("-", "_")
    coluna = coluna.replace(" ", "_")
    coluna = coluna.replace("__", "_")

    return coluna


def padronizar_colunas(df):
    df = df.copy()
    df.columns = [padronizar_nome_coluna(coluna) for coluna in df.columns]
    return df


def renomear_colunas_enamed(df):
    df = df.copy()

    mapa = {
        "alunos": "aluno",
        "aluno": "aluno",
        "nome": "aluno",
        "nome_do_aluno": "aluno",

        "periodo": "turma",
        "periodo_turma": "turma",
        "turma": "turma",

        "clinica_medica": "clinica_medica",
        "pediatria": "pediatria",
        "cirurgia": "cirurgia",
        "gineco_obs": "ginecologia_obstetricia",
        "ginecologia_obstetricia": "ginecologia_obstetricia",
        "saude_coletiva": "saude_coletiva"
    }

    novas_colunas = {}

    for coluna in df.columns:
        if coluna in mapa:
            novas_colunas[coluna] = mapa[coluna]

    df = df.rename(columns=novas_colunas)

    return df


def extrair_periodo(turma):
    texto = str(turma).strip()

    resultado = re.search(r"\d+", texto)

    if resultado:
        return int(resultado.group())

    return None


def calcular_acertos_total(df):
    df = df.copy()

    colunas_areas = [
        "clinica_medica",
        "pediatria",
        "cirurgia",
        "ginecologia_obstetricia",
        "saude_coletiva"
    ]

    colunas_existentes = [
        coluna for coluna in colunas_areas
        if coluna in df.columns
    ]

    if not colunas_existentes:
        raise ValueError(
            "Não foram encontradas colunas de áreas do ENAMED. "
            "A planilha deve conter colunas como CLÍNICA MÉDICA, PEDIATRIA, "
            "CIRURGIA, GINECO/OBS e SAÚDE COLETIVA."
        )

    for coluna in colunas_existentes:
        df[coluna] = pd.to_numeric(df[coluna], errors="coerce").fillna(0)

    df["acertos"] = df[colunas_existentes].sum(axis=1)

    return df


def preparar_coluna_periodo(df):
    df = df.copy()

    if "turma" not in df.columns:
        raise ValueError(
            "A planilha precisa conter a coluna Período ou Turma."
        )

    df["periodo"] = df["turma"].apply(extrair_periodo)

    return df


def validar_colunas_obrigatorias(df):
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
            "A planilha não possui as colunas obrigatórias após a padronização: "
            + ", ".join(colunas_faltantes)
        )

    return True


def preparar_dados():
    caminho = selecionar_planilha()

    df = carregar_planilha(caminho)
    df = padronizar_colunas(df)
    df = renomear_colunas_enamed(df)
    df = preparar_coluna_periodo(df)
    df = calcular_acertos_total(df)

    validar_colunas_obrigatorias(df)

    df = df.dropna(subset=["aluno"])
    df["aluno"] = df["aluno"].astype(str).str.strip()
    df["turma"] = df["turma"].astype(str).str.strip()

    return df, caminho