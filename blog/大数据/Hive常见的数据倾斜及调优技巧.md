Hive在执行MapReduce任务时经常会碰到数据倾斜的问题，表现为一个或者几个reduce节点运行很慢，延长了整个任务完成的时间，这是由于某些key的条数比其他key多很多，这些Key所在的reduce节点所处理的数据量比其他节点就大很多，从而导致某几个节点迟迟运行不完。

那么经常有哪些情况会产生数据倾斜呢，又该如何解决，这里梳理了几种最常见的数据倾斜场景。

# 小表与大表JOIN

小表与大表Join时容易发生数据倾斜，表现为小表的数据量比较少但key却比较集中，导致分发到某一个或几个reduce上的数据比其他reduce多很多，造成数据倾斜。

优化方法：使用Map Join将小表装入内存，在map端完成join操作，这样就避免了reduce操作。有两种方法可以执行Map Join：

(1) 通过hint指定小表做MapJoin

```sql
select
/*+ MAPJOIN(time_dim) */
count
(*)
from
store_sales join time_dim on ss_sold_time_sk
=
t_time_sk
;
```
(2) 通过配置参数自动做MapJoin

核心参数：

| 参数名称 | 默认值        | 参数描述                                      |
| --- |------------|-------------------------------------------|
| hive.auto.convert.join | true      | 是否允许 Hive 自动将普通 Join（Common Join，即 Reduce-Join）转换为 Map-Side Join（Broadcast/Map Join） |
| hive.mapjoin.smalltable.filesize | 25_000_000 | 当小表文件的估算总大小小于该阈值时（默认约 25 MB），Hive 会认为这是“小表”，可以尝试做 Map Join                 |

因此，巧用MapJoin可以有效解决小表关联大表场景下的数据倾斜。

# 大表与大表JOIN

大表与大表Join时，当其中一张表的NULL值（或其他值）比较多时，容易导致这些相同值在reduce阶段集中在某一个或几个reduce上，发生数据倾斜问题。

优化方法：

(1) 将NULL值提取出来最后合并，这一部分只有map操作；非NULL值的数据分散到不同reduce上，不会出现某个reduce任务数据加工时间过长的情况，整体效率提升明显。这种方法由于有两次Table Scan会导致map增多。

```sql
SELECT
    a.user_id,
    a.username,
    b.customer_id
FROM user_info a
         LEFT JOIN customer_info b
                   ON a.user_id = b.user_id
WHERE a.user_id IS NOT NULL

UNION ALL

SELECT
    a.user_id,
    a.username,
    NULL AS customer_id
FROM user_info a
WHERE a.user_id IS NULL;
```
(2) 在Join时直接把NULL值打散成随机值来作为reduce的key值，不会出现某个reduce任务数据加工时间过长的情况，整体效率提升明显。这种方法解释计划只有一次map，效率一般优于第一种方法。

```sql
select
    a.user_id,
    a.username,
    b.customer_id
from
    user_info a
        left join customer_info b
                  on
                      case
                          when a.user_id is null then CONCAT('dp_hive', RAND())
                          else a.user_id
                          end = b.user_id;
```

# GROUP BY 操作
Hive做group by查询，当遇到group by字段的某些值特别多的时候，会将相同值拉到同一个reduce任务进行聚合，也容易发生数据倾斜。

优化方法：

(1) 开启Map端聚合
参数设置：

| 参数名称 | 默认值 | 参数描述 |
| --- | --- | --- |
| hive.map.aggr | true | 是否启用 Map 端的 Group By 聚合操作（map-side partial aggregation） |
| hive.groupby.mapaggr.checkinterval | 100000 | 在 Map 端聚合时，每处理该数量的行检查一次聚合 hash 表的大小情况，用于决定是否拆分或调整聚合 |

(2) 有数据倾斜时进行负载均衡
参数设置：

| 参数名称 | 默认值 | 描述 |
| --- | --- |----|
| hive.groupby.skewindata | false | 当 GROUP BY 操作发生数据倾斜时，是否启用两阶段聚合（通过打散倾斜 key 以实现负载均衡）。仅在 MapReduce 执行引擎下生效。 |

当设定hive.groupby.skewindata为true时，生成的查询计划会有两个MapReduce任务。在第一个MapReduce 中，map的输出结果集合会随机分布到 reduce 中， 每个 reduce 做部分聚合操作，这样处理之后，相同的 Group By Key 有可能分发到不同的 reduce 中，从而达到负载均衡的目的。在第二个 MapReduce 任务再根据第一步中处理的数据按照Group By Key分布到reduce中，（这一步中相同的key在同一个reduce中），最终生成聚合操作结果。

# COUNT(DISTINCT) 操作
当在数据量比较大的情况下，由于COUNT DISTINCT操作是用一个reduce任务来完成，这一个reduce需要处理的数据量太大，就会导致整个job很难完成，这也可以归纳为一种数据倾斜。

优化方法：将COUNT DISTINCT使用先GROUP BY再COUNT的方式替换。例如：

```sql
SELECT
    COUNT(id)
FROM (
    SELECT
        id
    FROM bigtable
    GROUP BY id
) a;
```

因此，count distinct的优化本质上也是转成group by操作。