# Importações

import streamlit as st
import psycopg2
import tomllib

from pathlib import Path


# ------------------------------------------------------------------- #
# CONEXÃO COM O BANCO DE DADOS
# ------------------------------------------------------------------- #


def conexao_db():

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
            password=db["password"],
        )

        cursor = conn.cursor()

        return conn, cursor

    except Exception as erro:

        st.error(
            f"Erro ao conectar com o banco de dados: "
            f"{type(erro).__name__}: {erro}"
        )

        return None, None


# ------------------------------------------------------------------- #
# BUSCA DE SERVIDORES PELO NOME
# ------------------------------------------------------------------- #


def buscar_nome(nome_servidor):

    conn = None
    cursor = None

    try:

        conn, cursor = conexao_db()

        if conn is None or cursor is None:

            return []

        partes_nome = nome_servidor.strip().split()

        condicoes = []
        parametros = []

        for parte in partes_nome:

            condicoes.append(
                "LOWER(nome) LIKE LOWER(%s)"
            )

            parametros.append(
                f"%{parte}%"
            )

        filtro_nome = " AND ".join(
            condicoes
        )

        sql = f"""
        SELECT DISTINCT
            nome,
            cpf
        FROM dados_servidor
        WHERE {filtro_nome}
        ORDER BY nome, cpf
        """

        cursor.execute(
            sql,
            parametros
        )

        resultados = cursor.fetchall()

        return resultados

    except Exception as erro:

        st.error(
            f"Erro ao buscar servidor: {erro}"
        )

        return []

    finally:

        if cursor is not None:

            cursor.close()

        if conn is not None:

            conn.close()


# ------------------------------------------------------------------- #
# BUSCA DE MATRÍCULAS PELO CPF
# ------------------------------------------------------------------- #


def buscar_matriculas(cpf_servidor):

    conn = None
    cursor = None

    try:

        conn, cursor = conexao_db()

        if conn is None or cursor is None:

            return []

        sql = """
        SELECT DISTINCT
            matricula
        FROM dados_servidor
        WHERE cpf = %s
        ORDER BY matricula
        """

        cursor.execute(
            sql,
            (
                cpf_servidor,
            )
        )

        matriculas = cursor.fetchall()

        return matriculas

    except Exception as erro:

        st.error(
            f"Erro ao buscar matrículas: {erro}"
        )

        return []

    finally:

        if cursor is not None:

            cursor.close()

        if conn is not None:

            conn.close()


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

    if "nome_pesquisado" not in st.session_state:

        st.session_state.nome_pesquisado = ""


# ------------------------------------------------------------------- #
# FORMULÁRIO DE PESQUISA
# ------------------------------------------------------------------- #


def gerar_tela_pesquisa():

    with st.form(
        "formulario_busca"
    ):

        nome_servidor = st.text_input(
            "Digite aqui o nome da pessoa que você busca:",
            value=st.session_state.nome_pesquisado
        )

        buscar = st.form_submit_button(
            "Buscar servidor",
            type="primary"
        )

    return buscar, nome_servidor


# ------------------------------------------------------------------- #
# VALIDAÇÃO DO NOME
# ------------------------------------------------------------------- #


def validar_nome_servidor(nome_servidor):

    nome_servidor = nome_servidor.strip()

    partes_nome = nome_servidor.split()

    quantidade_letras = len(
        nome_servidor.replace(
            " ",
            ""
        )
    )

    if quantidade_letras < 5:

        st.warning(
            "O nome deve possuir pelo menos 5 letras."
        )

        return False

    if len(partes_nome) < 2:

        st.warning(
            "Digite pelo menos o nome e o sobrenome."
        )

        return False

    return True


# ------------------------------------------------------------------- #
# EXECUÇÃO DA BUSCA
# ------------------------------------------------------------------- #


def executar_busca(
        buscar,
        nome_servidor
):

    if not buscar:

        return

    nome_servidor = nome_servidor.strip()

    if not nome_servidor:

        st.warning(
            "Digite um nome antes de realizar a busca."
        )

        st.session_state.resultados = []
        st.session_state.servidor_selecionado = None
        st.session_state.nome_pesquisado = ""

        return

    nome_valido = validar_nome_servidor(
        nome_servidor=nome_servidor
    )

    if not nome_valido:

        st.session_state.resultados = []
        st.session_state.servidor_selecionado = None

        return

    resultados = buscar_nome(
        nome_servidor=nome_servidor
    )

    st.session_state.resultados = resultados

    st.session_state.servidor_selecionado = None

    st.session_state.nome_pesquisado = nome_servidor

    if resultados:

        st.success(
            f"{len(resultados)} servidor(es) encontrado(s)."
        )

    else:

        st.info(
            "Nenhum servidor foi encontrado."
        )


# ------------------------------------------------------------------- #
# SELEÇÃO DO SERVIDOR
# ------------------------------------------------------------------- #


def escolha_de_usuario():

    resultados = st.session_state.resultados

    if not resultados:

        return None

    servidor_selecionado = st.radio(
        "Selecione o servidor que deseja utilizar:",
        options=resultados,
        index=None,
        format_func=lambda servidor: (
            f"{servidor[0]} - CPF: "
            f"{servidor[1] if servidor[1] else 'Não informado'}"
        )
    )

    st.session_state.servidor_selecionado = (
        servidor_selecionado
    )

    if servidor_selecionado is None:

        return None

    nome_servidor = servidor_selecionado[0]

    cpf_servidor = servidor_selecionado[1]

    st.subheader(
        "Servidor selecionado"
    )

    st.write(
        f"**Nome:** {nome_servidor}"
    )

    st.write(
        f"**CPF:** "
        f"{cpf_servidor if cpf_servidor else 'Não informado'}"
    )

    if not cpf_servidor:

        st.warning(
            "O servidor selecionado não possui CPF cadastrado. "
            "Não foi possível consultar as matrículas pelo CPF."
        )

        return servidor_selecionado

    matriculas = buscar_matriculas(
        cpf_servidor=cpf_servidor
    )

    st.write(
        "**Matrículas:**"
    )

    if matriculas:

        for matricula in matriculas:

            st.write(
                f"- {matricula[0]}"
            )

    else:

        st.warning(
            "Nenhuma matrícula foi encontrada."
        )

    return servidor_selecionado


# ------------------------------------------------------------------- #
# FUNÇÃO PRINCIPAL
# ------------------------------------------------------------------- #


def main():

    titulo_pagina()

    inicializar_variaveis()

    buscar, nome_servidor = gerar_tela_pesquisa()

    executar_busca(
        buscar=buscar,
        nome_servidor=nome_servidor
    )

    servidor_selecionado = escolha_de_usuario()

    if servidor_selecionado is not None:

        st.success(
            "Servidor selecionado com sucesso."
        )


# ------------------------------------------------------------------- #
# EXECUÇÃO DO SISTEMA
# ------------------------------------------------------------------- #


if __name__ == "__main__":

    main()