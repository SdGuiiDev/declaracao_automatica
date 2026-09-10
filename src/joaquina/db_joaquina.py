#!/usr/bin/env python
# coding: utf-8

# # Bibliotecas

# In[61]:


import psycopg2
from psycopg2.extras import execute_values
from psycopg2 import sql

import tomllib

import pandas as pd

import pathlib
from pathlib import Path

import datetime
from datetime import date


# # def localizar_raiz_projeto
#     - Irá organizar os arquivos do projeto

# In[62]:


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


# # def conexao_db
#     - Serve para abrir a conexao com o banco de dados

# In[63]:


def conexao_db():

    # Lê as configurações do banco.
    with open(CAMINHO_CONFIG, "rb") as arquivo:
        config = tomllib.load(arquivo)

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


# # Tratmentos do codigo

# ## def tratamento_de_datas

# In[64]:


def tratamento_de_datas(valor):

    """
    Converte datas para um formato aceito pelo PostgreSQL.

    Aceita:
    - 25/09/2005
    - 25-09-2005
    - 2005-09-25
    - 2005/09/25
    - datetime/date/pandas Timestamp

    Retorna:
    - date válido
    - None quando estiver vazio, NaN, NaT ou inválido
    """

    if valor is None:
        return None

    if pd.isna(valor):
        return None

    if isinstance(valor, pd.Timestamp):
        return valor.date()

    if isinstance(valor, datetime.datetime):
        return valor.date()

    if isinstance(valor, date):
        return valor

    valor = str(valor).strip()

    if valor == "":
        return None

    formatos = [
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%Y-%m-%d",
        "%Y/%m/%d"
    ]

    for formato in formatos:
        try:
            return datetime.datetime.strptime(
                valor,
                formato
            ).date()

        except ValueError:
            continue

    return None


# ## def tratar_inteiro

# In[65]:


def tratar_inteiro(valor):
        if pd.isna(valor):
                return None

        valor = str(valor).strip()

        if valor == "":
                return None

        try:
                return int(float(valor))

        except (ValueError, TypeError):
                return None


# ## def tratar_valor_id

# In[66]:


def tratar_valor_id(valor):
    if pd.isna(valor):
        return None

    valor = str(valor).strip()

    if valor =="":
        return None

    return valor


# # def atualizar_upsert

# In[67]:


def atualizar_upsert(
    tabela,
    coluna,
    valor,
    conn,
    cursor
):

    valor = tratar_valor_id(valor)

    if valor is None:
        return None

    query = sql.SQL("""
        INSERT INTO {tabela} ({coluna})
        VALUES (%s)
        ON CONFLICT ({coluna})
        DO UPDATE SET {coluna} = EXCLUDED.{coluna}
        RETURNING id
    """).format(
        tabela=sql.Identifier(tabela),
        coluna=sql.Identifier(coluna)
    )

    cursor.execute(
        query,
        (valor,)
    )

    resultado = cursor.fetchone()

    if resultado:
        return resultado[0]

    return None


# # Obter dados SQL

# ## def obeter_sql_dados_servidor

# In[68]:


def obter_sql_dados_do_servidor():

    sql_dados_do_servidor = """
    INSERT INTO dados_do_servidor (
    matricula,
    nome,
    fk_cargo,
    fk_lotacao,
    admissao,
    aposentadoria,
    entrada_lotacao,
    termino,
    desligamento,
    fk_regime
    )
    VALUES %s
    ON CONFLICT 
        (matricula)
    DO UPDATE SET
        nome = EXCLUDED.nome,
        fk_cargo = EXCLUDED.fk_cargo,
        fk_lotacao = EXCLUDED.fk_lotacao,
        admissao = EXCLUDED.admissao,
        aposentadoria = EXCLUDED.aposentadoria,
        entrada_lotacao = EXCLUDED.entrada_lotacao,
        termino = EXCLUDED.termino,
        desligamento = EXCLUDED.desligamento,
        fk_regime = EXCLUDED.fk_regime
    RETURNING id;
    """

    return sql_dados_do_servidor


# In[69]:


def atualizar_upsert_lotacao(
    cod_lotacao,
    lotacao,
    cursor
):

    cod_lotacao = tratar_valor_id(cod_lotacao)
    lotacao = tratar_valor_id(lotacao)

    if cod_lotacao is None or lotacao is None:
        return None

    query = """
        INSERT INTO pk_lotacoes (
            cod_lotacao,
            lotacao
        )
        VALUES (%s, %s)
        ON CONFLICT (cod_lotacao)
        DO UPDATE SET
            lotacao = EXCLUDED.lotacao
        RETURNING cod_lotacao;
    """

    cursor.execute(
        query,
        (
            cod_lotacao,
            lotacao
        )
    )

    resultado = cursor.fetchone()

    if resultado:
        return resultado[0]

    return None


# In[70]:


def atualizar_upsert_cargo(
    cod_cargo,
    cargo,
    cursor
):

    cod_cargo = tratar_valor_id(cod_cargo)
    cargo = tratar_valor_id(cargo)

    if cod_cargo is None or cargo is None:
        return None

    query = """
        INSERT INTO pk_cargos (
            cod_cargo,
            cargo
        )
        VALUES (%s, %s)
        ON CONFLICT (cod_cargo)
        DO UPDATE SET
            cargo = EXCLUDED.cargo
        RETURNING cod_cargo;
    """

    cursor.execute(
        query,
        (
            cod_cargo,
            cargo
        )
    )

    resultado = cursor.fetchone()

    if resultado:
        return resultado[0]

    return None


# # Obter os IDs das chaves primarias

# ## def obter_ids_servidor

# In[71]:


def obter_ids_servidor(linha, conn, cursor):

    id_regime_servidor = atualizar_upsert(
        tabela="pk_regime_servidor",
        coluna="regime",
        valor=linha["regime"],
        conn=conn,
        cursor=cursor
    )

    cod_lotacao = atualizar_upsert_lotacao(
        cod_lotacao=linha["cod_lotacao"],
        lotacao=linha["lotacao"],
        cursor=cursor
    )

    cod_cargo = atualizar_upsert_cargo(
        cod_cargo=linha["cod_cargo"],
        cargo=linha["cargo"],
        cursor=cursor
    )

    return {
        "id_regime_servidor": id_regime_servidor,
        "cod_lotacao": cod_lotacao,
        "cod_cargo": cod_cargo
    }


# # def mostrar_ids

# In[72]:


def mostrar_ids(
    id_regime_servidor,
    cod_lotacao,
    cod_cargo
):

    print("Regime do servidor:", id_regime_servidor)
    print("Lotação do servidor:", cod_lotacao)
    print("Cargo do funcionário:", cod_cargo)


# # def montar_dados_servidor

# In[73]:


def montar_dados_servidor(
        index,
        linha,
        ids,
        dados_servidor
        ):

        dados_servidor.append((
                tratar_valor_id(linha["matricula"]),
                tratar_valor_id(linha["nome"]),
                ids["cod_cargo"],
                ids["cod_lotacao"],
                tratamento_de_datas(linha["admissao"]),
                tratamento_de_datas(linha["aposentadoria"]),
                tratamento_de_datas(linha["entrada_lotacao"]),
                tratamento_de_datas(linha["termino"]),
                tratamento_de_datas(linha["desligamento"]),
                ids["id_regime_servidor"]
        ))


# # def montar_dads_linhas

# In[74]:


def montar_dados_linha(
    index,
    linha_servidor,
    conn,
    cursor,
    dados_do_servidor
):

    ids_servidor = obter_ids_servidor(
        linha=linha_servidor,
        conn=conn,
        cursor=cursor
    )

    mostrar_ids(
        id_regime_servidor=ids_servidor["id_regime_servidor"],
        cod_cargo=ids_servidor["cod_cargo"],
        cod_lotacao=ids_servidor["cod_lotacao"]
    )

    montar_dados_servidor(
        index=index,
        linha=linha_servidor,
        ids=ids_servidor,
        dados_servidor=dados_do_servidor
    )


# # def verificar_listas_vazias

# In[75]:


def verificar_listas_vazias(dados_do_servidor):
    if(
        len(dados_do_servidor) == 0
    ):
        print("Nenhum funcionario encontrado para inserir")
        return True

    return False


# # def executar_query

# In[76]:


def executar_query(
    cursor,
    conn,
    sql_dados_do_servidor,
    dados_do_servidor
):

    if len(dados_do_servidor) > 0:

        execute_values(
            cursor,
            sql_dados_do_servidor,
            dados_do_servidor
        )

        conn.commit()

        print(
            f"{len(dados_do_servidor)} registro(s) "
            "de servidor processado(s) no banco com sucesso."
        )


# # def fechar_conexao

# In[77]:


def fechar_conexao(conn, cursor):
# Verifica se o cursor foi criado antes de tentar fechá-lo.
    if cursor:
            # Fecha o cursor usado na operação.
            cursor.close()

    # Verifica se a conexão foi criada antes de tentar fechá-la.
    if conn:
            # Fecha a conexão com o banco.
            conn.close()


# # def inserir_dados

# In[78]:


def inserir_dados(df_dados_do_servidor):

    conn = None
    cursor = None

    dados_do_servidor = []

    try:
        conn, cursor = conexao_db()

        for index, linha_servidor in df_dados_do_servidor.iterrows():

            montar_dados_linha(
                index=index,
                linha_servidor=linha_servidor,
                conn=conn,
                cursor=cursor,
                dados_do_servidor=dados_do_servidor
            )

        if verificar_listas_vazias(dados_do_servidor):
            return False

        sql_dados_do_servidor = (
            obter_sql_dados_do_servidor()
        )

        executar_query(
            cursor=cursor,
            conn=conn,
            sql_dados_do_servidor=sql_dados_do_servidor,
            dados_do_servidor=dados_do_servidor
        )

        return True

    except Exception as erro:

        if conn:
            conn.rollback()

        print(
            "Erro ao inserir dados no banco:"
        )

        print(
            f"{type(erro).__name__}: {erro}"
        )

        return False

    finally:

        fechar_conexao(
            conn=conn,
            cursor=cursor
        )


# # Criação de Busca por servidor

# ## def buscar_servidor

# In[79]:


def buscar_servidor(valor_busca):

    conn = None
    cursor = None

    try:

        conn, cursor = conexao_db()

        valor_busca = str(valor_busca).strip()

        sql = """
        SELECT
            matricula,
            nome,
            admissao
        FROM dados_do_servidor
        WHERE
            matricula::text =%s
            OR LOWER (nome) LIKE LOWER (%s)
        ORDER BY nome
        """

        cursor.execute(
            sql,
            (valor_busca, f"%{valor_busca}%")
        )

        resultados = cursor.fetchall()

        return resultados

    except Exception as erro:

        print(f"Erro ao buscar servidor \n{type(erro).__name__}: {erro}")

        return []

    finally:

        fechar_conexao(
            conn=conn,
            cursor=cursor
        )


# ## def teste

# In[80]:


resultado = buscar_servidor(
    valor_busca = "Daniela Aires campos"
)

print(resultado)


# In[81]:


resultado = buscar_servidor(
    valor_busca = "378011"
)

print(resultado)

