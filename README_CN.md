# ComfyUI Smart Caption - 智能配文节点

🎨 基于 Doubao 大模型的智能图片分类和配文生成系统

[![GitHub](https://img.shields.io/badge/GitHub-comfyui--smart--caption-blue)](https://github.com/JJfan0508/comfyui-smart-caption)

## 📖 项目简介

ComfyUI Smart Caption 是一个强大的 ComfyUI 自定义节点，提供：
- 🎯 **智能图片分类**：自动识别图片类型（日常plog、人像自拍、宠物、美食等）
- ✍️ **智能配文生成**：根据图片类型自动选择合适的配文风格
- 🔧 **PE在线配置**：所有分类规则和配文模板都可在节点上直接编辑
- ⚡ **批量处理**：支持多图并发处理，提高效率
- 🔗 **关联判断**：自动判断多图是否有关联

## ✨ 功能特性

### 支持的分类标签

- 📷 **日常plog**：旅行、生活记录、随拍（环境为主，人物仅为点缀）
- 👤 **人像自拍**：时尚、颜值、亲子、二次元（人物为主体，清晰可见）
- 🐾 **抽象文案**：宠物、动物相关
- 🍔 **图片详细描述**：美食、家居等
- 📝 **文案**：人生感悟、情感表达
- 🎯 **其他**：不属于以上类别

### 核心功能

1. **单图分类**：快速识别单张图片的类型
2. **批量分类**：同时处理多张图片
3. **关联判断**：自动判断多图是否属于同一主题（如旅行组图）
4. **智能配文**：根据图片类型自动选择合适的配文风格

## 📦 安装方法

### 方法1：Git克隆（推荐）

```bash
cd ComfyUI/custom_nodes/
git clone https://github.com/JJfan0508/comfyui-smart-caption.git
cd comfyui-smart-caption
python install.py
```

### 方法2：手动安装

1. 下载本项目
2. 将 `comfyui-smart-caption` 文件夹复制到 `ComfyUI/custom_nodes/`
3. 进入文件夹，运行：
   ```bash
   python install.py
   ```
4. 重启 ComfyUI

### 方法3：ComfyUI Manager

（待发布到官方市场后）
在 ComfyUI Manager 中搜索 "Smart Caption" 直接安装

## 🎨 节点说明

### 节点1：批量图片加载器 📁 (BatchImageLoader)

**功能**：从文件夹批量加载多张图片，支持自动分组

**输入参数**：
- `folder_path` (STRING)：文件夹路径
- `max_images` (INT, 可选)：最大加载图片数（默认100）

**输出**：
- `images` (IMAGE)：图片batch
- `groups` (STRING)：分组信息JSON（自动检测）

**自动分组规则**：
- **有子文件夹**：每个子文件夹作为一组
  ```
  parent/
  ├── group1/  → 第1组
  └── group2/  → 第2组
  ```
- **无子文件夹**：所有图片作为一组

**分组信息格式**：
```json
{
  "total_images": 5,
  "groups": [
    {"name": "group1", "start": 0, "end": 3, "count": 3},
    {"name": "group2", "start": 3, "end": 5, "count": 2}
  ]
}
```

**提示**：单图可以使用ComfyUI自带的Load Image节点

---

### 节点2：多图上传器 🖼️ (MultiImageUploader)

**功能**：从ComfyUI的input文件夹手动选择多张图片上传

**输入参数**：
- `image_pattern` (STRING)：文件匹配模式（如 `*.jpg` 或 `photo_*.png`）
- `start_index` (INT)：起始索引（默认0）
- `max_images` (INT)：最大加载数量（默认10）

**输出**：
- `images` (IMAGE)：图片batch

**使用方法**：
1. 先把图片上传到ComfyUI的 `input` 文件夹
2. 在节点中设置匹配模式（如 `*.jpg` 匹配所有jpg图片）
3. 设置起始索引和数量
4. 加载选中的图片

**使用场景**：
- 手动挑选几张图片进行处理
- 灵活控制加载哪些图片
- 不需要分组功能（所有图片作为一组）

**与BatchImageLoader的区别**：
- BatchImageLoader：自动化，文件夹路径，自动分组
- MultiImageUploader：手动化，input文件夹，文件模式匹配

---

### 节点3：图片分类器 📷 (ImageClassifier)

**功能**：对输入的图片进行分类，输出分类标签

**输入参数**：
- `image` (IMAGE)：输入图片（支持单图或批量）
- `classification_pe` (STRING)：分类规则PE（可编辑）
- `api_key` (STRING)：Doubao API密钥
- `api_url` (STRING)：API地址
- `model` (STRING)：模型名称
- `text_requirement` (STRING, 可选)：文本需求
- `mode` (COMBO)：single/multi/auto（自动判断）
- `groups` (STRING, 可选)：分组信息（从BatchImageLoader传入）

**分组处理**：
- **有groups且多组**：分别对每组进行关联判断
- **无groups或单组**：所有图片作为一个整体判断

**输出**：
- `classifications` (STRING)：分类结果JSON
- `image` (IMAGE)：原图透传

**输出JSON格式**：
```json
// 单图或多图有关联
{"style_tag": "日常plog"}
{"style_tag": "日常plog_multi_pic"}

// 多图无关联
{"style_tags": ["人像自拍", "日常plog", "抽象文案"]}
```

---

### 节点4：智能配文生成器 ✍️ (SmartCaptionGenerator)

**功能**：根据分类结果，使用对应的PE生成配文

**输入参数**：
- `image` (IMAGE)：输入图片
- `classifications` (STRING)：分类结果（从ImageClassifier）
- `日常plog_单图_pe` (STRING)：日常plog单图配文PE
- `日常plog_多图_pe` (STRING)：日常plog多图配文PE
- `人像自拍_单图_pe` (STRING)：人像自拍单图配文PE
- `人像自拍_多图_pe` (STRING)：人像自拍多图配文PE
- `抽象文案_单图_pe` (STRING)：抽象文案单图配文PE
- `抽象文案_多图_pe` (STRING)：抽象文案多图配文PE
- `图片详细描述_单图_pe` (STRING)：图片详细描述单图配文PE
- `图片详细描述_多图_pe` (STRING)：图片详细描述多图配文PE
- `其他_单图_pe` (STRING)：其他单图配文PE
- `其他_多图_pe` (STRING)：其他多图配文PE
- `api_key` (STRING)：Doubao API密钥
- `api_url` (STRING)：API地址
- `model` (STRING)：模型名称
- `text_requirement` (STRING, 可选)：额外的文本需求

**自动PE选择**：
- 标签包含 `_multi_pic` → 自动使用多图PE
- 标签不包含 `_multi_pic` → 自动使用单图PE

**单图/多图PE的区别**：
- **单图PE**：描述单个画面，10-20字
- **多图PE**：概括整组主题，15-25字

**输出**：
- `captions` (STRING)：配文结果JSON
- `image` (IMAGE)：原图透传

**输出JSON格式**：
```json
{
  "captions": ["今日穿搭分享～", "记录美好生活", "毛孩子太可爱了"]
}
```

## 💡 使用示例

### 工作流1：单图分类+配文

```
[Load Image]（ComfyUI自带）
     ↓ IMAGE
[ImageClassifier]
  配置：
  - classification_pe: (使用默认或自定义)
  - api_key: your_api_key
     ↓ classifications (STRING)
     ↓ IMAGE
[SmartCaptionGenerator]
  配置：
  - 日常plog_pe: "生成轻松随性的配文"
  - 人像自拍_pe: "生成时尚个性的配文"
  - ...
     ↓ captions (STRING)
[Display Text] / [Save Text]
```

### 工作流2：批量图片处理 - 自动分组（推荐✨）

```
[BatchImageLoader]
  输入：folder_path: "D:/photos/"
  文件夹结构：
    photos/
    ├── trip1/   (3张旅行照)
    └── trip2/   (2张旅行照)
     ↓ IMAGE (batch: 5张)
     ↓ groups (JSON: 2个分组)
[ImageClassifier]
  输入：groups连接到BatchImageLoader的groups输出
  mode: multi
  处理：
    - group1(3张) → 判断关联 → "日常plog_multi_pic"
    - group2(2张) → 判断关联 → "日常plog_multi_pic"
     ↓ classifications: {"style_tags": ["日常plog_multi_pic", "日常plog_multi_pic", "日常plog_multi_pic", "日常plog_multi_pic", "日常plog_multi_pic"]}
     ↓ IMAGE
[SmartCaptionGenerator]
     ↓ captions: {"captions": ["配文1", "配文2", ...]}
[Display Text] / [Save Text]
```

**关键点**：
- 将BatchImageLoader的 `groups` 输出连接到ImageClassifier的 `groups` 输入
- ImageClassifier会自动识别分组，分别判断每组的关联性
- SmartCaptionGenerator自动使用多图PE生成配文（因为标签是 `_multi_pic`）

**PE自动选择示例**：
```
分类结果: {"style_tags": ["日常plog_multi_pic", "人像自拍"]}

配文生成:
- 图1: "日常plog_multi_pic" → 使用"日常plog_多图_pe" → "周末旅行vlog｜记录美好时光"
- 图2: "人像自拍" → 使用"人像自拍_单图_pe" → "今日穿搭分享～✨"
```

### 工作流3：手动选择多图处理

```
[MultiImageUploader]
  输入：
  - image_pattern: "vacation_*.jpg"
  - start_index: 0
  - max_images: 5
  （从input文件夹加载vacation_0.jpg到vacation_4.jpg）
     ↓ IMAGE (batch: 5张，作为一组)
[ImageClassifier]
  mode: multi
  （5张图作为一个整体判断关联）
     ↓ classifications
     ↓ IMAGE
[SmartCaptionGenerator]
     ↓ captions
[Display/Save]
```

**适用场景**：
- 手动挑选几张特定图片
- 不需要自动分组
- 快速测试和调试

---

### 工作流4：完整自动化流程（推荐）

```
[BatchImageLoader] → 自动加载+分组
     ↓
[ImageClassifier] → 按组分别分类
     ↓
[SmartCaptionGenerator] → 自动选择PE生成配文
     ↓
[Save Text] → 保存配文结果
```

### 高级工作流：条件处理

你可以使用其他节点解析JSON，根据分类结果进行条件处理：

```
[ImageClassifier]
     ↓ classifications
[JSON Parser]
     ↓ style_tag
[Switch/Router] → 根据标签走不同流程
```

## 🔧 配置说明

### API配置

**Doubao API密钥获取**：
1. 访问火山引擎控制台
2. 创建应用获取API Key
3. 在节点的 `api_key` 参数中填入

**默认配置**：
- API URL: `https://ark.cn-beijing.volces.com/api/v3/chat/completions`
- Model: `doubao-seed-1-6-250615`
- Temperature: 0（确定性输出）

### PE配置

#### 分类PE（classification_pe）

定义图片分类的规则，默认支持：
- 文案识别
- 风格配文识别
- 图片特征判断

**可以根据需求修改**：
- 添加新的分类标签
- 调整判断规则
- 修改示例

#### 配文PE（各个_pe参数）

为每种分类定义配文生成的规则：

**示例**：
```
日常plog_pe:
请为这张日常生活照片生成一段简短的配文，风格轻松随性，记录生活的美好瞬间。
配文要求：10-20字，贴合图片内容，自然真实。

人像自拍_pe:
请为这张人像照片生成一段简短的配文，风格时尚个性，展现个人魅力和气质。
配文要求：10-20字，贴合图片风格。
```

**提示**：
- 可以在PE中指定配文长度、风格、语气等
- 支持中文和英文
- 建议保持PE简洁明确

## 📊 输出格式说明

### 分类结果JSON（classifications）

```json
// 情况1：单图
{"style_tag": "人像自拍"}

// 情况2：单图 - 文案类
{"style_tag": "文案", "text": "岁月静好，现世安稳"}

// 情况3：多图有关联
{"style_tag": "日常plog_multi_pic"}

// 情况4：多图无关联
{"style_tags": ["人像自拍", "日常plog", "抽象文案"]}
```

### 配文结果JSON（captions）

```json
{
  "captions": [
    "今日穿搭分享～✨",
    "记录美好生活的每一刻",
    "我家毛孩子太可爱了🐱"
  ]
}
```

## 🚀 性能优化

- ⚡ **并发处理**：多图分类和配文生成使用线程池并发执行
- 🎯 **确定性输出**：temperature=0，确保同一图片每次结果一致
- 💾 **内存优化**：使用PIL Image处理，避免大量内存占用

## ❓ 常见问题

### Q1: 节点加载失败？

**A**: 检查以下几点：
1. 是否运行了 `python install.py` 安装依赖？
2. ComfyUI是否重启？
3. 查看ComfyUI终端是否有错误信息

### Q2: API调用失败？

**A**: 请检查：
1. API Key是否正确
2. 网络是否正常
3. API URL和模型名称是否正确

### Q3: 分类结果不准确？

**A**: 可以：
1. 修改 `classification_pe` 调整分类规则
2. 添加更多示例到PE中
3. 调整关键词和判断条件

### Q4: 配文不满意？

**A**: 可以：
1. 修改对应分类的配文PE
2. 指定配文长度、风格、语气
3. 在 `text_requirement` 中提供额外要求

### Q5: 多图判断不准？

**A**: 关联判断阈值默认50%，可以在代码中调整：
- 修改 `core/multi_pic.py` 的 `threshold` 参数
- 提高阈值（如0.6, 0.7）可以更严格判断

## 🔗 相关链接

- 📂 **GitHub仓库**: https://github.com/JJfan0508/comfyui-smart-caption
- 📧 **问题反馈**: guangyuniu8023@gmail.com
- 💬 **ComfyUI社区**: [ComfyUI官方](https://github.com/comfyanonymous/ComfyUI)

## 📝 更新日志

### v1.0.0 (2025-11-09)
- ✨ 初始发布
- 🎯 实现图片分类节点
- ✍️ 实现配文生成节点
- 🔧 支持PE在线配置
- ⚡ 支持批量并发处理

## 📄 许可证

MIT License

## 👏 致谢

- Doubao AI团队提供的强大LLM能力
- ComfyUI社区的支持

---

**Enjoy! 🎉**

如果觉得有用，欢迎⭐Star支持！

