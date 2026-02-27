# 让研究人员绞尽脑汁的Transformer位置编码

> **原文**: [让研究人员绞尽脑汁的Transformer位置编码](https://mp.weixin.qq.com/s/WyDvRy7xudVMUXZzGNW-0A)  
> **作者**: 苏剑林（追一科技）  
> **来源**: PaperWeekly  
> **发布时间**: 2021年左右  
> **整理时间**: 2026-02-14  
> **分类**: AI-ML  
> **标签**: Transformer, 位置编码, Attention, BERT, GPT, 深度学习

---

## 📌 一句话总结

本文全面综述了Transformer模型中的位置编码方案，从绝对位置编码（训练式、三角式、递归式、相乘式）到相对位置编码（经典式、XLNET式、T5式、DeBERTa式），再到其他创新方案（CNN式、复数式、融合式），展现了研究人员在位置编码上的"八仙过海，各显神通"。

---

## 🎯 核心要点

### 1. 为什么需要位置编码？

**根本原因**：纯粹的Attention模块无法捕捉输入顺序，无法区分不同位置的Token。

**两大方向**：
1. **绝对位置编码**：将位置信息融入输入
2. **相对位置编码**：改造Attention结构，使其能分辨位置

### 2. 绝对位置编码方案对比

| 方案 | 核心思想 | 代表模型 | 优点 | 缺点 |
|------|---------|----------|------|------|
| **训练式** | 将位置编码作为可训练参数 | BERT、GPT | 简单直接 | 无外推性（处理不了超长文本） |
| **三角式** | 使用sin/cos函数生成 | 原始Transformer | 有显式规律，可外推 | 现在很少直接使用 |
| **递归式** | 用RNN/ODE递归生成 | FLOATER | 外推性好，灵活 | 牺牲并行性，速度瓶颈 |
| **相乘式** | 输入与位置编码逐位相乘 | 实验性方案 | 可能比相加更好 | 未充分验证 |

### 3. 相对位置编码方案对比

| 方案 | 核心改进 | 特点 |
|------|---------|------|
| **经典式** | 将绝对位置改为相对距离 | 只需有限个编码，可处理任意长度 |
| **XLNET式** | 替换query/key为可训练向量 | 去掉位置偏置，只保留相对位置 |
| **T5式** | 只保留"位置-位置"交互 | 最简单的相对位置编码，分桶处理 |
| **DeBERTa式** | 保留"输入-位置"交互，去掉"位置-位置" | 结合绝对和相对位置的新视角 |

### 4. 创新方案

- **CNN式**：Zero Padding泄露位置信息（不适用于Transformer）
- **复数式**：使用复数模型，每个词有三组词向量（最特立独行）
- **融合式**：作者提出的方案，绝对位置编码等价于相对位置编码

---

## 📝 详细内容

### 一、绝对位置编码（Absolute Position Encoding）

#### 1.1 训练式（Trainable）

**做法**：
```
最大长度512，维度768
→ 初始化一个 512×768 的矩阵
→ 作为可训练参数随模型一起训练
```

**应用**：
- BERT、GPT等主流模型
- Facebook 2017年《Convolutional Sequence to Sequence Learning》

**外推性问题**：
- 预训练最大长度512，就只能处理512长度
- 解决方案：层次分解位置编码（苏剑林提出）

#### 1.2 三角式（Sinusoidal）

**公式**：
```
PE(pos, 2i)   = sin(pos / 10000^(2i/d_model))
PE(pos, 2i+1) = cos(pos / 10000^(2i/d_model))
```

**优点**：
1. 显式生成规律，可外推
2. 位置k可表示为位置i和位置j的组合（提供相对位置可能性）

**现状**：现在很少直接使用

#### 1.3 递归式（Recursive）

**核心思想**：用RNN/ODE建模位置编码

**FLOATER方案**（ICML 2020）：
- 用微分方程（ODE）建模
- 函数f可通过神经网络学习
- 称为"神经微分方程"

**优缺点**：
- ✅ 外推性好，灵活（三角函数是其特解）
- ❌ 牺牲并行性，有速度瓶颈

#### 1.4 相乘式（Multiplicative）

** unconventional做法**：
```
普通: 输入 + 位置编码
新式: 输入 × 位置编码（逐位相乘）
```

**实验结果**：似乎比相加效果更好（参考《中文语言模型研究：(1) 乘性位置编码》）

---

### 二、相对位置编码（Relative Position Encoding）

**核心思想**：在计算Attention时考虑相对距离，而非绝对位置

#### 2.1 经典式（Google）

**论文**：《Self-Attention with Relative Position Representations》

**改造方式**：
```
原始Attention: q_i · k_j
改造后: 
  - 去掉第一项位置
  - q_i保持不变
  - k_j改为相对位置向量R_{i-j}
  - 增加可训练的位置偏置
```

**关键**：只依赖于相对距离i-j，进行截断处理

**优势**：有限个编码可表达任意长度

#### 2.2 XLNET式

**来源**：Transformer-XL论文《Transformer-XL: Attentive Language Models Beyond a Fixed-Length Context》

**做法**：
```
完全展开Attention公式后：
- 替换q_i为可训练向量u
- 替换k_j为可训练向量v
- 直接去掉位置偏置b
```

**影响**：从此后相对位置编码只加到Attention矩阵，不加到输入上

#### 2.3 T5式

**论文**：《Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer》

**核心思想**：输入信息与位置信息解耦

**简化策略**：
```
原始4项注意力：
1. 输入-输入
2. 输入-位置  ← 删除
3. 位置-输入  ← 删除
4. 位置-位置  ← 保留，改为可训练标量
```

**分桶（Bucketing）处理**：
```
相对位置0-7：每个位置独立编码
相对位置8-11：共用一个编码
距离越远，共用范围越大
```

**类似方案**：TUPE（ICLR 2021）

#### 2.4 DeBERTa式

**论文**：《DeBERTa: Decoding-enhanced BERT with Disentangled Attention》

**与T5相反的策略**：
```
保留：输入-位置（第2、3项）
删除：位置-位置（第4项）
```

**重要洞察**：
- NLP大多数任务只需要相对位置
- 但有些场景绝对位置更有帮助

**EMD结构**（Enhanced Mask Decoder）：
```
Base版13层：
- 前11层：只用相对位置（Encoder）
- 后2层：加入绝对位置（Decoder）
- 下游微调：前11层 + 1层Decoder
```

**成就**：登上SuperGLUE榜首，超过T5

**槽点**：命名容易引起误解（Encoder/Decoder/E MD都是重名）

---

### 三、其他位置编码

#### 3.1 CNN式

**惊人发现**（ICLR 2020）：
- CNN模型的位置信息来自**Zero Padding**！
- 卷积核的各向异性重要，但根本是padding边界

**局限性**：
- 依赖CNN的局部性
- 不适用于Transformer的全局结构

#### 3.2 复数式（Complex Order）

**论文**：《Encoding word order in complex embeddings》（ICLR 2020）

**疯狂做法**：
1. 每个词有三组词向量
2. 位置编码公式：
   ```
   PE(j,k) = w_j × exp(i × t_j × k)
   ```
3. **直接用于复数模型**！
   - Embedding层是复数
   - Transformer每一层都是复数
   - 实现了复数版Fasttext、LSTM、CNN

**作者**：Benyou Wang（复数模型铁杆粉）

#### 3.3 融合式（苏剑林提出）

**核心创新**：绝对位置编码等价于相对位置编码

**推导过程**：
```
二维向量[x,y]看作复数
内积公式：⟨x,y⟩ = Re(x · ȳ)  （ȳ是y的共轭）

加入绝对位置编码：
x_m = [x,y] × exp(i × m × θ)
y_n = [x,y] × exp(i × n × θ)

计算内积：
⟨x_m, y_n⟩ = Re(x_m · ȳ_n)
           = Re([x,y] × exp(i×m×θ) · [x,y] × exp(-i×n×θ))
           = Re([x,y]² × exp(i×(m-n)×θ))
           
结果只依赖于相对位置(m-n)！
```

**方案**：
- 每两维为一组
- 乘以exp(i×n×θ)赋予绝对位置
- Attention运算时自动等价于相对位置

**状态**：初步实验可work，待充分验证

---

## 💡 个人思考

### 1. 位置编码的演进逻辑

```
绝对位置编码
    ├── 训练式（简单但无外推性）
    ├── 三角式（可外推但不够灵活）
    ├── 递归式（灵活但慢）
    └── 相乘式（待验证）
    
相对位置编码
    ├── 经典式（理论基础）
    ├── XLNET式（简化实践）
    ├── T5式（极致简化）
    └── DeBERTa式（反向尝试）
    
其他
    ├── CNN式（意外发现）
    ├── 复数式（极端方案）
    └── 融合式（理论优雅）
```

### 2. 实践建议

**如果你在做预训练模型**：
1. **首选**：训练式（BERT/GPT都在用，简单有效）
2. **需要长文本**：层次分解位置编码或ALiBi
3. **追求效果**：DeBERTa式（SuperGLUE已验证）
4. **想创新**：融合式（理论优雅，待验证）

**如果你在做下游任务**：
- 直接使用预训练模型的位置编码即可
- 除非有超长文本需求，否则不需要改

### 3. 有趣的现象

**科研就是枚举排列组合**：
```
展开式有4项：
1. 输入-输入
2. 输入-位置
3. 位置-输入
4. 位置-位置

T5：保留1、4，删除2、3
DeBERTa：保留1、2、3，删除4

哪个好？看实验结果！
```

**简单往往更好**：
- T5式最简单（只加一个偏置项），效果却很好
- 复杂方案（如复数式）理论优雅，但工程复杂

### 4. 未来方向

1. **超长文本**：如何高效处理100K+ tokens？
2. **动态长度**：如何自适应不同长度？
3. **多模态**：视觉Transformer的位置编码如何设计？
4. **理论与实践的gap**：为什么某些方案理论上好但效果一般？

---

## 📚 参考文献速览

| 序号 | 论文 | 核心贡献 |
|------|------|----------|
| [1] | Convolutional Sequence to Sequence Learning | 训练式位置编码早期应用 |
| [2] | Attention is All You Need | 三角式位置编码 |
| [3] | FLOATER (ICML 2020) | 神经微分方程建模位置编码 |
| [5] | Self-Attention with Relative Position | 经典相对位置编码 |
| [6] | Transformer-XL | XLNET式位置编码 |
| [8] | T5 | 最简单的相对位置编码 |
| [9] | TUPE (ICLR 2021) | 类似T5的位置编码 |
| [10] | DeBERTa (ICLR 2021) | 反向策略，SuperGLUE榜首 |
| [13] | How Much Position Information Do CNNs Encode? | Zero Padding泄露位置信息 |
| [14] | Encoding word order in complex embeddings | 复数式位置编码 |

---

## 🔗 延伸阅读

- **ALiBi**: Attention with Linear Biases（另一种简洁的位置编码方案）
- **RoPE**: Rotary Position Embedding（旋转位置编码，现在LLaMA等在用）
- **NTK-aware scaling**: 扩展位置编码外推能力的技术

---

**本文档由 Article Saver Skill 自动生成**  
**生成时间: 2026-02-14 16:50:00**
