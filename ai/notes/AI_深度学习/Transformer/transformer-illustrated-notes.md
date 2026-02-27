# Transformer 图解完整笔记

> **原文**: [图解Transformer（完整版）](https://mp.weixin.qq.com/s/_ejGvrYENb3kGzmYlKAVrw)  
> **来源**: Datawhale / jalammar.github.io  
> **整理时间**: 2026-02-14  
> **难度**: 零基础 ⭐

---

## 前言

本文是**最经典的Transformer入门教程**，特点：
- ✅ 从输入到输出，**一步步图解**数据流动
- ✅ 包含**矩阵运算**的代码实现
- ✅ 大量**可视化图表**，直观理解

适合**零基础**读者建立完整概念。

---

## 一、宏观理解Transformer

### 1.1 整体结构

```
┌─────────────────────────────────────────────┐
│           Transformer（黑盒）                │
│                                             │
│   输入: "Hello World"（英文）               │
│                   ↓                         │
│         ┌────────┴────────┐                │
│         │                 │                │
│    ┌────▼────┐       ┌────▼────┐           │
│    │ Encoder │       │ Decoder │           │
│    │ 编码器  │       │ 解码器  │           │
│    │  ×6层   │       │  ×6层   │           │
│    └────┬────┘       └────┬────┘           │
│         │                 │                │
│         └────────┬────────┘                │
│                  ↓                          │
│   输出: "你好世界"（中文）                   │
└─────────────────────────────────────────────┘
```

### 1.2 编码器内部结构

每个编码器有两层：
```
输入向量
    ↓
┌──────────────────┐
│ Self-Attention   │  ← 看其他词，理解当前词
│ （自注意力层）    │
└────────┬─────────┘
         ↓
┌──────────────────┐
│ Feed Forward     │  ← 前馈神经网络，加工特征
│ （前馈层）        │
└────────┬─────────┘
         ↓
输出向量（传给下一层）
```

**核心思想**：处理一个词时，不仅看这个词，还要看句子中**其他所有词**。

类比翻译：翻译"it"时，你会回头看"animal"，Transformer也是这样做的。

---

## 二、Transformer的输入

### 2.1 词嵌入（Embedding）

```
句子: "Thinking Machines"
        ↓
    分词 + 查表
        ↓
┌──────────────────────┐
│ Thinking → [0.2, -0.5, 0.8, 0.3]  │  4维向量（实际512维）
│ Machines → [0.1, 0.7, -0.2, 0.9]  │
└──────────────────────┘
        ↓
输入矩阵 X: (2, 4)  2个词，每个4维
```

**实际处理**：
- 句子长度固定（不够补0，超长截断）
- 向量维度通常是256或512

### 2.2 输入在编码器中的流动

```
词向量1 ─────────┬─────────
                 │ Self-Attention
词向量2 ─────────┼─────────
                 │ （相互影响）
词向量3 ─────────┘
        ↓
每个词都和其他词交互后
        ↓
各自经过Feed Forward（互不影响，可并行）
        ↓
输出
```

**关键特性**：
- Self-Attention层：词之间有依赖（必须同时处理）
- Feed Forward层：词之间无依赖（可并行计算）

---

## 三、Self-Attention详解

### 3.1 什么是Self-Attention

**例子**：翻译句子
```
"The animal didn't cross the street because it was too tired"

问题: "it"指的是什么？
- animal（动物）？
- street（街道）？
```

**Self-Attention的作用**：
- 处理"it"时，自动关联到"animal"
- 让模型知道"it"和"animal"关系最强

### 3.2 计算步骤（6步）

#### 第1步：生成Q、K、V三个向量

```
每个词的向量 X
    ↓
    ├── 乘 W_Q → Q (Query)   "我要查什么"
    ├── 乘 W_K → K (Key)     "我是谁"  
    └── 乘 W_V → V (Value)   "我有什么信息"

维度变化：
X: 512维  →  Q/K/V: 64维（缩小，为了效率）
```

**图示**：
```
Thinking (X1) ──W_Q──→ q1
            ──W_K──→ k1
            ──W_V──→ v1

Machines (X2) ──W_Q──→ q2
            ──W_K──→ k2
            ──W_V──→ v2
```

#### 第2步：计算注意力分数（Attention Score）

```
以"Thinking"为例，计算它应该关注哪些词：

score_1 = q1 · k1   ( Thinking vs Thinking )
score_2 = q1 · k2   ( Thinking vs Machines )

结果：[score_1, score_2]
```

**直观理解**：
- 分数高 → 关系近 → 多关注
- 分数低 → 关系远 → 少关注

#### 第3步：缩放（除以√d_k）

```
scaled_score = score / √64 = score / 8
```

**为什么要缩放？**
- 防止点积结果过大
- 避免Softmax梯度消失
- 让训练更稳定

#### 第4步：Softmax归一化

```
[score_1, score_2] ──Softmax──→ [0.6, 0.4]

结果：
- Thinking 关注自己 60%
- Thinking 关注 Machines 40%
```

#### 第5步：分数乘Value

```
v1 × 0.6 = 加权后的v1
v2 × 0.4 = 加权后的v2
```

#### 第6步：加权求和

```
z1 = 0.6×v1 + 0.4×v2

z1就是"Thinking"经过Self-Attention后的输出
包含了"Machines"的信息
```

### 3.3 矩阵形式（并行计算）

实际代码用矩阵，一次算出所有词的输出：

```python
# X: (seq_len, 512) 输入矩阵
# W_Q, W_K, W_V: (512, 64) 可学习参数

Q = X @ W_Q   # (seq_len, 64)
K = X @ W_K   # (seq_len, 64)
V = X @ W_V   # (seq_len, 64)

# Attention计算
scores = Q @ K.T / sqrt(64)      # (seq_len, seq_len)
weights = softmax(scores, dim=-1) # (seq_len, seq_len)
Z = weights @ V                  # (seq_len, 64) 输出
```

**公式**：
```
Attention(Q, K, V) = softmax(QK^T / √d_k) V
```

---

## 四、Multi-Head Attention（多头注意力）

### 4.1 为什么需要多头

**问题**：单头注意力只能捕捉一种关系

**多头的优势**：
```
头1: 关注语法关系（主谓宾）
头2: 关注语义关系（同义词）
头3: 关注指代关系（it=animal）
...
头8: 关注其他模式

综合起来：更全面理解句子
```

### 4.2 多头计算过程

```
输入 X: (seq_len, 512)
            ↓
    分成8个头，每个64维
            ↓
┌─────────────────────────────────────┐
│ 头1: Q1,K1,V1 ──Attention──→ Z1     │
│ 头2: Q2,K2,V2 ──Attention──→ Z2     │
│ ...                                 │
│ 头8: Q8,K8,V8 ──Attention──→ Z8     │
└─────────────────────────────────────┘
            ↓
    拼接8个结果: [Z1, Z2, ..., Z8]
            ↓
    (seq_len, 512)
            ↓
    乘WO矩阵（线性变换）
            ↓
    最终输出: (seq_len, 512)
```

**维度计算**：
```
单头: d_k = 512 / 8 = 64

8个头并行计算：
- 每个头产出: (seq_len, 64)
- 拼接后: (seq_len, 512)
```

### 4.3 可视化多头注意力

```
句子: "The animal didn't cross the street because it was too tired"

编码"it"时，不同头的关注点：

头1: 最关注 "animal"（指代关系）
头2: 最关注 "tired"  （属性关系）
头3: 关注多个词      （综合理解）
...

所有头的结果拼接，"it"的表示融合了多种信息
```

---

## 五、代码实现

### 5.1 PyTorch官方实现

```python
import torch.nn as nn

# 定义多头注意力
multihead_attn = nn.MultiheadAttention(
    embed_dim=300,    # 输出维度
    num_heads=6,      # 6个头
    dropout=0.1       # dropout率
)

# 输入
query = torch.rand(12, 64, 300)  # (seq_len, batch, dim)
key = torch.rand(10, 64, 300)
value = torch.rand(10, 64, 300)

# 前向计算
attn_output, attn_weights = multihead_attn(query, key, value)
# attn_output: (12, 64, 300)
# attn_weights: (64, 12, 10) 注意力权重
```

### 5.2 手动实现多头注意力

```python
import torch
import torch.nn as nn

class MultiHeadAttention(nn.Module):
    def __init__(self, hid_dim, n_heads, dropout):
        super().__init__()
        self.hid_dim = hid_dim
        self.n_heads = n_heads
        self.head_dim = hid_dim // n_heads  # 每个头的维度
        
        # 确保能整除
        assert hid_dim % n_heads == 0
        
        # 定义权重矩阵
        self.w_q = nn.Linear(hid_dim, hid_dim)
        self.w_k = nn.Linear(hid_dim, hid_dim)
        self.w_v = nn.Linear(hid_dim, hid_dim)
        self.fc = nn.Linear(hid_dim, hid_dim)
        
        self.dropout = nn.Dropout(dropout)
        self.scale = torch.sqrt(torch.FloatTensor([self.head_dim]))
    
    def forward(self, query, key, value, mask=None):
        batch_size = query.shape[0]
        
        # 1. 计算Q, K, V
        Q = self.w_q(query)  # (batch, seq_len, hid_dim)
        K = self.w_k(key)
        V = self.w_v(value)
        
        # 2. 分成n_heads个头
        # (batch, seq_len, n_heads, head_dim)
        Q = Q.view(batch_size, -1, self.n_heads, self.head_dim)
        # 转置: (batch, n_heads, seq_len, head_dim)
        Q = Q.permute(0, 2, 1, 3)
        
        K = K.view(batch_size, -1, self.n_heads, self.head_dim)
        K = K.permute(0, 2, 1, 3)
        
        V = V.view(batch_size, -1, self.n_heads, self.head_dim)
        V = V.permute(0, 2, 1, 3)
        
        # 3. 计算注意力
        # Q: (batch, n_heads, seq_len_q, head_dim)
        # K: (batch, n_heads, seq_len_k, head_dim)
        # K^T: (batch, n_heads, head_dim, seq_len_k)
        energy = torch.matmul(Q, K.permute(0, 1, 3, 2)) / self.scale
        # energy: (batch, n_heads, seq_len_q, seq_len_k)
        
        # 4. Mask（可选）
        if mask is not None:
            energy = energy.masked_fill(mask == 0, -1e10)
        
        # 5. Softmax
        attention = torch.softmax(energy, dim=-1)
        attention = self.dropout(attention)
        
        # 6. 乘V
        # attention: (batch, n_heads, seq_len_q, seq_len_k)
        # V: (batch, n_heads, seq_len_k, head_dim)
        x = torch.matmul(attention, V)
        # x: (batch, n_heads, seq_len_q, head_dim)
        
        # 7. 拼接多头
        x = x.permute(0, 2, 1, 3).contiguous()
        # (batch, seq_len_q, n_heads, head_dim)
        
        x = x.view(batch_size, -1, self.hid_dim)
        # (batch, seq_len_q, hid_dim)
        
        # 8. 线性变换
        x = self.fc(x)
        
        return x, attention


# 测试
query = torch.rand(64, 12, 300)  # (batch, seq_len, dim)
key = torch.rand(64, 10, 300)
value = torch.rand(64, 10, 300)

attention = MultiHeadAttention(hid_dim=300, n_heads=6, dropout=0.1)
output, attn_weights = attention(query, key, value)

print(output.shape)        # torch.Size([64, 12, 300])
print(attn_weights.shape)  # torch.Size([64, 6, 12, 10])
```

---

## 六、位置编码（Positional Encoding）

### 6.1 为什么需要位置编码

**Transformer的问题**：同时看所有词，**不知道词序**

```
"我打你" 和 "你打我"
在Transformer眼中都是 [打, 我, 你]
分不清区别！
```

**解决方案**：给每个位置加个"地址标签"

### 6.2 正弦位置编码

```python
# 公式
PE(pos, 2i)   = sin(pos / 10000^(2i/d_model))
PE(pos, 2i+1) = cos(pos / 10000^(2i/d_model))

# pos: 词的位置(0, 1, 2, ...)
# i: 维度索引
```

**直观效果**：
```
位置0: [0.0, 1.0, 0.0, 1.0, ...]
位置1: [0.8, 0.9, 0.1, 0.95, ...]
位置2: [0.9, 0.4, 0.9, 0.6, ...]

相邻位置有相似的编码
远距离位置编码差异大
```

**可视化**（20个词，512维）：
```
每个位置一行，512个值
        
位置0   ████░░░░████░░░░████...  
位置1   ███░░░░░████░░░████░...
位置2   ██░░░░░░████░░████░░...
位置3   █░░░░░░░████░████░░░...
...
位置19  ░░░░████░░░░████░░░░...

中间分界线：左半sin，右半cos
```

**优点**：
- 可以扩展到训练时没见过的长度
- 相对位置可以线性表示

---

## 七、残差连接和层归一化

### 7.1 残差连接（Residual Connection）

```
输入 X
    ↓
[Self-Attention] → 输出 A
    ↓
X + A  ← 残差连接（把输入加回来）
    ↓
[LayerNorm]
    ↓
输出
```

**作用**：
- 防止梯度消失
- 保留原始信息
- 训练更深的网络

### 7.2 层归一化（Layer Normalization）

```
对每个样本，在特征维度上归一化

输入: [0.2, -0.5, 0.8, 0.3]
均值 = 0.2
方差 = 0.29
输出: [0.0, -1.3, 1.1, 0.2]  (标准化)
```

**作用**：
- 稳定训练
- 加速收敛

---

## 八、解码器（Decoder）

### 8.1 解码器结构

```
输入: <start> （开始标志）
    ↓
┌──────────────────────┐
│ Masked Self-Attention│  ← 只能看前面的词
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│ Encoder-Decoder      │  ← Q来自解码器，K/V来自编码器
│ Attention            │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│ Feed Forward         │
└──────────┬───────────┘
           ↓
输出: "你" （第一个词）
           ↓
把"你"加回输入，继续生成下一个词...
```

### 8.2 Masked Self-Attention

**关键区别**：编码时能看到所有词，解码时**只能看到已生成的词**

```
生成第3个词时：

可以看到的: [<start>, "我", "是"]
不能看到的: ["学", "生", "<end>"] （mask掉）

Mask矩阵（下三角）：
       <start>  我   是   学
<start>   1     0    0    0
我         1     1    0    0
是         1     1    1    0
学         1     1    1    1

上三角为0（-∞），softmax后为0
```

### 8.3 Encoder-Decoder Attention

```
Q: 来自解码器（我想生成什么）
K, V: 来自编码器（输入句子有什么）

作用: 让解码器关注输入句子的相关部分
```

---

## 九、输出层

### 9.1 线性层 + Softmax

```
解码器输出: (batch, seq_len, 512)
    ↓
线性层（全连接）
    ↓
Logits: (batch, seq_len, vocab_size)
    # vocab_size: 词表大小（如50000）
    ↓
Softmax
    ↓
概率分布: [0.001, 0.002, ..., 0.85, ..., 0.0001]
          # 第100个词概率最高（0.85）
    ↓
输出词: 取概率最大的词
```

### 9.2 贪婪解码 vs 束搜索

**贪婪解码（Greedy Decoding）**：
```
每个时间步选概率最高的词
简单快速，但可能不是全局最优
```

**束搜索（Beam Search）**：
```
每个时间步保留top-k个候选
下一步基于这些候选继续扩展
最终选整体概率最高的序列

例如 beam_size=2:
第1步保留: "I"(0.3), "My"(0.25)
第2步扩展: "I am"(0.2), "I was"(0.15), "My name"(0.18), "My dog"(0.12)
保留top2: "I am", "My name"
继续...
```

---

## 十、训练过程

### 10.1 前向传播

```
输入: "je suis étudiant"（法语）
目标: "i am a student"（英语）

模型输出概率分布:
时间步1: [0.1, 0.6, 0.1, 0.2]  → 预测"i"
时间步2: [0.2, 0.1, 0.7, 0.0]  → 预测"am"
时间步3: [0.5, 0.2, 0.1, 0.2]  → 预测"a"
...
```

### 10.2 损失函数（交叉熵）

```
预测分布 vs 真实标签

真实标签（one-hot）:
"i"    → [1, 0, 0, 0, 0, 0]
"am"   → [0, 1, 0, 0, 0, 0]
"a"    → [0, 0, 1, 0, 0, 0]
...

Loss = -Σ y_true × log(y_pred)
     = -[1×log(0.6) + 1×log(0.7) + 1×log(0.5) + ...]
```

### 10.3 反向传播

```
计算Loss → 梯度反向传播 → 更新权重

训练目标: 让预测分布接近真实分布
```

---

## 十一、总结

### 11.1 完整流程图

```
┌────────────────────────────────────────────────────────────┐
│                        训练阶段                             │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  输入句子        Tokenizer         Embedding + 位置编码     │
│  "Hello"    →    [15496]      →    [0.2, -0.5, ...]       │
│                                                            │
│  ┌─────────────────────────────────────────────────────┐  │
│  │                    Encoder × 6                       │  │
│  │  Self-Attention → Add&Norm → FeedForward → Add&Norm│  │
│  └─────────────────────────────────────────────────────┘  │
│                            ↓                               │
│                     上下文向量                             │
│                            ↓                               │
│  ┌─────────────────────────────────────────────────────┐  │
│  │                    Decoder × 6                       │  │
│  │  Masked Attn → Enc-Dec Attn → FeedForward            │  │
│  └─────────────────────────────────────────────────────┘  │
│                            ↓                               │
│                     概率分布                               │
│                            ↓                               │
│  输出句子        Tokenizer         贪婪/束搜索             │
│  "你好"     ←    [17784]      ←    概率最大词             │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### 11.2 核心概念回顾

| 概念 | 作用 | 公式/方法 |
|------|------|----------|
| **Self-Attention** | 计算词与词的关系 | softmax(QK^T/√d_k)V |
| **Multi-Head** | 多角度理解 | 8个头并行计算 |
| **Positional Encoding** | 添加位置信息 | sin/cos函数 |
| **Residual** | 防止梯度消失 | X + Sublayer(X) |
| **LayerNorm** | 稳定训练 | 标准化每一层 |
| **Masked Attention** | 防止看到未来 | 下三角mask |

---

## 十二、学习资源

### 必读论文
- [Attention Is All You Need](https://arxiv.org/abs/1706.03762) - Transformer原始论文

### 推荐博客
- [The Illustrated Transformer](http://jalammar.github.io/illustrated-transformer) - 原文（英文）
- [The Annotated Transformer](http://nlp.seas.harvard.edu/2018/04/03/attention.html) - 代码+解释

### 实践项目
- [Tensor2Tensor](https://github.com/tensorflow/tensor2tensor) - Google官方实现
- [Hugging Face Transformers](https://github.com/huggingface/transformers) - 最流行实现

---

## 学习建议

1. **第一步**：理解Self-Attention计算流程（6步）
2. **第二步**：动手实现ScaledDotProductAttention
3. **第三步**：理解Multi-Head的拼接逻辑
4. **第四步**：跑通完整Transformer代码
5. **第五步**：应用到实际任务（翻译/摘要）

---

*本文整理自jalammar的经典图解Transformer教程，建议配合原文的交互式图表学习。*
