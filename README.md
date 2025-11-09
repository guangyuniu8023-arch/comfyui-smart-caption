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

### Node 1: Batch Image Loader 📁

**Function**: Load multiple images from a folder

**Inputs**:
- `folder_path` (STRING): Folder path
- `max_images` (INT, optional): Maximum number of images to load (default: 100)

**Outputs**:
- `images` (IMAGE): Image batch
- `groups` (STRING): Auto-detected group information (JSON)

**Auto-grouping**:
- **With subfolders**: Each subfolder becomes a group
- **Without subfolders**: All images as one group

**Note**: For single image, use ComfyUI's built-in Load Image node

---

### Node 2: Multi Image Uploader 🖼️

**Function**: Connect multiple Load Image nodes and merge into batch

**Inputs**:
- `image_1` (IMAGE): First image (required)
- `image_2` (IMAGE, optional): Second image
- `image_3` (IMAGE, optional): Third image
- ... up to 10 images

**Outputs**:
- `images` (IMAGE): Merged image batch

**How to use**:
```
[Load Image] → image_1
[Load Image] → image_2
[Load Image] → image_3
     ↓ ↓ ↓
[MultiImageUploader] → auto merge
     ↓ images
```

**Features**:
- 📷 **Flexible**: Connect as many Load Image nodes as needed
- 🎯 **Visual**: See each image clearly in workflow
- ✨ **Auto-merge**: Automatically merge all connected images
- 🔢 **1-10 images**: First is required, others optional

**Use cases**:
- Manually pick specific images
- Visual control over each image
- Suitable for small batches (≤10 images)

**Difference from BatchImageLoader**:
- BatchImageLoader: Folder path, auto-grouping, large batches
- MultiImageUploader: Manual connection, visual, small batches

---

### Node 3: Image Classifier 📷

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

### Node 4: Smart Caption Generator ✍️

**Function**: Generate captions based on classification results

**Inputs**:
- `image` (IMAGE): Input image(s)
- `classifications` (STRING): From ImageClassifier (must connect)
- `日常plog_单图_pe` (STRING): PE for single daily plog (must connect)
- `日常plog_多图_pe` (STRING): PE for multiple daily plog (must connect)
- `人像自拍_单图_pe` (STRING): PE for single portrait (must connect)
- `人像自拍_多图_pe` (STRING): PE for multiple portrait (must connect)
- `抽象文案_单图_pe` (STRING): PE for single abstract (must connect)
- `抽象文案_多图_pe` (STRING): PE for multiple abstract (must connect)
- `图片详细描述_单图_pe` (STRING): PE for single description (must connect)
- `图片详细描述_多图_pe` (STRING): PE for multiple description (must connect)
- `其他_单图_pe` (STRING): PE for single other (must connect)
- `其他_多图_pe` (STRING): PE for multiple other (must connect)
- `api_key` (STRING): Doubao API key
- `api_url` (STRING): API endpoint
- `model` (STRING): Model name
- `text_requirement` (STRING, optional): Additional requirement

**PE Input Note**:
- All PE parameters must be connected from other nodes (e.g., Text nodes)
- Use ComfyUI's "Text" or "String Constant" nodes
- Refer to `config/default_captions.json` for default PE templates

**Auto PE Selection**:
- Tag contains `_multi_pic` → Use multi-image PE
- Tag doesn't contain `_multi_pic` → Use single-image PE

**PE Differences**:
- **Single-image PE**: Describe single moment (10-20 chars)
- **Multi-image PE**: Summarize theme of image set (15-25 chars)

**Outputs**:
- `captions` (STRING): Generated captions JSON
- `image` (IMAGE): Original image passthrough

## 💡 Usage Example

### Workflow 1: Single Image

```
[Load Image] (ComfyUI built-in)
     ↓ IMAGE
[Image Classifier]
     ↓ classifications
     ↓ IMAGE
[Smart Caption Generator]
     ↓ captions
[Display Text]
```

### Workflow 2: Batch Processing (Recommended)

```
[Batch Image Loader]
  folder_path: "D:/photos/"
     ↓ IMAGE (batch)
     ↓ groups
[Image Classifier]
  mode: multi
     ↓ classifications
     ↓ IMAGE
[Smart Caption Generator]
     ↓ captions (JSON)
[Display/Save Text]
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

