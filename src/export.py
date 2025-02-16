import os
import json
import shutil
import random
from PIL import Image

class DatasetExporter:
    """数据集导出类
    
    支持将合成的数据集导出为不同的格式，并支持训练集/验证集/测试集划分
    """
    
    def __init__(self, input_dir):
        """初始化导出器
        
        Args:
            input_dir (str): 输入目录，包含图片和annotations.json
        """
        self.input_dir = input_dir
        self.annotations_path = os.path.join(input_dir, 'annotations.json')
        
        # 加载标注数据
        if not os.path.exists(self.annotations_path):
            raise FileNotFoundError(f'找不到标注文件：{self.annotations_path}')
            
        with open(self.annotations_path, 'r', encoding='utf-8') as f:
            self.annotations = json.load(f)
            
    def split_dataset(self, output_dir, train_ratio=0.7, val_ratio=0.2, test_ratio=0.1):
        """划分数据集
        
        Args:
            output_dir (str): 输出目录
            train_ratio (float): 训练集比例
            val_ratio (float): 验证集比例
            test_ratio (float): 测试集比例
            
        Returns:
            tuple: (训练集索引, 验证集索引, 测试集索引)
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # 检查比例和是否为1
        total_ratio = train_ratio + val_ratio + test_ratio
        if not (0.99 < total_ratio < 1.01):  # 允许小数点误差
            raise ValueError('数据集划分比例之和必须为1')
            
        # 随机打乱数据
        indices = list(range(len(self.annotations)))
        random.shuffle(indices)
        
        # 计算每个集合的大小
        total_size = len(indices)
        train_size = int(total_size * train_ratio)
        val_size = int(total_size * val_ratio)
        
        # 划分数据集
        train_indices = indices[:train_size]
        val_indices = indices[train_size:train_size + val_size]
        test_indices = indices[train_size + val_size:]
        
        return train_indices, val_indices, test_indices
    
    def export_createml(self, output_dir, split=True, train_ratio=0.7, val_ratio=0.2, test_ratio=0.1):
        """导出为CreateML格式
        
        Args:
            output_dir (str): 输出目录
            split (bool): 是否划分数据集
            train_ratio (float): 训练集比例
            val_ratio (float): 验证集比例
            test_ratio (float): 测试集比例
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        if split:
            train_indices, val_indices, test_indices = self.split_dataset(
                output_dir, train_ratio, val_ratio, test_ratio)
            
            # 创建子目录
            train_dir = os.path.join(output_dir, 'train')
            val_dir = os.path.join(output_dir, 'val')
            test_dir = os.path.join(output_dir, 'test')
            
            os.makedirs(train_dir, exist_ok=True)
            os.makedirs(val_dir, exist_ok=True)
            os.makedirs(test_dir, exist_ok=True)
            
            # 导出各个数据集
            self._export_createml_subset(train_indices, train_dir)
            self._export_createml_subset(val_indices, val_dir)
            self._export_createml_subset(test_indices, test_dir)
        else:
            # 导出完整数据集
            self._export_createml_subset(range(len(self.annotations)), output_dir)
    
    def _export_createml_subset(self, indices, output_dir):
        """导出CreateML格式的子数据集
        
        Args:
            indices (list): 数据索引列表
            output_dir (str): 输出目录
        """
        createml_annotations = []
        
        for idx in indices:
            ann = self.annotations[idx]
            
            # 复制图片
            image_name = os.path.basename(ann['image_path'])
            shutil.copy2(ann['image_path'], os.path.join(output_dir, image_name))
            
            # 转换标注格式
            createml_ann = {
                'image': image_name,
                'annotations': [{
                    'label': ann['text'],
                    'coordinates': {
                        'x': ann['position'][0] + ann['size'][0] / 2,
                        'y': ann['position'][1] + ann['size'][1] / 2,
                        'width': ann['size'][0],
                        'height': ann['size'][1]
                    }
                }]
            }
            createml_annotations.append(createml_ann)
        
        # 保存标注文件
        with open(os.path.join(output_dir, 'annotations.json'), 'w', encoding='utf-8') as f:
            json.dump(createml_annotations, f, ensure_ascii=False, indent=2)
    
    def export_yolo(self, output_dir, split=True, train_ratio=0.7, val_ratio=0.2, test_ratio=0.1):
        """导出为YOLO格式
        
        Args:
            output_dir (str): 输出目录
            split (bool): 是否划分数据集
            train_ratio (float): 训练集比例
            val_ratio (float): 验证集比例
            test_ratio (float): 测试集比例
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 创建数据集目录结构
        images_dir = os.path.join(output_dir, 'images')
        labels_dir = os.path.join(output_dir, 'labels')
        os.makedirs(images_dir, exist_ok=True)
        os.makedirs(labels_dir, exist_ok=True)
        
        if split:
            train_indices, val_indices, test_indices = self.split_dataset(
                output_dir, train_ratio, val_ratio, test_ratio)
            
            # 创建训练集/验证集/测试集目录
            for subset in ['train', 'val', 'test']:
                os.makedirs(os.path.join(images_dir, subset), exist_ok=True)
                os.makedirs(os.path.join(labels_dir, subset), exist_ok=True)
            
            # 导出各个数据集
            self._export_yolo_subset(train_indices, images_dir, labels_dir, 'train')
            self._export_yolo_subset(val_indices, images_dir, labels_dir, 'val')
            self._export_yolo_subset(test_indices, images_dir, labels_dir, 'test')
            
            # 生成data.yaml
            yaml_content = {
                'train': f'./images/train',
                'val': f'./images/val',
                'test': f'./images/test',
                'nc': 1,  # 类别数量
                'names': ['text']  # 类别名称
            }
            
            with open(os.path.join(output_dir, 'data.yaml'), 'w', encoding='utf-8') as f:
                import yaml
                yaml.dump(yaml_content, f, allow_unicode=True)
        else:
            # 导出完整数据集
            self._export_yolo_subset(range(len(self.annotations)), images_dir, labels_dir)
    
    def _export_yolo_subset(self, indices, images_dir, labels_dir, subset=None):
        """导出YOLO格式的子数据集
        
        Args:
            indices (list): 数据索引列表
            images_dir (str): 图片目录
            labels_dir (str): 标签目录
            subset (str, optional): 子集名称（train/val/test）
        """
        for idx in indices:
            ann = self.annotations[idx]
            
            # 获取图片信息
            image_path = ann['image_path']
            image_name = os.path.basename(image_path)
            image = Image.open(image_path)
            img_width, img_height = image.size
            
            # 确定目标目录
            if subset:
                dst_img_dir = os.path.join(images_dir, subset)
                dst_label_dir = os.path.join(labels_dir, subset)
            else:
                dst_img_dir = images_dir
                dst_label_dir = labels_dir
            
            # 复制图片
            shutil.copy2(image_path, os.path.join(dst_img_dir, image_name))
            
            # 转换标注格式（YOLO格式：<class> <x_center> <y_center> <width> <height>）
            x_center = (ann['position'][0] + ann['size'][0] / 2) / img_width
            y_center = (ann['position'][1] + ann['size'][1] / 2) / img_height
            width = ann['size'][0] / img_width
            height = ann['size'][1] / img_height
            
            # 保存标签文件
            label_name = os.path.splitext(image_name)[0] + '.txt'
            with open(os.path.join(dst_label_dir, label_name), 'w') as f:
                f.write(f'0 {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n')
    
    def export_coco(self, output_dir, split=True, train_ratio=0.7, val_ratio=0.2, test_ratio=0.1):
        """导出为COCO格式
        
        Args:
            output_dir (str): 输出目录
            split (bool): 是否划分数据集
            train_ratio (float): 训练集比例
            val_ratio (float): 验证集比例
            test_ratio (float): 测试集比例
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        if split:
            train_indices, val_indices, test_indices = self.split_dataset(
                output_dir, train_ratio, val_ratio, test_ratio)
            
            # 创建子目录
            for subset in ['train', 'val', 'test']:
                os.makedirs(os.path.join(output_dir, subset), exist_ok=True)
            
            # 导出各个数据集
            self._export_coco_subset(train_indices, os.path.join(output_dir, 'train'))
            self._export_coco_subset(val_indices, os.path.join(output_dir, 'val'))
            self._export_coco_subset(test_indices, os.path.join(output_dir, 'test'))
        else:
            # 导出完整数据集
            self._export_coco_subset(range(len(self.annotations)), output_dir)
    
    def _export_coco_subset(self, indices, output_dir):
        """导出COCO格式的子数据集
        
        Args:
            indices (list): 数据索引列表
            output_dir (str): 输出目录
        """
        # 创建COCO格式的数据结构
        coco_data = {
            'info': {
                'description': 'Synthesized Chinese Text Dataset',
                'version': '1.0',
                'year': 2024,
                'contributor': 'Synthesizer',
                'date_created': '2024'
            },
            'licenses': [{
                'id': 1,
                'name': 'Unknown',
                'url': 'Unknown'
            }],
            'images': [],
            'annotations': [],
            'categories': [{
                'id': 1,
                'name': 'text',
                'supercategory': 'text'
            }]
        }
        
        ann_id = 1  # COCO格式要求annotation_id从1开始
        
        for img_id, idx in enumerate(indices, 1):  # COCO格式要求image_id从1开始
            ann = self.annotations[idx]
            
            # 复制图片
            image_name = os.path.basename(ann['image_path'])
            shutil.copy2(ann['image_path'], os.path.join(output_dir, image_name))
            
            # 获取图片信息
            image = Image.open(ann['image_path'])
            width, height = image.size
            
            # 添加图片信息
            coco_data['images'].append({
                'id': img_id,
                'width': width,
                'height': height,
                'file_name': image_name,
                'license': 1,
                'date_captured': '2024'
            })
            
            # 添加标注信息
            x, y = ann['position']
            w, h = ann['size']
            
            coco_data['annotations'].append({
                'id': ann_id,
                'image_id': img_id,
                'category_id': 1,
                'bbox': [x, y, w, h],
                'area': w * h,
                'segmentation': [],  # COCO格式要求，但我们不需要分割标注
                'iscrowd': 0,
                'attributes': {
                    'text': ann['text'],
                    'transform': ann['transform']
                }
            })