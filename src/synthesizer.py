import random
import json
from PIL import Image

class Synthesizer:
    """合成器类
    
    负责将背景和文字组合，生成标注数据
    """
    
    def __init__(self, background_generator, text_renderer):
        """初始化合成器
        
        Args:
            background_generator: 背景生成器实例
            text_renderer: 文字渲染器实例
        """
        self.background_generator = background_generator
        self.text_renderer = text_renderer
        
    def generate_random_position(self, text_width, text_height, background_width, background_height):
        """生成随机位置
        
        Args:
            text_width (int): 文字图像宽度
            text_height (int): 文字图像高度
            background_width (int): 背景图像宽度
            background_height (int): 背景图像高度
            
        Returns:
            tuple: (x, y) 坐标
        """
        # 确保文字不超过背景尺寸
        if text_width > background_width:
            text_width = background_width
        if text_height > background_height:
            text_height = background_height
            
        # 计算有效的随机范围
        max_x = max(0, background_width - text_width)
        max_y = max(0, background_height - text_height)
        
        x = random.randint(0, max_x)
        y = random.randint(0, max_y)
        return (x, y)
        
    def generate_random_transform(self):
        """生成随机变换参数
        
        Returns:
            dict: 变换参数
        """
        return {
            'rotation': random.uniform(-2, 2)  # 减小旋转角度范围
        }
        
    def synthesize(self, text, transform=None):
        """合成图像
        
        Args:
            text (str): 要合成的文字
            transform (dict, optional): 变换参数
            
        Returns:
            tuple: (合成后的图像, 标注数据)
        """
        # 获取背景图像
        background = self.background_generator.get_background()
        if not background:
            raise ValueError("背景图像未设置")
            
        # 渲染文字
        text_image = self.text_renderer.render_text(text)
        
        # 应用变换
        if transform:
            if 'rotation' in transform:
                text_image = self.text_renderer.apply_rotation(text_image, transform['rotation'])
            if 'perspective' in transform:
                text_image = self.text_renderer.apply_perspective(text_image, transform['perspective'])
        
        # 生成随机位置
        position = self.generate_random_position(
            text_image.width,
            text_image.height,
            background.width,
            background.height,
        )
        
        # 合成图像
        result = background.copy()
        result.paste(text_image, position, text_image)
        
        # 生成标注数据
        annotation = {
            'text': text,
            'position': (position[0] + 10, position[1] + 10),
            'size': (text_image.width - 20, text_image.height - 20),
            'transform': transform if transform else {}
        }
        
        return result, annotation
        
    def batch_synthesize(self, texts, output_dir, start_index=0):
        """批量合成图像
        
        Args:
            texts (list): 要合成的文字列表
            output_dir (str): 输出目录
            start_index (int): 起始索引
            
        Returns:
            list: 标注数据列表
        """
        annotations = []
        
        for i, text in enumerate(texts, start_index):
            # 生成随机变换
            transform = self.generate_random_transform()
            
            # 合成图像
            image, annotation = self.synthesize(text, transform)
            
            # 保存图像
            image_path = f"{output_dir}/{i:06d}.png"
            image.save(image_path)
            
            # 添加图像路径到标注数据
            annotation['image_path'] = image_path
            annotations.append(annotation)
            
        return annotations