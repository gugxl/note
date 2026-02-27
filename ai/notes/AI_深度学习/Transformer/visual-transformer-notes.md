# Visual Transformer 大白话笔记

> **原文**: [A Survey on Visual Transformer及引文理解](https://mp.weixin.qq.com/s/SGROkMleCiV6iPI7kNlXOA)  
> **整理时间**: 2026-02-14  
> **难度**: 零基础友好 ⭐

---

## 📌 一句话总结

**Transformer**（最初用于处理文字的AI模型）被应用到**图像和视频**领域，用"全局视角"替代了传统的"局部扫描"方法，正在成为视觉AI的新标准。

---

## 🎯 为什么要学这个？

```mermaid
graph LR
    A[传统CNN] -->|局部扫描| B[一点一点看图片]
    C[Transformer] -->|全局视角| D[一眼看清全图]
    B --> E[可能遗漏远距离关系]
    D --> F[猫头和猫尾自动关联]
    
    style C fill:#e1f5e1,stroke:#333
    style F fill:#fff3cd,stroke:#333
```

| 对比项 | CNN（传统） | Transformer（新方法） |
|--------|------------|---------------------|
| **看图片方式** | 像"近视眼"，3×3小窗口滑动 | 像"全局视角"，一眼看全图 |
| **捕捉关系** | 只能看附近像素 | 远距离像素也能直接关联 |
| **计算方式** | 顺序计算，较慢 | 并行计算，更快 |
| **需要数据** | 较少（有先验知识） | 较多（从零学习） |
| **计算量** | 较小 | 较大（30倍左右） |

---

## 🧩 核心概念详解

### 1. Self-Attention（自注意力）- 就是"联想能力"

#### 生活化理解

想象你在看这句话：**"张三把苹果给了李四"**

读到"苹果"时，你的大脑会自动联想：
- 前面是"张三"（谁给的）
- 后面是"给了李四"（给谁的）
- 所以这里的"苹果"是**水果**，不是手机！

**Self-Attention 就是让 AI 拥有这种联想能力。**

```mermaid
graph TD
    A[输入: 苹果] --> B{Query: 这是什么?}
    B --> C[问张三: 你是谁?]
    B --> D[问把: 你是什么?]
    B --> E[问给了: 什么动作?]
    B --> F[问李四: 你是谁?]
    
    C -->|我是主语 相关度0.3| G[加权整合]
    D -->|我是介词 相关度0.2| G
    E -->|我是给予 相关度0.8| G
    F -->|我是接收者 相关度0.6| G
    
    G --> H[输出: 苹果是水果!]
    
    style E fill:#ff9999,stroke:#333
    style H fill:#90EE90,stroke:#333
```

#### 在图片里怎么算？

```mermaid
graph TB
    subgraph "图片切成9块"
        A1[天空1] --- A2[天空2] --- A3[天空3]
        B1[猫咪4] --- B2[猫咪5] --- B3[猫咪6]
        C1[草地7] --- C2[草地8] --- C3[草地9]
    end
    
    subgraph "计算猫咪5的注意力"
        D[猫咪5的Query] --> E{问其他所有块}
        E -->|相关度0.9| F[猫咪4]
        E -->|相关度0.9| G[猫咪6]
        E -->|相关度0.3| H[天空2]
        E -->|相关度0.2| I[草地8]
    end
    
    F -.-> J[整合特征]
    G -.-> J
    H -.-> J
    I -.-> J
    
    J --> K[猫咪5知道: 我是猫的一部分!]
    
    style D fill:#e1f5e1,stroke:#333
    style K fill:#fff3cd,stroke:#333
```

**计算过程（简化版）：**

```
每个词/像素 都有三个身份：
┌─────────────────────────────────────┐
│  Query (Q) : 我有什么问题？         │
│  Key   (K) : 我是谁？               │
│  Value (V) : 我有什么信息？          │
└─────────────────────────────────────┘

计算步骤：
1. Q × K^T = 相关度分数  （谁和谁有关系？）
2. 归一化 (Softmax)      （变成概率）
3. × V = 加权求和         （整合信息）
```

---

### 2. 位置编码 - 给每个像素一个"地址"

#### 问题：Transformer 天生不知道顺序！

```mermaid
graph LR
    A[张三打了李四] --> B[Transformer眼中]
    C[李四打了张三] --> B
    B --> D[都是: 张三/李四/打 三个词]
    D --> E[分不清谁打谁!]
    
    style E fill:#ff9999,stroke:#333
```

#### 解决方案：加座位号

```mermaid
graph TB
    subgraph "原始输入（不知道位置）"
        A1[张三] --- A2[打了] --- A3[李四]
    end
    
    subgraph "加上位置编码后"
        B1[张三+位置1] --- B2[打了+位置2] --- B3[李四+位置3]
    end
    
    subgraph "现在模型知道"
        C1[位置1是主语] 
        C2[位置2是谓语] 
        C3[位置3是宾语]
    end
    
    B1 --> C1
    B2 --> C2
    B3 --> C3
    
    style B1 fill:#e1f5e1,stroke:#333
    style B2 fill:#e1f5e1,stroke:#333
    style B3 fill:#e1f5e1,stroke:#333
```

**图片的位置编码：**

```mermaid
graph TB
    subgraph "224×224 图片切成14×14网格"
        direction LR
        P00[0,0] --- P01[0,1] --- P02[0,2] --- P0n[...,] --- P013[0,13]
        P10[1,0] --- P11[1,1] --- P12[1,2] --- P1n[...,] --- P113[1,13]
        Pn0[...] --- Pn1[...] --- Pn2[...] --- Pnn[...] --- Pn13[...]
        P130[13,0] --- P131[13,1] --- P132[13,2] --- P13n[...,] --- P1313[13,13]
    end
    
    Note[每个格子有两个坐标: x和y<br/>模型就知道谁在哪，谁挨着谁]
    
    style P11 fill:#fff3cd,stroke:#333
    style P12 fill:#fff3cd,stroke:#333
    style P11 fill:#90EE90,stroke:#333
```

---

### 3. Multi-Head Attention（多头注意力）

#### 类比：多人多角度讨论

```mermaid
graph TB
    A[项目讨论会] --> B[头1: 技术视角]
    A --> C[头2: 成本视角]
    A --> D[头3: 市场视角]
    A --> E[头4: 风险视角]
    
    B -->|这个能做| F[综合决策]
    C -->|要花100万| F
    D -->|用户需要| F
    E -->|有风险| F
    
    F --> G[最终决定: 值得做!]
    
    style F fill:#90EE90,stroke:#333
```

#### 在 Transformer 里

```mermaid
graph LR
    A[输入特征<br/>768维] --> B{切成8个头}
    
    B --> C[头1: 96维<br/>看语法]
    B --> D[头2: 96维<br/>看语义]
    B --> E[头3: 96维<br/>看位置]
    B --> F[头4-8: ...]
    
    C --> G[拼接结果]
    D --> G
    E --> G
    F --> G
    
    G --> H[输出特征<br/>768维]
    
    style G fill:#e1f5e1,stroke:#333
```

**为什么需要多头？**

```
单头只能发现一种关系：
- 只看到"猫"和"坐"有关系（动作）

多头能发现多种关系：
- 头1: 猫-坐（动作关系）
- 头2: 猫-动物（类别关系）
- 头3: 坐-沙发（位置关系）
- 头4: 猫-胡须（特征关系）
- ...

综合起来：一只猫坐在沙发上，它有胡须 ✓
```

---

## 🖼️ ViT 完整流程图解

### Vision Transformer 是怎么处理一张图片的？

```mermaid
graph TB
    subgraph "Step 1: 输入图片"
        A["🐱 猫的照片<br/>224×224像素"]
    end
    
    subgraph "Step 2: 切 Patch"
        B["切成 16×16 的小块<br/>14×14 = 196 个 patch"]
    end
    
    subgraph "Step 3: 加 CLS Token"
        C["[CLS] [patch1] [patch2] ... [patch196]<br/>共197个token"]
    end
    
    subgraph "Step 4: Transformer 编码器（12层）"
        D1["第1层: 边缘/颜色<br/>局部特征"] 
        D2["第6层: 耳朵/眼睛<br/>中级特征"]
        D3["第12层: 这是猫!<br/>高级特征"]
        
        D1 --> D2 --> D3
    end
    
    subgraph "Step 5: 分类"
        E["看 [CLS] 的输出"]
        F["分类头"]
        G["🐱 猫: 95%<br/>🐶 狗: 3%<br/>🐰 兔子: 2%"]
    end
    
    A --> B --> C --> D1
    D3 --> E --> F --> G
    
    style G fill:#90EE90,stroke:#333
```

### 每一层内部在做什么？

```mermaid
graph TB
    subgraph "一个 Transformer Layer"
        A[输入] --> B[Multi-Head Attention]
        B --> C[残差连接<br/>+ LayerNorm]
        C --> D[Feed Forward<br/>全连接层]
        D --> E[残差连接<br/>+ LayerNorm]
        E --> F[输出]
    end
    
    A -.->|+ 原始信息| C
    C -.->|+ 加工信息| E
    
    Note[残差连接 = 抄近路<br/>防止信息丢失<br/>训练更稳定]
```

---

## 🔍 CNN vs Transformer 深度对比

### 看图片的方式对比

```mermaid
graph TB
    subgraph "CNN（传统方法）"
        C1["👀 3×3窗口<br/>看左上角"] --> C2["滑动 →"]
        C2 --> C3["看右上角"]
        C3 --> C4["滑动 → ...<br/>重复几百次"]
        C4 --> C5["最后拼起来<br/>判断是什么"]
        
        Note1["❌ 问题: 猫尾巴太远<br/>可能认不出是猫的一部分"]
    end
    
    subgraph "Transformer（新方法）"
        T1["👀 一眼看全图!"]
        T2["[patch1] [patch2] ... [patchN]"]
        T3["同时计算所有关系:<br/>- 猫头和猫身: 0.95<br/>- 猫身和猫尾: 0.90<br/>- 猫和背景: 0.10"]
        T4["全局理解<br/>这是一只猫!"]
        
        T1 --> T2 --> T3 --> T4
        
        Note2["✓ 优势: 不管多远<br/>都能发现关系"]
    end
    
    style Note1 fill:#ffcccc,stroke:#333
    style Note2 fill:#ccffcc,stroke:#333
```

### 优缺点对比表

| 特性 | CNN | Transformer |
|------|-----|-------------|
| **归纳偏置** | 有（局部性、平移不变性）| 无（从零学习）|
| **全局感知** | ❌ 需要堆叠很多层 | ✅ 一层就能看全图 |
| **长距离关系** | ❌ 难捕捉 | ✅ 直接计算 |
| **计算效率** | ✅ O(n) | ❌ O(n²) |
| **数据需求** | ✅ 较少 | ❌ 大量 |
| **可解释性** | ⚠️ 一般 | ❌ 较差（黑盒）|

---

## 📊 三种主要方法对比

```mermaid
graph LR
    A[视觉Transformer<br/>三大流派] --> B[iGPT]
    A --> C[ViT ⭐]
    A --> D[DeiT]
    
    B -->|最暴力| E["每个像素=一个token<br/>字典大小: 256^3<br/>训练: 预测下一个像素"]
    
    C -->|最聪明| F["16×16 patch=一个token<br/>加CLS token分类<br/>训练: ImageNet分类"]
    
    D -->|最高效| G["蒸馏学习<br/>老师模型带学生<br/>数据少也能学好"]
    
    style C fill:#fff3cd,stroke:#333,stroke-width:3px
    style F fill:#90EE90,stroke:#333
```

| 方法 | Token方式 | 训练目标 | 数据需求 | 现状 |
|------|-----------|----------|----------|------|
| **iGPT** | 每个像素 | 预测下一个像素 | 极大 | 研究用 |
| **ViT** | 16×16 patch | 图像分类 | 大 | ⭐ 主流 |
| **DeiT** | 16×16 patch | 分类+蒸馏 | 中等 | 实用 |

---

## 🎯 目标检测：DETR 是怎么工作的？

### 传统方法 vs DETR

```mermaid
graph TB
    subgraph "传统目标检测（Faster R-CNN等）"
        A1["输入图片"] --> B1["生成候选框<br/>Anchor（几千个）"]
        B1 --> C1["判断每个框<br/>是不是物体"]
        C1 --> D1["NMS去重<br/>去掉重叠框"]
        D1 --> E1["输出结果"]
        
        Note1["❌ 复杂 pipeline<br/>很多手工设计<br/>超参数多"]
    end
    
    subgraph "DETR（Transformer）"
        A2["输入图片"] --> B2["CNN提特征"]
        B2 --> C2["Transformer编码器<br/>理解全局"]
        C2 --> D2["Transformer解码器<br/>100个Object Query"]
        D2 --> E2["直接输出<br/>边界框+类别"]
        
        Note2["✅ 端到端<br/>无需NMS<br/>无需Anchor"]
    end
    
    style Note1 fill:#ffcccc,stroke:#333
    style Note2 fill:#ccffcc,stroke:#333
```

### Object Query 是什么？

```mermaid
graph LR
    A[100个Object Query] --> B[Query1: 图里最大的物体在哪?]
    A --> C[Query2: 左上角的物体是什么?]
    A --> D[Query3: 红色的物体是什么?]
    A --> E[...]
    
    B --> F["解码器计算"]
    C --> F
    D --> F
    E --> F
    
    F --> G["输出:<br/>汽车 bbox1<br/>行人 bbox2<br/>红绿灯 bbox3"]
    
    style F fill:#e1f5e1,stroke:#333
```

**DETR 的局限性：**
- 训练收敛慢（需要500个epoch）
- 小物体检测效果不好
- 现在已被 Deformable DETR 等改进版本超越

---

## ⚠️ 当前面临的挑战

```mermaid
graph LR
    A[Transformer<br/>四大挑战] --> B[计算量太大]
    A --> C[需要海量数据]
    A --> D[黑盒不可解释]
    A --> E[架构不够适配视觉]
    
    B -->|ViT vs GhostNet| F["180亿 vs 6亿 FLOPs<br/>差了30倍!"]
    C -->|预训练数据| G["ImageNet-21k: 1400万张<br/>JFT-300M: 3亿张"]
    D -->|可解释性| H["为什么判断这是猫?<br/>说不清楚..."]
    E -->|架构| I["直接从NLP搬过来<br/>没有利用图像的<br/>局部先验知识"]
    
    style B fill:#ff9999,stroke:#333
    style C fill:#ffcc99,stroke:#333
    style D fill:#ffff99,stroke:#333
    style E fill:#ccffff,stroke:#333
```

---

## 🚀 未来发展方向

```mermaid
graph TB
    A[未来方向] --> B[大一统模型]
    A --> C[高效部署]
    A --> D[可解释性]
    A --> E[自监督学习]
    
    B -->|一个模型做所有事| F["分类 + 检测 + 分割<br/>+ 生成 + ..."]
    C -->|轻量化| G["手机实时运行<br/>边缘设备部署"]
    D -->|可视化| H["Attention可视化<br/>知道模型在看哪"]
    E -->|减少标注依赖| I["像GPT一样<br/>无监督预训练"]
    
    style F fill:#90EE90,stroke:#333
    style G fill:#90EE90,stroke:#333
    style H fill:#90EE90,stroke:#333
    style I fill:#90EE90,stroke:#333
```

---

## 📈 发展历程

```mermaid
timeline
    title 视觉 Transformer 发展历程
    2017 : Transformer诞生<br/>（Attention is All You Need）
    2020 : iGPT发布<br/>ViT发布<br/>视觉Transformer元年
    2021 : DeiT发布<br/>Swin Transformer发布<br/>解决计算效率问题
    2022 : CLIP发布<br/>DALL-E 2发布<br/>多模态爆发
    2023 : GPT-4V发布<br/>SAM发布<br/>大模型时代
    2024-now : 几乎统治所有视觉任务
```

---

## 💡 我的思考

> **2020-2021年**写这篇文章时，Transformer 刚开始进入视觉领域，还有很多质疑声音。
>
> **现在（2024-2026年）**来看：
> - ✅ ViT 已经成为视觉 backbone 的标准选择
> - ✅ 多模态大模型（GPT-4V、Claude、Gemini）都基于视觉 Transformer
> - ✅ 计算效率问题通过 Swin、PVT 等架构大幅改善
> - ✅ 自监督预训练（MAE、BEiT）减少了对标注数据的依赖
>
> **结论**：Transformer 确实正在取代 CNN，成为计算机视觉的新范式。

---

## 📚 相关资源

| 资源 | 链接 | 说明 |
|------|------|------|
| **原文** | [微信文章](https://mp.weixin.qq.com/s/SGROkMleCiV6iPI7kNlXOA) | 综述性文章 |
| **ViT 论文** | [An Image is Worth 16x16 Words](https://arxiv.org/abs/2010.11929) | 开山之作 |
| **DeiT 论文** | [Training data-efficient image transformers](https://arxiv.org/abs/2012.12877) | 蒸馏学习 |
| **Swin 论文** | [Swin Transformer](https://arxiv.org/abs/2103.14030) | 层次化架构 |
| **DETR 论文** | [End-to-End Object Detection](https://arxiv.org/abs/2005.12872) | 目标检测 |

---

## 🎓 学习建议

1. **先理解 Self-Attention**（核心中的核心）
2. **动手实现一个小 ViT**（推荐用 PyTorch）
3. **阅读 ViT 源码**（Hugging Face Transformers 库）
4. **尝试微调预训练模型**（在自己的数据集上）

---

*整理完成，如有错误欢迎指正！*
