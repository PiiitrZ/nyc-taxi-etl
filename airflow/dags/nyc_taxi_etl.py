from datetime import datetime
from zoneinfo import ZoneInfo

from docker.types import Mount
from airflow.sdk import DAG, Param, task
from airflow.providers.docker.operators.docker import DockerOperator

def get_docker_operator(_task_id, _command):
    return \
        DockerOperator(
            task_id=_task_id,
            image="nyc-taxi-etl:latest",
            command=_command,
            docker_url="unix://var/run/docker.sock",
            auto_remove="success",
            mount_tmp_dir=False,
            mounts=[
                Mount(
                    source="/Users/petr.zoldos/Code/nyc-taxi-etl/data",
                    target="/app/data",
                    type="bind",
                ),
            ],
        )

default_args = {
    'owner': 'petr.zoldos',
    'depends_on_past': False
}

with (DAG(
    dag_id='NYC-TAXI-ETL-PIPELINE',
    description='NYC taxi dataset processing',
    schedule='0 1 1 * *',         # Every first day of month at 01:00 AM
    start_date=datetime(year=2026, month=8, day=1, tzinfo=ZoneInfo("Europe/Prague")),
    tags=['nyc', 'taxi'],
    catchup=False,
    default_args=default_args,
    params={
        "date_dashed": Param(default='2026-09-01', type="string", format="full-date",
                             description="Processing date"),
        "month_to_process": Param(default='9', type="string",
                                  description="Month to process"),
        "year_to_process": Param(default='2026', type="string",
                                 description="Year to process"),
    },
) as dag):
    date_dashed = '{{ params.date_dashed }}'
    month_to_process = '{{ params.month_to_process }}'
    year_to_process = '{{ params.year_to_process }}'

    @task(task_id="print-context-info")
    def print_context(input_args, **ctx):
        print(f"Input parameters: {input_args}")
        print(f"Context: {ctx}")
        return input_args

    dq_taxi_green = \
        get_docker_operator(_task_id="dq-taxi-green",
                            _command=["python",
                                      "src/etl/dq/report_taxi_green.py",
                                      f"--date={date_dashed}",
                                      f"--year={year_to_process}",
                                      f"--month={month_to_process}"])

    dq_taxi_yellow = \
        get_docker_operator(_task_id="dq-taxi-yellow",
                            _command=["python",
                                      "src/etl/dq/report_taxi_yellow.py",
                                      f"--date={date_dashed}",
                                      f"--year={year_to_process}",
                                      f"--month={month_to_process}"])

    dq_rental = \
        get_docker_operator(_task_id="dq-rental",
                            _command=["python",
                                      "src/etl/dq/report_rental.py",
                                      f"--date={date_dashed}",
                                      f"--year={year_to_process}",
                                      f"--month={month_to_process}"])

    process_taxi = \
        get_docker_operator(_task_id="process-taxi",
                            _command=["python",
                                      "src/etl/processing/process_taxi.py",
                                      f"--date={date_dashed}",
                                      f"--year={year_to_process}",
                                      f"--month={month_to_process}"])

    process_rental = \
        get_docker_operator(_task_id="process-rental",
                            _command=["python",
                                      "src/etl/processing/process_rental.py",
                                      f"--date={date_dashed}",
                                      f"--year={year_to_process}",
                                      f"--month={month_to_process}"])


    aggregate_report = \
        get_docker_operator(_task_id="aggregate-report",
                            _command=["python",
                                      "src/etl/reports/report.py",
                                      f"--date={date_dashed}",
                                      f"--year={year_to_process}",
                                      f"--month={month_to_process}"])

    read_report = \
        get_docker_operator(_task_id="read-report",
                            _command=["python",
                                      "src/etl/reports/report_read.py",
                                      f"--date={date_dashed}"])


    # run_etl = DockerOperator(
    #     task_id="run-nyc-taxi-etl",
    #     image="nyc-etl:latest",
    #     command=["python", "src/report.py"],
    #     docker_url="unix://var/run/docker.sock",
    #     network_mode="bridge",
    #     auto_remove="success",
    # )

    print_ctx = print_context((date_dashed, month_to_process, year_to_process))

    print_ctx >> [dq_taxi_green, dq_taxi_yellow] >> process_taxi
    print_ctx >> dq_rental >> process_rental
    [process_taxi, process_rental] >> aggregate_report >> read_report
