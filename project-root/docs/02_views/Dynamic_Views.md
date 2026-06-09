# Dynamic_Views

## 1. View-008: 学习进度上报异步削峰

- **关联 QAS**: QAS-008
- **关联 ADR**: 原文档未单独设置 ADR，本视图依据 QAS-008 和容器图补充运行时说明。

```mermaid
sequenceDiagram
    autonumber
    actor Student as 学生
    participant Web as Web/App 前端
    participant Gateway as API Gateway
    participant Learning as Learning Record Service
    participant MQ as Message Queue
    participant Worker as Progress Aggregation Worker
    participant DB as MySQL
    participant Obs as Observability

    loop 每 10 秒
        Student->>Web: 观看视频产生进度
        Web->>Gateway: POST /learning/progress<br/>userId/courseId/position/eventId
        Gateway->>Learning: 转发上报请求
        Learning->>MQ: 发布 LearningProgressEvent
        Learning-->>Gateway: 202 Accepted
        Gateway-->>Web: 快速返回
    end
    MQ-->>Worker: 批量拉取进度事件
    Worker->>Worker: 按 userId+courseId 窗口聚合<br/>保留最大播放位置和累计时长
    Worker->>DB: 批量 UPSERT 学习进度
    Worker-->>Obs: 上报 MQ lag、聚合延迟、落库耗时
```

### 2.时序说明

学习进度入口服务不直接同步写数据库，而是将事件写入 MQ 后快速返回。后台 Worker 按用户和课程维度做短窗口聚合，再批量落库，从而把高频小写转换成低频批量写。

### 3.质量属性响应分析

- **性能**: 上报 API 可在 100ms 内快速返回。
- **可伸缩性**: MQ 提供削峰能力，Worker 可水平扩容。
- **一致性权衡**: 学习进度存在短暂最终一致延迟，通常控制在 30 秒内。
