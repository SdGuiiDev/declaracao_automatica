#!/usr/bin/env python
# coding: utf-8

# # Bibliotecas

# In[54]:


import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_values
import tomllib
from pathlib import Path
from datetime import date, datetime
import pandas as pd
import traceback
import unicodedata

# # Raiz do projeto

# In[55]:


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

# In[56]:


def conexao_db():

    conn = None
    cursor = None

    try:

        with open(
            CAMINHO_CONFIG,
            "rb"
        ) as arquivo:

            config = tomllib.load(arquivo)

            db = config["rhweb"]

        conn = psycopg2.connect(
            host = db["host"],
            port = db["port"],
            dbname = db["dbname"],
            user = db["user"],
            password = db["password"]
        )

        cursor = conn.cursor()

        return conn, cursor

    except Exception as erro:

        print(
            f"Erro ao conectar com o banco de dados: "
            f"{erro}"
        )

        return None, None


# # def tratamento_de_datas

# In[57]:


def tratar_datas(valor):

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

    if isinstance(valor, datetime):
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
            return datetime.strptime(valor, formato).date()
        except ValueError:
            continue

    return None


# # def tratar_inteiro

# In[58]:


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

# In[59]:


def tratar_valor_id(valor):
        if pd.isna(valor):
                return None

        valor = str(valor).strip()

        if valor == "":
                return None

        return valor


# # def atualizar_upsert

# In[60]:


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

        cursor.execute(query, (valor,))

        resultado = cursor.fetchone()

        if resultado:
                return resultado[0]

        return None


# # def obter_sql_dados_servidor

# In[61]:


def obter_sql_dados_servidor():

        sql_dados_servidor = """
        INSERT INTO dados_servidor (
                matricula,
                nome,
                cpf,
                rg,
                data_nascimento,
                fk_tipo_servidor,
                fk_estado_civil,
                titulo_eleitor,
                data_emissao,
                zona_eleicao,
                secao_eleicao,
                fk_orgao_emissor,
                fk_grau_ensino,
                fk_uf,
                fk_municipio,
                fk_nacionalidade,
                fk_genero,
                fk_conselho_profissional,
                codigo,
                email,
                nome_mae,
                logradouro,
                numero_casa,
                bairro,
                cidade,
                cep,
                complemento,
                telefone,
                data_emissor_rg,
                fk_nome_do_curso,
                fk_origem_servidor
        )
        VALUES %s

        ON CONFLICT (matricula)
        DO UPDATE SET
                nome = EXCLUDED.nome,
                cpf = EXCLUDED.cpf,
                rg = EXCLUDED.rg,
                data_nascimento = EXCLUDED.data_nascimento,
                fk_tipo_servidor = EXCLUDED.fk_tipo_servidor,
                fk_estado_civil = EXCLUDED.fk_estado_civil,
                titulo_eleitor = EXCLUDED.titulo_eleitor,
                data_emissao = EXCLUDED.data_emissao,
                zona_eleicao = EXCLUDED.zona_eleicao,
                secao_eleicao = EXCLUDED.secao_eleicao,
                fk_orgao_emissor = EXCLUDED.fk_orgao_emissor,
                fk_grau_ensino = EXCLUDED.fk_grau_ensino,
                fk_uf = EXCLUDED.fk_uf,
                fk_municipio = EXCLUDED.fk_municipio,
                fk_nacionalidade = EXCLUDED.fk_nacionalidade,
                fk_genero = EXCLUDED.fk_genero,
                fk_conselho_profissional = EXCLUDED.fk_conselho_profissional,
                codigo = EXCLUDED.codigo,
                email = EXCLUDED.email,
                nome_mae = EXCLUDED.nome_mae,
                logradouro = EXCLUDED.logradouro,
                numero_casa = EXCLUDED.numero_casa,
                bairro = EXCLUDED.bairro,
                cidade = EXCLUDED.cidade,
                cep = EXCLUDED.cep,
                complemento = EXCLUDED.complemento,
                telefone = EXCLUDED.telefone,
                data_emissor_rg = EXCLUDED.data_emissor_rg,
                fk_nome_do_curso = EXCLUDED.fk_nome_do_curso,
                fk_origem_servidor = EXCLUDED.fk_origem_servidor

        RETURNING id;
        """

        return sql_dados_servidor


