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

**Function**: Load multiple images from ComfyUI's input folder

**Inputs**:
- `image_pattern` (STRING): File matching pattern (e.g., `*.jpg` or `photo_*.png`)
- `start_index` (INT): Starting index (default: 0)
- `max_images` (INT): Maximum number to load (default: 10)

**Outputs**:
- `images` (IMAGE): Image batch

**How to use**:
1. Upload images to ComfyUI's `input` folder
2. Set file pattern (e.g., `*.jpg` for all JPG files)
3. Set start index and max count
4. Load selected images

**Use cases**:
- Manually pick specific images
- Flexible control over which images to load
- No grouping (all images as one set)

**Difference from BatchImageLoader**:
- BatchImageLoader: Automated, folder path, auto-grouping
- MultiImageUploader: Manual, input folder, pattern matching

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
- `classifications` (STRING): From ImageClassifier
- `日常plog_单图_pe` (STRING): PE for single daily plog image
- `日常plog_多图_pe` (STRING): PE for multiple daily plog images
- `人像自拍_单图_pe` (STRING): PE for single portrait image
- `人像自拍_多图_pe` (STRING): PE for multiple portrait images
- `抽象文案_单图_pe` (STRING): PE for single abstract caption
- `抽象文案_多图_pe` (STRING): PE for multiple abstract captions
- `图片详细描述_单图_pe` (STRING): PE for single detailed description
- `图片详细描述_多图_pe` (STRING): PE for multiple detailed descriptions
- `其他_单图_pe` (STRING): PE for single other category
- `其他_多图_pe` (STRING): PE for multiple other category
- `api_key` (STRING): Doubao API key
- `api_url` (STRING): API endpoint
- `model` (STRING): Model name
- `text_requirement` (STRING, optional): Additional requirement

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

