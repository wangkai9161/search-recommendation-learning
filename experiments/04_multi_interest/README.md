# 04 MIND / 多兴趣召回

## 实现

本实验使用 4 个可学习兴趣查询，对用户历史进行注意力聚合，并加入兴趣多样性辅助 Loss。它用于理解 MIND 的核心思想：一个用户由多个兴趣向量表示；不是论文中完整的 Capsule Routing 复现。

## 运行

```powershell
C:\Users\wangx\miniconda3\Scripts\conda.exe run -n py310 python scripts/train_multi_interest.py --epochs 1 --max-users 300 --batch-size 512 --num-interests 4
```

## 结果

配置：300 用户、43,145 个训练样本、3,706 个物品、4 个兴趣、1 Epoch、CPU。

| Recall@10 | Recall@50 | NDCG@10 | NDCG@50 | Item Coverage@50 |
|---:|---:|---:|---:|---:|
| 0.0000 | 0.0033 | 0.0000 | 0.0006 | 0.0165 |

单 Epoch 结果较弱，不能说明多兴趣结构无效。下一步应增加训练轮数，比较兴趣数量和辅助 Loss 权重，并检查兴趣向量是否发生塌缩。

