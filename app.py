# Importações de bibliotecas

import streamlit as st
import tomllib

from pathlib import Path


#Importações de banco de dados
import psycopg2
import mariadb




# Importações do banco de dados e do Scraping do Joaquina
from src.joaquina.scraping import (
    executar_scraping_joaquina
)

from src.joaquina.db_joaquina import (
    buscar_servidor as buscar_servidor_joaquina
)

from src.rhweb.db_rhweb import (
    buscar_servidor as buscar_servidor_rhweb
)

from src.rhweb.scraping import (
    executar_scraping_rhweb
)

from src.risoluto.db_risoluto import (
    buscar_servidor as buscar_servidor_risoluto
)







# ------------------------------------------------------------------- #
# CONEXÃO COM O BANCO DE DADOS JOAQUINA
# ------------------------------------------------------------------- #

def conexao_joaquina():

    try:

        caminho_config = Path.cwd() / "config.toml"

        if not caminho_config.exists():

            raise FileNotFoundError(
                f"Arquivo config.toml não encontrado em: "
                f"{caminho_config}"
            )

        with open(
            caminho_config,
            "rb"
        ) as arquivo:

            config = tomllib.load(
                arquivo
            )

        db = config["joaquina"]

        conn = psycopg2.connect(
            host=db["host"],
            port=db["port"],
            dbname=db["dbname"],
            user=db["user"],
            password=db["password"]
        )

        cursor = conn.cursor()

        return conn, cursor

    except Exception as erro:

        st.error(
            f"Erro ao conectar com o banco Joaquina: "
            f"{type(erro).__name__}: {erro}"
        )

        return None, None


# ------------------------------------------------------------------- #
# CONEXÃO COM O BANCO DE DADOS RHWEB
# ------------------------------------------------------------------- #

def conexao_rhweb():

    try:

        caminho_config = Path.cwd() / "config.toml"

        if not caminho_config.exists():

            raise FileNotFoundError(
                f"Arquivo config.toml não encontrado em: "
                f"{caminho_config}"
            )

        with open(
            caminho_config,
            "rb"
        ) as arquivo:

            config = tomllib.load(
                arquivo
            )

        db = config["rhweb"]

        conn = psycopg2.connect(
            host=db["host"],
            port=db["port"],
            dbname=db["dbname"],
            user=db["user"],
            password=db["password"]
        )

        cursor = conn.cursor()

        return conn, cursor

    except Exception as erro:

        st.error(
            f"Erro ao conectar com o banco RHweb: "
            f"{type(erro).__name__}: {erro}"
        )

        return None, None


# ------------------------------------------------------------------- #
# CONEXÃO COM O BANCO DE DADOS RISOLUTO
# ------------------------------------------------------------------- #

def conexao_risoluto():

    try:

        caminho_config = Path.cwd() / "config.toml"

        if not caminho_config.exists():

            raise FileNotFoundError(
                f"Arquivo config.toml não encontrado em: "
                f"{caminho_config}"
            )

        with open(
            caminho_config,
            "rb"
        ) as arquivo:

            config = tomllib.load(
                arquivo
            )

        db = config["risoluto"]

        conn = mariadb.connect(
            host=db["host"],
            port=db["port"],
            database=db["database"],
            user=db["user"],
            password=db["password"]
        )

        cursor = conn.cursor()

        return conn, cursor

    except Exception as erro:

        st.error(
            f"Erro ao conectar com o banco Risoluto: "
            f"{type(erro).__name__}: {erro}"
        )

        return None, None















# ------------------------------------------------------------------- #
# TÍTULO DA PÁGINA
# ------------------------------------------------------------------- #


def titulo_pagina():

    st.title(
        "Busca de Servidores"
    )


# ------------------------------------------------------------------- #
# VARIÁVEIS DO SESSION STATE
# ------------------------------------------------------------------- #

def inicializar_variaveis():

    if "resultados" not in st.session_state:
        st.session_state.resultados = []

    if "servidor_selecionado" not in st.session_state:
        st.session_state.servidor_selecionado = None

    if "valor_pesquisado" not in st.session_state:
        st.session_state.valor_pesquisado = ""

    # Controla se o sistema está aguardando
    # o nome completo para realizar o scraping
    if "aguardando_nome_completo" not in st.session_state:
        st.session_state.aguardando_nome_completo = False

    if "todas_matriculas" not in st.session_state:
        st.session_state.todas_matriculas = False














