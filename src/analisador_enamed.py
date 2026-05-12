import pandas as pd
from src.utilitarios import identificar_colunas_area, detectar_ciclo


def calcular_percentual_acertos(df, config):
    df = df.copy()
    numero_questoes = config.get("numero_questoes", 120)
    df["percentual_acertos"] = (df["acertos"] / numero_questoes) * 100
    return df


def adicionar_ciclo_formativo(df, config):
    df = df.copy()
    df["ciclo"] = df["periodo"].apply(lambda x: detectar_ciclo(x, config))
    return df


def calcular_estatisticas_gerais(df):
    return {
        "total_estudantes": int(df.shape[0]),
        "media_acertos": round(df["acertos"].mean(), 2),
        "mediana_acertos": round(df["acertos"].median(), 2),
        "desvio_padrao_acertos": round(df["acertos"].std(), 2),
        "variancia_acertos": round(df["acertos"].var(), 2),
        "minimo_acertos": round(df["acertos"].min(), 2),
        "maximo_acertos": round(df["acertos"].max(), 2),
        "media_percentual": round(df["percentual_acertos"].mean(), 2)
    }


def gerar_ranking_geral(df):
    ranking = df.copy().sort_values(
        by=["acertos", "percentual_acertos"],
        ascending=False
    )

    ranking["ranking_geral"] = range(1, len(ranking) + 1)

    return ranking[
        [
            "ranking_geral",
            "aluno",
            "turma",
            "periodo",
            "ciclo",
            "acertos",
            "percentual_acertos"
        ]
    ]


def gerar_ranking_por_turma(df):
    ranking = df.copy().sort_values(
        by=["turma", "acertos", "percentual_acertos"],
        ascending=[True, False, False]
    )

    ranking["ranking_turma"] = (
        ranking.groupby("turma")["acertos"]
        .rank(method="first", ascending=False)
        .astype(int)
    )

    return ranking[
        [
            "ranking_turma",
            "aluno",
            "turma",
            "periodo",
            "ciclo",
            "acertos",
            "percentual_acertos"
        ]
    ]


def analisar_por_turma(df):
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

    return tabela.round(2)


def analisar_por_ciclo(df):
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

    return tabela.round(2)


def identificar_estudantes_em_risco(df, config):
    df = df.copy()

    media_turma = df.groupby("turma")["percentual_acertos"].transform("mean")

    df["media_percentual_turma"] = media_turma.round(2)
    df["diferenca_para_media_turma"] = (
        df["percentual_acertos"] - media_turma
    ).round(2)

    df["percentual_abaixo_media_turma"] = 0.0

    abaixo = df["diferenca_para_media_turma"] < 0

    df.loc[abaixo, "percentual_abaixo_media_turma"] = (
        df.loc[abaixo, "diferenca_para_media_turma"].abs()
    )

    df["classificacao_risco"] = "Sem risco"

    limite_moderado = config["risco_pedagogico"]["moderado"]
    limite_elevado = config["risco_pedagogico"]["elevado"]

    df.loc[
        (df["percentual_abaixo_media_turma"] > 0)
        & (df["percentual_abaixo_media_turma"] <= limite_moderado),
        "classificacao_risco"
    ] = "Risco moderado"

    df.loc[
        df["percentual_abaixo_media_turma"] >= limite_elevado,
        "classificacao_risco"
    ] = "Risco elevado"

    return df[
        [
            "aluno",
            "turma",
            "periodo",
            "ciclo",
            "acertos",
            "percentual_acertos",
            "media_percentual_turma",
            "diferenca_para_media_turma",
            "percentual_abaixo_media_turma",
            "classificacao_risco"
        ]
    ]


def calcular_bonificacao(df, config):
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
    df["descricao_bonus"] = "Sem bonificação"

    for nome_faixa, regra in config["bonificacao"].items():
        condicao = (
            (df["percentual_acima_media_turma"] >= regra["min"])
            & (df["percentual_acima_media_turma"] <= regra["max"])
        )

        df.loc[condicao, "bonus_por_disciplina"] = regra["bonus"]
        df.loc[condicao, "numero_disciplinas"] = regra["disciplinas"]
        df.loc[condicao, "bonus_total"] = regra["bonus"] * regra["disciplinas"]
        df.loc[condicao, "classificacao_bonus"] = nome_faixa
        df.loc[condicao, "descricao_bonus"] = regra.get("descricao", "")

    return df[
        [
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
            "classificacao_bonus",
            "descricao_bonus"
        ]
    ]


def analisar_por_areas(df, config):
    areas_detectadas = identificar_colunas_area(df, config)
    resultados = []

    for area, colunas in areas_detectadas.items():
        df_area = df.copy()

        for coluna in colunas:
            df_area[coluna] = pd.to_numeric(
                df_area[coluna],
                errors="coerce"
            ).fillna(0)

        soma_area = df_area[colunas].sum(axis=1)

        resultados.append(
            {
                "area": area,
                "colunas_identificadas": ", ".join(colunas),
                "media_acertos": round(soma_area.mean(), 2),
                "mediana_acertos": round(soma_area.median(), 2),
                "desvio_padrao": round(soma_area.std(), 2),
                "minimo": round(soma_area.min(), 2),
                "maximo": round(soma_area.max(), 2)
            }
        )

    return pd.DataFrame(resultados)


def analisar_areas_por_turma(df, config):
    areas_detectadas = identificar_colunas_area(df, config)
    resultados = []

    for turma, grupo in df.groupby("turma"):
        grupo = grupo.copy()

        for area, colunas in areas_detectadas.items():
            for coluna in colunas:
                grupo[coluna] = pd.to_numeric(
                    grupo[coluna],
                    errors="coerce"
                ).fillna(0)

            soma_area = grupo[colunas].sum(axis=1)

            resultados.append(
                {
                    "turma": turma,
                    "area": area,
                    "estudantes": int(grupo.shape[0]),
                    "media_acertos": round(soma_area.mean(), 2),
                    "mediana_acertos": round(soma_area.median(), 2),
                    "desvio_padrao": round(soma_area.std(), 2),
                    "minimo": round(soma_area.min(), 2),
                    "maximo": round(soma_area.max(), 2)
                }
            )

    return pd.DataFrame(resultados)


def executar_analise_completa(df, config):
    df = calcular_percentual_acertos(df, config)
    df = adicionar_ciclo_formativo(df, config)

    return {
        "dados_processados": df,
        "estatisticas_gerais": calcular_estatisticas_gerais(df),
        "ranking_geral": gerar_ranking_geral(df),
        "ranking_por_turma": gerar_ranking_por_turma(df),
        "analise_por_turma": analisar_por_turma(df),
        "analise_por_ciclo": analisar_por_ciclo(df),
        "analise_por_areas": analisar_por_areas(df, config),
        "analise_areas_por_turma": analisar_areas_por_turma(df, config),
        "estudantes_em_risco": identificar_estudantes_em_risco(df, config),
        "bonificacao": calcular_bonificacao(df, config)
    }