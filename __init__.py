"""
ComfyUI Smart Caption - 智能图片分类和配文生成节点

基于Doubao大模型的智能图片分类和配文生成系统
支持单图/多图分类、关联判断、自定义PE配置

作者: JJfan0508
版本: 1.0.0
"""
from .nodes.image_classifier import ImageClassifier
from .nodes.caption_generator import SmartCaptionGenerator
from .nodes.batch_image_loader import BatchImageLoader
from .nodes.multi_image_uploader import MultiImageUploader

NODE_CLASS_MAPPINGS = {
    "ImageClassifier": ImageClassifier,
    "SmartCaptionGenerator": SmartCaptionGenerator,
    "BatchImageLoader": BatchImageLoader,
    "MultiImageUploader": MultiImageUploader,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageClassifier": "图片分类器 📷",
    "SmartCaptionGenerator": "智能配文生成器 ✍️",
    "BatchImageLoader": "批量图片加载器 📁",
    "MultiImageUploader": "多图上传器 🖼️",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']

print("\n" + "=" * 60)
print("✅ ComfyUI Smart Caption 节点加载成功")
print("   - 图片分类器 📷")
print("   - 智能配文生成器 ✍️")
print("   - 批量图片加载器 📁")
print("   - 多图上传器 🖼️")
print("=" * 60 + "\n")

