from sqlalchemy import create_engine, text
from ..crypto_utils import decrypt_password


def get_engine(datasource):
    password = decrypt_password(datasource.db_password)
    if datasource.db_type == 'mysql':
        url = f'mysql+pymysql://{datasource.db_username}:{password}@{datasource.host}:{datasource.port}/{datasource.database_name}'
    else:
        url = f'postgresql://{datasource.db_username}:{password}@{datasource.host}:{datasource.port}/{datasource.database_name}'
    return create_engine(url)


def fetch_records(datasource, filters=None):
    engine = get_engine(datasource)
    with engine.connect() as conn:
        query = f"SELECT * FROM {datasource.table_name}"
        params = {}
        if filters:
            conditions = []
            if filters.get('keyword'):
                conditions.append(f"`产品名` LIKE :keyword")
                params['keyword'] = f"%{filters['keyword']}%"
            if filters.get('power'):
                conditions.append(f"`功率(KVA/KW)` = :power")
                params['power'] = filters['power']
            if filters.get('engine_model'):
                conditions.append(f"`柴油发动机型号` = :engine_model")
                params['engine_model'] = filters['engine_model']
            if filters.get('generator_model'):
                conditions.append(f"`发电机型号` = :generator_model")
                params['generator_model'] = filters['generator_model']
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
        result = conn.execute(text(query), params)
        columns = result.keys()
        return [dict(zip(columns, row)) for row in result.fetchall()]


def test_connection(datasource):
    try:
        engine = get_engine(datasource)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True, "连接成功"
    except Exception as e:
        return False, str(e)