# # def obter_sql_cargo_funcionario

# In[62]:


def obter_sql_cargo_funcionario():

        sql_cargo_funcionario = """
        INSERT INTO cargo_do_funcionario (
                data_admissao,
                data_prevista_saida,
                data_saida,
                carga_horaria_semanal,
                serie_escolaridade,
                fase_faculdade,
                fk_cargo,
                fk_curso_funcionario,
                fk_especialidade,
                fk_estabelecimento_ensino,
                fk_funcao_servidor,
                fk_origem_contrato,
                fk_situacao_contrato,
                fk_dados_servidor
        )
        VALUES %s

        ON CONFLICT (fk_dados_servidor)
        DO UPDATE SET
                data_admissao = EXCLUDED.data_admissao,
                data_prevista_saida = EXCLUDED.data_prevista_saida,
                data_saida = EXCLUDED.data_saida,
                carga_horaria_semanal = EXCLUDED.carga_horaria_semanal,
                serie_escolaridade = EXCLUDED.serie_escolaridade,
                fase_faculdade = EXCLUDED.fase_faculdade,
                fk_cargo = EXCLUDED.fk_cargo,
                fk_curso_funcionario = EXCLUDED.fk_curso_funcionario,
                fk_especialidade = EXCLUDED.fk_especialidade,
                fk_estabelecimento_ensino = EXCLUDED.fk_estabelecimento_ensino,
                fk_funcao_servidor = EXCLUDED.fk_funcao_servidor,
                fk_origem_contrato = EXCLUDED.fk_origem_contrato,
                fk_situacao_contrato = EXCLUDED.fk_situacao_contrato;
        """

        return sql_cargo_funcionario


# # obter_sql_historico

# In[63]:


def obter_sql_historico():

        sql_historico = """
        INSERT INTO historico_de_lotacao (
                fk_dados_servidor,
                fk_historico,
                data_entrada,
                data_saida_historico
        )
        VALUES %s

        ON CONFLICT (
                fk_dados_servidor,
                fk_historico,
                data_entrada
        )
        DO UPDATE SET
                data_saida_historico =
                EXCLUDED.data_saida_historico;
        """

        return sql_historico


# # obter_sqls

# In[64]:


def obter_sqls():
        sql_dados_servidor = obter_sql_dados_servidor()

        sql_cargo_funcionario = obter_sql_cargo_funcionario()

        sql_historico = obter_sql_historico()

        return sql_dados_servidor, sql_cargo_funcionario, sql_historico


# # def obter_ids_servidor

# In[65]:


def obter_ids_servidor(linha, conn, cursor):
        # Vai chamar cada função para inserir ou atualizar o dado e retornar seu id
        id_tipo_servidor = atualizar_upsert(
                tabela="pk_tipo_de_servidor",
                coluna="tipo_servidor",
                valor=linha["tipo_servidor"],
                conn=conn,
                cursor=cursor
        )

        id_estado_civil = atualizar_upsert(
                tabela="pk_estado_civil_funcionario",
                coluna="estado_civil",
                valor=linha["estado_civil"],
                conn=conn,
                cursor=cursor
        )

        id_orgao_emissor = atualizar_upsert(
                tabela="pk_orgao_emissor",
                coluna="orgao_emissor",
                valor=linha["orgao_emissor"],
                conn=conn,
                cursor=cursor
        )

        id_grau_ensino = atualizar_upsert(
                tabela="pk_grau_de_ensino",
                coluna="grau",
                valor=linha["grau"],
                conn=conn,
                cursor=cursor
        )

        id_uf = atualizar_upsert(
                tabela="pk_uf",
                coluna="uf",
                valor=linha["uf"],
                conn=conn,
                cursor=cursor
        )

        id_municipio = atualizar_upsert(
                tabela="pk_municipio",
                coluna="municipio",
                valor=linha["municipio"],
                conn=conn,
                cursor=cursor
        )

        id_nacionalidade = atualizar_upsert(
                tabela="pk_nacionalidade",
                coluna="nacionalidade",
                valor=linha["nacionalidade"],
                conn=conn,
                cursor=cursor
        )

        id_genero = atualizar_upsert(
                tabela="pk_genero_funcionario",
                coluna="sexo",
                valor=linha["sexo"],
                conn=conn,
                cursor=cursor
        )

        id_conselho_profissional = atualizar_upsert(
                tabela="pk_conselho_profissional",
                coluna="conselho_profissional",
                valor=linha["conselho_profissional"],
                conn=conn,
                cursor=cursor
        )

        id_nome_curso = atualizar_upsert(
                tabela="pk_nome_curso",
                coluna="nome_do_curso",
                valor=linha["nome_do_curso"],
                conn=conn,
                cursor=cursor
        )

        id_origem_servidor = atualizar_upsert(
                tabela="pk_origem_servidor",
                coluna="origem",
                valor=linha["origem"],
                conn=conn,
                cursor=cursor
        )

        return {
                "id_tipo_servidor": id_tipo_servidor,
                "id_estado_civil": id_estado_civil,
                "id_orgao_emissor": id_orgao_emissor,
                "id_grau_ensino": id_grau_ensino,
                "id_uf": id_uf,
                "id_municipio": id_municipio,
                "id_nacionalidade": id_nacionalidade,
                "id_genero": id_genero,
                "id_conselho_profissional": id_conselho_profissional,
                "id_nome_curso": id_nome_curso,
                "id_origem_servidor": id_origem_servidor
        }


