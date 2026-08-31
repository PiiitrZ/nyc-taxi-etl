from src.etl.helpers import get_arg_parser, Reader, TripDataType
from src.etl.dq.validate import print_data_overview, run_dq
from src.etl.dq.rules import RULES_TAXI, RULES_TAXI_YELLOW


def main(processing_date, reporting_year, reporting_month):
    reader = Reader(processing_date, (reporting_year, reporting_month))

    df = reader.read_trip_data_raw(TripDataType.yellow)

    print_data_overview(df)

    rules = {**RULES_TAXI,
             **RULES_TAXI_YELLOW}

    dq_results = run_dq(df, rules)

    # print/store/email
    print(dq_results)


if __name__ == '__main__':
    args = get_arg_parser().parse_args()
    main(args.date, args.year, args.month)