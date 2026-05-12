import json
import os
from datetime import datetime


def carregar_configuracao(caminho_config="config/config.json"):
    """
    Carrega o arquivo de configuração do projeto.
    """

    if not os.path.exists(caminho_config):
        raise FileNotFoundError(
            f"Arquivo de configuração não encontrado: {caminho_config}"
        )

    with open(caminho_config, "r", encoding="utf-8") as arquivo:
        config = json.load(arquivo)

    return config


def criar_pasta_execucao(base_outputs="outputs"):
    """
    Cria uma pasta única para cada execução do sistema.
    """

    agora = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    pasta_execucao = os.path.join(base_outputs, f"execucao_{agora}")

    subpastas = [
        "excel",
        "word",
        "figures",
        "tables",
        "csv"
    ]

    os.makedirs(pasta_execucao, exist_ok=True)

    for subpasta in subpastas:
        os.makedirs(os.path.join(pasta_execucao, subpasta), exist_ok=True)

    return pasta_execucao


def salvar_csv(df, caminho_saida):
    """
    Salva um DataFrame em CSV.
    """

    df.to_csv(caminho_saida, index=False, encoding="utf-8-sig")


def identificar_colunas_area(df, config):
    """
    Identifica quais colunas de área existem na planilha com base no config.json.
    """

    areas_detectadas = {}

    for area, colunas in config["areas"].items():
        colunas_encontradas = []

        for coluna in colunas:
            coluna_padronizada = (
                coluna.strip()
                .replace(" ", "_")
                .replace("-", "_")
                .replace("/", "_")
                .lower()
            )

            if coluna_padronizada in df.columns:
                colunas_encontradas.append(coluna_padronizada)

        if colunas_encontradas:
            areas_detectadas[area] = colunas_encontradas

    return areas_detectadas


def normalizar_texto(valor):
    """
    Normaliza textos simples para comparação.
    """

    if valor is None:
        return ""

    return str(valor).strip().lower()


def detectar_ciclo(periodo, config):
    """
    Detecta o ciclo formativo a partir do período do estudante.
    """

    periodo_texto = str(periodo).strip()

    for ciclo, periodos in config["ciclos"].items():
        if periodo_texto in [str(p).strip() for p in periodos]:
            return ciclo

    return "Nao identificado"


def caminho_seguro(nome):
    """
    Remove caracteres problemáticos para nomes de arquivos.
    """

    caracteres_invalidos = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']

    nome_limpo = str(nome)

    for caractere in caracteres_invalidos:
        nome_limpo = nome_limpo.replace(caractere, "_")

    return nome_limpo.strip()