# # def obter_ids_cargo_funcionario

# 

# In[66]:


def obter_ids_cargo_funcionario(
        linha,
        conn,
        cursor
):

        id_cargo = atualizar_upsert(
                tabela="pk_cargo",
                coluna="cargo",
                valor=linha["cargo"],
                conn=conn,
                cursor=cursor
        )

        id_curso_do_funcionario = atualizar_upsert(
                tabela="pk_curso_do_funcionario",
                coluna="curso",
                valor=linha["curso"],
                conn=conn,
                cursor=cursor
        )

        id_especialidade = atualizar_upsert(
                tabela="pk_especialidade",
                coluna="especialidade",
                valor=linha["especialidade"],
                conn=conn,
                cursor=cursor
        )

        id_estabelecimento_de_ensino = atualizar_upsert(
                tabela="pk_estabelecimento_de_ensino",
                coluna="estab_ensino",
                valor=linha["estab_ensino"],
                conn=conn,
                cursor=cursor
        )

        id_funcao_servidor = atualizar_upsert(
                tabela="pk_funcao_do_servidor",
                coluna="funcao",
                valor=linha["funcao"],
                conn=conn,
                cursor=cursor
        )

        id_origem_contrato = atualizar_upsert(
                tabela="pk_origem_do_contrato",
                coluna="origem_contrato",
                valor=linha["origem_contrato"],
                conn=conn,
                cursor=cursor
        )

        id_situacao_contrato = atualizar_upsert(
                tabela="pk_situacao_do_contrato",
                coluna="situacao",
                valor=linha["situacao"],
                conn=conn,
                cursor=cursor
        )

        return {
                "id_cargo": id_cargo,
                "id_curso_do_funcionario": id_curso_do_funcionario,
                "id_especialidade": id_especialidade,
                "id_estabelecimento_de_ensino": id_estabelecimento_de_ensino,
                "id_funcao_servidor": id_funcao_servidor,
                "id_origem_contrato": id_origem_contrato,
                "id_situacao_contrato": id_situacao_contrato
}


# # def obter_id_historico

# In[67]:


def obter_id_historico(linha, conn, cursor):

        id_historico = atualizar_upsert(
        tabela="pk_historico",
        coluna="historico",
        valor=linha["historico"],
        conn=conn,
        cursor=cursor
        )

        return {
        "id_historico": id_historico
        }


# # def mostrar_ids

# In[68]:


