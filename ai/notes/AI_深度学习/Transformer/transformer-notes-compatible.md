# Transformer 入门笔记 (IDEA兼容版)

> **原文**: 视觉Transformer入门教程  
> **整理时间**: 2026-02-14  
> **兼容性**: 支持标准Mermaid解析器

---

## 注意

本文档中的图表使用Mermaid语法。如果在IDEA中查看：
- **安装插件**: Settings → Plugins → 搜索 "Mermaid" → 安装重启
- **或使用**: Typora / VSCode / GitHub 查看效果最佳

---

## 1. 一句话总结

**Transformer** 是一种完全基于**注意力机制**的神经网络架构，抛弃了传统的RNN和CNN，能够并行处理序列数据并捕捉长距离依赖关系。

---

## 2. 为什么要用Transformer

### RNN vs Transformer 对比

```
RNN的特点:
- 顺序计算: 必须一个一个处理
- 慢: 无法并行
- 信息丢失: 长距离依赖困难

Transformer的特点:
- 并行计算: 所有位置同时处理
- 快: 适合GPU加速
- 全局感知: 任意两个位置直接关联
```

---

## 3. Self-Attention 核心机制

### 3.1 什么是Self-Attention

想象这个句子: **The animal did not cross the street because it was too tired**

问题: **it** 指的是什么?

- 距离近的: street (街道)
- 实际指的: animal (动物)

Self-Attention 的作用就是自动发现 **it** 和 **animal** 关系更强。

### 3.2 计算步骤

**Step 1: 生成Q, K, V三个向量**

```
输入X (句子中每个词的向量)
    |
    |--乘以WQ矩阵--> Q (Query: 我要查什么)
    |--乘以WK矩阵--> K (Key: 我是谁)
    |--乘以WV矩阵--> V (Value: 我有什么信息)
```

**Step 2: 计算注意力分数**

```
Score = Q x K转置 / sqrt(dk)
       |
       |-- Softmax --> 概率分布 (0.1, 0.7, 0.1, 0.1)
       |
       表示: 当前词应该关注其他词的程度
```

**Step 3: 加权求和**

```
Output = 概率分布 x V
        = 0.1xv1 + 0.7xv2 + 0.1xv3 + 0.1xv4
        
结果: 当前词的表示融入了其他词的信息
```

### 3.3 公式表示

```
Attention(Q, K, V) = Softmax(QK转置 / sqrt(dk)) x V
```

---

## 4. Multi-Head Attention 多头注意力

### 4.1 为什么需要多头

就像多人从不同角度看问题:

- **头1**: 看语法关系 (主谓宾)
- **头2**: 看语义关系 (同义词)
- **头3**: 看指代关系 (it指什么)
- **头4-8**: 看其他关系

### 4.2 计算过程

```
输入: 512维向量
      |
      |--分成8个头--|
                    |
头1: 64维 --> Attention计算 --> 输出64维
头2: 64维 --> Attention计算 --> 输出64维
头3: 64维 --> Attention计算 --> 输出64维
... (共8个)
头8: 64维 --> Attention计算 --> 输出64维
                    |
      |--拼接起来--|
                    v
              输出: 512维 (8 x 64)
```

---

## 5. 位置编码 Positional Encoding

### 5.1 问题

Transformer同时看所有词，**不知道词的顺序**:

```
"我打你" 和 "你打我"
在Transformer眼里都是: [打, 我, 你]
分不清区别!
```

### 5.2 解决方案

给每个位置加一个**位置向量**，表示这个词在句子中的位置:

```
位置0: [0.0, 1.0, 0.0, ...]
位置1: [0.8, 0.9, 0.1, ...]
位置2: [0.3, 0.2, 0.7, ...]
```

使用正弦函数生成:

```python
PE(pos, 2i)   = sin(pos / 10000^(2i/d_model))
PE(pos, 2i+1) = cos(pos / 10000^(2i/d_model))
```

---

## 6. Transformer 完整架构

### 6.1 编码器 Encoder

```
输入
  |
  |--词嵌入 + 位置编码
  |
  v
[Multi-Head Attention] --> [Add & Norm]
                               |
                               v
                        [Feed Forward] --> [Add & Norm]
                                                    |
                                                    v
                                               (重复N层)
                                                    |
                                                    v
                                               输出
```

**组件说明**:
- **Multi-Head Attention**: 计算词与词的关系
- **Add & Norm**: 残差连接 + 层归一化
- **Feed Forward**: 两个全连接层

