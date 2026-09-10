#!/usr/bin/env python
# coding: utf-8

# # Bibliotecas

# In[ ]:


# =========================
# BIBLIOTECAS DO SELENIUM
# =========================

from selenium.common.exceptions import NoSuchElementException

# Controla o navegador.
from selenium import webdriver

# Configura o ChromeDriver.
from selenium.webdriver.chrome.service import Service

# Configura opções do navegador Chrome.
from selenium.webdriver.chrome.options import Options

# Localiza elementos na página.
from selenium.webdriver.common.by import By

# Cria esperas explícitas.
from selenium.webdriver.support.ui import WebDriverWait

# Define condições para as esperas explícitas.
from selenium.webdriver.support import expected_conditions as EC

# Executa ações com mouse e teclado.
from selenium.webdriver.common.action_chains import ActionChains

# Manipula elementos HTML do tipo <select>.
from selenium.webdriver.support.ui import Select

# Exceções do Selenium.
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    WebDriverException,
)

# Baixa e configura automaticamente o ChromeDriver.
# Comente esta importação quando utilizar Docker.
from webdriver_manager.chrome import ChromeDriverManager


# =========================
# BIBLIOTECAS DO PYTHON
# =========================

# Cria pausas durante a automação.
import time

# Lê arquivos de configuração TOML.
import tomllib

# Trabalha com caminhos de arquivos e diretórios.
from pathlib import Path


# =========================
# TRATAMENTO DE DADOS
# =========================

# Trabalha com DataFrames.
import pandas as pd


# =========================
# BANCO DE DADOS
# =========================

# Conecta ao PostgreSQL.
import psycopg2

# Permite importar funções de arquivos Jupyter Notebook.
#import import_ipynb

# Importa a função responsável pela inserção no banco.
from .db_joaquina import inserir_dados


# # def localizar_raiz_projeto

# In[ ]:


def localizar_raiz_projeto():

    pasta_atual = Path.cwd().resolve()

    for pasta in [
        pasta_atual,
        *pasta_atual.parents
    ]:

        if (
            (pasta / "requirements.txt").exists()
            and
            (pasta / "src").exists()
        ):
            return pasta

    raise FileNotFoundError(
        "Não foi possível localizar a raiz do projeto."
    )


PROJETO_RH = localizar_raiz_projeto()

CAMINHO_CONFIG = (
    PROJETO_RH /
    "config.toml"
)

print(
    f"Raiz do projeto: {PROJETO_RH}"
)

print(
    f"Config encontrado: {CAMINHO_CONFIG.exists()}"
)


# # def config_navegador()
# - configura a forma que o navegador irá agir após ser iniciado

# In[ ]:


def config_navegador():
    chrome_options = Options()

    # Desativa as notificações do Chrome
    chrome_options.add_argument("--disable-notifications")

    # Desabilita o bloqueio de popup
    chrome_options.add_argument("--disable-popup-blocking")

    # Chrome inicia com tela cheia
    chrome_options.add_argument("--start-maximized")

    # Configura o serviço do ChromeDriver
    service = Service(ChromeDriverManager().install())

    # Cria o navegador controlado pelo Selenium
    driver = webdriver.Chrome(
        service=service,
        options=chrome_options

        # Cria uma espera explícita de até 10 segundos
    )
    wait = WebDriverWait(
        driver, 10
        )

    return driver, wait


# # def abrir_navegador()
# - Abre o navegador baseado na URL dele

# In[ ]:


# Cria o navegador usando a função config_navegador()
# O resultado da função, que é o driver do Selenium, fica guardado na variável driver


# Define uma função chamada abre_navegador
# Essa função recebe como parâmetro o driver, ou seja, o navegador que será controlado pelo Selenium
def abre_navegador(driver):

    # Abre o site informado no navegador
    # O método get() faz o navegador acessar a URL passada entre parênteses
    driver.get("https://adm.pmf.sc.gov.br/admin/index.php?pagina=")


# # def login_joaquina(driver)
# - Acesso dados sensiveis para fazer o login dentro do sistema
# - insere esses dados no campo solicitado e clica para entrar

# In[ ]:


