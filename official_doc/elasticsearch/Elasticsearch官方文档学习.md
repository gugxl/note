# 序

文档说明
[8.6官方文档](https://www.elastic.co/guide/en/elasticsearch/reference/8.6/elasticsearch-intro.html)
[最新版本](https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html)


单机模式: [docker compose搭建elk 8.6.2](https://blog.csdn.net/zhazhagu/article/details/148619309)
集群模式:[使用docker compose 部署Elasticsearch 9.0.4集群 + kinaba](https://blog.csdn.net/zhazhagu/article/details/149809217)

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
在单个请求中执行多个 index、create、delete 或 update 操作,可以减少开销,提高索引速度.

