# 搜广推召回与生成式推荐实践

面向 **搜索 / 广告 / 推荐算法实习面试** 的可复现实验项目。项目从 DSSM 双塔召回出发，逐步实现负采样对照、FM/DeepFM、多兴趣召回、离散表示、Decoder-only 生成式召回，并补充 Criteo Attribution CVR 基线，重点验证：

- 负采样策略如何影响 Top-K 召回和候选覆盖。
- 单兴趣用户向量为什么容易压缩用户兴趣，以及多兴趣 Router 如何缓解候选塌缩。
- 一个召回项目如何向广告粗排 / CTR-CVR 预估链路迁移。

> 面试官阅读建议：先看本 README 的结果、复现和项目边界，再看 [`experiments/README.md`](experiments/README.md) 的实验索引，最后进入 [`src/`](src/README.md) 和 [`scripts/`](scripts/README.md) 查看实现。

## 简历与仓库对应关系

简历中的相关内容分布在三个独立仓库。下面的状态以面试官当前能够打开的公开仓库为准；标记为“待上传”的内容暂不应描述为本仓库已经完成。

| 简历内容 | 对应仓库 | 当前状态 |
| --- | --- | --- |
| MovieLens-1M DSSM、Batch 内/随机负采样、FM/DeepFM、多兴趣和生成式召回 | 本仓库 | 已上传 |
| LastFM 用户--艺术家双塔、负样本 0~5、BCE/BPR 和长尾权重 | 本仓库 | 待上传：当前仓库暂不包含对应数据处理、训练脚本和实验结果 |
| MovieLens Two-Tower、GRU4Rec、SASRec、Popularity baseline | [`movielens-recommendation`](https://github.com/wangkai9161/movielens-recommendation) | 已上传至独立仓库，本仓库不重复放置 |
| Criteo Sponsored Search 约 1,600 万条点击日志、LR/FM/Wide&Deep/DeepFM CVR | [`search-ads-cvr`](https://github.com/wangkai9161/search-ads-cvr) | 已上传至独立仓库，本仓库不重复放置 |
| Criteo Attribution CVR toy 基线 | 本仓库 | 待上传：当前本地有扩展代码，公开仓库以本 README 状态为准 |

详细状态记录见 [`docs/UPLOAD_STATUS.md`](docs/UPLOAD_STATUS.md)。

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

Criteo Attribution 日志
  -> post-click CVR / impression-level CVR 样本
  -> Logistic Regression / DeepFM CVR 基线
  -> LogLoss / AUC 评估
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

这个仓库当前完成的是 **召回、行为序列建模、负采样、离线评估和公开广告转化数据上的 CVR 最小链路**，不是完整广告 CVR 生产系统。它对搜索广告 CVR 岗位的价值在于：

- 候选召回和粗排前置建模：DSSM、多兴趣召回、Top-K 检索、候选覆盖分析。
- 用户行为序列表征：从历史行为构造下一物品预测样本，可迁移到用户-查询-广告上下文。
- 特征交互基础：FM/DeepFM 为 CTR/CVR 稀疏特征交叉做铺垫。
- CVR 预估入口：Criteo Attribution 数据读取、点击后 CVR 样本过滤、LogLoss/AUC 二分类评估。
- 离线评估意识：区分 Recall/NDCG/覆盖率，避免只看单一指标。

如果继续扩展为更完整的广告 CTR/CVR 项目，下一步会补充：

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

运行 Criteo Attribution CVR toy smoke test：

```bash
python scripts/make_criteo_attribution_toy.py --rows 5000
python scripts/train_cvr_attribution.py --data-path data/raw/criteo-attribution --max-rows 5000 --epochs 1 --model deepfm
```

## 仓库结构

```text
data/          原始与处理后数据
configs/       实验配置说明
docs/          项目结构、学习路线和边界说明
experiments/   分阶段实验记录和结果
model/         模型注册与入口
notebooks/     探索性笔记
output/        训练后模型文件和可视化产物
prepare/       数据读取、清洗、归一化
result/        指标、训练历史和可视化数据
scripts/       训练与实验入口
train/         训练入口与模型选择
src/data/      MovieLens、MIND、Criteo Attribution 数据读取
src/evaluation/Recall、NDCG、Item Coverage、LogLoss、AUC
src/models/    DSSM、FM、DeepFM、多兴趣、生成式、离散化、CVR 模型
tests/         基础测试
```

## 新的相对路径骨架

如果你想把项目按“读数 -> 预处理 -> 训练 -> 输出”组织，新的默认链路是：

```text
data/      原始数据和处理后数据
prepare/   读取、归一化、特征处理
model/     模型注册
train/     训练入口
output/    模型文件和可视化产物
result/    训练结果、指标和可视化数据
```

所有脚本都通过 `project_paths.py` 统一定位根目录，尽量避免写死绝对路径。

## 已完成与边界

已完成：

- MovieLens-1M 行为序列和下一物品预测样本。
- DSSM、负采样对照、FM/DeepFM、多兴趣召回、离散表示和生成式召回最小链路。
- Full-catalog Top-K 检索、历史物品过滤、Recall/NDCG/Item Coverage 评估。
- Criteo Attribution CVR 的扩展代码当前标记为待上传；已公开的完整 Criteo Sponsored Search CVR 实验位于 [`search-ads-cvr`](https://github.com/wangkai9161/search-ads-cvr)。

当前边界：

- 不是工业推荐/广告线上系统。
- 未声称完成真实 MIND 全量曝光日志训练。
- 未包含工业搜索广告全链路、延迟反馈校正、校准或线上 A/B 验证。
- 当前结果仍需要更多随机种子和更大训练规模验证。
