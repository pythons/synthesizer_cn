# 中文标注数据合成工具

这是一个用于生成中文文字标注数据的合成工具，可以将文字渲染到各种背景图像上，并自动生成相应的标注数据。支持多种数据集格式导出，可用于训练文字检测和识别模型。

## 功能特点

- 支持自定义字体和字号
- 支持多种背景图片（PNG、JPG、JPEG、BMP）
- 可配置文字颜色和背景颜色
- 支持随机位置生成
- 支持文字旋转和透视变换
- 自动生成标注数据
- 支持导出多种数据集格式（COCO、YOLO、CreateML）
- 支持数据集划分（训练集、验证集、测试集）

## 安装要求

- Python 3.6+
- PIL (Pillow)
- OpenCV (cv2)
- NumPy

## 安装步骤

1. 克隆项目到本地：

```bash
git clone <repository_url>
cd synthesizer_cn
```

2. 安装依赖：

```bash
pip install -r requirements.txt
```

## 使用说明

### 1. 准备工作

- **字体文件**：将需要使用的字体文件（.ttf格式）放在 `font` 目录下
- **背景图片**：将背景图片放在 `background` 目录下（支持 .png、.jpg、.jpeg、.bmp 格式）

### 2. 命令行参数说明

#### 生成模式参数

```bash
--mode generate          # 运行模式：生成标注数据
--font-path             # 字体文件路径，默认：./font/kai_ti.ttf
--font-size             # 字体大小，默认：32
--text-color            # 文字颜色 (RGB)，默认：0 0 0
--background-size       # 背景图像大小 (宽 高)，默认：200 200
--background-color      # 背景颜色 (RGB)，默认：255 255 255
--output-dir           # 输出目录，默认：./output/images
--char-count           # 生成的汉字数量，默认：50
```

#### 导出模式参数

```bash
--mode export           # 运行模式：导出数据集
--export-format        # 导出格式：coco/yolo/createml，默认：coco
--export-dir           # 数据集导出目录，默认：./output/dataset
--split                # 是否划分数据集
--train-ratio          # 训练集比例，默认：0.7
--val-ratio            # 验证集比例，默认：0.2
--test-ratio           # 测试集比例，默认：0.1
```

### 3. 运行示例

#### 生成数据

基本用法：
```bash
python examples/demo.py --mode generate
```

自定义参数：
```bash
python examples/demo.py --mode generate \
    --font-path ./font/kai_ti.ttf \
    --font-size 32 \
    --text-color 0 0 0 \
    --background-size 200 200 \
    --background-color 255 255 255 \
    --output-dir ./output/images \
    --char-count 50
```

#### 导出数据集

导出为COCO格式：
```bash
python examples/demo.py --mode export --export-format coco
```

导出为YOLO格式并划分数据集：
```bash
python examples/demo.py --mode export \
    --export-format yolo \
    --split \
    --train-ratio 0.7 \
    --val-ratio 0.2 \
    --test-ratio 0.1 \
    --export-dir ./output/dataset
```

### 4. 输出说明

#### 生成模式输出

程序会在指定的输出目录下生成：

- 合成的图片文件（PNG格式）
- `annotations.json` 标注文件

标注数据格式：

```json
{
    "text": "文字内容",
    "position": [x, y],
    "size": [width, height],
    "transform": {
        "rotation": "角度",
        "perspective": [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
    },
    "image_path": "图片路径"
}
```

#### 导出模式输出

根据选择的导出格式，会在导出目录下生成相应格式的数据集文件：

- COCO格式：生成 `annotations.json` 和图片文件
- YOLO格式：生成 `.txt` 标注文件和图片文件
- CreateML格式：生成 `annotations.json` 和图片文件

如果启用数据集划分，会自动创建 train/val/test 子目录。

## 自定义使用

```python
from src.background import BackgroundGenerator
from src.text import TextRenderer
from src.synthesizer import Synthesizer

# 初始化组件
bg_generator = BackgroundGenerator()
text_renderer = TextRenderer()
synthesizer = Synthesizer(bg_generator, text_renderer)

# 加载背景和字体
bg_generator.load_background_directory('background')
text_renderer.load_font('font/kai_ti.ttf', 32)

# 生成数据
texts = ['你好', '世界']
output_dir = 'output/images'
annotations = synthesizer.batch_synthesize(texts, output_dir)
```

## 注意事项

1. 确保背景图片尺寸适合目标使用场景
2. 字体大小会根据背景尺寸自动调整，以确保文字合适显示
3. 如果未提供背景图片，将使用纯色背景
4. 所有输出目录会自动创建，无需手动创建
5. 导出数据集时请确保生成的标注数据存在