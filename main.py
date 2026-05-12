import os
import traceback

from src.leitor_planilha import preparar_dados
from src.utilitarios import carregar_configuracao, criar_pasta_execucao, salvar_csv
from src.analisador_enamed import executar_analise_completa
from src.gerador_graficos import gerar_todos_graficos
from src.gerador_excel import gerar_excel
from src.gerador_word import gerar_word


def exibir_cabecalho():
    print("=" * 80)
    print("ENAMED PERFORMANCE ANALYTICS")
    print("Análise de simulados e provas ENAMED para escolas médicas")
    print("Modelo configurado para 120 questões")
    print("=" * 80)


def salvar_bases_csv(resultados, pasta_execucao):
    pasta_csv = os.path.join(pasta_execucao, "csv")
    os.makedirs(pasta_csv, exist_ok=True)

    for nome, tabela in resultados.items():
        if hasattr(tabela, "to_csv"):
            salvar_csv(tabela, os.path.join(pasta_csv, f"{nome}.csv"))


def main():
    exibir_cabecalho()

    try:
        config = carregar_configuracao("config/config.json")
        pasta_execucao = criar_pasta_execucao("outputs")

        print("\nSelecione a planilha do simulado ou prova ENAMED.")
        df, caminho_planilha = preparar_dados()

        print("\nPlanilha carregada:")
        print(caminho_planilha)

        print("\nExecutando análise completa...")
        resultados = executar_analise_completa(df, config)

        print("Salvando arquivos CSV...")
        salvar_bases_csv(resultados, pasta_execucao)

        print("Gerando gráficos...")
        caminhos_graficos = gerar_todos_graficos(
            resultados,
            pasta_execucao,
            config
        )

        print("Gerando Excel analítico...")
        caminho_excel = gerar_excel(resultados, pasta_execucao, config)

        print("Gerando relatório Word...")
        caminho_word = gerar_word(
            resultados,
            caminhos_graficos,
            pasta_execucao,
            config
        )

        print("\n" + "=" * 80)
        print("ANÁLISE FINALIZADA COM SUCESSO")
        print("=" * 80)

        print("\nPasta da execução:")
        print(pasta_execucao)

        print("\nExcel gerado:")
        print(caminho_excel)

        print("\nRelatório Word gerado:")
        print(caminho_word)

    except Exception as erro:
        print("\n" + "=" * 80)
        print("ERRO DURANTE A EXECUÇÃO")
        print("=" * 80)
        print(f"\nErro: {erro}")
        print("\nDetalhes técnicos:")
        traceback.print_exc()

        print(
            "\nVerifique se a planilha contém colunas compatíveis com o modelo:\n"
            "ALUNOS | Período | CLÍNICA MÉDICA | PEDIATRIA | CIRURGIA | "
            "GINECO/OBS | SAÚDE COLETIVA"
        )


if __name__ == "__main__":
    main()