import os
import traceback

from src.leitor_planilha import preparar_dados
from src.utilitarios import carregar_configuracao, criar_pasta_execucao, salvar_csv
from src.analisador_enamed import executar_analise_completa
from src.gerador_graficos import gerar_todos_graficos
from src.gerador_excel import gerar_excel
from src.gerador_word import gerar_word


def exibir_cabecalho():
    print("=" * 70)
    print("ENAMED PERFORMANCE ANALYTICS")
    print("Análise de simulados e provas ENAMED para escolas médicas")
    print("=" * 70)


def salvar_bases_csv(resultados, pasta_execucao):
    pasta_csv = os.path.join(pasta_execucao, "csv")
    os.makedirs(pasta_csv, exist_ok=True)

    salvar_csv(
        resultados["dados_processados"],
        os.path.join(pasta_csv, "dados_processados.csv")
    )

    salvar_csv(
        resultados["ranking_geral"],
        os.path.join(pasta_csv, "ranking_geral.csv")
    )

    salvar_csv(
        resultados["ranking_por_turma"],
        os.path.join(pasta_csv, "ranking_por_turma.csv")
    )

    salvar_csv(
        resultados["analise_por_turma"],
        os.path.join(pasta_csv, "analise_por_turma.csv")
    )

    salvar_csv(
        resultados["analise_por_ciclo"],
        os.path.join(pasta_csv, "analise_por_ciclo.csv")
    )

    salvar_csv(
        resultados["analise_por_areas"],
        os.path.join(pasta_csv, "analise_por_areas.csv")
    )

    salvar_csv(
        resultados["estudantes_em_risco"],
        os.path.join(pasta_csv, "estudantes_em_risco.csv")
    )

    salvar_csv(
        resultados["bonificacao"],
        os.path.join(pasta_csv, "bonificacao.csv")
    )


def main():
    exibir_cabecalho()

    try:
        print("\nCarregando configurações do sistema...")
        config = carregar_configuracao("config/config.json")

        print("Criando pasta da execução...")
        pasta_execucao = criar_pasta_execucao("outputs")

        print("\nSelecione a planilha do simulado ou prova ENAMED.")
        df, caminho_planilha = preparar_dados()

        print(f"\nPlanilha carregada com sucesso:")
        print(caminho_planilha)

        print("\nExecutando análises estatísticas...")
        resultados = executar_analise_completa(df, config)

        print("Salvando bases CSV...")
        salvar_bases_csv(resultados, pasta_execucao)

        print("Gerando gráficos...")
        caminhos_graficos = gerar_todos_graficos(
            resultados,
            pasta_execucao,
            config
        )

        print("Gerando Excel analítico...")
        caminho_excel = gerar_excel(
            resultados,
            pasta_execucao,
            config
        )

        print("Gerando relatório Word...")
        caminho_word = gerar_word(
            resultados,
            caminhos_graficos,
            pasta_execucao,
            config
        )

        print("\n" + "=" * 70)
        print("ANÁLISE FINALIZADA COM SUCESSO")
        print("=" * 70)

        print(f"\nPasta da execução:")
        print(pasta_execucao)

        print(f"\nExcel gerado:")
        print(caminho_excel)

        print(f"\nRelatório Word gerado:")
        print(caminho_word)

        print("\nArquivos CSV e gráficos também foram salvos na pasta da execução.")

    except Exception as erro:
        print("\n" + "=" * 70)
        print("ERRO DURANTE A EXECUÇÃO")
        print("=" * 70)
        print(f"\nErro: {erro}")
        print("\nDetalhes técnicos:")
        traceback.print_exc()

        print(
            "\nVerifique se a planilha contém, no mínimo, as colunas: "
            "aluno, turma, periodo e acertos."
        )


if __name__ == "__main__":
    main()