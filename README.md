# 搜广推学习项目

这是一个围绕召回模型演进和负采样的实践型学习项目。

## 学习主线

```text
DSSM 双塔
  -> 负采样与对比学习
  -> FM / DeepFM
  -> MIND 多兴趣
  -> MiniBatch K-Means / VQ-VAE
  -> SASRec
  -> Decoder-only Transformer
  -> 生成式召回 + Batch 内负采样
```

## 项目约定

- `data/` 只存数据，不提交原始大文件。
- `src/` 存放可复用的模型、损失函数和评估代码。
- `experiments/` 记录每次实验的配置、结果和结论。
- 每个阶段都尽量使用同一份数据和同一套指标，避免只比较 AUC。

## 开始学习

1. 阅读 [`docs/ROADMAP.md`](docs/ROADMAP.md)。
2. 从 `01_dssm` 开始实现基线。
3. 使用 [`experiments/experiment_template.md`](experiments/experiment_template.md) 记录实验。
4. 每个阶段完成后更新 `docs/notes/` 和实验结果。

## 项目导航

- [`docs/PROJECT_STRUCTURE.md`](docs/PROJECT_STRUCTURE.md)：目录边界和阶段入口
- [`experiments/README.md`](experiments/README.md)：实验索引
- [`scripts/README.md`](scripts/README.md)：训练脚本说明
- [`docs/ROADMAP.md`](docs/ROADMAP.md)：路线完成状态

## 第一阶段：运行 DSSM 基线

安装依赖后，在项目根目录运行：

```powershell
conda run -n py310 python -m pip install -r requirements.txt --index-url https://pypi.tuna.tsinghua.edu.cn/simple
conda run -n py310 python scripts/train_dssm.py --epochs 2 --max-users 1000
```

完整 MovieLens 1M 数据可以去掉 `--max-users 1000`；第一次建议保留该参数验证流程。


## 推荐统一指标

`AUC`、`Recall@K`、`HitRate@K`、`NDCG@K`、Item 覆盖率、重复候选率、候选有效率。
