from src.etl.helpers import get_arg_parser
from src.etl.reports.transformations import Transformations

def main(processing_date, reporting_year, reporting_month):
    tf = Transformations(processing_date, reporting_year, reporting_month)

    df_lookup = tf.read_input_lookup()
    df_taxi = tf.read_transformed_taxi()
    df_rental = tf.read_transformed_rental()

    df_joined = tf.join_on_zone(df_lookup, df_taxi, df_rental)

    df_enhanced = tf.enhance(df_joined)

    df_aggregated = tf.aggregate(df_enhanced)

    df_adjusted = tf.adjust(df_aggregated)

    tf.writer.export_parquet(df_adjusted, path='report', f_name='result')


if __name__ == '__main__':
    args = get_arg_parser().parse_args()
    main(args.date, args.year, args.month)

