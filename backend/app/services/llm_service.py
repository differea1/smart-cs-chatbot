import json
import time
import httpx
from typing import AsyncIterator
from app.core.config import get_settings

settings = get_settings()

MOCK_RESPONSES = {
    "product_inquiry": "根据我们的产品信息，**极米 X1 Pro** 的主要参数如下：\n\n- **亮度**：2200 ANSI 流明\n- **分辨率**：4K（3840×2160）\n- **对比度**：5000:1\n- **投影尺寸**：30-200 英寸\n- **连接方式**：WiFi 6 / 蓝牙 5.2 / HDMI 2.1\n\n建议在环境光较暗的场景下使用以获得最佳观看效果 😊 请问还有其他想了解的吗？",
    "return_exchange": "了解！我来帮您处理退货事宜 📋\n\n首先需要确认一下：\n1. 请问您的**订单号**或**购买时使用的手机号**是什么？\n2. 方便说下退货原因吗？（拍错/不喜欢/质量问题/发错货等）\n\n这样我能更快帮您判断是否符合退换条件～",
    "troubleshooting": "好的，让我帮您排查一下 🔧\n\n投影仪画面模糊可能有几种原因，我们按以下步骤逐一排查：\n\n**第一步：检查镜头**\n- 镜头表面是否有灰尘或指纹？用干净的软布轻轻擦拭\n\n请问做完这一步后，画面有改善吗？",
    "complaint": "非常抱歉给您带来了不好的体验 😔 我完全理解您的感受。\n\n请放心，我马上帮您优先处理这个问题。为了更好地帮到您，请告诉我您的**订单号**和遇到的具体问题，我会尽最大努力为您解决。\n\n如果我的处理不能让您满意，我会立即为您转接高级客服专员。",
    "chitchat": "您好！我是小极，极米科技的智能售后助手 😊\n\n我可以帮您：\n- 📦 **查询订单**物流状态\n- ↩️ **申请退换货**\n- 🔧 **故障排查**引导\n- ℹ️ **了解产品**参数与使用教程\n\n请问今天有什么可以帮到您的吗？",
    "default": "好的，我理解您的问题了。让我为您查找相关信息...\n\n根据您提供的信息，我建议您可以通过以下方式获得更详细的帮助：\n\n1. 提供您的**订单号**，我可以帮您查询具体信息\n2. 描述您遇到的具体情况，我会为您提供针对性的解决方案\n\n请问还有什么我可以帮到您的吗？",
}


class LLMService:
    def __init__(self):
        self.mode = settings.LLM_MODE
        self.api_key = settings.DEEPSEEK_API_KEY
        self.base_url = settings.DEEPSEEK_BASE_URL
        self.model = settings.DEEPSEEK_MODEL

    async def chat_stream(self, messages: list[dict]) -> AsyncIterator[str]:
        if self.mode == "mock" or not self.api_key:
            async for chunk in self._mock_stream(messages):
                yield chunk
        else:
            async for chunk in self._deepseek_stream(messages):
                yield chunk

    async def _mock_stream(self, messages: list[dict]) -> AsyncIterator[str]:
        """模拟流式响应，用于开发测试"""
        user_msg = ""
        intent = "default"
        for m in reversed(messages):
            if m["role"] == "user":
                user_msg = m["content"]
            if m["role"] == "system" and "intent" in m.get("content", ""):
                pass

        # 简单意图判断
        if any(w in user_msg for w in ["退货", "退款", "退换", "换货"]):
            intent = "return_exchange"
        elif any(w in user_msg for w in ["故障", "坏了", "不亮", "模糊", "开不了机", "连不上"]):
            intent = "troubleshooting"
        elif any(w in user_msg for w in ["垃圾", "投诉", "差评", "气死", "坑人"]):
            intent = "complaint"
        elif any(w in user_msg for w in ["参数", "规格", "多少钱", "价格", "亮度", "分辨率"]):
            intent = "product_inquiry"
        elif any(w in user_msg for w in ["你好", "在吗", "hi", "hello"]):
            intent = "chitchat"

        response = MOCK_RESPONSES.get(intent, MOCK_RESPONSES["default"])

        # 模拟流式输出
        for char in response:
            yield char
            time.sleep(0.015)

    async def _deepseek_stream(self, messages: list[dict]) -> AsyncIterator[str]:
        """调用 DeepSeek API 流式响应"""
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 1024,
                    "stream": True,
                },
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data)
                            delta = (
                                chunk.get("choices", [{}])[0]
                                .get("delta", {})
                                .get("content", "")
                            )
                            if delta:
                                yield delta
                        except (json.JSONDecodeError, KeyError, IndexError):
                            continue
