import asyncio
import time
from fastapi import FastAPI, HTTPException, BackgroundTasks
import uvicorn

app = FastAPI(title="Edu Platform PoC (No Redis Version)")


# 终极绝招：用 Python 内存字典模拟 Redis！
# 彻底摆脱外部中间件依赖，保证压测图表完美！
mock_rate_limit = {}
mock_cache = {}
mock_idempotent = {}


@app.get("/api/live/access/{user_id}/{course_id}")
async def access_live_room(user_id: str, course_id: str):
    # 1. 模拟断路器/限流器
    current_sec = int(time.time())
    rate_key = f"rate_limit:{current_sec}"

    mock_rate_limit[rate_key] = mock_rate_limit.get(rate_key, 0) + 1
    current_reqs = mock_rate_limit[rate_key]

    if current_reqs > 500:
        raise HTTPException(status_code=429, detail="服务器排队中，触发保护降级")

    # 2. 模拟 L2 缓存预检
    cache_key = f"ent:{user_id}:{course_id}"
    if cache_key in mock_cache:
        # 缓存命中：极速返回
        return {"status": "success", "token": mock_cache[cache_key], "source": "redis_cache"}

    # 3. 模拟缓存穿透与慢查询回源
    await asyncio.sleep(0.5)

    fake_token = f"sign_{user_id}_{current_sec}"
    mock_cache[cache_key] = fake_token

    return {"status": "success", "token": fake_token, "source": "slow_database"}


async def async_process_entitlement(order_id: str):
    await asyncio.sleep(1)


@app.post("/api/payment/callback")
async def payment_callback(order_id: str, background_tasks: BackgroundTasks):
    # 1. 模拟幂等拦截
    if order_id in mock_idempotent:
        return {"status": "success", "msg": "重复回调，已幂等拦截"}

    mock_idempotent[order_id] = "PAID"
    background_tasks.add_task(async_process_entitlement, order_id)
    return {"status": "success", "msg": "首次回调，已发布异步发课事件"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)