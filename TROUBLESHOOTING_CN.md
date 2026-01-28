# Stitcher 故障排除指南（中文版）

本指南收集了使用 Stitcher 时可能遇到的常见问题及解决方案。

## 目录
1. [安装问题](#安装问题)
2. [运行问题](#运行问题)
3. [训练问题](#训练问题)
4. [推理问题](#推理问题)
5. [数据问题](#数据问题)
6. [性能问题](#性能问题)

---

## 安装问题

### 问题1: `ImportError: No module named 'maskrcnn_benchmark'`

**症状**：
```python
ImportError: No module named 'maskrcnn_benchmark'
```

**原因**：项目未正确安装

**解决方案**：
```bash
# 方案1: 开发模式安装（推荐）
cd /path/to/Stitcher
python setup.py build develop

# 方案2: 正式安装
python setup.py install

# 方案3: 检查是否在正确的conda环境
conda activate stitcher
which python  # 确认Python路径
```

---

### 问题2: `ImportError: cannot import name '_C'`

**症状**：
```python
ImportError: cannot import name '_C' from 'maskrcnn_benchmark'
```

**原因**：C++/CUDA扩展未编译或编译失败

**解决方案**：
```bash
# 1. 清理之前的编译
cd /path/to/Stitcher
rm -rf build/
python setup.py clean

# 2. 重新编译
python setup.py build develop

# 3. 如果仍然失败，检查编译器
gcc --version  # 需要 GCC >= 4.9
nvcc --version  # GPU版本需要CUDA

# 4. 设置环境变量（如果需要）
export CUDA_HOME=/usr/local/cuda
export PATH=$CUDA_HOME/bin:$PATH
export LD_LIBRARY_PATH=$CUDA_HOME/lib64:$LD_LIBRARY_PATH
```

---

### 问题3: CUDA版本不匹配

**症状**：
```
RuntimeError: CUDA error: no kernel image is available for execution
```

**原因**：PyTorch的CUDA版本与系统CUDA版本不匹配

**解决方案**：
```bash
# 1. 检查系统CUDA版本
nvcc --version

# 2. 检查PyTorch CUDA版本
python -c "import torch; print(torch.version.cuda)"

# 3. 重新安装匹配的PyTorch
# 例如，如果系统是CUDA 11.1:
conda install pytorch==1.7.1 torchvision==0.8.2 cudatoolkit=11.1 -c pytorch

# 4. 重新编译项目
python setup.py build develop
```

---

### 问题4: GCC版本过低

**症状**：
```
error: #error -- unsupported GNU version! gcc versions later than 7 are not supported!
```

**原因**：CUDA不支持过高的GCC版本

**解决方案**：
```bash
# Ubuntu/Debian
sudo apt-get install gcc-7 g++-7

# 临时使用GCC 7
export CC=gcc-7
export CXX=g++-7

# 或创建软链接
sudo ln -s /usr/bin/gcc-7 /usr/local/cuda/bin/gcc
sudo ln -s /usr/bin/g++-7 /usr/local/cuda/bin/g++

# 然后重新编译
python setup.py build develop
```

---

### 问题5: Windows下pycocotools安装失败

**症状**：
```
error: Microsoft Visual C++ 14.0 is required
```

**原因**：缺少C++编译器

**解决方案**：
```bash
# 方案1: 使用预编译版本
pip install pycocotools-windows

# 方案2: 从源码安装
pip install git+https://github.com/philferriere/cocoapi.git#subdirectory=PythonAPI

# 方案3: 安装Visual Studio 2017或更新版本
# 下载地址: https://visualstudio.microsoft.com/
```

---

### 问题6: APEX安装失败

**症状**：
```
RuntimeError: Cuda extensions are being compiled with a version of Cuda that does not match the version used to compile Pytorch binaries.
```

**原因**：APEX与PyTorch/CUDA版本不匹配

**解决方案**：
```bash
# 方案1: 简化安装（不包含CUDA扩展）
pip install -v --disable-pip-version-check --no-cache-dir apex/

# 方案2: 跳过APEX
# APEX是可选的，主要用于混合精度训练
# 不安装APEX不影响基本功能

# 方案3: 确保版本匹配
python -c "import torch; print(torch.version.cuda)"
nvcc --version
# 两者应该匹配
```

---

## 运行问题

### 问题7: `CUDA out of memory`

**症状**：
```
RuntimeError: CUDA out of memory. Tried to allocate 2.00 GiB
```

**原因**：GPU显存不足

**解决方案**：
```bash
# 方案1: 减小批次大小
python tools/train_net.py \
    --config-file configs/xxx.yaml \
    SOLVER.IMS_PER_BATCH 2  # 从8减到2

# 方案2: 减小图像尺寸
INPUT.MIN_SIZE_TRAIN 600
INPUT.MAX_SIZE_TRAIN 1000

# 方案3: 使用更小的模型
# 使用 R-50-C4 代替 R-50-FPN
# 使用 ResNet-50 代替 ResNet-101

# 方案4: 启用梯度累积（模拟大batch）
# 修改训练代码实现梯度累积

# 方案5: 清理显存
import torch
torch.cuda.empty_cache()
```

---

### 问题8: 多GPU训练失败

**症状**：
```
RuntimeError: Default process group has not been initialized
```

**原因**：分布式训练未正确初始化

**解决方案**：
```bash
# 正确的多GPU训练命令
export NGPUS=4

python -m torch.distributed.launch \
    --nproc_per_node=$NGPUS \
    --master_port=29500 \
    tools/train_net.py \
    --config-file configs/xxx.yaml \
    SOLVER.IMS_PER_BATCH 8

# 注意事项：
# 1. 必须使用 torch.distributed.launch
# 2. --nproc_per_node 应该等于GPU数量
# 3. IMS_PER_BATCH 是所有GPU的总batch size
```

---

### 问题9: 找不到配置文件

**症状**：
```
FileNotFoundError: [Errno 2] No such file or directory: 'configs/xxx.yaml'
```

**原因**：路径不正确或文件不存在

**解决方案**：
```bash
# 1. 确保在项目根目录
cd /path/to/Stitcher

# 2. 列出可用的配置文件
ls configs/*.yaml
ls configs/pascal_voc/*.yaml

# 3. 使用绝对路径
python tools/train_net.py \
    --config-file /absolute/path/to/config.yaml

# 4. 检查配置文件是否存在
cat configs/e2e_faster_rcnn_R_50_FPN_1x.yaml
```

---

## 训练问题

### 问题10: 训练loss为NaN

**症状**：
```
loss: nan, loss_classifier: nan, loss_box_reg: nan
```

**原因**：学习率过大、数据问题或数值溢出

**解决方案**：
```bash
# 方案1: 降低学习率
SOLVER.BASE_LR 0.001  # 从0.01降到0.001

# 方案2: 使用warmup
SOLVER.WARMUP_ITERS 1000
SOLVER.WARMUP_FACTOR 0.1

# 方案3: 检查数据
# 确保标注数据正确，没有异常值

# 方案4: 使用混合精度时注意
# 检查 loss scaling 设置

# 方案5: 检查模型初始化
# 使用预训练模型
MODEL.WEIGHT "catalog://ImageNetPretrained/MSRA/R-50"
```

---

### 问题11: 训练速度慢

**症状**：每个iteration需要很长时间

**解决方案**：
```bash
# 1. 检查数据加载
# 增加dataloader的worker数量
DATALOADER.NUM_WORKERS 4

# 2. 使用更快的数据增强
# 减少transform操作

# 3. 增大批次大小
SOLVER.IMS_PER_BATCH 16

# 4. 使用混合精度训练
DTYPE "float16"

# 5. 使用更快的模型
# 如使用 ResNet-50 代替 ResNet-101

# 6. 减少验证频率
SOLVER.CHECKPOINT_PERIOD 10000  # 从5000增加到10000

# 7. 使用SSD而不是HDD存储数据
```

---

### 问题12: 模型不收敛

**症状**：训练多个epoch后，loss不下降，AP很低

**解决方案**：
```bash
# 1. 检查学习率
# 太大或太小都可能导致不收敛
SOLVER.BASE_LR 0.01  # 尝试不同值: 0.001, 0.005, 0.01, 0.02

# 2. 确保使用预训练模型
MODEL.WEIGHT "catalog://ImageNetPretrained/MSRA/R-50"

# 3. 检查批次大小
# 批次太小可能导致训练不稳定
SOLVER.IMS_PER_BATCH 8  # 至少4-8

# 4. 调整学习率策略
SOLVER.STEPS "(60000, 80000)"
SOLVER.MAX_ITER 90000

# 5. 检查数据
# 确保数据集正确，标注准确
# 可以先在小数据集上测试

# 6. 使用warmup
SOLVER.WARMUP_ITERS 1000
```

---

### 问题13: 检查点加载失败

**症状**：
```
KeyError: 'iteration'
或
RuntimeError: Error(s) in loading state_dict
```

**原因**：模型结构不匹配或检查点损坏

**解决方案**：
```bash
# 1. 检查配置文件是否匹配
# 确保使用与训练时相同的配置

# 2. 检查模型权重文件
ls -lh output/model_xxx.pth

# 3. 只加载模型权重（不加载优化器状态）
# 修改代码，设置 load_optimizer=False

# 4. 使用部分权重
# 删除不匹配的层的权重

# 5. 重新开始训练
# 如果检查点损坏，从上一个检查点开始
```

---

## 推理问题

### 问题14: 推理结果差

**症状**：推理时AP很低或检测框质量差

**解决方案**：
```bash
# 1. 检查模型是否训练充分
# 查看训练日志，确认loss已收敛

# 2. 检查测试图像尺寸
INPUT.MIN_SIZE_TEST 800
INPUT.MAX_SIZE_TEST 1333

# 3. 调整NMS阈值
MODEL.ROI_HEADS.NMS 0.5  # 尝试 0.3-0.7

# 4. 调整置信度阈值
MODEL.ROI_HEADS.SCORE_THRESH_TEST 0.05

# 5. 增加proposal数量
MODEL.RPN.FPN_POST_NMS_TOP_N_TEST 2000

# 6. 使用测试时增强（TTA）
# 多尺度测试、翻转等
```

---

### 问题15: 推理速度慢

**症状**：单张图像推理时间过长

**解决方案**：
```bash
# 1. 增大batch size
TEST.IMS_PER_BATCH 8

# 2. 减少proposal数量
MODEL.RPN.FPN_POST_NMS_TOP_N_TEST 1000

# 3. 使用更快的模型
# R-50-C4 比 R-101-FPN 快

# 4. 降低图像分辨率
INPUT.MIN_SIZE_TEST 600

# 5. 使用FP16推理
DTYPE "float16"

# 6. 使用TorchScript或ONNX
# 将模型转换为优化格式
```

---

## 数据问题

### 问题16: 数据集路径错误

**症状**：
```
FileNotFoundError: Dataset not found: coco_2017_train
```

**原因**：数据集未正确配置

**解决方案**：
```bash
# 1. 检查paths_catalog.py
cat maskrcnn_benchmark/config/paths_catalog.py

# 2. 确认数据集目录结构
ls datasets/coco/
# 应该有: train2017/, val2017/, annotations/

# 3. 修改DATA_DIR
# 在 paths_catalog.py 中设置正确的路径
DATA_DIR = "/absolute/path/to/datasets"

# 4. 使用绝对路径
# 在配置中直接指定绝对路径
```

---

### 问题17: YOLO格式转换问题

**症状**：转换后的COCO JSON格式错误

**解决方案**：
```bash
# 1. 检查YOLO标注格式
# 格式应该是: <class_id> <x_center> <y_center> <width> <height>
# 所有值都应该在 [0, 1] 范围内

# 2. 使用转换脚本
python tools/yolo_to_coco.py \
    --images-dir path/to/images \
    --labels-dir path/to/labels \
    --classes path/to/classes.txt \
    --output output.json

# 3. 验证转换结果
python -c "import json; data=json.load(open('output.json')); print(len(data['images']), len(data['annotations']))"

# 4. 检查类别映射
# 确保classes.txt的顺序与YOLO标注一致
```

---

## 性能问题

### 问题18: 小目标检测效果差

**症状**：AP_small很低

**解决方案**：
```bash
# 1. 使用Stitcher
STITCHER.NUM_IMAGES_STITCH 4
STITCHER.FEEDBACK "reg_loss"
STITCHER.THRESH 0.1

# 2. 使用FPN
# FPN对小目标效果更好

# 3. 增大输入图像尺寸
INPUT.MIN_SIZE_TRAIN "(800, 1000, 1200)"
INPUT.MAX_SIZE_TRAIN 1600

# 4. 多尺度训练
# 使用不同尺度的训练图像

# 5. 数据增强
# 添加更多小目标的训练样本
```

---

### 问题19: 内存泄漏

**症状**：训练过程中内存持续增长

**解决方案**：
```python
# 1. 定期清理GPU缓存
if iteration % 100 == 0:
    torch.cuda.empty_cache()

# 2. 使用torch.no_grad()
with torch.no_grad():
    predictions = model(images)

# 3. 及时删除不需要的变量
del loss, predictions
torch.cuda.empty_cache()

# 4. 检查是否有循环引用
# 使用 objgraph 等工具检查

# 5. 减少日志保存频率
# 避免在内存中累积大量日志
```

---

### 问题20: 类别不平衡

**症状**：某些类别检测效果很差

**解决方案**：
```bash
# 1. 增加少数类的样本
# 使用数据增强生成更多样本

# 2. 调整类别权重
# 修改损失函数，给少数类更大权重

# 3. 使用Focal Loss
# 对于严重不平衡的数据

# 4. 重采样
# 过采样少数类或欠采样多数类

# 5. 使用OHEM
# Online Hard Example Mining
```

---

## 调试技巧

### 使用Python调试器

```bash
# 使用pdb
python -m pdb tools/train_net.py --config-file xxx.yaml

# 或在代码中插入断点
import pdb; pdb.set_trace()
```

### 检查梯度

```python
# 检查梯度是否正常
for name, param in model.named_parameters():
    if param.grad is not None:
        print(f"{name}: {param.grad.abs().mean()}")
```

### 可视化中间结果

```python
# 可视化特征图
import matplotlib.pyplot as plt
plt.imshow(features[0, 0].detach().cpu())
plt.show()

# 可视化proposal
from maskrcnn_benchmark.structures.image_list import to_image_list
# ... 可视化逻辑
```

---

## 获取更多帮助

1. **查看日志**: `tail -f output/log.txt`
2. **检查GitHub Issues**: [https://github.com/facebookresearch/maskrcnn-benchmark/issues](https://github.com/facebookresearch/maskrcnn-benchmark/issues)
3. **查看文档**:
   - [环境配置指南](./ENVIRONMENT_SETUP_CN.md)
   - [运行指南](./HOW_TO_RUN_CN.md)
   - [项目分析](./PROJECT_ANALYSIS_CN.md)
4. **运行诊断脚本**: `python tools/test_installation.py`

---

**祝调试顺利！** 🔧
