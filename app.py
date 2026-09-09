# Importações

import streamlit as st
import psycopg2
import mariadb
import tomllib

from pathlib import Path













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
# BUSCA DE SERVIDOR NO JOAQUINA
# ------------------------------------------------------------------- #

def buscar_servidor_joaquina(valor_busca):

    conn = None
    cursor = None

    try:

        conn, cursor = conexao_joaquina()

        if conn is None or cursor is None:
            return []

        valor_busca = str(valor_busca).strip()

        sql = """
        SELECT
            matricula,
            nome,
            admissao

        FROM dados_do_servidor

        WHERE
            TRIM(matricula::text) = %s
            OR LOWER(nome) LIKE LOWER(%s)

        ORDER BY
            nome,
            matricula
        """

        cursor.execute(
            sql,
            (
                valor_busca,
                f"%{valor_busca}%"
            )
        )

        resultados = cursor.fetchall()

        return resultados

    except Exception as erro:

        st.error(
            f"Erro ao buscar servidor no Joaquina: "
            f"{type(erro).__name__}: {erro}"
        )

        return []

    finally:

        if cursor is not None:
            cursor.close()

        if conn is not None:
            conn.close()


# ------------------------------------------------------------------- #
# BUSCA DE SERVIDOR NO RHWEB
# ------------------------------------------------------------------- #

def buscar_servidor_rhweb(valor_busca):

    conn = None
    cursor = None

    try:

        conn, cursor = conexao_rhweb()

        if conn is None or cursor is None:
            return []

        valor_busca = str(valor_busca).strip()

        sql = """
        SELECT
            ds.matricula,
            ds.nome,
            ds.cpf,
            cf.data_admissao

        FROM dados_servidor AS ds

        LEFT JOIN cargo_do_funcionario AS cf
            ON cf.fk_dados_servidor = ds.id

        WHERE
            ds.matricula::text = %s
            OR LOWER(ds.nome) LIKE LOWER(%s)

        ORDER BY
            ds.nome,
            ds.matricula
        """

        cursor.execute(
            sql,
            (
                valor_busca,
                f"%{valor_busca}%"
            )
        )

        resultados = cursor.fetchall()

        return resultados

    except Exception as erro:

        st.error(
            f"Erro ao buscar servidor no RHweb: "
            f"{type(erro).__name__}: {erro}"
        )

        return []

    finally:

        if cursor is not None:
            cursor.close()

        if conn is not None:
            conn.close()


# ------------------------------------------------------------------- #
# BUSCA DE SERVIDOR NO RISOLUTO
# ------------------------------------------------------------------- #

