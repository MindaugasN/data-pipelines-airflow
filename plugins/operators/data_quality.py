from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class DataQualityOperator(BaseOperator):

    ui_color = '#89DA59'

    @apply_defaults
    def __init__(self, table_name, redshift_conn_id, column, rule, treshold=0, *args, **kwargs):
        super(DataQualityOperator, self).__init__(*args, **kwargs)
        self.table_name = table_name
        self.redshift_conn_id = redshift_conn_id
        self.column = column
        self.rule = rule
        self.treshold = treshold

    def execute(self, context):
        pg_hook = PostgresHook(postgres_conn_id=self.redshift_conn_id)

        sql = f'''
            select count(*) 
            from {self.table_name}
            where {self.column} {self.rule};
            '''

        res = pg_hook.get_records(sql)

        if res[0][0] > self.treshold:
            raise ValueError(f'{self.column} in {self.table_name} does not conform {self.rule} rule.')

        self.log.info(f'SUCCESS: {self.column} in {self.table_name} conforms {self.rule} rule.')