def login_joaquina(driver, wait):

    # Carrega o arquivo config.toml.
    with open(CAMINHO_CONFIG, "rb") as acessos:
        config = tomllib.load(acessos)

    # Acessa a seção [acessos_joaquina].
    acesso = config["acessos_joaquina"]

    user = acesso["user"]
    password = acesso["password"]

    # Aguarda o campo de usuário ficar visível.
    usuario = wait.until(
        EC.visibility_of_element_located(
            (By.NAME, "usuario")
        )
    )

    usuario.clear()
    usuario.send_keys(user)

    # Aguarda o campo de senha ficar visível.
    senha = wait.until(
        EC.visibility_of_element_located(
            (By.NAME, "senha")
        )
    )

    senha.clear()
    senha.send_keys(password)

    # Aguarda o botão ENTRAR ficar presente.
    botao_entrar = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//input[@value='ENTRAR']")
        )
    )

    # Centraliza o botão na tela.
    driver.execute_script(
        """
        arguments[0].scrollIntoView({
            block: "center"
        });
        """,
        botao_entrar
    )

    # Aguarda o botão ficar clicável.
    botao_entrar = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//input[@value='ENTRAR']")
        )
    )

    try:
        botao_entrar.click()

    except ElementClickInterceptedException:
        driver.execute_script(
            "arguments[0].click();",
            botao_entrar
        )


# # def busca_funcionario

# In[ ]:


def busca_funcionario(driver, wait):

    # Garante que o Selenium está na página principal
    # Isso evita erro caso ele já esteja dentro de outro frame
    driver.switch_to.default_content()

    # Aguarda o frame chamado "menu" estar disponível
    # Quando estiver disponível, o Selenium entra automaticamente nele
    wait.until(
        EC.frame_to_be_available_and_switch_to_it((By.NAME, "menu"))
    )

    # Aguarda o campo de pesquisa do menu ficar clicável
    campo_pesquisa = wait.until(
        EC.element_to_be_clickable((
            By.CSS_SELECTOR,
            '#mmenu > div.mm-navbars_top.mm-navbars_has-tabs > div:nth-child(1) > div > div > div > input[type=text]'
        ))
    )

    # Limpa o campo de pesquisa antes de digitar
    campo_pesquisa.clear()

    # Digita "funcionario" no campo de pesquisa
    campo_pesquisa.send_keys("funcionario")

    # Aguarda o resultado da pesquisa ficar clicável
    funcionario = wait.until(
        EC.element_to_be_clickable((
            By.CSS_SELECTOR,
            '#mmenu > div.mm-panels > div.mm-panel.mm-panel_search.mm-panel_noanimation.mm-panel_opened > ul > li:nth-child(9) > a'
        ))
    )

    # Clica no resultado encontrado
    funcionario.click()


# # def pesquisar_funcionario_por_nome

# In[ ]:


def pesquisar_funcionario_por_nome(
        driver,
        wait,
        nome_servidor
):

    driver.switch_to.default_content()

    wait.until(
        EC.frame_to_be_available_and_switch_to_it(
            (By.NAME, "principal")
        )
    )

    campo_tipo_pesquisa = wait.until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "select")
        )
    )

    select = Select(
        campo_tipo_pesquisa
    )

    # Pesquisa por nome
    select.select_by_index(1)

    campo_nome = wait.until(
        EC.element_to_be_clickable(
            (By.ID, "valorconsulta")
        )
    )

    campo_nome.clear()

    campo_nome.send_keys(
        nome_servidor
    )

    botao_pesquisar = wait.until(
        EC.element_to_be_clickable(
            (
                By.CSS_SELECTOR,
                "input[type=button]:nth-child(13)"
            )
        )
    )

    botao_pesquisar.click()


# # obter dados da tabela

# # def pegar_tabelas

# In[ ]:


def pegar_tabelas(driver):
    # Define uma função chamada pegar_tabelas
    # Essa função recebe o driver do Selenium como parâmetro
    # O driver representa o navegador controlado pelo Selenium

    """
    Busca todas as tabelas <table> existentes na página atual.
    """

    # Procura todos os elementos HTML com a tag <table> na página atual
    tabelas = driver.find_elements(By.TAG_NAME, "table")

    # Mostra no terminal quantas tabelas foram encontradas
    print(f"Quantidade de tabelas encontradas: {len(tabelas)}")

    # Retorna a lista de tabelas encontradas
    return tabelas


