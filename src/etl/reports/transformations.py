import polars as pl
from polars import DataFrame
from datetime import date

from src.etl.transformations import TransformationsEtl
from src.etl.helpers import TransformedDataType


class Transformations(TransformationsEtl):
    def __init__(self, _date: date, year: int, month: int):
        super().__init__(_date, year, month)

    def read_transformed_taxi(self) -> DataFrame:
        return self.reader.read_trip_data_transformed(TransformedDataType.taxi)

    def read_transformed_rental(self) -> DataFrame:
        return self.reader.read_trip_data_transformed(TransformedDataType.rental)

    @staticmethod
    def join_on_zone(df_lookup: DataFrame, df_taxi: DataFrame, df_rental: DataFrame):
        df_zones_taxi = df_lookup.join(df_taxi.limit(100),
                                       left_on="LocationID",
                                       right_on="PULocationID",
                                       how="left")

        df_zones_rental = df_lookup.join(df_rental.limit(100),
                                         left_on="LocationID",
                                         right_on="PULocationID",
                                         how="left")

        df_union = pl.concat([df_zones_taxi, df_zones_rental], how="diagonal")

        return df_union


    @staticmethod
    def enhance(df: DataFrame) -> DataFrame:
        datum = (pl.col('pickup_datetime').cast(pl.Date).alias('datum'))
        borough_zone = (pl.concat_str(['Borough', 'Zone'], separator="/").alias("borough_zone"))
        trip_duration = (pl.coalesce([pl.col('trip_time'),
                                     ((pl.col('dropoff_datetime') - pl.col('pickup_datetime')).dt.total_seconds())]).alias('trip_duration'))
        trip_distance = (pl.coalesce([pl.col("trip_distance"), pl.col("trip_miles"),]).alias("trip_distance"))
        trip_fare = (pl.coalesce([pl.col("fare_amount"), pl.col("base_passenger_fare"),]).alias("trip_fare"))
        """
        fhvhv: driver_pay = Total driver pay (not including tolls or tips and net of commission, surcharges, or taxes).
            .. hence need to include tips: tips Total amount of tips received from passenger.
        taxi: total_amount = The total amount charged to passengers. Does not include cash tips.
        """
        trip_earnings = (pl.coalesce([pl.col('total_amount'), (pl.col('driver_pay') + pl.col('tips'))]).alias('trip_earnings'))

        return df.with_columns(datum, borough_zone, trip_duration, trip_distance, trip_fare, trip_earnings)

    @staticmethod
    def aggregate(df: DataFrame) -> DataFrame:
        df_agg = df.group_by('datum', 'borough_zone') \
                   .agg(pl.len().alias('trip_count'),
                        pl.col('trip_duration').mean().alias("trip_duration_avg"),
                        pl.col('trip_distance').mean().alias("trip_distance_avg"),
                        pl.col('trip_fare').mean().alias("trip_fare_avg"),
                        pl.col('trip_earnings').mean().alias("trip_earnings_avg"))

        return df_agg

    @staticmethod
    def adjust(df: DataFrame) -> DataFrame:
        return df
