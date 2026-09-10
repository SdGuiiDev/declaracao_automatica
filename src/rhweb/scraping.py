#!/usr/bin/env python
# coding: utf-8

# # Bibliotecas

# In[1]:


from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import (
    ChromeDriverManager,
)  # comentar essa linha quando utilizar no docker
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys

import time

import tomllib

import pandas as pd

import psycopg2

import gc

import sys

import pathlib

from pathlib import Path


from .db_rhweb import inserir_dados



# # def localiza_raiz_projeto

# In[2]:


def localizar_raiz_projeto():

    projeto_rh = Path.cwd().resolve()

    for pasta in [
        projeto_rh,
        *projeto_rh.parents
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
    PROJETO_RH / "config.toml"
)

CAMINHO_CHROMEDRIVER = (
    PROJETO_RH / "chromedriver.exe"
)

print(
    f"Raiz do projeto: "
    f"{PROJETO_RH}"
)

print(
    f"Config encontrado: "
    f"{CAMINHO_CONFIG.exists()}"
)

print(
    f"ChromeDriver encontrado: "
    f"{CAMINHO_CHROMEDRIVER.exists()}"
)


# # def config_navegador
# 
# - função que gera as configurações no navegador quando o Selenium for executado
#     As configurações utilizadas foram:
#     - "--disable-notifications" --> Desativa as notificações do Chromer
#     - "--disable-popup-blocking" --> Desabilita o bloqueio de PopUp
#     - "--start-maximized" --> Inicializa o Chromer em tela cheia
# 
# - declaramos os valores do nosso "service", "driver" e "wait"
#     Uso:
#     - "Service" Configura e inicia automaticamente o ChromeDriver compatível para o Selenium controlar o Chrome.
#     - "driver" (ChromeDriverManager().install())" --> Cria um navegador que será controlado pelo selenium.
#     - "wait" WebDriverWait(driver, 30) --> Gera 30 segundos de espera até o navegador fechar.
# 
# - "return" --> retorna valores permitindo uso no codigo apenas pela variavel

# In[3]:


def config_navegador():

    chrome_options = Options()

    # Desativa as notificações do Chrome.
    chrome_options.add_argument(
        "--disable-notifications"
    )

    # Desabilita o bloqueio de pop-ups.
    chrome_options.add_argument(
        "--disable-popup-blocking"
    )

    # Inicia o Chrome com a tela maximizada.
    chrome_options.add_argument(
        "--start-maximized"
    )

    # Baixa ou localiza automaticamente o ChromeDriver.
    service = Service(
        ChromeDriverManager().install()
    )

    # Cria o navegador controlado pelo Selenium.
    driver = webdriver.Chrome(
        service=service,
        options=chrome_options
    )

    # Cria uma espera explícita de até 30 segundos.
    wait = WebDriverWait(
        driver,
        30
    )

    return driver, wait


# # def abrir_navegador
# 
# - "driver.get" --> get serve para abrir uma URL
# - "driver" --> chama a nossa variavel criado ah cima

# In[4]:


# recebe o parametro driver, que é o navegador que será controlado pelo selenium
def abrir_navegador(driver):

    # O método get() faz o navegador acessar a URL passada entre parênteses
    driver.get("https://sms.pmf.sc.gov.br:8443/SMSAdministrativo/")


# # def login_rhweb
# 
# - Abre um arquivo toml, acessa os dados informados
# - declara que os dados do arquivo ficarão armazenados na variavel "config"
# - A variável acess recebe a seção "acessos" do arquivo TOML, e "user" e "password" recebem os valores de seus respectivos campos.
# 
# - "campo_usuario" é a variavel que irá identificar o elemento que será trabalhado na pagina
# - ".click()" --> clica no elemento
# - ".send.keys(variavel)" --> insere dados que estão armazenados na variavel
# 
# - "campo_senha" repete o mesmo procedimento anterior"
# 
# - "botao_entrar" recebe na variavel o elemento que queremos trabalhar
# - "clica no botão
# 
# - fluxo:
#     - insere dados do login do usuario
#     - clica no botão de pesquisar

# In[5]:


def login_rhweb(wait):

    with open(
        CAMINHO_CONFIG,
        "rb"
    ) as acessos:

        config = tomllib.load(
            acessos
        )

    acesso = config["acessos_rhweb"]

    user = acesso["user"]
    password = acesso["password"]

    # Campo usuário.
    campo_usuario = wait.until(
        EC.element_to_be_clickable(
            (
                By.CSS_SELECTOR,
                "vaadin-text-field"
            )
        )
    )

    campo_usuario.click()
    campo_usuario.send_keys(
        user
    )

    # Campo senha.
    campo_senha = wait.until(
        EC.element_to_be_clickable(
            (
                By.CSS_SELECTOR,
                "vaadin-password-field"
            )
        )
    )

    campo_senha.click()
    campo_senha.send_keys(
        password
    )

    # Botão entrar.
    botao_entrar = wait.until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "//vaadin-button[contains(., 'Entrar')]"
            )
        )
    )

    botao_entrar.click()


# # def botao_recusrsos_humanos
# 
# - executa um click no container "Recursos Humanos"

# In[6]:


def botao_recursos_humanos(wait):

    botao_rh = wait.until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                '//*[@id="module-view-layout"]/div/div/span'
            )
        )
    )

    botao_rh.click()


# # def botao_servidor
# 
# - Executa um click no container "servidor"

# In[7]:


def botao_servidor(wait):

    botao_servidor = wait.until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                '//*[@id="ContainerMenuModulo"]/div[1]/span'
            )
        )
    )

    botao_servidor.click()


# # def botao_cadastro_servidor
# 
# - Clica no botão cadastro para inserir um dado

# In[8]:


def botao_cadastro_servidor(wait):

    botao_cad_servidor = wait.until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                '//*[@id="application-view-body-menu-options"]/div/vaadin-horizontal-layout[1]/label',
            )
        )
    )
    botao_cad_servidor.click()


# # Futuro StreamLite
# 
# - usuario irá inserir um nome
#     - retorna uma variavel que pode ser chamado com seus dados dentro

# In[10]:


