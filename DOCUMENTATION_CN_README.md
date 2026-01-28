# 新增文档说明 / New Documentation

本项目新增了以下中文文档，帮助您理解项目结构并使用 YOLO 格式数据集进行训练。

This project now includes the following Chinese documentation to help you understand the project structure and train with YOLO format datasets.

---

## 📚 文档列表 / Documentation List

### 1. [PROJECT_ANALYSIS_CN.md](./PROJECT_ANALYSIS_CN.md)
**项目代码分析文档（中文版）**

详细说明：
- 项目目录结构
- 每个核心文件的作用和功能
- Stitcher 算法的实现原理
- 数据处理流程
- 配置系统说明

适合：想要深入了解项目代码结构和 Stitcher 算法原理的用户

### 2. [YOLO_DATASET_GUIDE_CN.md](./YOLO_DATASET_GUIDE_CN.md)
**YOLO 格式数据集使用指南（中文版）**

包含内容：
- YOLO 格式详细说明
- 数据集准备步骤
- 格式转换方法
- 数据集注册流程
- 配置文件设置
- 训练和评估命令
- 常见问题解答
- 完整示例

适合：想要使用自己的 YOLO 格式数据集训练模型的用户

### 3. [tools/yolo_to_coco.py](./tools/yolo_to_coco.py)
**YOLO 到 COCO 格式转换脚本**

功能：
- 将 YOLO 格式标注转换为 COCO JSON 格式
- 支持自定义类别
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