def mostrar_ids(
        id_tipo_servidor,
        id_estado_civil,
        id_orgao_emissor,
        id_grau_ensino,
        id_uf,
        id_municipio,
        id_nacionalidade,
        id_genero,
        id_conselho_profissional,
        id_nome_curso,
        id_origem_servidor,
        id_cargo,
        id_curso_do_funcionario,
        id_especialidade,
        id_estabelecimento_de_ensino,
        id_funcao_servidor,
        id_origem_contrato,
        id_situacao_contrato,
        id_historico
):
        #Mostra no terminal o id do servidor retornado por cada função
        print("Tipo de servidor:", id_tipo_servidor)
        print("Estado Civil:", id_estado_civil)
        print("Orgão Emissor:", id_orgao_emissor)
        print("Grau de Ensino:", id_grau_ensino)
        print("uf:", id_uf)
        print("Municipio:", id_municipio)
        print("Nacionalidade:", id_nacionalidade)
        print("Gênero:", id_genero)
        print("Conselho Profissional:", id_conselho_profissional)
        print("Nome do curso:", id_nome_curso)
        print("País de Origem do servidor:", id_origem_servidor)

        print("Cargo do funcionario:", id_cargo)
        print("Curso do funcionario", id_curso_do_funcionario)
        print("Especialidade", id_especialidade)
        print("Estabelecimento de ensino", id_estabelecimento_de_ensino)
        print("Função do servidor", id_funcao_servidor)
        print("Origem do contrato:", id_origem_contrato)
        print("Situação do contrato: ", id_situacao_contrato)

        print("Historico de lotação:", id_historico)


# # def montar_dados_servidor

# In[69]:


def montar_dados_servidor(
        index,
        linha,
        ids,
        dados_servidor
):
        dados_servidor.append((
                linha["matricula"],
                linha["nome"],
                linha["cpf"],
                linha["rg"],
                tratar_datas(linha["data_nascimento"]),
                tratar_inteiro(ids["id_tipo_servidor"]),
                tratar_inteiro(ids["id_estado_civil"]),
                linha["titulo_eleitor"],
                tratar_datas(linha["data_emissao"]),
                linha["zona_eleicao"],
                linha["secao_eleicao"],
                tratar_inteiro(ids["id_orgao_emissor"]),
                tratar_inteiro(ids["id_grau_ensino"]),
                tratar_inteiro(ids["id_uf"]),
                tratar_inteiro(ids["id_municipio"]),
                tratar_inteiro(ids["id_nacionalidade"]),
                tratar_inteiro(ids["id_genero"]),
                tratar_inteiro(ids["id_conselho_profissional"]),
                linha["codigo"],
                linha["email"],
                linha["nome_mae"],
                linha["logradouro"],
                linha["numero_casa"],
                linha["bairro"],
                linha["cidade"],
                linha["cep"],
                linha["complemento"],
                linha["telefone"],
                tratar_datas(linha["data_emissor_rg"]),
                tratar_inteiro(ids["id_nome_curso"]),
                tratar_inteiro(ids["id_origem_servidor"])
        ))

        print(
                f"Dados do servidor montados na linha {index}"
        )

        return dados_servidor


# # def montar_dados_cargo_servidor

# In[70]:


def montar_dados_cargo_funcionario(
        index,
        linha,
        ids,
        id_dados_servidor,
        dados_cargo_funcionario
):
        dados_cargo_funcionario.append((
                tratar_datas(linha["data_admissao"]),
                tratar_datas(linha["data_prevista_saida"]),
                tratar_datas(linha["data_saida"]),
                linha["carga_horaria_semanal"],
                linha["serie_escolaridade"],
                linha["fase_faculdade"],
                tratar_inteiro(ids["id_cargo"]),
                tratar_inteiro(ids["id_curso_do_funcionario"]),
                tratar_inteiro(ids["id_especialidade"]),
                tratar_inteiro(ids["id_estabelecimento_de_ensino"]),
                tratar_inteiro(ids["id_funcao_servidor"]),
                tratar_inteiro(ids["id_origem_contrato"]),
                tratar_inteiro(ids["id_situacao_contrato"]),
                id_dados_servidor
        ))

        print(f"Dados do cargo montados na linha {index}")

        return dados_cargo_funcionario


# # def montar_dados_historico

# In[71]:


def montar_dados_historico(
        index,
        linha,
        ids,
        id_dados_servidor,
        dados_historico
):
        dados_historico.append((
                id_dados_servidor,
                tratar_inteiro(ids["id_historico"]),
                tratar_datas(linha["data_entrada"]),
                tratar_datas(linha["data_saida_historico"])
        ))

        print(f"Dados do histórico montados na linha {index}")

        return dados_historico


# # def montar_dados_linha

# In[72]:


