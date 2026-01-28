# Stitcher 环境配置完整指南（中文版）

本指南将详细说明如何配置 Stitcher 项目的运行环境，包括 CPU 和 GPU 版本的安装步骤。

## 目录
1. [系统要求](#系统要求)
2. [安装方式选择](#安装方式选择)
3. [方式1：Conda环境安装（推荐）](#方式1conda环境安装推荐)
4. [方式2：Docker安装](#方式2docker安装)
5. [方式3：手动安装](#方式3手动安装)
6. [验证安装](#验证安装)
7. [常见问题](#常见问题)

---

## 系统要求

### 硬件要求
- **CPU版本**：任何现代 x86_64 CPU
- **GPU版本（推荐）**：
  - NVIDIA GPU（推荐 GTX 1080 或更高）
  - 显存至少 8GB（训练时）
  - 显存至少 4GB（推理时）

### 软件要求
- **操作系统**：
  - Linux (Ubuntu 18.04+ 推荐)
  - Windows 10/11
  - macOS (仅支持CPU版本)
  
- **必需软件**：
  - Python 3.6 - 3.8（推荐 3.7）
  - CUDA 9.0 - 11.3（GPU版本）
  - cuDNN 7.0+（GPU版本）
  - GCC 4.9+（Linux）
  - Visual Studio 2017+（Windows）

---

## 安装方式选择

| 方式 | 优点 | 缺点 | 适用场景 |
|------|------|------|---------|
| **Conda安装** | 依赖管理简单，环境隔离好 | 需要下载较多文件 | 推荐给所有用户 |
| **Docker安装** | 环境完全隔离，一键部署 | 需要了解Docker | 生产环境、服务器 |
| **手动安装** | 灵活度高，可自定义 | 容易出错，需要经验 | 高级用户 |

---

## 方式1：Conda环境安装（推荐）

### 步骤1：安装Anaconda或Miniconda

如果还没有安装 Conda，请先安装：

**Linux/macOS:**
```bash
# 下载 Miniconda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
# 安装
bash Miniconda3-latest-Linux-x86_64.sh
# 按照提示完成安装
```

**Windows:**
从 [Anaconda官网](https://www.anaconda.com/products/distribution) 下载安装包并安装。

### 步骤2：创建Python环境

```bash
# 创建名为 stitcher 的环境，Python版本 3.7
conda create -n stitcher python=3.7

# 激活环境
conda activate stitcher

# 验证Python版本
python --version  # 应该显示 Python 3.7.x
```

### 步骤3：安装PyTorch

根据您的系统选择合适的安装命令：

#### GPU版本（CUDA 10.2）
```bash
conda install pytorch==1.7.1 torchvision==0.8.2 cudatoolkit=10.2 -c pytorch
```

#### GPU版本（CUDA 11.1）
```bash
conda install pytorch==1.7.1 torchvision==0.8.2 cudatoolkit=11.1 -c pytorch
```

#### CPU版本
```bash
conda install pytorch==1.7.1 torchvision==0.8.2 cpuonly -c pytorch
```

**查找其他版本**：访问 [PyTorch官网](https://pytorch.org/get-started/previous-versions/) 选择适合您CUDA版本的PyTorch。

### 步骤4：安装基础依赖

```bash
# 安装基础Python包
pip install ninja yacs cython matplotlib tqdm opencv-python pillow

# 安装其他工具
pip install tensorboard  # 可选：用于可视化训练过程
pip install scipy        # 可选：某些功能需要
```

### 步骤5：安装pycocotools

```bash
# Linux/macOS
pip install pycocotools

# Windows（可能需要Visual Studio）
pip install pycocotools-windows
```

如果Windows安装失败，尝试：
```bash
pip install git+https://github.com/philferriere/cocoapi.git#subdirectory=PythonAPI
```

### 步骤6：安装APEX（可选，用于混合精度训练）

**注意**：APEX需要编译，如果安装失败可以跳过，不影响基本功能。

```bash
# 克隆APEX仓库
git clone https://github.com/NVIDIA/apex
cd apex

# 安装（仅Python操作，较快）
pip install -v --disable-pip-version-check --no-cache-dir ./

# 或者完整安装（包含C++/CUDA扩展，较慢但性能更好）
pip install -v --disable-pip-version-check --no-cache-dir --global-option="--cpp_ext" --global-option="--cuda_ext" ./

cd ..
```

### 步骤7：安装Stitcher项目

```bash
# 进入项目目录
cd /path/to/Stitcher

# 编译并安装
python setup.py build develop

# 或者直接安装
python setup.py install
```

**说明**：
- `build develop`：开发模式，代码修改后无需重新安装
- `install`：正式安装，代码修改后需要重新安装

### 步骤8：验证安装

```bash
# 测试导入
python -c "import maskrcnn_benchmark; print('安装成功！')"

# 测试CUDA是否可用（GPU版本）
python -c "import torch; print('CUDA可用:', torch.cuda.is_available())"
```

---

## 方式2：Docker安装

Docker方式适合需要快速部署或在服务器上运行的场景。

### 前置条件

**Linux:**
```bash
# 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 安装nvidia-docker（GPU版本需要）
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update && sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker
```

### 构建Docker镜像

```bash
# 进入项目目录
cd /path/to/Stitcher

# 构建默认镜像（CUDA 9.0）
docker build -t stitcher:latest ./docker/

# 或指定CUDA版本（如CUDA 10.2）
docker build -t stitcher:cuda10.2 --build-arg CUDA=10.2 --build-arg CUDNN=7 ./docker/

# 构建CPU版本
docker build -t stitcher:cpu --build-arg FORCE_CUDA=0 ./docker/
```

### 运行Docker容器

```bash
# GPU版本
docker run --gpus all -it --rm \
    -v /path/to/your/data:/data \
    -v /path/to/Stitcher:/workspace \
    stitcher:latest \
    /bin/bash

# CPU版本
docker run -it --rm \
    -v /path/to/your/data:/data \
    -v /path/to/Stitcher:/workspace \
    stitcher:cpu \
    /bin/bash
```

**参数说明**：
- `--gpus all`：使用所有GPU
- `-it`：交互式终端
- `--rm`：退出后删除容器
- `-v`：挂载目录（主机路径:容器路径）

---

## 方式3：手动安装

适合有经验的用户或需要自定义配置的场景。

### 步骤概览

1. **安装Python 3.7**
2. **安装CUDA和cuDNN**（GPU版本）
3. **安装PyTorch**
4. **安装依赖包**
5. **编译安装Stitcher**

详细步骤参考 [INSTALL.md](./INSTALL.md)。

---

## 验证安装

创建测试脚本 `test_installation.py`：

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""验证Stitcher安装"""

import sys

def test_imports():
    """测试必要的包是否可以导入"""
    print("=" * 60)
    print("测试包导入...")
    print("=" * 60)
    
    packages = [
        'torch',
        'torchvision',
        'cv2',
        'numpy',
        'PIL',
        'matplotlib',
        'yacs',
        'tqdm',
        'maskrcnn_benchmark',
    ]
    
    failed = []
    for pkg in packages:
        try:
            __import__(pkg)
            print(f"✓ {pkg:30s} 导入成功")
        except ImportError as e:
            print(f"✗ {pkg:30s} 导入失败: {e}")
            failed.append(pkg)
    
    return len(failed) == 0

def test_cuda():
    """测试CUDA是否可用"""
    print("\n" + "=" * 60)
    print("测试CUDA...")
    print("=" * 60)
    
    import torch
    
    print(f"PyTorch版本: {torch.__version__}")
    print(f"CUDA是否可用: {torch.cuda.is_available()}")
    
    if torch.cuda.is_available():
        print(f"CUDA版本: {torch.version.cuda}")
        print(f"GPU数量: {torch.cuda.device_count()}")
        for i in range(torch.cuda.device_count()):
            print(f"  GPU {i}: {torch.cuda.get_device_name(i)}")
            print(f"    显存: {torch.cuda.get_device_properties(i).total_memory / 1024**3:.2f} GB")
    else:
        print("警告: CUDA不可用，将使用CPU模式")
    
    return True

def test_maskrcnn():
    """测试maskrcnn_benchmark基本功能"""
    print("\n" + "=" * 60)
    print("测试Maskrcnn Benchmark...")
    print("=" * 60)
    
    try:
        from maskrcnn_benchmark.config import cfg
        print("✓ 配置系统正常")
        
        from maskrcnn_benchmark.modeling.detector import build_detection_model
        print("✓ 模型构建系统正常")
        
        from maskrcnn_benchmark.data import make_data_loader
        print("✓ 数据加载系统正常")
        
        return True
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

def main():
    """主函数"""
    print("\n开始验证Stitcher安装...\n")
    
    success = True
    
    # 测试包导入
    if not test_imports():
        print("\n部分包导入失败，请检查安装")
        success = False
    
    # 测试CUDA
    test_cuda()
    
    # 测试maskrcnn_benchmark
    if not test_maskrcnn():
        success = False
    
    # 总结
    print("\n" + "=" * 60)
    if success:
        print("✓ 安装验证通过！环境配置成功！")
        print("=" * 60)
        return 0
    else:
        print("✗ 安装验证失败，请检查上述错误信息")
        print("=" * 60)
        return 1

if __name__ == '__main__':
    sys.exit(main())
```

运行验证：
```bash
python test_installation.py
```

---

## 常见问题

### Q1: ImportError: No module named 'maskrcnn_benchmark'

**原因**：项目未正确安装

**解决**：
```bash
cd /path/to/Stitcher
python setup.py build develop
```

### Q2: CUDA out of memory

**原因**：显存不足

**解决**：
- 减小批次大小（在配置文件中设置 `SOLVER.IMS_PER_BATCH`）
- 减小图像尺寸
- 使用更小的模型（如 R-50-C4 代替 R-50-FPN）

### Q3: GCC版本过低

**原因**：编译CUDA扩展需要较新的GCC

**解决**：
```bash
# Ubuntu
sudo apt-get install gcc-7 g++-7
export CC=gcc-7
export CXX=g++-7
```

### Q4: Windows下pycocotools安装失败

**原因**：pycocotools需要C++编译器

**解决**：
1. 安装Visual Studio 2017或更新版本
2. 使用预编译版本：
   ```bash
   pip install pycocotools-windows
   ```
3. 或使用替代包：
   ```bash
   pip install git+https://github.com/philferriere/cocoapi.git#subdirectory=PythonAPI
   ```

### Q5: APEX安装失败

**原因**：APEX需要编译CUDA扩展

**解决**：
- 可以跳过APEX安装，仅影响混合精度训练
- 如需安装，确保CUDA和nvcc可用：
  ```bash
  nvcc --version
  ```

### Q6: 找不到libcudnn.so

**原因**：cuDNN库路径未设置

**解决**：
```bash
# 添加到~/.bashrc
export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH
source ~/.bashrc
```

### Q7: Python版本不兼容

**原因**：项目需要Python 3.6-3.8

**解决**：
```bash
# 使用Conda创建正确版本的环境
conda create -n stitcher python=3.7
conda activate stitcher
```

### Q8: 编译时内存不足

**原因**：编译C++/CUDA扩展需要大量内存

**解决**：
```bash
# 限制并行编译进程数
MAX_JOBS=2 python setup.py build develop
```

---

## 推荐配置

### 开发环境
```yaml
操作系统: Ubuntu 20.04
Python: 3.7
PyTorch: 1.7.1
CUDA: 10.2 或 11.1
GPU: GTX 1080 Ti 或更高
内存: 16GB+
```

### 生产环境
```yaml
操作系统: Ubuntu 20.04
Python: 3.7
PyTorch: 1.7.1
CUDA: 11.1
GPU: RTX 3090 或 A100
内存: 32GB+
使用Docker部署
```

---

## 下一步

环境配置完成后，请查看：
- [代码运行指南](./HOW_TO_RUN_CN.md) - 学习如何运行训练和推理
- [YOLO数据集指南](./YOLO_DATASET_GUIDE_CN.md) - 使用自己的数据集
- [项目代码分析](./PROJECT_ANALYSIS_CN.md) - 深入了解代码结构

---

## 获取帮助

如果遇到问题：
1. 查看本文档的"常见问题"部分
2. 查看 [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)
3. 运行验证脚本获取详细错误信息
4. 在GitHub Issues中搜索类似问题

**祝安装顺利！** 🚀
