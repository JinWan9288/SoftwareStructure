## 🎓 在线教育直播与点播平台

[![Java Version](https://img.shields.io/badge/Java-17%2B-blue.svg)](https://openjdk.java.net/)
[![Spring Boot](https://img.shields.io/badge/SpringBoot-3.1.x-brightgreen.svg)](https://spring.io/projects/spring-boot)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

#### 📖 项目总览 (Project Overview)

本项目是一个支持万人同时在线的高可用教育直播与点播平台。系统致力于在开学季流量洪峰等高并发场景下，为师生提供极低延迟的推拉流接入、高吞吐的实时弹幕互动以及安全可靠的知识产权防盗播保护。

系统后端采用 **Java (Spring Cloud Alibaba 微服务体系)** 构建，基于领域驱动设计（DDD）的思想划分微服务边界，并采用异步事件驱动架构来保障核心交易链路的最终一致性与高可用。

#### 🏗️ 核心微服务模块 (Microservices)
本项目采用 Maven 多模块结构，划分为以下核心业务域：
* **`edu-gateway` (API 统一网关)**：基于 Spring Cloud Gateway，负责全局 JWT 鉴权、路由分发、以及基于 Sentinel 的防刷限流机制。
* **`edu-auth` (认证与安全服务)**：负责 SSO 单点登录、动态防盗链 Token的签名计算与下发 (对应 ADR-006)。
* **`edu-live-access` (直播接入服务)**：应对万人并发进入直播间的极点流量，内置 Caffeine + Redis 多级缓存与断路器保护 (对应 ADR-002)。
* **`edu-course` (课程与多校区服务)**：课程元数据管理，底层集成 MyBatis-Plus 动态多租户拦截器，实现多校区数据逻辑隔离 (对应 ADR-005)。
* **`edu-order` (交易订单服务)**：处理选课下单，集成支付宝/微信回调，利用数据库唯一索引实施回调幂等拦截。
* **`edu-entitlement` (权益与异步任务服务)**：订阅 Kafka 支付成功事件，完成跨域的虚拟权益资产发放与对账补偿 (对应 ADR-001)。

#### 🛠️ 核心技术栈
* **后端框架**: Java 17, Spring Boot 3.x, Spring Cloud Alibaba
* **持久化层**: MySQL 8.0, MyBatis-Plus (含多租户插件)
* **缓存与分布式锁**: Redis 7.0 (Redisson)
* **消息中间件**: Kafka (用于异步事件驱动、进度聚合微批处理)
* **流量防护与熔断**: Alibaba Sentinel / Resilience4j
* **基础设施**: Docker & Docker-Compose

---

#### 🚀 快速入门 (Quick Start)

##### 1. 环境准备 (Prerequisites)
* JDK 17 或更高版本
* Maven 3.8+
* Python 3.9+ (用于运行本地架构 PoC 验证)
* Docker & Docker Compose (用于启动依赖中间件)

##### 2. 启动基础设施 (Middleware)
系统依赖 MySQL、Redis、Kafka 和 Nacos（注册中心）。我们在 `deploy/docker-compose/` 目录下提供了编排文件，一键拉起所有依赖：
```bash
cd deploy/docker-compose
docker-compose up -d

# 检查服务运行状态
docker-compose ps