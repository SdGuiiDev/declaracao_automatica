#!/usr/bin/env python
# coding: utf-8

# # Bibliotecas

# In[23]:


#########################
##      MARIADB        ##
#########################
import mariadb


#########################
#    TOMLLIB            #
#########################
import tomllib


#########################
##       PATHLIB       ##
#########################
import pathlib
from pathlib import Path


#########################
##      DATETIME       ##
#########################
import datetime
from datetime import date


#########################
##      pandas         ##
#########################
import pandas as pd


#########################
##      TRACEBACK      ##
#########################
import traceback


# # def raiz_do_projeto

# In[24]:


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

# In[25]:


def conexao_db():
    conn = None
    cursor = None

    try:

        with open(
            CAMINHO_CONFIG,
            "rb"
        ) as arquivo:

            config = tomllib.load(arquivo)

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

        print(f"Erro ao conectar com o banco de dados: {erro}")

        return None, None


# # def tratamento_de_datas

# In[26]:


def tratamento_de_datas(valor):

    if valor is None:
        return None

    if pd.isna(valor):
        return None

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
            return datetime.datetime.strptime(valor, formato).date()

        except ValueError:
            continue

    return None


# # def tratar_inteiro

# In[27]:


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


# # def tratar_valor_id

# In[28]:


def tratar_valor_id(valor):
        if pd.isna(valor):
                return None

        valor = str(valor).strip()

        if valor == "":
                return None

        return valor


# # def atualizar_upsert

# In[29]:


def atualizar_upsert(
        tabela,
        coluna,
        valor,
        conn,
        cursor
):

    if valor is None:
        return None

    query = f"""
        INSERT INTO `{tabela}` (`{coluna}`)
        VALUES (?)
        ON DUPLICATE KEY UPDATE
            id = LAST_INSERT_ID(id)
    """

    cursor.execute(query, (valor,))

    return cursor.lastrowid


# # def obter_dados_do_servidor

# In[30]:


def obter_dados_do_servidor():

    sql_obter_dados_do_servidor = """
        INSERT INTO pk_usuario (
            matricula,
            nome,
            cpf,
            especialidade
        )
        VALUES (?, ?, ?, ?)

        ON DUPLICATE KEY UPDATE
            nome = VALUES(nome),
            cpf = VALUES(cpf),
            especialidade = VALUES(especialidade)
    """

    return sql_obter_dados_do_servidor


# # def obter_sql_servidor

# In[31]:


def obter_sql_servidor():

    sql_dados_servidor = """
    INSERT INTO tb_fp_por_profissional(
        matricula_data,
        competencia,
        projecao_mensal,
        horas_trabalhadas_competencia,
        dias_faltas,
        horas_faltas,
        horas_adicionais,
        saldo_competencia,
        horas_aprovadas,
        trab_sobre_aviso,
        sobre_aviso,
        horas_plantao,
        unidade,
        matricula,
        especialidade,
        data,
        entrada_1,
        saida_1,
        entrada_2,
        saida_2,
        entrada_3,
        saida_3,
        entrada_4,
        saida_4,
        nao_aprovadas,
        horas_trabalhadas_dia,
        motivo_falta,
        saldo_dia,
        ultima_atualizacao
    )
    VALUES (
        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
        ?, ?, ?, ?, ?, ?, ?, ?, ?
    )
    ON DUPLICATE KEY UPDATE
        competencia = VALUES(competencia),
        projecao_mensal = VALUES(projecao_mensal),
        horas_trabalhadas_competencia = VALUES(horas_trabalhadas_competencia),
        dias_faltas = VALUES(dias_faltas),
        horas_faltas = VALUES(horas_faltas),
        horas_adicionais = VALUES(horas_adicionais),
        saldo_competencia = VALUES(saldo_competencia),
        horas_aprovadas = VALUES(horas_aprovadas),
        trab_sobre_aviso = VALUES(trab_sobre_aviso),
        sobre_aviso = VALUES(sobre_aviso),
        horas_plantao = VALUES(horas_plantao),
        unidade = VALUES(unidade),
        matricula = VALUES(matricula),
        especialidade = VALUES(especialidade),
        data = VALUES(data),
        entrada_1 = VALUES(entrada_1),
        saida_1 = VALUES(saida_1),
        entrada_2 = VALUES(entrada_2),
        saida_2 = VALUES(saida_2),
        entrada_3 = VALUES(entrada_3),
        saida_3 = VALUES(saida_3),
        entrada_4 = VALUES(entrada_4),
        saida_4 = VALUES(saida_4),
        nao_aprovadas = VALUES(nao_aprovadas),
        horas_trabalhadas_dia = VALUES(horas_trabalhadas_dia),
        motivo_falta = VALUES(motivo_falta),
        saldo_dia = VALUES(saldo_dia),
        ultima_atualizacao = VALUES(ultima_atualizacao)
    """

    return sql_dados_servidor