# ------------------------------------------------------------------- #
# FORMULÁRIO DE PESQUISA
# ------------------------------------------------------------------- #

def gerar_tela_pesquisa():

    with st.form(
        "formulario_busca"
    ):

        valor_busca = st.text_input(
            "Digite o nome ou a matrícula do servidor:",
            value=st.session_state.valor_pesquisado
        )

        buscar = st.form_submit_button(
            "Buscar servidor",
            type="primary"
        )

    return buscar, valor_busca










# ------------------------------------------------------------------- #
# VALIDAÇÃO DA BUSCA
# ------------------------------------------------------------------- #

def validar_valor_busca(valor_busca):

    # Remove espaços no início e no final
    valor_busca = valor_busca.strip()

    # Verifica se algum valor foi informado
    if not valor_busca:

        st.warning(
            "Digite o nome ou a matrícula do servidor."
        )

        return False

    # Caso seja uma matrícula
    if valor_busca.isdigit():

        # Verifica tamanho mínimo da matrícula
        if len(valor_busca) < 3:

            st.warning(
                "Digite uma matrícula válida."
            )

            return False

        return True

    # Divide o nome digitado em partes
    partes_nome = valor_busca.split()

    # Exige pelo menos duas partes do nome
    if len(partes_nome) < 2:

        st.warning(
            "Digite pelo menos duas partes do nome."
        )

        return False

    # Soma a quantidade de letras digitadas
    quantidade_letras = sum(
        len(parte)
        for parte in partes_nome
    )

    # Evita pesquisas muito genéricas
    if quantidade_letras < 5:

        st.warning(
            "Digite mais letras do nome para realizar a busca."
        )

        return False

    # Pesquisa válida
    return True













# ------------------------------------------------------------------- #
# EXECUÇÃO DA BUSCA
# ------------------------------------------------------------------- #

