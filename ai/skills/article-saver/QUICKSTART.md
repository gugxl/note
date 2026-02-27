# Article Saver Skill - 快速开始指南

## 30秒上手

### 方式1: 直接给我链接（最简单）

```
你: /save-articles
    https://mp.weixin.qq.com/s/xxx
    https://mp.weixin.qq.com/s/yyy
    
AI: 好的，我来处理这些文章...
    ✅ 已保存3篇文章:
       - notes/01-AI-ML/xxx.md
       - notes/02-Frontend/yyy.md
       - ...
```

### 方式2: 使用Python脚本

```bash
# 1. 创建URL列表
echo "https://mp.weixin.qq.com/s/xxx" > urls.txt
echo "https://mp.weixin.qq.com/s/yyy" >> urls.txt

# 2. 批量处理
cd ai
python skills/article-saver/scripts/batch_processor.py process urls.txt

# 3. 查看结果
python skills/article-saver/scripts/batch_processor.py list
```

## 常用命令

```bash
# 列出所有文章
python skills/article-saver/scripts/batch_processor.py list

# 列出AI分类的文章  
python skills/article-saver/scripts/batch_processor.py list AI-ML

# 搜索Transformer相关文章
python skills/article-saver/scripts/batch_processor.py search Transformer

# 查看统计
python skills/article-saver/scripts/batch_processor.py stats
```

## 工作流建议

### 每日整理流程

```
1. 微信收藏 → 复制文章链接
2. 粘贴给AI: "帮我整理今天的收藏"
3. AI生成笔记 → 保存到对应目录
4. 你查看笔记，补充个人思考
5. 定期回顾和复习
```

### 批量整理流程

```
1. 积累10-20篇文章链接
2. 一次性发给AI批量处理
3. 按分类查看生成的笔记
4. 选择重要的深入整理
5. 生成周/月学习总结
```

## 分类说明

| 目录 | 内容 |
|------|------|
| 01-AI-ML | Transformer, 深度学习, GPT, BERT等 |
| 02-Frontend | React, Vue, JavaScript, CSS等 |
| 03-Backend | Java, Python, Go, 数据库等 |
| 04-DevOps | Docker, K8s, CI/CD, Linux等 |
| 05-Architecture | 系统设计, 分布式, 微服务等 |
| 06-Algorithm | 算法, 数据结构, LeetCode等 |
| 07-Career | 面试, 职业规划, 成长等 |
| 08-Others | 其他未分类内容 |

## 笔记模板说明

每篇笔记包含以下章节:

1. **一句话总结** - 快速理解核心
2. **核心要点** - 重点提取
3. **详细内容** - 完整笔记
4. **代码示例** - 可运行代码
5. **个人思考** - 你的理解和感悟

## 下一步

现在你可以:

1. **测试**: 给我1-3个微信文章链接，我演示完整流程
2. **配置**: 修改 `config.json` 添加你感兴趣的分类
3. **模板**: 自定义 `templates/note-template.md` 格式
4. **导入**: 批量处理你现有的收藏文章

准备好开始了吗？给我几个链接试试吧！
