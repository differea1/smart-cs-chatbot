# 极米科技 销售（售后）服务AI聊天机器人

> 大数据机器学习III 课程项目

## 项目简介

面向销售（售后）服务场景的 AI 聊天机器人全栈应用。支持产品咨询、订单查询、退换货引导、故障排查、情绪感知安抚等功能。

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + Vite + Vant UI |
| 后端 | Python FastAPI + SQLAlchemy |
| 向量库 | ChromaDB（嵌入式） |
| 大模型 | DeepSeek API（或本地模拟） |
| 数据库 | SQLite（开发）/ MySQL（生产） |
| 部署 | Docker Compose + Nginx |

## 快速开始

### 1. 克隆项目

```bash
git clone <repo-url>
cd smart-cs-chatbot
```

### 2. 配置环境变量

编辑 `backend/.env`：

```env
DATABASE_URL=sqlite:///./chatbot.db
LLM_MODE=deepseek          # 使用 mock 模式不需要 API Key
DEEPSEEK_API_KEY=sk-xxxx   # 你的 DeepSeek API Key
JWT_SECRET=your-secret-key
```

### 3. 启动后端

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 初始化知识库（首次运行）
python scripts/seed_knowledge.py

# 启动后端（http://localhost:8000）
uvicorn app.main:app --reload
```

### 4. 启动前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器（http://localhost:5173）
npm run dev
```

### 5. 访问应用

- 用户聊天界面：http://localhost:5173
- API 文档：http://localhost:8000/docs
- 管理后台：http://localhost:5173/admin
  - 默认账号：admin / admin123

## Docker 部署

```bash
# 构建并启动
docker-compose up -d --build

# 初始化知识库
docker-compose exec backend python scripts/seed_knowledge.py

# 访问 http://localhost
```

## 项目结构

```
smart-cs-chatbot/
├── backend/
│   ├── app/
│   │   ├── api/          # REST API 路由
│   │   ├── core/         # 配置、数据库、安全
│   │   ├── models/       # SQLAlchemy 模型
│   │   ├── schemas/      # Pydantic 模型
│   │   ├── services/     # 业务逻辑层
│   │   ├── prompts/      # 提示词模板
│   │   └── main.py       # FastAPI 入口
│   ├── scripts/          # 初始化脚本
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── views/        # 页面组件
│       ├── components/   # 通用组件
│       ├── store/        # Pinia 状态管理
│       ├── api/          # API 封装
│       └── router/       # 路由配置
├── nginx/                # Nginx 配置
├── docker-compose.yml
└── README.md
```

## 核心功能

- 7×24 小时智能客服
- 产品咨询（RAG 知识库检索）
- 订单查询与物流跟踪
- 退换货政策解答与流程引导
- 故障排查决策树引导
- 客户情绪感知与安抚
- 满意度评分反馈
- 管理后台（仪表盘、对话记录、知识库管理）

## 提示词工程

本项目采用四层分层提示词架构：
1. **基础角色层**：机器人身份与核心行为准则
2. **业务规则层**：按意图类型动态加载（退换货/故障排查/投诉安抚）
3. **动态上下文层**：RAG 检索结果注入
4. **对话注入层**：最近 N 轮对话历史

提示词模板位于 `backend/app/prompts/`。
