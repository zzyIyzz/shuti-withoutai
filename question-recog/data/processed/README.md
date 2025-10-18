# 处理后数据目录

存放特征提取后的训练数据，用于模型训练和评估。

## 数据格式

JSONL格式，每行一个样本：
```json
{
  "source_id": "file://path/to/file.xlsx#q1",
  "features": {
    "has_options": 1,
    "num_options": 4,
    "answer_is_single_letter": 1,
    "question_len": 25,
    "layout_score": 0.85,
    ...
  },
  "label": "single_choice",
  "question_text": "题目内容摘要..."
}
```

## 数据分割

- `train.feat.jsonl`: 训练集 (70%)
- `val.feat.jsonl`: 验证集 (15%) 
- `test.feat.jsonl`: 测试集 (15%)

## 生成方式

```bash
python -m src.app build-dataset --input data/interim --labels data/labels/train.jsonl --output data/processed/train.feat.jsonl
```