### 6.2 解码器 Decoder

```
输入
  |
  |--词嵌入 + 位置编码
  |
  v
[Masked Multi-Head Attention] --> [Add & Norm]
                                         |
                                         v
                              [Cross Attention] --> [Add & Norm]
                                                             |
                                                             v
                                                      [Feed Forward]
                                                             |
                                                             v
                                                      (重复N层)
                                                             |
                                                             v
                                                        输出
```

**特殊组件**:
- **Masked Attention**: 只能看前面的词，不能看后面的
- **Cross Attention**: Q来自解码器，K,V来自编码器

---

## 7. Vision Transformer (ViT)

### 7.1 核心思想

把图片当成"句子"来处理:

```
图片 (224x224)
      |
      |--切成16x16的小块 (patch)
      |--共14x14=196个patch
      |
      v
每个patch拉平: 16x16x3=768维
      |
      |--Linear投影到512维
      |
      v
196个token，每个512维
      |
      |--加CLS token (用于分类)
      |--加位置编码
      |
      v
输入Transformer (和标准NLP一样)
      |
      v
取CLS输出做分类
```

### 7.2 详细步骤

**Step 1: Patch Embedding**

```python
# 输入: (batch, 3, 224, 224)
# 切分成 14x14=196 个patch
x = rearrange(img, 'b c (h p1) (w p2) -> b (h w) (p1 p2 c)', p1=16, p2=16)
# 输出: (batch, 196, 768)

# 降维
x = Linear(768, 512)(x)
# 输出: (batch, 196, 512)
```

**Step 2: 加CLS Token**

```python
# CLS token: 可学习的向量
cls_token = nn.Parameter(torch.randn(1, 1, 512))

# 复制batch份
cls_tokens = cls_token.expand(batch_size, -1, -1)

# 拼接到最前面
x = torch.cat([cls_tokens, x], dim=1)
# 输出: (batch, 197, 512)
```

**Step 3: 位置编码**

```python
# 可学习的位置编码
pos_embedding = nn.Parameter(torch.randn(1, 197, 512))

# 加上位置信息
x = x + pos_embedding
```

**Step 4: Transformer编码**

```python
# 和标准Transformer一样
for i in range(12):  # 12层
    x = MultiHeadAttention(x)
    x = FeedForward(x)
```

**Step 5: 分类**

```python
# 取CLS token的输出 (第0个位置)
cls_output = x[:, 0]  # (batch, 512)

# 分类头
output = Linear(512, num_classes)(cls_output)
```

---

## 8. DETR (目标检测)

### 8.1 核心创新

传统目标检测:
```
图片 --> CNN特征 --> 生成Anchor --> NMS去重 --> 结果
          (复杂后处理，手工设计多)
```

DETR:
```
图片 --> CNN特征 --> Transformer --> 直接输出100个框
          (端到端，无需NMS)
```

### 8.2 关键组件

**Object Queries (对象查询)**:

```
100个可学习的向量，每个代表一个"查询"

Query1: 找图片中最大的物体
Query2: 找左上角的物体
Query3: 找红色的物体
...
Query100
```

**双边匹配 (匈牙利算法)**:

```
问题: 输出的100个框是无序的，如何和Ground Truth匹配?

解决方案:
1. 计算100个预测框和M个真实框的匹配代价
   (分类损失 + 坐标损失 + GIoU损失)
   
2. 使用匈牙利算法找到最优匹配
   (使得总体损失最小)
   
3. 只计算匹配上的框的损失
```

### 8.3 损失函数

```python
# 1. 分类损失 (交叉熵)
loss_cls = CrossEntropy(pred_classes, target_classes)

# 2. 边界框损失 (L1)
loss_bbox = L1Loss(pred_boxes, target_boxes)

# 3. GIoU损失 (考虑重叠度)
loss_giou = 1 - GIoU(pred_boxes, target_boxes)

# 总损失
loss = loss_cls + loss_bbox + loss_giou
```

---

## 9. 性能对比

### Transformer vs CNN

| 指标 | CNN (ResNet) | ViT |
|------|-------------|-----|
| 数据需求 | 少 (ImageNet-1k) | 多 (需要JFT-300M) |
| 计算量 | 小 | 大 (30倍) |
| 全局感知 | 弱 (局部) | 强 (全局) |
| 并行性 | 一般 | 好 |
| 可解释性 | 中 | 高 |

### 数据量影响

