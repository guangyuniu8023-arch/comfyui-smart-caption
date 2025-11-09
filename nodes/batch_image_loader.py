"""
BatchImageLoader节点 - 批量图片加载器
从文件夹加载多张图片，支持自动分组
"""
import os
import json
import torch
import numpy as np
from PIL import Image


def load_images_from_folder(folder_path, max_images=100):
    """
    从文件夹加载所有图片（支持自动分组）
    
    Args:
        folder_path: 文件夹路径
        max_images: 最大加载图片数
    
    Returns:
        (pil_images, groups_info)
        - pil_images: list of PIL Images
        - groups_info: dict with group structure
    """
    if not os.path.exists(folder_path):
        raise ValueError(f"文件夹不存在: {folder_path}")
    
    if not os.path.isdir(folder_path):
        raise ValueError(f"路径不是文件夹: {folder_path}")
    
    # 支持的图片格式
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
    
    # 检查是否有子文件夹
    subdirs = [d for d in os.listdir(folder_path) 
               if os.path.isdir(os.path.join(folder_path, d))]
    
    pil_images = []
    groups = []  # 存储每组的起始和结束索引
    
    if subdirs:
        # 有子文件夹：按子文件夹分组
        print(f"   📂 检测到 {len(subdirs)} 个子文件夹，将自动分组")
        
        for subdir in sorted(subdirs):
            subdir_path = os.path.join(folder_path, subdir)
            group_start = len(pil_images)
            
            # 加载当前子文件夹的图片
            for filename in sorted(os.listdir(subdir_path)):
                ext = os.path.splitext(filename)[1].lower()
                if ext in image_extensions:
                    file_path = os.path.join(subdir_path, filename)
                    try:
                        img = Image.open(file_path)
                        if img.mode != 'RGB':
                            img = img.convert('RGB')
                        pil_images.append(img)
                        
                        if len(pil_images) >= max_images:
                            break
                    except Exception as e:
                        print(f"⚠️  加载图片失败: {file_path} - {str(e)}")
                        continue
            
            group_end = len(pil_images)
            
            # 记录分组（如果该组有图片）
            if group_end > group_start:
                groups.append({
                    "name": subdir,
                    "start": group_start,
                    "end": group_end,
                    "count": group_end - group_start
                })
                print(f"   ✓ {subdir}: {group_end - group_start} 张图片")
            
            if len(pil_images) >= max_images:
                break
    else:
        # 没有子文件夹：所有图片作为一组
        print(f"   📄 无子文件夹，所有图片作为一组")
        
        for filename in sorted(os.listdir(folder_path)):
            ext = os.path.splitext(filename)[1].lower()
            if ext in image_extensions:
                file_path = os.path.join(folder_path, filename)
                try:
                    img = Image.open(file_path)
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    pil_images.append(img)
                    
                    if len(pil_images) >= max_images:
                        break
                except Exception as e:
                    print(f"⚠️  加载图片失败: {file_path} - {str(e)}")
                    continue
        
        # 所有图片作为一组
        if pil_images:
            groups.append({
                "name": "all",
                "start": 0,
                "end": len(pil_images),
                "count": len(pil_images)
            })
    
    if not pil_images:
        raise ValueError(f"文件夹中没有找到图片: {folder_path}")
    
    # 构造分组信息
    groups_info = {
        "total_images": len(pil_images),
        "groups": groups
    }
    
    return pil_images, groups_info


def pil_batch_to_tensor(pil_images):
    """
    将PIL Image列表转换为ComfyUI的IMAGE tensor
    
    Args:
        pil_images: list of PIL Images
    
    Returns:
        torch.Tensor: shape [B, H, W, C], range 0-1
    """
    if not pil_images:
        raise ValueError("图片列表为空")
    
    # 获取最大尺寸（用于统一大小）
    max_width = max(img.width for img in pil_images)
    max_height = max(img.height for img in pil_images)
    
    # 转换每张图片
    images_np = []
    for img in pil_images:
        # 如果尺寸不一致，resize到最大尺寸
        if img.size != (max_width, max_height):
            img = img.resize((max_width, max_height), Image.LANCZOS)
        
        # 转换为numpy数组
        img_np = np.array(img).astype(np.float32) / 255.0
        images_np.append(img_np)
    
    # 堆叠成batch
    batch_tensor = torch.from_numpy(np.stack(images_np, axis=0))
    
    return batch_tensor


class BatchImageLoader:
    """
    批量图片加载器节点
    从文件夹加载多张图片
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "folder_path": ("STRING", {
                    "default": "",
                    "multiline": False
                }),
            },
            "optional": {
                "max_images": ("INT", {
                    "default": 100,
                    "min": 1,
                    "max": 1000,
                    "step": 1
                }),
            }
        }
    
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("images", "groups")
    FUNCTION = "load_images"
    CATEGORY = "SmartCaption"
    
    def load_images(self, folder_path, max_images=100):
        """
        加载图片主函数
        
        Returns:
            (images_tensor, groups_json)
        """
        try:
            print(f"\n{'='*60}")
            print(f"📁 BatchImageLoader - 开始加载图片")
            print(f"   文件夹: {folder_path}")
            print(f"   最大数量: {max_images}")
            print(f"{'='*60}")
            
            # 从文件夹加载图片（支持分组）
            pil_images, groups_info = load_images_from_folder(folder_path, max_images)
            
            print(f"✅ 成功加载 {len(pil_images)} 张图片")
            print(f"   分组数: {len(groups_info['groups'])}")
            
            # 转换为tensor
            images_tensor = pil_batch_to_tensor(pil_images)
            
            # 将分组信息转为JSON
            groups_json = json.dumps(groups_info, ensure_ascii=False)
            
            print(f"   尺寸: {images_tensor.shape}")
            print(f"{'='*60}\n")
            
            return (images_tensor, groups_json)
        
        except Exception as e:
            error_msg = f"加载图片失败: {str(e)}"
            print(f"❌ {error_msg}")
            raise RuntimeError(error_msg)


# 节点类映射
NODE_CLASS_MAPPINGS = {
    "BatchImageLoader": BatchImageLoader
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "BatchImageLoader": "批量图片加载器 📁"
}

