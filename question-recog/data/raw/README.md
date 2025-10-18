# 原始数据目录

将原始题库文件放在此目录下：
- Excel文件 (*.xlsx)
- Word文件 (*.docx) 
- PDF文件 (*.pdf)
- 图片文件 (*.png, *.jpg, *.jpeg)

## 示例文件结构

```
raw/
├── 电力安全题库.xlsx
├── 继电保护试题.docx
├── 变电运行题库.pdf
└── 手写题目图片.jpg
```

## 使用方法

```bash
# 解析原始文件
python -m src.app parse --input data/raw --output data/interim --use-ocr false
```
