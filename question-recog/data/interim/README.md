# 中间数据目录

存放解析后的JSON格式数据，作为特征提取的输入。

## 数据格式

每个JSON文件包含：
```json
{
  "source": "原始文件路径",
  "questions": [
    {
      "question": "题干内容",
      "options": ["选项A", "选项B", "选项C", "选项D"],
      "answer_raw": "D",
      "explanation_raw": "解析内容",
      "layout_score": 0.85,
      "parse_flags": {
        "merged_lines": false,
        "tail_answer_stripped": true
      }
    }
  ]
}
```

## 生成方式

```bash
python -m src.app parse --input data/raw --output data/interim
```
