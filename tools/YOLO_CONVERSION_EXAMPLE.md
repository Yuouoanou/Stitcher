# 快速示例：YOLO 到 COCO 转换

这是一个快速演示如何使用转换脚本的示例。

## 示例数据集结构

假设你有一个 YOLO 格式的数据集：

```
my_yolo_data/
├── images/
│   ├── 001.jpg
│   ├── 002.jpg
│   └── 003.jpg
├── labels/
│   ├── 001.txt
│   ├── 002.txt
│   └── 003.txt
└── classes.txt
```

### classes.txt 内容
```
cat
dog
person
```

### labels/001.txt 内容
```
0 0.5 0.5 0.3 0.4
2 0.2 0.3 0.15 0.2
```
（第一行：cat 在图像中心；第二行：person 在左上区域）

## 转换命令

### 基本用法
```bash
python tools/yolo_to_coco.py \
    --images-dir my_yolo_data/images \
    --labels-dir my_yolo_data/labels \
    --classes my_yolo_data/classes.txt \
    --output datasets/my_data/annotations/instances.json
```

### 分别转换训练集和验证集
```bash
# 训练集
python tools/yolo_to_coco.py \
    --images-dir my_yolo_data/images/train \
    --labels-dir my_yolo_data/labels/train \
    --classes my_yolo_data/classes.txt \
    --output datasets/my_data/annotations/instances_train.json \
    --split train

# 验证集
python tools/yolo_to_coco.py \
    --images-dir my_yolo_data/images/val \
    --labels-dir my_yolo_data/labels/val \
    --classes my_yolo_data/classes.txt \
    --output datasets/my_data/annotations/instances_val.json \
    --split val
```

## 输出 COCO JSON 格式

转换后的 JSON 文件包含：

```json
{
  "info": {
    "description": "YOLO to COCO converted dataset - train",
    "version": "1.0",
    "year": 2024
  },
  "images": [
    {
      "id": 1,
      "file_name": "001.jpg",
      "width": 1920,
      "height": 1080
    }
  ],
  "annotations": [
    {
      "id": 1,
      "image_id": 1,
      "category_id": 1,
      "bbox": [864.0, 324.0, 576.0, 432.0],
      "area": 248832.0,
      "iscrowd": 0
    }
  ],
  "categories": [
    {
      "id": 1,
      "name": "cat",
      "supercategory": "object"
    },
    {
      "id": 2,
      "name": "dog",
      "supercategory": "object"
    },
    {
      "id": 3,
      "name": "person",
      "supercategory": "object"
    }
  ]
}
```

## 坐标转换说明

### YOLO 格式
- 归一化坐标 [0, 1]
- 格式：`<class_id> <x_center> <y_center> <width> <height>`
- 中心点坐标

### COCO 格式
- 绝对像素坐标
- 格式：`[x_min, y_min, width, height]`
- 左上角坐标

### 转换公式
```python
# YOLO → COCO
x_min = (x_center - width / 2) * image_width
y_min = (y_center - height / 2) * image_height
width_px = width * image_width
height_px = height * image_height
```

## 常见问题

### Q: 标注文件和图像数量不匹配？
A: 这是正常的。没有标注的图像会被包含但不会有对应的 annotations（负样本）。

### Q: 某些图像读取失败？
A: 脚本会跳过无法读取的图像并打印警告。检查图像文件是否损坏。

### Q: 类别 ID 超出范围？
A: 确保 YOLO 标注中的 class_id 在 [0, N-1] 范围内，N 是 classes.txt 中的类别数。

### Q: 转换后的坐标不对？
A: 运行测试脚本验证：
```bash
python tools/test_yolo_to_coco.py
```

## 下一步

转换完成后，按照 [YOLO_DATASET_GUIDE_CN.md](../YOLO_DATASET_GUIDE_CN.md) 继续：
1. 注册数据集到 `paths_catalog.py`
2. 创建配置文件
3. 开始训练

## 完整流程示例

```bash
# 1. 转换数据集
python tools/yolo_to_coco.py \
    --images-dir /data/yolo/images/train \
    --labels-dir /data/yolo/labels/train \
    --classes /data/yolo/classes.txt \
    --output datasets/my_data/annotations/instances_train.json

# 2. 创建软链接
mkdir -p datasets/my_data/images
ln -s /data/yolo/images/train datasets/my_data/images/train
ln -s /data/yolo/images/val datasets/my_data/images/val

# 3. 注册数据集（编辑 maskrcnn_benchmark/config/paths_catalog.py）

# 4. 开始训练
python tools/train_net.py \
    --config-file configs/my_config.yaml
```

更多详细信息请查看 [YOLO_DATASET_GUIDE_CN.md](../YOLO_DATASET_GUIDE_CN.md)
