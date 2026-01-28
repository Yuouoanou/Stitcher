# 新增文档说明 / New Documentation

本项目新增了完整的中文文档体系，包括环境配置、代码运行、项目分析和数据集使用等全方位指南。

This project now includes a complete Chinese documentation system, covering environment setup, code execution, project analysis, and dataset usage.

---

## 📚 文档列表 / Documentation List

### 🚀 快速开始 / Quick Start

#### 1. [ENVIRONMENT_SETUP_CN.md](./ENVIRONMENT_SETUP_CN.md) ⭐ **新增**
**环境配置完整指南（中文版）**

详细说明如何配置运行环境：
- 系统要求
- Conda 环境安装（推荐）
- Docker 安装
- 手动安装
- 验证安装
- 常见问题解决

适合：所有用户，特别是第一次使用的用户

#### 2. [HOW_TO_RUN_CN.md](./HOW_TO_RUN_CN.md) ⭐ **新增**
**代码运行完整指南（中文版）**

包含内容：
- 快速开始
- 数据准备
- 训练模型（单GPU/多GPU）
- 模型推理
- 模型评估
- 可视化结果
- 高级功能
- 性能基准

适合：已完成环境配置，准备开始训练的用户

### 📖 深入理解 / Deep Dive

#### 3. [PROJECT_ANALYSIS_CN.md](./PROJECT_ANALYSIS_CN.md)
**项目代码分析文档（中文版）**

详细说明：
- 项目目录结构
- 每个核心文件的作用和功能
- Stitcher 算法的实现原理
- 数据处理流程
- 配置系统说明

适合：想要深入了解项目代码结构和 Stitcher 算法原理的用户

#### 4. [YOLO_DATASET_GUIDE_CN.md](./YOLO_DATASET_GUIDE_CN.md)
**YOLO 格式数据集使用指南（中文版）**

包含内容：
- YOLO 格式详细说明
- 数据集准备步骤
- 格式转换方法
- 数据集注册流程
- 配置文件设置
- 训练和评估命令
- 常见问题解答（8个）
- 完整示例（车辆检测）

适合：想要使用自己的 YOLO 格式数据集训练模型的用户

### 🔧 工具和脚本 / Tools & Scripts

#### 5. [tools/yolo_to_coco.py](./tools/yolo_to_coco.py)
**YOLO 到 COCO 格式转换脚本**

功能：
- 将 YOLO 格式标注转换为 COCO JSON 格式
- 支持自定义类别
- 坐标验证和边界限制
- 自动处理多种图像格式
- 完整的错误检查和警告提示

使用方法：
```bash
python tools/yolo_to_coco.py \
    --images-dir /path/to/images \
    --labels-dir /path/to/labels \
    --classes /path/to/classes.txt \
    --output /path/to/output.json
```

#### 6. [tools/test_installation.py](./tools/test_installation.py) ⭐ **新增**
**安装验证脚本**

功能：
- 测试所有依赖包是否正确安装
- 检测 CUDA 是否可用
- 验证 maskrcnn_benchmark 功能
- 提供详细的诊断信息

使用方法：
```bash
python tools/test_installation.py
```

#### 7. [tools/quick_install.sh](./tools/quick_install.sh) ⭐ **新增**
**一键安装脚本（Linux）**

功能：
- 自动创建 Conda 环境
- 安装所有依赖
- 编译项目
- 验证安装

使用方法：
```bash
bash tools/quick_install.sh
```

### 🛠️ 故障排除 / Troubleshooting

#### 8. [TROUBLESHOOTING_CN.md](./TROUBLESHOOTING_CN.md) ⭐ **新增**
**故障排除指南（中文版）**

收录了20+个常见问题及解决方案：
- 安装问题（6个）
- 运行问题（3个）
- 训练问题（7个）
- 推理问题（2个）
- 数据问题（2个）
- 性能问题（3个）

适合：遇到问题时查找解决方案

---

## 🚀 快速开始 / Quick Start

