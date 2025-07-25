import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from trino.dbapi import connect

from app.env_variables import TRINO_USER, TRINO_HOST, TRINO_PORT
from app.bussiness_logic.db_models import Base
import re


class SQLOperations:

    def __init__(self, catalog: str):
        self.conn = connect(
            host=TRINO_HOST,
            port=TRINO_PORT,
            user=TRINO_USER,
            catalog=catalog.lower(),
            schema='default',  # Replace with your schema
            http_scheme='http',
            verify=False
        )

        # Create the SQLAlchemy engine using the Trino connection
        self.engine = create_engine(
            'trino://',
            creator=lambda: self.conn
        )

    def execute_query(self, modelo: Base, *filters, joins=None, join_columns=None, page_size: int = 10,
                      page_number: int = 1, order_by: str = None):
        '''
        :param modelo: Es el modelo de la base de datos a las que se hara el query
        :param filters: Estos argumentos son los filtros se usan como positional arguments, ej:
                        modelo_1.columna_1 == 5, modelo_1.columna_2 > 0
        :param joins: Lista de tuplas con los joins la primera posicion de la tupla es el modelo,la segunda es la
                      condicion y la tercera es si es 'left'(outerjoin) o 'inner'(join), ej:
                      (modelo_2, modelo_1.columna_3 == modelo_2.columna_1, 'inner')
        :param page_size: Numero de resultados en la pagina
        :param page_number: Numero de pagina
        :param order_by: Campo por el cual se va a ordenar los resultados
        :return:
        '''
        query, session = self._get_query_and_session(filters, joins, modelo, order_by, page_number, page_size)

        results = query.all()

        session.close()
        return results

    def execute_query_df(self, modelo: Base, *filters, joins=None, join_columns=None, page_size: int = None,
                         page_number: int = None, order_by: str = None):
        '''
        Similar to execute_query but returns a pandas DataFrame instead of ORM objects

        :param modelo: Database model to query
        :param filters: Filter conditions as positional arguments, e.g.:
                       modelo_1.columna_1 == 5, modelo_1.columna_2 > 0
        :param joins: List of tuples with joins (model, condition, join_type), e.g.:
                     (modelo_2, modelo_1.columna_3 == modelo_2.columna_1, 'inner')
        :param page_size: Number of results per page
        :param page_number: Page number
        :param order_by: Field to order results by
        :return: pandas DataFrame with query results
        '''
        query, session = self._get_query_and_session(filters, joins, modelo, order_by, page_number, page_size,
                                                     join_columns)
        query = str(query.statement.compile(
            compile_kwargs={"literal_binds": True}))

        # Convert to pandas DataFrame
        df = pd.read_sql(query, self.conn)
        session.close()
        return df

    def _get_query_and_session(self, filters, joins, modelo, order_by, page_number, page_size, join_columns=None):
        joins = joins or []
        offset_value = (page_number - 1) * page_size if page_size and page_number else None
        session = self._create_session()

        columns = [c for c in modelo.__table__.columns if c.name != '_dummy_pk']

        if join_columns:
            columns = [*columns, *join_columns]

        query = session.query(*columns)

        for join_info in joins:
            if isinstance(join_info, tuple):
                table, condition, join_type = join_info
                if join_type == 'left':
                    query = query.outerjoin(table, condition)
                else:
                    query = query.join(table, condition)
            else:
                query = query.join(join_info)

        query = query.filter(*filters)
        if order_by:
            query = query.order_by(order_by)
        if offset_value is not None:
            query = query.offset(offset_value)
        if page_size:
            query = query.limit(page_size)

        # Convert datetime strings to TIMESTAMP format in the compiled query
        compiled_query = str(query.statement.compile(compile_kwargs={"literal_binds": True}))
        pattern = r"(>=|<=|>|<|=)\s*'(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}\.\d+)'"
        compiled_query = re.sub(pattern, r"\1 TIMESTAMP '\2'", compiled_query)

        # Use the same columns for the final query as we used for the initial query
        final_query = session.query(*columns).from_statement(text(compiled_query))

        return final_query, session

    def insert_record(self, modelo: Base):
        session = self._create_session()
        session.add(modelo)
        self._commit_close_session(session)

    def update_record(self, modelo: Base, *filters, **updated_data):
        session = self._create_session()
        session.query(modelo).filter(*filters).update(**updated_data)
        self._commit_close_session(session)

    def execute_simple_select(self, fields: str, table: str, conditions: str):
        return self.execute_query(f'SELECT {fields} FROM {table} WHERE {conditions}')

    def execute_query_no_orm(self, query, params=None):
        with self.engine.connect() as conn:
            result = conn.execute(text(query), params)
            fetched_results = result.fetchall()
            try:
                return [dict(row) for row in fetched_results]
            except Exception:
                return fetched_results

    def execute_simple_insert(self, table: str, columns: str, values: str):
        return self.execute_non_query(f'INSERT INTO {table} ({columns}) VALUES ({values})')

    def execute_non_query(self, query, params=None):
        with self.engine.connect() as conn:
            conn.execute(text(query), params)

    def _create_session(self):
        return sessionmaker(bind=self.engine)()

    @staticmethod
    def _commit_close_session(session):
        session.commit()
        session.close()