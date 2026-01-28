# Stitcher 代码运行完整指南（中文版）

本指南详细说明如何运行 Stitcher 项目的各种功能，包括训练、推理、评估等。

## 目录
1. [快速开始](#快速开始)
2. [数据准备](#数据准备)
3. [训练模型](#训练模型)
4. [模型推理](#模型推理)
5. [模型评估](#模型评估)
6. [可视化结果](#可视化结果)
7. [高级功能](#高级功能)
8. [常见问题](#常见问题)

---

## 快速开始

### 第一次运行：测试安装

```bash
# 1. 激活环境
conda activate stitcher

# 2. 进入项目目录
cd /path/to/Stitcher

# 3. 运行安装验证脚本
python tools/test_installation.py

# 4. 检查CUDA
python -c "import torch; print('CUDA:', torch.cuda.is_available())"
```

### 快速测试训练（使用小数据集）

```bash
# 使用quick schedule快速测试（几分钟内完成）
python tools/train_net.py \
    --config-file configs/quick_schedules/e2e_faster_rcnn_R_50_FPN_quick.yaml \
    OUTPUT_DIR output/quick_test
```

---

## 数据准备

### 使用COCO数据集

#### 1. 下载COCO数据集

```bash
# 创建数据目录
mkdir -p datasets/coco

# 下载并解压（以2017版本为例）
cd datasets/coco

# 训练图像（约18GB）
wget http://images.cocodataset.org/zips/train2017.zip
unzip train2017.zip

# 验证图像（约1GB）
wget http://images.cocodataset.org/zips/val2017.zip
unzip val2017.zip

# 标注文件（约250MB）
wget http://images.cocodataset.org/annotations/annotations_trainval2017.zip
unzip annotations_trainval2017.zip

cd ../..
```

#### 2. 目录结构

确保目录结构如下：
```
datasets/coco/
├── train2017/
│   ├── 000000000009.jpg
│   ├── 000000000025.jpg
│   └── ...
├── val2017/
│   ├── 000000000139.jpg
│   ├── 000000000285.jpg
│   └── ...
└── annotations/
    ├── instances_train2017.json
    ├── instances_val2017.json
    └── ...
```

### 使用YOLO格式数据集

如果您的数据集是YOLO格式，请参考 [YOLO数据集指南](./YOLO_DATASET_GUIDE_CN.md) 进行转换。

### 使用自定义数据集

1. **转换为COCO格式**（推荐）
2. **注册数据集**：编辑 `maskrcnn_benchmark/config/paths_catalog.py`
3. **配置文件**：创建或修改配置文件

详细步骤见 [YOLO数据集指南](./YOLO_DATASET_GUIDE_CN.md)。

---

## 训练模型

### 基础训练命令

#### 单GPU训练

```bash
python tools/train_net.py \
    --config-file configs/e2e_faster_rcnn_R_50_FPN_1x.yaml \
    SOLVER.IMS_PER_BATCH 2 \
    SOLVER.BASE_LR 0.0025 \
    SOLVER.MAX_ITER 90000 \
    OUTPUT_DIR output/faster_rcnn_R_50_FPN
```

#### 多GPU训练（推荐）

```bash
# 使用4个GPU
export NGPUS=4

python -m torch.distributed.launch \
    --nproc_per_node=$NGPUS \
    tools/train_net.py \
    --config-file configs/e2e_faster_rcnn_R_50_FPN_1x.yaml \
    SOLVER.IMS_PER_BATCH 8 \
    OUTPUT_DIR output/faster_rcnn_R_50_FPN_4gpu
```

**参数说明**：
- `--config-file`：配置文件路径
- `SOLVER.IMS_PER_BATCH`：每批图像数（总batch size）
- `SOLVER.BASE_LR`：基础学习率
- `SOLVER.MAX_ITER`：最大迭代次数
- `OUTPUT_DIR`：输出目录

### 从检查点恢复训练

```bash
python tools/train_net.py \
    --config-file configs/e2e_faster_rcnn_R_50_FPN_1x.yaml \
    MODEL.WEIGHT output/faster_rcnn_R_50_FPN/model_0010000.pth \
    OUTPUT_DIR output/faster_rcnn_R_50_FPN_resume
```

### 使用预训练模型

```bash
# 从ImageNet预训练开始
python tools/train_net.py \
    --config-file configs/e2e_faster_rcnn_R_50_FPN_1x.yaml \
    MODEL.WEIGHT catalog://ImageNetPretrained/MSRA/R-50 \
    OUTPUT_DIR output/faster_rcnn_R_50_FPN_pretrained
```

### Stitcher训练（改进小目标检测）

Stitcher会自动使用图像拼接和反馈机制：

```bash
python tools/train_net.py \
    --config-file configs/e2e_faster_rcnn_R_50_FPN_1x.yaml \
    STITCHER.NUM_IMAGES_STITCH 4 \
    STITCHER.BATCH_STITCH False \
    STITCHER.FEEDBACK reg_loss \
    STITCHER.THRESH 0.1 \
    OUTPUT_DIR output/faster_rcnn_R_50_FPN_stitcher
```

**Stitcher参数**：
- `NUM_IMAGES_STITCH`：拼接图像数量（默认4，形成2×2网格）
- `BATCH_STITCH`：是否使用批次级拼接（默认False）
- `FEEDBACK`：反馈类型（`reg_loss`或`cls_loss`）
- `THRESH`：小目标损失阈值（默认0.1）

### 监控训练过程

#### 使用TensorBoard（推荐）

```bash
# 在另一个终端启动TensorBoard
tensorboard --logdir=output/faster_rcnn_R_50_FPN --port=6006

# 然后在浏览器打开
# http://localhost:6006
```

#### 查看日志文件

```bash
# 实时查看训练日志
tail -f output/faster_rcnn_R_50_FPN/log.txt

# 查看最近20行
tail -20 output/faster_rcnn_R_50_FPN/log.txt
```

---

## 模型推理

### 单张图像推理

创建推理脚本 `demo.py`：

```python
import cv2
import torch
from maskrcnn_benchmark.config import cfg
from maskrcnn_benchmark.modeling.detector import build_detection_model
from maskrcnn_benchmark.utils.checkpoint import DetectronCheckpointer
from maskrcnn_benchmark.structures.image_list import to_image_list
from maskrcnn_benchmark.modeling.roi_heads.mask_head.inference import Masker
import numpy as np

def load_model(config_file, model_file):
    """加载模型"""
    cfg.merge_from_file(config_file)
    cfg.MODEL.WEIGHT = model_file
    cfg.freeze()
    
    model = build_detection_model(cfg)
    model.eval()
    model.to(cfg.MODEL.DEVICE)
    
    checkpointer = DetectronCheckpointer(cfg, model)
    _ = checkpointer.load(cfg.MODEL.WEIGHT)
    
    return model, cfg

def inference(model, cfg, image_path):
    """对单张图像进行推理"""
    # 读取图像
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # 预处理
    device = cfg.MODEL.DEVICE
    image_tensor = torch.from_numpy(image).permute(2, 0, 1).float()
    image_list = to_image_list([image_tensor], cfg.DATALOADER.SIZE_DIVISIBILITY)
    image_list = image_list.to(device)
    
    # 推理
    with torch.no_grad():
        predictions = model(image_list)
    
    # 获取结果
    predictions = [o.to("cpu") for o in predictions]
    prediction = predictions[0]
    
    return prediction

# 使用示例
if __name__ == '__main__':
    config_file = "configs/e2e_faster_rcnn_R_50_FPN_1x.yaml"
    model_file = "output/faster_rcnn_R_50_FPN/model_final.pth"
    image_path = "demo/sample.jpg"
    
    model, cfg = load_model(config_file, model_file)
    prediction = inference(model, cfg, image_path)
    
    print(f"检测到 {len(prediction)} 个目标")
    print(f"目标框: {prediction.bbox}")
    print(f"类别: {prediction.get_field('labels')}")
    print(f"置信度: {prediction.get_field('scores')}")
```

### 批量推理

```bash
# 使用官方测试脚本
python tools/test_net.py \
    --config-file configs/e2e_faster_rcnn_R_50_FPN_1x.yaml \
    MODEL.WEIGHT output/faster_rcnn_R_50_FPN/model_final.pth \
    TEST.IMS_PER_BATCH 8
```

---

## 模型评估

### 在验证集上评估

```bash
# COCO验证集评估
python tools/test_net.py \
    --config-file configs/e2e_faster_rcnn_R_50_FPN_1x.yaml \
    MODEL.WEIGHT output/faster_rcnn_R_50_FPN/model_final.pth
```

### 评估指标说明

输出结果包含：
- **AP（Average Precision）**：平均精度
  - `AP`: IoU=0.50:0.95的平均AP
  - `AP50`: IoU=0.50的AP
  - `AP75`: IoU=0.75的AP
- **AR（Average Recall）**：平均召回率
- **AP by size**：不同尺寸目标的AP
  - `AP_small`: 小目标（面积<32²）
  - `AP_medium`: 中等目标（32²≤面积<96²）
  - `AP_large`: 大目标（面积≥96²）

### 评估多个检查点

```bash
# 创建评估脚本
for iter in 10000 20000 30000 40000 50000; do
    echo "评估 iteration $iter"
    python tools/test_net.py \
        --config-file configs/e2e_faster_rcnn_R_50_FPN_1x.yaml \
        MODEL.WEIGHT output/faster_rcnn_R_50_FPN/model_00${iter}.pth \
        OUTPUT_DIR output/eval/iter_${iter}
done
```

---

## 可视化结果

### 可视化检测结果

创建可视化脚本 `visualize.py`：

```python
import cv2
import torch
from maskrcnn_benchmark.config import cfg
from maskrcnn_benchmark.modeling.detector import build_detection_model
from maskrcnn_benchmark.utils.checkpoint import DetectronCheckpointer
from maskrcnn_benchmark.structures.image_list import to_image_list
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# COCO类别（简化版）
CATEGORIES = [
    'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus',
    'train', 'truck', 'boat', 'traffic light', 'fire hydrant',
    'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog',
    'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe',
    'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee',
    # ... 添加所有80个类别
]

def visualize_prediction(image, prediction, threshold=0.7):
    """可视化预测结果"""
    # 创建图形
    fig, ax = plt.subplots(1, figsize=(12, 9))
    ax.imshow(image)
    
    # 获取预测结果
    boxes = prediction.bbox.numpy()
    labels = prediction.get_field('labels').numpy()
    scores = prediction.get_field('scores').numpy()
    
    # 过滤低置信度结果
    mask = scores > threshold
    boxes = boxes[mask]
    labels = labels[mask]
    scores = scores[mask]
    
    # 绘制每个检测框
    for box, label, score in zip(boxes, labels, scores):
        x1, y1, x2, y2 = box
        width = x2 - x1
        height = y2 - y1
        
        # 绘制矩形框
        rect = patches.Rectangle(
            (x1, y1), width, height,
            linewidth=2, edgecolor='red', facecolor='none'
        )
        ax.add_patch(rect)
        
        # 添加标签
        category = CATEGORIES[label - 1] if label <= len(CATEGORIES) else 'unknown'
        text = f'{category}: {score:.2f}'
        ax.text(
            x1, y1 - 5,
            text,
            bbox=dict(boxstyle='round', facecolor='red', alpha=0.5),
            fontsize=10, color='white'
        )
    
    plt.axis('off')
    return fig

# 使用
image = cv2.imread('demo/sample.jpg')
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# ... 加载模型和推理 ...

fig = visualize_prediction(image, prediction, threshold=0.7)
plt.savefig('output/visualization.jpg', bbox_inches='tight', dpi=150)
plt.show()
```

---

## 高级功能

### 配置文件参数覆盖

在命令行中覆盖任何配置参数：

```bash
python tools/train_net.py \
    --config-file configs/e2e_faster_rcnn_R_50_FPN_1x.yaml \
    MODEL.RPN.FPN_POST_NMS_TOP_N_TRAIN 2000 \
    MODEL.ROI_HEADS.BATCH_SIZE_PER_IMAGE 512 \
    SOLVER.BASE_LR 0.02 \
    SOLVER.WEIGHT_DECAY 0.0001 \
    SOLVER.IMS_PER_BATCH 16 \
    OUTPUT_DIR output/custom_config
```

### 多尺度训练

```bash
python tools/train_net.py \
    --config-file configs/e2e_faster_rcnn_R_50_FPN_1x.yaml \
    INPUT.MIN_SIZE_TRAIN "(640, 672, 704, 736, 768, 800)" \
    OUTPUT_DIR output/multiscale
```

### 混合精度训练（需要APEX）

```bash
python tools/train_net.py \
    --config-file configs/e2e_faster_rcnn_R_50_FPN_1x.yaml \
    DTYPE "float16" \
    OUTPUT_DIR output/fp16
```

### 使用不同的骨干网络

```bash
# ResNet-101
python tools/train_net.py \
    --config-file configs/e2e_faster_rcnn_R_101_FPN_1x.yaml \
    OUTPUT_DIR output/R_101

# ResNext-101
python tools/train_net.py \
    --config-file configs/e2e_faster_rcnn_X_101_32x8d_FPN_1x.yaml \
    OUTPUT_DIR output/X_101
```

---

## 常见问题

### Q1: CUDA out of memory

**解决方法**：
```bash
# 减小批次大小
SOLVER.IMS_PER_BATCH 2

# 减小图像尺寸
INPUT.MIN_SIZE_TRAIN 600
INPUT.MAX_SIZE_TRAIN 1000

# 使用更小的模型
# 使用 R-50-C4 而不是 R-50-FPN
```

### Q2: 训练速度慢

**优化方法**：
1. 使用多GPU训练
2. 增大批次大小
3. 使用混合精度训练（FP16）
4. 减小验证频率

```bash
# 示例：优化训练速度
python -m torch.distributed.launch --nproc_per_node=4 \
    tools/train_net.py \
    --config-file configs/e2e_faster_rcnn_R_50_FPN_1x.yaml \
    SOLVER.IMS_PER_BATCH 16 \
    DTYPE float16 \
    SOLVER.CHECKPOINT_PERIOD 5000 \
    OUTPUT_DIR output/optimized
```

### Q3: 训练不收敛

**检查项**：
1. 学习率是否合适（通常0.01-0.02）
2. 批次大小是否足够（建议≥8）
3. 预训练模型是否正确加载
4. 数据集是否正确

### Q4: 推理速度慢

**优化方法**：
```bash
# 增大测试批次
TEST.IMS_PER_BATCH 8

# 减小每张图像的proposal数
MODEL.RPN.FPN_POST_NMS_TOP_N_TEST 1000
```

### Q5: 内存泄漏

**解决方法**：
```python
# 在推理循环中定期清理
if iteration % 100 == 0:
    torch.cuda.empty_cache()
```

### Q6: 检测结果不佳

**改进方法**：
1. 训练更多epoch
2. 使用更大的模型
3. 使用Stitcher（针对小目标）
4. 数据增强
5. 调整NMS阈值

---

## 性能基准

### 训练时间（COCO，单个epoch）

| 模型 | GPU | 批次 | 时间 |
|------|-----|------|------|
| R-50-C4 | 1x V100 | 2 | ~12h |
| R-50-FPN | 1x V100 | 2 | ~8h |
| R-50-FPN | 4x V100 | 8 | ~2.5h |
| R-101-FPN | 4x V100 | 8 | ~3.5h |

### 推理速度（单张图像）

| 模型 | GPU | FPS |
|------|-----|-----|
| R-50-C4 | V100 | ~8 |
| R-50-FPN | V100 | ~15 |
| R-101-FPN | V100 | ~12 |

---

## 完整训练示例

### 从零开始训练（COCO数据集）

```bash
#!/bin/bash
# complete_training.sh

# 1. 激活环境
conda activate stitcher

# 2. 设置变量
CONFIG="configs/e2e_faster_rcnn_R_50_FPN_1x.yaml"
OUTPUT="output/my_model"
GPUS=4

# 3. 开始训练
python -m torch.distributed.launch \
    --nproc_per_node=$GPUS \
    tools/train_net.py \
    --config-file $CONFIG \
    SOLVER.IMS_PER_BATCH 8 \
    SOLVER.BASE_LR 0.01 \
    SOLVER.MAX_ITER 90000 \
    SOLVER.STEPS "(60000, 80000)" \
    SOLVER.CHECKPOINT_PERIOD 5000 \
    MODEL.WEIGHT "catalog://ImageNetPretrained/MSRA/R-50" \
    OUTPUT_DIR $OUTPUT

# 4. 评估最终模型
python tools/test_net.py \
    --config-file $CONFIG \
    MODEL.WEIGHT $OUTPUT/model_final.pth \
    OUTPUT_DIR $OUTPUT/inference

# 5. 查看结果
cat $OUTPUT/inference/coco_results.txt
```

运行脚本：
```bash
chmod +x complete_training.sh
./complete_training.sh
```

---

## 下一步

- 查看 [项目代码分析](./PROJECT_ANALYSIS_CN.md) 了解代码结构
- 查看 [YOLO数据集指南](./YOLO_DATASET_GUIDE_CN.md) 使用自己的数据
- 查看 [环境配置指南](./ENVIRONMENT_SETUP_CN.md) 解决环境问题

**祝训练顺利！** 🚀
