# Stitcher 快速入门指南

本指南将帮助您在15分钟内完成环境配置并开始使用 Stitcher。

## 📋 前置条件

- Linux/Ubuntu 系统（推荐）或 Windows 10/11
- 至少 20GB 可用磁盘空间
- （可选）NVIDIA GPU + CUDA 驱动

---

## 🚀 方案A：一键安装（Linux推荐）

### 1. 克隆项目

```bash
git clone https://github.com/Yuouoanou/Stitcher.git
cd Stitcher
```

### 2. 运行一键安装脚本

```bash
bash tools/quick_install.sh
```

脚本会：
- ✅ 自动检测系统
- ✅ 创建 Conda 环境
- ✅ 安装所有依赖
- ✅ 编译项目
- ✅ 验证安装

### 3. 激活环境

```bash
conda activate stitcher
```

### 4. 运行快速测试

```bash
python tools/train_net.py \
    --config-file configs/quick_schedules/e2e_faster_rcnn_R_50_FPN_quick.yaml \
    OUTPUT_DIR output/quick_test
```

**完成！** 🎉

---

## 🛠️ 方案B：手动安装

### 步骤1：安装 Anaconda/Miniconda

如果还没有安装，从 [这里](https://docs.conda.io/en/latest/miniconda.html) 下载安装。

### 步骤2：创建环境

```bash
# 创建 Python 3.7 环境
conda create -n stitcher python=3.7 -y
conda activate stitcher
```

### 步骤3：安装 PyTorch

**GPU 版本（推荐）：**
```bash
conda install pytorch==1.7.1 torchvision==0.8.2 cudatoolkit=10.2 -c pytorch -y
```

**CPU 版本：**
```bash
conda install pytorch==1.7.1 torchvision==0.8.2 cpuonly -c pytorch -y
```

### 步骤4：安装依赖

```bash
pip install ninja yacs cython matplotlib tqdm opencv-python pillow scipy pycocotools
```

### 步骤5：编译项目

```bash
cd /path/to/Stitcher
python setup.py build develop
```

### 步骤6：验证安装

```bash
python tools/test_installation.py
```

---

## ✅ 验证安装

运行验证脚本：

```bash
python tools/test_installation.py
```

**期望输出：**
```
========================================
✓ 安装验证通过！
========================================

环境配置成功，您可以开始使用Stitcher了！
```

如果验证失败，查看 [故障排除指南](./TROUBLESHOOTING_CN.md)。

---

## 📚 下一步：开始使用

### 1. 快速测试（3分钟）

```bash
# 运行快速训练测试
python tools/train_net.py \
    --config-file configs/quick_schedules/e2e_faster_rcnn_R_50_FPN_quick.yaml \
    OUTPUT_DIR output/quick_test
```

### 2. 使用 COCO 数据集

#### 下载数据

```bash
mkdir -p datasets/coco
cd datasets/coco

# 训练集（约18GB）
wget http://images.cocodataset.org/zips/train2017.zip
unzip train2017.zip

# 验证集（约1GB）
wget http://images.cocodataset.org/zips/val2017.zip
unzip val2017.zip

# 标注（约250MB）
wget http://images.cocodataset.org/annotations/annotations_trainval2017.zip
unzip annotations_trainval2017.zip

cd ../..
```

#### 开始训练

```bash
# 单GPU训练
python tools/train_net.py \
    --config-file configs/e2e_faster_rcnn_R_50_FPN_1x.yaml \
    SOLVER.IMS_PER_BATCH 2 \
    OUTPUT_DIR output/faster_rcnn_R_50_FPN

# 多GPU训练（4个GPU）
export NGPUS=4
python -m torch.distributed.launch --nproc_per_node=$NGPUS \
    tools/train_net.py \
    --config-file configs/e2e_faster_rcnn_R_50_FPN_1x.yaml \
    SOLVER.IMS_PER_BATCH 8 \
    OUTPUT_DIR output/faster_rcnn_R_50_FPN_4gpu
```

### 3. 使用自己的 YOLO 数据集

#### 转换格式

```bash
python tools/yolo_to_coco.py \
    --images-dir /path/to/your/images \
    --labels-dir /path/to/your/labels \
    --classes /path/to/classes.txt \
    --output datasets/my_dataset/annotations/instances.json
```

#### 注册数据集

编辑 `maskrcnn_benchmark/config/paths_catalog.py`，添加：

```python
"my_dataset_train": {
    "img_dir": "my_dataset/images",
    "ann_file": "my_dataset/annotations/instances.json"
}
```

#### 创建配置文件

复制并修改配置文件：

```bash
cp configs/e2e_faster_rcnn_R_50_FPN_1x.yaml configs/my_dataset.yaml
```

修改以下内容：
```yaml
DATASETS:
  TRAIN: ("my_dataset_train",)
  TEST: ("my_dataset_val",)
MODEL:
  ROI_HEADS:
    NUM_CLASSES: 你的类别数 + 1
```

#### 开始训练

```bash
python tools/train_net.py \
    --config-file configs/my_dataset.yaml \
    OUTPUT_DIR output/my_model
```

详细指南请查看 [YOLO数据集指南](./YOLO_DATASET_GUIDE_CN.md)。

---

## 📖 完整文档

### 基础文档
- **[环境配置指南](./ENVIRONMENT_SETUP_CN.md)** - 详细的安装步骤
- **[代码运行指南](./HOW_TO_RUN_CN.md)** - 完整的使用教程
- **[故障排除指南](./TROUBLESHOOTING_CN.md)** - 常见问题解决

### 进阶文档
- **[项目代码分析](./PROJECT_ANALYSIS_CN.md)** - 深入了解代码结构
- **[YOLO数据集指南](./YOLO_DATASET_GUIDE_CN.md)** - 使用自己的数据

### 工具脚本
- `tools/test_installation.py` - 验证安装
- `tools/quick_install.sh` - 一键安装
- `tools/yolo_to_coco.py` - 格式转换

---

## 🎯 常见使用场景

### 场景1：快速体验 Stitcher

```bash
# 1. 安装
bash tools/quick_install.sh

# 2. 快速测试
conda activate stitcher
python tools/train_net.py \
    --config-file configs/quick_schedules/e2e_faster_rcnn_R_50_FPN_quick.yaml
```

### 场景2：在 COCO 上训练标准模型

```bash
# 1. 下载 COCO 数据集（参考上面的说明）

# 2. 训练
python tools/train_net.py \
    --config-file configs/e2e_faster_rcnn_R_50_FPN_1x.yaml \
    OUTPUT_DIR output/coco_model
```

### 场景3：使用自己的 YOLO 数据集

```bash
# 1. 转换数据集
python tools/yolo_to_coco.py \
    --images-dir my_data/images \
    --labels-dir my_data/labels \
    --classes my_data/classes.txt \
    --output datasets/my_data/annotations/instances.json

# 2. 注册数据集（编辑 paths_catalog.py）

# 3. 训练
python tools/train_net.py \
    --config-file configs/my_config.yaml
```

### 场景4：使用 Stitcher 改进小目标检测

```bash
python tools/train_net.py \
    --config-file configs/e2e_faster_rcnn_R_50_FPN_1x.yaml \
    STITCHER.NUM_IMAGES_STITCH 4 \
    STITCHER.FEEDBACK reg_loss \
    STITCHER.THRESH 0.1 \
    OUTPUT_DIR output/stitcher_model
```

---

## ⚠️ 常见问题快速解决

### 问题：CUDA out of memory

```bash
# 减小批次大小
SOLVER.IMS_PER_BATCH 2
```

### 问题：找不到模块 'maskrcnn_benchmark'

```bash
# 重新编译
python setup.py build develop
```

### 问题：CUDA 不可用

```bash
# 检查 CUDA
nvcc --version

# 检查 PyTorch
python -c "import torch; print(torch.cuda.is_available())"

# 重新安装匹配的 PyTorch
conda install pytorch torchvision cudatoolkit=10.2 -c pytorch
```

更多问题请查看 [故障排除指南](./TROUBLESHOOTING_CN.md)。

---

## 💡 提示和技巧

### 监控训练

```bash
# 使用 TensorBoard
tensorboard --logdir=output/your_model

# 查看日志
tail -f output/your_model/log.txt
```

### 显存优化

```bash
# 1. 减小批次大小
SOLVER.IMS_PER_BATCH 2

# 2. 减小图像尺寸
INPUT.MIN_SIZE_TRAIN 600

# 3. 使用小模型
# 使用 R-50-C4 代替 R-50-FPN
```

### 加速训练

```bash
# 1. 使用多GPU
export NGPUS=4
python -m torch.distributed.launch --nproc_per_node=$NGPUS ...

# 2. 增大批次
SOLVER.IMS_PER_BATCH 16

# 3. 混合精度训练
DTYPE "float16"
```

---

## 🔗 相关资源

- **GitHub**: [Stitcher项目](https://github.com/Yuouoanou/Stitcher)
- **论文**: [Stitcher: Feedback-driven Data Provider](https://arxiv.org/abs/2004.12432)
- **原始项目**: [maskrcnn-benchmark](https://github.com/facebookresearch/maskrcnn-benchmark)

---

## 📞 获取帮助

1. **查看文档**
   - 环境问题 → [ENVIRONMENT_SETUP_CN.md](./ENVIRONMENT_SETUP_CN.md)
   - 运行问题 → [HOW_TO_RUN_CN.md](./HOW_TO_RUN_CN.md)
   - 其他问题 → [TROUBLESHOOTING_CN.md](./TROUBLESHOOTING_CN.md)

2. **运行诊断**
   ```bash
   python tools/test_installation.py
   ```

3. **查看日志**
   ```bash
   tail -f output/your_model/log.txt
   ```

---

**祝您使用愉快！Happy coding! 🚀**

---

## 📝 快速命令参考

```bash
# 环境管理
conda activate stitcher          # 激活环境
conda deactivate                 # 退出环境

# 验证安装
python tools/test_installation.py

# 快速测试
python tools/train_net.py --config-file configs/quick_schedules/e2e_faster_rcnn_R_50_FPN_quick.yaml

# 单GPU训练
python tools/train_net.py --config-file configs/xxx.yaml OUTPUT_DIR output/model

# 多GPU训练
python -m torch.distributed.launch --nproc_per_node=4 tools/train_net.py --config-file configs/xxx.yaml

# 评估模型
python tools/test_net.py --config-file configs/xxx.yaml MODEL.WEIGHT output/model/model_final.pth

# 格式转换
python tools/yolo_to_coco.py --images-dir images/ --labels-dir labels/ --classes classes.txt --output output.json

# 监控训练
tensorboard --logdir=output/model
tail -f output/model/log.txt
```
