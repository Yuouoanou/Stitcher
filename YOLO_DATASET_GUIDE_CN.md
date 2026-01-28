# 在 Stitcher 项目上运行 YOLO 格式数据集指南

本指南详细说明如何将 YOLO 格式的数据集转换并用于 Stitcher 项目的训练。

## 目录
1. [YOLO 格式说明](#yolo-格式说明)
2. [数据集准备](#数据集准备)
3. [格式转换](#格式转换)
4. [数据集注册](#数据集注册)
5. [配置文件设置](#配置文件设置)
6. [训练模型](#训练模型)
7. [常见问题](#常见问题)

---

## YOLO 格式说明

### YOLO 格式特点
- 每张图片对应一个 `.txt` 标注文件
- 文件名与图片名相同（仅扩展名不同）
- 每行代表一个目标框

### 标注格式
```
<class_id> <x_center> <y_center> <width> <height>
```

**参数说明**：
- `class_id`: 类别索引（从 0 开始）
- `x_center`: 目标框中心点 x 坐标（归一化，范围 0-1）
- `y_center`: 目标框中心点 y 坐标（归一化，范围 0-1）
- `width`: 目标框宽度（归一化，范围 0-1）
- `height`: 目标框高度（归一化，范围 0-1）

**归一化说明**：
- x 坐标和宽度除以图像宽度
- y 坐标和高度除以图像高度

### 示例

**图像信息**：
- 文件名：`image001.jpg`
- 尺寸：640×480 像素

**标注文件**：`image001.txt`
```
0 0.5 0.5 0.3 0.4
1 0.2 0.3 0.15 0.2
```

**解释**：
- 第一个目标：类别 0，中心点 (320, 240)，尺寸 192×192
- 第二个目标：类别 1，中心点 (128, 144)，尺寸 96×96

---

## 数据集准备

### 1. YOLO 数据集目录结构

```
my_yolo_dataset/
├── images/
│   ├── train/
│   │   ├── image001.jpg
│   │   ├── image002.jpg
│   │   └── ...
│   └── val/
│       ├── image101.jpg
│       ├── image102.jpg
│       └── ...
├── labels/
│   ├── train/
│   │   ├── image001.txt
│   │   ├── image002.txt
│   │   └── ...
│   └── val/
│       ├── image101.txt
│       ├── image102.txt
│       └── ...
└── classes.txt
```

### 2. 创建类别文件

创建 `classes.txt` 文件，每行一个类别名，顺序对应类别 ID：

```
person
car
bicycle
dog
cat
```

**注意**：
- 类别顺序必须与标注文件中的 `class_id` 一致
- 第一行对应 class_id=0，第二行对应 class_id=1，以此类推

---

## 格式转换

### 使用转换脚本

项目提供了 `tools/yolo_to_coco.py` 脚本用于格式转换。

### 转换训练集

```bash
python tools/yolo_to_coco.py \
    --images-dir /path/to/my_yolo_dataset/images/train \
    --labels-dir /path/to/my_yolo_dataset/labels/train \
    --classes /path/to/my_yolo_dataset/classes.txt \
    --output datasets/my_dataset/annotations/instances_train.json \
    --split train
```

### 转换验证集

```bash
python tools/yolo_to_coco.py \
    --images-dir /path/to/my_yolo_dataset/images/val \
    --labels-dir /path/to/my_yolo_dataset/labels/val \
    --classes /path/to/my_yolo_dataset/classes.txt \
    --output datasets/my_dataset/annotations/instances_val.json \
    --split val
```

### 参数说明

| 参数 | 说明 | 必需 |
|------|------|------|
| `--images-dir` | 图像文件所在目录 | 是 |
| `--labels-dir` | YOLO 标注文件所在目录 | 是 |
| `--classes` | 类别文件路径 | 是 |
| `--output` | 输出的 COCO JSON 文件路径 | 是 |
| `--split` | 数据集划分名称（train/val/test） | 否，默认 train |

### 转换后的目录结构

```
datasets/
└── my_dataset/
    ├── images/
    │   ├── train/          # 复制或链接原始 YOLO 图像
    │   │   ├── image001.jpg
    │   │   └── ...
    │   └── val/
    │       ├── image101.jpg
    │       └── ...
    └── annotations/        # 转换后的 COCO JSON
        ├── instances_train.json
        └── instances_val.json
```

**建议**：使用软链接节省空间

```bash
ln -s /path/to/my_yolo_dataset/images/train datasets/my_dataset/images/train
ln -s /path/to/my_yolo_dataset/images/val datasets/my_dataset/images/val
```

---

## 数据集注册

### 1. 编辑 paths_catalog.py

打开文件：`maskrcnn_benchmark/config/paths_catalog.py`

### 2. 在 DATASETS 字典中添加数据集

找到 `DatasetCatalog` 类中的 `DATASETS` 字典，添加：

```python
DATASETS = {
    # ... 其他数据集 ...
    
    # 你的自定义数据集
    "my_dataset_train": {
        "img_dir": "my_dataset/images/train",
        "ann_file": "my_dataset/annotations/instances_train.json"
    },
    "my_dataset_val": {
        "img_dir": "my_dataset/images/val",
        "ann_file": "my_dataset/annotations/instances_val.json"
    },
}
```

**注意**：
- 路径是相对于 `DatasetCatalog.DATA_DIR` 的（默认是 `datasets/`）
- 可以使用绝对路径：`"img_dir": "/absolute/path/to/images"`

---

## 配置文件设置

### 1. 创建配置文件

复制一个基础配置文件并修改：

```bash
cp configs/e2e_faster_rcnn_R_50_FPN_1x.yaml configs/my_dataset/e2e_faster_rcnn_R_50_FPN_1x.yaml
```

### 2. 编辑配置文件

打开 `configs/my_dataset/e2e_faster_rcnn_R_50_FPN_1x.yaml`，修改以下内容：

```yaml
MODEL:
  META_ARCHITECTURE: "GeneralizedRCNN"
  WEIGHT: "catalog://ImageNetPretrained/MSRA/R-50"  # 预训练权重
  RPN:
    PRE_NMS_TOP_N_TEST: 6000
    POST_NMS_TOP_N_TEST: 1000
  ROI_HEADS:
    NUM_CLASSES: 6  # 修改为你的类别数（包括背景类，即类别数+1）

DATASETS:
  TRAIN: ("my_dataset_train",)      # 训练集名称
  TEST: ("my_dataset_val",)         # 验证集名称

SOLVER:
  BASE_LR: 0.01                     # 基础学习率
  WEIGHT_DECAY: 0.0001
  STEPS: (120000, 160000)           # 学习率衰减步数
  MAX_ITER: 180000                  # 最大迭代次数
  IMS_PER_BATCH: 8                  # 每批图像数
  CHECKPOINT_PERIOD: 5000           # 检查点保存间隔

INPUT:
  MIN_SIZE_TRAIN: (800,)            # 训练时图像最小边
  MAX_SIZE_TRAIN: 1333              # 训练时图像最大边
  MIN_SIZE_TEST: 800                # 测试时图像最小边
  MAX_SIZE_TEST: 1333               # 测试时图像最大边

OUTPUT_DIR: "./output/my_dataset"   # 输出目录

# Stitcher 配置（可选）
STITCHER:
  NUM_IMAGES_STITCH: 4              # 拼接图像数量（2x2网格）
  BATCH_STITCH: False               # 是否使用批次级拼接
  FEEDBACK: 'reg_loss'              # 反馈类型：'reg_loss' 或 'cls_loss'
  THRESH: 0.1                       # 小目标损失阈值
```

### 3. 关键参数说明

#### 类别数量
```yaml
MODEL:
  ROI_HEADS:
    NUM_CLASSES: 6  # 你的类别数 + 1（背景类）
```

**计算方法**：
- 如果有 5 个目标类别 → `NUM_CLASSES = 6`
- COCO（80类） → `NUM_CLASSES = 81`

#### 学习率和迭代次数

根据数据集大小调整：

| 数据集大小 | MAX_ITER | STEPS | BASE_LR |
|----------|----------|-------|---------|
| 小（<5K）   | 50000    | (30000, 40000) | 0.001 |
| 中（5K-20K）| 90000    | (60000, 80000) | 0.005 |
| 大（>20K）  | 180000   | (120000, 160000) | 0.01 |

#### 批次大小

根据 GPU 显存调整：

| GPU 显存 | IMS_PER_BATCH | 建议模型 |
|---------|---------------|---------|
| 8GB     | 2             | R-50-C4 |
| 11GB    | 4             | R-50-FPN |
| 16GB    | 8             | R-50-FPN |
| 24GB+   | 16            | R-101-FPN |

#### Stitcher 参数

```yaml
STITCHER:
  NUM_IMAGES_STITCH: 4      # 每次拼接的图像数（默认4，形成2x2网格）
  BATCH_STITCH: False       # True: 批次级拼接; False: 空间拼接
  FEEDBACK: 'reg_loss'      # 'reg_loss': 使用回归损失; 'cls_loss': 使用分类损失
  THRESH: 0.1               # 小目标损失比例阈值，低于此值使用拼接图像
```

---

## 训练模型

### 1. 单 GPU 训练

```bash
python tools/train_net.py \
    --config-file configs/my_dataset/e2e_faster_rcnn_R_50_FPN_1x.yaml
```

### 2. 多 GPU 训练

```bash
export NGPUS=4
python -m torch.distributed.launch \
    --nproc_per_node=$NGPUS \
    tools/train_net.py \
    --config-file configs/my_dataset/e2e_faster_rcnn_R_50_FPN_1x.yaml
```

### 3. 从检查点恢复训练

```bash
python tools/train_net.py \
    --config-file configs/my_dataset/e2e_faster_rcnn_R_50_FPN_1x.yaml \
    MODEL.WEIGHT output/my_dataset/model_0050000.pth
```

### 4. 训练参数覆盖

可以在命令行直接覆盖配置参数：

```bash
python tools/train_net.py \
    --config-file configs/my_dataset/e2e_faster_rcnn_R_50_FPN_1x.yaml \
    SOLVER.IMS_PER_BATCH 4 \
    SOLVER.BASE_LR 0.005 \
    OUTPUT_DIR ./output/my_experiment
```

---

## 模型推理和评估

### 1. 评估模型

```bash
python tools/test_net.py \
    --config-file configs/my_dataset/e2e_faster_rcnn_R_50_FPN_1x.yaml \
    MODEL.WEIGHT output/my_dataset/model_final.pth
```

### 2. 多 GPU 评估

```bash
export NGPUS=4
python -m torch.distributed.launch \
    --nproc_per_node=$NGPUS \
    tools/test_net.py \
    --config-file configs/my_dataset/e2e_faster_rcnn_R_50_FPN_1x.yaml \
    MODEL.WEIGHT output/my_dataset/model_final.pth
```

### 3. 查看评估结果

评估结果会保存在输出目录中：
```
output/my_dataset/
└── inference/
    └── my_dataset_val/
        └── coco_results.pth    # 评估结果
```

---

## 常见问题

### Q1: 转换后的 JSON 文件很大怎么办？

**A**: COCO JSON 文件可能会比较大。可以：
1. 使用压缩：`gzip instances_train.json`
2. 修改代码不保存 `indent`：`json.dump(coco_data, f)`
3. 不影响训练，只是占用磁盘空间

### Q2: 我的数据集没有验证集怎么办？

**A**: 可以从训练集中划分：

```python
# 在 yolo_to_coco.py 中添加随机划分逻辑
import random
random.seed(42)
random.shuffle(image_files)

# 80% 训练，20% 验证
split_idx = int(len(image_files) * 0.8)
train_files = image_files[:split_idx]
val_files = image_files[split_idx:]
```

### Q3: 如何调整 Stitcher 的效果？

**A**: 调整这些参数：

1. **`NUM_IMAGES_STITCH`**: 
   - 值越大，小目标越多，但图像更小
   - 推荐：4（2×2）或 9（3×3）

2. **`THRESH`**:
   - 值越小，使用拼接图像的时间越长
   - 推荐：0.05-0.15

3. **`FEEDBACK`**:
   - 'reg_loss': 适用于目标框回归较难的情况
   - 'cls_loss': 适用于类别分类较难的情况

### Q4: 类别数量设置错误会怎样？

**A**: 会导致训练崩溃或精度为 0。请确保：
```yaml
MODEL:
  ROI_HEADS:
    NUM_CLASSES: N + 1  # N 是你的类别数
```

### Q5: 显存不足怎么办？

**A**: 尝试以下方法：
1. 减少 `IMS_PER_BATCH`
2. 减小图像尺寸：`MIN_SIZE_TRAIN: (600,)`, `MAX_SIZE_TRAIN: 1000`
3. 使用更小的主干网络：R-50-C4 代替 R-50-FPN
4. 启用混合精度训练（已默认启用）

### Q6: 如何查看训练日志？

**A**: 日志保存在输出目录：
```bash
tail -f output/my_dataset/log.txt
```

或使用 TensorBoard（如果配置）：
```bash
tensorboard --logdir output/my_dataset
```

### Q7: YOLO 标注文件中有空行或格式错误怎么办？

**A**: 转换脚本会自动跳过错误行，并打印警告信息。建议检查数据质量：

```bash
# 检查空的标注文件
find labels/ -type f -empty

# 检查格式错误
python tools/yolo_to_coco.py ... 2>&1 | grep Warning
```

### Q8: 如何使用预训练模型？

**A**: 在配置文件中指定：

```yaml
MODEL:
  WEIGHT: "catalog://ImageNetPretrained/MSRA/R-50"  # ImageNet 预训练
  # 或使用本地路径
  # WEIGHT: "/path/to/model.pth"
```

可用的预训练模型：
- `catalog://ImageNetPretrained/MSRA/R-50`
- `catalog://ImageNetPretrained/MSRA/R-101`
- `catalog://ImageNetPretrained/FAIR/X-101-32x8d`

---

## 完整示例

### 场景：训练一个包含 3 个类别的车辆检测器

#### 1. 准备数据

```
vehicle_dataset/
├── images/
│   ├── train/ (1000 张图片)
│   └── val/ (200 张图片)
├── labels/
│   ├── train/ (1000 个 txt 文件)
│   └── val/ (200 个 txt 文件)
└── classes.txt
```

**classes.txt**:
```
car
truck
bus
```

#### 2. 转换格式

```bash
# 转换训练集
python tools/yolo_to_coco.py \
    --images-dir vehicle_dataset/images/train \
    --labels-dir vehicle_dataset/labels/train \
    --classes vehicle_dataset/classes.txt \
    --output datasets/vehicle/annotations/instances_train.json \
    --split train

# 转换验证集
python tools/yolo_to_coco.py \
    --images-dir vehicle_dataset/images/val \
    --labels-dir vehicle_dataset/labels/val \
    --classes vehicle_dataset/classes.txt \
    --output datasets/vehicle/annotations/instances_val.json \
    --split val
```

#### 3. 创建软链接

```bash
ln -s $(pwd)/vehicle_dataset/images/train datasets/vehicle/images/train
ln -s $(pwd)/vehicle_dataset/images/val datasets/vehicle/images/val
```

#### 4. 注册数据集

编辑 `maskrcnn_benchmark/config/paths_catalog.py`:

```python
DATASETS = {
    # ...
    "vehicle_train": {
        "img_dir": "vehicle/images/train",
        "ann_file": "vehicle/annotations/instances_train.json"
    },
    "vehicle_val": {
        "img_dir": "vehicle/images/val",
        "ann_file": "vehicle/annotations/instances_val.json"
    },
}
```

#### 5. 创建配置文件

`configs/vehicle/e2e_faster_rcnn_R_50_FPN.yaml`:

```yaml
MODEL:
  META_ARCHITECTURE: "GeneralizedRCNN"
  WEIGHT: "catalog://ImageNetPretrained/MSRA/R-50"
  ROI_HEADS:
    NUM_CLASSES: 4  # 3 个类别 + 1 个背景类

DATASETS:
  TRAIN: ("vehicle_train",)
  TEST: ("vehicle_val",)

SOLVER:
  BASE_LR: 0.005
  MAX_ITER: 50000
  STEPS: (30000, 40000)
  IMS_PER_BATCH: 4
  CHECKPOINT_PERIOD: 2500

INPUT:
  MIN_SIZE_TRAIN: (800,)
  MAX_SIZE_TRAIN: 1333

OUTPUT_DIR: "./output/vehicle"

STITCHER:
  NUM_IMAGES_STITCH: 4
  THRESH: 0.1
  FEEDBACK: 'reg_loss'
```

#### 6. 开始训练

```bash
python tools/train_net.py \
    --config-file configs/vehicle/e2e_faster_rcnn_R_50_FPN.yaml
```

#### 7. 评估模型

```bash
python tools/test_net.py \
    --config-file configs/vehicle/e2e_faster_rcnn_R_50_FPN.yaml \
    MODEL.WEIGHT output/vehicle/model_final.pth
```

---

## 进阶技巧

### 1. 数据增强

可以在 YOLO 数据集转换前进行数据增强：
- 使用 Albumentations 库
- 保持 YOLO 格式不变
- 然后转换为 COCO 格式

### 2. 多尺度训练

```yaml
INPUT:
  MIN_SIZE_TRAIN: (640, 672, 704, 736, 768, 800)  # 随机选择
  MAX_SIZE_TRAIN: 1333
```

### 3. 类别不平衡处理

如果某些类别样本很少，可以：
1. 调整类别权重（需要修改代码）
2. 对少数类别进行过采样
3. 使用 Focal Loss（RetinaNet 架构）

### 4. 小目标优化

Stitcher 本身就是为小目标设计的，还可以：
1. 增大图像尺寸：`MIN_SIZE_TRAIN: (1200,)`
2. 使用 FPN 架构
3. 调整 `STITCHER.NUM_IMAGES_STITCH: 9`（3×3网格）

---

## 参考资源

- **Stitcher 论文**: https://arxiv.org/abs/2004.12432
- **Maskrcnn-benchmark**: https://github.com/facebookresearch/maskrcnn-benchmark
- **COCO 数据集格式**: https://cocodataset.org/#format-data
- **YOLO 格式说明**: https://github.com/ultralytics/yolov5/wiki/Train-Custom-Data

---

## 技术支持

如遇到问题，请检查：
1. 数据集路径是否正确
2. 类别数量是否匹配
3. 图像和标注文件是否一一对应
4. YOLO 标注格式是否正确（坐标范围 0-1）

祝训练顺利！🚀
