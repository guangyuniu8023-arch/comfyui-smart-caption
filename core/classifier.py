"""
图片分类器（ComfyUI版本）
支持单图和多图分类，集成关联判断
"""
from typing import List, Dict, Any, Union
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image
from .doubao_client import call_doubao_api
from .multi_pic import multi_image_relation_check


def classify_single_image(
    image: Union[str, Image.Image],
    classification_pe: str,
    text_requirement: str = "",
    api_key: str = "",
    api_url: str = "",
    model: str = ""
) -> Dict[str, Any]:
    """
    对单张图片进行分类
    
    Args:
        image: PIL Image对象或文件路径
        classification_pe: 分类PE
        text_requirement: 文本需求（可选）
        api_key: Doubao API Key
        api_url: API URL
        model: 模型名称
    
    Returns:
        {"style_tag": "日常plog"} 或
        {"style_tag": "文案", "text": "..."}
    """
    try:
        result = call_doubao_api(
            image=image,
            prompt=classification_pe,
            text_requirement=text_requirement,
            api_key=api_key,
            api_url=api_url,
            model=model
        )
        
        # 验证返回格式
        if 'style_tag' not in result:
            raise ValueError(f"API 返回结果缺少 style_tag 字段: {result}")
        
        return result
    
    except Exception as e:
        return {
            'style_tag': 'ERROR',
            'error': str(e)
        }


def classify_multi_images(
    images: List[Union[str, Image.Image]],
    classification_pe: str,
    text_requirement: str = "",
    api_key: str = "",
    api_url: str = "",
    model: str = "",
    max_workers: int = 5
) -> Dict[str, Any]:
    """
    对多张图片进行分类并判断关联性
    
    Args:
        images: PIL Image列表或文件路径列表
        classification_pe: 分类PE
        text_requirement: 文本需求（可选）
        api_key: Doubao API Key
        api_url: API URL
        model: 模型名称
        max_workers: 并发线程数
    
    Returns:
        有关联: {"style_tag": "日常plog_multi_pic"}
        无关联: {"style_tags": ["人像自拍", "日常plog", "抽象文案"]}
    """
    if not images or len(images) < 2:
        raise ValueError("多图模式至少需要2张图片")
    
    # 并发调用单图分类
    individual_results = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        future_to_idx = {
            executor.submit(
                classify_single_image,
                img,
                classification_pe,
                text_requirement,
                api_key,
                api_url,
                model
            ): idx
            for idx, img in enumerate(images)
        }
        
        # 收集结果（按原始顺序）
        idx_to_result = {}
        for future in as_completed(future_to_idx):
            idx = future_to_idx[future]
            try:
                result = future.result()
                idx_to_result[idx] = result
            except Exception as e:
                idx_to_result[idx] = {
                    'style_tag': 'ERROR',
                    'error': str(e)
                }
        
        # 按原始顺序排列结果
        individual_results = [idx_to_result[i] for i in range(len(images))]
    
    # 提取所有 style_tag
    tags = [result.get('style_tag', 'ERROR') for result in individual_results]
    
    # 调用关联判断函数
    try:
        relation_result = multi_image_relation_check(
            images=list(range(len(images))),  # 传索引即可
            tags=tags,
            threshold=0.5
        )
        
        if relation_result['result'] == 'yes':
            # 有关联：返回统一标签
            return {
                'style_tag': relation_result['tag']
            }
        else:
            # 无关联：返回标签列表
            return {
                'style_tags': tags
            }
    
    except Exception as e:
        # 如果关联判断失败，返回无关联结果
        return {
            'style_tags': tags,
            'error': str(e)
        }

