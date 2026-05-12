import pandas as pd
import numpy as np

from src.utilitarios import identificar_colunas_area, detectar_ciclo


def calcular_percentual_acertos(df, config):
    """
    Calcula o percentual de acertos com base no número total de questões.
    """

    df = df.copy()

    numero_questoes = config.get("numero_questoes", 100)

    df["percentual_acertos"] = (df["acertos"] / numero_questoes) * 100

    return df


def adicionar_ciclo_formativo(df, config):
    """
    Adiciona a coluna de ciclo formativo.
    """

    df = df.copy()

    df["ciclo"] = df["periodo"].apply(lambda x: detectar_ciclo(x, config))

    return df


def calcular_estatisticas_gerais(df):
    """
    Calcula estatísticas gerais do simulado ou prova ENAMED.
    """

    estatisticas = {
        "total_estudantes": int(df.shape[0]),
        "media_acertos": round(df["acertos"].mean(), 2),
        "mediana_acertos": round(df["acertos"].median(), 2),
        "desvio_padrao_acertos": round(df["acertos"].std(), 2),
        "variancia_acertos": round(df["acertos"].var(), 2),
        "minimo_acertos": round(df["acertos"].min(), 2),
        "maximo_acertos": round(df["acertos"].max(), 2),
        "media_percentual": round(df["percentual_acertos"].mean(), 2)
    }

    return estatisticas


def gerar_ranking_geral(df):
    """
    Gera ranking geral dos estudantes.
    """

    ranking = df.copy()

    ranking = ranking.sort_values(
        by=["acertos", "percentual_acertos"],
        ascending=False
    )

    ranking["ranking_geral"] = range(1, len(ranking) + 1)

    colunas = [
        "ranking_geral",
        "aluno",
        "turma",
        "periodo",
        "ciclo",
        "acertos",
        "percentual_acertos"
    ]

    return ranking[colunas]


def gerar_ranking_por_turma(df):
    """
    Gera ranking por turma.
    """

    ranking = df.copy()

    ranking = ranking.sort_values(
        by=["turma", "acertos", "percentual_acertos"],
        ascending=[True, False, False]
    )

    ranking["ranking_turma"] = (
        ranking.groupby("turma")["acertos"]
        .rank(method="first", ascending=False)
        .astype(int)
    )

    colunas = [
        "ranking_turma",
        "aluno",
        "turma",
        "periodo",
        "ciclo",
        "acertos",
        "percentual_acertos"
    ]

    return ranking[colunas]


def analisar_por_turma(df):
    """
    Calcula estatísticas por turma/período.
    """

    tabela = (
        df.groupby(["turma", "periodo", "ciclo"])
        .agg(
            estudantes=("aluno", "count"),
            media_acertos=("acertos", "mean"),
            mediana_acertos=("acertos", "median"),
            desvio_padrao=("acertos", "std"),
            minimo=("acertos", "min"),
            maximo=("acertos", "max"),
            media_percentual=("percentual_acertos", "mean")
        )
        .reset_index()
    )

    colunas_numericas = [
        "media_acertos",
        "mediana_acertos",
        "desvio_padrao",
        "minimo",
        "maximo",
        "media_percentual"
    ]

    tabela[colunas_numericas] = tabela[colunas_numericas].round(2)

    return tabela


def analisar_por_ciclo(df):
    """
    Calcula estatísticas por ciclo formativo.
    """

    tabela = (
        df.groupby("ciclo")
        .agg(
            estudantes=("aluno", "count"),
            media_acertos=("acertos", "mean"),
            mediana_acertos=("acertos", "median"),
            desvio_padrao=("acertos", "std"),
            minimo=("acertos", "min"),
            maximo=("acertos", "max"),
            media_percentual=("percentual_acertos", "mean")
        )
        .reset_index()
    )

    colunas_numericas = [
        "media_acertos",
        "mediana_acertos",
        "desvio_padrao",
        "minimo",
        "maximo",
        "media_percentual"
    ]

    tabela[colunas_numericas] = tabela[colunas_numericas].round(2)

    return tabela