# # def pegar_tabela_por_indice

# In[ ]:


def pegar_tabela_por_indice(driver, indice_tabela=2):
    # Define uma função chamada pegar_tabela_por_indice
    # Recebe o driver do Selenium
    # Recebe também o índice da tabela desejada
    # O valor padrão é 2, ou seja, a terceira tabela da página

    """
    Busca todas as tabelas da página e retorna uma tabela específica pelo índice.
    """

    # Chama a função pegar_tabelas para buscar todas as tabelas da página
    tabelas = pegar_tabelas(driver)

    # Verifica se o índice informado existe dentro da lista de tabelas
    if len(tabelas) <= indice_tabela:

        # Mostra mensagem de erro caso o índice não exista
        print(f"Erro: não existe tabela no índice {indice_tabela}.")

        # Mostra quantas tabelas estão disponíveis
        print(f"Total de tabelas disponíveis: {len(tabelas)}")

        # Retorna None para indicar que nenhuma tabela válida foi encontrada
        return None

    # Seleciona a tabela desejada usando o índice informado
    tabela = tabelas[indice_tabela]

    # Retorna a tabela selecionada
    return tabela


# # def limpar_texto

# In[ ]:


def limpar_texto(texto):
    # Define uma função chamada limpar_texto
    # Essa função recebe um texto e devolve esse texto limpo

    """
    Limpa o texto removendo quebras de linha, espaços especiais e espaços extras.
    """

    # Verifica se o texto recebido é None
    if texto is None:

        # Se o texto for None, retorna None
        return None

    # Remove espaços no começo e no final do texto
    texto = texto.strip()

    # Substitui quebras de linha por espaço comum
    texto = texto.replace("\n", " ")

    # Substitui espaços especiais de HTML por espaço comum
    texto = texto.replace("\xa0", " ")

    # Remove novamente espaços no começo e no final após as substituições
    texto = texto.strip()

    # Verifica se depois da limpeza o texto ficou vazio
    if texto == "":

        # Se estiver vazio, retorna None para representar ausência de valor
        return None

    # Retorna o texto limpo
    return texto


# # def pegar_cabecalhos

# In[ ]:


def pegar_cabecalhos(tabela):

    """
    Extrai os cabeçalhos <th> da tabela.
    """

    cabecalhos = []

    ths = tabela.find_elements(
        By.TAG_NAME,
        "th"
    )

    for th in ths:

        try:
            texto = th.find_element(
                By.TAG_NAME,
                "a"
            ).text

        except NoSuchElementException:
            texto = th.text

        texto = limpar_texto(texto)

        if texto is not None:
            cabecalhos.append(texto)

    print("Cabeçalhos encontrados:")
    print(cabecalhos)

    return cabecalhos


# # def pegar_linhas

# In[ ]:


def pegar_linhas(tabela):

    """
    Busca todas as linhas <tr> dentro da tabela.
    """

    linhas = tabela.find_elements(
        By.TAG_NAME,
        "tr"
    )

    print(f"Total de linhas é {len(linhas)}")

    if len(linhas) == 3:
        print("Servidor não encontrado")

    return linhas


# # def extrair_dados_linhas

# In[ ]:


def extrair_dados_linhas(linhas, cabecalhos):
    # Define uma função chamada extrair_dados_linhas
    # Recebe as linhas da tabela
    # Recebe também os cabeçalhos da tabela

    """
    Percorre as linhas da tabela e extrai os valores das células <td>.
    """

    # Cria uma lista vazia para armazenar todas as linhas extraídas
    dados = []

    # Percorre cada linha da lista de linhas
    for linha in linhas:

        # Dentro da linha atual, busca todas as células <td>
        # Cada <td> representa uma coluna de dados
        colunas = linha.find_elements(By.TAG_NAME, "td")

        # Verifica se a quantidade de células da linha é igual à quantidade de cabeçalhos
        # Isso evita pegar linhas quebradas, títulos ou rodapés da tabela
        if len(colunas) == len(cabecalhos):

            # Cria uma lista vazia para armazenar os valores da linha atual
            valores = []

            # Percorre cada célula encontrada na linha atual
            for coluna in colunas:

                # Pega o texto visível da célula
                texto = coluna.text

                # Limpa o texto usando a função limpar_texto
                texto = limpar_texto(texto)

                # Adiciona o texto tratado na lista de valores da linha atual
                valores.append(texto)

            # Adiciona a linha completa na lista principal de dados
            dados.append(valores)

    # Retorna todos os dados extraídos da tabela
    return dados


