import os
import pandas as pd

from docx import Document
from docx.shared import Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH


def adicionar_titulo(documento, texto):
    titulo = documento.add_heading(texto, level=1)
    titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER


def adicionar_subtitulo(documento, texto):
    documento.add_heading(texto, level=2)


def adicionar_paragrafo(documento, texto):
    paragrafo = documento.add_paragraph()
    paragrafo.add_run(texto)
    paragrafo.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY


def adicionar_tabela(documento, df, titulo):
    adicionar_subtitulo(documento, titulo)

    if df is None or df.empty:
        adicionar_paragrafo(documento, "Não há dados disponíveis para esta seção.")
        return

    tabela = documento.add_table(rows=1, cols=len(df.columns))
    tabela.style = "Table Grid"

    for i, coluna in enumerate(df.columns):
        tabela.rows[0].cells[i].text = str(coluna)

    for _, linha in df.iterrows():
        cells = tabela.add_row().cells
        for i, valor in enumerate(linha):
            cells[i].text = str(valor)

    documento.add_paragraph("Fonte: ENAMED Performance Analytics.")


def adicionar_figura(documento, caminho_figura, legenda):
    if caminho_figura and os.path.exists(caminho_figura):
        documento.add_picture(caminho_figura, width=Inches(6))
        paragrafo = documento.add_paragraph(legenda)
        paragrafo.alignment = WD_ALIGN_PARAGRAPH.CENTER


def gerar_texto_resumo(estatisticas, config):
    instituicao = config.get("instituicao", "Instituição de Ensino Superior")
    numero_questoes = config.get("numero_questoes", 120)

    return (
        f"O presente relatório apresenta a análise dos resultados de simulados e/ou provas "
        f"do ENAMED aplicados aos estudantes de Medicina da {instituicao}. "
        f"A prova analisada foi considerada com {numero_questoes} questões. "
        f"A base contemplou {estatisticas['total_estudantes']} estudantes. "
        f"A média geral de acertos foi de {estatisticas['media_acertos']} questões, "
        f"com mediana de {estatisticas['mediana_acertos']}, desvio-padrão de "
        f"{estatisticas['desvio_padrao_acertos']} e média percentual de "
        f"{estatisticas['media_percentual']}%. Esses indicadores subsidiam ações "
        f"do NDE, da coordenação do curso, do colegiado e dos processos de melhoria contínua."
    )


def gerar_interpretacao_turmas(tabela_turma):
    if tabela_turma.empty:
        return "Não foram identificados dados suficientes para análise por turma."

    melhor = tabela_turma.sort_values("media_percentual", ascending=False).iloc[0]
    menor = tabela_turma.sort_values("media_percentual", ascending=True).iloc[0]

    return (
        f"A turma com maior média percentual foi {melhor['turma']}, com "
        f"{melhor['media_percentual']}% de acertos. A menor média percentual foi "
        f"observada na turma {menor['turma']}, com {menor['media_percentual']}%. "
        f"Esses resultados permitem identificar desigualdades formativas e orientar "
        f"intervenções pedagógicas específicas."
    )


def gerar_interpretacao_ciclos(tabela_ciclo):
    if tabela_ciclo.empty:
        return "Não foram identificados dados suficientes para análise por ciclo."

    melhor = tabela_ciclo.sort_values("media_percentual", ascending=False).iloc[0]

    return (
        f"A análise por ciclos formativos indicou maior desempenho médio no ciclo "
        f"{melhor['ciclo']}, com {melhor['media_percentual']}% de acertos. "
        f"Essa leitura favorece o acompanhamento longitudinal da progressão cognitiva."
    )


def gerar_interpretacao_areas(tabela_areas):
    if tabela_areas is None or tabela_areas.empty:
        return "A análise por grandes áreas não foi realizada por ausência de colunas compatíveis."

    maior = tabela_areas.sort_values("media_acertos", ascending=False).iloc[0]
    menor = tabela_areas.sort_values("media_acertos", ascending=True).iloc[0]

    return (
        f"A análise por grandes áreas indicou maior desempenho médio em {maior['area']}, "
        f"com média de {maior['media_acertos']} acertos. A menor média foi observada "
        f"em {menor['area']}, com {menor['media_acertos']} acertos. "
        f"Esses achados podem direcionar revisões curriculares, oficinas de reforço "
        f"e análise pedagógica dos eixos avaliativos do ENAMED."
    )


def gerar_interpretacao_risco(tabela_risco):
    if tabela_risco.empty:
        return "Não foram identificados estudantes em risco."

    contagem = tabela_risco["classificacao_risco"].value_counts().to_dict()

    moderado = contagem.get("Risco moderado", 0)
    elevado = contagem.get("Risco elevado", 0)

    return (
        f"A análise de risco pedagógico identificou {moderado} estudantes em risco moderado "
        f"e {elevado} estudantes em risco elevado. Foram considerados em risco os estudantes "
        f"abaixo da média da própria turma: até 10% abaixo da média foram classificados como "
        f"risco moderado; 11% ou mais abaixo da média foram classificados como risco elevado."
    )


