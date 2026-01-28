#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证Stitcher安装

测试所有必要的依赖是否正确安装
"""

import sys

def test_imports():
    """测试必要的包是否可以导入"""
    print("=" * 60)
    print("测试包导入...")
    print("=" * 60)
    
    packages = [
        ('torch', 'PyTorch'),
        ('torchvision', 'TorchVision'),
        ('cv2', 'OpenCV'),
        ('numpy', 'NumPy'),
        ('PIL', 'Pillow'),
        ('matplotlib', 'Matplotlib'),
        ('yacs', 'YACS'),
        ('tqdm', 'TQDM'),
        ('maskrcnn_benchmark', 'Maskrcnn Benchmark'),
    ]
    
    failed = []
    for pkg_name, display_name in packages:
        try:
            __import__(pkg_name)
            print(f"✓ {display_name:30s} 导入成功")
        except ImportError as e:
            print(f"✗ {display_name:30s} 导入失败: {e}")
            failed.append(display_name)
    
    if failed:
        print(f"\n警告: {len(failed)} 个包导入失败")
        return False
    
    print("\n所有包导入成功！")
    return True

def test_cuda():
    """测试CUDA是否可用"""
    print("\n" + "=" * 60)
    print("测试CUDA...")
    print("=" * 60)
    
    try:
        import torch
        
        print(f"PyTorch版本: {torch.__version__}")
        print(f"CUDA是否可用: {torch.cuda.is_available()}")
        
        if torch.cuda.is_available():
            print(f"CUDA版本: {torch.version.cuda}")
            print(f"cuDNN版本: {torch.backends.cudnn.version()}")
            print(f"GPU数量: {torch.cuda.device_count()}")
            
            for i in range(torch.cuda.device_count()):
                props = torch.cuda.get_device_properties(i)
                print(f"\nGPU {i}: {torch.cuda.get_device_name(i)}")
                print(f"  显存总量: {props.total_memory / 1024**3:.2f} GB")
                print(f"  计算能力: {props.major}.{props.minor}")
                
                # 测试GPU内存分配
                try:
                    x = torch.zeros(1, device=f'cuda:{i}')
                    print(f"  内存测试: ✓ 通过")
                    del x
                    torch.cuda.empty_cache()
                except Exception as e:
                    print(f"  内存测试: ✗ 失败 ({e})")
        else:
            print("\n⚠️  CUDA不可用，将使用CPU模式")
            print("如果您有NVIDIA GPU，请检查：")
            print("  1. CUDA是否正确安装")
            print("  2. PyTorch是否安装了CUDA版本")
            print("  3. GPU驱动是否正确安装")
        
        return True
    except Exception as e:
        print(f"✗ CUDA测试失败: {e}")
        return False

def test_maskrcnn():
    """测试maskrcnn_benchmark基本功能"""
    print("\n" + "=" * 60)
    print("测试Maskrcnn Benchmark...")
    print("=" * 60)
    
    try:
        # 测试配置系统
        from maskrcnn_benchmark.config import cfg
        print("✓ 配置系统导入成功")
        
        # 测试模型构建
        from maskrcnn_benchmark.modeling.detector import build_detection_model
        print("✓ 模型构建系统导入成功")
        
        # 测试数据加载
        from maskrcnn_benchmark.data import make_data_loader
        print("✓ 数据加载系统导入成功")
        
        # 测试结构
        from maskrcnn_benchmark.structures.image_list import to_image_list
        from maskrcnn_benchmark.structures.bounding_box import BoxList
        print("✓ 数据结构导入成功")
        
        # 测试工具
        from maskrcnn_benchmark.utils.checkpoint import DetectronCheckpointer
        from maskrcnn_benchmark.utils.comm import get_world_size
        print("✓ 工具函数导入成功")
        
        # 测试C++扩展
        try:
            import maskrcnn_benchmark._C as _C
            print("✓ C++扩展导入成功")
        except ImportError:
            print("⚠️  C++扩展导入失败（可能需要重新编译）")
            print("  运行: python setup.py build develop")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Maskrcnn Benchmark测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_optional_packages():
    """测试可选包"""
    print("\n" + "=" * 60)
    print("测试可选包...")
    print("=" * 60)
    
    optional_packages = [
        ('tensorboard', 'TensorBoard', '用于训练可视化'),
        ('scipy', 'SciPy', '某些功能需要'),
        ('pycocotools', 'COCO API', 'COCO数据集评估'),
    ]
    
    for pkg_name, display_name, description in optional_packages:
        try:
            __import__(pkg_name)
            print(f"✓ {display_name:20s} 已安装 ({description})")
        except ImportError:
            print(f"○ {display_name:20s} 未安装 ({description})")
    
    # 检查APEX
    try:
        import apex
        print(f"✓ {'APEX':20s} 已安装 (混合精度训练)")
    except ImportError:
        print(f"○ {'APEX':20s} 未安装 (混合精度训练，可选)")
        print("  如需安装，参考: https://github.com/NVIDIA/apex")

def get_system_info():
    """获取系统信息"""
    print("\n" + "=" * 60)
    print("系统信息")
    print("=" * 60)
    
    import platform
    print(f"操作系统: {platform.system()} {platform.release()}")
    print(f"Python版本: {sys.version}")
    print(f"Python路径: {sys.executable}")
    
    try:
        import torch
        print(f"PyTorch版本: {torch.__version__}")
        print(f"PyTorch路径: {torch.__file__}")
    except:
        pass

def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("Stitcher 安装验证")
    print("=" * 60)
    
    success = True
    
    # 系统信息
    get_system_info()
    
    # 测试包导入
    if not test_imports():
        print("\n⚠️  部分必需包导入失败")
        print("请检查安装: pip install -r requirements.txt")
        success = False
    
    # 测试CUDA
    if not test_cuda():
        print("\n⚠️  CUDA测试失败")
        success = False
    
    # 测试maskrcnn_benchmark
    if not test_maskrcnn():
        print("\n⚠️  Maskrcnn Benchmark测试失败")
        print("请重新编译: python setup.py build develop")
        success = False
    
    # 测试可选包
    test_optional_packages()
    
    # 总结
    print("\n" + "=" * 60)
    if success:
        print("✓ 安装验证通过！")
        print("=" * 60)
        print("\n环境配置成功，您可以开始使用Stitcher了！")
        print("\n下一步:")
        print("  1. 查看 HOW_TO_RUN_CN.md 了解如何运行代码")
        print("  2. 查看 YOLO_DATASET_GUIDE_CN.md 使用自己的数据集")
        print("  3. 运行快速测试:")
        print("     python tools/train_net.py \\")
        print("         --config-file configs/quick_schedules/e2e_faster_rcnn_R_50_FPN_quick.yaml")
        return 0
    else:
        print("✗ 安装验证失败")
        print("=" * 60)
        print("\n请根据上述错误信息进行修复")
        print("\n常见问题:")
        print("  1. 包导入失败 → 安装缺失的包")
        print("  2. CUDA不可用 → 检查CUDA和GPU驱动")
        print("  3. C++扩展失败 → 重新编译: python setup.py build develop")
        print("\n详细帮助请查看 ENVIRONMENT_SETUP_CN.md")
        return 1

if __name__ == '__main__':
    sys.exit(main())
