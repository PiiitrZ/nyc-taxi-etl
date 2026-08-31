import polars as pl

RULES_TAXI = {
    "trip_distance_non_negative":
        pl.col("trip_distance") >= 0,

    "fare_amount_non_negative":
        pl.col("fare_amount") >= 0,

    "total_amount_non_negative":
        pl.col("total_amount") >= 0,

    "passenger_count_positive":
        pl.col("passenger_count") > 0,

    "pickup_before_dropoff":
        pl.col("lpep_pickup_datetime")
        <= pl.col("lpep_dropoff_datetime"),

    "valid_store_and_fwd_flag":
        pl.col("store_and_fwd_flag").is_in(["Y", "N"]),

    "valid_payment_type":
        pl.col("payment_type").is_in([1, 2, 3, 4, 5, 6]),
}

RULES_TAXI_YELLOW = {
    "pickup_before_dropoff":
        pl.col("tpep_pickup_datetime")
        <= pl.col("tpep_dropoff_datetime"),
}

RULES_TAXI_GREEN = {
    "pickup_before_dropoff":
        pl.col("lpep_pickup_datetime")
        <= pl.col("lpep_dropoff_datetime"),

    "valid_trip_type":
        pl.col("trip_type").is_in([1, 2]),
}

RULES_RENTAL = {
    # ─────────────────────────────────────────
    # Required / basic fields
    # ─────────────────────────────────────────
    "hvfhs_license_num_present":
        pl.col("hvfhs_license_num").is_not_null(),

    "dispatching_base_num_present":
        pl.col("dispatching_base_num").is_not_null(),

    "request_datetime_present":
        pl.col("request_datetime").is_not_null(),

    "pickup_datetime_present":
        pl.col("pickup_datetime").is_not_null(),

    "dropoff_datetime_present":
        pl.col("dropoff_datetime").is_not_null(),

    "pickup_location_present":
        pl.col("PULocationID").is_not_null(),

    "dropoff_location_present":
        pl.col("DOLocationID").is_not_null(),

    # ─────────────────────────────────────────
    # Categorical / code validation
    # ─────────────────────────────────────────
    "valid_hvfhs_license_num":
        pl.col("hvfhs_license_num").is_in([
            "HV0002",
            "HV0003",
            "HV0004",
            "HV0005",
            "HV0007",
        ]),

    "valid_shared_request_flag":
        pl.col("shared_request_flag").is_in(["Y", "N"]),

    "valid_shared_match_flag":
        pl.col("shared_match_flag").is_in(["Y", "N"]),

    "valid_access_a_ride_flag":
        pl.col("access_a_ride_flag").is_in(["Y", "N"]),

    "valid_wav_request_flag":
        pl.col("wav_request_flag").is_in(["Y", "N"]),

    "valid_wav_match_flag":
        pl.col("wav_match_flag").is_in(["Y", "N"]),

    # ─────────────────────────────────────────
    # Location validation
    # ─────────────────────────────────────────
    "pickup_location_positive":
        pl.col("PULocationID") > 0,

    "dropoff_location_positive":
        pl.col("DOLocationID") > 0,

    # ─────────────────────────────────────────
    # Trip metrics
    # ─────────────────────────────────────────

    "trip_miles_non_negative":
        pl.col("trip_miles") >= 0,

    "trip_time_non_negative":
        pl.col("trip_time") >= 0,

    "base_passenger_fare_non_negative":
        pl.col("base_passenger_fare") >= 0,

    "tolls_non_negative":
        pl.col("tolls") >= 0,

    "bcf_non_negative":
        pl.col("bcf") >= 0,

    "sales_tax_non_negative":
        pl.col("sales_tax") >= 0,

    "congestion_surcharge_non_negative":
        pl.col("congestion_surcharge") >= 0,

    "airport_fee_non_negative":
        pl.col("airport_fee") >= 0,

    "tips_non_negative":
        pl.col("tips") >= 0,

    "driver_pay_non_negative":
        pl.col("driver_pay") >= 0,

    "cbd_congestion_fee_non_negative":
        pl.col("cbd_congestion_fee") >= 0,

    # ─────────────────────────────────────────
    # Datetime relationships
    # ─────────────────────────────────────────
    "request_before_on_scene":
        pl.col("request_datetime")
        <= pl.col("on_scene_datetime"),

    "on_scene_before_pickup":
        pl.col("on_scene_datetime")
        <= pl.col("pickup_datetime"),

    "pickup_before_dropoff":
        pl.col("pickup_datetime")
        <= pl.col("dropoff_datetime"),

    # ─────────────────────────────────────────
    # Trip duration consistency
    # trip_time is seconds
    # ─────────────────────────────────────────
    "trip_time_matches_timestamps":
        (
            (
                pl.col("dropoff_datetime")
                - pl.col("pickup_datetime")
            )
            .dt.total_seconds()
            - pl.col("trip_time")
        ).abs() <= 60,

    # ─────────────────────────────────────────
    # Reasonableness checks
    # ─────────────────────────────────────────
    "reasonable_trip_miles":
        pl.col("trip_miles").is_between(0, 500),

    "reasonable_trip_time":
        pl.col("trip_time").is_between(1, 24 * 60 * 60),

    "reasonable_average_speed":
        (
            pl.col("trip_miles") /
            (pl.col("trip_time") / 3600)
        ).is_between(0, 100),
}