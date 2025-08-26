
@[TOC](java并发)

# 1. ExecutorService

ExecutorServices 是 java.util.concurrent 包重要的组成部分，是java JDK提供的简化异步模式下任务执行的框架。一般情况下 ExecutorServices 会自动提供一个线程池和相关 API，用来分配任务。

## 实例化 ExecutorService
方式有两种：工厂方法和直接创建

### Executors.newFixedThreadPool() 工厂方法创建 ExecutorService 实例
Executors 提供了多种创建 ExecutorService 的工厂方法，例如
```java
ExecutorService executor = Executors.newFixedThreadPool(10);

ExecutorService executor = Executors.newSingleThreadExecutor();

ExecutorService executor = Executors.newCachedThreadPool();

ExecutorService executor = Executors.newWorkStealingPool();
```
特点和场景
newFixedThreadPool：
- 固定大小线程池
- 当所有线程都在执行的时候，新任务进入无界队列
