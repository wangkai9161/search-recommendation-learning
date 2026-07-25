# 搜广推召回与生成式推荐实践

一个从双塔召回出发，逐步实现负采样、FM/DeepFM、多兴趣、离散化和生成式推荐的实践项目。项目重点研究：**负采样策略如何影响 Top-K 召回、候选覆盖和生成结果质量**。

## 项目亮点

- 从 DSSM 双塔基线开始，统一比较随机负采样和 Batch 内负采样。
- 使用 `Recall@10/50`、`NDCG@10/50`、`Item Coverage` 等召回指标，避免只看 AUC。
- 实现 FM、DeepFM、多兴趣召回和 Decoder-only 下一物品预测教学版本。
- 增加 MiniBatch K-Means / VQ 风格 Item Code 实验。
- 所有实验使用 MovieLens 1M，训练入口可由 `py310` 环境直接运行。

## 模型路线

```text
DSSM 双塔
  -> 随机负采样 / Batch 内负采样
  -> FM / DeepFM
  -> 多兴趣召回
  -> MiniBatch K-Means / VQ 离散化
  -> Decoder-only 生成式召回
```

## 核心结果

主对照实验使用 MovieLens 1M 的前 1,000 个用户、2 个 Epoch；FM、多兴趣和生成式实验为教学规模验证，不能直接横向比较。

| 实验 | Recall@10 | Recall@50 | NDCG@10 | Item Coverage@50 |
|---|---:|---:|---:|---:|
| DSSM + Batch 内负采样 | 0.0370 | 0.1420 | 0.0169 | 0.7275 |
| DSSM + 随机 10 个负样本 | 0.0350 | 0.1360 | 0.0184 | 0.1811 |
| FM 风格召回 | 0.0100 | 0.0667 | 0.0075 | 0.5880 |
| DeepFM 风格召回 | 0.0200 | 0.1267 | 0.0080 | 0.4900 |
| 多兴趣召回，4 兴趣 | 0.0000 | 0.0033 | 0.0000 | 0.0165 |
| Decoder-only 生成式召回 | 0.0167 | 0.1000 | - | 0.1751 |

初步观察：Batch 内负采样与随机负采样的 Top-K 命中接近，但候选覆盖差异明显。Loss 数值不能跨 Loss 定义直接比较；多兴趣和生成式模型还需要更长训练及多随机种子验证。

## 快速开始

项目使用 Python `3.10.20` 和 CPU 版 PyTorch。依赖安装：

```powershell
$conda = 'C:\Users\wangx\miniconda3\Scripts\conda.exe'
& $conda run -n py310 python -m pip install -r requirements.txt --index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

运行 DSSM 基线：

```powershell
& $conda run -n py310 python scripts/train_dssm.py --epochs 2 --max-users 1000 --negative-mode in_batch
```

运行负采样对照：

```powershell
& $conda run -n py310 python scripts/train_dssm.py --epochs 2 --max-users 1000 --negative-mode random --num-negatives 10
```

## 项目结构

```text
data/          原始数据和处理后数据
src/data/      MovieLens、MIND 数据读取
src/models/    DSSM、FM、DeepFM、多兴趣、生成式、离散化模型
src/evaluation/统一召回指标
scripts/       训练和实验入口
experiments/   按阶段保存配置、结果和结论
docs/          学习路线、项目结构和数据说明
```

详细目录边界见 [`docs/PROJECT_STRUCTURE.md`](docs/PROJECT_STRUCTURE.md)，实验索引见 [`experiments/README.md`](experiments/README.md)。

## 数据与复现

项目使用 MovieLens 1M。原始数据不提交到仓库，下载和格式说明见 [`data/raw/README.md`](data/raw/README.md)。MIND 解析器已提供，但真实 MIND 数据训练尚未在本仓库中声称完成。

## 项目边界

这是一个面向学习和面试展示的可运行实验项目，不是工业推荐系统。当前仍待补充：完整 MIND 曝光日志实验、3 个随机种子统计、离散 Item Code 接入生成式模型，以及线上下发指标验证。

