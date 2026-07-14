# Importações

import streamlit as st
import psycopg2 
import tomllib
import pathlib
from pathlib import Path

def conexao_db():
    try:

        caminho_config = Path.cwd() / "config.toml"

        with open(caminho_config, "rb") as arquivo:
            config = tomllib.load(arquivo)

        db = config["rhweb"]

        conn = psycopg2.connect(
            host=db["host"],
            port=db["port"],
            dbname=db["dbname"],
            user=db["user"],
            password=db["password"],
        )

        print("Banco conectado com sucesso")

        cursor = conn.cursor()

        return conn, cursor

    except Exception as e:
        print("Erro ao conectar com o banco de dados:")
        print(type(e).__name__)
        print(e)
        return None, None
    
conexao_db()

#-----------------------------------------------------------------------------------#
def buscar_nome(nome_servidor):

    conn = None
    cursor = None

    try:

        conn, cursor = conexao_db()

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
        SELECT
            nome,
            cpf,
            matricula
        FROM dados_servidor
        WHERE {filtro_nome}
        ORDER BY nome
        """

        cursor.execute(
            sql,
            parametros
        )

        return cursor.fetchall()

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

def buscar_matriculas(cpf_servidor):

    conn = None
    cursor = None

    try:

        conn, cursor = conexao_db()

        sql = """
        SELECT matricula
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

        return cursor.fetchall()

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


def titulo_pagina():

    st.title(
        "Busca de Servidores"
    )


# ------------------------------------------------------------------- #


def inicializar_variaveis():

    # Inicializa os resultados da busca.
    if "resultados" not in st.session_state:

        st.session_state.resultados = []

    # Inicializa o servidor selecionado.
    if "servidor_selecionado" not in st.session_state:

        st.session_state.servidor_selecionado = None


# ------------------------------------------------------------------- #


def gerar_tela_pesquisa():

    # Agrupa os campos e envia os dados somente
    # quando o botão do formulário for clicado.
    with st.form(
        "formulario_busca"
    ):

        # Permite ao usuário informar o nome
        # utilizado na busca.
        nome_servidor = st.text_input(
            "Digite aqui o nome da pessoa que você busca:"
        )

        # Envia os campos presentes no formulário.
        buscar = st.form_submit_button(
            "Buscar servidor",
            type="primary"
        )

    return buscar, nome_servidor


# ------------------------------------------------------------------- #


def validar_nome_servidor(nome_servidor):

    # Remove espaços no início e no final.
    nome_servidor = nome_servidor.strip()

    # Separa o nome pelas palavras digitadas.
    partes_nome = nome_servidor.split()

    # Verifica se o nome possui pelo menos 5 letras.
    quantidade_letras = len(
        nome_servidor.replace(" ", "")
    )

    if quantidade_letras < 5:

        st.warning(
            "O nome deve possuir pelo menos 5 letras."
        )

        return False

    # Verifica se foram informados pelo menos dois nomes.
    if len(partes_nome) < 2:

        st.warning(
            "Digite pelo menos o nome e o sobrenome."
        )

        return False

    return True



#----------------------------------------------------------------#




def executar_busca(
        buscar,
        nome_servidor
):

    # Executa a busca somente quando
    # o botão for clicado.
    if not buscar:
        return

    # Verifica se o usuário digitou algum nome.
    if not nome_servidor.strip():

        st.warning(
            "Digite um nome antes de realizar a busca."
        )

        st.session_state.resultados = []
        st.session_state.servidor_selecionado = None

        return

    # Verifica se o nome atende aos requisitos.
    nome_valido = validar_nome_servidor(
        nome_servidor=nome_servidor
    )

    if not nome_valido:

        st.session_state.resultados = []
        st.session_state.servidor_selecionado = None

        return

    # Busca os servidores com o nome informado.
    resultados = buscar_nome(
        nome_servidor=nome_servidor
    )

    # Guarda os resultados entre as atualizações
    # automáticas do Streamlit.
    st.session_state.resultados = resultados

    # Limpa a seleção feita anteriormente.
    st.session_state.servidor_selecionado = None

    if resultados:

        st.success(
            f"{len(resultados)} servidor(es) encontrado(s)."
        )

    else:

        st.info(
            "Nenhum servidor foi encontrado."
        )


# ------------------------------------------------------------------- #


def escolha_de_usuario():

    resultados = st.session_state.resultados

    # Não mostra o campo de seleção enquanto
    # nenhuma busca tiver resultados.
    if not resultados:
        return None

    servidor_selecionado = st.radio(
        "Selecione o servidor que deseja utilizar:",
        options=resultados,
        index=None,
        format_func=lambda servidor: (
            f"{servidor[0]} - CPF: {servidor[1]}"
        )
    )

    # Guarda o servidor selecionado.
    st.session_state.servidor_selecionado = (
        servidor_selecionado
    )

    if servidor_selecionado is not None:

        # Guarda o nome do servidor selecionado.
        nome_servidor = servidor_selecionado[0]

        # Guarda o CPF do servidor selecionado.
        cpf_servidor = servidor_selecionado[1]

        # Busca todas as matrículas vinculadas
        # ao CPF do servidor selecionado.
        matriculas = buscar_matriculas(
            cpf_servidor=cpf_servidor
        )

        st.write(
            "Servidor selecionado:"
        )

        st.write(
            f"Nome: {nome_servidor}"
        )

        st.write(
            f"CPF: {cpf_servidor}"
        )

        st.write(
            "Matrículas:"
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


if __name__ == "__main__":

    main()


#------------------------------------------------------------#