### 如果您想了解项目代码
阅读 [PROJECT_ANALYSIS_CN.md](./PROJECT_ANALYSIS_CN.md)

### 如果您想使用 YOLO 数据集训练
按照 [YOLO_DATASET_GUIDE_CN.md](./YOLO_DATASET_GUIDE_CN.md) 的步骤操作

### 基本流程

1. **准备 YOLO 格式数据集**
   ```
   my_dataset/
   ├── images/
   │   ├── train/
   │   └── val/
   ├── labels/
   │   ├── train/
   │   └── val/
   └── classes.txt
   ```

2. **转换为 COCO 格式**
   ```bash
   python tools/yolo_to_coco.py \
       --images-dir my_dataset/images/train \
       --labels-dir my_dataset/labels/train \
       --classes my_dataset/classes.txt \
       --output datasets/my_dataset/annotations/instances_train.json
   ```

3. **注册数据集**
   
   编辑 `maskrcnn_benchmark/config/paths_catalog.py`

4. **创建配置文件**
   
   修改 `configs/` 中的配置文件

5. **开始训练**
   ```bash
   python tools/train_net.py \
       --config-file configs/my_config.yaml
   ```

---

## 📖 原始 README / Original README

原始的英文 README 请查看 [README.md](./README.md)

For the original English README, please see [README.md](./README.md)

---

## 🔍 关键改进 / Key Improvements

### 中文文档 / Chinese Documentation
- ✅ 完整的项目代码分析
- ✅ 详细的 YOLO 数据集使用指南
- ✅ 包含完整示例和常见问题解答

### 工具脚本 / Utility Scripts
- ✅ YOLO 到 COCO 格式转换脚本
- ✅ 自动化测试脚本
- ✅ 完善的错误处理

### 使用便利性 / Ease of Use
- ✅ 逐步指导
- ✅ 实际示例
- ✅ 参数说明
- ✅ 故障排除

---

## 💡 技术支持 / Technical Support

如果您在使用过程中遇到问题：

1. 首先查看 [YOLO_DATASET_GUIDE_CN.md](./YOLO_DATASET_GUIDE_CN.md) 中的"常见问题"部分
2. 检查您的数据集格式是否正确
3. 验证配置文件中的参数设置
4. 查看训练日志中的错误信息

If you encounter any issues:

1. First check the "Common Issues" section in [YOLO_DATASET_GUIDE_CN.md](./YOLO_DATASET_GUIDE_CN.md)
2. Verify your dataset format is correct
3. Check the parameter settings in your config file
4. Review error messages in the training logs

---

## 📝 文档维护 / Documentation Maintenance

这些文档基于当前代码库创建，如有更新请参考最新版本。

These documents are created based on the current codebase. Please refer to the latest version for updates.

---

## 🙏 致谢 / Acknowledgments

