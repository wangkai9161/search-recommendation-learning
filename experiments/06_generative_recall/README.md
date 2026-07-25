# 06 生成式召回

## 实现

本实验使用带因果 Mask 的 Transformer 做下一物品预测。模型读取用户历史序列，输出最后一个有效位置的隐藏向量，再预测整个物品词表；这是 Decoder-only 生成式召回的最小教学版本。

## 运行

```powershell
C:\Users\wangx\miniconda3\Scripts\conda.exe run -n py310 python scripts/train_generative.py --epochs 1 --max-users 300 --batch-size 256 --embedding-dim 64
```

## 结果

配置：300 用户、43,145 个训练样本、3,706 个物品、1 Epoch、CPU。

| Loss | Recall@10 | Recall@50 | Coverage@50 | Unique Ratio | Tail Ratio |
|---:|---:|---:|---:|---:|---:|
| 7.8102 | 0.0167 | 0.1000 | 0.1751 | 0.0433 | 0.0000 |

后续需要增加生成候选去重、Coverage、长尾占比和与 DSSM 的统一评估；当前结果只验证了自回归训练链路。

## 补充指标

`train_generative.py` 额外输出：

- `item_coverage@50`：所有用户 Top-50 候选覆盖的物品比例
- `candidate_unique_ratio`：跨用户候选去重后的比例
- `tail_ratio`：候选中低于测试集物品频次中位数的物品比例
