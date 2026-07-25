# 实验汇总

## 统一评估

- `Recall@K`：目标物品是否进入候选集。
- `NDCG@K`：目标物品在候选集中的位置质量。
- `Item Coverage@K`：所有用户候选覆盖的物品比例。
- 生成式召回额外记录候选唯一率和长尾比例。

## 负采样对照

| 策略 | Recall@10 | Recall@50 | NDCG@10 | Coverage@50 |
|---|---:|---:|---:|---:|
| Batch 内负采样 | 0.0370 | 0.1420 | 0.0169 | 0.7275 |
| 随机 10 个负样本 | 0.0350 | 0.1360 | 0.0184 | 0.1811 |

配置和完整讨论见 [`../experiments/02_negative_sampling/README.md`](../experiments/02_negative_sampling/README.md)。

## 其他模型

FM、DeepFM、多兴趣和生成式实验结果分别见 [`../experiments/03_fm/README.md`](../experiments/03_fm/README.md)、[`../experiments/04_multi_interest/README.md`](../experiments/04_multi_interest/README.md) 和 [`../experiments/06_generative_recall/README.md`](../experiments/06_generative_recall/README.md)。