def pesquisa_funcionario_nome(
    wait,
    nome_servidor
):

    # Campo de pesquisa do funcionário.
    campo_pesquisa = wait.until(
        EC.element_to_be_clickable(
            (
                By.ID,
                "edtFuncionarioPesquisa"
            )
        )
    )

    campo_pesquisa.click()

    # Seleciona e apaga o conteúdo atual do campo.
    campo_pesquisa.send_keys(
        Keys.CONTROL,
        "a"
    )

    campo_pesquisa.send_keys(
        Keys.BACKSPACE
    )

    # Digita o nome do servidor.
    campo_pesquisa.send_keys(
        nome_servidor
    )

    # Botão pesquisar.
    botao_pesquisar = wait.until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "//vaadin-button[contains(., 'Pesquisar')]"
            )
        )
    )

    botao_pesquisar.click()

    # Aguarda o carregamento da página.
    wait.until(
        lambda driver: driver.execute_script(
            "return document.readyState"
        ) == "complete"
    )

    # Aguarda o grid de resultados aparecer.
    wait.until(
        EC.visibility_of_element_located(
            (
                By.TAG_NAME,
                "vaadin-grid"
            )
        )
    )


# # Nova def aguardar_resultado_matriculas
# 
# delclara as variaveis
# 
# - Fluxo: verifica se apareceram resultados -> compara a quantidade atual
# - com a anterior -> reinicia a contagem quando houver mudança ->
# - considera o carregamento concluído quando a quantidade ficar estável.
# 
# aguardar_resultados_matriculas
# 
# Declara as variáveis:
# 
# Cria uma espera com o tempo máximo informado.
# Armazena a quantidade de matrículas encontrada na verificação anterior.
# Conta quantas vezes a quantidade de matrículas permaneceu igual.
# Cria uma função interna para verificar se os resultados terminaram de carregar.
#     nonlocal quantidade_anterior: permite alterar a quantidade anterior.
#     nonlocal quantidade_estavel: permite alterar a contagem de estabilidade.
# quantidade_atual: executa um script na página e conta os números únicos encontrados nos grids.
# Caso nenhuma matrícula seja encontrada, reinicia os controles e continua aguardando.
# Caso a quantidade atual seja igual à anterior, aumenta a contagem de estabilidade.
# Caso a quantidade mude, atualiza a quantidade anterior e reinicia a contagem.
# Quando a quantidade permanece igual pelo número definido de verificações, considera o carregamento concluído.
# Caso ainda não esteja estável, aguarda o intervalo e realiza outra verificação.
# O WebDriverWait executa a função interna até receber a quantidade de matrículas ou atingir o tempo máximo.
# 
# - Fluxo: nenhum resultado apareceu -> continua aguardando ->
# - a quantidade mudou -> reinicia a contagem ->
# - a quantidade permaneceu igual várias vezes ->
# - considera que o carregamento terminou.

# In[11]:


def aguardar_resultados_matriculas(
        driver,
        timeout=10,
        intervalo=1,
        verificacoes_estaveis=2
):

    # Cria uma espera explícita com o tempo máximo informado.
    wait = WebDriverWait(driver, timeout)

    # Armazena a quantidade encontrada anteriormente.
    quantidade_anterior = -1

    # Conta quantas vezes seguidas a quantidade permaneceu igual.
    quantidade_estavel = 0

    def verificar_matriculas(d):

        nonlocal quantidade_anterior
        nonlocal quantidade_estavel

        quantidade_atual = d.execute_script("""
            const grids = document.querySelectorAll("vaadin-grid");

            let matriculas = new Set();

            for (const grid of grids) {

                const spans = grid.querySelectorAll("span");

                for (const span of spans) {

                    const texto = (
                        span.innerText ||
                        span.textContent ||
                        ""
                    ).trim();

                    if (/^\\d+$/.test(texto)) {
                        matriculas.add(texto);
                    }
                }
            }

            return matriculas.size;
        """)

        # Verifica se a quantidade permaneceu igual.
        if quantidade_atual == quantidade_anterior:
            quantidade_estavel += 1

        else:
            quantidade_anterior = quantidade_atual
            quantidade_estavel = 0

        # Considera finalizado mesmo quando a quantidade é zero.
        if quantidade_estavel >= verificacoes_estaveis:
            return quantidade_atual

        time.sleep(intervalo)

        return False

    return wait.until(verificar_matriculas)


# # def retornar_grid_para_inicio
# 
# Recebe o navegador, o índice do grid e o tempo de espera após a rolagem.
# Executa um script JavaScript na página.
# Localiza todos os elementos vaadin-grid.
# Seleciona o grid correspondente ao índice informado.
# Caso o grid não exista, encerra o script.
# Verifica se o grid possui a função scrollToIndex.
# Caso possua, posiciona o grid no primeiro registro.
# Procura o elemento interno responsável pela rolagem dentro do shadowRoot.
# Caso o elemento seja encontrado, define a posição vertical da rolagem como zero.
# Após retornar o grid ao início, aguarda o tempo definido antes de continuar.
# 
#     # Fluxo: localiza o grid pelo índice -> posiciona no primeiro registro ->
#     # redefine a rolagem interna para o topo -> aguarda antes de continuar.

# In[12]:


def retornar_grid_para_inicio(
        driver,
        indice_grid,
        tempo_espera=0.5
):

    driver.execute_script("""
        const grids = document.querySelectorAll(
            "vaadin-grid"
        );

        const grid = grids[arguments[0]];

        if (!grid) {
            return;
        }

        if (
            typeof grid.scrollToIndex ===
            "function"
        ) {
            grid.scrollToIndex(0);
        }

        const scroller =
            grid.shadowRoot?.querySelector(
                "#scroller"
            );

        if (scroller) {
            scroller.scrollTop = 0;
        }
    """, indice_grid)

    time.sleep(tempo_espera)


# # Nova def obter_lista_matricula

# In[13]:


def obter_lista_matriculas(
        driver,
        timeout=30,
        passo=15,
        tempo_espera=0.4,
        limite_sem_novas=10,
        limite_indices=10000
):

    aguardar_resultados_matriculas(
        driver=driver,
        timeout=timeout
    )

    wait = WebDriverWait(driver, timeout)

    wait.until(
        lambda d: d.execute_script("""
            return document.querySelectorAll(
                "vaadin-grid"
            ).length > 0;
        """)
    )

    quantidade_grids = driver.execute_script("""
        return document.querySelectorAll(
            "vaadin-grid"
        ).length;
    """)

    matriculas_encontradas = []
    matriculas_adicionadas = set()

    for indice_grid in range(quantidade_grids):

        possui_matricula = driver.execute_script("""
            const grids = document.querySelectorAll(
                "vaadin-grid"
            );

            const grid = grids[arguments[0]];

            if (!grid) {
                return false;
            }

            const textoGrid = (
                grid.innerText ||
                grid.textContent ||
                ""
            ).toLowerCase();

            return textoGrid.includes("matrícula") ||
                   textoGrid.includes("matricula");
        """, indice_grid)

        if not possui_matricula:
            continue

        print(
            f"Grid de matrículas encontrado: "
            f"{indice_grid + 1}"
        )

        tamanho_grid = driver.execute_script("""
            const grids = document.querySelectorAll(
                "vaadin-grid"
            );

            const grid = grids[arguments[0]];

            if (!grid) {
                return null;
            }

            const tamanhos = [
                grid.size,
                grid._effectiveSize,
                grid._size,
                grid.__effectiveSize
            ];

            for (const tamanho of tamanhos) {
                if (
                    typeof tamanho === "number" &&
                    tamanho > 0
                ) {
                    return tamanho;
                }
            }

            return null;
        """, indice_grid)

        if tamanho_grid:
            print(
                f"Quantidade informada pelo grid: "
                f"{tamanho_grid}"
            )

            limite_percorrer = tamanho_grid

        else:
            print(
                "O grid não informou a quantidade total. "
                "A extração continuará até não aparecerem "
                "novas matrículas."
            )

            limite_percorrer = limite_indices

        driver.execute_script("""
            const grids = document.querySelectorAll(
                "vaadin-grid"
            );

            const grid = grids[arguments[0]];

            if (
                grid &&
                typeof grid.scrollToIndex === "function"
            ) {
                grid.scrollToIndex(0);
            }

            const scroller =
                grid?.shadowRoot?.querySelector(
                    "#scroller"
                );

            if (scroller) {
                scroller.scrollTop = 0;
            }
        """, indice_grid)

        time.sleep(tempo_espera)

        indice_atual = 0
        quantidade_sem_novas = 0

        while indice_atual < limite_percorrer:

            driver.execute_script("""
                const grids = document.querySelectorAll(
                    "vaadin-grid"
                );

                const grid = grids[arguments[0]];

                const indice = arguments[1];

                if (!grid) {
                    return;
                }

                if (
                    typeof grid.scrollToIndex ===
                    "function"
                ) {
                    grid.scrollToIndex(indice);
                }
            """, indice_grid, indice_atual)

            time.sleep(tempo_espera)

            matriculas_visiveis = driver.execute_script("""
                const grids = document.querySelectorAll(
                    "vaadin-grid"
                );

                const grid = grids[arguments[0]];

                if (!grid) {
                    return [];
                }

                const matriculas = new Set();

                const celulas = grid.querySelectorAll(
                    "vaadin-grid-cell-content"
                );

                celulas.forEach(celula => {
                    const slot =
                        celula.getAttribute("slot") || "";

                    const matchSlot = slot.match(
                        /vaadin-grid-cell-content-(\\d+)/
                    );

                    if (!matchSlot) {
                        return;
                    }

                    const numeroSlot = Number(
                        matchSlot[1]
                    );

                    if (
                        numeroSlot >= 8 &&
                        numeroSlot % 2 === 0
                    ) {
                        const span =
                            celula.querySelector("span");

                        if (!span) {
                            return;
                        }

                        const texto =
                            span.innerText.trim();

                        if (/^\\d+$/.test(texto)) {
                            matriculas.add(texto);
                        }
                    }
                });

                return Array.from(matriculas);
            """, indice_grid)

            quantidade_antes = len(
                matriculas_adicionadas
            )

            for matricula in matriculas_visiveis:

                if matricula not in matriculas_adicionadas:

                    matriculas_adicionadas.add(
                        matricula
                    )

                    matriculas_encontradas.append(
                        matricula
                    )

            quantidade_depois = len(
                matriculas_adicionadas
            )

            if quantidade_depois == quantidade_antes:
                quantidade_sem_novas += 1

            else:
                quantidade_sem_novas = 0

                print(
                    f"Índice atual: {indice_atual} | "
                    f"Matrículas encontradas: "
                    f"{quantidade_depois}"
                )

            if (
                not tamanho_grid and
                quantidade_sem_novas >= limite_sem_novas
            ):
                print(
                    "Nenhuma matrícula nova foi encontrada "
                    "nas últimas movimentações."
                )

                break

            indice_atual += passo

        if tamanho_grid:

            ultimo_indice = max(
                tamanho_grid - 1,
                0
            )

            driver.execute_script("""
                const grids = document.querySelectorAll(
                    "vaadin-grid"
                );

                const grid = grids[arguments[0]];

                if (
                    grid &&
                    typeof grid.scrollToIndex ===
                    "function"
                ) {
                    grid.scrollToIndex(arguments[1]);
                }
            """, indice_grid, ultimo_indice)

            time.sleep(tempo_espera)

            ultimas_matriculas = driver.execute_script("""
                const grids = document.querySelectorAll(
                    "vaadin-grid"
                );

                const grid = grids[arguments[0]];

                if (!grid) {
                    return [];
                }

                const matriculas = new Set();

                const celulas = grid.querySelectorAll(
                    "vaadin-grid-cell-content"
                );

                celulas.forEach(celula => {
                    const slot =
                        celula.getAttribute("slot") || "";

                    const matchSlot = slot.match(
                        /vaadin-grid-cell-content-(\\d+)/
                    );

                    if (!matchSlot) {
                        return;
                    }

                    const numeroSlot = Number(
                        matchSlot[1]
                    );

                    if (
                        numeroSlot >= 8 &&
                        numeroSlot % 2 === 0
                    ) {
                        const span =
                            celula.querySelector("span");

                        if (!span) {
                            return;
                        }

                        const texto =
                            span.innerText.trim();

                        if (/^\\d+$/.test(texto)) {
                            matriculas.add(texto);
                        }
                    }
                });

                return Array.from(matriculas);
            """, indice_grid)

            for matricula in ultimas_matriculas:

                if matricula not in matriculas_adicionadas:

                    matriculas_adicionadas.add(
                        matricula
                    )

                    matriculas_encontradas.append(
                        matricula
                    )

        driver.execute_script("""
            const grids = document.querySelectorAll(
                "vaadin-grid"
            );

            const grid = grids[arguments[0]];

            if (!grid) {
                return;
            }

            if (
                typeof grid.scrollToIndex ===
                "function"
            ) {
                grid.scrollToIndex(0);
            }

            const scroller =
                grid.shadowRoot?.querySelector(
                    "#scroller"
                );

            if (scroller) {
                scroller.scrollTop = 0;
            }
        """, indice_grid)

        time.sleep(tempo_espera)

        wait.until(
            lambda d: d.execute_script("""
                const grids = document.querySelectorAll(
                    "vaadin-grid"
                );

                const grid = grids[arguments[0]];

                if (!grid) {
                    return false;
                }

                const celulas = grid.querySelectorAll(
                    "vaadin-grid-cell-content"
                );

                return celulas.length > 0;
            """, indice_grid)
        )

        print(
            "Grid retornado para o primeiro registro."
        )

    print("Matrículas encontradas:")
    print(matriculas_encontradas)

    print(
        f"Total de matrículas encontradas: "
        f"{len(matriculas_encontradas)}"
    )

    return matriculas_encontradas