def montar_dados_linha(
        index,
        linha_servidor,
        linha_cargo,
        linha_historico,
        conn,
        cursor,
        id_dados_servidor,
        dados_servidor,
        dados_cargo_funcionario,
        dados_historico
):
        ids_servidor = obter_ids_servidor(
                linha=linha_servidor,
                conn=conn,
                cursor=cursor
        )

        ids_cargo = obter_ids_cargo_funcionario(
                linha=linha_cargo,
                conn=conn,
                cursor=cursor
        )

        ids_historico = obter_id_historico(
                linha=linha_historico,
                conn=conn,
                cursor=cursor
        )

        mostrar_ids(
                id_tipo_servidor=ids_servidor["id_tipo_servidor"],
                id_estado_civil=ids_servidor["id_estado_civil"],
                id_orgao_emissor=ids_servidor["id_orgao_emissor"],
                id_grau_ensino=ids_servidor["id_grau_ensino"],
                id_uf=ids_servidor["id_uf"],
                id_municipio=ids_servidor["id_municipio"],
                id_nacionalidade=ids_servidor["id_nacionalidade"],
                id_genero=ids_servidor["id_genero"],
                id_conselho_profissional=ids_servidor["id_conselho_profissional"],
                id_nome_curso=ids_servidor["id_nome_curso"],
                id_origem_servidor=ids_servidor["id_origem_servidor"],
                id_cargo=ids_cargo["id_cargo"],
                id_curso_do_funcionario=ids_cargo["id_curso_do_funcionario"],
                id_especialidade=ids_cargo["id_especialidade"],
                id_estabelecimento_de_ensino=ids_cargo["id_estabelecimento_de_ensino"],
                id_funcao_servidor=ids_cargo["id_funcao_servidor"],
                id_origem_contrato=ids_cargo["id_origem_contrato"],
                id_situacao_contrato=ids_cargo["id_situacao_contrato"],
                id_historico=ids_historico["id_historico"]
        )

        montar_dados_servidor(
                index=index,
                linha=linha_servidor,
                ids=ids_servidor,
                dados_servidor=dados_servidor
        )

        montar_dados_cargo_funcionario(
                index=index,
                linha=linha_cargo,
                ids=ids_cargo,
                id_dados_servidor=id_dados_servidor,
                dados_cargo_funcionario=dados_cargo_funcionario
        )

        montar_dados_historico(
                index=index,
                linha=linha_historico,
                ids=ids_historico,
                id_dados_servidor=id_dados_servidor,
                dados_historico=dados_historico
        )


# # def verificar_listas_vazias

# In[73]:


def verificar_listas_vazias(dados_servidor, dados_cargo_funcionario, dados_historico):
        # Verifica se todas as listas de dados ficaram vazias após percorrer o DataFrame
        if (
                len(dados_servidor) == 0 and
                len(dados_cargo_funcionario) == 0 and
                len(dados_historico) == 0
        ):
                print("Nenhum funcionário encontrado para inserir")
                return True

        return False


# # def executar_query

# In[74]:


def executar_query(
        cursor,
        conn,
        sql_dados_servidor,
        sql_cargo_funcionario,
        sql_historico,
        dados_servidor,
        dados_cargo_funcionario,
        dados_historico
):
        if len(dados_servidor) > 0:
                execute_values(
                        cursor,
                        sql_dados_servidor,
                        dados_servidor
                )

        if len(dados_cargo_funcionario) > 0:
                execute_values(
                        cursor,
                        sql_cargo_funcionario,
                        dados_cargo_funcionario
                )

        if len(dados_historico) > 0:
                execute_values(
                        cursor,
                        sql_historico,
                        dados_historico
                )

        conn.commit()

        print(
                f"{len(dados_servidor)} registro(s) de servidor processado(s) "
                f"no banco com sucesso."
        )

        print(
                f"{len(dados_cargo_funcionario)} registro(s) de cargo processado(s) "
                f"no banco com sucesso."
        )

        print(
                f"{len(dados_historico)} registro(s) de histórico processado(s) "
                f"no banco com sucesso."
        )


# # def fechar_conexao

# In[75]:


def fechar_conexao(conn, cursor):
# Verifica se o cursor foi criado antes de tentar fechá-lo.
        if cursor:
                # Fecha o cursor usado na operação.
                cursor.close()

        # Verifica se a conexão foi criada antes de tentar fechá-la.
        if conn:
                # Fecha a conexão com o banco.
                conn.close()


# # def remover_duplicados_lista

# In[76]:


def remover_duplicados_lista(lista_dados, indices_chave):
        dados_unicos = {}

        for dados in lista_dados:
                chave = tuple(
                        dados[indice]
                        for indice in indices_chave
                )

                dados_unicos[chave] = dados

        return list(dados_unicos.values())


