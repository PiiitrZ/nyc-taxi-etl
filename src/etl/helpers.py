import argparse
import polars as pl
from datetime import date, datetime

from src.etl import INPUT_DATA_PATH, LOOKUP_FILE_NAME, OUTPUT_DATA_PATH, DATA_RECORDS_LIMIT


def get_arg_parser():
    def parse_date(value):
        for fmt in ("%Y%m%d", "%Y-%m-%d"):
            try:
                return datetime.strptime(value, fmt).date()
            except ValueError:
                pass

        raise argparse.ArgumentTypeError(
            "date must be YYYYMMDD or YYYY-MM-DD"
        )

    def parse_month(value):
        month = int(value)
        if not 1 <= month <= 12:
            raise argparse.ArgumentTypeError("month must be between 1 and 12")
        return month

    def parse_year(value):
        year = int(value)
        if not 1000 <= year <= 9999:
            raise argparse.ArgumentTypeError("year must be a 4-digit integer")
        return year

    arg_def = {
        "date": {"help": "processing date -> yyyymmdd",
                 "type": parse_date},
        "year": {"help": "reporting year: 4 digit integer",
                 "type": parse_year, "required": False},
        "month": {"help": "reporting month: 1 to 12",
                  "type": parse_month, "required": False},
    }

    parser = argparse.ArgumentParser()

    for name, definition in arg_def.items():
        parser.add_argument(f"--{name}", **definition)

    return parser


class TripDataType(object):
    fhv: str = 'fhv_tripdata'
    fhvhv: str = 'fhvhv_tripdata'
    green: str = 'green_tripdata'
    yellow: str = 'yellow_tripdata'

class TransformedDataType(object):
    taxi: str = 'taxi'
    rental: str = 'rental'


class Reader:
    def __init__(self, _date: date, year_month: tuple[int, int] = None):
        self.day_partition = f"day={_date.strftime("%Y%m%d")}"
        self.year_month = f"{year_month[0]}-{year_month[1]:02d}" if year_month else None
        self.ym_partition = f"month={year_month[0]}{year_month[1]:02d}" if year_month else None

    @staticmethod
    def read_full_path(path: str, f_name: str, f_type: str = 'parquet') -> pl.DataFrame:
        full_path = f'{path}/{f_name}.{f_type}'
        print(f'Reading from {full_path} limited to {DATA_RECORDS_LIMIT}')
        match f_type:
            case 'parquet':
                return pl.read_parquet(full_path).limit(DATA_RECORDS_LIMIT)
            case 'csv':
                return pl.read_csv(full_path).limit(DATA_RECORDS_LIMIT)
            case _:
                raise ValueError(f"Wrong input value for f_type: {f_type}")

    def read_lookup_data(self) -> pl.DataFrame:
        return self.read_full_path(INPUT_DATA_PATH, LOOKUP_FILE_NAME, 'csv')

    def read_trip_data_raw(self, trip_type: str = TripDataType.fhv) -> pl.DataFrame:
        path = f"{INPUT_DATA_PATH}/{self.ym_partition}"
        f_name = f"{trip_type}_{self.year_month}"

        return self.read_full_path(path, f_name)

    def read_trip_data_transformed(self, trip_type: str) -> pl.DataFrame:
        match trip_type:
            case TransformedDataType.taxi:
                path = 'transformed/trips/taxi'
            case TransformedDataType.rental:
                path = 'transformed/trips/rental'
            case _:
                raise ValueError(f"Wrong input value for trip_type: {trip_type}")

        path = f"{OUTPUT_DATA_PATH}/{path}/{self.day_partition}"
        f_name = "transformed"

        return self.read_full_path(path, f_name)


class Writer:
    def __init__(self, _date: date):
        self._date = _date
        self.day_partition = f"day={self._date.strftime("%Y%m%d")}"

    def export_parquet(self, df: pl.DataFrame, path: str, f_name: str = 'file'):
        # todo: partitioning by day/month?
        full_path = f"{OUTPUT_DATA_PATH}/{path}/{self.day_partition}/{f_name}.parquet"

        df.write_parquet(full_path)

        print(f"Results exported to {full_path}")