# # def clicar_na_matricula

# In[14]:


def clicar_na_matricula(driver, matricula, timeout=15):
    """
    Clica no servidor pelo número da matrícula dentro do vaadin-grid.
    Retorna True se conseguiu clicar e False se não conseguiu.
    """

    try:
        matricula = str(matricula).strip()

        wait = WebDriverWait(driver, timeout)

        # Aguarda a matrícula existir no grid e retorna a célula encontrada.
        celula_matricula = wait.until(
            lambda d: d.execute_script(
                """
                const matricula = arguments[0];

                const grids = document.querySelectorAll(
                    "vaadin-grid"
                );

                for (const grid of grids) {
                    const celulas = grid.querySelectorAll(
                        "vaadin-grid-cell-content"
                    );

                    for (const celula of celulas) {
                        const texto = (
                            celula.innerText ||
                            celula.textContent ||
                            ""
                        ).trim();

                        if (texto === matricula) {
                            return celula;
                        }
                    }
                }

                return null;
                """,
                matricula
            )
        )

        # Posiciona a matrícula no centro da tela.
        driver.execute_script(
            """
            arguments[0].scrollIntoView({
                behavior: "auto",
                block: "center",
                inline: "center"
            });
            """,
            celula_matricula
        )

        # Aguarda rapidamente a célula ficar estável.
        posicao_anterior = None
        verificacoes_estaveis = 0
        tempo_inicio = time.time()

        while time.time() - tempo_inicio < 3:

            posicao_atual = driver.execute_script(
                """
                const elemento = arguments[0];

                if (!elemento || !elemento.isConnected) {
                    return null;
                }

                const rect = elemento.getBoundingClientRect();

                return {
                    top: Math.round(rect.top),
                    left: Math.round(rect.left),
                    width: Math.round(rect.width),
                    height: Math.round(rect.height)
                };
                """,
                celula_matricula
            )

            if posicao_atual is None:
                celula_matricula = wait.until(
                    lambda d: d.execute_script(
                        """
                        const matricula = arguments[0];

                        const grids = document.querySelectorAll(
                            "vaadin-grid"
                        );

                        for (const grid of grids) {
                            const celulas = grid.querySelectorAll(
                                "vaadin-grid-cell-content"
                            );

                            for (const celula of celulas) {
                                const texto = (
                                    celula.innerText ||
                                    celula.textContent ||
                                    ""
                                ).trim();

                                if (texto === matricula) {
                                    return celula;
                                }
                            }
                        }

                        return null;
                        """,
                        matricula
                    )
                )

                posicao_anterior = None
                verificacoes_estaveis = 0

                continue

            if posicao_atual == posicao_anterior:
                verificacoes_estaveis += 1

            else:
                posicao_anterior = posicao_atual
                verificacoes_estaveis = 0

            # Duas verificações já são suficientes.
            if verificacoes_estaveis >= 2:
                break

            time.sleep(0.1)

        if verificacoes_estaveis < 2:
            print(
                f"A matrícula {matricula} não ficou estável "
                f"para realizar o clique."
            )

            return False

        # Localiza novamente a célula após o grid estabilizar.
        celula_matricula = wait.until(
            lambda d: d.execute_script(
                """
                const matricula = arguments[0];

                const grids = document.querySelectorAll(
                    "vaadin-grid"
                );

                for (const grid of grids) {
                    const celulas = grid.querySelectorAll(
                        "vaadin-grid-cell-content"
                    );

                    for (const celula of celulas) {
                        const texto = (
                            celula.innerText ||
                            celula.textContent ||
                            ""
                        ).trim();

                        if (texto === matricula) {
                            return celula;
                        }
                    }
                }

                return null;
                """,
                matricula
            )
        )

        # Executa o clique diretamente na célula encontrada.
        resultado = driver.execute_script(
            """
            const celula = arguments[0];

            if (!celula || !celula.isConnected) {
                return false;
            }

            const span = celula.querySelector("span");

            if (span) {
                span.click();

                return true;
            }

            celula.click();

            return true;
            """,
            celula_matricula
        )

        if not resultado:
            print(
                f"Não foi possível clicar na matrícula "
                f"{matricula}."
            )

            return False

        # Aguarda a tela de dados do servidor abrir.
        wait.until(
            lambda d: d.execute_script(
                """
                const campoNome = document.querySelector(
                    "#edtNome"
                );

                const campoCpf = document.querySelector(
                    "#cpf"
                );

                return Boolean(campoNome || campoCpf);
                """
            )
        )

        print(
            f"Matrícula {matricula} clicada com sucesso."
        )

        return True

    except Exception as erro:
        print(
            f"Erro ao clicar na matrícula "
            f"{matricula}: "
            f"{type(erro).__name__}: {erro}"
        )

        print(
            f"A matrícula {matricula} será ignorada."
        )

        return False


# # def aguardar_matricula_carregada

# In[15]:


def aguardar_matricula_carregada(driver, matricula_esperada, timeout=15):
    """
    Aguarda até a tela de cadastro carregar a matrícula correta.
    Valida somente campos visíveis, ignorando elementos escondidos do Vaadin.
    """

    matricula_esperada = str(matricula_esperada).strip()

    def verificar(driver):
        return driver.execute_script(
            """
            const matriculaEsperada = arguments[0];

            function visivel(el) {
                if (!el) return false;

                const rect = el.getBoundingClientRect();
                const style = window.getComputedStyle(el);

                return (
                    rect.width > 0 &&
                    rect.height > 0 &&
                    style.display !== "none" &&
                    style.visibility !== "hidden" &&
                    style.opacity !== "0"
                );
            }

            function valorCampo(campo) {
                if (!campo) return "";

                if (campo.value) {
                    return campo.value.toString().trim();
                }

                if (campo.inputElement && campo.inputElement.value) {
                    return campo.inputElement.value.toString().trim();
                }

                if (campo.shadowRoot) {
                    const input = campo.shadowRoot.querySelector("input");

                    if (input && input.value) {
                        return input.value.toString().trim();
                    }
                }

                return "";
            }

            const campos = Array.from(document.querySelectorAll("vaadin-text-field"))
                .filter(campo => visivel(campo));

            for (const campo of campos) {
                const id = campo.getAttribute("id") || "";

                if (id === "edtMatriculaPesquisa") {
                    continue;
                }

                const valor = valorCampo(campo);

                if (valor === matriculaEsperada) {
                    return true;
                }
            }

            return false;
            """,
            matricula_esperada
        )

    WebDriverWait(driver, timeout).until(verificar)

    print(f"Tela carregada corretamente para matrícula: {matricula_esperada}")
    return True


