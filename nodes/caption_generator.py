"""
SmartCaptionGenerator节点 - 智能配文生成器
"""
import os
import json
import torch
import numpy as np
from PIL import Image
from concurrent.futures import ThreadPoolExecutor, as_completed
from ..core import doubao_client


def load_default_captions():
    """加载默认的配文PE配置"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "default_captions.json")
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {
            "日常plog": "请为这张日常生活照片生成一段简短的配文，风格轻松随性。配文要求：10-20字。",
            "人像自拍": "请为这张人像照片生成一段简短的配文，风格时尚个性。配文要求：10-20字。",
            "抽象文案": "请为这张宠物照片生成一段温馨可爱的配文。配文要求：10-20字。",
            "图片详细描述": "请为这张图片生成一段描述性配文。配文要求：10-20字。",
            "其他": "请为这张图片生成一段合适的配文。配文要求：10-20字。"
        }


def tensor_to_pil_batch(tensor):
    """
    将ComfyUI的IMAGE tensor转换为PIL Image列表
    Args:
        tensor: shape [B, H, W, C], range 0-1
    Returns:
        list of PIL Images
    """
    images_np = (255. * tensor.cpu().numpy()).astype(np.uint8)
    pil_images = []
    for i in range(images_np.shape[0]):
        img = Image.fromarray(images_np[i])
        pil_images.append(img)
    return pil_images


def parse_classifications(classifications_json, batch_size):
    """
    解析分类结果JSON，返回每张图对应的标签
    
    Args:
        classifications_json: JSON字符串
        batch_size: batch大小
    
    Returns:
        list of style_tags
    """
    data = json.loads(classifications_json)
    
    # 单标签情况（单图或多图有关联）
    if "style_tag" in data:
        # 所有图片使用同一个标签
        tag = data["style_tag"]
        return [tag] * batch_size
    
    # 多标签情况（多图无关联）
    elif "style_tags" in data:
        return data["style_tags"]
    
    else:
        raise ValueError("Invalid classification JSON format")


def select_pe(style_tag, pe_configs):
    """
    根据分类标签选择对应的PE
    
    Args:
        style_tag: 分类标签（如 "日常plog" 或 "日常plog_multi_pic"）
        pe_configs: PE配置字典
    
    Returns:
        对应的PE文本
    """
    # 去掉_multi_pic后缀
    base_tag = style_tag.replace("_multi_pic", "")
    
    # 映射关系
    return pe_configs.get(base_tag, pe_configs.get("其他", "请生成配文"))


class SmartCaptionGenerator:
    """
    智能配文生成器节点
    根据分类结果和配置的PE生成配文
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        default_pes = load_default_captions()
        
        return {
            "required": {
                "image": ("IMAGE",),
                "classifications": ("STRING", {
                    "forceInput": True  # 必须从其他节点输入
                }),
                "日常plog_pe": ("STRING", {
                    "multiline": True,
                    "default": default_pes.get("日常plog", ""),
                    "dynamicPrompts": False
                }),
                "人像自拍_pe": ("STRING", {
                    "multiline": True,
                    "default": default_pes.get("人像自拍", ""),
                    "dynamicPrompts": False
                }),
                "抽象文案_pe": ("STRING", {
                    "multiline": True,
                    "default": default_pes.get("抽象文案", ""),
                    "dynamicPrompts": False
                }),
                "图片详细描述_pe": ("STRING", {
                    "multiline": True,
                    "default": default_pes.get("图片详细描述", ""),
                    "dynamicPrompts": False
                }),
                "其他_pe": ("STRING", {
                    "multiline": True,
                    "default": default_pes.get("其他", ""),
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
            }
        }
    
    RETURN_TYPES = ("STRING", "IMAGE")
    RETURN_NAMES = ("captions", "image")
    FUNCTION = "generate_captions"
    CATEGORY = "SmartCaption"
    
    def generate_captions(
        self,
        image,
        classifications,
        日常plog_pe,
        人像自拍_pe,
        抽象文案_pe,
        图片详细描述_pe,
        其他_pe,
        api_key,
        api_url,
        model,
        text_requirement=""
    ):
        """
        生成配文主函数
        
        Returns:
            (captions_json, image)
        """
        try:
            batch_size = image.shape[0]
            pil_images = tensor_to_pil_batch(image)
            
            print(f"\n{'='*60}")
            print(f"✍️  SmartCaptionGenerator - 开始生成配文")
            print(f"   图片数: {batch_size}")
            print(f"{'='*60}")
            
            # 解析分类结果
            style_tags = parse_classifications(classifications, batch_size)
            
            # 准备PE配置
            pe_configs = {
                "日常plog": 日常plog_pe,
                "人像自拍": 人像自拍_pe,
                "抽象文案": 抽象文案_pe,
                "图片详细描述": 图片详细描述_pe,
                "其他": 其他_pe
            }
            
            # 为每张图片生成配文
            captions = []
            
            # 使用并发处理提高速度
            with ThreadPoolExecutor(max_workers=5) as executor:
                # 提交所有任务
                future_to_idx = {}
                for idx, (img, tag) in enumerate(zip(pil_images, style_tags)):
                    # 选择对应的PE
                    selected_pe = select_pe(tag, pe_configs)
                    
                    print(f"   📝 图片 {idx+1}: {tag} -> 生成配文中...")
                    
                    future = executor.submit(
                        doubao_client.call_doubao_api,
                        img,
                        selected_pe,
                        text_requirement,
                        api_key,
                        api_url,
                        model
                    )
                    future_to_idx[future] = idx
                
                # 收集结果
                idx_to_caption = {}
                for future in as_completed(future_to_idx):
                    idx = future_to_idx[future]
                    try:
                        result = future.result()
                        # 提取配文内容（可能在不同字段）
                        caption = result.get('caption', result.get('text', result.get('content', '生成失败')))
                        idx_to_caption[idx] = caption
                        print(f"   ✅ 图片 {idx+1}: {caption}")
                    except Exception as e:
                        idx_to_caption[idx] = f"生成失败: {str(e)}"
                        print(f"   ❌ 图片 {idx+1}: 生成失败 - {str(e)}")
                
                # 按顺序排列
                captions = [idx_to_caption[i] for i in range(batch_size)]
            
            # 构造返回JSON
            captions_json = json.dumps({
                "captions": captions
            }, ensure_ascii=False)
            
            print(f"{'='*60}")
            print(f"✅ 配文生成完成")
            print(f"{'='*60}\n")
            
            return (captions_json, image)
        
        except Exception as e:
            error_msg = f"配文生成失败: {str(e)}"
            print(f"❌ {error_msg}")
            
            # 返回错误结果
            error_json = json.dumps({
                "captions": [error_msg],
                "error": error_msg
            }, ensure_ascii=False)
            
            return (error_json, image)


# 节点类映射
NODE_CLASS_MAPPINGS = {
    "SmartCaptionGenerator": SmartCaptionGenerator
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SmartCaptionGenerator": "智能配文生成器 ✍️"
}