```
ImageNet-1k (130万张):
    CNN > ViT
    
ImageNet-21k (1400万张):
    CNN ≈ ViT
    
JFT-300M (3亿张):
    ViT >> CNN
```

**结论**: Transformer是数据饥渴型，数据越多越强。

---

## 10. 发展趋势

```
2017: Transformer诞生 (Attention is All You Need)
2020: ViT发布 (视觉Transformer元年)
2021: DeiT, Swin Transformer (数据效率优化)
2022: CLIP, DALL-E (多模态爆发)
2023: GPT-4V, SAM (大模型时代)
2024+: 几乎统治CV所有任务
```

---

## 11. 学习建议

### 入门路线

1. **理解Self-Attention** (最重要)
   - 手动画一遍Q,K,V计算流程
   - 理解Attention分数的含义

2. **阅读代码**
   - PyTorch: nn.MultiheadAttention
   - 开源: lucidrains/vit-pytorch

3. **动手实践**
   - 实现简单Transformer
   - 用Hugging Face微调ViT

4. **阅读论文**
   - Attention is All You Need
   - An Image is Worth 16x16 Words (ViT)
   - End-to-End Object Detection with Transformers (DETR)

### 推荐工具

| 工具 | 用途 | 特点 |
|------|------|------|
| Typora | Markdown阅读 | 原生支持Mermaid |
| VSCode | 代码+文档 | 插件丰富 |
| GitHub | 在线查看 | 原生渲染Mermaid |
| mermaid.live | 在线调试 | 实时预览 |

---

## 12. 核心代码片段

### 12.1 Self-Attention实现

```python
import torch
import torch.nn as nn
import math

class SelfAttention(nn.Module):
    def __init__(self, d_model):
        super().__init__()
        self.d_model = d_model
        
        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)
        
    def forward(self, x):
        # x: (batch, seq_len, d_model)
        
        Q = self.W_q(x)  # (batch, seq_len, d_model)
        K = self.W_k(x)
        V = self.W_v(x)
        
        # 计算注意力分数
        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.d_model)
        # (batch, seq_len, seq_len)
        
        # Softmax
        attn = torch.softmax(scores, dim=-1)
        
        # 加权求和
        output = torch.matmul(attn, V)
        # (batch, seq_len, d_model)
        
        return output, attn
```

### 12.2 ViT完整代码

```python
import torch
import torch.nn as nn
from einops import rearrange, repeat

class ViT(nn.Module):
    def __init__(self, image_size=224, patch_size=16, num_classes=1000, 
                 dim=512, depth=12, heads=8):
        super().__init__()
        
        self.patch_size = patch_size
        num_patches = (image_size // patch_size) ** 2
        patch_dim = 3 * patch_size ** 2
        
        # Patch embedding
        self.patch_to_embedding = nn.Linear(patch_dim, dim)
        
        # CLS token
        self.cls_token = nn.Parameter(torch.randn(1, 1, dim))
        
        # 位置编码
        self.pos_embedding = nn.Parameter(torch.randn(1, num_patches + 1, dim))
        
        # Transformer
        encoder_layer = nn.TransformerEncoderLayer(d_model=dim, nhead=heads)
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=depth)
        
        # 分类头
        self.mlp_head = nn.Sequential(
            nn.LayerNorm(dim),
            nn.Linear(dim, num_classes)
        )
    
    def forward(self, img):
        b = img.shape[0]
        
        # 切patch
        x = rearrange(img, 'b c (h p1) (w p2) -> b (h w) (p1 p2 c)', 
                      p1=self.patch_size, p2=self.patch_size)
        
        # Embedding
        x = self.patch_to_embedding(x)
        
        # 加CLS
        cls_tokens = repeat(self.cls_token, '1 1 d -> b 1 d', b=b)
        x = torch.cat([cls_tokens, x], dim=1)
        
        # 加位置编码
        x += self.pos_embedding
        
        # Transformer
        x = self.transformer(x)
        
        # 分类
        return self.mlp_head(x[:, 0])
```

---

## 13. 总结

### 核心要点

1. **Self-Attention**: 计算序列中任意两个位置的关系
2. **Multi-Head**: 从多个角度理解关系
3. **Positional Encoding**: 给模型位置信息
4. **并行计算**: 比RNN快很多

### 在CV中的应用

- **分类**: ViT (Patch + CLS)
- **检测**: DETR (Object Query + 匈牙利匹配)
- **分割**: Segmenter
- **多模态**: CLIP (图文对齐)

---

*整理完成。建议配合代码实践学习效果更佳。*
