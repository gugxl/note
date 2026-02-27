# Article Saver Skill

自动整理微信收藏文章为标准化笔记的知识库管理工具。

## 功能特性

- ✅ **自动分类**: 根据关键词自动分类到8大类（AI/ML、前端、后端、DevOps等）
- ✅ **标签提取**: 自动提取技术关键词作为标签
- ✅ **标准化模板**: 统一笔记格式，便于查阅
- ✅ **索引管理**: 自动维护文章索引，支持搜索
- ✅ **批量处理**: 支持批量导入多个链接
- ✅ **统计报表**: 生成知识库统计信息

## 目录结构

```
skills/article-saver/
├── config.json              # 配置文件
├── templates/
│   └── note-template.md     # 笔记模板
├── scripts/
│   └── batch_processor.py   # 批量处理脚本
├── data/
│   └── index.json           # 文章索引
└── README.md                # 本文件

notes/                       # 生成的笔记存放处
├── 01-AI-ML/               # AI/机器学习
├── 02-Frontend/            # 前端开发
├── 03-Backend/             # 后端开发
├── 04-DevOps/              # DevOps/运维
├── 05-Architecture/        # 架构设计
├── 06-Algorithm/           # 算法
├── 07-Career/              # 职业发展
└── 08-Others/              # 其他
```

## 快速开始

### 1. 安装依赖

确保已安装Python 3.7+

```bash
# 无需额外依赖，使用标准库
```

### 2. 批量处理文章

#### 方式A：从文件读取URL列表

1. 创建一个文本文件 `urls.txt`:
```
https://mp.weixin.qq.com/s/xxx
https://mp.weixin.qq.com/s/yyy
https://mp.weixin.qq.com/s/zzz
```

2. 运行脚本:
```bash
cd ai
python skills/article-saver/scripts/batch_processor.py process urls.txt
```

#### 方式B：交互式输入

```bash
python skills/article-saver/scripts/batch_processor.py process
# 然后按提示输入URL，空行结束
```

### 3. 查看整理好的笔记

```bash
# 列出所有文章
python skills/article-saver/scripts/batch_processor.py list

# 列出特定分类的文章
python skills/article-saver/scripts/batch_processor.py list AI-ML

# 搜索文章
python skills/article-saver/scripts/batch_processor.py search Transformer

# 查看统计
python skills/article-saver/scripts/batch_processor.py stats
```

## 配置说明

编辑 `skills/article-saver/config.json` 可以自定义：

### 修改分类规则

```json
"categories": {
  "AI-ML": {
    "keywords": ["Transformer", "深度学习", "GPT", "BERT"],
    "path": "notes/01-AI-ML"
  },
  "Your-Category": {
    "keywords": ["关键词1", "关键词2"],
    "path": "notes/09-Your-Category"
  }
}
```

### 修改笔记模板

编辑 `skills/article-saver/templates/note-template.md`，可用占位符：

- `{{title}}` - 文章标题
- `{{source_url}}` - 原文链接
- `{{author}}` - 作者
- `{{category}}` - 分类
- `{{tags}}` - 标签
- `{{summary}}` - 总结
- `{{content}}` - 正文
- `{{save_date}}` - 保存日期

## 使用流程

### 完整工作流程

```
1. 收集文章
   └─ 在微信PC版中右键文章 → 在浏览器中打开 → 复制URL

2. 批量处理
   └─ 将所有URL保存到 urls.txt
   └─ 运行: python batch_processor.py process urls.txt

3. 人工整理（关键步骤）
   └─ 打开生成的笔记文件
   └─ 补充总结、要点、个人思考
   └─ 保存

4. 知识库管理
   └─ 使用 list/search/stats 命令管理笔记
```

### 实际使用示例

**Step 1**: 收集5篇文章的URL
```
https://mp.weixin.qq.com/s/SGROkMleCiV6iPI7kNlXOA
https://mp.weixin.qq.com/s/7MjBJlczIxElTDrMh7yriQ
https://mp.weixin.qq.com/s/_ejGvrYENb3kGzmYlKAVrw
```

**Step 2**: 批量处理
```bash
python skills/article-saver/scripts/batch_processor.py process
# 粘贴3个URL，然后空行结束
```

**Step 3**: 查看结果
```bash
python skills/article-saver/scripts/batch_processor.py list
```

输出:
```
📁 AI-ML (3篇)
  • Visual Transformer 大白话笔记
    标签: Transformer, 深度学习
    文件: notes/01-AI-ML/20260214-Visual-Transformer.md
  ...
```

## 注意事项

1. **自动分类基于关键词匹配**，可能不完全准确，建议手动检查
2. **内容需要人工整理**，脚本只创建框架，核心内容需要你自己填充
3. **定期备份** `data/index.json` 文件，这是知识库的索引

## 扩展计划

未来可以添加的功能：

- [ ] Web界面浏览知识库
- [ ] 自动抓取文章内容（配合爬虫）
- [ ] 导出为PDF/EPUB
- [ ] 阅读进度跟踪
- [ ] 文章推荐（基于标签相似度）
- [ ] 定时同步微信收藏

## 与AI助手配合使用

当前最佳实践：

```
1. 你: 收集文章URL → 保存到 urls.txt

2. 你: 发送给AI助手
   "请帮我整理这些文章"
   [粘贴urls.txt内容]

3. AI: 读取文章 → 按模板整理 → 生成笔记文件
   → 保存到对应分类目录

4. AI: 返回整理好的文件路径和简要说明

5. 你: 查看笔记，补充个人思考
```

## 文件说明

- `config.json` - 技能配置文件
- `note-template.md` - 笔记模板，可自定义格式
- `batch_processor.py` - 核心处理脚本
- `index.json` - 自动生成的文章索引

---

**创建时间**: 2026-02-14  
**版本**: 1.0.0  
**作者**: User + AI Assistant