# # def inserir_dados

# In[77]:


def inserir_dados(
        df_dados_servidor,
        df_cargos,
        df_historico
):

        conn = None
        cursor = None

        try:

                conn, cursor = conexao_db()

                if conn is None or cursor is None:
                        return False

                (
                        sql_dados_servidor,
                        sql_cargo_funcionario,
                        sql_historico
                ) = obter_sqls()

                total_servidores = 0
                total_cargos = 0
                total_historicos = 0

                # Remove servidores repetidos.
                df_dados_servidor = (
                        df_dados_servidor
                        .drop_duplicates(
                                subset=["matricula"],
                                keep="last"
                        )
                        .copy()
                )

                # Mantém apenas um cargo para cada matrícula.
                df_cargos = (
                        df_cargos
                        .drop_duplicates(
                                subset=["matricula"],
                                keep="last"
                        )
                        .copy()
                )

                # Remove históricos repetidos.
                df_historico = (
                        df_historico
                        .drop_duplicates(
                                subset=[
                                        "matricula",
                                        "historico",
                                        "data_entrada"
                                ],
                                keep="last"
                        )
                        .copy()
                )

                for index, linha_servidor in (
                        df_dados_servidor.iterrows()
                ):

                        dados_servidor = []
                        dados_cargo_funcionario = []
                        dados_historico = []

                        ids_servidor = obter_ids_servidor(
                                linha=linha_servidor,
                                conn=conn,
                                cursor=cursor
                        )

                        montar_dados_servidor(
                                index=index,
                                linha=linha_servidor,
                                ids=ids_servidor,
                                dados_servidor=dados_servidor
                        )

                        ids_dados_servidor = execute_values(
                                cursor,
                                sql_dados_servidor,
                                dados_servidor,
                                fetch=True
                        )

                        if not ids_dados_servidor:

                                raise Exception(
                                        "Não foi possível obter o ID "
                                        f"do servidor na linha {index}."
                                )

                        id_dados_servidor = (
                                ids_dados_servidor[0][0]
                        )

                        total_servidores += 1

                        matricula = str(
                                linha_servidor["matricula"]
                        ).strip()

                        cargos_servidor = df_cargos[
                                df_cargos["matricula"]
                                .astype(str)
                                .str.strip()
                                ==
                                matricula
                        ]

                        for index_cargo, linha_cargo in (
                                cargos_servidor.iterrows()
                        ):

                                ids_cargo = (
                                        obter_ids_cargo_funcionario(
                                                linha=linha_cargo,
                                                conn=conn,
                                                cursor=cursor
                                        )
                                )

                                montar_dados_cargo_funcionario(
                                        index=index_cargo,
                                        linha=linha_cargo,
                                        ids=ids_cargo,
                                        id_dados_servidor=(
                                                id_dados_servidor
                                        ),
                                        dados_cargo_funcionario=(
                                                dados_cargo_funcionario
                                        )
                                )

                        if dados_cargo_funcionario:

                                execute_values(
                                        cursor,
                                        sql_cargo_funcionario,
                                        dados_cargo_funcionario
                                )

                                total_cargos += len(
                                        dados_cargo_funcionario
                                )

                        historicos_servidor = df_historico[
                                df_historico["matricula"]
                                .astype(str)
                                .str.strip()
                                ==
                                matricula
                        ]

                        for index_historico, linha_historico in (
                                historicos_servidor.iterrows()
                        ):

                                ids_historico = obter_id_historico(
                                        linha=linha_historico,
                                        conn=conn,
                                        cursor=cursor
                                )

                                montar_dados_historico(
                                        index=index_historico,
                                        linha=linha_historico,
                                        ids=ids_historico,
                                        id_dados_servidor=(
                                                id_dados_servidor
                                        ),
                                        dados_historico=dados_historico
                                )

                        if dados_historico:

                                execute_values(
                                        cursor,
                                        sql_historico,
                                        dados_historico
                                )

                                total_historicos += len(
                                        dados_historico
                                )

                if total_servidores == 0:

                        print(
                                "Nenhum funcionário encontrado "
                                "para inserir."
                        )

                        return False

                conn.commit()

                print(
                        f"{total_servidores} registro(s) de servidor "
                        "processado(s) no banco com sucesso."
                )

                print(
                        f"{total_cargos} registro(s) de cargo "
                        "processado(s) no banco com sucesso."
                )

                print(
                        f"{total_historicos} registro(s) de histórico "
                        "processado(s) no banco com sucesso."
                )

                return True

        except Exception as erro:

                if conn is not None:
                        conn.rollback()

                print(
                        "Erro ao inserir dados no banco: "
                        f"{type(erro).__name__}: {erro}"
                )

                traceback.print_exc()

                return False

        finally:

                fechar_conexao(
                        conn,
                        cursor
                )