def buscar_servidor_risoluto(valor_busca):

    conn = None
    cursor = None

    try:

        conn, cursor = conexao_risoluto()

        if conn is None or cursor is None:
            return []

        valor_busca = str(valor_busca).strip()

        sql = """
        SELECT
            u.matricula,
            u.nome,
            u.cpf,
            MAX(fp.data) AS ultima_data

        FROM pk_usuarios AS u

        LEFT JOIN tb_fp_por_profissional AS fp
            ON fp.matricula = u.matricula

        WHERE
            u.matricula = ?
            OR LOWER(u.nome) LIKE LOWER(?)

        GROUP BY
            u.matricula,
            u.nome,
            u.cpf

        ORDER BY
            u.nome,
            u.matricula
        """

        cursor.execute(
            sql,
            (
                valor_busca,
                f"%{valor_busca}%"
            )
        )

        resultados = cursor.fetchall()

        return resultados

    except Exception as erro:

        st.error(
            f"Erro ao buscar servidor no Risoluto: "
            f"{type(erro).__name__}: {erro}"
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

    if "valor_pesquisado" not in st.session_state:
        st.session_state.valor_pesquisado = ""


















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

    valor_busca = valor_busca.strip()

    # --------------------------------------------------------------- #
    # CAMPO VAZIO
    # --------------------------------------------------------------- #

    if not valor_busca:

        st.warning(
            "Digite o nome ou a matrícula do servidor."
        )

        return False

    # --------------------------------------------------------------- #
    # BUSCA POR MATRÍCULA
    # --------------------------------------------------------------- #

    if valor_busca.isdigit():

        if len(valor_busca) < 3:

            st.warning(
                "Digite uma matrícula válida."
            )

            return False

        return True

    # --------------------------------------------------------------- #
    # BUSCA POR NOME
    # --------------------------------------------------------------- #

    partes_nome = valor_busca.split()

    quantidade_letras = len(
        valor_busca.replace(
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
        valor_busca
):

    if not buscar:
        return

    valor_busca = valor_busca.strip()

    if not valor_busca:

        st.warning(
            "Digite um nome ou matrícula antes de realizar a busca."
        )

        st.session_state.resultados = []
        st.session_state.servidor_selecionado = None
        st.session_state.valor_pesquisado = ""

        return

    valor_valido = validar_valor_busca(
        valor_busca=valor_busca
    )

    if not valor_valido:

        st.session_state.resultados = []
        st.session_state.servidor_selecionado = None

        return

    resultados = buscar_servidor_joaquina(
        valor_busca=valor_busca
    )

    st.session_state.resultados = resultados
    st.session_state.servidor_selecionado = None
    st.session_state.valor_pesquisado = valor_busca

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

    resultados = st.session_state.resultados

    if not resultados:
        return None

    # --------------------------------------------------------------- #
    # IDENTIFICA OS NOMES ENCONTRADOS
    # --------------------------------------------------------------- #

    nomes_encontrados = []

    for resultado in resultados:

        nome = resultado[1]

        if nome not in nomes_encontrados:
            nomes_encontrados.append(nome)

    # --------------------------------------------------------------- #
    # SE HOUVER MAIS DE UM SERVIDOR, ESCOLHE PRIMEIRO O NOME
    # --------------------------------------------------------------- #

    if len(nomes_encontrados) > 1:

        nome_selecionado = st.radio(
            "Selecione o servidor que deseja utilizar:",
            options=nomes_encontrados,
            index=None
        )

        if nome_selecionado is None:
            return None

        vinculos = []

        for resultado in resultados:

            if resultado[1] == nome_selecionado:
                vinculos.append(resultado)

    else:

        nome_selecionado = nomes_encontrados[0]
        vinculos = resultados

    # --------------------------------------------------------------- #
    # MONTA AS OPÇÕES DE MATRÍCULA
    # --------------------------------------------------------------- #

    opcoes = vinculos.copy()

    if len(vinculos) > 1:
        opcoes.append("TODAS")

    # --------------------------------------------------------------- #
    # FORMATA O TEXTO DAS OPÇÕES
    # --------------------------------------------------------------- #

    def formatar_opcao(opcao):

        if opcao == "TODAS":
            return "Todas as matrículas"

        matricula = opcao[0]
        admissao = opcao[2]

        if admissao:
            admissao_formatada = admissao.strftime(
                "%d/%m/%Y"
            )

        else:
            admissao_formatada = "Não informada"

        return (
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

    if matricula_selecionada is None:
        return None

    # --------------------------------------------------------------- #
    # UMA OU TODAS AS MATRÍCULAS
    # --------------------------------------------------------------- #

    if matricula_selecionada == "TODAS":

        vinculos_selecionados = vinculos

    else:

        vinculos_selecionados = [
            matricula_selecionada
        ]

    st.session_state.servidor_selecionado = (
        vinculos_selecionados
    )

    # --------------------------------------------------------------- #
    # EXIBE O QUE FOI SELECIONADO
    # --------------------------------------------------------------- #

    st.subheader(
        "Servidor selecionado"
    )

    st.write(
        f"**Nome:** {nome_selecionado}"
    )

    for vinculo in vinculos_selecionados:

        matricula = vinculo[0]
        admissao = vinculo[2]

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

    for vinculo in vinculos_rhweb:

        matricula = vinculo[0]

        resultado = buscar_servidor_rhweb(
            valor_busca=matricula
        )

        if resultado:

            resultados_rhweb.extend(
                resultado
            )

        else:

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