# # def obter_sqls

# In[32]:


def obter_sqls():

    sql_servidor = obter_sql_servidor()

    sql_dados_do_servidor = obter_dados_do_servidor()

    return sql_servidor, sql_dados_do_servidor


# # def obter_ids_servidor_geral

# In[33]:


def obter_ids_servidor_geral(linha, conn, cursor):

    id_competencia = atualizar_upsert(
        tabela = "pk_competencia",
        coluna = "competencia",
        valor = linha["competencia"],
        conn = conn,
        cursor = cursor
    )

    id_especialidade = atualizar_upsert(
        tabela = "pk_especialidade",
        coluna = "especialidade",
        valor = linha["especialidade"],
        conn = conn,
        cursor = cursor
    )

    id_motivo_falta = atualizar_upsert(
        tabela = "pk_motivo_falta",
        coluna = "motivo_falta",
        valor = linha["motivo_falta"],
        conn = conn,
        cursor = cursor
    )

    id_unidade = atualizar_upsert(
        tabela = "pk_unidade",
        coluna = "unidade",
        valor = linha["unidade"],
        conn = conn,
        cursor = cursor
    )

    return {
        "id_competencia": id_competencia,
        "id_especialidade": id_especialidade,
        "id_motivo_falta": id_motivo_falta,
        "id_unidade": id_unidade,
    }


# # def obter_ids_servidor

# In[34]:


def obter_ids_servidor(linha, conn, cursor):

    matricula = tratar_inteiro(linha["matricula"])

    if matricula is None:
        return {
            "id_matricula": None
        }

    query = """
        SELECT id
        FROM pk_usuario
        WHERE matricula = ?
    """

    cursor.execute(query, (matricula,))

    resultado = cursor.fetchone()

    if resultado:
        id_matricula = resultado[0]
    else:
        id_matricula = None

    return {
        "id_matricula": id_matricula
    }


# # def mostrar_ids

# In[35]:


def mostrar_ids(
        id_competencia,
        id_especialidade,
        id_motivo_falta,
        id_unidade,
        id_matricula
):

    print("Competencia do servidor: ", id_competencia)
    print("Especialidade do servidor: ", id_especialidade)
    print("Motivo de falta: ", id_motivo_falta)
    print("Unidade do servidor: ", id_unidade)
    print("Matricula do funcionario: ", id_matricula)


# # def montar_dados_servidor

# In[36]:


def montar_dados_gerais_servidor(
        index,
        linha,
        ids,
        dados_gerais_servidor
):

    dados_gerais_servidor.append((

        linha["matricula_data"],

        tratar_inteiro(ids["id_competencia"]),

        linha["projecao_mensal"],

        linha["horas_trabalhadas_competencia"],

        linha["dias_faltas"],

        linha["horas_faltas"],

        linha["horas_adicionais"],

        linha["saldo_competencia"],

        linha["horas_aprovadas"],

        linha["trab_sobre_aviso"],

        linha["sobre_aviso"],

        linha["horas_plantao"],

        tratar_inteiro(ids["id_unidade"]),

        tratar_inteiro(linha["matricula"]),

        tratar_inteiro(ids["id_especialidade"]),

        tratamento_de_datas(linha["data"]),

        linha["entrada_1"],
        linha["saida_1"],

        linha["entrada_2"],
        linha["saida_2"],

        linha["entrada_3"],
        linha["saida_3"],

        linha["entrada_4"],
        linha["saida_4"],

        linha["nao_aprovadas"],

        linha["horas_trabalhadas_dia"],

        tratar_inteiro(ids["id_motivo_falta"]),

        linha["saldo_dia"],

        linha["ultima_atualizacao"]

    ))

    print(
        f"Dados do servidor montados na linha {index}"
    )

    return dados_gerais_servidor


