"""
ImageClassifier节点 - 图片分类器
"""
import os
import json
import torch
import numpy as np
from PIL import Image
from ..core import classifier, doubao_client


def load_default_classification_pe():
    """加载默认的分类PE"""
    pe_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts", "default_classification.txt")
    try:
        with open(pe_path, 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return "# 分类PE加载失败，请手动输入分类规则"


def tensor_to_pil_batch(tensor):
    """
    将ComfyUI的IMAGE tensor转换为PIL Image列表
    Args:
        tensor: shape [B, H, W, C], range 0-1
    Returns:
        list of PIL Images
    """
    # 转换为numpy，范围0-255
    images_np = (255. * tensor.cpu().numpy()).astype(np.uint8)
    
    # 转换为PIL Image列表
    pil_images = []
    for i in range(images_np.shape[0]):
        img = Image.fromarray(images_np[i])
        pil_images.append(img)
    
    return pil_images


class ImageClassifier:
    """
    图片分类器节点
    对输入的图片进行分类，返回分类标签
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),  # ComfyUI图片输入
                "classification_pe": ("STRING", {
                    "multiline": True,
                    "default": load_default_classification_pe(),
                    "dynamicPrompts": False
                }),
                "api_key": ("STRING", {
                    "default": "d26ed5b5-0816-4bec-b045-c353abc16667"
                }),
                "api_url": ("STRING", {
                    "default": "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
                }),
                "model": ("STRING", {
                    "default": "doubao-seed-1-6-250615"
                }),
            },
            "optional": {
                "text_requirement": ("STRING", {
                    "default": "",
                    "multiline": False
                }),
                "mode": (["auto", "single", "multi"], {
                    "default": "auto"
                }),
                "groups": ("STRING", {
                    "default": "",
                    "forceInput": False  # 可选，从BatchImageLoader输入
                }),
            }
        }
    
    RETURN_TYPES = ("STRING", "IMAGE")
    RETURN_NAMES = ("classifications", "image")
    FUNCTION = "classify"
    CATEGORY = "SmartCaption"
    
    def classify(self, image, classification_pe, api_key, api_url, model, text_requirement="", mode="auto", groups=""):
        """
        分类主函数
        
        Returns:
            (classifications_json, image)
        """
        try:
            # 获取batch size
            batch_size = image.shape[0]
            
            # 转换tensor为PIL Images
            pil_images = tensor_to_pil_batch(image)
            
            # 解析分组信息
            groups_info = None
            if groups:
                try:
                    groups_info = json.loads(groups)
                except:
                    print(f"⚠️  分组信息解析失败，将作为整体处理")
                    groups_info = None
            
            # 自动判断模式
            if mode == "auto":
                if batch_size == 1:
                    mode = "single"
                else:
                    mode = "multi"
            
            print(f"\n{'='*60}")
            print(f"📷 ImageClassifier - 开始分类")
            print(f"   模式: {mode} | 图片数: {batch_size}")
            if groups_info:
                print(f"   分组数: {len(groups_info.get('groups', []))}")
            print(f"{'='*60}")
            
            # 单图模式
            if mode == "single" or batch_size == 1:
                result = classifier.classify_single_image(
                    image=pil_images[0],
                    classification_pe=classification_pe,
                    text_requirement=text_requirement,
                    api_key=api_key,
                    api_url=api_url,
                    model=model
                )
                
                classifications_json = json.dumps(result, ensure_ascii=False)
                print(f"✅ 分类完成: {result.get('style_tag', 'ERROR')}")
                
            # 多图模式
            else:
                # 如果有分组信息，按组分别处理
                if groups_info and len(groups_info.get('groups', [])) > 1:
                    print(f"   🗂️  检测到多组图片，将分别判断关联")
                    all_results = []
                    
                    for group in groups_info['groups']:
                        group_name = group['name']
                        start_idx = group['start']
                        end_idx = group['end']
                        
                        print(f"\n   📁 处理分组: {group_name} ({group['count']}张)")
                        
                        # 提取当前组的图片
                        group_images = pil_images[start_idx:end_idx]
                        
                        # 对当前组进行分类
                        if len(group_images) == 1:
                            # 单图
                            group_result = classifier.classify_single_image(
                                image=group_images[0],
                                classification_pe=classification_pe,
                                text_requirement=text_requirement,
                                api_key=api_key,
                                api_url=api_url,
                                model=model
                            )
                            all_results.append(group_result)
                        else:
                            # 多图
                            group_result = classifier.classify_multi_images(
                                images=group_images,
                                classification_pe=classification_pe,
                                text_requirement=text_requirement,
                                api_key=api_key,
                                api_url=api_url,
                                model=model
                            )
                            all_results.append(group_result)
                    
                    # 合并所有组的结果
                    # 展开为每张图的标签列表
                    all_tags = []
                    for result in all_results:
                        if 'style_tag' in result:
                            # 单标签或有关联
                            all_tags.append(result['style_tag'])
                        elif 'style_tags' in result:
                            # 多标签
                            all_tags.extend(result['style_tags'])
                    
                    result = {"style_tags": all_tags}
                    classifications_json = json.dumps(result, ensure_ascii=False)
                    print(f"✅ 所有分组处理完成，共 {len(all_tags)} 个标签")
                    
                else:
                    # 无分组或只有一组，作为整体处理
                    result = classifier.classify_multi_images(
                        images=pil_images,
                        classification_pe=classification_pe,
                        text_requirement=text_requirement,
                        api_key=api_key,
                        api_url=api_url,
                        model=model
                    )
                    
                    classifications_json = json.dumps(result, ensure_ascii=False)
                    
                    if 'style_tag' in result:
                        print(f"✅ 多图有关联: {result['style_tag']}")
                    else:
                        print(f"⚠️  多图无关联: {result.get('style_tags', [])}")
            
            print(f"{'='*60}\n")
            
            return (classifications_json, image)
        
        except Exception as e:
            error_msg = f"分类失败: {str(e)}"
            print(f"❌ {error_msg}")
            
            # 返回错误结果
            error_json = json.dumps({
                "style_tag": "ERROR",
                "error": error_msg
            }, ensure_ascii=False)
            
            return (error_json, image)


# 节点类映射
NODE_CLASS_MAPPINGS = {
    "ImageClassifier": ImageClassifier
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageClassifier": "图片分类器 📷"
}

