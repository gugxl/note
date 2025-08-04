# 序

文档说明
[8.6官方文档](https://www.elastic.co/guide/en/elasticsearch/reference/8.6/elasticsearch-intro.html)
[最新版本](https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html)


单机模式: [docker compose搭建elk 8.6.2](https://blog.csdn.net/zhazhagu/article/details/148619309)
集群模式:[使用docker compose 部署Elasticsearch 9.0.4集群 + kibana](https://blog.csdn.net/zhazhagu/article/details/149809217)

使用最新版的进行学习,按照重要程度进行学习,先学习重要的

# 快速开始
[get-started](https://www.elastic.co/docs/solutions/search/get-started)
https://www.elastic.co/docs/api/doc/elasticsearch/group/endpoint-document
## 基础知识 
[Index basics](https://www.elastic.co/docs/manage-data/data-store/index-basics)
索引是Elasticsearch存储的基本单元.是名称或者别名唯一标识的文档的集合.所有的搜索和查询都要基于这个唯一标识.

### 索引组成
#### 1.  文档 (Documents)
使用json文档的形式序列化和存储数据.文档是一组字段,每个字段包含一个名称和值.每个文档都有唯一的ID,可以自己指定或者由Elasticsearch自动生成.
示例:
```http request
{
  "_index": "my-first-elasticsearch-index",
  "_id": "DyFpo5EBxE8fzbb95DOa",
  "_version": 1,
  "_seq_no": 0,
  "_primary_term": 1,
  "found": true,
  "_source": {
    "email": "john@smith.com",
    "first_name": "John",
    "last_name": "Smith",
    "info": {
      "bio": "Eco-warrior and defender of the weak",
      "age": 25,
      "interests": [
        "dolphins",
        "whales"
      ]
    },
    "join_date": "2024/05/01"
  }
}
```

#### 2. 元数据字段(Metadata fields)
元数据字段是存储有关文档信息的系统字段.在Elasticsearch中元数据字段的名称都以_开头.
例如 :
_index : 存储文档的索引名称
_id : 文档的ID,在索引里面文档的id是唯一的
#### 3. 映射和数据类型(Mappings and data types)
每个索引都有一个映射或模式,用于说明如何对文档中的字段进行索引.映射定义了索引的类型、字段的索引方式以及存储方式.

```http request
PUT /semantic-index
```

## 文档操作(Document)
[Document](https://www.elastic.co/docs/api/doc/elasticsearch/group/endpoint-document)

### 批量创建或者删除文档 (Bulk index or delete documents)
语法 :
```http request
PUT /{index}/_bulk
POST /{index}/_bulk
PUT /_bulk
POST /_bulk
```
例如:多种操作
> 注意如果是kibana数据批量请求,数据放到同一行,如果是curl,数据最后一行多个换行符,下面一般情况下使用kibana的格式

```http request
POST /_bulk?pretty
{"index":{"_index":"test","_id":"1"}}{"field1":"value1"}{"delete":{"_index":"test","_id":"2"}}{"create":{"_index":"test","_id":"3"}}{"field1":"value3"}{"update":{"_index":"test","_id":"1"}}{"doc":{"field2":"value2"}}
```

批量update 可以使用retry_on_conflict 指定版本冲突重试次数
```http request
POST /_bulk?pretty
{ "update" : {"_id" : "1", "_index" : "index1", "retry_on_conflict" : 3} }{ "doc" : {"field" : "value"} }{ "update" : { "_id" : "0", "_index" : "index1", "retry_on_conflict" : 3} }{ "script" : { "source": "ctx._source.counter += params.param1", "lang" : "painless", "params" : {"param1" : 1}}, "upsert" : {"counter" : 1}}{ "update" : {"_id" : "2", "_index" : "index1", "retry_on_conflict" : 3} }{ "doc" : {"field" : "value"}, "doc_as_upsert" : true }{ "update" : {"_id" : "3", "_index" : "index1", "_source" : true} }{ "doc" : {"field" : "value"} }{ "update" : {"_id" : "4", "_index" : "index1"} }{ "doc" : {"field" : "value"}, "_source": true}
```

只查看失败的信息,使用`filter_path=items.*.error`进行过滤
```http request
POST /_bulk?filter_path=items.*.error
{ "index" : { "_index" : "test", "_id" : "1" } }{ "field1" : "value1" }{ "delete" : { "_index" : "test", "_id" : "2" } }{ "create" : { "_index" : "test", "_id" : "3" } }{ "field1" : "value3" }{ "update" : {"_id" : "1", "_index" : "test"} }{ "doc" : {"field2" : "value2"} }
```

运行`POST /_bulk`以执行包含索引和创建操作且带有`dynamic_templates`参数的批量请求。根据`dynamic_templates`参数，该批量请求会创建两个类型为`geo_point`的新字段`work_location`和`home_location`。然而，`raw_location`字段是使用默认的动态映射规则创建的，在这种情况下，由于它在JSON文档中是以字符串形式提供的，因此被创建为文本字段。
```http request
POST /_bulk
{ "index" : { "_index" : "my_index", "_id" : "1", "dynamic_templates": {"work_location": "geo_point"}} }{ "field" : "value1", "work_location": "41.12,-71.34", "raw_location": "41.12,-71.34"}{ "create" : { "_index" : "my_index", "_id" : "2", "dynamic_templates": {"home_location": "geo_point"}} }{ "field" : "value2", "home_location": "41.12,-71.34"}
```

在单个请求中执行多个 index、create、delete 或 update 操作,可以减少开销,提高索引速度.

如果开启了权限功能,需要的权限说明
- create操作: create_doc、create、index、 write index权限;数据流只支持create操作
- index操作: create、index或write index权限;
- delete操作: delete、write index权限;
- update操作: index或write index权限;
- 批量API自动创建数据流或索引:auto_configure、create_index或者manage index权限;
- 使用refresh让批量操作对搜索结果可见:maintenance或manage index权限;

数据流自动创建需要启用数据流匹配的索引模版

如果在批量请求的路径上指定了index，那么在所有没有指明_index的操作中都会使用这个索引
> Elasticsearch默认将HTTTP请求设置最大大小为100MB，因此在请求的时候必须保证请求小于这个大小。

#### 乐观并发控制 Optimistic concurrency control

批量API调用的每个index和delete在各自的动作和Meta数据行中包含if_seq_no和if_primary_term参数，使用if_seq_no和if_primary_term参数根据现有文档最后一次修改来控制操作的运行方法。


#### 版本控制（version）
每个批量操作都可以包含版本值。会根据_version映射自动匹配索引或者删除操作。也支持version_type操作

#### 路由 Routing
每个批量操作都支持`routing`字段，会根据_routing映射自动匹配对应的索引或者删除操作

> 数据流不支持自定义路由除非在模版中使用` allow_custom_routing`

##  search
[search](https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-search)



##  映射
[Mapping](https://www.elastic.co/docs/manage-data/data-store/mapping)

## 模版
[templates](https://www.elastic.co/docs/manage-data/data-store/templates)

## 聚合
[aggregations](https://www.elastic.co/docs/explore-analyze/query-filter/aggregations)

## 节点设置
[node-settings](https://www.elastic.co/docs/reference/elasticsearch/configuration-reference/node-settings)、

## 分析器
[text-analysis](https://www.elastic.co/docs/manage-data/data-store/text-analysis)

## 优化加速
[search-speed](https://www.elastic.co/docs/deploy-manage/production-guidance/optimize-performance/search-speed)
