import re


class IntentService:
    INTENT_PATTERNS = {
        "product_inquiry": [
            r"(参数|规格|配置|性能|多少钱|价格|尺寸|重量|亮度|分辨率|功能|支持|有没有|介绍|说明书)",
        ],
        "order_query": [
            r"(订单|物流|快递|发货|到哪|还没到|什么时候到|查.*单|物流.*号)",
        ],
        "return_exchange": [
            r"(退货|退款|换货|退掉|不想要|买错|拍错|退.*钱|退.*货|换.*个)",
        ],
        "troubleshooting": [
            r"(故障|坏了|不好使|开不了|打不开|不亮了|没反应|连不上|模糊|偏色|噪音|遥控.*不|不能.*用|出问题|失灵)",
        ],
        "complaint": [
            r"(投诉|差评|垃圾|骗子|坑人|气死|火大|太差|失望|什么破|烂|差劲)",
        ],
        "chitchat": [
            r"^(你好|hi|hello|在吗|嗨|早上好|晚上好|谢谢|感谢|再见|拜拜)",
        ],
    }

    async def classify(self, message: str) -> tuple[str, float]:
        # 先检查是否明确要求转人工
        if re.search(r"(转人工|人工客服|找人工|接人工|找客服|真人)", message):
            return "escalate", 0.95

        # 按优先级匹配
        for intent, patterns in self.INTENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, message):
                    return intent, 0.85

        # 默认：产品咨询
        if len(message) > 10:
            return "product_inquiry", 0.5
        return "chitchat", 0.6
