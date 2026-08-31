Running:
1.build python etl: docker build -t nyc-taxi-etl:latest .
1.build airflow: docker compose build airflow
1.get Airlflow UI credentials: docker compose logs airflow //'admin': Zwg5k652hBbXUsQY
1.run Airflow UI: docker compose up
airflow-1  | standalone | Starting Airflow Standalone
airflow-1  | Simple auth manager | Password for user 'admin': TmhM8przdKzsqwpA


Or run python independently:
docker run --rm -v "$(pwd)/data:/app/data" nyc-taxi-etl:latest python src/etl/processing/process_taxi.py --date=20260826 --year=2026 --month=1 
docker run --rm -v "$(pwd)/data:/app/data" nyc-taxi-etl:latest python src/etl/processing/process_rental.py --date=20260826 --year=2026 --month=1

docker run --rm -v "$(pwd)/data:/app/data" nyc-taxi-etl:latest python src/etl/reports/report.py --date=20260826 --year=2026 --month=1

docker run --rm -v "$(pwd)/data:/app/data" nyc-taxi-etl:latest python src/etl/reports/report_read.py --date=20260826


python -m pip install -e ".[test]"
python -m pytest


The Airflow container needs access to the Docker daemon in order to create your nyc-tax-etl container.
That's why this is here:
- /var/run/docker.sock:/var/run/docker.sock