- 原始项目：[Stitcher: Feedback-driven Data Provider for Object Detection](https://arxiv.org/abs/2004.12432)
- 基础框架：[maskrcnn-benchmark](https://github.com/facebookresearch/maskrcnn-benchmark)

Original project: [Stitcher: Feedback-driven Data Provider for Object Detection](https://arxiv.org/abs/2004.12432)
Base framework: [maskrcnn-benchmark](https://github.com/facebookresearch/maskrcnn-benchmark)

### 📋 其他文档 / Other Documentation

#### 9. [PROJECT_COMPLETION_SUMMARY.md](./PROJECT_COMPLETION_SUMMARY.md)
**项目完成总结**

内容：
- 所有交付内容概览
- 快速使用指南
- 技术亮点说明
- 文件清单

#### 10. [YOLO_CONVERSION_EXAMPLE.md](./tools/YOLO_CONVERSION_EXAMPLE.md)
**转换脚本使用示例**

内容：
- 实际转换命令
- 格式对比
- 完整工作流程

---

## 🎯 使用流程 / Usage Workflow

### 第一次使用（完整流程）

```bash
# 1. 环境配置
# 查看 ENVIRONMENT_SETUP_CN.md
# 或使用一键安装脚本
bash tools/quick_install.sh

# 2. 验证安装
python tools/test_installation.py

# 3. 了解项目
# 阅读 PROJECT_ANALYSIS_CN.md

# 4. 准备数据
# 如果是 YOLO 格式，参考 YOLO_DATASET_GUIDE_CN.md
python tools/yolo_to_coco.py \
    --images-dir my_data/images \
    --labels-dir my_data/labels \
    --classes my_data/classes.txt \
    --output datasets/my_data/annotations/instances.json

# 5. 开始训练
# 参考 HOW_TO_RUN_CN.md
python tools/train_net.py \
    --config-file configs/my_config.yaml

# 6. 遇到问题
# 查看 TROUBLESHOOTING_CN.md
```

### 已有环境（快速开始）

```bash
# 1. 激活环境
conda activate stitcher

# 2. 运行快速测试
python tools/train_net.py \
    --config-file configs/quick_schedules/e2e_faster_rcnn_R_50_FPN_quick.yaml

# 3. 查看运行指南
cat HOW_TO_RUN_CN.md
```

---

## 📂 文档结构 / Documentation Structure

```
Stitcher/
├── ENVIRONMENT_SETUP_CN.md      ← 环境配置（第一步）
├── HOW_TO_RUN_CN.md            ← 代码运行（第二步）
├── PROJECT_ANALYSIS_CN.md      ← 项目分析（深入了解）
├── YOLO_DATASET_GUIDE_CN.md    ← YOLO数据集（使用自己的数据）
├── TROUBLESHOOTING_CN.md       ← 故障排除（遇到问题时）
├── DOCUMENTATION_CN_README.md  ← 文档索引（当前文件）
├── PROJECT_COMPLETION_SUMMARY.md ← 完成总结
└── tools/
    ├── yolo_to_coco.py         ← 格式转换工具
    ├── test_installation.py    ← 安装验证工具
    ├── quick_install.sh        ← 一键安装脚本
    └── YOLO_CONVERSION_EXAMPLE.md ← 转换示例
```

---

## 🔍 按需求查找文档 / Find Documentation by Need

### 我想配置环境
→ [ENVIRONMENT_SETUP_CN.md](./ENVIRONMENT_SETUP_CN.md)

### 我想开始训练
→ [HOW_TO_RUN_CN.md](./HOW_TO_RUN_CN.md)

### 我想了解代码结构
→ [PROJECT_ANALYSIS_CN.md](./PROJECT_ANALYSIS_CN.md)

### 我有 YOLO 格式数据
→ [YOLO_DATASET_GUIDE_CN.md](./YOLO_DATASET_GUIDE_CN.md)

### 我遇到了问题
→ [TROUBLESHOOTING_CN.md](./TROUBLESHOOTING_CN.md)

### 我想快速开始
→ 运行 `bash tools/quick_install.sh`

---

## 💡 重要提示 / Important Notes

### 安装顺序

1. **必须先配置环境** → ENVIRONMENT_SETUP_CN.md
2. **验证安装** → `python tools/test_installation.py`
3. **然后开始运行** → HOW_TO_RUN_CN.md

### 推荐学习路径

```
环境配置 → 安装验证 → 快速测试 → 项目分析 → 完整训练
    ↓           ↓          ↓          ↓          ↓
  SETUP      TEST     QUICK_RUN   ANALYSIS   HOW_TO_RUN
```

### 常见问题优先级

1. **环境问题** → 查看 ENVIRONMENT_SETUP_CN.md 和 TROUBLESHOOTING_CN.md
2. **运行问题** → 查看 HOW_TO_RUN_CN.md 和 TROUBLESHOOTING_CN.md
3. **数据问题** → 查看 YOLO_DATASET_GUIDE_CN.md

---

**祝您使用顺利！Good luck! 🚀**
