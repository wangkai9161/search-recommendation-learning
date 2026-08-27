# 搜广推召回与生成式推荐实践

面向 **搜索 / 广告 / 推荐算法实习面试** 的可复现实验项目。项目从 DSSM 双塔召回出发，逐步实现负采样对照、FM/DeepFM、多兴趣召回、离散表示和 Decoder-only 生成式召回，重点验证：

- 负采样策略如何影响 Top-K 召回和候选覆盖。
- 单兴趣用户向量为什么容易压缩用户兴趣，以及多兴趣 Router 如何缓解候选塌缩。
- 一个召回项目如何向广告粗排 / CTR-CVR 预估链路迁移。

> 面试官阅读建议：先看本 README 的结果、复现和项目边界，再看 [`experiments/README.md`](experiments/README.md) 的实验索引，最后进入 [`src/`](src/README.md) 和 [`scripts/`](scripts/README.md) 查看实现。

## 3 分钟快速判断

| 你可能关心的问题 | 当前仓库证据 |
| --- | --- |
| 是否只是写了 README？ | `src/models/` 有 DSSM、FM、DeepFM、多兴趣、离散化和生成式模型实现；`scripts/` 有训练入口。 |
| 是否有可比实验？ | `experiments/` 按阶段记录 DSSM、负采样、FM/DeepFM、多兴趣和生成式召回结果。 |
| 是否只看 AUC？ | 统一使用 `Recall@10/50`、`NDCG@10/50`、`Item Coverage@50`，更贴近召回阶段。 |
| 是否夸大成工业广告系统？ | 没有。当前使用 MovieLens-1M，定位为可复现离线实验；广告 CVR 扩展路径在下方单独说明。 |

## 项目路线

```text
MovieLens-1M 行为序列
  -> DSSM 双塔召回基线
  -> 随机负采样 / Batch 内负采样对照
  -> FM / DeepFM 特征交互实验
  -> 多兴趣 Router 召回
  -> MiniBatch K-Means / VQ 风格离散表示
  -> Decoder-only 下一物品生成式召回
```

## 核心结果

### 公平对比：300 用户、2 Epoch

| 实验 | Recall@10 | Recall@50 | NDCG@10 | Item Coverage@50 |
| --- | ---: | ---: | ---: | ---: |
| DSSM + Batch 内负采样 | 0.0067 | 0.0467 | 0.0019 | 0.1349 |
| 多兴趣 Router，4 兴趣 | 0.0300 | 0.0967 | 0.0145 | 0.3546 |

结论：在相同训练规模下，多兴趣 Router 相比单向量 DSSM 明显提升 Top-K 命中和候选覆盖。这个结果用于说明用户行为序列中存在多兴趣表达需求，而不是声称已经达到工业线上指标。

### 其他教学规模结果

FM、DeepFM 使用 300 用户、2 Epoch；负采样主对照使用 1,000 用户、2 Epoch；Decoder-only 使用 100 用户、32 维、1 Epoch。不同规模结果不直接横向比较。

| 实验 | Recall@10 | Recall@50 | NDCG@10 | Item Coverage@50 |
| --- | ---: | ---: | ---: | ---: |
| DSSM + Batch 内负采样 | 0.0370 | 0.1420 | 0.0169 | 0.7275 |
| DSSM + 随机 10 负样本 | 0.0350 | 0.1360 | 0.0184 | 0.1811 |
| FM 风格召回 | 0.0200 | 0.0767 | 0.0117 | 0.6384 |
| DeepFM 风格召回 | 0.0200 | 0.1100 | 0.0067 | 0.5046 |
| Decoder-only 生成式召回 | 0.0300 | 0.0700 | - | 0.1819 |

观察：Batch 内负采样与随机负采样的 Recall@50 接近，但 Item Coverage@50 差异明显，说明采样方式不仅影响命中率，也影响候选分布和覆盖面。

## 和搜索广告 CVR 的关系

这个仓库当前完成的是 **召回、行为序列建模、负采样和离线评估**，不是完整广告 CVR 生产系统。它对搜索广告 CVR 岗位的价值在于：

- 候选召回和粗排前置建模：DSSM、多兴趣召回、Top-K 检索、候选覆盖分析。
- 用户行为序列表征：从历史行为构造下一物品预测样本，可迁移到用户-查询-广告上下文。
- 特征交互基础：FM/DeepFM 为 CTR/CVR 稀疏特征交叉做铺垫。
- 离线评估意识：区分 Recall/NDCG/覆盖率，避免只看单一指标。

如果扩展为广告 CTR/CVR 项目，下一步会补充：

1. 曝光-点击-转化样本构造，区分 `CTR = P(click | impression)`、`CVR = P(conversion | click)`、`CTCVR = P(click, conversion | impression)`。
2. 用户、query、ad、context、time 等稀疏/稠密特征。
3. Wide&Deep、DeepFM、DCN、ESMM/MMoE 等 CTR/CVR 基线。
4. 延迟转化、负采样校正、校准和线上/离线指标偏差分析。

## 快速复现

建议 Python 3.10。原始 MovieLens-1M 数据不提交到仓库，下载和放置方式见 [`data/raw/README.md`](data/raw/README.md)。

```bash
pip install -r requirements.txt
```

运行 DSSM Batch 内负采样：

```bash
python scripts/train_dssm.py --epochs 2 --max-users 1000 --negative-mode in_batch
```

运行随机负采样对照：

```bash
python scripts/train_dssm.py --epochs 2 --max-users 1000 --negative-mode random --num-negatives 10
```

运行多兴趣召回：

```bash
python scripts/train_multi_interest.py --epochs 2 --max-users 300 --num-interests 4
```

## 仓库结构

```text
data/          数据说明与原始数据占位
configs/       实验配置说明
docs/          项目结构、学习路线和边界说明
experiments/   分阶段实验记录和结果
notebooks/     探索性笔记
scripts/       训练与实验入口
src/data/      MovieLens、MIND 数据读取
src/evaluation/Recall、NDCG、Item Coverage
src/models/    DSSM、FM、DeepFM、多兴趣、生成式、离散化模型
tests/         基础测试
```

## 已完成与边界

已完成：

- MovieLens-1M 行为序列和下一物品预测样本。
- DSSM、负采样对照、FM/DeepFM、多兴趣召回、离散表示和生成式召回最小链路。
- Full-catalog Top-K 检索、历史物品过滤、Recall/NDCG/Item Coverage 评估。

当前边界：

- 不是工业推荐/广告线上系统。
- 未声称完成真实 MIND 全量曝光日志训练。
- 未包含真实广告 CVR 标签、延迟反馈、校准或线上 A/B 验证。
- 当前结果仍需要更多随机种子和更大训练规模验证。
