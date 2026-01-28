#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YOLO格式转COCO格式转换脚本
将YOLO格式的数据集转换为COCO JSON格式，以便在Stitcher项目中使用

YOLO格式：
- 每张图片对应一个txt文件
- 每行格式：<class_id> <x_center> <y_center> <width> <height>
- 坐标都是相对于图像尺寸的归一化值 [0, 1]

COCO格式：
- 单个JSON文件包含所有标注
- bbox格式：[x_min, y_min, width, height]（绝对像素坐标）
"""

import json
import os
import argparse
from pathlib import Path
from PIL import Image
from tqdm import tqdm


def parse_args():
    parser = argparse.ArgumentParser(description='Convert YOLO format to COCO format')
    parser.add_argument('--images-dir', type=str, required=True,
                        help='Path to directory containing images')
    parser.add_argument('--labels-dir', type=str, required=True,
                        help='Path to directory containing YOLO label txt files')
    parser.add_argument('--output', type=str, required=True,
                        help='Output path for COCO JSON file')
    parser.add_argument('--classes', type=str, required=True,
                        help='Path to classes.txt file (one class name per line)')
    parser.add_argument('--split', type=str, default='train',
                        help='Dataset split name (train/val/test)')
    return parser.parse_args()


def load_classes(classes_file):
    """
    加载类别文件
    
    Args:
        classes_file: 类别文件路径，每行一个类别名
        
    Returns:
        list: 类别名列表
    """
    with open(classes_file, 'r', encoding='utf-8') as f:
        classes = [line.strip() for line in f.readlines() if line.strip()]
    return classes


def yolo_to_coco_bbox(yolo_bbox, img_width, img_height):
    """
    将YOLO格式的bbox转换为COCO格式
    
    Args:
        yolo_bbox: [x_center, y_center, width, height] (归一化值 0-1)
        img_width: 图像宽度（像素）
        img_height: 图像高度（像素）
        
    Returns:
        list: [x_min, y_min, width, height] (像素值)
    """
    x_center, y_center, w, h = yolo_bbox
    
    # 转换为像素坐标
    x_center_px = x_center * img_width
    y_center_px = y_center * img_height
    w_px = w * img_width
    h_px = h * img_height
    
    # 转换为左上角坐标
    x_min = x_center_px - w_px / 2
    y_min = y_center_px - h_px / 2
    
    return [x_min, y_min, w_px, h_px]


def convert_yolo_to_coco(images_dir, labels_dir, classes, split='train'):
    """
    转换YOLO数据集到COCO格式
    
    Args:
        images_dir: 图像目录路径
        labels_dir: 标签目录路径
        classes: 类别名列表
        split: 数据集划分名称
        
    Returns:
        dict: COCO格式的数据字典
    """
    images_dir = Path(images_dir)
    labels_dir = Path(labels_dir)
    
    # 初始化COCO数据结构
    coco_data = {
        'info': {
            'description': f'YOLO to COCO converted dataset - {split}',
            'version': '1.0',
            'year': 2024,
        },
        'licenses': [],
        'images': [],
        'annotations': [],
        'categories': []
    }
    
    # 添加类别信息
    for idx, class_name in enumerate(classes):
        coco_data['categories'].append({
            'id': idx + 1,  # COCO类别ID从1开始
            'name': class_name,
            'supercategory': 'object'
        })
    
    # 支持的图像格式
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
    
    # 获取所有图像文件
    image_files = []
    for ext in image_extensions:
        image_files.extend(list(images_dir.glob(f'*{ext}')))
        image_files.extend(list(images_dir.glob(f'*{ext.upper()}')))
    
    if not image_files:
        raise ValueError(f"No images found in {images_dir}")
    
    print(f"Found {len(image_files)} images")
    
    annotation_id = 1
    
    # 处理每张图像
    for img_id, image_file in enumerate(tqdm(image_files, desc="Converting")):
        # 读取图像获取尺寸
        try:
            with Image.open(image_file) as img:
                img_width, img_height = img.size
        except Exception as e:
            print(f"Warning: Cannot read image {image_file}: {e}")
            continue
        
        # 添加图像信息
        image_info = {
            'id': img_id + 1,  # COCO图像ID从1开始
            'file_name': image_file.name,
            'width': img_width,
            'height': img_height
        }
        coco_data['images'].append(image_info)
        
        # 查找对应的标注文件
        label_file = labels_dir / f"{image_file.stem}.txt"
        
        if not label_file.exists():
            # 如果没有标注文件，跳过（可能是负样本）
            continue
        
        # 读取YOLO标注
        try:
            with open(label_file, 'r') as f:
                lines = f.readlines()
        except Exception as e:
            print(f"Warning: Cannot read label file {label_file}: {e}")
            continue
        
        # 处理每个标注
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            parts = line.split()
            if len(parts) != 5:
                print(f"Warning: Invalid annotation format in {label_file}: {line}")
                continue
            
            try:
                class_id = int(parts[0])
                yolo_bbox = [float(x) for x in parts[1:5]]
            except ValueError as e:
                print(f"Warning: Cannot parse annotation in {label_file}: {line}, {e}")
                continue
            
            # 检查类别ID是否有效
            if class_id < 0 or class_id >= len(classes):
                print(f"Warning: Invalid class_id {class_id} in {label_file}")
                continue
            
            # 转换bbox格式
            coco_bbox = yolo_to_coco_bbox(yolo_bbox, img_width, img_height)
            
            # 计算面积
            area = coco_bbox[2] * coco_bbox[3]
            
            # 添加标注信息
            annotation = {
                'id': annotation_id,
                'image_id': img_id + 1,
                'category_id': class_id + 1,  # COCO类别ID从1开始
                'bbox': coco_bbox,
                'area': area,
                'iscrowd': 0,
                'segmentation': []  # 没有分割信息
            }
            coco_data['annotations'].append(annotation)
            annotation_id += 1
    
    print(f"Conversion completed:")
    print(f"  - Total images: {len(coco_data['images'])}")
    print(f"  - Total annotations: {len(coco_data['annotations'])}")
    print(f"  - Total categories: {len(coco_data['categories'])}")
    
    return coco_data


def main():
    args = parse_args()
    
    # 检查输入路径
    if not os.path.exists(args.images_dir):
        raise ValueError(f"Images directory not found: {args.images_dir}")
    if not os.path.exists(args.labels_dir):
        raise ValueError(f"Labels directory not found: {args.labels_dir}")
    if not os.path.exists(args.classes):
        raise ValueError(f"Classes file not found: {args.classes}")
    
    # 加载类别
    classes = load_classes(args.classes)
    print(f"Loaded {len(classes)} classes: {classes}")
    
    # 转换数据集
    coco_data = convert_yolo_to_coco(
        args.images_dir,
        args.labels_dir,
        classes,
        args.split
    )
    
    # 保存COCO JSON
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(coco_data, f, indent=2, ensure_ascii=False)
    
    print(f"\nCOCO JSON saved to: {output_path}")


if __name__ == '__main__':
    main()
