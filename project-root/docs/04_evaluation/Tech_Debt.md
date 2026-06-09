# Tech_Debt

| 债务ID | 描述 | 关联ADR | 债务类型 | 影响范围 | 偿还策略 | 优先级 |
|---|---|---|---|---|---|---|
| TD-001 | 支付链路从强一致改为最终一致后，需要完善消息可靠投递、死信队列、对账补偿和前端“权益确认中”提示。 | ADR-001a | 一致性债务/运维债务 | Order Service、Entitlement Service、Message Queue、前端订单页 | 建立 Outbox 或可靠事件发布机制；补充死信处理页面；对账任务记录补偿结果；前端展示权益处理中状态。 | H |
| TD-002 | Live Access 的权益缓存 TTL 会造成退款或权限变更后的短期一致性窗口。 | ADR-002a | 一致性债务 | Live Access Service、Redis、Entitlement Service | 在退款、撤销权益等操作后主动删除 Redis 和本地缓存；对敏感课程降低 TTL；记录 Token 签发审计。 | H |
| TD-003 | 视频云熔断参数依赖经验值，需要通过真实压测和运行数据持续校准。 | ADR-002a | 可用性债务 | CircuitBreaker、VideoCloudClient、Observability | 建立视频云 Mock 压测；采集超时率、错误率、熔断次数；根据 P95/P99 数据调参。 | H |
| TD-004 | CDN 防盗链依赖源站与边缘节点时间同步，当前只在 ADR 中提出，尚需运维落地。 | ADR-006 | 安全债务/运维债务 | Media Auth Service、CDN、NTP | 配置高可靠 NTP；增加时钟漂移告警；制定密钥轮换流程和回滚方案。 | H |
| TD-005 | `campus_id` 逻辑隔离降低成本，但需要覆盖所有 SQL 路径和批处理路径。 | ADR-005 | 安全债务 | DAO、MySQL、报表任务、管理员接口 | 增加 SQL 审计和跨校区越权自动化测试；禁止绕过 DAO 的原生 SQL；对管理后台增加权限评审。 | H |
| TD-006 | 使用第三方 CDN 和视频云降低自建成本，但平台对外部 SLA 和配置正确性依赖较强。 | ADR-003 | 外部依赖债务 | CDN、第三方视频云、播放器 SDK | 维护备用节点和重连策略；记录 CDN 配置变更；压测节点故障切换。 | M |
| TD-007 | 转码任务异步化后，用户不能立即看到可播放视频，需要完善转码状态反馈。 | ADR-004 | 用户体验债务/一致性债务 | Transcode Worker、Object Storage、前端课程管理页 | 增加转码状态字段；提供轮询 API 或 WebSocket 通知；失败任务展示重试入口。 | M |
| TD-008 | 学习进度异步削峰未单独形成 ADR，当前只在视图和 QAS 中表达。 | 无 | 文档债务/一致性债务 | Learning Record Service、Message Queue、Progress Aggregation Worker | 保持本次 Phase 3 记录为评估依据；若后续进入实现阶段，可补充正式 ADR 或设计说明。 | M |
| TD-009 | 课程详情高频浏览未单独形成 ADR，缓存预热、热点 Key 保护和回源限流策略仍需细化。 | 无 | 性能债务/文档债务 | Course Service、Redis、MySQL | 在实现设计中补充课程缓存策略；增加缓存穿透、击穿和雪崩测试。 | M |
| TD-010 | Barrage Service 支持滚动发布，但 WebSocket 长连接优雅摘流和前端重连策略尚需细化。 | 无 | 可修改性债务 | Barrage Service、Load Balancer、Frontend | 制定滚动发布流程；实现连接排空、重连退避和互动降级提示。 | M |
| TD-011 | TraceID 需要跨 REST、MQ、Worker 和外部回调传播，当前依赖各服务共同遵守日志规范。 | ADR-001a、ADR-002a | 可观测性债务 | API Gateway、Order Service、Live Access Service、MQ、OTel Collector | 制定日志字段标准；在 MQ Header 中传递 TraceID；增加链路追踪完整性检查。 | M |
| TD-012 | 微服务数量较多，团队需要维护 Redis、MQ、MySQL、OTel、CDN 等多个基础设施组件。 | ADR-001a、ADR-002a、ADR-003、ADR-004 | 运维债务 | 全平台部署与监控 | 优先选择托管服务；编写最小化运维 Runbook；建立容量、告警、扩容和故障演练流程。 | M |

