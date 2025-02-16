import cv2
import numpy as np
from PIL import Image
import os
import random

class BackgroundGenerator:
    """背景图像生成器类
    
    负责生成或处理用于合成的背景图像
    """
    
    def __init__(self):
        self.image = None
        
    def load_image(self, image_path):
        """加载背景图像
        
        Args:
            image_path (str): 背景图像的路径
            
        Returns:
            bool: 加载是否成功
        """
        try:
            self.image = Image.open(image_path)
            return True
        except Exception as e:
            print(f"加载图像失败: {e}")
            return False
            
    def load_background_directory(self, directory_path):
        """加载背景图片目录
        
        Args:
            directory_path (str): 背景图片目录的路径
            
        Returns:
            bool: 加载是否成功
        """
        try:
            self.background_images = []
            for filename in os.listdir(directory_path):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                    image_path = os.path.join(directory_path, filename)
                    image = Image.open(image_path)
                    self.background_images.append(image)
            return len(self.background_images) > 0
        except Exception as e:
            print(f"加载背景图片目录失败: {e}")
            return False
            
    def get_random_background(self):
        """随机获取一个背景图像
        
        Returns:
            PIL.Image: 随机选择的背景图像
        """
        if hasattr(self, 'background_images') and self.background_images:
            return random.choice(self.background_images)
        return self.image
        
    def generate_solid_background(self, width, height, color=(255, 255, 255)):
        """生成纯色背景
        
        Args:
            width (int): 背景宽度
            height (int): 背景高度
            color (tuple): RGB颜色值，默认为白色
        """
        self.image = Image.new('RGB', (width, height), color)
        
    def generate_random_noise(self, width, height):
        """生成随机噪声背景
        
        Args:
            width (int): 背景宽度
            height (int): 背景高度
        """
        noise = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
        self.image = Image.fromarray(noise)
        
    def get_background(self):
        """获取当前背景图像
        
        Returns:
            PIL.Image: 背景图像
        """
        return self.get_random_background()
        
    def resize(self, width, height):
        """调整背景图像大小
        
        Args:
            width (int): 目标宽度
            height (int): 目标高度
        """
        if self.image:
            self.image = self.image.resize((width, height), Image.LANCZOS)