def gerar_interpretacao_bonus(tabela_bonus):
    if tabela_bonus.empty:
        return "Não foram identificados estudantes elegíveis à bonificação."

    elegiveis = tabela_bonus[tabela_bonus["bonus_total"] > 0]

    return (
        f"Foram identificados {len(elegiveis)} estudantes elegíveis à bonificação acadêmica. "
        f"Estudantes com desempenho de 1% a 9,99% acima da média da turma recebem 0,1 ponto "
        f"em uma disciplina; de 10% a 19,99%, recebem 0,2 pontos em duas disciplinas "
        f"(0,4 no total); e com 20% ou mais acima da média recebem 0,3 pontos em três "
        f"disciplinas (0,9 no total)."
    )


def gerar_plano_acao():
    return (
        "Recomenda-se que os resultados sejam discutidos em reunião do NDE e do colegiado, "
        "com registro em ata. As turmas com menor desempenho devem receber ações de reforço "
        "pedagógico. Os estudantes em risco devem ser acompanhados por tutoria, monitoria "
        "e orientação acadêmica. As áreas com menor desempenho devem subsidiar revisão "
        "curricular, oficinas de aprendizagem e análise de itens."
    )


def gerar_word(resultados, caminhos_graficos, pasta_execucao, config):
    pasta_word = os.path.join(pasta_execucao, "word")
    os.makedirs(pasta_word, exist_ok=True)

    caminho_word = os.path.join(
        pasta_word,
        "relatorio_enamed_performance_analytics.docx"
    )

    documento = Document()

    adicionar_titulo(
        documento,
        config.get("nome_relatorio", "Relatório ENAMED Performance Analytics")
    )

    adicionar_paragrafo(
        documento,
        "Sistema institucional para análise de desempenho em simulados e provas do ENAMED em escolas médicas."
    )

    adicionar_subtitulo(documento, "1. Resumo executivo")
    adicionar_paragrafo(
        documento,
        gerar_texto_resumo(resultados["estatisticas_gerais"], config)
    )

    adicionar_tabela(
        documento,
        pd.DataFrame([resultados["estatisticas_gerais"]]),
        "Tabela 1 – Estatísticas gerais do desempenho"
    )

    adicionar_subtitulo(documento, "2. Desempenho por turma")
    adicionar_paragrafo(
        documento,
        gerar_interpretacao_turmas(resultados["analise_por_turma"])
    )

    adicionar_tabela(
        documento,
        resultados["analise_por_turma"],
        "Tabela 2 – Indicadores por turma"
    )

    if caminhos_graficos.get("media_turma"):
        adicionar_figura(
            documento,
            caminhos_graficos["media_turma"][0],
            "Figura 1 – Média percentual de acertos por turma."
        )

    adicionar_subtitulo(documento, "3. Desempenho por ciclo")
    adicionar_paragrafo(
        documento,
        gerar_interpretacao_ciclos(resultados["analise_por_ciclo"])
    )

    adicionar_tabela(
        documento,
        resultados["analise_por_ciclo"],
        "Tabela 3 – Indicadores por ciclo formativo"
    )

    adicionar_subtitulo(documento, "4. Grandes áreas do ENAMED")
    adicionar_paragrafo(
        documento,
        gerar_interpretacao_areas(resultados["analise_por_areas"])
    )

    adicionar_tabela(
        documento,
        resultados["analise_por_areas"],
        "Tabela 4 – Desempenho por grandes áreas"
    )

    adicionar_tabela(
        documento,
        resultados["analise_areas_por_turma"],
        "Tabela 5 – Desempenho por área e turma"
    )

    adicionar_subtitulo(documento, "5. Estudantes em risco")
    adicionar_paragrafo(
        documento,
        gerar_interpretacao_risco(resultados["estudantes_em_risco"])
    )

    adicionar_tabela(
        documento,
        resultados["estudantes_em_risco"],
        "Tabela 6 – Classificação de risco pedagógico"
    )

    adicionar_subtitulo(documento, "6. Bonificação acadêmica")
    adicionar_paragrafo(
        documento,
        gerar_interpretacao_bonus(resultados["bonificacao"])
    )

    adicionar_tabela(
        documento,
        resultados["bonificacao"],
        "Tabela 7 – Bonificação acadêmica por estudante"
    )

    adicionar_subtitulo(documento, "7. Plano de ação pedagógico")
    adicionar_paragrafo(documento, gerar_plano_acao())

    documento.save(caminho_word)

    return caminho_word