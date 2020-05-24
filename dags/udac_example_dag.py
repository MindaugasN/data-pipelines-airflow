from datetime import datetime, timedelta
import os
from airflow import DAG

from airflow.operators.dummy_operator import DummyOperator
from operators.stage_redshift import StageToRedshiftOperator
from operators.load_fact import LoadFactOperator
from operators.load_dimension import LoadDimensionOperator
from operators.data_quality import DataQualityOperator

from helpers import SqlQueries


default_args = {
    'owner': 'mindaugasn',
    'start_date': datetime(2020, 5, 20),
    'depends_on_past': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'catchup': False,
    'email_on_failure': True,
    'email_on_retry': False
}

dag = DAG('udac_example_dag',
          default_args=default_args,
          description='Load and transform data in Redshift with Airflow',
          schedule_interval='0 * * * *',
        )

start_operator = DummyOperator(task_id='Begin_execution',  dag=dag)

stage_events_to_redshift = StageToRedshiftOperator(
    task_id='Stage_events',
    dag=dag,
    redshift_conn_id='redshift',
    aws_conn_id='aws_credentials',
    table_name='staging_events',
    s3_bucket='udacity-dend',
    s3_prefix='log_data',
    extra_parameters=["JSON AS 'auto'"]
)

stage_songs_to_redshift = StageToRedshiftOperator(
    task_id='Stage_songs',
    dag=dag,
    redshift_conn_id='redshift',
    aws_conn_id='aws_credentials',
    table_name='staging_songs',
    s3_bucket='udacity-dend',
    s3_prefix='song_data',
    extra_parameters=["JSON AS 'auto'"]
)

load_songplays_table = LoadFactOperator(
    task_id='Load_songplays_fact_table',
    dag=dag,
    redshift_conn_id='redshift',
    table_name='songplays',
    sql=SqlQueries.songplay_table_insert
)

load_user_dimension_table = LoadDimensionOperator(
    task_id='Load_user_dim_table',
    dag=dag,
    redshift_conn_id='redshift',
    table_name='users',
    sql=SqlQueries.user_table_insert
)

load_song_dimension_table = LoadDimensionOperator(
    task_id='Load_song_dim_table',
    dag=dag,
    redshift_conn_id='redshift',
    table_name='songs',
    sql=SqlQueries.song_table_insert
)

load_artist_dimension_table = LoadDimensionOperator(
    task_id='Load_artist_dim_table',
    dag=dag,
    redshift_conn_id='redshift',
    table_name='artists',
    sql=SqlQueries.artist_table_insert
)

load_time_dimension_table = LoadDimensionOperator(
    task_id='Load_time_dim_table',
    dag=dag,
    redshift_conn_id='redshift',
    table_name='time',
    sql=SqlQueries.time_table_insert
)

run_quality_check_songplays = DataQualityOperator(
    task_id='Run_data_quality_checks_songplays',
    dag=dag,
    redshift_conn_id='redshift',
    table_name='songplays',
    column='user_id',
    rule='is not null',
    treshold=0
)

run_quality_check_users = DataQualityOperator(
    task_id='Run_data_quality_checks_users',
    dag=dag,
    redshift_conn_id='redshift',
    table_name='users',
    column='first_name',
    rule='is not null',
    treshold=5
)

end_operator = DummyOperator(task_id='Stop_execution',  dag=dag)

start_operator >> [stage_songs_to_redshift, stage_events_to_redshift] >> load_songplays_table
load_songplays_table >> [load_song_dimension_table, load_user_dimension_table, load_artist_dimension_table, load_time_dimension_table] >> [run_quality_check_songplays, run_quality_check_users]
[run_quality_check_songplays, run_quality_check_users] >> end_operator