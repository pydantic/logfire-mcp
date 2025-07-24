import os
from datetime import UTC, datetime, timedelta
from typing import Any

from logfire._internal.utils import truncate_string
from logfire.experimental.query_client import LogfireQueryClient
from psycopg import sql


def overview_analysis(
    filter: str = "is_exception and level >= 'error'", minutes: int = 60, num_attributes: int = 12, num_values: int = 8
) -> list[sql.Composable]:
    """Analyze a subset of the `records` table to help the user understand the data.

    This can be used as a first step, and then the user can use the `arbitrary_query` tool to get more specific details.
    You can repeat this as many times as you want.

    Args:
        filter: SQL filter to apply to records, defaults to: "is_exception and level >= 'error'"
        minutes: Time range in minutes to analyze, default 60
        num_attributes: Number of attributes to break down, default 12
        num_values: Number of distinct values for each column/attribute, default 8
    """
    global_filter = sql.SQL(filter)  # type: ignore
    print(f"\nAnalyzing:\n\n{global_filter.as_string()}\n")
    options: list[sql.Composable] = []
    value_sqls: list[sql.Composable] = [
        sql.Identifier(c)
        for c in [
            "service_name",
            "otel_scope_name",
            "span_name",
            "message",
            "exception_type",
            "exception_message",
        ]
    ]

    rows = get_rows(
        sql.SQL("""
        with attrs as (select attributes
                       from records
                       where {}),
             all_keys as (select unnest(json_keys(attributes)::text[]) as key, attributes from attrs),
             keys_values as (select key, attributes ->> key as value
                             from all_keys)
        select count(1) as n, key, count(distinct value) as n2
        from keys_values
        group by key
        order by n desc, n2 asc
        limit {}
        """).format(global_filter, num_attributes),
        minutes,
    )

    for row in rows:
        key = row["key"]
        value_sql = sql.SQL("attributes->>{}").format(sql.Literal(key))
        value_sqls.append(value_sql)

    for value_sql in value_sqls:
        num_values = get_rows(
            sql.SQL("""
                    select count(distinct {}) as n
                    from records
                    where {}
                    """).format(value_sql, global_filter),
            minutes,
        )[0]["n"]
        counts = get_rows(
            sql.SQL("""
                select {} as value, count(1) as n
                from records
                where {}
                group by value
                order by n desc
                limit {}
            """).format(value_sql, global_filter, num_values),
            minutes,
        )
        print("---")
        if num_values == 1:
            value = trunc(counts[0]["value"])
            print(f"{value_sql.as_string()} = {value!r}")
        else:
            print(f"{value_sql.as_string()} ({num_values} distinct values):\n")
            for count_row in counts:
                option_num = len(options)
                value = trunc(count_row["value"])
                print(f"Option {option_num}, {count_row['n']} rows: {value!r}")
                if value and "\n" in value:
                    print()
                options.append(sql.SQL("{} = {}").format(value_sql, sql.Literal(value)))
    return options


def trunc(x: Any) -> str | None:
    if x is None:
        return x
    return truncate_string(str(x).strip(), max_length=300)


def get_rows(query: sql.Composable, time_range_minutes: int):
    client = LogfireQueryClient(
        read_token=os.environ["LOGFIRE_READ_TOKEN"],
        base_url="https://logfire-eu.pydantic.info/",
    )
    min_timestamp = datetime.now(tz=UTC) - timedelta(minutes=time_range_minutes)
    rows = client.query_json_rows(query.as_string(), min_timestamp=min_timestamp)["rows"]
    return rows
