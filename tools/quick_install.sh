#!/bin/bash
# Stitcher 快速安装脚本
# 适用于 Ubuntu/Debian Linux

set -e  # 遇到错误立即退出

echo "=========================================="
echo "Stitcher 快速安装脚本"
echo "=========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查是否是Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo -e "${RED}错误: 此脚本仅支持Linux系统${NC}"
    echo "Windows和macOS用户请参考 ENVIRONMENT_SETUP_CN.md 手动安装"
    exit 1
fi

# 检查是否有conda
if ! command -v conda &> /dev/null; then
    echo -e "${RED}错误: 未找到conda${NC}"
    echo "请先安装Anaconda或Miniconda"
    echo "下载地址: https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

# 询问用户选择
echo "请选择安装模式:"
echo "  1) GPU版本 (推荐，需要NVIDIA GPU)"
echo "  2) CPU版本"
read -p "请输入选择 [1/2]: " mode_choice

if [[ "$mode_choice" == "1" ]]; then
    MODE="gpu"
    echo -e "${GREEN}选择: GPU版本${NC}"
    
    # 检查CUDA
    if command -v nvcc &> /dev/null; then
        CUDA_VERSION=$(nvcc --version | grep "release" | awk '{print $5}' | cut -d',' -f1)
        echo "检测到CUDA版本: $CUDA_VERSION"
    else
        echo -e "${YELLOW}警告: 未检测到CUDA，请确保已安装NVIDIA驱动和CUDA${NC}"
        read -p "是否继续? [y/n]: " continue_choice
        if [[ "$continue_choice" != "y" ]]; then
            exit 1
        fi
    fi
elif [[ "$mode_choice" == "2" ]]; then
    MODE="cpu"
    echo -e "${GREEN}选择: CPU版本${NC}"
else
    echo -e "${RED}无效选择${NC}"
    exit 1
fi

# 环境名称
ENV_NAME="stitcher"

# 检查环境是否已存在
if conda env list | grep -q "^${ENV_NAME} "; then
    echo -e "${YELLOW}环境 ${ENV_NAME} 已存在${NC}"
    read -p "是否删除并重新创建? [y/n]: " recreate_choice
    if [[ "$recreate_choice" == "y" ]]; then
        echo "删除旧环境..."
        conda env remove -n ${ENV_NAME} -y
    else
        echo "保留现有环境，退出安装"
        exit 0
    fi
fi

echo ""
echo "=========================================="
echo "步骤 1/7: 创建Conda环境"
echo "=========================================="
conda create -n ${ENV_NAME} python=3.7 -y
echo -e "${GREEN}✓ Conda环境创建完成${NC}"

echo ""
echo "=========================================="
echo "步骤 2/7: 安装PyTorch"
echo "=========================================="

# 激活环境
source $(conda info --base)/etc/profile.d/conda.sh
conda activate ${ENV_NAME}

if [[ "$MODE" == "gpu" ]]; then
    # GPU版本 - CUDA 10.2
    echo "安装PyTorch (GPU版本, CUDA 10.2)..."
    conda install pytorch==1.7.1 torchvision==0.8.2 cudatoolkit=10.2 -c pytorch -y
else
    # CPU版本
    echo "安装PyTorch (CPU版本)..."
    conda install pytorch==1.7.1 torchvision==0.8.2 cpuonly -c pytorch -y
fi
echo -e "${GREEN}✓ PyTorch安装完成${NC}"

echo ""
echo "=========================================="
echo "步骤 3/7: 安装基础依赖"
echo "=========================================="
pip install ninja yacs cython matplotlib tqdm opencv-python pillow scipy

# 安装pycocotools
pip install pycocotools

echo -e "${GREEN}✓ 基础依赖安装完成${NC}"

echo ""
echo "=========================================="
echo "步骤 4/7: 安装APEX (可选)"
echo "=========================================="
echo "APEX用于混合精度训练，如果安装失败不影响基本功能"
read -p "是否安装APEX? [y/n]: " apex_choice

if [[ "$apex_choice" == "y" ]]; then
    TEMP_DIR=$(mktemp -d)
    cd $TEMP_DIR
    
    echo "克隆APEX仓库..."
    git clone https://github.com/NVIDIA/apex
    cd apex
    
    echo "安装APEX..."
    if [[ "$MODE" == "gpu" ]]; then
        pip install -v --disable-pip-version-check --no-cache-dir --global-option="--cpp_ext" --global-option="--cuda_ext" ./ || {
            echo -e "${YELLOW}APEX完整安装失败，尝试简化安装...${NC}"
            pip install -v --disable-pip-version-check --no-cache-dir ./
        }
    else
        pip install -v --disable-pip-version-check --no-cache-dir ./
    fi
    
    cd -
    rm -rf $TEMP_DIR
    echo -e "${GREEN}✓ APEX安装完成${NC}"
else
    echo "跳过APEX安装"
fi

echo ""
echo "=========================================="
echo "步骤 5/7: 编译Stitcher"
echo "=========================================="

# 获取项目根目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "编译C++/CUDA扩展..."
python setup.py build develop

echo -e "${GREEN}✓ Stitcher编译完成${NC}"

echo ""
echo "=========================================="
echo "步骤 6/7: 验证安装"
echo "=========================================="

python tools/test_installation.py

INSTALL_RESULT=$?

echo ""
echo "=========================================="
echo "步骤 7/7: 完成"
echo "=========================================="

if [[ $INSTALL_RESULT -eq 0 ]]; then
    echo -e "${GREEN}✓ 安装成功！${NC}"
    echo ""
    echo "下一步："
    echo "  1. 激活环境:"
    echo "     conda activate ${ENV_NAME}"
    echo ""
    echo "  2. 查看使用指南:"
    echo "     cat HOW_TO_RUN_CN.md"
    echo ""
    echo "  3. 运行快速测试:"
    echo "     python tools/train_net.py \\"
    echo "         --config-file configs/quick_schedules/e2e_faster_rcnn_R_50_FPN_quick.yaml \\"
    echo "         OUTPUT_DIR output/quick_test"
    echo ""
    echo "  4. 准备数据集:"
    echo "     参考 YOLO_DATASET_GUIDE_CN.md"
else
    echo -e "${RED}✗ 安装验证失败${NC}"
    echo ""
    echo "请检查错误信息并参考 ENVIRONMENT_SETUP_CN.md 手动安装"
fi

echo ""
echo "=========================================="
echo "安装脚本完成"
echo "=========================================="
