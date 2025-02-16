import os
import sys
import argparse
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.background import BackgroundGenerator
from src.text import TextRenderer
from src.synthesizer import Synthesizer

def parse_args():
    parser = argparse.ArgumentParser(description='中文标注数据合成工具')
    parser.add_argument('--mode', type=str, choices=['generate', 'export'], required=True,
                        help='运行模式：generate(生成标注数据) / export(导出数据集)')
    
    # 生成模式参数
    parser.add_argument('--font-path', type=str, default='./font/kai_ti.ttf',
                        help='字体文件路径')
    parser.add_argument('--font-size', type=int, default=32,
                        help='字体大小')
    parser.add_argument('--text-color', type=int, nargs=3, default=[0, 0, 0],
                        help='文字颜色 (RGB)')
    parser.add_argument('--background-size', type=int, nargs=2, default=[200, 200],
                        help='背景图像大小 (宽 高)')
    parser.add_argument('--background-color', type=int, nargs=3, default=[255, 255, 255],
                        help='背景颜色 (RGB)')
    parser.add_argument('--output-dir', type=str, default='./output/images',
                        help='输出目录')
    parser.add_argument('--char-count', type=int, default=50,
                        help='生成的汉字数量')
    
    # 导出模式参数
    parser.add_argument('--export-format', type=str, choices=['coco', 'yolo', 'createml'],
                        default='coco', help='导出格式')
    parser.add_argument('--export-dir', type=str, default='./output/dataset',
                        help='数据集导出目录')
    parser.add_argument('--split', action='store_true',
                        help='是否划分数据集')
    parser.add_argument('--train-ratio', type=float, default=0.7,
                        help='训练集比例')
    parser.add_argument('--val-ratio', type=float, default=0.2,
                        help='验证集比例')
    parser.add_argument('--test-ratio', type=float, default=0.1,
                        help='测试集比例')
    
    return parser.parse_args()

def generate_data(args):
    # 确保输出目录存在
    os.makedirs(args.output_dir, exist_ok=True)
    
    # 初始化组件
    bg_generator = BackgroundGenerator()
    text_renderer = TextRenderer()
    synthesizer = Synthesizer(bg_generator, text_renderer)
    
    # 加载背景图片目录
    background_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'background')
    if not bg_generator.load_background_directory(background_dir):
        # 如果加载背景图片失败，则使用纯色背景
        bg_generator.generate_solid_background(
            args.background_size[0],
            args.background_size[1],
            tuple(args.background_color)
        )
    
    # 加载字体
    if not text_renderer.load_font(args.font_path, args.font_size):
        print('加载字体失败')
        return
    
    # 设置文字颜色
    text_renderer.set_text_color(tuple(args.text_color))
    
    # 生成汉字列表
    common_chars = []
    for i in range(0xB0, 0xD8):
        for j in range(0xA1, 0xFE):
            try:
                gb_bytes = bytes([i, j])
                char = gb_bytes.decode('gb2312')
                common_chars.append(char)
            except:
                continue
    
    # 取指定数量的汉字
    common_chars = common_chars[:args.char_count]
    texts = [char for char in common_chars]
    
    # 批量生成数据
    annotations = synthesizer.batch_synthesize(texts, args.output_dir)
    
    # 保存标注数据
    import json
    with open(os.path.join(args.output_dir, 'annotations.json'), 'w', encoding='utf-8') as f:
        json.dump(annotations, f, ensure_ascii=False, indent=2)
    
    print(f'已生成 {len(texts)} 个样本')
    print(f'图像保存在: {args.output_dir}')
    print(f'标注文件保存在: {os.path.join(args.output_dir, "annotations.json")}')

def export_dataset(args):
    from src.export import DatasetExporter
    
    # 初始化数据集导出器
    exporter = DatasetExporter(args.output_dir)
    
    # 确保导出目录存在
    os.makedirs(args.export_dir, exist_ok=True)
    
    # 导出参数
    export_params = {
        'output_dir': args.export_dir,
        'split': args.split,
        'train_ratio': args.train_ratio,
        'val_ratio': args.val_ratio,
        'test_ratio': args.test_ratio
    }
    
    # 根据格式导出数据集
    if args.export_format == 'coco':
        exporter.export_coco(**export_params)
    elif args.export_format == 'yolo':
        exporter.export_yolo(**export_params)
    elif args.export_format == 'createml':
        exporter.export_createml(**export_params)
    
    print(f'数据集已导出到: {args.export_dir}')
    if args.split:
        print('包含训练集、验证集和测试集')

def main():
    args = parse_args()
    
    if args.mode == 'generate':
        generate_data(args)
    elif args.mode == 'export':
        export_dataset(args)

if __name__ == '__main__':
    main()