# # def montar_dados_servidor

# In[37]:


def montar_dados_servidor(
        index,
        linha,
        ids,
        dados_servidor
):

    dados_servidor.append((

        tratar_inteiro(linha["matricula"]),

        linha["nome"],

        linha["cpf"],

        tratar_inteiro(ids["id_especialidade"])

    ))

    print(
        f"Dados do servidor montados na linha {index}"
    )

    return dados_servidor


# # def montar_dados_linha
# 

# In[38]:


def montar_dados_linha(
        index,
        linha_servidor_geral,
        linha_servidor,
        conn,
        cursor,
        dados_do_servidor_geral,
        dados_do_servidor
):

    ids_servidor_geral = obter_ids_servidor_geral(
        linha=linha_servidor_geral,
        conn=conn,
        cursor=cursor
    )

    ids_servidor = obter_ids_servidor(
        linha=linha_servidor,
        conn=conn,
        cursor=cursor
    )

    mostrar_ids(
        id_competencia=ids_servidor_geral["id_competencia"],
        id_unidade=ids_servidor_geral["id_unidade"],
        id_especialidade=ids_servidor_geral["id_especialidade"],
        id_motivo_falta=ids_servidor_geral["id_motivo_falta"],
        id_matricula=ids_servidor["id_matricula"]
    )

    montar_dados_gerais_servidor(
        index=index,
        linha=linha_servidor_geral,
        ids=ids_servidor_geral,
        dados_gerais_servidor=dados_do_servidor_geral
    )

    montar_dados_servidor(
        index=index,
        linha=linha_servidor,
        ids=ids_servidor_geral,
        dados_servidor=dados_do_servidor
    )


# # def verificar_listas_vazias

# In[39]:


def verificar_listas_vazias(dados_do_servidor, dados_do_servidor_geral):

    if(
        len(dados_do_servidor) == 0 and
        len(dados_do_servidor_geral) ==0
    ):
        print("Nenhum funcionario encontrado para inserir")
        return True

    return False


# # def executar_query

# In[40]:


def executar_query(
        cursor,
        conn,
        sql_obter_dados_do_servidor,
        sql_dados_servidor,
        dados_do_servidor_geral,
        dados_do_servidor
):

    if len(dados_do_servidor) > 0:

        cursor.executemany(
            sql_obter_dados_do_servidor,
            dados_do_servidor
        )

    if len(dados_do_servidor_geral) > 0:

        cursor.executemany(
            sql_dados_servidor,
            dados_do_servidor_geral
        )

    conn.commit()

    print(
        f"{len(dados_do_servidor)} registro(s) "
        "de servidor processado(s) no banco com sucesso."
    )

    print(
        f"{len(dados_do_servidor_geral)} registro(s) "
        "de dados gerais processado(s) no banco com sucesso."
    )


# # def fechar_conexao

# In[41]:


def fechar_conexxao(conn, cursor):

    if cursor:
        cursor.close()

    if conn:
        conn.close()


# # Criação de busca por servidor

# ## def buscar_servidor

# In[42]:


def buscar_servidor(valor_busca):

    conn = None
    cursor = None

    try:

        conn, cursor = conexao_db()

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

        print(
            f"Erro ao buscar servidor: "
            f"{type(erro).__name__}: {erro}"
        )

        return []

    finally:

        fechar_conexxao(
            conn=conn,
            cursor=cursor
        )