def executar_busca(
        buscar,
        valor_busca
):

    # Verifica se o botão de busca foi pressionado
    if not buscar:
        return

    # Remove espaços no início e no final da pesquisa
    valor_busca = valor_busca.strip()

    # Verifica se algum valor foi informado
    if not valor_busca:

        st.warning(
            "Digite um nome ou matrícula antes de realizar a busca."
        )

        st.session_state.resultados = []
        st.session_state.servidor_selecionado = None
        st.session_state.valor_pesquisado = ""

        return

    # Valida o nome ou matrícula informada
    valor_valido = validar_valor_busca(
        valor_busca=valor_busca
    )

    # Caso o valor seja inválido
    if not valor_valido:

        st.session_state.resultados = []
        st.session_state.servidor_selecionado = None

        return

    # --------------------------------------------------------------- #
    # PRIMEIRO CONSULTA O BANCO DE DADOS
    # --------------------------------------------------------------- #

    resultados = buscar_servidor_joaquina(
        valor_busca=valor_busca
    )

    # --------------------------------------------------------------- #
    # CASO O BANCO TENHA ENCONTRADO RESULTADOS
    # --------------------------------------------------------------- #

    if resultados:

        # Salva os resultados encontrados
        st.session_state.resultados = resultados

        # Limpa qualquer servidor selecionado anteriormente
        st.session_state.servidor_selecionado = None

        # Guarda o valor pesquisado
        st.session_state.valor_pesquisado = valor_busca

        # Como encontrou no banco,
        # não é mais necessário aguardar nome completo
        st.session_state.aguardando_nome_completo = False

        # Informa a quantidade de vínculos encontrados
        st.success(
            f"{len(resultados)} vínculo(s) encontrado(s)."
        )

        # Encerra a função para impedir o scraping
        return

    # --------------------------------------------------------------- #
    # CASO A PESQUISA TENHA SIDO FEITA POR MATRÍCULA
    # --------------------------------------------------------------- #

    if valor_busca.isdigit():

        # O scraping não deve ser feito utilizando matrícula
        st.warning(
            "A matrícula não foi localizada no banco. "
            "Pesquise pelo nome do servidor."
        )

        st.session_state.resultados = []
        st.session_state.servidor_selecionado = None
        st.session_state.valor_pesquisado = valor_busca

        return

    # --------------------------------------------------------------- #
    # PRIMEIRA BUSCA POR NOME SEM RESULTADOS
    # --------------------------------------------------------------- #

    if not st.session_state.aguardando_nome_completo:

        # Informa que o nome não existe no banco
        st.warning(
            "Nenhum servidor correspondente foi encontrado "
            "no banco de dados."
        )

        # Solicita que o usuário informe o nome completo
        st.info(
            "Informe o nome completo do servidor para realizar "
            "uma consulta no sistema Joaquina."
        )

        # Agora o sistema passa a aguardar uma nova pesquisa
        # contendo o nome completo
        st.session_state.aguardando_nome_completo = True

        # Limpa os resultados anteriores
        st.session_state.resultados = []

        # Limpa qualquer seleção anterior
        st.session_state.servidor_selecionado = None

        # Mantém o valor pesquisado no campo
        st.session_state.valor_pesquisado = valor_busca

        # Não executa scraping nesta primeira tentativa
        return

    # --------------------------------------------------------------- #
    # SEGUNDA BUSCA SEM RESULTADOS
    # AGORA O USUÁRIO INFORMOU O NOME COMPLETO
    # --------------------------------------------------------------- #

    with st.spinner(
        "Servidor não encontrado no banco. "
        "Consultando o sistema Joaquina..."
    ):

        # Executa o scraping utilizando o nome informado
        resultado_scraping = executar_scraping_joaquina(
            nome_servidor=valor_busca
        )

    # --------------------------------------------------------------- #
    # VERIFICA SE O SCRAPING APRESENTOU ERRO
    # --------------------------------------------------------------- #

    if resultado_scraping is None:

        st.error(
            "Não foi possível concluir a consulta no Joaquina."
        )

        st.session_state.resultados = []
        st.session_state.servidor_selecionado = None
        st.session_state.valor_pesquisado = valor_busca

        return

    # --------------------------------------------------------------- #
    # DEPOIS DO SCRAPING CONSULTA O BANCO NOVAMENTE
    # --------------------------------------------------------------- #

    resultados = buscar_servidor_joaquina(
        valor_busca=valor_busca
    )

    # Salva os resultados da nova consulta
    st.session_state.resultados = resultados

    # Limpa qualquer seleção anterior
    st.session_state.servidor_selecionado = None

    # Guarda o nome pesquisado
    st.session_state.valor_pesquisado = valor_busca

    # Finaliza a espera pelo nome completo
    st.session_state.aguardando_nome_completo = False

    # --------------------------------------------------------------- #
    # EXIBE O RESULTADO FINAL
    # --------------------------------------------------------------- #

    if resultados:

        st.success(
            f"{len(resultados)} vínculo(s) encontrado(s)."
        )

    else:

        st.info(
            "Nenhum servidor foi encontrado no Joaquina."
        )









# ------------------------------------------------------------------- #
# SELEÇÃO DO SERVIDOR
# ------------------------------------------------------------------- #