# #  extrair_dados_tela_servidor

# In[16]:


def extrair_dados_tela_servidor(driver):
    wait = WebDriverWait(driver, 20)

    wait.until(
        EC.presence_of_element_located(
            (
                By.CSS_SELECTOR,
                "vaadin-text-field, vaadin-combo-box, custom-date-picker, vaadin-grid",
            )
        )
    )

    dados = driver.execute_script("""
        function limparTexto(texto) {
            if (!texto) return "";
            return texto.replace("*", "").trim();
        }

        function textoElemento(elemento) {
            if (!elemento) return "";

            let texto = "";

            if (elemento.innerText) {
                texto = elemento.innerText;
            }

            if (!texto && elemento.textContent) {
                texto = elemento.textContent;
            }

            if (!texto && elemento.content) {
                texto = elemento.content.textContent;
            }

            return limparTexto(texto);
        }

        function pegarValor(campo) {
            if (!campo) return "";

            const tag = campo.tagName.toLowerCase();

            if (tag === "vaadin-radio-group") {
                const selecionado = campo.querySelector(
                    'vaadin-radio-button[checked], vaadin-radio-button[aria-checked="true"]'
                );

                if (selecionado) {
                    return textoElemento(selecionado);
                }

                return campo.value || "";
            }

            if (tag === "vaadin-combo-box") {
                if (campo.inputElement && campo.inputElement.value) {
                    return campo.inputElement.value.toString().trim();
                }

                if (campo.shadowRoot) {
                    const input = campo.shadowRoot.querySelector("input");

                    if (input && input.value) {
                        return input.value.toString().trim();
                    }
                }

                if (campo.innerText && campo.innerText.trim()) {
                    return campo.innerText.trim();
                }

                if (campo.selectedItem) {
                    return campo.selectedItem.label ||
                        campo.selectedItem.nome ||
                        campo.selectedItem.name ||
                        "";
                }

                return campo.value ? campo.value.toString().trim() : "";
            }

            if (campo.value) {
                return campo.value.toString().trim();
            }

            if (campo.inputElement && campo.inputElement.value) {
                return campo.inputElement.value.toString().trim();
            }

            if (campo.shadowRoot) {
                const input = campo.shadowRoot.querySelector(
                    "input, textarea, vaadin-text-field"
                );

                if (input && input.value) {
                    return input.value.toString().trim();
                }

                if (input && input.inputElement && input.inputElement.value) {
                    return input.inputElement.value.toString().trim();
                }
            }

            return textoElemento(campo);
        }

        function pegarGrid(grid) {
            const colunas = [];

            grid.querySelectorAll("vaadin-grid-column").forEach(coluna => {
                const header = coluna.querySelector("template.header");

                let nomeColuna = "";

                if (header) {
                    if (header.content && header.content.textContent) {
                        nomeColuna = limparTexto(header.content.textContent);
                    }

                    if (!nomeColuna && header.textContent) {
                        nomeColuna = limparTexto(header.textContent);
                    }

                    if (!nomeColuna && header.innerText) {
                        nomeColuna = limparTexto(header.innerText);
                    }
                }

                if (nomeColuna) {
                    colunas.push(nomeColuna);
                }
            });

            let celulas = Array.from(
                grid.querySelectorAll("vaadin-grid-cell-content")
            );

            let valores = celulas
                .map(celula => textoElemento(celula))
                .filter(valor => valor !== "");

            valores = valores.filter(valor => !colunas.includes(valor));

            const linhas = [];

            if (colunas.length === 0) {
                return [];
            }

            for (let i = 0; i < valores.length; i += colunas.length) {
                const valoresLinha = valores.slice(i, i + colunas.length);

                if (valoresLinha.length < colunas.length) {
                    continue;
                }

                const linha = {};

                colunas.forEach((coluna, index) => {
                    linha[coluna] = valoresLinha[index] || "";
                });

                linhas.push(linha);
            }

            return linhas;
        }

        function encontrarCampoDepoisDoLabel(label) {
            const camposValidos = [
                "vaadin-text-field",
                "vaadin-combo-box",
                "custom-date-picker",
                "custom-textfield-time",
                "vaadin-radio-group",
                "vaadin-text-area",
                "vaadin-grid"
            ];

            let campo = label.nextElementSibling;

            while (campo) {
                const tag = campo.tagName.toLowerCase();

                if (tag === "template") {
                    campo = campo.nextElementSibling;
                    continue;
                }

                if (camposValidos.includes(tag)) {
                    return campo;
                }

                campo = campo.nextElementSibling;
            }

            return null;
        }

        const resultado = {};
        const tabelas = {};

        const labels = document.querySelectorAll("label");

        labels.forEach(label => {
            const nomeCampo = limparTexto(label.innerText || label.textContent);

            if (!nomeCampo) return;

            const campo = encontrarCampoDepoisDoLabel(label);

            if (!campo) return;

            const tag = campo.tagName.toLowerCase();

            const camposValidos = [
                "vaadin-text-field",
                "vaadin-combo-box",
                "custom-date-picker",
                "custom-textfield-time",
                "vaadin-radio-group",
                "vaadin-text-area"
            ];

            if (camposValidos.includes(tag)) {
                resultado[nomeCampo] = pegarValor(campo);
            }

            if (tag === "vaadin-grid") {
                tabelas[nomeCampo] = pegarGrid(campo);
            }
        });

        return {
            campos: resultado,
            tabelas: tabelas
        };
    """)

    campos = dados.get("campos", {})
    tabelas = dados.get("tabelas", {})

    df_campos = pd.DataFrame([campos])

    df_historico_lotacoes = pd.DataFrame(
        tabelas.get("Histórico de Lotações", [])
    )

    return campos, tabelas, df_campos, df_historico_lotacoes