#Remove acentos para quando fizer a busca nos sistemas
def remover_acentos(texto):

    # Converte o valor para texto
    texto = str(texto)

    # Remove os acentos do texto
    texto = unicodedata.normalize(
        "NFKD",
        texto
    )

    texto = "".join(
        caractere
        for caractere in texto
        if not unicodedata.combining(caractere)
    )

    return texto













# # Criação de busca por servidor

# ## def buscar_Servidor

# In[78]:


def buscar_servidor(valor_busca):

    # Inicializa as variáveis de conexão
    conn = None
    cursor = None

    try:

        # ----------------------------------------------------------- #
        # ABRE A CONEXÃO COM O BANCO
        # ----------------------------------------------------------- #

        conn, cursor = conexao_db()

        # Converte o valor pesquisado para texto
        # e remove espaços no início e no final
        valor_busca = str(
            valor_busca
        ).strip()

        # ----------------------------------------------------------- #
        # PESQUISA POR MATRÍCULA
        # ----------------------------------------------------------- #

        if valor_busca.isdigit():

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
                TRIM(ds.matricula::text) = %s

            ORDER BY
                ds.nome,
                ds.matricula
            """

            parametros = (
                valor_busca,
            )

        # ----------------------------------------------------------- #
        # PESQUISA POR NOME
        # ----------------------------------------------------------- #

        else:

            # Divide o nome pesquisado em partes
            termos = valor_busca.split()

            # Lista que receberá as condições SQL
            condicoes = []

            # Lista que receberá os parâmetros
            parametros = []

            # Percorre cada parte digitada pelo usuário
            for termo in termos:

                # Remove os acentos do termo pesquisado
                termo_normalizado = remover_acentos(
                    termo
                ).lower()

                # Remove acentos maiúsculos e minúsculos
                # existentes no nome salvo no banco
                condicoes.append(
                    """
                    LOWER(
                        TRANSLATE(
                            ds.nome,
                            'ÁÀÂÃÄÉÈÊËÍÌÎÏÓÒÔÕÖÚÙÛÜÇáàâãäéèêëíìîïóòôõöúùûüç',
                            'AAAAAEEEEIIIIOOOOOUUUUCaaaaaeeeeiiiiooooouuuuc'
                        )
                    ) LIKE %s
                    """
                )

                # Adiciona o termo normalizado
                # aos parâmetros da consulta
                parametros.append(
                    f"%{termo_normalizado}%"
                )

            # Junta todas as partes utilizando AND
            condicao_nome = " AND ".join(
                condicoes
            )

            # Monta a consulta SQL
            sql = f"""
            SELECT
                ds.matricula,
                ds.nome,
                ds.cpf,
                cf.data_admissao

            FROM dados_servidor AS ds

            LEFT JOIN cargo_do_funcionario AS cf
                ON cf.fk_dados_servidor = ds.id

            WHERE
                {condicao_nome}

            ORDER BY
                ds.nome,
                ds.matricula
            """

            # Converte os parâmetros para tupla
            parametros = tuple(
                parametros
            )

        # ----------------------------------------------------------- #
        # EXECUTA A CONSULTA
        # ----------------------------------------------------------- #

        cursor.execute(
            sql,
            parametros
        )

        # Busca todos os registros encontrados
        resultados = cursor.fetchall()

        # Retorna os resultados
        return resultados

    except Exception as erro:

        print(
            f"Erro ao buscar servidor:\n"
            f"{type(erro).__name__}: {erro}"
        )

        return []

    finally:

        # ----------------------------------------------------------- #
        # FECHA A CONEXÃO
        # ----------------------------------------------------------- #

        if cursor is not None:
            cursor.close()

        if conn is not None:
            conn.close()