# # def criar_dataframe

# In[ ]:


def criar_dataframe(
        dados,
        cabecalhos
):

    # Define uma função chamada criar_dataframe
    # Recebe os dados extraídos da tabela
    # Recebe também os cabeçalhos que serão usados como nomes das colunas

    """
    Cria um DataFrame com os dados extraídos da tabela.
    """

    # Cria um DataFrame usando os dados como linhas
    # e os cabeçalhos como nomes das colunas
    df = pd.DataFrame(
        dados,
        columns=cabecalhos
    )

    # Mostra o DataFrame criado no terminal
    print(df)

    # Mostra a lista de colunas do DataFrame
    print(
        df.columns.tolist()
    )

    # Retorna o DataFrame criado
    return df


# # def tratar_matricula

# In[ ]:


def tratar_matricula(df):

    # Verifica se existe uma coluna chamada Matrícula no DataFrame
    if "Matrícula" in df.columns:

        # Converte a coluna Matrícula para texto
        df["Matrícula"] = df["Matrícula"].astype(str)

        # Remove pontos existentes nas matrículas
        df["Matrícula"] = df["Matrícula"].str.replace(
            ".",
            "",
            regex=False
        )

        # Remove espaços no início e no final das matrículas
        df["Matrícula"] = df["Matrícula"].str.strip()

    # Caso a coluna Matrícula não exista
    else:

        # Mostra mensagem informando que a coluna não foi encontrada
        print(
            "Coluna Matrícula não encontrada."
        )

        # Mostra as colunas disponíveis no DataFrame
        print(
            "Colunas disponíveis:",
            df.columns.tolist()
        )

    # Retorna o DataFrame tratado
    return df


# # def tratar_lotacao

# In[ ]:


def tratar_lotacao(df):

    # Verifica se existe uma coluna chamada Lotação no DataFrame
    if "Lotação" in df.columns:

        # Converte a coluna Lotação para texto
        df["Lotação"] = df["Lotação"].astype(str)

        # Remove espaços extras no início e no final
        df["Lotação"] = df["Lotação"].str.strip()

    # Caso a coluna Lotação não exista
    else:

        # Mostra mensagem informando que a coluna não foi encontrada
        print(
            "Coluna Lotação não encontrada."
        )

        # Mostra as colunas disponíveis no DataFrame
        print(
            "Colunas disponíveis:",
            df.columns.tolist()
        )

    # Retorna o DataFrame tratado
    return df


# # def converter_colunas_datas

# In[ ]:


def converter_datas_funcionarios(df):

    # Cria uma lista com os nomes das colunas que devem ser convertidas para data
    colunas_datas = [
        "Admissão",
        "Aposentadoria/Pensão",
        "Entrada na Lotação",
        "Término",
        "Desligamento"
    ]

    # Percorre cada coluna da lista de datas
    for coluna in colunas_datas:

        # Verifica se a coluna existe no DataFrame
        if coluna in df.columns:

            # Converte a coluna para data no formato dia/mês/ano
            df[coluna] = pd.to_datetime(
                df[coluna],
                format="%d/%m/%Y",
                errors="coerce"
            )

        # Caso a coluna não exista no DataFrame
        else:

            # Mostra qual coluna de data não foi encontrada
            print(
                f"Coluna de data não encontrada: {coluna}"
            )

    # Retorna o DataFrame com as datas convertidas
    return df


# # def limpar_dataframe

# In[ ]:


