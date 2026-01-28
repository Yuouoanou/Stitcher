# Stitcher 项目代码分析（中文版）

## 项目概述

Stitcher 是一个基于反馈驱动的数据增强方法，用于改进目标检测模型的训练，特别是针对小目标检测。该项目基于 Facebook 的 maskrcnn-benchmark 实现。

**核心思想**：将多张图像缩小后拼接成同样大小的图像，让模型看到更多的小目标，并根据训练损失反馈动态调整是否使用拼接图像。

**论文**：[Stitcher: Feedback-driven Data Provider for Object Detection](https://arxiv.org/abs/2004.12432)

---

## 项目目录结构

```
Stitcher/
├── maskrcnn_benchmark/          # 核心代码库
│   ├── config/                  # 配置文件模块
│   ├── data/                    # 数据加载和处理
│   ├── engine/                  # 训练和推理引擎
│   ├── modeling/                # 模型定义
│   ├── solver/                  # 优化器和学习率调度
│   ├── structures/              # 数据结构（如 BoundingBox）
│   └── utils/                   # 工具函数
├── configs/                     # 配置文件（YAML）
├── tools/                       # 训练和测试脚本
├── tests/                       # 单元测试
└── docker/                      # Docker 配置
```

---

## 核心文件详细说明

### 1. 入口脚本

#### `tools/train_net.py`
**作用**：训练的主入口脚本
- 解析命令行参数
- 加载配置文件
- 初始化模型、优化器、数据加载器
- 调用训练循环
- 保存检查点

**使用方法**：
```bash
python tools/train_net.py --config-file configs/e2e_faster_rcnn_R_50_C4_1x.yaml
```

#### `tools/test_net.py`
**作用**：模型推理和评估的入口脚本
- 加载训练好的模型
- 在测试集上进行推理
- 计算评估指标（mAP等）

---

### 2. 配置系统

#### `maskrcnn_benchmark/config/defaults.py`
**作用**：定义所有配置参数的默认值
- 模型配置（MODEL）
- 数据集配置（DATASETS）
- 训练配置（SOLVER）
- **Stitcher 特有配置（STITCHER）**：
  - `NUM_IMAGES_STITCH`: 拼接的图像数量（默认4张，形成2x2网格）
  - `BATCH_STITCH`: 是否使用批次级拼接
  - `USE_PAD`: 是否使用填充
  - `FEEDBACK`: 反馈类型（'reg_loss' 或 'cls_loss'）
  - `THRESH`: 小目标比例阈值，决定何时使用拼接图像

#### `maskrcnn_benchmark/config/paths_catalog.py`
**作用**：数据集路径的中心化管理
- 定义各种数据集的图像和标注文件路径
- 支持 COCO、VOC、Cityscapes 等数据集
- **重要**：添加自定义数据集需要在这里注册

---

### 3. 数据处理模块

#### `maskrcnn_benchmark/data/build.py`
**作用**：构建数据加载器
- `make_data_loader()`: 创建训练/测试数据加载器
- 支持分布式训练
- **Stitcher 关键**：可以创建两个数据加载器（普通图像和拼接图像）

#### `maskrcnn_benchmark/data/datasets/coco.py`
**作用**：COCO 数据集的加载类
- 继承自 torchvision 的 CocoDetection
- 解析 COCO JSON 格式的标注文件
- 返回图像、目标框、类别等信息
- 支持实例分割的 mask 标注

**关键方法**：
- `__getitem__()`: 获取单个样本
- 将 COCO 的类别 ID 映射为连续的 ID

#### `maskrcnn_benchmark/data/datasets/voc.py`
**作用**：Pascal VOC 数据集的加载类
- 解析 XML 格式的标注文件
- 定义了 VOC 的 20 个类别

#### `maskrcnn_benchmark/data/transforms/transforms.py`
**作用**：数据增强和预处理
- `Resize`: 图像缩放
- `RandomHorizontalFlip`: 水平翻转
- `RandomVerticalFlip`: 垂直翻转
- `ColorJitter`: 颜色抖动
- `ToTensor`: 转换为张量
- `Normalize`: 归一化

#### `maskrcnn_benchmark/data/transforms/build.py`
**作用**：构建数据增强管道
- **Stitcher 关键**：当 `batch_stitch=True` 时，会将图像尺寸减半（因为4张小图拼成1张）

---

### 4. Stitcher 核心实现

#### `maskrcnn_benchmark/structures/image_list.py`
**作用**：图像列表的数据结构，包含 Stitcher 的拼接逻辑

**关键函数**：

1. `to_image_list_synthesize_4()` (第 69-168 行)
   - 将 4 张图像拼接成 2x2 网格
   - 缩小每张图像到原来的一半
   - 调整目标框的坐标（根据拼接位置偏移）
   - 调整分割 mask 的坐标

2. `to_image_list_synthesize_batchstitch()` (第 171-235 行)
   - 批次级拼接：对整个 batch 中的每张图像都进行处理
   - 不拼接成 2x2 网格，而是单独缩小每张图像
   - 适用于 `BATCH_STITCH=True` 的情况

3. `to_image_list_synthesize()` (第 238-244 行)
   - 根据配置选择使用哪种拼接方式

**拼接示例**：
```
原始：4张图像，每张 800x800
  [Img1] [Img2] [Img3] [Img4]

拼接后：1张图像 800x800
  [Img1_400x400 | Img2_400x400]
  [Img3_400x400 | Img4_400x400]
```

#### `maskrcnn_benchmark/engine/trainer.py`
**作用**：训练循环的核心逻辑

**Stitcher 的训练策略**（第 69-80 行）：
```python
ratio_small = 0.0  # 小目标损失比例
for iteration in range(start_iter, max_iter):
    if ratio_small < cfg.STITCHER.THRESH:
        # 小目标损失高于阈值 → 使用拼接图像
        images, targets, _ = next(data_loader_unregular_iter)
        ratio_stitch = cfg.STITCHER.NUM_IMAGES_STITCH
    else:
        # 小目标损失低于阈值 → 使用普通图像
        images, targets, _ = next(data_loader_regular_iter)
        ratio_stitch = 1
```

**反馈机制**：
- 模型返回 `loss_dict` 和 `ratio_small`
- `ratio_small` 表示小目标的损失占比
- 根据这个比例动态决定下一次迭代使用哪种数据

---

### 5. 模型相关

#### `maskrcnn_benchmark/modeling/detector/generalized_rcnn.py`
**作用**：通用 R-CNN 检测器的实现
- 前向传播逻辑
- 接收 `ratio_stitch` 参数并传递给各个组件
- 返回损失字典和小目标损失比例

#### `maskrcnn_benchmark/modeling/rpn/rpn.py`
**作用**：Region Proposal Network (RPN)
- 生成候选区域
- 根据 `ratio_stitch` 调整正负样本采样数量

#### `maskrcnn_benchmark/modeling/roi_heads/roi_heads.py`
**作用**：ROI Head（检测头）
- 对候选区域进行分类和回归
- 根据 `ratio_stitch` 调整采样策略

#### `maskrcnn_benchmark/modeling/balanced_positive_negative_sampler.py`
**作用**：平衡正负样本采样
- **Stitcher 修改**：当使用拼接图像时，调整每张图像的样本数
- `num_pos = batch_size_per_image // ratio_stitch * positive_fraction`

---

### 6. 工具和辅助

#### `maskrcnn_benchmark/utils/checkpoint.py`
**作用**：模型检查点的保存和加载

#### `maskrcnn_benchmark/utils/logger.py`
**作用**：日志记录

#### `maskrcnn_benchmark/data/collate_batch.py`
**作用**：批次数据的整理
- **Stitcher 关键**：调用 `to_image_list_synthesize()` 进行图像拼接

---

## Stitcher 算法流程总结

### 初始化阶段
1. 创建两个数据加载器：
   - `data_loader_regular`: 普通图像（原始大小）
   - `data_loader_unregular`: 拼接图像（4张拼成1张）

### 训练阶段
1. **初始状态**：`ratio_small = 0`，使用拼接图像
2. **前向传播**：
   - 输入：拼接后的图像和调整后的标注
   - 输出：损失和小目标损失比例 `ratio_small`
3. **反馈决策**：
   - 如果 `ratio_small < THRESH`（默认 0.1）：继续使用拼接图像
   - 如果 `ratio_small >= THRESH`：切换到普通图像
4. **采样调整**：
   - 使用拼接图像时，每张子图的正负样本数减少为原来的 1/4
   - 保证总的样本数与普通训练一致

### 优势
- **小目标增强**：拼接后的图像中，原本的中大型目标变成小目标
- **动态调整**：根据训练进度自适应切换数据源
- **几乎无额外开销**：不需要改变模型结构，推理时不使用拼接

---

## 配置文件说明

### 基础配置示例 (`configs/e2e_faster_rcnn_R_50_C4_1x.yaml`)

```yaml
MODEL:
  META_ARCHITECTURE: "GeneralizedRCNN"
  WEIGHT: "catalog://ImageNetPretrained/MSRA/R-50"

DATASETS:
  TRAIN: ("coco_2014_train", "coco_2014_valminusminival")
  TEST: ("coco_2014_minival",)

SOLVER:
  BASE_LR: 0.01
  WEIGHT_DECAY: 0.0001
  STEPS: (120000, 160000)
  MAX_ITER: 180000
  IMS_PER_BATCH: 8
```

### Stitcher 配置（在 defaults.py 中定义）

```yaml
STITCHER:
  NUM_IMAGES_STITCH: 4           # 拼接图像数量
  BATCH_STITCH: False            # 是否批次级拼接
  USE_PAD: False                 # 是否使用填充
  FEEDBACK: 'reg_loss'           # 反馈类型
  THRESH: 0.1                    # 切换阈值
```

---

## 支持的数据集格式

### 1. COCO 格式
- **标注文件**：JSON 格式
- **结构**：
  ```json
  {
    "images": [...],
    "annotations": [...],
    "categories": [...]
  }
  ```
- **坐标格式**：`[x, y, width, height]`（左上角坐标 + 宽高）

### 2. Pascal VOC 格式
- **标注文件**：XML 格式
- **目录结构**：
  ```
  VOC2007/
  ├── Annotations/    # XML 标注文件
  ├── JPEGImages/     # 图像文件
  └── ImageSets/      # 数据集划分
      └── Main/
          ├── train.txt
          ├── val.txt
          └── test.txt
  ```

---

## 数据集注册流程

要使用自定义数据集，需要在 `maskrcnn_benchmark/config/paths_catalog.py` 中注册：

```python
DATASETS = {
    "my_dataset_train": {
        "img_dir": "path/to/images",
        "ann_file": "path/to/annotations.json"
    },
    "my_dataset_val": {
        "img_dir": "path/to/images",
        "ann_file": "path/to/annotations.json"
    }
}
```

然后在配置文件中使用：

```yaml
DATASETS:
  TRAIN: ("my_dataset_train",)
  TEST: ("my_dataset_val",)
```

---

## 总结

### 关键创新点
1. **图像拼接**：将多张图像缩小后拼接，增加小目标数量
2. **反馈机制**：根据训练损失动态选择数据源
3. **无推理开销**：训练时拼接，推理时使用原始图像

### 主要代码修改
1. `image_list.py`：拼接图像的核心实现
2. `trainer.py`：双数据加载器和反馈决策
3. `balanced_positive_negative_sampler.py`：采样数量调整
4. `config/defaults.py`：Stitcher 相关配置

### 适用场景
- 小目标检测任务
- 需要提升小目标 AP 的场景
- COCO、VOC 等标准数据集
