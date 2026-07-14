# Importa a biblioteca psycopg2, usada para conectar o Python ao banco PostgreSQL.
import psycopg2
# Importa a função execute_values, usada para inserir vários registros de uma vez no PostgreSQL com mais desempenho.
from psycopg2.extras import execute_values
# Importa a biblioteca tomllib, usada para ler arquivos .toml, como o config.toml.
import tomllib
# Importa a biblioteca pandas, usada para trabalhar com DataFrames e tratar valores vazios como NaN ou NaT.
import pandas as pd
# Importa Path, usado para montar caminhos de arquivos e pastas de forma mais segura.
from pathlib import Path

#------------------------------------------------------------------------------------------------------------------#


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






# Abre a conexão com o PostgreSQL.
def conexao_db():
    base_dir = Path(__file__).resolve().parent.parent
    config_path = base_dir / "config.toml"

    # Lê as configurações do banco.
    with open(config_path, "rb") as arquivo:
        config = tomllib.load(arquivo)

    db = config["database"]

    # Cria a conexão.
    conn = psycopg2.connect(
        host=db["host"],
        port=db["port"],
        dbname=db["dbname"],
        user=db["user"],
        password=db["password"]
    )

    cursor = conn.cursor()

    return conn, cursor







# Executa um comando SQL.
def executar_sql(sql, valores=None):
    conn = None
    cursor = None

    try:
        conn, cursor = conexao_db()

        cursor.execute(sql, valores)
        conn.commit()

    except Exception as erro:
        if conn:
            conn.rollback()

        print(f"Erro ao executar SQL: {erro}")

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()








# Insere os funcionários no banco.
def inserir_funcionarios(df):
    conn = None
    cursor = None

    try:
        conn, cursor = conexao_db()

        sql = """
            INSERT INTO joaquina (
                fk_servidor,
                fk_cargos,
                fk_lotacoes,
                fk_aposentadoria,
                fk_jornada_funcional,
                regime
            )
            VALUES %s
            ON CONFLICT (
                fk_servidor,
                fk_cargos,
                fk_lotacoes,
                fk_jornada_funcional
            )
            DO UPDATE SET
                fk_aposentadoria = EXCLUDED.fk_aposentadoria,
                regime = EXCLUDED.regime;
        """

        dados = []

        # Percorre as linhas do DataFrame.
        for index, linha in df.iterrows():
            id_servidor = pk_servidor(
                linha["matricula"],
                linha["nome"]
            )

            id_cargo = pk_cargos(
                linha["cod_cargo"],
                linha["cargo"]
            )

            id_lotacao = pk_lotacoes(
                linha["cod_lotacao"],
                linha["lotacao"]
            )

            id_aposentadoria = pk_aposentadoria(
                linha["aposentado"]
            )

            id_jornada_funcional = pk_jornada_funcional(
                linha["admitido"],
                linha["entrada_lotacao"],
                linha["saida_lotacao"],
                linha["exonerado"]
            )

            # Exibe os dados processados.
            print("Servidor:", id_servidor)
            print("Cargo:", id_cargo)
            print("Lotação:", id_lotacao)
            print("Aposentadoria:", id_aposentadoria)
            print("Jornada:", id_jornada_funcional)
            print("Regime:", linha["regime"])
            print("-" * 40)

            # Valida os IDs retornados.
            if (
                id_servidor is None
                or id_cargo is None
                or id_lotacao is None
                or id_aposentadoria is None
                or id_jornada_funcional is None
            ):
                raise ValueError(
                    f"Erro na linha {index}: alguma função pk retornou None."
                )

            dados.append((
                id_servidor,
                id_cargo,
                id_lotacao,
                id_aposentadoria,
                id_jornada_funcional,
                linha["regime"]
            ))

        # Verifica se existem dados.
        if not dados:
            print("Nenhum funcionário encontrado para inserir.")
            return

        # Insere os registros em lote.
        execute_values(
            cursor,
            sql,
            dados
        )

        conn.commit()

        print(
            f"{len(dados)} registro(s) "
            "processado(s) com sucesso."
        )

    except Exception as erro:
        if conn:
            conn.rollback()

        print(f"Erro ao inserir dados no banco: {erro}")

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()









# Insere ou atualiza um servidor.
def pk_servidor(matricula, nome):
    conn = None
    cursor = None

    try:
        conn, cursor = conexao_db()

        sql = """
            INSERT INTO pk_servidor (
                matricula,
                nome
            )
            VALUES (%s, %s)
            ON CONFLICT (matricula)
            DO UPDATE SET
                nome = EXCLUDED.nome
            RETURNING id;
        """

        cursor.execute(
            sql,
            (matricula, nome)
        )

        id_servidor = cursor.fetchone()[0]

        conn.commit()

        return id_servidor

    except Exception as erro:
        if conn:
            conn.rollback()

        print(f"Erro ao inserir servidor: {erro}")

        return None

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()









