# ComfyUI Smart Caption

🎨 Intelligent Image Classification and Caption Generation System powered by Doubao LLM

[中文文档](README_CN.md) | [English](README.md)

## 📖 Introduction

ComfyUI Smart Caption is a powerful custom node set for ComfyUI that provides:
- 🎯 **Intelligent Image Classification**: Automatically identify image types (daily life, portrait, pets, food, etc.)
- ✍️ **Smart Caption Generation**: Generate captions based on image classification
- 🔧 **Configurable Prompts**: Edit classification rules and caption templates directly in nodes
- ⚡ **Batch Processing**: Support concurrent processing for multiple images
- 🔗 **Relation Detection**: Automatically detect if multiple images are related

## ✨ Features

### Supported Classification Tags

- 📷 **Daily Plog**: Travel, life records, snapshots (environment-focused)
- 👤 **Portrait Selfie**: Fashion, beauty, family, cosplay (person-focused)
- 🐾 **Abstract Caption**: Pets, animals
- 🍔 **Detailed Description**: Food, home decoration
- 📝 **Text**: Life insights, emotional expressions
- 🎯 **Others**: Other categories

## 📦 Installation

### Method 1: Git Clone (Recommended)

```bash
cd ComfyUI/custom_nodes/
git clone https://github.com/JJfan0508/comfyui-smart-caption.git
cd comfyui-smart-caption
python install.py
```

### Method 2: Manual Installation

1. Download this project
2. Copy `comfyui-smart-caption` folder to `ComfyUI/custom_nodes/`
3. Run `python install.py`
4. Restart ComfyUI

## 🎨 Node Description

### Node 1: Image Classifier 📷

**Function**: Classify input images and output classification tags

**Inputs**:
- `image` (IMAGE): Input image(s)
- `classification_pe` (STRING): Classification rules (editable)
- `api_key` (STRING): Doubao API key
- `api_url` (STRING): API endpoint
- `model` (STRING): Model name
- `text_requirement` (STRING, optional): Text requirement
- `mode` (COMBO): single/multi/auto

**Outputs**:
- `classifications` (STRING): Classification result JSON
- `image` (IMAGE): Original image passthrough

---

### Node 2: Smart Caption Generator ✍️

**Function**: Generate captions based on classification results

**Inputs**:
- `image` (IMAGE): Input image(s)
- `classifications` (STRING): From ImageClassifier
- `日常plog_pe` (STRING): PE for daily plog
- `人像自拍_pe` (STRING): PE for portrait selfie
- `抽象文案_pe` (STRING): PE for abstract caption
- `图片详细描述_pe` (STRING): PE for detailed description
- `其他_pe` (STRING): PE for others
- `api_key` (STRING): Doubao API key
- `api_url` (STRING): API endpoint
- `model` (STRING): Model name
- `text_requirement` (STRING, optional): Additional requirement

**Outputs**:
- `captions` (STRING): Generated captions JSON
- `image` (IMAGE): Original image passthrough

## 💡 Usage Example

### Basic Workflow

```
[Load Image]
     ↓
[Image Classifier]
     ↓ classifications
     ↓ IMAGE
[Smart Caption Generator]
     ↓ captions
[Display Text]
```

### Batch Processing

```
[Load Images (Batch)]
     ↓ IMAGE (batch)
[Image Classifier]
  mode: multi
     ↓ classifications
[Smart Caption Generator]
     ↓ captions (JSON array)
[Save/Display]
```

## 🔧 Configuration

### API Settings

- **API Key**: Get from Volcengine Console
- **API URL**: Default is Doubao endpoint
- **Model**: Default is `doubao-seed-1-6-250615`

### Prompt Engineering

You can customize:
- Classification rules in `classification_pe`
- Caption generation templates for each category
- Output format and style requirements

## 📊 JSON Output Format

### Classifications Output

```json
{"style_tag": "人像自拍"}                           // Single image
{"style_tag": "日常plog_multi_pic"}                // Multi images with relation
{"style_tags": ["人像自拍", "日常plog"]}            // Multi images without relation
```

### Captions Output

```json
{
  "captions": ["Caption 1", "Caption 2", "Caption 3"]
}
```

## ❓ FAQ

**Q: Node loading failed?**
A: Make sure you ran `python install.py` and restarted ComfyUI.

**Q: API call failed?**
A: Check your API key, network connection, and API URL.

**Q: Inaccurate classification?**
A: Modify the `classification_pe` to adjust classification rules.

**Q: Unsatisfied with captions?**
A: Customize the PE for each category to match your needs.

## 📄 License

MIT License

## 🙏 Credits

- Doubao AI Team for the powerful LLM
- ComfyUI Community

---

**Star ⭐ this repo if you find it useful!**