def limpar_dataframe(df):

    # Define uma função chamada limpar_dataframe
    # Essa função recebe um DataFrame
    # Ela centraliza todos os tratamentos em um único lugar

    """
    Aplica todos os tratamentos necessários no DataFrame.
    """

    # Chama a função que trata a matrícula
    df = tratar_matricula(
        df
    )

    # Chama a função que trata a lotação
    df = tratar_lotacao(
        df
    )

    # Chama a função que converte colunas de data
    df = converter_datas_funcionarios(
        df
    )

    # Retorna o DataFrame depois de todos os tratamentos
    return df


# # FUNÇÃO PRINCIPAL PANDAS (def tabela_html_para_dataframe)

# In[ ]:


def gerar_dataframe_funcionarios(driver):

    # Mostra mensagem indicando início do processo
    print(
        "Iniciando captura dos funcionários..."
    )

    # Pega a tabela 2, que é a tabela real dos funcionários
    tabela_funcionarios = pegar_tabela_por_indice(
        driver
    )

    # Verifica se a tabela de funcionários não foi encontrada
    if tabela_funcionarios is None:

        # Mostra mensagem informando que não foi possível continuar
        print(
            "Não foi possível gerar o DataFrame porque "
            "a tabela de funcionários não foi encontrada."
        )

        # Retorna um DataFrame vazio
        return pd.DataFrame()

    # Pega os cabeçalhos da tabela de funcionários
    cabecalhos = pegar_cabecalhos(
        tabela_funcionarios
    )

    # Verifica se nenhum cabeçalho foi encontrado
    if len(cabecalhos) == 0:

        # Mostra mensagem informando que não há cabeçalhos
        print(
            "Nenhum cabeçalho foi encontrado "
            "na tabela de funcionários."
        )

        # Retorna um DataFrame vazio
        return pd.DataFrame()

    # Pega as linhas da tabela de funcionários
    linhas = pegar_linhas(
        tabela_funcionarios
    )

    # Extrai os dados das linhas
    dados = extrair_dados_linhas(
        linhas,
        cabecalhos
    )

    # Verifica se nenhum dado foi capturado
    if len(dados) == 0:

        # Mostra mensagem informando que nenhum registro foi encontrado
        print(
            "Nenhum dado foi capturado "
            "da tabela de funcionários."
        )

        # Retorna um DataFrame vazio, mas já com os cabeçalhos
        return pd.DataFrame(
            columns=cabecalhos
        )

    # Cria o DataFrame com os dados capturados
    df = criar_dataframe(
        dados,
        cabecalhos
    )

    # Aplica os tratamentos no DataFrame
    df = limpar_dataframe(
        df
    )

    # Mostra mensagem antes de exibir o resultado final
    print(
        "DataFrame final tratado:"
    )

    # Exibe o DataFrame final completo
    print(
        df.to_string()
    )

    # Retorna o DataFrame final
    return df


# .
# 

# # chama a tabela em pandas

# In[ ]:


def chama_tabela_pd(driver):

    # Gera o DataFrame com os funcionários encontrados
    # utilizando o navegador recebido pela função
    df = gerar_dataframe_funcionarios(
        driver
    )

    # Verifica se o DataFrame está vazio
    if df.empty:

        # Mostra mensagem informando que nenhum dado será inserido
        print(
            "O DataFrame está vazio. "
            "Nenhum dado será inserido no banco."
        )

        # Retorna o DataFrame vazio
        return df

    # Mostra o DataFrame completo no terminal
    print(
        df.to_string()
    )

    # Mostra as colunas existentes antes da alteração dos nomes
    print(
        "Colunas antes do rename:"
    )

    # Mostra a lista de colunas
    print(
        df.columns.tolist()
    )

    # Renomeia as colunas para os nomes utilizados no banco de dados
    df = df.rename(
        columns={
            "Matrícula": "matricula",
            "Nome": "nome",
            "Código do Cargo": "cod_cargo",
            "Cargo": "cargo",
            "Código da Lotação": "cod_lotacao",
            "Lotação": "lotacao",
            "Admissão": "admissao",
            "Aposentadoria/Pensão": "aposentadoria",
            "Entrada na Lotação": "entrada_lotacao",
            "Término": "termino",
            "Desligamento": "desligamento",
            "Regime": "regime"
        }
    )

    # Mostra as colunas existentes depois da alteração dos nomes
    print(
        "Colunas depois do rename:"
    )

    # Mostra a nova lista de colunas
    print(
        df.columns.tolist()
    )

    # Define as colunas obrigatórias para realizar a inserção no banco
    colunas_obrigatorias = {
        "matricula",
        "nome",
        "cod_cargo",
        "cargo",
        "cod_lotacao",
        "lotacao",
        "regime"
    }

    # Verifica se alguma coluna obrigatória está faltando
    colunas_faltantes = (
        colunas_obrigatorias - set(df.columns)
    )

    # Caso existam colunas obrigatórias faltando
    if colunas_faltantes:

        # Mostra quais colunas estão faltando
        print(
            "Não foi possível inserir os dados. "
            f"Colunas ausentes: "
            f"{sorted(colunas_faltantes)}"
        )

        # Retorna o DataFrame sem realizar a inserção
        return df

    # Insere os dados tratados no banco de dados
    resultado_insercao = inserir_dados(
        df_dados_do_servidor=df
    )

    # Verifica se os dados foram inseridos com sucesso
    if resultado_insercao:

        # Mostra mensagem de sucesso
        print(
            "Dados inseridos no banco com sucesso."
        )

    # Caso a inserção não tenha sido realizada
    else:

        # Mostra mensagem de erro
        print(
            "Não foi possível inserir os dados no banco."
        )

    # Retorna o DataFrame tratado
    return df


# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# # main

# In[ ]:


# ------------------------------------------------------------------- #
# EXECUÇÃO DO SCRAPING JOAQUINA
# ------------------------------------------------------------------- #

def executar_scraping_joaquina(nome_servidor):

    print(
        "Iniciando sistema de busca de funcionário."
    )

    driver = None

    try:

        driver, wait = config_navegador()

        abre_navegador(
            driver
        )

        login_joaquina(
            driver,
            wait
        )

        busca_funcionario(
            driver,
            wait
        )

        pesquisar_funcionario_por_nome(
            driver=driver,
            wait=wait,
            nome_servidor=nome_servidor
        )

        df = gerar_dataframe_funcionarios(
            driver
        )

        if df.empty:

            print(
                "O DataFrame está vazio. "
                "Nenhum dado será inserido no banco."
            )

            return df

        print(
            "Colunas antes do rename:"
        )

        print(
            df.columns.tolist()
        )

        df = df.rename(
            columns={
                "Matrícula": "matricula",
                "Nome": "nome",
                "Código do Cargo": "cod_cargo",
                "Cargo": "cargo",
                "Código da Lotação": "cod_lotacao",
                "Lotação": "lotacao",
                "Admissão": "admissao",
                "Aposentadoria/Pensão": "aposentadoria",
                "Entrada na Lotação": "entrada_lotacao",
                "Término": "termino",
                "Desligamento": "desligamento",
                "Regime": "regime"
            }
        )

        print(
            "Colunas depois do rename:"
        )

        print(
            df.columns.tolist()
        )

        print(
            df.to_string()
        )

        colunas_obrigatorias = {
            "matricula",
            "nome",
            "cod_cargo",
            "cargo",
            "cod_lotacao",
            "lotacao",
            "regime"
        }

        colunas_faltantes = (
            colunas_obrigatorias - set(df.columns)
        )

        if colunas_faltantes:

            print(
                "Não foi possível inserir os dados. "
                f"Colunas ausentes: "
                f"{sorted(colunas_faltantes)}"
            )

            return df

        resultado_insercao = inserir_dados(
            df_dados_do_servidor=df
        )

        if resultado_insercao:

            print(
                "Dados inseridos no banco com sucesso."
            )

        else:

            print(
                "Não foi possível inserir os dados no banco."
            )

        return df

    except Exception as erro:

        print(
            f"Erro durante o scraping do Joaquina: "
            f"{type(erro).__name__}: {erro}"
        )

        return None

    finally:

        if driver is not None:

            driver.quit()


# In[ ]:


if __name__ == "__main__":

    executar_scraping_joaquina(
        nome_servidor="DANIELA AIRES CAMPOS"
    )

