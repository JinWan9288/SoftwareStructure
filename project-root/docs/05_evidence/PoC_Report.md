# PoC_Report

## PoC-001: 基于消息队列的支付回调异步与最终一致性验证
### 验证的架构假设
验证 ADR-001a 提出的假设：通过 MQ 异步解耦订单与权益服务，能够在第三方支付平台发生高并发重复投递时，实现有效削峰，并保证权益数据的最终一致性。

### 实验设计
- **环境**: Docker-compose 本地集群 (1x API Gateway, 1x Order Service, 1x Entitlement Service, 1x MySQL, 1x RabbitMQ)
- **方法**: 使用 JMeter 模拟第三方支付平台，针对同一个 `paymentOrderId` 在 1 秒内并发发送 50 次支付成功 Webhook 回调。同时在中途人为杀死 Entitlement Service 进程 30 秒后重启。
- **验证标准(Pass/Fail条件)**: 
  1. Order Service 响应时间 P95 < 200ms。
  2. 订单状态仅跃迁一次。
  3. 服务恢复后，用户权益正确发放，且仅发放一次（无重复计算）。

### 实验过程
1. 启动压测脚本 `payment_webhook_stress.jmx`，并发度 50。
2. 观察 Order Service 日志，确认 49 次请求触发 `PaymentIdempotencyGuard` 拦截并返回 200。
3. 停止 Entitlement Service 容器：`docker stop entitlement-service`。
4. 消息堆积在 RabbitMQ `order_paid_queue` 中。
5. 恢复服务：`docker start entitlement-service`。

### 结果数据
- **Order Service P95 延迟**: 45ms（远低于 200ms 的阈值）。
- **幂等拦截率**: 98% (49/50)。
- **一致性审计**: 恢复后，RabbitMQ 积压消息被成功消费。通过 `userId+courseId` 的唯一索引，二次幂等生效，用户权益表中仅增加 1 条记录。

### 结论
- **假设是否成立**: 是。
- **对架构决策的影响**: 确认 ADR-001a 设计可靠，正式采纳。
- **后续行动**: 在生产环境补充死信队列监控告警配置。

---

## PoC-002: 视频云接口抖动熔断与降级机制验证
### 验证的架构假设
验证 ADR-002a 提出的假设：当第三方视频云 API 发生大面积延迟或故障时，Live Access Service 的断路器能在 30 秒内打开，防止本地应用线程池被耗尽。

### 实验设计
- **环境**: 同上，外加一个模拟视频云的 Mock Server（基于 WireMock）。
- **方法**: 以 5,000 QPS 的恒定速率请求进入直播间接口。运行 10 秒后，通过 WireMock 管理接口注入 2.5 秒的固定延迟和 30% 的 HTTP 503 错误率。
- **验证标准**: 断路器在 10 秒内打开，后续请求立即触发快速失败，网关层返回“正在排队中”降级提示，且 Live Access Service 的内存和线程池指标保持稳定。

### 实验过程
1. 启动 Locust 发起 5k QPS 请求。
2. 注入故障。
3. 监控 Resilience4j 的 metrics 指标和 JVM 线程数。

### 结果数据
- **断路器状态**: 在故障注入后的第 6 秒，错误率及超时率超过 20% 阈值，状态从 CLOSED 跃迁至 OPEN。
- **资源消耗**: JVM 活跃线程数在短时间冲高后迅速回落至健康水位（150左右），未发生 OOM 或假死。
- **降级响应**: 降级后的 P95 响应时间缩减至 15ms。

### 结论
- **假设是否成立**: 是。
- **对架构决策的影响**: 巩固了通过 Resilience4j 实现外部依赖隔离的决策。
- **后续行动**: 将断路器半开状态的探测请求数调整为 10，以平滑恢复流量。