# # def extrair_grid_com_scroll
# 
# extração da tabela historico
# 
# 

# In[17]:


def extrair_grid_com_scroll(
    driver,
    nome_tabela,
    tentativas_max=100,
    tempo_espera_ms=500,
    passo=1,
    limite_sem_novos=3
):
    """
    Extrai dados de um vaadin-grid rolando por partes.
    Mostra apenas a quantidade final de itens encontrados.
    """

    driver.set_script_timeout(60)

    linhas_map = {}
    tentativas_sem_novos = 0

    for tentativa in range(tentativas_max):
        indice = tentativa * passo
        qtd_antes = len(linhas_map)

        dados_grid = driver.execute_async_script(
            """
            const nomeTabela = arguments[0];
            const indice = arguments[1];
            const tempoEspera = arguments[2];
            const callback = arguments[arguments.length - 1];

            function limparTexto(texto) {
                if (!texto) return "";
                return texto.replace("*", "").trim();
            }

            function textoElemento(elemento) {
                if (!elemento) return "";

                return limparTexto(
                    elemento.innerText ||
                    elemento.textContent ||
                    ""
                );
            }

            function encontrarGrid(nomeTabela) {
                const labels = Array.from(document.querySelectorAll("label"));

                for (const label of labels) {
                    const textoLabel = limparTexto(label.innerText || label.textContent);

                    if (textoLabel === nomeTabela) {
                        let elemento = label.nextElementSibling;

                        while (elemento) {
                            const tag = elemento.tagName
                                ? elemento.tagName.toLowerCase()
                                : "";

                            if (tag === "vaadin-grid") {
                                return elemento;
                            }

                            if (elemento.querySelector) {
                                const grid = elemento.querySelector("vaadin-grid");

                                if (grid) {
                                    return grid;
                                }
                            }

                            elemento = elemento.nextElementSibling;
                        }

                        if (label.parentElement) {
                            return label.parentElement.querySelector("vaadin-grid");
                        }
                    }
                }

                return null;
            }

            function pegarColunas(grid) {
                const colunas = [];

                grid.querySelectorAll("vaadin-grid-column").forEach(coluna => {
                    const header = coluna.querySelector("template.header");

                    let nome = "";

                    if (header) {
                        nome = limparTexto(
                            header.content?.textContent ||
                            header.textContent ||
                            header.innerText ||
                            ""
                        );
                    }

                    if (nome) {
                        colunas.push(nome);
                    }
                });

                return colunas;
            }

            function pegarLinhas(grid, colunas) {
                let valores = Array.from(
                    grid.querySelectorAll("vaadin-grid-cell-content")
                )
                .map(celula => textoElemento(celula))
                .filter(valor => valor !== "")
                .filter(valor => !colunas.includes(valor));

                const linhas = [];

                for (let i = 0; i < valores.length; i += colunas.length) {
                    const pedaco = valores.slice(i, i + colunas.length);

                    if (pedaco.length < colunas.length) {
                        continue;
                    }

                    const linha = {};

                    colunas.forEach((coluna, index) => {
                        linha[coluna] = pedaco[index] || "";
                    });

                    linhas.push(linha);
                }

                return linhas;
            }

            const grid = encontrarGrid(nomeTabela);

            if (!grid) {
                callback({
                    erro: "Grid não encontrado: " + nomeTabela,
                    linhas: []
                });
                return;
            }

            const colunas = pegarColunas(grid);

            if (colunas.length === 0) {
                callback({
                    erro: "Colunas não encontradas: " + nomeTabela,
                    linhas: []
                });
                return;
            }

            if (grid.scrollToIndex) {
                grid.scrollToIndex(indice);
            } else {
                grid.scrollTop = indice * 40;
            }

            setTimeout(() => {
                callback({
                    erro: null,
                    linhas: pegarLinhas(grid, colunas)
                });
            }, tempoEspera);
            """,
            nome_tabela,
            indice,
            tempo_espera_ms,
        )

        if dados_grid.get("erro"):
            print(dados_grid["erro"])
            break

        linhas = dados_grid.get("linhas", [])

        for linha in linhas:
            chave = tuple(sorted(linha.items()))
            linhas_map[chave] = linha

        qtd_depois = len(linhas_map)

        if qtd_depois == qtd_antes:
            tentativas_sem_novos += 1
        else:
            tentativas_sem_novos = 0

        if tentativas_sem_novos >= limite_sem_novos:
            break

    print(f"{nome_tabela}: {len(linhas_map)} item(ns) encontrado(s)")

    return pd.DataFrame(list(linhas_map.values()))


# # def separar_dataframe_servidor

# In[18]:


def separar_dataframe_servidor(df_campos):
    if df_campos.empty:
        return pd.DataFrame()

    colunas_servidor = [
        "Matrícula",
        "Nome",
        "CPF",
        "RG",
        "Dt Nascimento",
        "Título",
        "Dt Emissão Titulo",
        "Zona",
        "Seção",
        "Código",
        "E-mail",
        "Nome da Mãe",
        "Logradouro",
        "Número",
        "Bairro",
        "Cidade",
        "CEP",
        "Complemento",
        "Telefone Fixo/Celular",
        "Dt Emissor RG",
        "Tipo Servidor",
        "Estado Civil",
        "UF Nascimento",
        "Órgão Emissor",
        "Nacionalidade",
        "Municipio Nascimento",
        "Grau de Instrução",
        "Sexo",
        "País de Origem",
        "Conselho Prof.",
        "Cartão SUS",
        "Busca CEP",
    ]

    colunas_existentes = [
        coluna for coluna in colunas_servidor
        if coluna in df_campos.columns
    ]

    df_dados_servidor = df_campos[colunas_existentes].copy()

    df_dados_servidor = df_dados_servidor.rename(
        columns={
            "Matrícula": "matricula",
            "Nome": "nome",
            "CPF": "cpf",
            "RG": "rg",
            "Dt Nascimento": "data_nascimento",
            "Título": "titulo_eleitor",
            "Dt Emissão Titulo": "data_emissao",
            "Zona": "zona_eleicao",
            "Seção": "secao_eleicao",
            "Código": "codigo",
            "E-mail": "email",
            "Nome da Mãe": "nome_mae",
            "Logradouro": "logradouro",
            "Número": "numero_casa",
            "Bairro": "bairro",
            "Cidade": "cidade",
            "CEP": "cep",
            "Complemento": "complemento",
            "Telefone Fixo/Celular": "telefone",
            "Dt Emissor RG": "data_emissor_rg",
            "Tipo Servidor": "tipo_servidor",
            "Estado Civil": "estado_civil",
            "UF Nascimento": "uf",
            "Órgão Emissor": "orgao_emissor",
            "Nacionalidade": "nacionalidade",
            "Municipio Nascimento": "municipio",
            "Grau de Instrução": "grau",
            "Sexo": "sexo",
            "País de Origem": "origem",
            "Conselho Prof.": "conselho_profissional",
            "Cartão SUS": "cartao_sus",
            "Busca CEP": "busca_cep"
        }
    )

    return df_dados_servidor


