from src.etl.helpers import get_arg_parser
from src.etl.processing.transformations import Transformations

def main(processing_date, reporting_year, reporting_month):
    tf = Transformations(processing_date, reporting_year, reporting_month)

    df_taxi_green_raw = tf.get_trip_taxi_green()
    df_taxi_yellow_raw = tf.get_trip_taxi_yellow()

    df_taxi_transformed = tf.transform_taxi(df_taxi_green_raw, df_taxi_yellow_raw)

    tf.writer.export_parquet(df_taxi_transformed, path='transformed/trips/taxi', f_name='transformed')


if __name__ == '__main__':
    args = get_arg_parser().parse_args()
    main(args.date, args.year, args.month)

