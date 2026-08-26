from src.etl.helpers import get_arg_parser
from src.etl.processing.transformations import Transformations

def main(processing_date, reporting_year, reporting_month):
    tf = Transformations(processing_date, reporting_year, reporting_month)

    df_trip_raw = tf.get_trip_rental()

    df_trip_transformed = tf.transform_rental(df_trip_raw)

    tf.writer.export_parquet(df_trip_transformed, path='transformed/trips/rental', f_name='transformed')


if __name__ == '__main__':
    args = get_arg_parser().parse_args()
    main(args.date, args.year, args.month)