def escolha_de_usuario():

    # Recupera os resultados armazenados na sessão
    resultados = st.session_state.resultados

    # Caso não existam resultados
    if not resultados:

        return None

    # --------------------------------------------------------------- #
    # IDENTIFICA OS NOMES ENCONTRADOS
    # --------------------------------------------------------------- #

    nomes_encontrados = []

    # Percorre todos os resultados encontrados
    for resultado in resultados:

        # Recupera o nome do servidor
        nome = resultado[1]

        # Verifica se o nome existe
        # e evita nomes duplicados na lista
        if nome and nome not in nomes_encontrados:

            nomes_encontrados.append(
                nome
            )

    # Caso nenhum nome válido tenha sido encontrado
    if not nomes_encontrados:

        st.warning(
            "O servidor foi encontrado, mas o nome "
            "não está disponível no banco de dados."
        )

        return None

    # --------------------------------------------------------------- #
    # SE HOUVER MAIS DE UM SERVIDOR, ESCOLHE PRIMEIRO O NOME
    # --------------------------------------------------------------- #

    if len(nomes_encontrados) > 1:

        nome_selecionado = st.radio(
            "Selecione o servidor que deseja utilizar:",
            options=nomes_encontrados,
            index=None
        )

        # Aguarda o usuário selecionar um servidor
        if nome_selecionado is None:

            return None

        vinculos = []

        # Filtra somente os vínculos pertencentes
        # ao servidor selecionado
        for resultado in resultados:

            if resultado[1] == nome_selecionado:

                vinculos.append(
                    resultado
                )

    # Caso somente um servidor tenha sido encontrado
    else:

        # Define automaticamente o único servidor encontrado
        nome_selecionado = nomes_encontrados[0]

        # Recupera somente os vínculos desse servidor
        vinculos = []

        for resultado in resultados:

            if resultado[1] == nome_selecionado:

                vinculos.append(
                    resultado
                )

        # Mostra ao usuário qual servidor foi encontrado
        st.write(
            f"**Servidor encontrado:** {nome_selecionado}"
        )

    # --------------------------------------------------------------- #
    # MONTA AS OPÇÕES DE MATRÍCULA
    # --------------------------------------------------------------- #

    opcoes = vinculos.copy()

    # Caso o servidor possua mais de uma matrícula,
    # adiciona a opção para utilizar todas
    if len(vinculos) > 1:

        opcoes.append(
            "TODAS"
        )

    # --------------------------------------------------------------- #
    # FORMATA O TEXTO DAS OPÇÕES
    # --------------------------------------------------------------- #

    def formatar_opcao(opcao):

        # Caso seja selecionada a opção de todas as matrículas
        if opcao == "TODAS":

            return "Todas as matrículas"

        # Recupera matrícula, nome e admissão
        matricula = opcao[0]

        nome = opcao[1]

        admissao = opcao[2]

        # Formata a data de admissão
        if admissao:

            admissao_formatada = admissao.strftime(
                "%d/%m/%Y"
            )

        else:

            admissao_formatada = "Não informada"

        # Retorna o texto exibido para o usuário
        return (
            f"{nome} - "
            f"Matrícula: {matricula} - "
            f"Admissão: {admissao_formatada}"
        )

    # --------------------------------------------------------------- #
    # ESCOLHA DA MATRÍCULA
    # --------------------------------------------------------------- #

    matricula_selecionada = st.radio(
        "Selecione a matrícula que deseja utilizar:",
        options=opcoes,
        index=None,
        format_func=formatar_opcao
    )

    # Aguarda o usuário selecionar uma matrícula
    if matricula_selecionada is None:

        return None

    # --------------------------------------------------------------- #
    # UMA OU TODAS AS MATRÍCULAS
    # --------------------------------------------------------------- #

    if matricula_selecionada == "TODAS":

        # Guarda que o usuário deseja todas as matrículas
        st.session_state.todas_matriculas = True

        vinculos_selecionados = vinculos

    else:

        # Guarda que o usuário deseja somente uma matrícula
        st.session_state.todas_matriculas = False

        vinculos_selecionados = [
            matricula_selecionada
        ]

    # Salva os vínculos escolhidos na sessão
    st.session_state.servidor_selecionado = (
        vinculos_selecionados
    )

    # --------------------------------------------------------------- #
    # EXIBE O QUE FOI SELECIONADO
    # --------------------------------------------------------------- #

    st.subheader(
        "Servidor selecionado"
    )

    # Mostra o nome do servidor selecionado
    st.write(
        f"**Nome:** {nome_selecionado}"
    )

    # Mostra todas as matrículas selecionadas
    for vinculo in vinculos_selecionados:

        matricula = vinculo[0]

        admissao = vinculo[2]

        # Formata a data de admissão
        if admissao:

            admissao_formatada = admissao.strftime(
                "%d/%m/%Y"
            )

        else:

            admissao_formatada = "Não informada"

        st.write(
            f"**Matrícula:** {matricula}"
        )

        st.write(
            f"**Admissão:** {admissao_formatada}"
        )

    # Retorna os vínculos selecionados pelo usuário
    return vinculos_selecionados











# ------------------------------------------------------------------- #
# IDENTIFICAÇÃO DO BANCO PELA DATA DE ADMISSÃO
# ------------------------------------------------------------------- #

