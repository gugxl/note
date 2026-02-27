# 如何用Transformer来做目标检测？一文简述DERT及其变体

> **原文**: [如何用Transformer来做目标检测？一文简述DERT及其变体](https://mp.weixin.qq.com/s/AFqe8keKi46BlBl8MxkDCg)  
> **作者**: 张一帆（华南理工大学本科生）  
> **来源**: PaperWeekly  
> **发布时间**: 2021年左右  
> **整理时间**: 2026-02-14  
> **分类**: AI-ML  
> **标签**: Transformer, DETR, 目标检测, 计算机视觉, Deep Learning

---

## 📌 一句话总结

本文综述了DETR（基于Transformer的端到端目标检测器）及其4个重要变体：ViT-FRCNN、TSP-FCOS/RCNN、Deformable DETR、ACT，分析了各自的改进点、优缺点及实验效果。

---

## 🎯 核心要点

### 1. DETR 的核心贡献与局限

**贡献：**
- ✅ 首次将Transformer应用于目标检测
- ✅ 端到端训练，无需NMS等后处理
- ✅ 简洁优雅，实现简单

**局限：**
- ❌ 训练周期长（比Faster-RCNN慢20倍）
- ❌ 小物体检测效果差
- ❌ 收敛速度慢（attention map从均匀到稀疏耗时）

### 2. 四大变体改进方向

| 模型 | 核心改进 | 主要优势 |
|------|---------|----------|
| **ViT-FRCNN** | ViT + Faster-RCNN结合 | 利用patch token的局部信息，无需decoder |
| **TSP-FCOS/RCNN** | Encoder-only + FPN | 去除cross-attention，融入传统检测方法 |
| **Deformable DETR** | 可变形注意力机制 | 关注稀疏空间位置，训练快50倍 |
| **ACT** | 自适应聚类Transformer | 通过LSH聚类减少计算量 |

### 3. 关键问题与解决方案

**问题1：DETR为什么收敛慢？**
- 主要原因：decoder中的cross-attention难以稀疏化
- 解决：TSP系列直接去掉decoder，只用encoder

**问题2：小物体检测差？**
- 原因：高分辨率特征图计算量太大（O(n²)复杂度）
- 解决：Deformable DETR只关注稀疏采样点

**问题3：计算量大？**
- 解决：ACT通过聚类原型减少key的数量

---

## 📝 详细内容

### 一、DETR（基础模型）

**论文**: End-to-End Object Detection with Transformers (ECCV 2020)  
**代码**: https://github.com/facebookresearch/detr

**核心思想**：
- 将目标检测视为**集合预测（set prediction）**问题
- 使用二分图匹配（Hungarian matching）替代NMS
- 无需anchor生成，端到端训练

**结构**：
```
图像 → CNN Backbone → Transformer Encoder → Transformer Decoder → 预测框+类别
```

**存在的问题**：
1. 训练周期长（500 epochs）
2. 小物体检测效果不佳
3. Attention map收敛慢（从均匀到稀疏）

---

### 二、ViT-FRCNN

**论文**: Toward Transformer-Based Object Detection  
**核心思想**：ViT + Faster-RCNN结合

**改进点**：
1. 直接用ViT的encoder提取特征，无需CNN backbone
2. 将patch token重组为feature map
3. 使用Faster-RCNN的检测头（RPN + RoI + 分类/回归）

**特点**：
- 保留了Transformer的全局建模能力
- 利用了Faster-RCNN的局部检测优势
- 但未与DETR进行深入比较

---

### 三、TSP-FCOS & TSP-RCNN

**论文**: Rethinking Transformer-based Set Prediction for Object Detection  
**核心思想**：研究DETR优化困难的原因并提出解决方案

#### 3.1 DETR收敛慢的根本原因

**实验发现**：
- Hungarian loss影响较小
- **Cross-attention是罪魁祸首**：即使训练100个epoch，attention的稀疏性仍在增加，未收敛

**原因分析**：
- Attention map需要从均匀分布学到稀疏分布
- Cross-attention难以快速稀疏化

#### 3.2 Encoder-only架构

**思路**：去掉decoder，encoder直接输出预测

**实验结果**：
- AP下降不多
- **小物体检测显著提升**
- 但大物体检测效果下降

**原因**：
- 大物体包含太多潜在匹配点，encoder难以处理
- 单一特征尺度对不同尺度物体不鲁棒

#### 3.3 融入FPN的解决方案

**TSP-FCOS**：
- Backbone → FPN → Transformer Encoder → 检测头
- 从特征金字塔中提取FoI（Feature of Interest）

**TSP-RCNN**：
- Backbone → FPN → RoIAlign → Transformer Encoder → 检测头
- 从多尺度特征中提取RoI

**特殊设计**：
- 针对RoI的特殊位置编码（基于box中心点、长宽）
- 融入FCOS/RCNN的匹配方法，提高匹配效率

**实验效果**：
- 训练速度和准确性都优于DETR
- 收敛速度显著提升

---

### 四、Deformable DETR

**论文**: Deformable DETR: Deformable Transformers for End-to-End Object Detection (ICLR 2021)  
**代码**: https://github.com/DeppMeng/Deformable-DETR

#### 4.1 主要问题

1. **训练周期长**：比Faster-RCNN慢20倍
2. **小物体检测差**：高分辨率导致O(n²)复杂度，内存和计算量剧增

#### 4.2 可变形注意力（Deformable Attention）

**核心思想**：
- 传统attention：密集连接，但需学到稀疏知识
- 可变形attention：直接定义需要学习的知识为稀疏的

**关键区别**：
- 传统：Attention weight基于query和key的pairwise对比
- 可变形：只依赖于query，直接学习采样的offset

**实现细节**：
- 每个query映射到R^(M×K×3)空间
  - M：attention head数
  - K：预设key的数量
  - 前2K个通道：采样的offset（决定query找哪些key）
  - 最后K个通道：keys的贡献权重（直接回归）

- 使用双线性插值处理非整数坐标

#### 4.3 多尺度可变形注意力

- 提取ResNet多层特征构成多尺度特征图
- 每层选K个点，共ML个点
- 归一化reference坐标到[0,1]
- 重新映射回各层真实坐标用于索引

#### 4.4 Deformable Transformer结构

**Encoder**：
- 输入输出保持相同分辨率的多尺度特征图
- Query和key都是多尺度特征图上的像素点
- Reference point就是像素点本身
- 使用可变形attention处理

**Decoder**：
- Cross-attention替换为可变形attention
- 保持self-attention不变（object query之间充分交互）
- Reference point作为预测box的初始中心点
- 回归目标设为offset而非直接预测长宽

**特色**：
- Iterative bbox refinement
- Two-stage策略

#### 4.5 实验效果

- 同等参数量下，训练50个epoch即可达到DETR 500个epoch的效果
- 小物体检测显著提升
- 速度与准确率tradeoff优秀

**争议**：
- K=1时退化为deformable conv
- 有人认为"如果attention改得太多，就回到传统检测老路上了"

---

### 五、ACT（Adaptive Clustering Transformer）

**论文**: End-to-End Object Detection with Adaptive Clustering Transformers

#### 5.1 Motivation

**观察1：Attention Map冗余**
- DETR encoder输出中，相近点的attention map非常相似

**观察2：特征相似度随层数增加**
- Encoder不断做自注意力，包含更多全局信息
- 深层特征越来越相似

#### 5.2 自适应聚类Transformer

**核心思想**：对相似特征图聚类，计算聚类中心（prototype）

**好处**：
- 用原型特征代替query做attention
- 大大减少参数量
- 时间复杂度从O(n²)降到O(n×c)（c是聚类数）

**关键技术：E2LSH（Locality Sensitivity Hashing）**

**哈希函数**：
```
h(v) = ⌊(a·v + b) / w⌋
```
- a：随机向量
- b：随机偏移
- w：控制间距的超参数

**过程**：
1. 做P次哈希增加可信度
2. 相同哈希值的特征进入同一cell
3. 对cell中特征求平均得到prototype
4. 用prototype代替query计算attention

**超参数选择**：
- 随机采样1000张图像
- 计算真实attention map与ACT产生attention map的MSE
- 选择合适的超参数

#### 5.3 实验效果

- 速度-准确性tradeoff优于传统DETR和Kmeans聚类
- 能较好近似DETR的attention map
- 但小物体检测更差（丢失局部信息）

---

## 💻 关键公式与代码思路

### 可变形注意力公式

```
DeformAttn(z_q, p_q, x) = Σ_m W_m [Σ_k A_mqk · W_m' x(p_q + Δp_mqk)]

其中：
- z_q: query
- p_q: reference point（参考点）
- Δp_mqk: 学习的偏移量
- A_mqk: 注意力权重
- x: 输入特征
```

### 多尺度可变形注意力

```
MSDeformAttn(z_q, p̂_q, {x^l}_{l=1}^L) = 
    Σ_m W_m [Σ_{l=1}^L Σ_{k=1}^K A_mlqk · W_m' x^l(φ_l(p̂_q) + Δp_mlqk)]

其中：
- L: 多尺度层数
- K: 每层采样点数
- φ_l: 归一化坐标映射回第l层
```

---

## 💡 个人思考

### 1. DETR的意义

DETR的价值不仅在于提出了一种新的检测范式，更在于证明了**纯Transformer可以做好检测任务**，为后续研究打开了一扇门。

### 2. 变体的演进方向

从DETR到各变体，演进路线很清晰：

```
DETR (原始) 
    ↓ 太慢，需要加速
ViT-FRCNN (换backbone) 
    ↓ 还是慢，去掉decoder
TSP (Encoder-only + FPN)
    ↓ attention太密集，要稀疏
Deformable DETR (稀疏采样)
    ↓ 计算量还是大，要聚类
ACT (自适应聚类)
```

### 3. 值得思考的问题

**Q1: Deformable DETR还是Transformer吗？**
- 核心attention机制已经大幅改变
- 更像可变形卷积的扩展
- "改着改着就回到传统检测"的批评有一定道理

**Q2: 速度和精度的tradeoff**
- 所有改进都在速度和精度间找平衡
- 实际应用中，Deformable DETR可能是最佳选择
- 但学术价值上，DETR的开创性意义最大

**Q3: 小物体检测的困境**
- 高分辨率 → 计算量大
- 低分辨率 → 小物体检测差
- 多尺度是解决方案，但增加了复杂度

### 4. 实践建议

**如果要做目标检测项目：**
1. **快速验证**：用YOLOv8或Faster-RCNN
2. **追求精度**：尝试Deformable DETR
3. **学术研究**：从DETR出发，探索新的变体

**如果要研究Transformer in Detection：**
1. 深入理解DETR的set prediction思想
2. 掌握二分图匹配（Hungarian algorithm）
3. 理解各变体的改进动机
4. 关注最新的DINO、DAB-DETR等工作

---

## 📚 相关文章

- DETR: End-to-End Object Detection with Transformers (ECCV 2020)
- Deformable DETR (ICLR 2021)
- ViT: An Image is Worth 16x16 Words (ICLR 2021)
- TSP-FCOS & TSP-RCNN: Rethinking Transformer-based Set Prediction
- ACT: End-to-End Object Detection with Adaptive Clustering Transformers

---

## 🔗 延伸阅读

- DINO: DETR with Improved DeNoising Anchor Boxes for End-to-End Object Detection
- DAB-DETR: Dynamic Anchor Boxes are Better Queries for DETR
- Conditional DETR for Fast Training Convergence
- Anchor DETR: Query Design for Transformer-Based Detector

---

**本文档由 Article Saver Skill 自动生成**  
**生成时间: 2026-02-14 16:35:00**
