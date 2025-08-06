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

# 文档操作(Document)
[Document](https://www.elastic.co/docs/api/doc/elasticsearch/group/endpoint-document)

## 批量创建或者删除文档 (Bulk index or delete documents)
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

> 数据流不支持自定义路由除非在模版中启用` allow_custom_routing`设置创建的

#### 等待活动分片 Wait for active shards
在进行批量调用的时候，可以指定`wait_for_active_shards`参数，以要求在开始处理批量请求之前至少有多少个分片副本处于活动状态。

#### 刷新 Refresh
控制什么时候可以搜索到这个请求所做的更改
> 只有接受批量请求的分片才会受到刷新的影响，`refresh=wait_for`
> 可以禁用刷新，以提高批量请求的索引吞吐量。

[参考文档](https://www.elastic.co/docs/deploy-manage/production-guidance/optimize-performance/indexing-speed#disable-refresh-interval)

### 路径参数 Path parameters
index String 必须
批量操作必须包含data stream或者索引或别名

### 查询参数
**include_source_error** Boolean
分析发生错误的时候错误消息是否包含源文档

**list_executed_pipelines** Boolean
true的时候响应包含每个索引或创建运行的管道

**pipeline** String
用于预处理传入文档的管道标识符。如果指定了默认的提取管道，则将该值设置为`_none`会关闭此请求的默认提取管道。如果配置了最终管道，则一直会保持运行。

#### refresh String
如果`true`,Elasticsearch会刷新受影响的分片，只对搜索可见。如果是`wait_for`，等待刷新以使这个操作可以提供搜索。如果是`false`，就不刷新。

#### routing String
用于将操作路由到也定的分片的自定义值

#### _source Boolean，String，Array[String]
是否返回 `_source`字段，或者要返回的字段列表。

#### _source_excludes String,Array[String]
从响应中排除的源字段。也可以从`_source_includes`查询参数中指定的子集中排除字段。如果`_source`是`false`，就会忽略这个参数。

#### _source_includes String,Array[String]
要包含着响应中的源字段的列表。如果使用这个字段，就会仅返回这些源字段。也可以使用_source_excludes，在子集中继续排除，如果`_source`是`false`，就会忽略这个参数。

#### timeout String
每个操作等待下一个操作的时间；自动索引创建、动态映射更新和等待活动分片。默认值是1min，保证Elasticsearch值失败之亲啊的至少等待超时。实际时间可能会更长，当发生多个等待的时候。

可以设置值是 0 代表不等待, -1 一直等待

#### wait_for_active_shards Number | string
批量操作必须等待至少多少个分片副本处于活动状态。可以设置为all或者任意正整数,最大是索引中分片副本数(`number_of_replicas+1`),默认是1,等待每个主分片处于活动状态.

#### require_alias Boolean
true 代表必须是索引的别名

#### require_data_stream Boolean
true 代表操作的目标必须是数据流(已经存在或创建)

### Body Object Required

#### OperationContainer Object

**index** Object
- _id: String
- _index: String
- routing:  String
- if_primary_term: Number
- if_seq_no: Number
- version: Number
- version_type: String 值可以是 internal, external, external_gte, force
- dynamic_templates: Object 从字段全名匹配的动态模板,如果不存在就使用这个模版,如果已经存在就不处理.
**dynamic_templates attribute** Object
String
- pipeline String
  用于预处理传入文档的管道标识符。如果指定了默认的提取管道，则将该值设置为`_none`会关闭此请求的默认提取管道。如果配置了最终管道，则一直会保持运行。
- require_alias Boolean . true 代表必须是索引的别名,默认false

**create** Object
跟index 完全一样
- _id: String
- _index: String
- routing:  String
- if_primary_term: Number
- if_seq_no: Number
- version: Number
- version_type: String 值可以是 internal, external, external_gte, force
- dynamic_templates: Object 从字段全名匹配的动态模板,如果不存在就使用这个模版,如果已经存在就不处理.
  **dynamic_templates attribute** Object
  String
- pipeline String
  用于预处理传入文档的管道标识符。如果指定了默认的提取管道，则将该值设置为`_none`会关闭此请求的默认提取管道。如果配置了最终管道，则一直会保持运行。
- require_alias Boolean . true 代表必须是索引的别名,默认false

**update** Object
多出这个字段
- retry_on_conflict:  Number 版本冲突重试的次数
其他基本一样的字段
- _id: String
- _index: String
- routing:  String
- if_primary_term: Number
- if_seq_no: Number
- version: Number
- version_type: String 值可以是 internal, external, external_gte, force
- pipeline String
  用于预处理传入文档的管道标识符。如果指定了默认的提取管道，则将该值设置为`_none`会关闭此请求的默认提取管道。如果配置了最终管道，则一直会保持运行。
- require_alias Boolean . true 代表必须是索引的别名,默认false


**delete** Object
- _id: String
- _index: String
- routing:  String
- if_primary_term: Number
- if_seq_no: Number
- version: Number
- version_type: String 值可以是 internal, external, external_gte, force

### Responses 
200
- errors Boolean Required .如果是true,批量请求中有一个或多个操作失败
- items Array[Object] Required. 每个操作响应的结果,按照提交请求顺序
attribute 如下
    - _id string | null
    - _index string Required
    - status number Required . http请求状态码
    - failure_store String. 值可能出现的范围:[not_applicable_or_unknown | used | not_enabled | failed ]
    - error  Object,包含属性
      - reason string | null . 错误信息
      - stack_trace string 错误堆栈,error_trace=true的时候才会有
      - caused_by Object. 请求失败详细原因
      - root_cause Array[Object] . 请求失败的原因和详细信息。
    - _primary_term number. 操作成功的时候有值,操作的主分片的任期号
    - result string. 操作的结果,值可能出现的范围:[created | updated | deleted ]
    - _seq_no number
    - _shards Object.
      - failed number Required
      - successful number Required
      - total number Required
      - failures Array[Object]
      - skipped number
    - _version  number
    - forced_refresh  boolean
    - get Object.
      - fields object 
      - found boolean Required
      - _seq_no number
      - _primary_term number
      - _routing string
      - _source object
    - took number Required
    - ingest_took number
## Create a new document in the index 创建文档
格式
```http request
POST /{index}/_create/{id}
PUT /{index}/_create/{id}
```
使用_creat的时候需要保证{id}不存在,如果存在,则返回409错误

示例
```http request
PUT my-index-000001/_create/1
{
  "@timestamp": "2099-11-15T13:12:00",
  "message": "GET /search HTTP/1.1 200 1070000",
  "user": {
    "id": "kimchy"
  }
}
```
如果启用了安全功能,执行的时候需要对目标数据流、索引或者索引别名有索引权限
- `POST /{index}/_create/{id}`: 创建文档必须要有`create_doc,create,index`或`write index`的权限
- 如果要自动创建索引或者数据流,必须要有`auto_config,create_index`或`manage`权限
自动创建数据流需要启用数据流的匹配索引模版

### Automatically create data streams and indices 自动创建数据流或者索引
如果请求的目标不存在,并且有与具有data_stream定义的索引模版匹配,则索引操作自动创建数据流.
如果目标不存在,没有与之匹配的数据流模版,那么就会自动创建索引,并应用任何匹配的索引模版
如果不存在映射,索引操作会创建动态映射.默认情况,新的字段和对象会自添加到映射中.

自动创建索引由`action.auto_create_index`控制,true可以创建任意索引,false是禁止, 可以使用多个逗号分割的模式,使用 + 或 - 前缀来标记允许或禁用模式.直接使用列表代表不允许.

> `action.auto_create_index` 只影响索引的自动创建,不影响数据流的创建

### Routing 路由

默认情况下分片的位置(或者路由)是使用文档的ID值的散列来控制.对于显示的控制,可以使用`routing`参数来显式控制,直接指定路由器使用的hash函数的值.
在使用显示映射时,可以使用`_routing`参数来指定索引操作从文档中获取路由值,但是需要额外解析文档(代价也比较小).如果定义了`_routing`设置,并且设置为必须,如果没有提供或提取路由值,那么索引操作就会失败.

> 数据流不支持自定义路由,除非是在模版中使用`allow_custom_routing`创建的

### Distributed 分布式
索引操作根据主分片的路由定位到主分片,并且在该分片的实际节点上执行.在主分片完成操作后,如果需要,把更新分发到合适的副本.

### Active shards 激活分片
为了提高系统的写入的弹性,可以将索引的操作配置为在操作之前等待一定数量的活动分片副本.如果没有达到数量,写入操作必须等待或者重试,直到需要的分片副本已经启动或发送超时.默认情况下写操作只会等待主分片处于活动状态后才会继续(`wait_for_active_shards`是1).可以通过`index.write.wait_for_active_shards`参数进行覆盖配置配置.也可以直接在请求中携带参数`wait_for_active_shards`

有效值范围是索引中每个分片配置的副本总数(number_of_replicas + 1)以内的所有或任意正整数.如果是负值或者大于分片副本数就会报错.

这个设置会降低写入操作的未写入所需分片副本的可能性,但是不能消除,因为这个检查发生在写操作之前,在写操作完成之后,复制可能在任何数量的分片副本上失败,但是主分仍然是成功的,响应结果中`_shards`部分显示复制成功和失败的分片副本数量.

### No operation (noop) update
在使用API更新文档的时候,如果文档没有改变,也总是会创建文档的新副本,如果不能接受,那么在使用 `_update` API的时候设置`detect_noop`为true.但是创建文档的时候这个选项是不可用的,因为没有旧的 文档,就不能进行比较.

### Versioning 版本控制


#  search
[search](https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-search)



#  映射
[Mapping](https://www.elastic.co/docs/manage-data/data-store/mapping)

# 模版
[templates](https://www.elastic.co/docs/manage-data/data-store/templates)

# 聚合
[aggregations](https://www.elastic.co/docs/explore-analyze/query-filter/aggregations)

# 节点设置
[node-settings](https://www.elastic.co/docs/reference/elasticsearch/configuration-reference/node-settings)、

# 分析器
[text-analysis](https://www.elastic.co/docs/manage-data/data-store/text-analysis)

# 优化加速
[search-speed](https://www.elastic.co/docs/deploy-manage/production-guidance/optimize-performance/search-speed)

# 生产指导
[生产指导](https://www.elastic.co/docs/deploy-manage/production-guidance)





