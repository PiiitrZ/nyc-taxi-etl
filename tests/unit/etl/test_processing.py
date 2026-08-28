import polars as pl
from datetime import date

from src.etl.processing.transformations import Transformations

transformer = Transformations(date(2026, 8, 28), 2026, 1)


def test_filter_valid_taxi_trips():
    df = pl.DataFrame({
        "lpep_pickup_datetime": [
            "2026-01-01 01:00:00",
            None,
            "2026-01-01 03:00:00",
            "2026-01-01 04:00:00",
        ],
        "lpep_dropoff_datetime": [
            "2026-01-01 01:10:00",
            "2026-01-01 02:10:00",
            None,
            "2026-01-01 04:10:00",
        ],
        "PUlocationID": [
            1,
            2,
            3,
            None,
        ],
        "DOlocationID": [
            10,
            20,
            30,
            40,
        ],
    })

    result = transformer.filter_valid_taxi_trips(df)

    assert result.height == 1

    assert result["PUlocationID"].to_list() == [1]
    assert result["DOlocationID"].to_list() == [10]


def test_transform_taxi():
    df_green = pl.DataFrame({ "lpep_pickup_datetime": ["2026-01-01 01:00:00"],
                              "lpep_dropoff_datetime": ["2026-01-01 01:10:00"],
                              "trip_type": [1],
                              "store_and_fwd_flag": ["N"],
                              "RatecodeID": [1],
                              "passenger_count": [2],
                              "trip_distance": [5.5], })

    df_yellow = pl.DataFrame({ "tpep_pickup_datetime": ["2026-01-02 02:00:00"],
                               "tpep_dropoff_datetime": ["2026-01-02 02:15:00"],
                               "store_and_fwd_flag": ["N"],
                               "RatecodeID": [1],
                               "passenger_count": [3],
                               "trip_distance": [10.0], })

    result = Transformations.transform_taxi(df_green, df_yellow)

    expected = pl.DataFrame({
        "pickup_datetime": [
            "2026-01-01 01:00:00",
            "2026-01-02 02:00:00",
        ],
        "dropoff_datetime": [
            "2026-01-01 01:10:00",
            "2026-01-02 02:15:00",
        ],
        "trip_distance": [5.5, 10.0],
        "ride_type": ["taxi_green", "taxi_yellow"],
    })

    assert result.equals(expected)


def test_transform_rental():
    df = pl.DataFrame({ "hvfhs_license_num": ["HV0001"],
                        "dispatching_base_num": ["B001"],
                        "originating_base_num": ["B002"],
                        "shared_request_flag": ["N"],
                        "shared_match_flag": ["N"],
                        "access_a_ride_flag": ["N"],
                        "wav_request_flag": ["N"],
                        "wav_match_flag": ["N"],
                        "pickup_datetime": ["2026-01-01 01:00:00"],
                        "dropoff_datetime": ["2026-01-01 01:15:00"],
                        "trip_miles": [5.5],
                        "base_passenger_fare": [20.0], })

    expected = pl.DataFrame({ "pickup_datetime": ["2026-01-01 01:00:00"],
                              "dropoff_datetime": ["2026-01-01 01:15:00"],
                              "trip_miles": [5.5],
                              "base_passenger_fare": [20.0],
                              "ride_type": ["rental"], })

    result = Transformations.transform_rental(df)

    assert result.equals(expected)