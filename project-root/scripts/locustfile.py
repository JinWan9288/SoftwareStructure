from locust import HttpUser, task, between
import random


class ArchitecturePoCUser(HttpUser):
    wait_time = between(0.1, 0.5)

    @task(3)
    def test_live_access_adr002a(self):
        """测试 ADR-002a: 直播间入口大并发 (验证缓存与熔断)"""
        user_id = random.randint(1, 10000)
        course_id = "Course_Hot_01"  # 模拟万人涌入同一个爆款直播间

        with self.client.get(f"/api/live/access/{user_id}/{course_id}", catch_response=True) as response:
            # 业务降级 429 属于架构预期的自我保护，在压测中标为成功
            if response.status_code in [200, 429]:
                response.success()
            else:
                response.failure(f"崩了: {response.status_code}")

    @task(1)
    def test_payment_callback_adr001a(self):
        """测试 ADR-001a: 支付回调风暴 (验证幂等性与异步处理)"""
        # 故意只用 100 个订单号，模拟第三方因为没收到响应而在疯狂重复投递
        order_id = f"ORDER_{random.randint(1, 100)}"

        with self.client.post(f"/api/payment/callback?order_id={order_id}", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure("回调处理失败")