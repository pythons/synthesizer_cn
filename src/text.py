import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

class TextRenderer:
    """文字渲染器类
    
    负责汉字的渲染和变换处理
    """
    
    def __init__(self):
        self.font = None
        self.text_color = (0, 0, 0)  # 默认黑色文字
        
    def load_font(self, font_path, font_size):
        """加载字体
        
        Args:
            font_path (str): 字体文件路径
            font_size (int): 字体大小
            
        Returns:
            bool: 加载是否成功
        """
        try:
            self.font = ImageFont.truetype(font_path, font_size)
            return True
        except Exception as e:
            print(f"加载字体失败: {e}")
            return False
            
    def set_text_color(self, color):
        """设置文字颜色
        
        Args:
            color (tuple): RGB颜色值
        """
        self.text_color = color
        
    def render_text(self, text, target_size=(200, 200)):
        """渲染文字
        
        Args:
            text (str): 要渲染的文字
            target_size (tuple): 目标图像大小
            
        Returns:
            PIL.Image: 渲染后的文字图像
        """
        if not self.font:
            raise ValueError("请先加载字体")
            
        # 创建目标大小的透明背景图像
        image = Image.new('RGBA', target_size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # 计算目标尺寸，可以通过修改这个比例来调整文字大小
        target_width = int(target_size[0] * 0.9)  # 增加到90%
        target_height = int(target_size[1] * 0.9)  # 增加到90%
        
        # 调整字体大小以适应目标尺寸
        font_size = self.font.size
        bbox = self.font.getbbox(text)
        current_width = bbox[2] - bbox[0]
        current_height = bbox[3] - bbox[1]
        
        # 计算缩放比例
        # 确保文字边界框的宽度和高度不为零
        if current_width <= 0 or current_height <= 0:
            # 如果边界框无效，使用默认字体大小
            new_font_size = font_size
        else:
            scale = min(target_width / current_width, target_height / current_height)
            new_font_size = int(font_size * scale)
        
        # 使用新的字体大小
        self.font = ImageFont.truetype(self.font.path, new_font_size)
        
        # 获取新字体大小下的文字边界框和字体度量信息
        bbox = self.font.getbbox(text)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        metrics = self.font.getmetrics()
        ascent = metrics[0]
        descent = metrics[1]
        
        # 计算居中位置
        # 使用mm作为anchor实现完全居中
        x = target_size[0] // 2
        y = target_size[1] // 2
        
        # 绘制文字，使用mm作为anchor实现水平和垂直居中
        draw.text((x, y), text, font=self.font, fill=self.text_color, anchor="mm")
        return image
        
    def apply_rotation(self, image, angle):
        """对文字图像进行旋转
        
        Args:
            image (PIL.Image): 文字图像
            angle (float): 旋转角度
            
        Returns:
            PIL.Image: 旋转后的图像
        """
        return image.rotate(angle, expand=True, resample=Image.BICUBIC)
        
    def apply_perspective(self, image, points):
        """应用透视变换
        
        Args:
            image (PIL.Image): 文字图像
            points (list): 四个角点的坐标
            
        Returns:
            PIL.Image: 变换后的图像
        """
        width = image.width
        height = image.height
        
        # 源图像的四个角点
        src_points = np.float32([
            [0, 0],
            [width-1, 0],
            [width-1, height-1],
            [0, height-1]
        ])
        
        # 目标图像的四个角点，限制变换范围
        dst_points = np.float32(points)
        # 计算每个点的偏移量，并限制在合理范围内
        max_offset = min(width, height) * 0.05  # 限制最大偏移为图像尺寸的5%
        for i in range(4):
            dx = dst_points[i][0] - src_points[i][0]
            dy = dst_points[i][1] - src_points[i][1]
            # 使用双曲正切函数限制偏移量
            dx = max_offset * np.tanh(dx / max_offset)
            dy = max_offset * np.tanh(dy / max_offset)
            dst_points[i] = [src_points[i][0] + dx, src_points[i][1] + dy]
        
        # 计算透视变换矩阵
        matrix = cv2.getPerspectiveTransform(src_points, dst_points)
        
        # 转换为OpenCV格式进行处理
        img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGBA2BGRA)
        
        # 应用透视变换，使用更好的插值方法
        result = cv2.warpPerspective(
            img_cv,
            matrix,
            (width, height),
            flags=cv2.INTER_CUBIC,  # 使用三次插值
            borderMode=cv2.BORDER_TRANSPARENT
        )
        
        # 转换回PIL格式
        return Image.fromarray(cv2.cvtColor(result, cv2.COLOR_BGRA2RGBA))
