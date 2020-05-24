# Installing Airflow Locally

### Installation

1. Open up a terminal and create directory for airflow.
    ```bash
    cd ~
    mkdir airflow_standalone
    cd airflow_standalone
    ```

2. Install and activate virtual environment.
    ```bash
    pip install virtualenv
    python -m venv venv
    source venv/bin/activate
    ```

3. Install airflow.
    ```bash
    pip install apache-airflow
    ```

### Configuration

1. Set AIRFLOW_HOME environment variable, where Airflow will store config and log files.
    ```bash
    (venv) export AIRFLOW_HOME=~/airflow_standalone/airflow_home 
    ```

2. Create SQLite metadata database, which also create `airflow.cfg` and `unittests.cfg`.
    ```bash
    (venv) airflow initdb
    ```

### Running Airflow

1. Start Airflow webserver on port 8080 and then you can visit [localhost:8080](localhost:8080).
    ```bash
    (venv) airflow webserver --port 8080
    ```
2. Open another terminal window and start scheduler.
    ```bash
    cd ~/airflow_standalone
    source venv/bin/activate

    (venv) airflow scheduler
    ```

3. If you get `ValueError: unknown locale: UTF-8` when trying to run example dags, you need to set `LC_ALL` variable. Read more on [github](https://stackoverflow.com/questions/36394101/pip-install-locale-error-unsupported-locale-setting). 
    ```bash
    (venv) export LC_ALL=C
    ```

4. To stop all processes of webserver and scheduler, just kill them in third terminal window.
    ```bash
    kill -9 `ps aux | grep airflow | awk '{print $2}'`
    ```

# Project Introduction

A music streaming company, Sparkify, has decided that it is time to introduce more automation and monitoring to their data warehouse ETL pipelines and come to the conclusion that the best tool to achieve this is Apache Airflow. The source data resides in S3 and needs to be processed in Sparkify's data warehouse in Amazon Redshift. The source datasets consist of JSON logs that tell about user activity in the application and JSON metadata about the songs the users listen to.

## Datasets

>s3://udacity-dend/song_data
>s3://udacity-dend/log_data

#### song_data preview

The first dataset is a subset of real data from the [Million Song Dataset](http://millionsongdataset.com/). Each file is in JSON format and contains metadata about a song and the artist of that song. The files are partitioned by the first three letters of each song's track ID.

>song_data/A/A/B/TRAABJL12903CDCF1A.json

```json
{"num_songs": 1, "artist_id": "ARJIE2Y1187B994AB7", "artist_latitude": null, "artist_longitude": null, "artist_location": "", "artist_name": "Line Renaud", "song_id": "SOUPIRU12A6D4FA1E1", "title": "Der Kleine Dompfaff", "duration": 152.92036, "year": 0}
```

#### log_data preview

The second dataset consists of log files in JSON format generated by this [event simulator](https://github.com/Interana/eventsim) based on the songs in the dataset above. These simulate app activity logs from an imaginary music streaming app based on configuration settings. The log files in the dataset you'll be working with are partitioned by year and month. For example, here are filepaths to two files in this dataset.

>log_data/2018/11/2018-11-01-events.json

```json
{"artist":null,"auth":"Logged In","firstName":"Walter","gender":"M","itemInSession":0,"lastName":"Frye","length":null,"level":"free","location":"San Francisco-Oakland-Hayward, CA","method":"GET","page":"Home","registration":1540919166796.0,"sessionId":38,"song":null,"status":200,"ts":1541105830796,"userAgent":"\"Mozilla\/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit\/537.36 (KHTML, like Gecko) Chrome\/36.0.1985.143 Safari\/537.36\"","userId":"39"}
```

## Tasks

Using Apache Airflow we should build Data pipelines that are be dynamic and built from reusable tasks, can be monitored, and allow easy backfills. Data quality plays a big part when analyses are executed on top the data warehouse and tests need to be run against their datasets after the ETL steps have been executed to catch any discrepancies in the datasets.

#### DAG
* The DAG does not have dependencies on past runs;
* On failure, the task are retried 3 times;
* Retries happen every 5 minutes;
* Catchup is turned off;
* Do not email on retry.

#### Operators
1. **Stage Operator** - Load JSON files from S3 to Amazon Redshift
    * Runs a SQL COPY.
2. **Fact and Dimension Operators** - SQL helper class to run data transformations.
    * Take target database on which to run the query against
3. **Data Quality Operator** - Run checks on the data itself
    * Certain column contains NULL.

## Project structure

```
project
|-- dags
    |-- etl.py
|-- plugins
    |-- __init__.py
    |-- helpers
        |-- __init__.py
        |-- sql_queries.py
    |-- operators
        |-- __init__.py
        |-- data_quality.py
        |-- load_dimension.py
        |-- load_fact.py
        |-- stage_redshift.py
|-- create_tables.sql
|-- README.md
|-- .gitignore
```

## Requirements

1. Software:

- [Python 3.6.x](http://docs.python-guide.org/en/latest/starting/installation/)
- [pip](https://pip.pypa.io/en/stable/installing/)

2. Running installation of Airflow (follow steps at the top of README)

3. AWS account:
- [AWS credentials](https://aws.amazon.com/getting-started/)
- [Redshift cluster](https://docs.aws.amazon.com/redshift/latest/gsg/getting-started.html)

4. Python 3rd party libraries (make sure you have virtual environment activated): 

- [boto3](https://pypi.org/project/boto3/)
- [botocore](https://pypi.org/project/botocore/)
- [psycopg2](https://pypi.org/project/psycopg2/)

```bash
(venv) pip install boto3
(venv) pip install botocore
(venv) pip install psycopg2
```

## How to use this repo?

1. Clone or download it.
2. Make sure you met all the requirements listed above.
3. Create `redshift` and `aws_credentials` in Airflow [connections tab](http://localhost:8080/admin/connection/)
4. Run `create_table.sql` script and create tables. (It can be done via [query editor](https://docs.aws.amazon.com/redshift/latest/mgmt/query-editor.html))
4. Open [localhost:8080](localhost:8080) and run `main_etl` DAG.