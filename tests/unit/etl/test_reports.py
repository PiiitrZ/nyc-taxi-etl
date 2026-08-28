import polars as pl
from datetime import date, datetime

from src.etl.reports.transformations import Transformations

transformer = Transformations(date(2026, 8, 28), 2026, 1)


def test_join_on_zone():
    df_lookup = pl.DataFrame({
        "LocationID": [1, 2],
        "Zone": ["Manhattan", "Brooklyn"],
    })

    df_taxi = pl.DataFrame({
        "PULocationID": [1],
        "trip_distance": [5.5],
        "ride_type": ["taxi"],
    })

    df_rental = pl.DataFrame({
        "PULocationID": [2],
        "trip_miles": [10.0],
        "ride_type": ["rental"],
    })

    expected = pl.DataFrame({
        "LocationID": [1, 2, 1, 2],
        "Zone": ["Manhattan", "Brooklyn", "Manhattan", "Brooklyn"],
        "trip_distance": [5.5, None, None, None],
        "ride_type": ["taxi", None, None, "rental"],
        "trip_miles": [None, None, None, 10.0],
    })

    result = Transformations.join_on_zone(
        df_lookup,
        df_taxi,
        df_rental,
    )

    assert result.equals(expected)


def test_enhance():
    df = pl.DataFrame(
    {"pickup_datetime": [datetime(2026, 1, 1, 1, 0), datetime(2026, 1, 2, 2, 0), ],
     "dropoff_datetime": [datetime(2026, 1, 1, 1, 10), datetime(2026, 1, 2, 2, 20), ],
     "Borough": ["Manhattan", "Brooklyn"], "Zone": ["Midtown", "Downtown"], "trip_time": [None, 123],
     "trip_distance": [5.5, None], "trip_miles": [None, 10.0], "fare_amount": [20.0, None],
     "base_passenger_fare": [None, 30.0], "total_amount": [25.0, None], "driver_pay": [None, 40.0],
     "tips": [None, 5.0], })

    expected = pl.DataFrame({"pickup_datetime": [datetime(2026, 1, 1, 1, 0), datetime(2026, 1, 2, 2, 0), ],
                             "dropoff_datetime": [datetime(2026, 1, 1, 1, 10), datetime(2026, 1, 2, 2, 20), ],
                             "Borough": ["Manhattan", "Brooklyn"], "Zone": ["Midtown", "Downtown"],
                             "trip_time": [None, 123], "trip_distance": [5.5, 10.0], "trip_miles": [None, 10.0],
                             "fare_amount": [20.0, None], "base_passenger_fare": [None, 30.0],
                             "total_amount": [25.0, None], "driver_pay": [None, 40.0], "tips": [None, 5.0],
                             "datum": [date(2026, 1, 1), date(2026, 1, 2), ],
                             "borough_zone": ["Manhattan/Midtown", "Brooklyn/Downtown", ],
                             "trip_duration": [600.0, 123.0], "trip_fare": [20.0, 30.0],
                             "trip_earnings": [25.0, 45.0], })
    result = Transformations.enhance(df)

    assert result.equals(expected)