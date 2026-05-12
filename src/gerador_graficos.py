import os
import matplotlib.pyplot as plt


def salvar_figura(nome_arquivo, pasta_figures, config):
    dpi = config.get("graficos", {}).get("dpi", 300)
    salvar_svg = config.get("graficos", {}).get("salvar_svg", True)

    caminho_png = os.path.join(pasta_figures, f"{nome_arquivo}.png")
    plt.savefig(caminho_png, dpi=dpi, bbox_inches="tight")

    caminho_svg = None

    if salvar_svg:
        caminho_svg = os.path.join(pasta_figures, f"{nome_arquivo}.svg")
        plt.savefig(caminho_svg, bbox_inches="tight")

    plt.close()

    return caminho_png, caminho_svg


def grafico_histograma_desempenho(df, pasta_figures, config):
    plt.figure(figsize=(10, 6))
    plt.hist(df["percentual_acertos"], bins=10, edgecolor="black")

    plt.title("Distribuição do desempenho percentual dos estudantes")
    plt.xlabel("Percentual de acertos")
    plt.ylabel("Número de estudantes")

    return salvar_figura(
        "histograma_desempenho_percentual",
        pasta_figures,
        config
    )


def grafico_boxplot_por_turma(df, pasta_figures, config):
    turmas = sorted(df["turma"].dropna().unique())
    dados = [
        df[df["turma"] == turma]["percentual_acertos"]
        for turma in turmas
    ]

    plt.figure(figsize=(12, 6))
    plt.boxplot(dados, labels=turmas, showmeans=True)

    plt.title("Distribuição do desempenho percentual por turma")
    plt.xlabel("Turma")
    plt.ylabel("Percentual de acertos")
    plt.xticks(rotation=45)

    return salvar_figura(
        "boxplot_desempenho_por_turma",
        pasta_figures,
        config
    )


def grafico_media_por_turma(tabela_turma, pasta_figures, config):
    tabela = tabela_turma.sort_values(
        "media_percentual",
        ascending=False
    )

    plt.figure(figsize=(12, 6))
    plt.bar(
        tabela["turma"].astype(str),
        tabela["media_percentual"]
    )

    plt.title("Média percentual de acertos por turma")
    plt.xlabel("Turma")
    plt.ylabel("Média percentual de acertos")
    plt.xticks(rotation=45)

    return salvar_figura(
        "media_percentual_por_turma",
        pasta_figures,
        config
    )


def grafico_media_por_ciclo(tabela_ciclo, pasta_figures, config):
    tabela = tabela_ciclo.sort_values(
        "media_percentual",
        ascending=False
    )

    plt.figure(figsize=(10, 6))
    plt.bar(
        tabela["ciclo"].astype(str),
        tabela["media_percentual"]
    )

    plt.title("Média percentual de acertos por ciclo formativo")
    plt.xlabel("Ciclo formativo")
    plt.ylabel("Média percentual de acertos")

    return salvar_figura(
        "media_percentual_por_ciclo",
        pasta_figures,
        config
    )


def grafico_areas(tabela_areas, pasta_figures, config):
    if tabela_areas is None or tabela_areas.empty:
        return None, None

    tabela = tabela_areas.sort_values(
        "media_acertos",
        ascending=False
    )

    plt.figure(figsize=(12, 6))
    plt.bar(
        tabela["area"],
        tabela["media_acertos"]
    )

    plt.title("Desempenho médio por grande área do ENAMED")
    plt.xlabel("Grande área")
    plt.ylabel("Média de acertos")
    plt.xticks(rotation=45, ha="right")

    return salvar_figura(
        "desempenho_medio_por_area",
        pasta_figures,
        config
    )


def grafico_areas_por_turma(tabela_areas_turma, pasta_figures, config):
    if tabela_areas_turma is None or tabela_areas_turma.empty:
        return None, None

    tabela_pivot = tabela_areas_turma.pivot_table(
        index="turma",
        columns="area",
        values="media_acertos",
        aggfunc="mean"
    )

    plt.figure(figsize=(14, 7))

    tabela_pivot.plot(kind="bar", figsize=(14, 7))

    plt.title("Desempenho médio por área e turma")
    plt.xlabel("Turma")
    plt.ylabel("Média de acertos")
    plt.xticks(rotation=45)
    plt.legend(title="Área", bbox_to_anchor=(1.05, 1), loc="upper left")

    return salvar_figura(
        "desempenho_area_por_turma",
        pasta_figures,
        config
    )


def grafico_risco_pedagogico(tabela_risco, pasta_figures, config):
    contagem = (
        tabela_risco["classificacao_risco"]
        .value_counts()
        .reset_index()
    )

    contagem.columns = ["classificacao_risco", "quantidade"]

    plt.figure(figsize=(10, 6))
    plt.bar(
        contagem["classificacao_risco"],
        contagem["quantidade"]
    )

    plt.title("Distribuição dos estudantes por classificação de risco")
    plt.xlabel("Classificação de risco")
    plt.ylabel("Número de estudantes")
    plt.xticks(rotation=30, ha="right")

    return salvar_figura(
        "distribuicao_risco_pedagogico",
        pasta_figures,
        config
    )


def grafico_bonificacao(tabela_bonus, pasta_figures, config):
    if tabela_bonus is None or tabela_bonus.empty:
        return None, None

    contagem = (
        tabela_bonus["classificacao_bonus"]
        .value_counts()
        .reset_index()
    )

    contagem.columns = ["classificacao_bonus", "quantidade"]

    plt.figure(figsize=(10, 6))
    plt.bar(
        contagem["classificacao_bonus"],
        contagem["quantidade"]
    )

    plt.title("Distribuição dos estudantes por faixa de bonificação")
    plt.xlabel("Classificação de bonificação")
    plt.ylabel("Número de estudantes")
    plt.xticks(rotation=30, ha="right")

    return salvar_figura(
        "distribuicao_bonificacao",
        pasta_figures,
        config
    )


def gerar_todos_graficos(resultados, pasta_execucao, config):
    pasta_figures = os.path.join(pasta_execucao, "figures")
    os.makedirs(pasta_figures, exist_ok=True)

    caminhos = {}

    df = resultados["dados_processados"]

    caminhos["histograma"] = grafico_histograma_desempenho(
        df,
        pasta_figures,
        config
    )

    caminhos["boxplot_turma"] = grafico_boxplot_por_turma(
        df,
        pasta_figures,
        config
    )

    caminhos["media_turma"] = grafico_media_por_turma(
        resultados["analise_por_turma"],
        pasta_figures,
        config
    )

    caminhos["media_ciclo"] = grafico_media_por_ciclo(
        resultados["analise_por_ciclo"],
        pasta_figures,
        config
    )

    caminhos["areas"] = grafico_areas(
        resultados["analise_por_areas"],
        pasta_figures,
        config
    )

    caminhos["areas_por_turma"] = grafico_areas_por_turma(
        resultados["analise_areas_por_turma"],
        pasta_figures,
        config
    )

    caminhos["risco"] = grafico_risco_pedagogico(
        resultados["estudantes_em_risco"],
        pasta_figures,
        config
    )

    caminhos["bonificacao"] = grafico_bonificacao(
        resultados["bonificacao"],
        pasta_figures,
        config
    )

    return caminhos