import polars as pl


def run_dq(df: pl.DataFrame, rules: dict[str, pl.Expr]) -> pl.DataFrame:
    total_rows = df.height

    return (
        df.select([(~expr.fill_null(False)).sum().alias(rule_name) for rule_name, expr in rules.items()])
          .unpivot(variable_name="rule",
                   value_name="failed_rows")
          .with_columns(pl.lit(total_rows).alias("total_rows"),
                        (pl.col("failed_rows") / total_rows * 100).alias("failure_pct"),
                        pl.when(pl.col("failed_rows") == 0).then(pl.lit("PASS")).otherwise(pl.lit("FAIL")).alias("status"))
        .select(["rule",
                 "total_rows",
                 "failed_rows",
                 "failure_pct",
                 "status"]))


def print_data_overview(df: pl.DataFrame):
    # Shape
    print("Rows:", df.height)
    print("Columns:", df.width)

    # Schema
    print(df.schema)

    # Null counts
    print(df.null_count())

    # Basic statistics
    print(df.describe())

    df.glimpse()
