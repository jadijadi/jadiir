+++
title = "Find clickhouse table disk usage statistics"
description = "If you have a clickhouse database and want to find each tables disk usage and some related stats, this is my snippet:"
date = 2024-10-24T08:55:08.567Z
tags = ["admin", "clickhouse", "database", "devops", "snippet"]
medium = "https://medium.com/@jadi/find-clickhouse-table-disk-usage-statistics-9156a7c9928c"
+++

If you have a clickhouse database and want to find each tables disk usage and some related stats, this is my snippet:

```
select
    parts.*,
    columns.compressed_size,
    columns.uncompressed_size,
    columns.ratio
from (
    select database,
        table,
        formatReadableSize(sum(data_uncompressed_bytes))          AS uncompressed_size,
        formatReadableSize(sum(data_compressed_bytes))            AS compressed_size,
        sum(data_compressed_bytes) / sum(data_uncompressed_bytes) AS ratio
    from system.columns
    group by database, table
) columns right join (
    select database,
           table,
           sum(rows)                                            as rows,
           max(modification_time)                               as latest_modification,
           formatReadableSize(sum(bytes))                       as disk_size,
           formatReadableSize(sum(primary_key_bytes_in_memory)) as primary_keys_size,
           any(engine)                                          as engine,
           sum(bytes)                                           as bytes_size,
           formatReadableSize(bytes_size / rows)                as bytes_per_row
    from system.parts
    where active
    group by database, table
) parts on ( columns.database = parts.database and columns.table = parts.table )
order by parts.bytes_size desc;
```

[source](https://gist.github.com/sanchezzzhak/511fd140e8809857f8f1d84ddb937015)

---
*Originally published on [Medium](https://medium.com/@jadi/find-clickhouse-table-disk-usage-statistics-9156a7c9928c).*