# # def separar_dataframe_cargos

# In[19]:


def separar_dataframe_cargos(df_campos):
    if df_campos.empty:
        return pd.DataFrame()

    colunas_cargos = [
        "Cargo",
        "Função",
        "Data de Admissão",
        "Data Prevista Saída",
        "Data de Saída",
        "Carga H. Contratual",
        "Série",
        "Fase",
        "Situação",
        "Origem",
        "Estabelecimento de Ensino",
        "Especialidade",
        "Curso",
        "Nome do Curso",
    ]

    colunas_existentes = [
        coluna for coluna in colunas_cargos
        if coluna in df_campos.columns
    ]

    df_cargos = df_campos[colunas_existentes].copy()

    df_cargos = df_cargos.rename(
        columns={
            "Cargo": "cargo",
            "Função": "funcao",
            "Data de Admissão": "data_admissao",
            "Data Prevista Saída": "data_prevista_saida",
            "Data de Saída": "data_saida",
            "Carga H. Contratual": "carga_horaria_semanal",
            "Série": "serie_escolaridade",
            "Fase": "fase_faculdade",
            "Situação": "situacao",
            "Origem": "origem_contrato",
            "Estabelecimento de Ensino": "estab_ensino",
            "Especialidade": "especialidade",
            "Curso": "curso",
            "Nome do Curso": "nome_do_curso"
        }
    )

    return df_cargos


# # def voltar_para_lista_resultados

# In[20]:


def voltar_para_lista_resultados(driver, wait, timeout=15):
    """
    Clica no botão Voltar e confirma se voltou de verdade para a tela de pesquisa.
    No Vaadin, não basta verificar se o elemento existe no DOM.
    É necessário verificar se está visível na tela.
    """

    try:
        print("Clicando no botão Voltar...")

        clicou = driver.execute_script(
            """
            function texto(el) {
                return (el.innerText || el.textContent || "").trim();
            }

            function visivel(el) {
                if (!el) return false;

                const rect = el.getBoundingClientRect();
                const style = window.getComputedStyle(el);

                return (
                    rect.width > 0 &&
                    rect.height > 0 &&
                    style.display !== "none" &&
                    style.visibility !== "hidden" &&
                    style.opacity !== "0"
                );
            }

            const botoes = Array.from(document.querySelectorAll("vaadin-button, button"));

            for (const botao of botoes) {
                const t = texto(botao);

                if (visivel(botao) && t.includes("Voltar")) {
                    botao.scrollIntoView({block: "center"});
                    botao.click();
                    return true;
                }
            }

            return false;
            """
        )

        if not clicou:
            print("Botão Voltar não encontrado ou não estava visível.")
            return False

        voltou = WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script(
                """
                function visivel(el) {
                    if (!el) return false;

                    const rect = el.getBoundingClientRect();
                    const style = window.getComputedStyle(el);

                    return (
                        rect.width > 0 &&
                        rect.height > 0 &&
                        style.display !== "none" &&
                        style.visibility !== "hidden" &&
                        style.opacity !== "0"
                    );
                }

                const campoFuncionario = document.querySelector("#edtFuncionarioPesquisa");
                const campoMatriculaPesquisa = document.querySelector("#edtMatriculaPesquisa");

                const grids = Array.from(document.querySelectorAll("vaadin-grid"))
                    .filter(grid => visivel(grid));

                return (
                    visivel(campoFuncionario) &&
                    visivel(campoMatriculaPesquisa) &&
                    grids.length > 0
                );
                """
            )
        )

        if voltou:
            print("Lista de resultados carregada novamente.")
            return True

        print("Não confirmou retorno para a lista.")
        return False

    except Exception as e:
        print(f"Erro ao voltar para lista: {e}")
        return False


# # main

# In[21]:


def executar_scraping_rhweb(nome_servidor):

    driver = None
    interrompido_por_erro = False

    try:

        driver, wait = config_navegador()

        abrir_navegador(driver)

        login_rhweb(wait)

        botao_recursos_humanos(wait)

        botao_servidor(wait)

        botao_cadastro_servidor(wait)

        pesquisa_funcionario_nome(
            wait,
            nome_servidor
        )

        matriculas = obter_lista_matriculas(
            driver,
            timeout=30
        )

        if len(matriculas) == 0:

            print(
                "Nenhuma matrícula foi encontrada."
            )

            return []

        for indice, matricula in enumerate(
            matriculas,
            start=1
        ):

            # Durante os testes, não limpa a saída.
            # clear_output(wait=True)

            print("-" * 50)

            print(
                f"Processando matrícula "
                f"{indice}/{len(matriculas)}: "
                f"{matricula}"
            )

            clicou = clicar_na_matricula(
                driver,
                matricula,
                timeout=30
            )

            if not clicou:

                print(
                    f"Não conseguiu clicar na matrícula: "
                    f"{matricula}"
                )

                continue

            try:

                # Confirma se a matrícula correta foi carregada.
                aguardar_matricula_carregada(
                    driver,
                    matricula,
                    timeout=30
                )

                (
                    campos,
                    tabelas,
                    df_campos,
                    df_historico_lotacoes
                ) = extrair_dados_tela_servidor(
                    driver
                )

                # Extrai o histórico completo com scroll.
                df_historico_lotacoes = (
                    extrair_grid_com_scroll(
                        driver,
                        nome_tabela=(
                            "Histórico de Lotações"
                        ),
                        tentativas_max=100,
                        tempo_espera_ms=500,
                        passo=2,
                        limite_sem_novos=3
                    )
                )

                # --------------------------------------------------- #
                # TRATA O HISTÓRICO DE LOTAÇÕES
                # --------------------------------------------------- #

                # Caso não exista histórico de lotações,
                # cria um DataFrame vazio com as colunas esperadas.
                if df_historico_lotacoes.empty:

                    df_historico_lotacoes = pd.DataFrame(
                        columns=[
                            "data_entrada",
                            "data_saida_historico",
                            "historico"
                        ]
                    )

                else:

                    # Remove espaços dos nomes das colunas.
                    # Converte cada nome de coluna para texto
                    # antes de aplicar strip.
                    df_historico_lotacoes.columns = [
                        str(coluna).strip()
                        for coluna
                        in df_historico_lotacoes.columns
                    ]

                    # Renomeia as colunas do histórico.
                    df_historico_lotacoes = (
                        df_historico_lotacoes.rename(
                            columns={
                                "Data Entrada": (
                                    "data_entrada"
                                ),
                                "Data Saída": (
                                    "data_saida_historico"
                                ),
                                "Lotação": "historico"
                            }
                        )
                    )

                # --------------------------------------------------- #
                # SEPARA OS DADOS DO SERVIDOR E DOS CARGOS
                # --------------------------------------------------- #

                df_dados_servidor = (
                    separar_dataframe_servidor(
                        df_campos
                    )
                )

                df_cargos = (
                    separar_dataframe_cargos(
                        df_campos
                    )
                )

                # Adiciona a matrícula aos DataFrames.
                df_dados_servidor[
                    "matricula"
                ] = matricula

                df_historico_lotacoes[
                    "matricula"
                ] = matricula

                df_cargos[
                    "matricula"
                ] = matricula

                # Copia o nome do curso para os dados do servidor.
                if (
                    not df_dados_servidor.empty
                    and
                    not df_cargos.empty
                    and
                    "nome_do_curso" in df_cargos.columns
                ):

                    nome_do_curso = (
                        df_cargos[
                            "nome_do_curso"
                        ]
                        .dropna()
                    )

                    if not nome_do_curso.empty:

                        df_dados_servidor[
                            "nome_do_curso"
                        ] = nome_do_curso.iloc[-1]

                # Remove possíveis servidores duplicados.
                if (
                    not df_dados_servidor.empty
                    and
                    "matricula"
                    in df_dados_servidor.columns
                ):

                    df_dados_servidor = (
                        df_dados_servidor
                        .drop_duplicates(
                            subset=[
                                "matricula"
                            ],
                            keep="last"
                        )
                        .reset_index(
                            drop=True
                        )
                    )

                # Remove possíveis cargos duplicados.
                if (
                    not df_cargos.empty
                    and
                    "matricula" in df_cargos.columns
                    and
                    "cargo" in df_cargos.columns
                    and
                    "data_admissao" in df_cargos.columns
                ):

                    df_cargos = (
                        df_cargos
                        .drop_duplicates(
                            subset=[
                                "matricula",
                                "cargo",
                                "data_admissao"
                            ],
                            keep="last"
                        )
                        .reset_index(
                            drop=True
                        )
                    )

                # Remove possíveis históricos duplicados.
                if (
                    not df_historico_lotacoes.empty
                    and
                    "matricula"
                    in df_historico_lotacoes.columns
                    and
                    "historico"
                    in df_historico_lotacoes.columns
                    and
                    "data_entrada"
                    in df_historico_lotacoes.columns
                ):

                    df_historico_lotacoes = (
                        df_historico_lotacoes
                        .drop_duplicates(
                            subset=[
                                "matricula",
                                "historico",
                                "data_entrada"
                            ],
                            keep="last"
                        )
                        .reset_index(
                            drop=True
                        )
                    )

                if df_dados_servidor.empty:

                    print(
                        f"Nenhum dado foi extraído para "
                        f"a matrícula {matricula}."
                    )

                else:

                    print(
                        f"Dados da matrícula {matricula} "
                        f"extraídos com sucesso."
                    )

                    print(
                        "\nDADOS ANTES DA INSERÇÃO:"
                    )

                    print(
                        f"Servidor: "
                        f"{len(df_dados_servidor)} "
                        f"registro(s)"
                    )

                    print(
                        f"Cargos: "
                        f"{len(df_cargos)} "
                        f"registro(s)"
                    )

                    print(
                        f"Históricos: "
                        f"{len(df_historico_lotacoes)} "
                        f"registro(s)"
                    )

                    print(
                        "\nSalvando os dados no banco..."
                    )

                    salvou = inserir_dados(
                        df_dados_servidor=(
                            df_dados_servidor
                        ),
                        df_cargos=df_cargos,
                        df_historico=(
                            df_historico_lotacoes
                        )
                    )

                    print(
                        f"Retorno de inserir_dados(): "
                        f"{salvou}"
                    )

                    if salvou is None:

                        print(
                            "A função inserir_dados() "
                            "retornou None."
                        )

                        interrompido_por_erro = True

                        break

                    if salvou is False:

                        print(
                            f"Erro ao salvar a matrícula "
                            f"{matricula} no banco."
                        )

                        interrompido_por_erro = True

                        break

                    print(
                        f"Matrícula {matricula} salva "
                        f"no banco com sucesso."
                    )

            except Exception as erro:

                print(
                    f"Erro ao processar a matrícula "
                    f"{matricula}: "
                    f"{type(erro).__name__}: {erro}"
                )

                interrompido_por_erro = True

                break

            voltou = voltar_para_lista_resultados(
                driver,
                wait,
                timeout=30
            )

            if not voltou:

                print(
                    f"Não conseguiu voltar para a lista "
                    f"após processar a matrícula "
                    f"{matricula}."
                )

                interrompido_por_erro = True

                break

            print(
                "Voltou corretamente para a lista."
            )

            # Remove os dados da matrícula atual da memória.
            if "campos" in locals():
                del campos

            if "tabelas" in locals():
                del tabelas

            if "df_campos" in locals():
                del df_campos

            if "df_dados_servidor" in locals():
                del df_dados_servidor

            if "df_historico_lotacoes" in locals():
                del df_historico_lotacoes

            if "df_cargos" in locals():
                del df_cargos

            gc.collect()

        if interrompido_por_erro:

            print(
                "\nExecução interrompida devido "
                "a um erro."
            )

            return None

        else:

            print(
                "\nLoop de matrículas finalizado "
                "com sucesso."
            )

            return matriculas

    except Exception as erro:

        print(
            f"Erro ao executar o código: "
            f"{type(erro).__name__}: {erro}"
        )

        return None

    finally:

        if driver is not None:
            driver.quit()

        print(
            "Navegador fechado."
        )