def identificar_banco(admissao):

    if admissao is None:
        return None

    if admissao.year < 2024:
        return "rhweb"

    else:
        return "risoluto"











# ------------------------------------------------------------------- #
# DIRECIONAMENTO DOS VÍNCULOS
# ------------------------------------------------------------------- #

def direcionar_vinculos(vinculos_selecionados):

    vinculos_rhweb = []
    vinculos_risoluto = []

    for vinculo in vinculos_selecionados:

        matricula = vinculo[0]
        nome = vinculo[1]
        admissao = vinculo[2]

        banco = identificar_banco(
            admissao=admissao
        )

        if banco == "rhweb":

            vinculos_rhweb.append(
                vinculo
            )

        elif banco == "risoluto":

            vinculos_risoluto.append(
                vinculo
            )

    return vinculos_rhweb, vinculos_risoluto














# ------------------------------------------------------------------- #
# CONSULTA DOS VÍNCULOS NOS BANCOS
# ------------------------------------------------------------------- #

def consultar_vinculos(
        vinculos_rhweb,
        vinculos_risoluto
):

    resultados_rhweb = []

    resultados_risoluto = []

    matriculas_rhweb_nao_encontradas = []

    matriculas_risoluto_nao_encontradas = []

    # --------------------------------------------------------------- #
    # CONSULTA RHWEB
    # --------------------------------------------------------------- #

    # Guarda os nomes já consultados para evitar
    # pesquisar a mesma pessoa várias vezes
    nomes_consultados = []

    for vinculo in vinculos_rhweb:

        # Recupera o nome vindo do Joaquina
        nome = vinculo[1]

        # Evita consultar novamente a mesma pessoa
        if nome in nomes_consultados:
            continue

        nomes_consultados.append(
            nome
        )

        # ----------------------------------------------------------- #
        # IDENTIFICA AS MATRÍCULAS SELECIONADAS DESTA PESSOA
        # ----------------------------------------------------------- #

        matriculas_selecionadas = []

        for vinculo_rhweb in vinculos_rhweb:

            if vinculo_rhweb[1] == nome:

                matriculas_selecionadas.append(
                    str(vinculo_rhweb[0]).strip()
                )

        # ----------------------------------------------------------- #
        # PRIMEIRO CONSULTA O BANCO RHWEB PELO NOME
        # ----------------------------------------------------------- #

        print(
            f"\n[RHWEB] Consultando banco pelo nome: {nome}"
        )

        resultado = buscar_servidor_rhweb(
            valor_busca=nome
        )

        print(
            f"[RHWEB] Resultado do banco antes do scraping: {resultado}"
)

        # ----------------------------------------------------------- #
        # CASO NÃO EXISTA NO BANCO, EXECUTA O SCRAPING PELO NOME
        # ----------------------------------------------------------- #

        if not resultado:

            print(
                f"[RHWEB] Nenhum dado encontrado."
                f" Iniciando scraping para: {nome}"
            )

            with st.spinner(
                f"Servidor {nome} não encontrado no banco RHweb. "
                f"Consultando o sistema RHweb..."
            ):

                resultado_scraping = executar_scraping_rhweb(
                    nome_servidor=nome
                )

            print(
                f"[RHWEB] Retorno do scraping: {resultado_scraping}"
            )

            # ------------------------------------------------------- #
            # DEPOIS DO SCRAPING CONSULTA NOVAMENTE PELO NOME
            # ------------------------------------------------------- #

            resultado = buscar_servidor_rhweb(
                valor_busca=nome
            )

            print(
                f"[RHWEB] Resultado do banco depois do scraping: "
                f"{resultado}"
            )

        # ----------------------------------------------------------- #
        # FILTRA SOMENTE AS MATRÍCULAS ESCOLHIDAS PELO USUÁRIO
        # ----------------------------------------------------------- #

        matriculas_encontradas = []

        if resultado:

            for registro in resultado:

                matricula_resultado = str(
                    registro[0]
                ).strip()

                if (
                    matricula_resultado
                    in matriculas_selecionadas
                ):

                    resultados_rhweb.append(
                        registro
                    )

                    if (
                        matricula_resultado
                        not in matriculas_encontradas
                    ):

                        matriculas_encontradas.append(
                            matricula_resultado
                        )

        # ----------------------------------------------------------- #
        # IDENTIFICA MATRÍCULAS QUE CONTINUARAM NÃO ENCONTRADAS
        # ----------------------------------------------------------- #

        for matricula in matriculas_selecionadas:

            if matricula not in matriculas_encontradas:

                matriculas_rhweb_nao_encontradas.append(
                    matricula
                )

    # --------------------------------------------------------------- #
    # CONSULTA RISOLUTO
    # --------------------------------------------------------------- #

    for vinculo in vinculos_risoluto:

        matricula = vinculo[0]

        resultado = buscar_servidor_risoluto(
            valor_busca=matricula
        )

        if resultado:

            resultados_risoluto.extend(
                resultado
            )

        else:

            matriculas_risoluto_nao_encontradas.append(
                matricula
            )

    return (
        resultados_rhweb,
        resultados_risoluto,
        matriculas_rhweb_nao_encontradas,
        matriculas_risoluto_nao_encontradas
    )












