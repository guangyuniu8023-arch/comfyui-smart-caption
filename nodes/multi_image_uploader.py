"""
MultiImageUploader节点 - 多图上传器
支持从input文件夹加载多张图片
"""
import os
import json
import torch
import numpy as np
from PIL import Image
import folder_paths  # ComfyUI提供的路径管理


class MultiImageUploader:
    """
    多图上传器节点
    从input文件夹加载多张图片（用户手动选择）
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        # 获取input文件夹中的所有图片
        input_dir = folder_paths.get_input_directory()
        files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
        
        return {
            "required": {
                "image_pattern": ("STRING", {
                    "default": "*.jpg",
                    "multiline": False
                }),
                "start_index": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 1000,
                    "step": 1
                }),
                "max_images": ("INT", {
                    "default": 10,
                    "min": 1,
                    "max": 1000,
                    "step": 1
                }),
            }
        }
    
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("images",)
    FUNCTION = "load_images"
    CATEGORY = "SmartCaption"
    
    def load_images(self, image_pattern, start_index=0, max_images=10):
        """
        从input文件夹加载多张图片
        
        Args:
            image_pattern: 文件模式（如 "*.jpg" 或 "photo_*.png"）
            start_index: 起始索引
            max_images: 最大加载数量
        
        Returns:
            (images_tensor,)
        """
        try:
            import glob
            
            input_dir = folder_paths.get_input_directory()
            
            print(f"\n{'='*60}")
            print(f"🖼️  MultiImageUploader - 开始加载图片")
            print(f"   Input文件夹: {input_dir}")
            print(f"   文件模式: {image_pattern}")
            print(f"{'='*60}")
            
            # 使用glob匹配文件
            pattern_path = os.path.join(input_dir, image_pattern)
            all_files = sorted(glob.glob(pattern_path))
            
            if not all_files:
                raise ValueError(f"未找到匹配的图片: {image_pattern}")
            
            print(f"   找到 {len(all_files)} 个匹配文件")
            
            # 应用起始索引和最大数量限制
            selected_files = all_files[start_index:start_index + max_images]
            
            if not selected_files:
                raise ValueError(f"起始索引 {start_index} 超出范围")
            
            print(f"   加载图片: {start_index} 到 {start_index + len(selected_files) - 1}")
            
            # 加载图片
            pil_images = []
            for file_path in selected_files:
                try:
                    img = Image.open(file_path)
                    # 转换为RGB
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    pil_images.append(img)
                    print(f"   ✓ {os.path.basename(file_path)}")
                except Exception as e:
                    print(f"   ⚠️  加载失败: {os.path.basename(file_path)} - {str(e)}")
                    continue
            
            if not pil_images:
                raise ValueError("没有成功加载任何图片")
            
            # 统一尺寸
            max_width = max(img.width for img in pil_images)
            max_height = max(img.height for img in pil_images)
            
            images_np = []
            for img in pil_images:
                if img.size != (max_width, max_height):
                    img = img.resize((max_width, max_height), Image.LANCZOS)
                
                img_np = np.array(img).astype(np.float32) / 255.0
                images_np.append(img_np)
            
            # 转换为tensor
            images_tensor = torch.from_numpy(np.stack(images_np, axis=0))
            
            print(f"✅ 成功加载 {len(pil_images)} 张图片")
            print(f"   尺寸: {images_tensor.shape}")
            print(f"{'='*60}\n")
            
            return (images_tensor,)
        
        except Exception as e:
            error_msg = f"加载图片失败: {str(e)}"
            print(f"❌ {error_msg}")
            raise RuntimeError(error_msg)


# 节点类映射
NODE_CLASS_MAPPINGS = {
    "MultiImageUploader": MultiImageUploader
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "MultiImageUploader": "多图上传器 🖼️"
}

