import os
import matplotlib.pyplot as plt


def salvar_figura(nome_arquivo, pasta_figures, config):
    """
    Salva a figura em PNG e, opcionalmente, SVG.
    """

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
    """
    Gera histograma do percentual de acertos dos estudantes.
    """

    plt.figure(figsize=(10, 6))
    plt.hist(df["percentual_acertos"], bins=10, edgecolor="black")

    plt.title("Distribuição do desempenho percentual dos estudantes")
    plt.xlabel("Percentual de acertos")
    plt.ylabel("Número de estudantes")

    return salvar_figura("histograma_desempenho_percentual", pasta_figures, config)


def grafico_boxplot_por_turma(df, pasta_figures, config):
    """
    Gera boxplot do desempenho percentual por turma.
    """

    turmas = sorted(df["turma"].dropna().unique())
    dados = [df[df["turma"] == turma]["percentual_acertos"] for turma in turmas]

    plt.figure(figsize=(12, 6))
    plt.boxplot(dados, labels=turmas, showmeans=True)

    plt.title("Distribuição do desempenho percentual por turma")
    plt.xlabel("Turma")
    plt.ylabel("Percentual de acertos")
    plt.xticks(rotation=45)

    return salvar_figura("boxplot_desempenho_por_turma", pasta_figures, config)


def grafico_media_por_turma(tabela_turma, pasta_figures, config):
    """
    Gera gráfico de barras com média percentual por turma.
    """

    tabela = tabela_turma.sort_values("media_percentual", ascending=False)

    plt.figure(figsize=(12, 6))
    plt.bar(tabela["turma"].astype(str), tabela["media_percentual"])

    plt.title("Média percentual de acertos por turma")
    plt.xlabel("Turma")
    plt.ylabel("Média percentual de acertos")
    plt.xticks(rotation=45)

    return salvar_figura("media_percentual_por_turma", pasta_figures, config)


def grafico_media_por_ciclo(tabela_ciclo, pasta_figures, config):
    """
    Gera gráfico de barras com média percentual por ciclo formativo.
    """

    tabela = tabela_ciclo.sort_values("media_percentual", ascending=False)

    plt.figure(figsize=(10, 6))
    plt.bar(tabela["ciclo"].astype(str), tabela["media_percentual"])

    plt.title("Média percentual de acertos por ciclo formativo")
    plt.xlabel("Ciclo formativo")
    plt.ylabel("Média percentual de acertos")

    return salvar_figura("media_percentual_por_ciclo", pasta_figures, config)


def grafico_areas(tabela_areas, pasta_figures, config):
    """
    Gera gráfico de barras com desempenho médio por grande área do ENAMED.
    """

    if tabela_areas.empty:
        return None, None

    tabela = tabela_areas.sort_values("media_percentual", ascending=False)

    plt.figure(figsize=(12, 6))
    plt.bar(tabela["area"], tabela["media_percentual"])

    plt.title("Desempenho médio por grande área do ENAMED")
    plt.xlabel("Grande área")
    plt.ylabel("Média percentual de acertos")
    plt.xticks(rotation=45, ha="right")

    return salvar_figura("desempenho_medio_por_area", pasta_figures, config)


def grafico_risco_pedagogico(tabela_risco, pasta_figures, config):
    """
    Gera gráfico de barras com quantidade de estudantes por classificação de risco.
    """

    contagem = (
        tabela_risco["classificacao_risco"]
        .value_counts()
        .reset_index()
    )

    contagem.columns = ["classificacao_risco", "quantidade"]

    plt.figure(figsize=(10, 6))
    plt.bar(contagem["classificacao_risco"], contagem["quantidade"])

    plt.title("Distribuição dos estudantes por classificação de risco")
    plt.xlabel("Classificação de risco")
    plt.ylabel("Número de estudantes")
    plt.xticks(rotation=30, ha="right")

    return salvar_figura("distribuicao_risco_pedagogico", pasta_figures, config)


def gerar_todos_graficos(resultados, pasta_execucao, config):
    """
    Gera todos os gráficos do relatório.
    """

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

    caminhos["risco"] = grafico_risco_pedagogico(
        resultados["estudantes_em_risco"],
        pasta_figures,
        config
    )

    return caminhos