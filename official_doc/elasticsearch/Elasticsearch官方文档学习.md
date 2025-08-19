# 序

文档说明
[8.6官方文档](https://www.elastic.co/guide/en/elasticsearch/reference/8.6/elasticsearch-intro.html)
[最新版本](https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html)


单机模式: [docker compose搭建elk 8.6.2](https://blog.csdn.net/zhazhagu/article/details/148619309)  

集群模式:[使用docker compose 部署Elasticsearch 9.0.4集群 + kibana](https://blog.csdn.net/zhazhagu/article/details/149809217)

使用最新版的进行学习,按照重要程度进行学习,先学习重要的

# 快速开始

[get-started](https://www.elastic.co/docs/solutions/search/get-started)

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
- _index : 存储文档的索引名称
- _id : 文档的ID,在索引里面文档的id是唯一的

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

批量`update` 可以使用`retry_on_conflict` 指定版本冲突重试次数
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

在单个请求中执行多个 `index`、`create`、`delete` 或 `update` 操作,可以减少开销,提高索引速度.

如果开启了权限功能,需要的权限说明
- create操作: `create_doc`、`create`、`index`、 `write index`权限;数据流只支持create操作
- index操作: `create`、`index`或`write index`权限;
- delete操作: `delete`、`write index`权限;
- update操作: `index`或`write index`权限;
- 批量API自动创建数据流或索引:`auto_configure`、`create_index`或者`manage index`权限;
- 使用refresh让批量操作对搜索结果可见:`maintenance`或`manage index`权限;

数据流自动创建需要启用数据流匹配的索引模版

如果在批量请求的路径上指定了`index`，那么在所有没有指明`_index`的操作中都会使用这个索引
> Elasticsearch默认将HTTTP请求设置最大大小为100MB，因此在请求的时候必须保证请求小于这个大小。

#### 乐观并发控制 Optimistic concurrency control

批量API调用的每个`index`和`delete`在各自的动作和`Meta`数据行中包含`if_seq_no`和`if_primary_term`参数，使用`if_seq_no`和`if_primary_term`参数根据现有文档最后一次修改来控制操作的运行方法。


#### 版本控制（version）
每个批量操作都可以包含版本值。会根据_version映射自动匹配索引或者删除操作。也支持version_type操作

#### 路由 Routing
每个批量操作都支持`routing`字段，会根据`_routing`映射自动匹配对应的索引或者删除操作

> 数据流不支持自定义路由除非在模版中启用` allow_custom_routing`设置创建的

#### 等待活动分片 Wait for active shards
在进行批量调用的时候，可以指定`wait_for_active_shards`参数，以要求在开始处理批量请求之前至少有多少个分片副本处于活动状态。

#### 刷新 Refresh
控制什么时候可以搜索到这个请求所做的更改
> 只有接受批量请求的分片才会受到刷新的影响，`refresh=wait_for`
> 可以禁用刷新，以提高批量请求的索引吞吐量。

[参考文档](https://www.elastic.co/docs/deploy-manage/production-guidance/optimize-performance/indexing-speed#disable-refresh-interval)

### 路径参数 Path parameters
- `index` `String` 必须
批量操作必须包含data stream或者索引或别名

### 查询参数
- **`include_source_error`** `Boolean`
分析发生错误的时候错误消息是否包含源文档

- **`list_executed_pipelines`** `Boolean`
true的时候响应包含每个索引或创建运行的管道

- **`pipeline`** `String`
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
要包含着响应中的源字段的列表。如果使用这个字段，就会仅返回这些源字段。也可以使用`_source_excludes`，在子集中继续排除，如果`_source`是`false`，就会忽略这个参数。

#### timeout String
每个操作等待下一个操作的时间；自动索引创建、动态映射更新和等待活动分片。默认值是1min，保证Elasticsearch值失败之亲啊的至少等待超时。实际时间可能会更长，当发生多个等待的时候。

可以设置值是 0 代表不等待, -1 一直等待

#### wait_for_active_shards Number | string
批量操作必须等待至少多少个分片副本处于活动状态。可以设置为`all`或者任意正整数,最大是索引中分片副本数(`number_of_replicas+1`),默认是1,等待每个主分片处于活动状态.

#### require_alias Boolean
`true` 代表必须是索引的别名

#### require_data_stream Boolean
`true` 代表操作的目标必须是数据流(已经存在或创建)

### Body Object Required

#### OperationContainer Object

**`index`** Object
- _id: String
- _index: String
- routing:  String
- if_primary_term: Number
- if_seq_no: Number
- version: Number
- version_type: String 值可以是 internal, external, external_gte, force
- dynamic_templates: Object 从字段全名匹配的动态模板,如果不存在就使用这个模版,如果已经存在就不处理.
**`dynamic_templates attribute`** Object
String
- pipeline String
  用于预处理传入文档的管道标识符。如果指定了默认的提取管道，则将该值设置为`_none`会关闭此请求的默认提取管道。如果配置了最终管道，则一直会保持运行。
- require_alias Boolean . true 代表必须是索引的别名,默认false

**`create`** Object
跟index 完全一样
- _id: String
- _index: String
- routing:  String
- if_primary_term: Number
- if_seq_no: Number
- version: Number
- version_type: String 值可以是 internal, external, external_gte, force
- dynamic_templates: Object 从字段全名匹配的动态模板,如果不存在就使用这个模版,如果已经存在就不处理.
  **`dynamic_templates attribute`** Object
  String
- pipeline String
  用于预处理传入文档的管道标识符。如果指定了默认的提取管道，则将该值设置为`_none`会关闭此请求的默认提取管道。如果配置了最终管道，则一直会保持运行。
- require_alias Boolean . true 代表必须是索引的别名,默认false

**`update`** Object
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


**`delete`** Object
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
`attribute` 如下
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
使用`_creat`的时候需要保证{id}不存在,如果存在,则返回409错误

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
如果请求的目标不存在,并且有与具有`data_stream`定义的索引模版匹配,则索引操作自动创建数据流.
如果目标不存在,没有与之匹配的数据流模版,那么就会自动创建索引,并应用任何匹配的索引模版
如果不存在映射,索引操作会创建动态映射.默认情况,新的字段和对象会自添加到映射中.

自动创建索引由`action.auto_create_index`控制,`true`可以创建任意索引,`false`是禁止, 可以使用多个逗号分割的模式,使用 + 或 - 前缀来标记允许或禁用模式.直接使用列表代表不允许.

> `action.auto_create_index` 只影响索引的自动创建,不影响数据流的创建

### Routing 路由

默认情况下分片的位置(或者路由)是使用文档的ID值的散列来控制.对于显示的控制,可以使用`routing`参数来显式控制,直接指定路由器使用的hash函数的值.
在使用显示映射时,可以使用`_routing`参数来指定索引操作从文档中获取路由值,但是需要额外解析文档(代价也比较小).如果定义了`_routing`设置,并且设置为必须,如果没有提供或提取路由值,那么索引操作就会失败.

> 数据流不支持自定义路由,除非是在模版中使用`allow_custom_routing`创建的

### Distributed 分布式
索引操作根据主分片的路由定位到主分片,并且在该分片的实际节点上执行.在主分片完成操作后,如果需要,把更新分发到合适的副本.

### Active shards 激活分片
为了提高系统的写入的弹性,可以将索引的操作配置为在操作之前等待一定数量的活动分片副本.如果没有达到数量,写入操作必须等待或者重试,直到需要的分片副本已经启动或发送超时.默认情况下写操作只会等待主分片处于活动状态后才会继续(`wait_for_active_shards`是1).可以通过`index.write.wait_for_active_shards`参数进行覆盖配置配置.也可以直接在请求中携带参数`wait_for_active_shards`

有效值范围是索引中每个分片配置的副本总数`(number_of_replicas + 1)`以内的所有或任意正整数.如果是负值或者大于分片副本数就会报错.

这个设置会降低写入操作的未写入所需分片副本的可能性,但是不能消除,因为这个检查发生在写操作之前,在写操作完成之后,复制可能在任何数量的分片副本上失败,但是主分仍然是成功的,响应结果中`_shards`部分显示复制成功和失败的分片副本数量.

### No operation (noop) update
在使用API更新文档的时候,如果文档没有改变,也总是会创建文档的新副本,如果不能接受,那么在使用 `_update` API的时候设置`detect_noop`为true.但是创建文档的时候这个选项是不可用的,因为没有旧的 文档,就不能进行比较.

### Versioning 版本控制
每个被索引的文档都有一个版本号。默认情况下使用内部版本控制，从1开始，随着每次更新（包括删除）递增。版本号也可以使用外部的值，这个时候应该把`version_type`设置为`external`。提供的值必须大于等于`0`小于`9.2e+18`的长整型数值.

> 版本控制是完全实时的，搜索是近实时的，如果没有提供版本，那么就不会进行任何版本检查

当使用外部版本类型时，系统检查传递给索引请求的版本号是否大于当前存储文档的版本。如果大于，对文档进行索引并且使用新的版本号。如果小于或者等于，就会发生版本冲突，索引操作失败。
```http request
PUT my-index-000001/_doc/1?version=2&version_type=external
{
  "user": {
    "id": "elkbee"
  }
}
```
上面的示例会正常执行，但是当重复执行的时候，因为提供的版本号不大于当前文档的版本，就会出现版本冲突，http 409状态


### Path parameters路径参数

- index String Required
目标数据流或者索引的名称，如果目标不存在，并且与具有*定义的索引模版名称或者模式匹配，则此请求将会创建数据流。如果目标不存在，且与数据流模版不匹配，则此请求会创建索引

- id String Required
文档的唯一标识。如果需要自动生成文档id，可以生路id字段进行创建如 `POST /<target>/_doc/`并省略这个参数。

### Query parameters 查询参数
- if_primary_term Number
只有在主分片任期（primary term）与请求中的值完全匹配的时候，才会执行这次操作，否则拒绝。
- if_seq_no Number
仅当文档具有此序号时才执行此操作
- include_source_on_error Boolean
当值为`ture`，当索引文档出现解析错误`（parsing error）`的时候，错误消息会包含整个文档的`_source`内容
当值为`false`，错误信息不包含`_source`，只显示错误原因。
> 为什么有这个选项，1. **方便调试**，2. **安全考虑**，文档中有敏感信息，可以设置为false，3. 性能考虑可以设置为false减少响应数据量
- op_type String
设置为`create`，仅当文档不存在的时候索引文档，如果指定了`_id`的文档已经存在了，索引操作将失败。操作跟 `<index>/_create`一致。如果指定了文档的id，则参数默认为`index`。否则默认为`create`。如果请求的目标是数据流，则需要`op_typ`e为`create`
取值 为 `【 index ｜ create 】`，分别代表覆盖任何已经存在的文档，仅索引不存在的文档。
- pipeline String
  用于预处理传入文档的管道标识符。如果指定了默认的提取管道，则将该值设置为`_none`会关闭此请求的默认提取管道。如果配置了最终管道，则一直会保持运行。
- refresh String
  如果`true`,Elasticsearch会刷新受影响的分片，只对搜索可见。如果是`wait_for`，等待刷新以使这个操作可以提供搜索。如果是`false`，就不刷新。
- routing String
  用于将操作路由到也定的分片的自定义值
- timeout String
请求等待以下操作的时间；自动索引创建、动态映射更新和等待活动分片。默认值是`1min`，保证Elasticsearch值失败之亲啊的至少等待超时。实际时间可能会更长，当发生多个等待的时候。

可以设置值是 0 代表不等待, -1 一直等待
- version Number 
跟之前的一样是非负的长整数
- version_type String
  值可以是 
  - internal, 内部控制，从1开始，每次更新或删除时递增
  - external, 版本高于文档版本或者文档不存在的时候才能编辑文档
  - external_gte, 版本高于或等于文档版本或者文档不存在的时候才能编辑文档，需要谨慎使用，可能会导致数据丢失
  - force 已经弃用，因为可能导致 主分片和副本分片分离 
- wait_for_active_shards Number | string
  批量操作必须等待至少多少个分片副本处于活动状态。可以设置为`all`或者任意正整数,最大是索引中分片副本数(`number_of_replicas+1`),默认是1,等待每个主分片处于活动状态.
- require_alias Boolean
  true 代表必须是索引的别名 
- require_data_stream Boolean 
   true 代表操作的目标必须是数据流(已经存在或创建)
### Body Object Required 
### Responses
200 
- _id String Required
- _index String Required
- status number Required . http请求状态码
    - failure_store String. 值可能出现的范围:[not_applicable_or_unknown | used | not_enabled | failed ]
    - error  Object,包含属性
        - reason string | null . 错误信息
        - stack_trace string 错误堆栈,error_trace=true的时候才会有
        - caused_by Object. 请求失败详细原因
        - root_cause Array[Object] . 请求失败的原因和详细信息。
    - _primary_term number. 操作成功的时候有值,操作的主分片的任期号
    - result string. 操作的结果,值可能出现的范围:[created | updated | deleted | not_found | noop]
    - _seq_no number
    - _shards Object.
        - failed number Required
        - successful number Required
        - total number Required
        - failures Array[Object]
        - skipped number
    - _version  number
    - forced_refresh  boolean
  
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
响应
```json
{
  "_index": "my-index-000001",
  "_id": "1",
  "_version": 4,
  "result": "created",
  "_shards": {
    "total": 2,
    "successful": 2,
    "failed": 0
  },
  "_seq_no": 3,
  "_primary_term": 1
}
```
## Get a document by its ID 根据id获取文档
格式
```http request
GET /{index}/_doc/<id>
```
从索引中获取文档

默认情况下是实时的,不受刷新率影响.在使用`stored_fields`参数请求存储字段并且文档已经更新但尚未刷新的情况下，API必须解析和分析源以存储字段.如果需要关闭可以把`realtime`参数设置为`false`.

Source filtering
默认情况下,API返回_source字段的内容,除非使用了`stored_fields`或者`_source`字段被关闭,可以使用`_source`来关闭
```http request
GET /my-index-000001/_doc/1?_source=false
```
如果只需要其中的几个字段可以使用`_source_includes`或`_source_excludes` 来包含或者过滤掉某些字段.对于检索可以节省网络开销,对于大型文档很有作用,都是逗号分割的字段或者表达式.
```http request
GET my-index-000001/_doc/0?_source_includes=*.id&_source_excludes=entities
GET my-index-000001/_doc/0?_source=*.id
```
Routing 路由

如果在索引期间使用路由，则还需要指定路由值以检索文档
```http request
GET my-index-000001/_doc/2?routing=user1
```
此请求获取ID为2的文档，但它是根据用户路由的。如果未指定正确的路由，则不会获取文档。但是如果分片是一样的时候也是可以获取数据的

Distribute 分布式
`GET`操作被散列到分片`Id`上，然后这个分片的所有副本都可以返回结果。也意味着副本越多，GET请求的伸缩性就越好。

Version Support 版本控制支持
当文档版本等于当前查询指定的版本，才能检索出文档
在更新的时候，在内部Elasticsearch旧文档被标记为删除，并添加新文档，即使无法访问他，旧的文档也不会立即消失，Elasticsearch会在后台清理已经删除的文档，同时索引更多的数据。

Required authorization

索引的`read`权限

Path parameters 路径参数
- index String required 索引名称
- id String required 文档唯一标识

Query parameters 查询参数
- preference String 首选项
应该在哪个节点或分片上执行，默认再分片和副本间随机变化
如果设置为_local,则操作优先中本地分配的分片上执行。如果设置为自定义值，则该值用于确保相同的自定义值用于相同的分片，有助于在不同的刷新状态下访问不同分片时进行“跳跃值”操作。例如可以使用`web session ID`或者用户名。
- realtime boolean
true的时候请求是实时的，而不是近实时的。
- refresh Boolean
如果是`true`，会在请求检索文档之前刷新相关分片。需要考虑并确认这个操作不会给系统造成过重负载。
- routing String
用于将操作路由到特定分片的自定义值
- _source Boolean | String | Array[String]
标识返回是否包含`_source`字段（true或false）或列出要返回的字段
- _source_excludes String | Array[String]
  从响应中排除的源字段。也可以从`_source_includes`查询参数中指定的子集中排除字段。如果`_source`是`false`，就会忽略这个参数。
- _source_exclude_vectors Boolean 在9.2.0版本中添加
是否应从`_source`排除向量
- _source_includes String,Array[String]
  要包含着响应中的源字段的列表。如果使用这个字段，就会仅返回这些源字段。也可以使用_source_excludes，在子集中继续排除，如果`_source`是`false`，就会忽略这个参数。
- stored_fields String|Array[String]
以逗号分隔存储的字段列表，作为命中的一部分返回。如果没有指定字段，那么响应中不包含任何存储字段。如果指定了这个字段，则`_source`字段默认为`false`。使用`stored_fields`只能检索叶子字段。不能返回对象字段；如果指定对象字段就会请求失败。
- version Number 版本号
  用于并发控制的版本号，当文档版本等于当前查询指定的版本，才能检索出文档
- version_type String
  值可以是
    - internal, 内部控制，从1开始，每次更新或删除时递增
    - external, 版本高于文档版本或者文档不存在的时候才能编辑文档
    - external_gte, 版本高于或等于文档版本或者文档不存在的时候才能编辑文档，需要谨慎使用，可能会导致数据丢失
    - force 已经弃用，因为可能导致 主分片和副本分片分离

### Response 响应
200

-  _index String Boolean Required
- fields Object 如果 `stored_fields` 参数设置为 `true` ，并且 `found` 为 `true` ，则它包含存储在索引中的文档字段。
- _ignored Array[String]
- found Boolean Required
- _primary_term Number 索引分配给文档的主要标识符
- _routing String 显示路由[如果设置]
- _seq_no Number
- _source Object  如果`found`是`true`，则包含json格式的文档数据，如果`_source`参数设置为`false`或者`stored_fields`是`true`，就排除这个参数
- _version 版本号

示例
```http request
GET my-index-000001/_doc/1?stored_fields=tags,counter
```
响应
```json
{
  "_index": "my-index-000001",
  "_id": "1",
  "_version": 4,
  "_seq_no": 3,
  "_primary_term": 1,
  "found": true
}
```

## Create or Update a document in an index

格式
```http request
POST /{index}/_doc/{id}
POST /{index}/_doc
PUT /{index}/_doc/{id}
```
将 JSON 文档添加到指定的数据流或索引，并使其可搜索。如果目标是索引且文档已存在，则请求会更新文档并增加其版本。
> 不能使用此API发送数据流现有文档的更新请求。

如果启用了安全功能。就需要对目标数据流，索引或索引别名具有以下的索引权限：
- 使用 `PUT /<target>/_doc/<_id>` 请求格式添加或者覆盖文档，必须要有`create`、`index`或`write`索引权限
- 使用 `POST /<target>/_doc/` 请求格式添加文档，必须要有`create`、`create_doc`、`index`或`write`索引权限
- 如果需要自动创建数据流或者索引，必须要有`auto_config`、`create_index`或者`manage` 索引权限

自动创建数据流需要启用数据流的匹配索引模版

> 索引成功返回时，副本分片可能不是完全启动的，可以通过参数 wait_for_active_shards 修改默认行为。

### Automatically create data streams and indices 自动创建数据流和索引
如果请求的目标不存在，并且有`data_stream`定义的索引模版匹配，索引会自动创建数据流

如果目标不存在，并且没有数据流模版匹配，就会自动创建索引，并且应用任何匹配的索引模版

如果不存在映射，索引会自动创建映射，默认情况下，新字段会添加到映射里面

自动创建索引由`action.auto_create_index`控制,`true`可以创建任意索引,`false`是禁止, 可以使用多个逗号分割的模式,使用 + 或 - 前缀来标记允许或禁用模式.直接使用列表代表不允许.

> `action.auto_create_index` 只影响索引的自动创建,不影响数据流的创建

### optimistic concurrency control 乐观并发控制
索引可以设置为有条件的，并且仅当对文档的最后一次分配修改了`if_seq_no`和`if_primary_term`参数指定的序列号和主术语（`primary term`）才会执行索引操作。如果检测到不匹配，就会导致`VersionConflictException`并且状态码`409`。

### Routing 路由
默认情况下分片的位置(或者路由)是使用文档的ID值的散列来控制.对于显示的控制,可以使用`routing`参数来显式控制,直接指定路由器使用的hash函数的值.
在使用显示映射时,可以使用`_routing`参数来指定索引操作从文档中获取路由值,但是需要额外解析文档(代价也比较小).如果定义了`_routing`设置,并且设置为必须,如果没有提供或提取路由值,那么索引操作就会失败.

> 数据流不支持自定义路由除非在模版中启用` allow_custom_routing`设置创建的

### Distributed 分布式
索引操作根据主分片的路由定位到主分片,并且在该分片的实际节点上执行.在主分片完成操作后,如果需要,把更新分发到合适的副本.

### Active shards 激活分片
为了提高系统的写入的弹性,可以将索引的操作配置为在操作之前等待一定数量的活动分片副本.如果没有达到数量,写入操作必须等待或者重试,直到需要的分片副本已经启动或发送超时.默认情况下写操作只会等待主分片处于活动状态后才会继续(`wait_for_active_shards`是1).可以通过`index.write.wait_for_active_shards`参数进行覆盖配置配置.也可以直接在请求中携带参数`wait_for_active_shards`

### No operation (noop) update
在使用API更新文档的时候,如果文档没有改变,也总是会创建文档的新副本,如果不能接受,那么在使用 `_update` API的时候设置`detect_noop`为true.但是创建文档的时候这个选项是不可用的,因为没有旧的 文档,就不能进行比较.

每个被索引的文档都有一个版本号。默认情况下使用内部版本控制，从1开始，随着每次更新（包括删除）递增。版本号也可以使用外部的值，这个时候应该把`version_type`设置为`external`。提供的值必须大于等于0小于9.2e+18的长整型数值.

> 版本控制是完全实时的，搜索是近实时的，如果没有提供版本，那么就不会进行任何版本检查

当使用外部版本类型时，系统检查传递给索引请求的版本号是否大于当前存储文档的版本。如果大于，对文档进行索引并且使用新的版本号。如果小于或者等于，就会发生版本冲突，索引操作失败。
```http request
PUT my-index-000001/_doc/1?version=2&version_type=external
{
  "user": {
    "id": "elkbee"
  }
}
```
上面的示例会正常执行，但是当重复执行的时候，因为提供的版本号不大于当前文档的版本，就会出现版本冲突，`http 409`状态

### Path parameters 路径参数
- index String 必须
要定位的数据流或者索引的名称，如果目标不存在，并且与具有`data_stream`定义的索引模版的名称或者通配符（*）模式匹配，则此请求就会创建数据流。如果模版不存在，且没有对应的数据流模版，那么就会创建索引。可以使用解析索引检查索引是否存在。
- id String required
  文档的唯一标识。如果需要自动生成文档id，可以生路id字段进行创建如 `POST /<target>/_doc/`并省略这个参数。

### Query parameters 查询参数
- if_primary_term Number
  只有在主分片任期（`primary term`）与请求中的值完全匹配的时候，才会执行这次操作，否则拒绝。
- if_seq_no Number
  仅当文档具有此序号时才执行此操作
- include_source_on_error Boolean
  当值为ture，当索引文档出现解析错误（parsing error）的时候，错误消息会包含整个文档的`_source`内容
  当值为false，错误信息不包含`_source`，只显示错误原因。
> 为什么有这个选项，1. **方便调试**，2. **安全考虑**，文档中有敏感信息，可以设置为false，3. 性能考虑可以设置为false减少响应数据量
- op_type String
  设置为`create`，仅当文档不存在的时候索引文档，如果指定了_id的文档已经存在了，索引操作将失败。操作跟` <index>/_create`一致。如果指定了文档的id，则参数默认为index。否则默认为create。如果请求的目标是数据流，则需要op_type为create
  取值 为 【` index ｜ create` 】，分别代表覆盖任何已经存在的文档，仅索引不存在的文档。
- pipeline String
  用于预处理传入文档的管道标识符。如果指定了默认的提取管道，则将该值设置为`_none`会关闭此请求的默认提取管道。如果配置了最终管道，则一直会保持运行。
- refresh String
  如果`true`,Elasticsearch会刷新受影响的分片，只对搜索可见。如果是`wait_for`，等待刷新以使这个操作可以提供搜索。如果是`false`，就不刷新。
- routing String
  用于将操作路由到也定的分片的自定义值
- timeout String
  请求等待以下操作的时间；自动索引创建、动态映射更新和等待活动分片。默认值是`1min`，保证Elasticsearch值失败之亲啊的至少等待超时。实际时间可能会更长，当发生多个等待的时候。

可以设置值是 0 代表不等待, -1 一直等待
- version Number
  跟之前的一样是非负的长整数
- version_type String
  值可以是
    - internal, 内部控制，从1开始，每次更新或删除时递增
    - external, 版本高于文档版本或者文档不存在的时候才能编辑文档
    - external_gte, 版本高于或等于文档版本或者文档不存在的时候才能编辑文档，需要谨慎使用，可能会导致数据丢失
    - force 已经弃用，因为可能导致 主分片和副本分片分离
- wait_for_active_shards Number | string
  批量操作必须等待至少多少个分片副本处于活动状态。可以设置为all或者任意正整数,最大是索引中分片副本数(`number_of_replicas+1`),默认是1,等待每个主分片处于活动状态.
- require_alias Boolean
  true 代表必须是索引的别名
- require_data_stream Boolean
  true 代表操作的目标必须是数据流(已经存在或创建) 

### Body Required 
Object

### Responses
200
- _id String Required
- _index String Required
- _primary_term number. 操作成功的时候有值,操作的主分片的任期号
- result string. 操作的结果,值可能出现的范围:[created | updated | deleted | not_found | noop]
- _seq_no number
- _shards Object.
    - failed number Required
    - successful number Required
    - total number Required
    - failures Array[Object]
      - index String
      - node String
      - reason Object Required
        - type String Required
        - reason String | Null
        - stack_trace String
        - cased_by Object
        - root_cause Array[Object]
        - suppressed Array[Object]
      - shard Number Required
      - status String
    - skipped number
- _version  number
- forced_refresh  boolean

## Delete a document 删除文档
格式
```http request
DELETE /{index}/_doc/{id}
```
从索引中删除文档
> 注意：不能直接将删除请求发送到数据流，要删除数据流中的文档，必须是包含该文档支持的索引为目标

### Optimistic concurrency control 乐观并发控制
删除可以设置为有条件的，并且仅当对文档的最后一次分配修改了`if_seq_no`和`if_primary_term`参数指定的序列号和主术语（`primary term`）才会执行索引操作。如果检测到不匹配，就会导致`VersionConflictException`并且状态码`409`。

### Versioning  版本控制
每个被索引的文档都有一个版本号。删除文档的时候，可以指定版本，以确保尝试删除的相关文档实际上正在被删除，并且在此期间没有更该。在文档上的每个写入操作（包括删除）都会导致版本递增。已删除的文档的版本号在删除后短时间仍然可用，以便控制并发。已经删除的文档保持可用时间有`index.gc_deletes`索引设置决定。

### Routing 路由
如果在索引期间指定了路由，则还需要指定路由才能删除文档。
如果`_routing`映射设置为required并且未指定路由值，那么执行删除文档的时候会抛出`RoutingMissException`并拒绝请求。
```http request
DELETE /my-index-000001/_doc/1?routing=shard-1
```
这个请求就会删除ID为1的文档，但是会根据用户指定的路由，如果指定的路由不正确，就不会删除。

### Distributed 分布式
删除操作hash到对应的分片ID,然后重定向到这个分片的.在主分片完成操作后,如果需要,把更新分发到对应分片副本.

### Required authorization 所需权限
- Index privileges： delete

### Path parameters 路径参数
- index String Required
- id String Required

### Query parameters 查询参数
- if_primary_term Number 主分片版本号一致才执行
- if_seq_no Number 当文档的序列化是这个值的时候才执行
- refresh String
如果为 `true`，Elasticsearch 将刷新受影响的分片，使此作对搜索可见。如果 `wait_for`，它会等待刷新以使此作对搜索可见。如果为 `false`，则刷新不执行任何作。
- routing String
用于将路由到特定分片的自定义值。
- timeout  String
等待活动分片的时间段  
参数适用于在删除操作运行的时候分配给执行操作的主分片可能不可用的情况。造成这种情况的一般原因是主分片正在从存储中恢复或正在重定位。默认情况下，时间是1min，然后会失败响应错误。
可以使用 0 代表不等待, -1 一直等待
- version Number
用于并发控制的显式版本号。它必须与文档的当前版本匹配，请求才能成功。
- version_type String
  值可以是
    - internal, 内部控制，从1开始，每次更新或删除时递增
    - external, 版本高于文档版本或者文档不存在的时候才能编辑文档
    - external_gte, 版本高于或等于文档版本或者文档不存在的时候才能编辑文档，需要谨慎使用，可能会导致数据丢失
    - force 已经弃用，因为可能导致 主分片和副本分片分离
- wait_for_active_shards Number | string
  批量操作必须等待至少多少个分片副本处于活动状态。可以设置为all或者任意正整数,最大是索引中分片副本数(`number_of_replicas+1`),默认是1,等待每个主分片处于活动状态.

### Response 
200
- _id String Required
- _index String Required
- _primary_term Number 分配给索引的主分片的年代号 【自己翻译的，主分片在变更的时候这序号会递增，防止数据变脏】
- result String Required 值是 `create`、`updated`、`deleted`、`not_found`、`noop`
- _seq_no Number 
- _shards Object Object
  - failed Number Required
  - successful Number Required
  - total Number Required
  - failures Array[object]
    - index String
    - node String
    - reason Object Required
      - type String Required
      - reason String | Null
      - stack_trace String
      - cased_by Object
      - root_cause Array[Object]
      - suppressed Array[Object]
      - shard Number Required
      - status String
    - skipped number
- _version  number
- forced_refresh  boolean

```http request
DELETE /my-index-000001/_doc/1
```
```JSON
{
  "_shards": {
    "total": 2,
    "failed": 0,
    "successful": 2
  },
  "_index": "my-index-000001",
  "_id": "1",
  "_version": 2,
  "_primary_term": 1,
  "_seq_no": 5,
  "result": "deleted"
}
```

## Check a document 检查文档【是否存在】
格式
```http request
HEAD /{index}/_doc/{id}
```
检测文档是否存在，例如检查`_id`为0的文档是否存在
```http request
HEAD my-index-000001/_doc/0
```
如果文档存在就会返回状态码200，不存在返回状态码404

### Version support 版本控制
当且版本等于指定版本的时候才会返回  

在内部，Elasticsearch将旧的版本设置为已删除，并且添加一个全新的文档。旧文档的版本不会立即消失，尽管无法访问他。Elasticsearch会在后台清理已经删除的文档。

### Path parameter 路径参数
- index String  Required 以逗号分割的数据流，索引和别名列表。支持通配符（*）
- id String Required 文档的唯一标识

### Query parameter 查询参数
- preference String
应在哪个节点或分片上执行。默认情况在分片和副本之间随机。
如果设置为_local,则操作优先中本地分配的分片上执行。如果设置为自定义值，则该值用于确保相同的自定义值用于相同的分片，有助于在不同的刷新状态下访问不同分片时进行“跳跃值”操作。例如可以使用`web session ID`或者用户名。
- realtime boolean
  true的时候请求是实时的，而不是近实时的。
- refresh Boolean
  如果是`true`，会在请求检索文档之前刷新相关分片。需要考虑并确认这个操作不会给系统造成过重负载。
- routing String
  用于将操作路由到特定分片的自定义值
- _source Boolean | String | Array[String]
  标识返回是否包含`_source`字段（true或false）或列出要返回的字段
- _source_excludes String | Array[String]
  从响应中排除的源字段。也可以从`_source_includes`查询参数中指定的子集中排除字段。如果`_source`是`false`，就会忽略这个参数。
- _source_exclude_vectors Boolean 在9.2.0版本中添加
  是否应从`_source`排除向量
- _source_includes String,Array[String]
  要包含着响应中的源字段的列表。如果使用这个字段，就会仅返回这些源字段。也可以使用_source_excludes，在子集中继续排除，如果`_source`是`false`，就会忽略这个参数。
- stored_fields String|Array[String]
  以逗号分隔存储的字段列表，作为命中的一部分返回。如果没有指定字段，那么响应中不包含任何存储字段。如果指定了这个字段，则`_source`字段默认为`false`。使用`stored_fields`只能检索叶子字段。不能返回对象字段；如果指定对象字段就会请求失败。
- Version Number 版本号
  用于并发控制的版本号，当文档版本等于当前查询指定的版本，才能检索出文档
- version_type String
  值可以是
    - internal, 内部控制，从1开始，每次更新或删除时递增
    - external, 版本高于文档版本或者文档不存在的时候才能编辑文档
    - external_gte, 版本高于或等于文档版本或者文档不存在的时候才能编辑文档，需要谨慎使用，可能会导致数据丢失
    - force 已经弃用，因为可能导致 主分片和副本分片分离

### Response 响应
200

## Delete document 删除文档
格式
```http request
POST /{index}/_delete_by_query
```
删除指定查询匹配的文档

如果启用了Elasticsearch安全功能，必须对目标数据流、索引和别名具有以下索引权限
- read
- delete 或 write
可以使用与查询一样的语法在请求URI或者请求正文中指定查询条件。当提交通过查询删除文档的请求时，Elasticsearch会开始处理获取数据流或索引的快照，并使用内部版本控制删除匹配的文档。如果文档在快照和处理删除之间发生改变，则会导致版本冲突，并且删除失败。
> 注意版本等于0的文档无法使用“通过查询删除”删除，因为内部版本控制不支持0作为有效版本号

在处理删除查询请求时，Elasticsearch会按顺序执行多个搜索请求，以查找要删除的所有匹配文档。对每批匹配文档执行批量删除请求。如果搜索或批量删除请求被拒绝，则请求最多重试10次，并且重试的时间间隔会按照指数退避（exponential backoff）方式递增。如果达到最大重试次数，就会停止处理，并在响应中返回所有失败的请求。任何成功删除的请求仍会保留，不会回退。

你可以通过 `conflicts` 参数设置为 `proceed`，选择在遇到版本冲突（`version conflicts`）时继续执行并统计冲突数量，而不是立即停止并返回错误。如果选择计算版本冲突，那么这个删除操作可能会尝试从数据源删除的文档数会超过`max_docs`限制，直到成功删除了max_docs个文档或者已经遍历所有文档。

### Throttling delete requests 限制删除请求
如果要控制查询删除的批量删除请求的速率，可以把`requests_per_second`设置为任何正十进制数字。这会为每个批次填充等待时间以限制速率。将`requests_per_second`设置为`-1`可以禁用限制。

限制使用批处理之间的等待时间，以便可以为内部`scroll`请求提供一个超时，该超时将请求等待时间（`padding time`）考虑在内.填充时间是`batch size`除以`requests_per_second`与写入所花费的时间之间的差值。默认情况下，批量处理大小为1000条数据，如果将`requests_per_second`设置为500：
```
target_time = 1000 / 500 （per second = 2 seconds）
wait_time = target_time - write_time = 2 seconds - 0.5 seconds = 1.5 seconds
```
由于批次是作为单个`_bulk`,因此大批量会导致Elasticsearch创建许多请求，并且在开发下一组之前等待。这个是突发而不是平滑。

### Slicing 切片
按查询删除支持切片并滚动以并行化删除过程。这样可以提高效率，并提供一种将请求分解为更小部分的便捷方法。

将切片设置为`auto`,允许Elasticsearch选择要使用的切片（`slice`）数量。此设置将每个分片(shard)分配一个切片，但是有最大限制。如果有多个源数据流或索引，他将根据分片数量最少的索引或底层索引（`backing index`）来选择切片数量。将切片添加到“通过查询删除”作为创建子请求，因此他有一些特殊的行为。
- 可以在任务API中查看这些请求，这些子请求是具有切片的请求的任务的子任务
- 获取具有切片请求的任务状态仅包含已经完成的切片的状态
- 这些子请求（sub-requests）是可以单独访问/操作的，比如可以单独取消他们，或者重新调整他们的限速（rethrottling）
- 重新限流请求 `slices`将按比例重新限流未完成的子请求
- 取消`slices`将取消每个子请求
- 由于`slices`的性质，每个子请求不会得到完全均匀的文档分配，所有文档都将被处理，但是某些切片会比别的切片更大。预期较大的切片会有更均匀的分布。
- 在带有`slices`的请求中，参数 `requests_per_second`和 `max_doc`将按比例分配给每个子请求。结合之前关于分配可能不均匀这一点，你应该得出结论，使用`max_docs`和`slices`结合可能不能导致恰好删除 max_docs整个文档。
- 每个子请求都会得到data stream或索引略有不同的快照，尽管这些快照是在大约相同时间获取的。

如果你是手动切片或者以其他方式调整自动切片，需要注意下面几点
- 查询性能在切片数量等于索引或底层索引的分片数量的时候最高。如果数字很大（例如500），应该选择比较小的数字，因为过多的 `slices`会影响性能，将`slices`的数量设置为高于分片的数量的值通常不会提高效率，反而会增加额外开销。
- 删除性能随可用资源的切片数量线性提高

查询性能还是删除性能在运行时占主导地位，取决于重新索引的文档和集群资源

### Cancel a delete by query operation 取消删除查询操作
任何删除查询操作都可以通过API进行取消
```http request
POST _tasks/r1A2WoRbTwKZ516z6NEs5A:36619/_cancel
```
可以通过获取任务的API来找到任务ID.
取消操作应该迅速完成，但是可能需要几秒执行时间。获取任务状态的API会继续列出通过删除查询的任务，直达该任务检查到自己已经被取消并且自动终止。

### Required authorization 需要授权
- Index privileges： read、delete

### Path parameters 路径参数
- index String|Array[String]  Required

要搜索的数据流、索引和索引别名的逗号分割列表，支持通配符（`*`），要搜索所有数据流或索引，可以省略参数或使用`*`或者使用 `_all`

### Query parameters 查询参数
- allow_no_indices Boolean 
如果是`false`,当任何通配符表达式、索引别名或`_all`值仅针对缺失或已经关闭的索引时，，请求返回错误。即使请求针对其他开放索引，规则也适用。如果一个索引是以 `foo` 开头，但是没有以 `bar` 开头的索引，那么针对 `foo*,bar*` 请求将会返回错误.
- analyzer String 分析器
用于查询字符串的分析器，当且仅当指定了 `q`查询字符串参数时才可以使用。
-  analyze_wildcard Boolean
如果是 `true`则分析通配符和前缀查询。当且仅当指定了 `q`查询字符串参数时才可以使用。
  - conflicts String
  如果通过查询删除的时候遇见版本冲突该怎么办：`abort` 还是 `proceed`
  Supported values include 支持的值包括
    - abort：如果存在冲突，就停止重新索引
    - proceed： 即使纯真冲突也继续重新索引
- default_operator String
查询字符串默认运算符：`AND` 或 `OR` 。当且仅当指定了 `q`查询字符串参数时才可以使用。
- df String 当查询的字符串中为提供字段前缀时，用作默认字段的字段。当且仅当指定了 `q`查询字符串参数时才可以使用。
- expand_wildcards String ｜ Array[String] 通配符模式可以匹配的索引的类型。如果请求可以定位数据流。支持逗号分隔的值，eg `open,hidden`.支持的值包括：
  - all ： 匹配任何的数据流和索引，包含隐藏的数据流和索引
  - open： 匹配开放的非隐藏的索引和数据流
  - closed；匹配已关闭的非隐藏索引。也匹配任意非隐藏的数据流。数据流无法关闭。
  - hidden：匹配隐藏的数据流和隐藏的索引。必须与 `open`、`close`或 `both`结合使用
  - none: 不接受通配符表达式
- form Number 跳过指定数量的文档
- ignore_unavailable Boolean：忽略不可用，如果是`false`,当请求针对缺失或关闭的索引时，返回错误。
- lenient Boolean：如果是`true`,查询字符串基于格式的查询失败（例如，向数字字段提供文本）将被忽略。当且仅当指定了 `q`查询字符串参数时才可以使用。
- max_docs Number ：需要处理的最大文档数。默认所有文档。如果设置小于或等于`scroll_size`值，则不会使用滚动来检索操作的结果。
- preference String：执行操作的节点或分片，默认是随机的
- refresh Boolean：
  如果为 `true`，Elasticsearch会在请求完成后刷新`delete by`查询中涉及的所有分片。这个和delete API的refresh参数不同，后者仅刷新收到删除请求的分片。并且这里不支持 `wait_for`。
- request_cache Boolean： 如果是true，表示请求中使用请求缓存。默认是索引级别的设置。
- requests_per_second Number：每秒请求数量，请求的限制（以每秒子请求数量计算）
- routing String：用于将操作路由到特定分片的自定义值。
- q String：Lucene 查询字符串语法中的查询。
- scroll String：保留搜索上下文以进行滚动的时间段，可以是 -1 或 0 
- scroll_size Number：支持该操作的滚动请求的大小。
- search_timeout String：每次搜索请求的显式超时时间，默认无超时。可以为`0`或`-1`
- search_type String: 搜索操作的类型。可以选`query_then_fetch` 和 `dfs_query_then_fetch`
  -  query_then_fetch:文档的打分是基于分片内的本地词频和文档频率来计算的。这种方式通常更快，但准确性较低
  - dfs_query_then_fetch：使用所有分片中的全局词频和文档频率对文档进行评分。这种速度较慢，但更准确。
- slices Number｜String 切片数，可以为auto或数字（该任务应该划分的切片数）
- sort Array[String] ：以逗号分隔的 `<field>:<direction>`的列表
- stats Array[String]:用于记录和统计目的的请求的特定的`tag`
- terminate_after : 每个分片可收集的最大文档数。如果查询达到这个限制，Elasticsearch会提前终止查询。Elasticsearch会在排序之前收集文档。需要谨慎使用。Elasticsearch会将此参数应用与处理请求的每个分片。如果可能，请让Elasticsearch自动执行提前终止。如果请求的目标数据流包含跨很多歌数据层的支持索引，请避免使用这个参数。
- timeout String：每个删除请求等待活动分片的时间，可以为 `-1` 或 `0 `
- version Boolean:如果是`true`则返回文档版本作为匹配的一部分
- wait_for_active_shards Number|String
  继续操作之前必须等待至少多少个分片副本处于活动状态。可以设置为`all`或者任意正整数,最大是索引中分片副本数(`number_of_replicas+1`)。`timeout`值控制每个写入win各位iu放入哪个粉丝不可用分片的可用时间,值可以是 `all` 或 `index_setting`.
- wait_for_completion Boolean
如果是`true`,请求会被阻塞，直到操作完成。如果是 `false`,Elasticsearch会执行一些预检查，启动请求，并返回一个任务，可以使用该任务取消或获取其状态。Elasticsearch会在 .tasks/task/${taskId}中创建此任务的记录作为文档。完成任务后，可以删除这个任务文档，以便Elasticsearch回收空间。

### Body Required
- max_docs Number： 要删除的最大文档数
- query Object：定义Elasticsearch查询DSL对象
[参考文档](https://www.elastic.co/docs/explore-analyze/query-filter/languages/querydsl)
- slice Object
  - field String：字段路径或路径数组。某些API支持在路径中使用通配符来选择多个字段
  - id String：Required
  - max Number：Required

### Response
200
- batches Number：通过删除查询时，滚动查询（scroll）返回的响应数量
- deleted Number：成功删除的文档数量
- failures Array[object]: 如果在过程中出现任何不可恢复的错误，就会包含一系列的失败。如果数组不为空，那么请求由于这些失败而异常结束。通过查询删除是通过批量实现的，任何失败都会导致整个过程结束，但当前批次的全部失败都会被收集到该数组，可以使用 `conflict`选项来方式由于版本冲突而重新索引的结束。
  - cause Object Required：请求失败的成因和详细信息，定义了所有错误类型的共有属性，还提供了根据错误类型而变化的额外详细信息。
    - type String Required：错误类型
    - reason String ｜ Null
    - stack_trace String ：服务器堆栈跟踪。仅当请求中包含` error_trace=true`参数时才显示。
    - caused_by Object: 请求失败的成因和详细信息。此类定义了所有的错误类型共有的属性。还提供了根据错误类型而变化的额外详细信息。
    - root_cause Array｜Object：请求失败的成因和详细信息。此类定义了所有的错误类型共有的属性。还提供了根据错误类型而变化的额外详细信息。
    - suppressed Array[Object]: 请求失败的成因和详细信息。此类定义了所有的错误类型共有的属性。还提供了根据错误类型而变化的额外详细信息。
- id String Required
- index String Required
- status Number Required
- noops Number：通过查询删除，这个字段的值是0。仅存在以便通过查询删除、通过查询更新和重新索引API返回相同的结构响应。
- request_per_second Number：每秒请求数，通过查询删除期间每秒实际运行的请求数量
- retries Object：
  - bulk Number Required：重试的批量操作数量。
  - search Number Required：重试搜索操作的数量
- slice_id Number
- task String
- throttled String：一个持续时间。单位可以是 `nanos`、`micros`、`ms`、`s`、`m`、`h`和`d`。也可以使用没有单位的 `0` 和 `-1` 表示没有指定值。
- throttled_unit_millis Number: 
- timed_out Boolean: 如果是`true`一些删除查询操作期间运行的请求超时了
- took Number：毫秒的时间单位
- total Number：成功处理的文档数量
- version_conflicts Number：版本冲突数量

示例
删除所有文档
```http request
POST /my-index-000001,my-index-000002/_delete_by_query
{
  "query": {
    "match_all": {}
  }
}
```
删除一个文档
```http request
POST /my-index-000001,my-index-000002/_delete_by_query
{
  "query": {
    "term": {
      "user.id": "kimchy"
    }
  },
  "max_docs": 1
}
```
手动切片
```http request
POST /my-index-000001,my-index-000002/_delete_by_query
{
  "slice": {
    "id": 0,
    "max": 2
  },
  "query": {
    "range": {
      "http.response.bytes": {
        "lt": 2000000
      }
    }
  }
}
```
自动切片
````http request
POST my-index-000001/_delete_by_query?refresh&slices=5
{
  "query": {
    "range": {
      "http.response.bytes": {
        "lt": 2000000
      }
    }
  }
}
````

响应
```http request
{
  "took" : 147,
  "timed_out": false,
  "total": 119,
  "deleted": 119,
  "batches": 1,
  "version_conflicts": 0,
  "noops": 0,
  "retries": {
    "bulk": 0,
    "search": 0
  },
  "throttled_millis": 0,
  "requests_per_second": -1.0,
  "throttled_until_millis": 0,
  "failures" : [ ]
}
```

## Throttle a deleted by query operation 限制删除查询操作
格式
```http request
POST /_delete_by_query/{task_id}/_rethrottle
```
更改删除查询请求数量修改，重新限流加速查询立即生效，而重新限流减速查询在完成当前批次之后生效，防止滚动超时。

### Path parameters 路径参数
- task_id String Required

### Query parameters 
- requests_per_second Number:请求的速率限制，以每秒的子请求数表示。如果要禁用速率限制可以设置为`-1`

### Response 
200
- node_failures Array[Object]
请求失败的详细信息。此类定义了所有错误类型共有的属性。此外，还提供了根据错误类型而变化的额外详细信息。
    - type String Required：错误类型
    - reason String ｜ Null
    - stack_trace String ：服务器堆栈跟踪。仅当请求中包含` error_trace=true`参数时才显示。
    - caused_by Object: 请求失败的成因和详细信息。此类定义了所有的错误类型共有的属性。还提供了根据错误类型而变化的额外详细信息。
    - root_cause Array｜Object：请求失败的成因和详细信息。此类定义了所有的错误类型共有的属性。还提供了根据错误类型而变化的额外详细信息。
    - suppressed Array[Object]: 请求失败的成因和详细信息。此类定义了所有的错误类型共有的属性。还提供了根据错误类型而变化的额外详细信息。
- task_failures  Array[Object]
  - task_id Number Required 
  - node_id String Required
  - status String Required
  - type String Required：错误类型
  - reason String ｜ Null
  - stack_trace String ：服务器堆栈跟踪。仅当请求中包含` error_trace=true`参数时才显示。
  - caused_by Object: 请求失败的成因和详细信息。此类定义了所有的错误类型共有的属性。还提供了根据错误类型而变化的额外详细信息。
  - root_cause Array｜Object：请求失败的成因和详细信息。此类定义了所有的错误类型共有的属性。还提供了根据错误类型而变化的额外详细信息。
  - suppressed Array[Object]: 请求失败的成因和详细信息。此类定义了所有的错误类型共有的属性。还提供了根据错误类型而变化的额外详细信息。
- nodes  Object: 节点按任务分组，如果 `group by` 设置为 `node` （默认值）
  - name String
  - transport_address String
  - host String 主机
  - ip String
  - roles Array[String] 
  - attribute Object
  - tasks Object Required
    - action String Object
    - cancelled Boolean
    - cancellable Boolean Required
    - description String: 可读文本，用于表示任务正在执行的搜索请求。例如 可能表示搜索任务正在执行的搜索请求。不同类型的任务有不同的描述。例如 `_reindex` 包含源和目标。或 `_bulk`仅包含请求数量和目标索引。但是有很多请求是空的描述，有些请求的描述信息比较难获得且没有什么帮助。
    - headers Object Required
    - id Number String
    - node String Required
    - running_time String 运行时间 一个持续时间。单位可以是 `nanos` 、 `micros` 、 `ms` (毫秒)、 `s` (秒)、 `m` (分钟)、 `h` (小时) 和 `d` (天)。也接受没有单位的 "`0`" 和表示未指定值的 "`-1`"。
    - running_time_in_nanos Number 运行时间的纳秒数
    - start_time_in_millis Number 毫秒时间
    - status Object 任务内部的当前状态，不同任务的状态可能不同。 格式也可能有所不同。 虽然目标是保持特定任务的状态在版本之间保持一致，但这并不总是可能的，因为有时实现方式会发生变化。 对于特定请求的状态，字段可能会被移除，因此你在状态上的任何解析在次要版本中可能会失效。
    - type String Required
    - parent_task_id String
  - tasks Array[Object] | Object
    - action String Object
      - cancelled Boolean
      - cancellable Boolean Required
      - description String: 可读文本，用于表示任务正在执行的搜索请求。例如 可能表示搜索任务正在执行的搜索请求。不同类型的任务有不同的描述。例如 `_reindex` 包含源和目标。或 `_bulk`仅包含请求数量和目标索引。但是有很多请求是空的描述，有些请求的描述信息比较难获得且没有什么帮助。
      - headers Object Required
      - id Number String
      - node String Required
      - running_time String 运行时间 一个持续时间。单位可以是 `nanos` 、 `micros` 、 `ms` (毫秒)、 `s` (秒)、 `m` (分钟)、 `h` (小时) 和 `d` (天)。也接受没有单位的 "`0`" 和表示未指定值的 "`-1`"。
      - running_time_in_nanos Number 运行时间的纳秒数
      - start_time_in_millis Number 毫秒时间
      - status Object 任务内部的当前状态，不同任务的状态可能不同。 格式也可能有所不同。 虽然目标是保持特定任务的状态在版本之间保持一致，但这并不总是可能的，因为有时实现方式会发生变化。 对于特定请求的状态，字段可能会被移除，因此你在状态上的任何解析在次要版本中可能会失效。
      - type String Required
      - parent_task_id String

## Get a document‘s source 获取文档源
格式
```http request
GET /{index}/_source/{id}
```
可以使用源过滤参数来控制返回 `_source` 的哪些部分
```http request
GET my-index-000001/_source/1/?_source_includes=*.id&_source_excludes=entities
```
[_source 字段说明](#_source-字段说明)

### Path parameters 路径参数
- index String Required
- id String Required

### Query parameters 查询参数
- preference String 首选项
  应该在哪个节点或分片上执行，默认再分片和副本间随机变化
  如果设置为_local,则操作优先中本地分配的分片上执行。如果设置为自定义值，则该值用于确保相同的自定义值用于相同的分片，有助于在不同的刷新状态下访问不同分片时进行“跳跃值”操作。例如可以使用`web session ID`或者用户名。
- realtime boolean
  true的时候请求是实时的，而不是近实时的。
- refresh Boolean
  如果是`true`，会在请求检索文档之前刷新相关分片。需要考虑并确认这个操作不会给系统造成过重负载。
- routing String
  用于将操作路由到特定分片的自定义值
- _source Boolean | String | Array[String]
  标识返回是否包含`_source`字段（true或false）或列出要返回的字段
- _source_excludes String | Array[String]
  从响应中排除的源字段。也可以从`_source_includes`查询参数中指定的子集中排除字段。如果`_source`是`false`，就会忽略这个参数。
- _source_exclude_vectors Boolean 在9.2.0版本中添加
  是否应从`_source`排除向量
- _source_includes String,Array[String]
  要包含着响应中的源字段的列表。如果使用这个字段，就会仅返回这些源字段。也可以使用_source_excludes，在子集中继续排除，如果`_source`是`false`，就会忽略这个参数。
- stored_fields String|Array[String]
  以逗号分隔存储的字段列表，作为命中的一部分返回。如果没有指定字段，那么响应中不包含任何存储字段。如果指定了这个字段，则`_source`字段默认为`false`。使用`stored_fields`只能检索叶子字段。不能返回对象字段；如果指定对象字段就会请求失败。
- version Number 版本号
  用于并发控制的版本号，当文档版本等于当前查询指定的版本，才能检索出文档
- version_type String
  值可以是
    - internal, 内部控制，从1开始，每次更新或删除时递增
    - external, 版本高于文档版本或者文档不存在的时候才能编辑文档
    - external_gte, 版本高于或等于文档版本或者文档不存在的时候才能编辑文档，需要谨慎使用，可能会导致数据丢失
    - force 已经弃用，因为可能导致 主分片和副本分片分离

#### Responses
200

## Check for a document source
格式
```http request
HEAD /{index}/_source/{id}
```
检查文档源是否存在索引中
```http request
HEAD my-index-000001/_source/1
```
如果文档在映射中禁用，则其源不可用。


[_source 字段说明](#_source-字段说明)



# Query DSL
[Query DSL](https://www.elastic.co/docs/explore-analyze/query-filter/languages/querydsl)
## 什么是 Query DSL
是一种功能齐全的JSON样式的查询语言，支持复杂的搜索、过滤和聚合操作。他是Elasticsearch目前最原始最强大的查询语言。


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



# 其他

[mapping-source-field](https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/mapping-source-field)
## _source 字段说明
`_source` 字段包含在索引时传递的原始json文档正文。`_source` 字段本身不会被索引（因此不可搜索），但他被存储起来，以便在执行获取请求（如 `get` 或 `search` ）时返回.
如果关心磁盘使用情况，可以考虑下面的选项：
- 使用 `synthetic _source`,他在检索时，重建源内容，而不是将其存储在磁盘上。这样会减少磁盘使用，但是会降低 `Get` 和 `Search` 查询中对 `_source` 的访问速度。
- 完全禁用 `_source` 字段。这回减少磁盘使用，但会禁用依赖 `_source` 的功能。

### Synthetic _source
虽然很方便，但源字段中磁盘上占用了大量空间。Elasticsearch不是将源文档按发送时的样子存储在磁盘上，而是在检索时动态重建内容，要启用此订阅功能，请将索引设置 `index.mapping.source.mode` 的 值设置为 `synthetic`：
```http request
PUT idx
{
  "settings": {
    "index": {
      "mapping": {
        "source": {
          "mode": "synthetic"
        }
      }
    }
  }
}
```
虽然这种动态重建通常比按原样保存源文档并在查询时加载它们要慢，但节省了大量存储空间，在不需要时，通常不在查询中加载 _source 字段，可以避免额外的延迟。

#### Supported fields 支持的字段
Synthetic `_source` 所有类型的字段都是支持。根据实现细节，不同的字段类型中使用 Synthetic `_source` 具有不同的属性。

大多数字段类型使用相同的数据构造合成 `_source` ,最常见的是 `doc_values` 和存储字段。对于这些字段类型， 不需要额外的空间来存储 `_source` 字段的值。由于 `doc_values` 的存储布局，生成的 `_source` 字段和原始文档会发生变化。

对于所有其他字段类型，字段的原始值会“原样”存储，就像在非合成（`non-synthetic`）模式下的 `_source` 字段一样。
在这种情况下，不会进行任何修改，`_source` 中的字段数据与原始文档中的数据完全一致。
类似地，那些使用了 `ignore_malformed`（忽略格式错误）或 `ignore_above`（忽略过长值）的字段，其格式错误或被忽略的值也必须原样存储。
这种方式的缺点是存储效率比较低，因为为了能重建 `_source`，需要额外保存一份字段的原始数据，而索引字段时本身还需要保存其他数据（比如 `doc_values`），导致同一份信息在不同地方重复存储。

#### Synthetic _source restrictions 合成 _source 限制

#### Synthetic _source modifications 合成 _source 修改
当启用合成 `_source` 时，检索到的文档与原始 JSON 相比会进行一些修改。

#### Arrays moved to leaf fields 数组已经移动到叶子结点

```http request
PUT idx/_doc/1
{
  "foo": [
    {
      "bar": 1
    },
    {
      "bar": 2
    }
  ]
}
```
会变成
```json
{
  "foo": {
    "bar": [1, 2]
  }
}
```
这可能会导致某些数组消失：
```http request
PUT idx/_doc/1
{
  "foo": [
    {
      "bar": 1
    },
    {
      "baz": 2
    }
  ]
}
```
将会变为：
```json
{
  "foo": {
    "bar": 1,
    "baz": 2
  }
}
```
#### Fields named as they are mapped 字段按其映射命名
按映射中的名称创建合成源字段。在使用动态映射时，字段名中包含点（ . ）默认被视为多个对象，而字段名中的点在禁用 `subobjects` 的对象中会被保留。例如：
```http request
PUT idx/_doc/1
{
  "foo.bar.baz": 1
}
```
会变为
```json
{
  "foo": {
    "bar": {
      "baz": 1
    }
  }
}
```
这会影响在脚本中如何引用源内容。例如，以脚本原始源形式引用脚本将返回 null：
```shell
"script": { "source": """  emit(params._source['foo.bar.baz'])  """ }
```
相反，源引用需要与映射结构保持一致：
```shell
"script": { "source": """  emit(params._source['foo']['bar']['baz'])  """ }
```
或者
```shell
"script": { "source": """  emit(params._source.foo.bar.baz)  """ }
```
以下字段 API 更可取，因为它们不仅对映射结构保持中立，而且如果可用会使用 docvalues，并且仅在需要时才回退到合成源。这减少了源合成，这是一个缓慢且昂贵的操作。
```shell
"script": { "source": """  emit(field('foo.bar.baz').get(null))   """ }
"script": { "source": """  emit($('foo.bar.baz', null))   """ }
```

#### Alphabetical sorting 字母排序
合成 `_source` 字段按字母顺序排序。JSON RFC 将对象定义为“零个或多个名称/值对的无序集合”，因此应用程序不应关心，但如果没有合成 `_source` ，原始顺序将被保留，并且某些应用程序可能会与规范相悖，根据该顺序执行某些操作。

#### Representation of ranges
范围字段值（例如`long_range`）始终以包含两边的方式表示

#### Reduced precision of `geo_point` values 精度降低
`geo_point` 字段的值以合成 `_source` 的形式表示，精度降低。

#### Minimizing source modifications
可以避免对特定对象或字段进行合成源代码修改，但这需要额外的存储成本。这通过参数 `synthetic_source_keep` 进行控制，具有以下选项：
- none: 源代码与上述原始源代码不同（默认）。
- arrays: 字段或对象的数组保留原始元素顺序和重复元素。对于此类数组，合成源代码片段不一定能完全匹配原始源代码，例如数组 `[1, 2, [5], [[4, [3]]], 5]` 可能以原样或等效格式（如 `[1, 2, 5, 4, 3, 5] `）出现。未来可能会更改确切格式，以减少此选项的存储开销。
- all : 单例实例和相应字段或对象的数组源都会被记录。应用于对象时，所有子对象和子字段的源都会被捕获。此外，数组的原始源也会被捕获，并以合成源的形式出现，且无修改。

```http request
PUT idx_keep
{
  "settings": {
    "index": {
      "mapping": {
        "source": {
          "mode": "synthetic"
        }
      }
    }
  },
  "mappings": {
    "properties": {
      "path": {
        "type": "object",
        "synthetic_source_keep": "all"
      },
      "ids": {
        "type": "integer",
        "synthetic_source_keep": "arrays"
      }
    }
  }
}
```

```http request
PUT idx_keep/_doc/1
{
  "path": {
    "to": [
      { "foo": [3, 2, 1] },
      { "foo": [30, 20, 10] }
    ],
    "bar": "baz"
  },
  "ids": [ 200, 100, 300, 100 ]
}
```
返回原始源，无数组去重和排序：
```json
{
  "path": {
    "to": [
      { "foo": [3, 2, 1] },
      { "foo": [30, 20, 10] }
    ],
    "bar": "baz"
  },
  "ids": [ 200, 100, 300, 100 ]
}
```
捕获数组源的选择可以在索引级别应用，通过将 `index.mapping.synthetic_source_keep` 设置为 `arrays` 。这适用于索引中的所有对象和字段，除了那些 `synthetic_source_keep` 设置为 `none` 的显式覆盖项。在这种情况下，存储开销会随着每个文档源中数组数量和大小而增长，这是自然的。
#### Field types that support synthetic source with no storage overhead
以下字段类型使用 `doc_values` 或存储字段的数据支持合成源，构建 `_source` 字段时无需额外的存储空间。
不进行详细介绍了

- aggregate_metric_double
- annotated-text
- binary
- boolean
- byte
- date
- date_nanos
- dense_vector
- double
- flattened
- float
- geo_point
- half_float
- histogram
- integer
- ip
- keyword
- long
- rang types
- scaled_float
- short
- text
- version
- wildcard

#### Disabling the _source field 禁用 _source 字段
尽管它非常方便，但源字段确实会在索引中产生存储开销。因此，可以按照以下方式禁用它：
```http request
PUT my-index-000001
{
  "mappings": {
    "_source": {
      "enabled": false
    }
  }
}
```
> 注意： 不要禁用 `_source` 字段，除非绝对必要。如果你禁用它，以下关键功能将不受支持：
> - `update` 、 `update_by_query` 和 `reindex` API。
> - 在 Kibana Discover 应用中显示字段数据。
> - 动态高亮显示
> - 从其中一个 Elasticsearch 索引重新索引到另一个索引的能力，无论是更改映射或分析，还是将索引升级到新的大版本。
> - 通过查看索引时使用的原始文档来调试查询或聚合的能力。
> - 未来可能具备自动修复索引损坏的能力。

> 注意 您不能禁用字段 `_source` ，当索引的 `index_mode` 设置为 `logsdb` 或 `time_series` 时。

> 如果磁盘空间是问题，最好增加压缩级别而不是禁用 _source 。

#### Including / Excluding fields from _source 包含或者排除 _source 字段
> 从 _source 中移除字段与禁用 `_source` 类似，都有类似的缺点，尤其是你无法从一个 Elasticsearch 索引重新索引文档到另一个索引。考虑使用源过滤代替。

includes / excludes 参数（也接受通配符）可以按如下方式使用：

```http request
PUT logs
{
  "mappings": {
    "_source": {
      "includes": [
        "*.count",
        "meta.*"
      ],
      "excludes": [
        "meta.description",
        "meta.other.*"
      ]
    }
  }
}
```
```http request
PUT logs/_doc/1
{
  "requests": {
    "count": 10,
    "foo": "bar"  (i)
  },
  "meta": {
    "name": "Some metric", 
    "description": "Some metric description",  (i)
    "other": {
      "foo": "one",  (i)
      "baz": "two"   (i)
    }
  }
}
```

```http request
GET logs/_search
{
  "query": {
    "match": {
      "meta.other.foo": "one"   (ii)
    }
  }
}
```
(i) 这些字段将从存储的 _source 字段中移除。
(ii)即使它不在存储的 _source 中，我们仍然可以在这个字段上搜索。





