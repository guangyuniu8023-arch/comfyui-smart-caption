from typing import List, Dict, Any
from collections import Counter


def multi_image_relation_check(
    images: List[Any],
    tags: List[str],
    threshold: float = 0.5
) -> Dict[str, Any]:
    """
    多图关联判断（至少2张图）
    
    Args:
        images: 图片列表（至少2张）
        tags: 对应的分类标签列表
        threshold: 关联判断阈值，默认0.5
    
    Returns:
        有关联: {"result": "yes", "tag": "日常plog_multi_pic"}
        无关联: {"result": "no", "items": [{"image": ..., "tag": "..."}, ...]}
    """
    # 参数校验
    if not images or not tags:
        raise ValueError("images和tags不能为空")
    
    if len(images) != len(tags):
        raise ValueError("images和tags长度不一致")
    
    # 统计标签并找出占比最高的
    tag_counts = Counter(tags)
    max_tag = max(tag_counts, key=tag_counts.get)
    max_ratio = tag_counts[max_tag] / len(tags)
    
    # 判断是否有关联
    if max_ratio >= threshold:
        return {
            "result": "yes",
            "tag": f"{max_tag}_multi_pic"
        }
    else:
        return {
            "result": "no",
            "items": [
                {"image": img, "tag": tag}
                for img, tag in zip(images, tags)
            ]
        }

