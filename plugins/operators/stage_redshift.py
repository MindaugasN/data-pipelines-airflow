from airflow.hooks.postgres_hook import PostgresHook
from airflow.hooks.S3_hook import S3Hook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class StageToRedshiftOperator(BaseOperator):
    ui_color = '#358140'

    @apply_defaults
    def __init__(self, table_name, s3_bucket, s3_prefix, redshift_conn_id, aws_conn_id, extra_parameters=None, *args, **kwargs):
        super(StageToRedshiftOperator, self).__init__(*args, **kwargs)
        self.table_name = table_name
        self.s3_bucket = s3_bucket
        self.s3_prefix = s3_prefix
        self.redshift_conn_id = redshift_conn_id
        self.aws_conn_id = aws_conn_id
        self.extra_parameters = extra_parameters or []

    def execute(self, context):
        pg_hook = PostgresHook(postgres_conn_id=self.redshift_conn_id)
        s3_hook = S3Hook(aws_conn_id=self.aws_conn_id)
        credentials = s3_hook.get_credentials()
        extra_parameters_text = ' '.join(self.extra_parameters)

        copy_sql = """
            COPY {table}
            FROM 's3://{bucket}/{prefix}'
            CREDENTIALS 'aws_access_key_id={access_key};aws_secret_access_key={secret_key}'
            {extra_parameters_text}
        """.format(
            table=self.table_name, bucket = self.s3_bucket, prefix = self.s3_prefix,
            access_key=credentials.access_key, secret_key=credentials.secret_key,
            extra_parameters_text=extra_parameters_text
        )

        pg_hook.run(copy_sql)
        self.log.info(f"COPY {self.table_name} into Redshift finished.")