# Insere ou atualiza uma lotação.
def pk_lotacoes(cod_lotacao, lotacao):
    conn = None
    cursor = None

    try:
        conn, cursor = conexao_db()

        sql = """
            INSERT INTO pk_lotacoes (
                cod_lotacao,
                lotacao
            )
            VALUES (%s, %s)
            ON CONFLICT (lotacao)
            DO UPDATE SET
                cod_lotacao = EXCLUDED.cod_lotacao,
                lotacao = EXCLUDED.lotacao
            RETURNING id;
        """

        cursor.execute(
            sql,
            (cod_lotacao, lotacao)
        )

        id_lotacao = cursor.fetchone()[0]

        conn.commit()

        return id_lotacao

    except Exception as erro:
        if conn:
            conn.rollback()

        print(f"Erro ao inserir lotação: {erro}")

        return None

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()













# Insere ou atualiza um cargo.
def pk_cargos(cod_cargo, cargo):
    conn = None
    cursor = None

    try:
        conn, cursor = conexao_db()

        sql = """
            INSERT INTO pk_cargos (
                cod_cargo,
                cargo
            )
            VALUES (%s, %s)
            ON CONFLICT (cargo)
            DO UPDATE SET
                cod_cargo = EXCLUDED.cod_cargo,
                cargo = EXCLUDED.cargo
            RETURNING id;
        """

        cursor.execute(
            sql,
            (cod_cargo, cargo)
        )

        id_cargo = cursor.fetchone()[0]

        conn.commit()

        return id_cargo

    except Exception as erro:
        if conn:
            conn.rollback()

        print(f"Erro ao inserir cargo: {erro}")

        return None

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()













# Insere ou busca uma aposentadoria.
def pk_aposentadoria(aposentado):
    conn = None
    cursor = None

    try:
        conn, cursor = conexao_db()

        # Converte valores vazios.
        if pd.isna(aposentado):
            aposentado = None

        # Busca um registro nulo.
        if aposentado is None:
            sql_select = """
                SELECT id
                FROM pk_aposentadoria
                WHERE aposentado IS NULL;
            """

            cursor.execute(sql_select)

            resultado = cursor.fetchone()

            if resultado:
                return resultado[0]

            sql_insert = """
                INSERT INTO pk_aposentadoria (
                    aposentado
                )
                VALUES (NULL)
                RETURNING id;
            """

            cursor.execute(sql_insert)

            id_aposentadoria = cursor.fetchone()[0]

            conn.commit()

            return id_aposentadoria

        # Insere uma data válida.
        sql = """
            INSERT INTO pk_aposentadoria (
                aposentado
            )
            VALUES (%s)
            ON CONFLICT (aposentado)
            DO UPDATE SET
                aposentado = EXCLUDED.aposentado
            RETURNING id;
        """

        cursor.execute(
            sql,
            (aposentado,)
        )

        id_aposentadoria = cursor.fetchone()[0]

        conn.commit()

        return id_aposentadoria

    except Exception as erro:
        if conn:
            conn.rollback()

        print(f"Erro ao inserir aposentadoria: {erro}")

        return None

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()















# Insere ou busca uma jornada.
def pk_jornada_funcional(
        admitido,
        entrada_lotacao,
        saida_lotacao,
        exonerado
):
    conn = None
    cursor = None

    try:
        conn, cursor = conexao_db()

        # Converte valores vazios.
        admitido = None if pd.isna(admitido) else admitido
        entrada_lotacao = (
            None
            if pd.isna(entrada_lotacao)
            else entrada_lotacao
        )
        saida_lotacao = (
            None
            if pd.isna(saida_lotacao)
            else saida_lotacao
        )
        exonerado = None if pd.isna(exonerado) else exonerado

        # Busca uma jornada igual.
        sql_select = """
            SELECT id
            FROM pk_jornada_funcional
            WHERE admitido IS NOT DISTINCT FROM %s
            AND entrada_lotacao IS NOT DISTINCT FROM %s
            AND saida_lotacao IS NOT DISTINCT FROM %s
            AND exonerado IS NOT DISTINCT FROM %s;
        """

        valores = (
            admitido,
            entrada_lotacao,
            saida_lotacao,
            exonerado
        )

        cursor.execute(
            sql_select,
            valores
        )

        resultado = cursor.fetchone()

        if resultado:
            return resultado[0]

        # Insere uma nova jornada.
        sql_insert = """
            INSERT INTO pk_jornada_funcional (
                admitido,
                entrada_lotacao,
                saida_lotacao,
                exonerado
            )
            VALUES (%s, %s, %s, %s)
            RETURNING id;
        """

        cursor.execute(
            sql_insert,
            valores
        )

        id_jornada_funcional = cursor.fetchone()[0]

        conn.commit()

        return id_jornada_funcional

    except Exception as erro:
        if conn:
            conn.rollback()

        print(f"Erro ao inserir jornada funcional: {erro}")

        return None

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()