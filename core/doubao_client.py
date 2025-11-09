"""
Doubao API 客户端（ComfyUI版本）
用于调用豆包大模型的图片分类和配文生成接口
"""
import base64
import json
import requests
import io
from typing import Dict, Any, Optional, Union
from pathlib import Path
from PIL import Image


def pil_to_base64(image: Image.Image) -> str:
    """将PIL Image转换为base64编码"""
    buffered = io.BytesIO()
    
    # 保存为JPEG格式
    if image.mode == 'RGBA':
        # 转换RGBA为RGB
        rgb_image = Image.new('RGB', image.size, (255, 255, 255))
        rgb_image.paste(image, mask=image.split()[3])
        rgb_image.save(buffered, format="JPEG", quality=95)
    else:
        image.save(buffered, format="JPEG", quality=95)
    
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return f"data:image/jpeg;base64,{img_str}"


def image_path_to_base64(image_path: str) -> str:
    """将图片文件路径转换为base64编码"""
    with open(image_path, 'rb') as f:
        image_data = f.read()
        b64_data = base64.b64encode(image_data).decode('utf-8')
        
        # 检测图片类型
        ext = Path(image_path).suffix.lower()
        mime_type = {
            '.jpg': 'jpeg',
            '.jpeg': 'jpeg',
            '.png': 'png',
            '.gif': 'gif',
            '.webp': 'webp',
            '.bmp': 'bmp'
        }.get(ext, 'jpeg')
        
        return f"data:image/{mime_type};base64,{b64_data}"


def call_doubao_api(
    image: Union[str, Image.Image],
    prompt: str,
    text_requirement: str = "",
    api_key: str = "",
    api_url: str = "https://ark.cn-beijing.volces.com/api/v3/chat/completions",
    model: str = "doubao-seed-1-6-250615"
) -> Dict[str, Any]:
    """
    调用 Doubao API
    
    Args:
        image: PIL Image对象或图片文件路径
        prompt: 系统提示词（PE）
        text_requirement: 文本需求（可选）
        api_key: Doubao API Key
        api_url: API URL
        model: 模型名称
    
    Returns:
        API返回的JSON结果
    """
    # 转换图片为base64
    if isinstance(image, str):
        # 文件路径
        image_base64 = image_path_to_base64(image)
    elif isinstance(image, Image.Image):
        # PIL Image
        image_base64 = pil_to_base64(image)
    else:
        raise ValueError(f"不支持的图片类型: {type(image)}")
    
    # 构造用户消息内容
    user_content = [
        {
            "type": "image_url",
            "image_url": {
                "url": image_base64
            }
        }
    ]
    
    # 构造文本部分
    if text_requirement:
        text_prompt = f'{{"image": "图片内容", "文本需求": "{text_requirement}"}}'
    else:
        text_prompt = '{"image": "图片内容"}'
    
    user_content.append({
        "type": "text",
        "text": f"{prompt}\n\n请根据以上规则，对以下输入进行分类：\n{text_prompt}\n\n只输出JSON格式结果，不要有任何其他内容。"
    })
    
    # 构造请求
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": user_content
            }
        ],
        "temperature": 0,  # 完全确定性输出，消除随机性
        "thinking": {
            "type": "disabled"  # 关闭思考模式
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # 发送请求
    try:
        response = requests.post(
            api_url,
            headers=headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        
        # 解析响应
        result = response.json()
        
        # 提取 AI 返回的内容
        if 'choices' in result and len(result['choices']) > 0:
            content = result['choices'][0]['message']['content']
            
            # 清理可能的markdown格式
            content = content.strip()
            if content.startswith('```json'):
                content = content[7:]
            if content.startswith('```'):
                content = content[3:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()
            
            # 解析 JSON
            classification_result = json.loads(content)
            return classification_result
        else:
            raise ValueError(f"API 返回格式错误: {result}")
    
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"API 请求失败: {str(e)}")
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON 解析失败: {str(e)}, 原始内容: {content}")
    except Exception as e:
        raise RuntimeError(f"调用 Doubao API 时发生错误: {str(e)}")


def call_doubao_api_for_caption(
    image: Union[str, Image.Image],
    prompt: str,
    text_requirement: str = "",
    api_key: str = "",
    api_url: str = "https://ark.cn-beijing.volces.com/api/v3/chat/completions",
    model: str = "doubao-seed-1-6-250615"
) -> str:
    """
    调用 Doubao API 生成配文（返回纯文本）
    
    Args:
        image: PIL Image对象或图片文件路径
        prompt: 配文生成PE
        text_requirement: 额外的文本需求（可选）
        api_key: Doubao API Key
        api_url: API URL
        model: 模型名称
    
    Returns:
        生成的配文文本
    """
    # 转换图片为base64
    if isinstance(image, str):
        image_base64 = image_path_to_base64(image)
    elif isinstance(image, Image.Image):
        image_base64 = pil_to_base64(image)
    else:
        raise ValueError(f"不支持的图片类型: {type(image)}")
    
    # 构造用户消息内容
    user_content = [
        {
            "type": "image_url",
            "image_url": {
                "url": image_base64
            }
        }
    ]
    
    # 构造文本部分
    if text_requirement:
        full_prompt = f"{prompt}\n\n额外要求：{text_requirement}"
    else:
        full_prompt = prompt
    
    user_content.append({
        "type": "text",
        "text": full_prompt
    })
    
    # 构造请求
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": user_content
            }
        ],
        "temperature": 0,  # 完全确定性输出
        "thinking": {
            "type": "disabled"  # 关闭思考模式
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # 发送请求
    try:
        response = requests.post(
            api_url,
            headers=headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        
        # 解析响应
        result = response.json()
        
        # 提取 AI 返回的内容（纯文本）
        if 'choices' in result and len(result['choices']) > 0:
            content = result['choices'][0]['message']['content']
            return content.strip()
        else:
            raise ValueError(f"API 返回格式错误: {result}")
    
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"API 请求失败: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"调用 Doubao API 时发生错误: {str(e)}")

