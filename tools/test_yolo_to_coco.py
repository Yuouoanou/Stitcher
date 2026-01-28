#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 YOLO 到 COCO 格式转换脚本

创建一些测试数据并验证转换功能是否正常工作
"""

import os
import json
import tempfile
import shutil
from pathlib import Path
from PIL import Image
import sys

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from tools.yolo_to_coco import yolo_to_coco_bbox, convert_yolo_to_coco, load_classes


def create_test_dataset(base_dir):
    """
    创建测试数据集
    
    Args:
        base_dir: 基础目录
    """
    base_dir = Path(base_dir)
    
    # 创建目录结构
    images_dir = base_dir / "images"
    labels_dir = base_dir / "labels"
    images_dir.mkdir(parents=True, exist_ok=True)
    labels_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建类别文件
    classes = ["person", "car", "dog"]
    classes_file = base_dir / "classes.txt"
    with open(classes_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(classes))
    
    # 创建测试图像和标注
    test_cases = [
        {
            'image_name': 'test1.jpg',
            'image_size': (640, 480),
            'annotations': [
                '0 0.5 0.5 0.3 0.4',  # person in center
                '1 0.2 0.3 0.15 0.2',  # car in top-left area
            ]
        },
        {
            'image_name': 'test2.jpg',
            'image_size': (800, 600),
            'annotations': [
                '2 0.7 0.6 0.2 0.3',  # dog in bottom-right area
            ]
        },
        {
            'image_name': 'test3.jpg',
            'image_size': (1024, 768),
            'annotations': []  # 空标注（负样本）
        }
    ]
    
    for case in test_cases:
        # 创建图像
        img = Image.new('RGB', case['image_size'], color=(128, 128, 128))
        img.save(images_dir / case['image_name'])
        
        # 创建标注文件
        label_file = labels_dir / case['image_name'].replace('.jpg', '.txt')
        with open(label_file, 'w') as f:
            f.write('\n'.join(case['annotations']))
    
    return images_dir, labels_dir, classes_file, classes


def test_bbox_conversion():
    """测试 bbox 坐标转换"""
    print("测试 bbox 坐标转换...")
    
    # 测试用例 1: 中心点的目标框
    yolo_bbox = [0.5, 0.5, 0.3, 0.4]  # 中心点 (0.5, 0.5), 尺寸 (0.3, 0.4)
    img_w, img_h = 640, 480
    
    coco_bbox = yolo_to_coco_bbox(yolo_bbox, img_w, img_h)
    
    expected_x = 0.5 * 640 - 0.3 * 640 / 2  # 224
    expected_y = 0.5 * 480 - 0.4 * 480 / 2  # 144
    expected_w = 0.3 * 640  # 192
    expected_h = 0.4 * 480  # 192
    
    assert abs(coco_bbox[0] - expected_x) < 1e-6, f"x 坐标错误: {coco_bbox[0]} != {expected_x}"
    assert abs(coco_bbox[1] - expected_y) < 1e-6, f"y 坐标错误: {coco_bbox[1]} != {expected_y}"
    assert abs(coco_bbox[2] - expected_w) < 1e-6, f"宽度错误: {coco_bbox[2]} != {expected_w}"
    assert abs(coco_bbox[3] - expected_h) < 1e-6, f"高度错误: {coco_bbox[3]} != {expected_h}"
    
    # 测试用例 2: 验证边界限制
    yolo_bbox_edge = [0.95, 0.95, 0.2, 0.2]  # 接近边界的目标框
    coco_bbox_edge = yolo_to_coco_bbox(yolo_bbox_edge, img_w, img_h)
    
    # 确保坐标不超出图像边界
    assert coco_bbox_edge[0] >= 0, "x 坐标不应为负"
    assert coco_bbox_edge[1] >= 0, "y 坐标不应为负"
    assert coco_bbox_edge[0] + coco_bbox_edge[2] <= img_w, f"bbox 不应超出图像右边界: {coco_bbox_edge[0] + coco_bbox_edge[2]} > {img_w}"
    assert coco_bbox_edge[1] + coco_bbox_edge[3] <= img_h, f"bbox 不应超出图像下边界: {coco_bbox_edge[1] + coco_bbox_edge[3]} > {img_h}"
    assert coco_bbox_edge[2] > 0, "宽度应该大于0"
    assert coco_bbox_edge[3] > 0, "高度应该大于0"
    
    # 测试用例 3: 验证无效坐标会抛出异常
    try:
        invalid_bbox = [1.5, 0.5, 0.3, 0.4]  # 超出范围
        yolo_to_coco_bbox(invalid_bbox, img_w, img_h)
        assert False, "应该抛出 ValueError"
    except ValueError:
        pass  # 期望的行为
    
    print("✓ bbox 坐标转换测试通过")


def test_classes_loading():
    """测试类别文件加载"""
    print("测试类别文件加载...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建类别文件
        classes_file = Path(tmpdir) / "classes.txt"
        with open(classes_file, 'w', encoding='utf-8') as f:
            f.write("person\ncar\ndog\n")
        
        # 加载类别
        classes = load_classes(classes_file)
        
        assert len(classes) == 3, f"类别数量错误: {len(classes)} != 3"
        assert classes == ["person", "car", "dog"], f"类别内容错误: {classes}"
    
    print("✓ 类别文件加载测试通过")


def test_full_conversion():
    """测试完整的数据集转换"""
    print("测试完整的数据集转换...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建测试数据集
        images_dir, labels_dir, classes_file, classes = create_test_dataset(tmpdir)
        
        # 执行转换
        coco_data = convert_yolo_to_coco(
            str(images_dir),
            str(labels_dir),
            classes,
            split='test'
        )
        
        # 验证结果
        assert 'images' in coco_data, "缺少 images 字段"
        assert 'annotations' in coco_data, "缺少 annotations 字段"
        assert 'categories' in coco_data, "缺少 categories 字段"
        
        # 验证图像数量
        assert len(coco_data['images']) == 3, f"图像数量错误: {len(coco_data['images'])} != 3"
        
        # 验证类别数量
        assert len(coco_data['categories']) == 3, f"类别数量错误: {len(coco_data['categories'])} != 3"
        
        # 验证类别内容
        for idx, cat in enumerate(coco_data['categories']):
            assert cat['id'] == idx + 1, f"类别 ID 错误: {cat['id']} != {idx + 1}"
            assert cat['name'] == classes[idx], f"类别名称错误: {cat['name']} != {classes[idx]}"
        
        # 验证标注数量（test1.jpg 有 2 个，test2.jpg 有 1 个，test3.jpg 有 0 个）
        assert len(coco_data['annotations']) == 3, f"标注数量错误: {len(coco_data['annotations'])} != 3"
        
        # 验证标注内容
        for ann in coco_data['annotations']:
            assert 'id' in ann, "标注缺少 id 字段"
            assert 'image_id' in ann, "标注缺少 image_id 字段"
            assert 'category_id' in ann, "标注缺少 category_id 字段"
            assert 'bbox' in ann, "标注缺少 bbox 字段"
            assert 'area' in ann, "标注缺少 area 字段"
            assert len(ann['bbox']) == 4, f"bbox 长度错误: {len(ann['bbox'])} != 4"
            assert ann['area'] > 0, f"面积应该大于 0: {ann['area']}"
        
        # 验证图像信息存在且合理
        for img in coco_data['images']:
            assert img['width'] > 0, f"图像宽度应该大于 0: {img['width']}"
            assert img['height'] > 0, f"图像高度应该大于 0: {img['height']}"
            assert 'file_name' in img, "图像缺少 file_name 字段"
        
        print("✓ 完整数据集转换测试通过")
        
        # 打印结果摘要
        print("\n转换结果摘要:")
        print(f"  - 图像数量: {len(coco_data['images'])}")
        print(f"  - 标注数量: {len(coco_data['annotations'])}")
        print(f"  - 类别数量: {len(coco_data['categories'])}")
        print(f"  - 类别列表: {[cat['name'] for cat in coco_data['categories']]}")


def test_json_output():
    """测试 JSON 文件输出"""
    print("测试 JSON 文件输出...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建测试数据集
        images_dir, labels_dir, classes_file, classes = create_test_dataset(tmpdir)
        
        # 执行转换
        coco_data = convert_yolo_to_coco(
            str(images_dir),
            str(labels_dir),
            classes,
            split='test'
        )
        
        # 保存 JSON
        output_file = Path(tmpdir) / "output.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(coco_data, f, indent=2)
        
        # 验证文件存在
        assert output_file.exists(), "JSON 文件未创建"
        
        # 重新加载并验证
        with open(output_file, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        
        assert loaded_data == coco_data, "保存和加载的数据不一致"
        
        print("✓ JSON 文件输出测试通过")


def main():
    """运行所有测试"""
    print("=" * 60)
    print("YOLO 到 COCO 格式转换测试")
    print("=" * 60)
    print()
    
    try:
        test_bbox_conversion()
        print()
        
        test_classes_loading()
        print()
        
        test_full_conversion()
        print()
        
        test_json_output()
        print()
        
        print("=" * 60)
        print("所有测试通过！✓")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n✗ 测试失败: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
