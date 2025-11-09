"""
MultiImageUploader节点 - 多图上传器
支持连接多个Load Image节点，自动合并成batch
"""
import torch


class MultiImageUploader:
    """
    多图上传器节点
    连接1-10个Load Image节点，自动合并成batch
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image_1": ("IMAGE",),
            },
            "optional": {
                "image_2": ("IMAGE",),
                "image_3": ("IMAGE",),
                "image_4": ("IMAGE",),
                "image_5": ("IMAGE",),
                "image_6": ("IMAGE",),
                "image_7": ("IMAGE",),
                "image_8": ("IMAGE",),
                "image_9": ("IMAGE",),
                "image_10": ("IMAGE",),
            }
        }
    
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("images",)
    FUNCTION = "merge_images"
    CATEGORY = "SmartCaption"
    
    def merge_images(
        self,
        image_1,
        image_2=None,
        image_3=None,
        image_4=None,
        image_5=None,
        image_6=None,
        image_7=None,
        image_8=None,
        image_9=None,
        image_10=None
    ):
        """
        合并多个图片为batch
        
        Returns:
            (images_batch,)
        """
        try:
            print(f"\n{'='*60}")
            print(f"🖼️  MultiImageUploader - 合并图片")
            print(f"{'='*60}")
            
            # 收集所有非None的图片
            images = [image_1]
            optional_images = [image_2, image_3, image_4, image_5, image_6, 
                             image_7, image_8, image_9, image_10]
            
            for img in optional_images:
                if img is not None:
                    images.append(img)
            
            print(f"   连接的图片数: {len(images)}")
            
            # 收集所有图片tensor
            all_tensors = []
            for idx, img in enumerate(images):
                # 每个image可能本身就是batch，需要分解
                if img.shape[0] == 1:
                    all_tensors.append(img[0])  # 去掉batch维度
                else:
                    # 已经是batch，分解每一张
                    for i in range(img.shape[0]):
                        all_tensors.append(img[i])
                print(f"   ✓ 图片 {idx+1}: shape {img.shape}")
            
            print(f"   总共收集 {len(all_tensors)} 张图片")
            
            # 统一图片尺寸（找最大尺寸）
            max_height = max(t.shape[0] for t in all_tensors)
            max_width = max(t.shape[1] for t in all_tensors)
            
            # Resize所有图片到统一尺寸
            import torch.nn.functional as F
            resized_tensors = []
            for t in all_tensors:
                if t.shape[0] != max_height or t.shape[1] != max_width:
                    # 需要resize: [H, W, C] -> [C, H, W] -> resize -> [H, W, C]
                    t_chw = t.permute(2, 0, 1).unsqueeze(0)  # [1, C, H, W]
                    t_resized = F.interpolate(
                        t_chw,
                        size=(max_height, max_width),
                        mode='bilinear',
                        align_corners=False
                    )
                    t_hwc = t_resized.squeeze(0).permute(1, 2, 0)  # [H, W, C]
                    resized_tensors.append(t_hwc)
                else:
                    resized_tensors.append(t)
            
            # 堆叠成batch: [B, H, W, C]
            result = torch.stack(resized_tensors, dim=0)
            
            print(f"✅ 合并完成: {result.shape}")
            print(f"{'='*60}\n")
            
            return (result,)
        
        except Exception as e:
            error_msg = f"合并图片失败: {str(e)}"
            print(f"❌ {error_msg}")
            raise RuntimeError(error_msg)


# 节点类映射
NODE_CLASS_MAPPINGS = {
    "MultiImageUploader": MultiImageUploader
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "MultiImageUploader": "多图上传器 🖼️"
}

