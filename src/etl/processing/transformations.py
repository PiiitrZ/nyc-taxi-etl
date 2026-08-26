import polars as pl
from polars import DataFrame

from datetime import date

from src.etl.transformations import TransformationsEtl
from src.etl.helpers import TripDataType

class Transformations(TransformationsEtl):
    def __init__(self, _date: date, year: int, month: int):
        super().__init__(_date, year, month)

    def get_trip_taxi_green(self):
        return self.reader.read_trip_data_raw(TripDataType.green)

    def get_trip_taxi_yellow(self):
        return self.reader.read_trip_data_raw(TripDataType.yellow)

    def get_trip_rental(self):
        return self.reader.read_trip_data_raw(TripDataType.fhvhv)

    def get_trip_rental_hv(self):
        return self.reader.read_trip_data_raw(TripDataType.fhvhv)

    @staticmethod
    def filter_valid_taxi_trips(df: DataFrame):
        return df.filter(pl.col('lpep_pickup_datetime').is_not_null() &
                         pl.col('lpep_dropoff_datetime').is_not_null() &
                         pl.col('PUlocationID').is_not_null() &
                         pl.col('DOlocationID').is_not_null())

    @staticmethod
    def transform_taxi(df_green: DataFrame, df_yellow: DataFrame) -> DataFrame:
        df_green_upd = df_green.drop('trip_type')\
                               .rename({"lpep_pickup_datetime": "pickup_datetime",
                                        "lpep_dropoff_datetime": "dropoff_datetime"}) \
                               .with_columns(pl.lit('taxi_green').alias('ride_type'))

        df_yellow_enh = df_yellow.rename({"tpep_pickup_datetime": "pickup_datetime",
                                          "tpep_dropoff_datetime": "dropoff_datetime"}) \
                                 .with_columns(pl.lit('taxi_yellow').alias('ride_type'))

        # union ignoring missing columns
        df_union = pl.concat([df_green_upd, df_yellow_enh], how="diagonal")

        # dropping columns irrelevant for report
        df_select = df_union.drop('store_and_fwd_flag',
                                  'RatecodeID',
                                  'passenger_count')

        return df_select

    @staticmethod
    def transform_rental(df: DataFrame) -> DataFrame:
        # dropping columns irrelevant for report
        df_upd = df.drop('hvfhs_license_num', 'dispatching_base_num', 'originating_base_num',
                          'shared_request_flag', 'shared_match_flag', 'access_a_ride_flag',
                          'wav_request_flag', 'wav_match_flag') \
                   .with_columns(pl.lit('rental').alias('ride_type'))

        return df_upd

    @staticmethod
    def validate_data(df: pl.DataFrame):
        pass