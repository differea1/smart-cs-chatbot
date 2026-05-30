import re


class SentimentService:
    NEGATIVE_PATTERNS = [
        r"(垃圾|骗子|坑人|差评|气[死炸]|火大|太差|失望|什么破[东西玩意]|烂|差劲|投诉|退款.*不|退货.*不)",
        r"(烦|糟糕|恶[心劣]|无语|忽悠|骗人|扯淡|坑爹)",
        r"(妈的|操|日了|卧槽|fuck|s[h\\*]it)",
    ]
    POSITIVE_PATTERNS = [
        r"(谢谢|感谢|很好|不错|满意|棒|赞|好评|喜欢|快|高效)",
    ]
    NEUTRAL_EXCLUDE = [
        r"(退货|退款|退换)",  # 退货本身不等于不满
    ]

    async def analyze(self, message: str) -> str:
        # 先检查是否在排除列表（中性词但可能被负面匹配）
        for pattern in self.NEUTRAL_EXCLUDE:
            if re.search(pattern, message):
                for neg_pattern in self.NEGATIVE_PATTERNS:
                    if re.search(neg_pattern, message):
                        return "negative"
                break

        # 负面检测
        for pattern in self.NEGATIVE_PATTERNS:
            if re.search(pattern, message):
                return "negative"

        # 正面检测
        for pattern in self.POSITIVE_PATTERNS:
            if re.search(pattern, message):
                return "positive"

        return "neutral"
