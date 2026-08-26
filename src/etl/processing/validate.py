from src.etl.helpers import get_arg_parser
from src.etl.processing.transformations import Transformations

def main(processing_date, reporting_year, reporting_month):
    tf = Transformations(processing_date, reporting_year, reporting_month)

    df_trip_raw = tf.reader.read_trip_data_raw()

    tf.validate_data(df_trip_raw)

    """
    Cols not null
    PUlocationID not null; 
    DOlocationID not null
    """


if __name__ == '__main__':
    args = get_arg_parser().parse_args()
    main(args.date, args.year, args.month)