def identificar_estudantes_em_risco(df, config):
    """
    Identifica estudantes abaixo da média da própria turma.
    """

    df = df.copy()

    media_turma = df.groupby("turma")["percentual_acertos"].transform("mean")

    df["media_percentual_turma"] = media_turma.round(2)
    df["diferenca_para_media_turma"] = (
        df["percentual_acertos"] - media_turma
    ).round(2)

    df["classificacao_risco"] = "Sem risco"

    limite_moderado = config["risco_pedagogico"]["moderado"]
    limite_critico = config["risco_pedagogico"]["critico"]

    df.loc[
        (df["diferenca_para_media_turma"] < 0)
        & (df["diferenca_para_media_turma"] >= -limite_moderado),
        "classificacao_risco"
    ] = "Risco pedagógico moderado"

    df.loc[
        df["diferenca_para_media_turma"] <= -limite_critico,
        "classificacao_risco"
    ] = "Risco pedagógico crítico"

    colunas = [
        "aluno",
        "turma",
        "periodo",
        "ciclo",
        "acertos",
        "percentual_acertos",
        "media_percentual_turma",
        "diferenca_para_media_turma",
        "classificacao_risco"
    ]

    return df[colunas]


def calcular_bonificacao(df, config):
    """
    Calcula bonificação acadêmica com base no desempenho acima da média da turma.
    """

    df = df.copy()

    media_turma = df.groupby("turma")["percentual_acertos"].transform("mean")

    df["media_percentual_turma"] = media_turma.round(2)
    df["percentual_acima_media_turma"] = (
        df["percentual_acertos"] - media_turma
    ).round(2)

    df["bonus_por_disciplina"] = 0.0
    df["numero_disciplinas"] = 0
    df["bonus_total"] = 0.0
    df["classificacao_bonus"] = "Sem bonificação"

    for nome_faixa, regra in config["bonificacao"].items():
        minimo = regra["min"]
        maximo = regra["max"]
        bonus = regra["bonus"]
        disciplinas = regra["disciplinas"]

        condicao = (
            (df["percentual_acima_media_turma"] >= minimo)
            & (df["percentual_acima_media_turma"] <= maximo)
        )

        df.loc[condicao, "bonus_por_disciplina"] = bonus
        df.loc[condicao, "numero_disciplinas"] = disciplinas
        df.loc[condicao, "bonus_total"] = bonus * disciplinas
        df.loc[condicao, "classificacao_bonus"] = nome_faixa

    colunas = [
        "aluno",
        "turma",
        "periodo",
        "ciclo",
        "acertos",
        "percentual_acertos",
        "media_percentual_turma",
        "percentual_acima_media_turma",
        "bonus_por_disciplina",
        "numero_disciplinas",
        "bonus_total",
        "classificacao_bonus"
    ]

    return df[colunas]


def analisar_por_areas(df, config):
    """
    Analisa o desempenho por grandes áreas do ENAMED.
    As colunas das áreas devem estar configuradas no config.json.
    """

    areas_detectadas = identificar_colunas_area(df, config)

    resultados = []

    for area, colunas in areas_detectadas.items():
        df_area = df.copy()

        df_area[f"acertos_{area}"] = df_area[colunas].sum(axis=1)
        df_area[f"percentual_{area}"] = (
            df_area[f"acertos_{area}"] / len(colunas)
        ) * 100

        resumo_area = {
            "area": area,
            "questoes_identificadas": len(colunas),
            "media_acertos": round(df_area[f"acertos_{area}"].mean(), 2),
            "media_percentual": round(df_area[f"percentual_{area}"].mean(), 2),
            "desvio_padrao": round(df_area[f"acertos_{area}"].std(), 2),
            "minimo": round(df_area[f"acertos_{area}"].min(), 2),
            "maximo": round(df_area[f"acertos_{area}"].max(), 2)
        }

        resultados.append(resumo_area)

    if not resultados:
        return pd.DataFrame()

    return pd.DataFrame(resultados)


def executar_analise_completa(df, config):
    """
    Executa todo o pipeline analítico do ENAMED Performance Analytics.
    """

    df = calcular_percentual_acertos(df, config)
    df = adicionar_ciclo_formativo(df, config)

    resultados = {
        "dados_processados": df,
        "estatisticas_gerais": calcular_estatisticas_gerais(df),
        "ranking_geral": gerar_ranking_geral(df),
        "ranking_por_turma": gerar_ranking_por_turma(df),
        "analise_por_turma": analisar_por_turma(df),
        "analise_por_ciclo": analisar_por_ciclo(df),
        "estudantes_em_risco": identificar_estudantes_em_risco(df, config),
        "bonificacao": calcular_bonificacao(df, config),
        "analise_por_areas": analisar_por_areas(df, config)
    }

    return resultados