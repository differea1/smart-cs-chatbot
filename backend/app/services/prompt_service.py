import os


class PromptBuilder:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    PROMPTS_DIR = os.path.join(BASE_DIR, "prompts")

    def __init__(self):
        self.base_prompt = self._load("base_role.txt")
        self.business_prompts = {
            "return_exchange": self._load("business_return.txt"),
            "troubleshooting": self._load("business_troubleshoot.txt"),
            "complaint": self._load("business_complaint.txt"),
        }

    def _load(self, filename: str) -> str:
        path = os.path.join(self.PROMPTS_DIR, filename)
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except FileNotFoundError:
            print(f"[PromptBuilder] Warning: {filename} not found")
            return ""

    def build(
        self,
        intent: str,
        rag_results: list[dict],
        conversation_history: list[dict],
        sentiment: str,
    ) -> list[dict]:
        messages = []

        # 第1层 + 第2层
        system_prompt = self.base_prompt
        if intent in self.business_prompts:
            system_prompt += "\n\n" + self.business_prompts[intent]

        if sentiment == "negative":
            system_prompt += "\n\n## 当前用户情绪状态\n检测到用户有负面情绪，请优先使用安抚策略，展示理解和解决问题的真诚意愿。主动道歉并快速给出解决方案。"

        messages.append({"role": "system", "content": system_prompt})

        # 第3层：RAG 知识注入
        if rag_results:
            rag_text = "## 参考知识库信息\n\n以下是知识库中与用户问题最相关的信息，请优先依据这些信息作答：\n\n"
            for i, r in enumerate(rag_results, 1):
                rag_text += f"**参考{i}** (相似度: {r['similarity']})\n{r['content']}\n\n"
            rag_text += "\n如果参考信息不相关，请诚实说明并引导用户转人工。"
            messages.append({"role": "system", "content": rag_text})

        # 第4层：对话历史（最近10轮）
        for turn in conversation_history[-10:]:
            messages.append({"role": turn.get("role", "user"), "content": turn.get("content", "")})

        return messages