# ------------------------------------------------------------------- #
# EXIBIÇÃO DOS RESULTADOS DO RHWEB
# ------------------------------------------------------------------- #

def exibir_resultados_rhweb(
        resultados_rhweb,
        matriculas_nao_encontradas
):

    if resultados_rhweb:

        st.write(
            "**Dados encontrados no RHweb:**"
        )

        for resultado in resultados_rhweb:

            st.write(
                f"- Matrícula: {resultado[0]} | "
                f"Nome: {resultado[1]}"
            )

    if matriculas_nao_encontradas:

        st.warning(
            "Matrícula(s) não encontrada(s) no RHweb: "
            + ", ".join(
                str(matricula)
                for matricula in matriculas_nao_encontradas
            )
        )










# ------------------------------------------------------------------- #
# EXIBIÇÃO DOS RESULTADOS DO RISOLUTO
# ------------------------------------------------------------------- #

def exibir_resultados_risoluto(
        resultados_risoluto,
        matriculas_nao_encontradas
):

    if resultados_risoluto:

        st.write(
            "**Dados encontrados no Risoluto:**"
        )

        for resultado in resultados_risoluto:

            st.write(
                f"- Matrícula: {resultado[0]} | "
                f"Nome: {resultado[1]}"
            )

    if matriculas_nao_encontradas:

        st.warning(
            "Matrícula(s) não encontrada(s) no Risoluto: "
            + ", ".join(
                str(matricula)
                for matricula in matriculas_nao_encontradas
            )
        )













# ------------------------------------------------------------------- #
# PROCESSAMENTO DO SERVIDOR SELECIONADO
# ------------------------------------------------------------------- #

def processar_servidor_selecionado(
        servidor_selecionado
):

    if servidor_selecionado is None:
        return

    st.success(
        "Servidor selecionado com sucesso."
    )

    vinculos_rhweb, vinculos_risoluto = direcionar_vinculos(
        vinculos_selecionados=servidor_selecionado
    )

    (
        resultados_rhweb,
        resultados_risoluto,
        matriculas_rhweb_nao_encontradas,
        matriculas_risoluto_nao_encontradas
    ) = consultar_vinculos(
        vinculos_rhweb=vinculos_rhweb,
        vinculos_risoluto=vinculos_risoluto
    )

    exibir_resultados_rhweb(
        resultados_rhweb=resultados_rhweb,
        matriculas_nao_encontradas=matriculas_rhweb_nao_encontradas
    )

    exibir_resultados_risoluto(
        resultados_risoluto=resultados_risoluto,
        matriculas_nao_encontradas=matriculas_risoluto_nao_encontradas
    )











# ------------------------------------------------------------------- #
# FUNÇÃO PRINCIPAL
# ------------------------------------------------------------------- #

def main():

    titulo_pagina()

    inicializar_variaveis()

    buscar, valor_busca = gerar_tela_pesquisa()

    executar_busca(
        buscar=buscar,
        valor_busca=valor_busca
    )

    servidor_selecionado = escolha_de_usuario()

    processar_servidor_selecionado(
        servidor_selecionado=servidor_selecionado
    )


# ------------------------------------------------------------------- #
# EXECUÇÃO DO SISTEMA
# ------------------------------------------------------------------- #

if __name__ == "__main__":

    main()