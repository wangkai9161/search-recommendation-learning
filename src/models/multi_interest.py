"""带兴趣多样性约束的教学版多兴趣召回模型。"""

import torch
from torch import nn
from torch.nn import functional as F


class MultiInterestRecall(nn.Module):
    def __init__(self, num_items: int, embedding_dim: int = 64, num_interests: int = 4):
        super().__init__()
        self.num_interests = num_interests
        self.item_embedding = nn.Embedding(num_items, embedding_dim)
        self.interest_queries = nn.Parameter(torch.randn(num_interests, embedding_dim) * 0.02)
        self.projection = nn.Linear(embedding_dim, embedding_dim)
        nn.init.normal_(self.item_embedding.weight, std=0.02)

    def encode_interests(self, histories, mask=None):
        sequence = self.item_embedding(histories)
        if mask is not None:
            sequence = sequence.masked_fill(~mask.unsqueeze(-1), 0.0)
        queries = self.interest_queries.unsqueeze(0).expand(sequence.size(0), -1, -1)
        # 每个兴趣查询从用户行为序列中选择自己关注的行为子集。
        attention = queries @ sequence.transpose(1, 2) / sequence.size(-1) ** 0.5
        if mask is not None:
            attention = attention.masked_fill(~mask.unsqueeze(1), -torch.inf)
        weights = attention.softmax(dim=-1)
        interests = weights @ sequence
        return F.normalize(self.projection(interests), dim=-1)

    def encode_item(self, items):
        return F.normalize(self.item_embedding(items), dim=-1)

    def in_batch_loss(self, histories, positives, mask=None, temperature=0.07):
        interests = self.encode_interests(histories, mask)
        items = self.encode_item(positives)
        # 一个用户的多个兴趣中，只要任一兴趣与候选匹配即可作为用户分数。
        logits = (interests @ items.T).amax(dim=1) / temperature
        labels = torch.arange(logits.size(0), device=logits.device)
        return F.cross_entropy(logits, labels)

    def diversity_loss(self, histories, mask=None):
        interests = self.encode_interests(histories, mask)
        # 除对角线外的兴趣相似度应尽量小，避免多个兴趣向量塌缩为同一个。
        similarity = interests @ interests.transpose(1, 2)
        identity = torch.eye(self.num_interests, device=similarity.device).unsqueeze(0)
        return ((similarity - identity) ** 2).mean()
