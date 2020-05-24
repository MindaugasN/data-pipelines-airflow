from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class LoadDimensionOperator(BaseOperator):

    ui_color = '#80BD9E'

    @apply_defaults
    def __init__(self, table_name, redshift_conn_id, sql, truncate=True, *args, **kwargs):
        super(LoadDimensionOperator, self).__init__(*args, **kwargs)
        self.table_name = table_name
        self.redshift_conn_id = redshift_conn_id
        self.sql = sql
        self.truncate = truncate

    def execute(self, context):
        pg_hook = PostgresHook(postgres_conn_id=self.redshift_conn_id)

        if self.truncate:
            pg_hook.run(f'truncate table {self.table_name};')
        self.log.info(f"Truncate {self.table_name} finished.")

        insert_sql = f"insert into {self.table_name} ({self.sql})"
        pg_hook.run(insert_sql)

        self.log.info(f"Insert into {self.table_name} finished.")

