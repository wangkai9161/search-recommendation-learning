# 源码结构

- `models/`：DSSM、FM、MIND、SASRec、Transformer 等模型
- `losses/`：点式、Pairwise、Softmax、In-batch 对比损失
- `data/`：序列构造、样本生成、负采样
- `evaluation/`：AUC、Recall@K、NDCG、覆盖率等指标
- `utils/`：配置、随机种子、日志和通用工具

训练入口不放在 `src/`，统一位于项目根目录的 `scripts/`。模型和评估模块应保持可被多个实验脚本复用。
