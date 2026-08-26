from src.etl.helpers import get_arg_parser
from src.etl.reports.transformations import Transformations

def main(processing_date):
    tf = Transformations(processing_date, None, None)

    path = f"data/output/report/{tf.reader.day_partition}"
    file_name = "result"
    df_results = tf.reader.read_full_path(path, file_name)

    df_results.show()

if __name__ == '__main__':
    args = get_arg_parser().parse_args()
    main(args.date)

