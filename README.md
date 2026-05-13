# 多智能体用户故事生成与优化系统

## 一、项目简介

本项目是一个基于大语言模型与多智能体协作机制的用户故事自动生成与优化系统。系统面向软件需求分析阶段，支持用户通过文本需求、代码片段、需求文档以及项目源码等多种输入方式生成用户故事，并结合 INVEST 原则对生成结果进行质量评估、反馈优化和多轮迭代改进。

系统通过模拟产品经理、架构师、测试人员、评价智能体等多个角色之间的协作过程，实现从需求理解、用户故事生成、质量评分、问题反馈到结果优化的完整流程，能够辅助需求分析人员快速获得结构规范、语义清晰、可测试性较强的用户故事内容。

本项目主要用于毕业设计与论文实验验证，适用于需求工程、敏捷开发、用户故事生成、AIGC 辅助软件工程等相关场景。

---

## 二、主要功能

### 1. 文本需求生成用户故事

用户输入自然语言需求后，系统自动分析需求内容，并生成符合敏捷开发规范的用户故事。

示例格式：

```text
作为一名用户，
我希望能够找回密码，
以便在忘记密码时重新登录系统。
```

### 2. 代码逆向生成用户故事

系统支持输入代码片段，通过分析代码中的接口、业务逻辑、函数含义和数据处理流程，逆向生成对应的用户故事。

该功能适用于已有系统的需求补全文档、代码理解和需求反向建模。

### 3. 需求文档生成用户故事

用户可以上传或输入需求文档内容，系统根据文档中的功能描述、业务规则和用户目标，自动提取并生成用户故事。

### 4. 项目源码生成用户故事

系统支持对整个项目源码进行分析，识别系统功能模块、接口逻辑和业务流程，并生成对应的用户故事集合。

### 5. 多智能体协作生成

系统通过多个智能体模拟不同软件工程角色之间的协作过程，包括：

- 产品经理智能体：负责理解用户需求并生成初始用户故事；
- 架构师智能体：负责分析系统结构与业务边界；
- 测试智能体：负责根据 INVEST 原则评价用户故事质量；
- 反馈智能体：负责生成结构化修改建议；
- 优化智能体：负责根据反馈信息重写和优化用户故事。

### 6. INVEST 用户故事质量评估

系统基于 INVEST 原则对用户故事进行评分，评价维度包括：

- Independent，独立性；
- Negotiable，可协商性；
- Valuable，价值性；
- Estimable，可估算性；
- Small，小型性；
- Testable，可测试性。

系统会给出每个维度的评分、问题说明和优化建议。

### 7. 多轮迭代优化

系统支持根据评分结果和反馈建议进行多轮用户故事优化，使用户故事逐步达到更高质量。

基本流程如下：

```text
初始生成 → 质量评估 → 反馈生成 → 优化重写 → 再次评估 → 输出最终结果
```

### 8. 结果展示与导出

系统支持对生成结果进行可视化展示，包括：

- 多智能体对话过程展示；
- 用户故事列表展示；
- INVEST 评分雷达图；
- 评分变化折线图；
- 优化过程展示；
- PDF 文档导出；
- 历史记录查看。

---

## 三、技术栈

### 前端技术

- Vue 3
- Vite
- Vue Router
- Axios
- ECharts
- Element Plus / 原生组件样式
- Nginx

### 后端技术

- Python
- FastAPI
- Uvicorn
- LangChain / LLM API 调用
- ReportLab，PDF 生成
- MongoDB，历史记录存储

### 部署技术

- Docker
- Docker Compose
- Nginx
- MongoDB 容器化部署

---

## 四、项目目录结构

项目目录结构示例如下：

```text
storygen/
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── api/                # 接口路由
│   │   ├── agents/             # 多智能体模块
│   │   ├── services/           # 业务逻辑服务
│   │   ├── models/             # 数据模型
│   │   ├── utils/              # 工具函数
│   │   └── main.py             # FastAPI 入口文件
│   ├── outputs/                # PDF 导出文件目录
│   ├── requirements.txt        # Python 依赖
│   └── Dockerfile              # 后端 Docker 配置
│
├── frontend/                   # 前端项目
│   ├── src/
│   │   ├── assets/             # 静态资源
│   │   ├── components/         # 公共组件
│   │   ├── views/              # 页面组件
│   │   ├── router/             # 路由配置
│   │   ├── services/           # API 请求封装
│   │   ├── composables/        # 组合式函数
│   │   ├── App.vue             # 根组件
│   │   └── main.js             # 前端入口文件
│   ├── package.json            # 前端依赖配置
│   ├── vite.config.js          # Vite 配置
│   ├── nginx.conf              # Nginx 配置
│   └── Dockerfile              # 前端 Docker 配置
│
├── docker-compose.yml          # Docker Compose 编排文件
├── README.md                   # 项目说明文档
└── .gitignore                  # Git 忽略配置
```

实际目录可能会根据项目实现略有差异。

---

## 五、环境要求

### 本地运行环境

运行项目前，请确保本机已安装以下环境：

```text
Node.js >= 16
npm >= 8
Python >= 3.9
MongoDB >= 5.0
Git
```

### Docker 部署环境

如果使用 Docker 部署，请确保安装：

```text
Docker
Docker Compose
```

---

## 六、本地运行方式

### 1. 克隆项目

```bash
git clone https://github.com/CSMA-Graduation-Projects/2026-luoyigang-storygen.git
cd 2026-luoyigang-storygen
```

---

## 七、后端运行说明

### 1. 进入后端目录

```bash
cd backend
```

### 2. 创建虚拟环境

Linux / macOS：

```bash
python3 -m venv venv
source venv/bin/activate
```

Windows：

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

在 `backend` 目录下创建 `.env` 文件：

```env
OPENAI_API_KEY=你的大模型API密钥
MONGO_URL=mongodb://localhost:27017
DATABASE_NAME=storygen
```

如果项目使用其他大模型接口，可以根据实际情况配置：

```env
LLM_API_KEY=你的API密钥
LLM_BASE_URL=你的模型接口地址
LLM_MODEL=模型名称
```

### 5. 启动 MongoDB

如果本地已经安装 MongoDB，可直接启动 MongoDB 服务。

Linux 示例：

```bash
sudo systemctl start mongod
```

也可以使用 Docker 启动 MongoDB：

```bash
docker run -d \
  --name storygen-mongo \
  -p 27017:27017 \
  mongo:6.0
```

### 6. 启动后端服务

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

启动成功后，后端服务地址为：

```text
http://localhost:8000
```

FastAPI 接口文档地址为：

```text
http://localhost:8000/docs
```

---

## 八、前端运行说明

### 1. 进入前端目录

```bash
cd frontend
```

### 2. 安装依赖

```bash
npm install
```

### 3. 配置接口地址

在前端项目中创建 `.env.development` 文件：

```env
VITE_API_BASE_URL=http://localhost:8000
```

如果项目中已经在 `src/services/api.js` 中写死接口地址，请检查并修改为后端实际地址：

```js
const BASE_URL = "http://localhost:8000"
```

### 4. 启动前端项目

```bash
npm run dev
```

启动成功后，访问：

```text
http://localhost:5173
```

---

## 九、Docker 部署说明

项目支持通过 Docker Compose 一键部署前端、后端和 MongoDB 服务。

### 1. 项目根目录准备

确保项目根目录包含以下文件：

```text
docker-compose.yml
backend/Dockerfile
frontend/Dockerfile
frontend/nginx.conf
```

---

## 十、后端 Dockerfile 示例

`backend/Dockerfile`：

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 十一、前端 Dockerfile 示例

`frontend/Dockerfile`：

```dockerfile
FROM node:18-alpine AS build

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

RUN npm run build

FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html

COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

---

## 十二、前端 Nginx 配置示例

`frontend/nginx.conf`：

```nginx
server {
    listen 80;
    server_name localhost;

    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://backend:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

如果前端请求地址为 `/api` 开头，则可以通过 Nginx 转发到后端服务。

---

## 十三、Docker Compose 配置示例

`docker-compose.yml`：

```yaml
version: "3.8"

services:
  mongo:
    image: mongo:6.0
    container_name: storygen-mongo
    restart: always
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: storygen-backend
    restart: always
    ports:
      - "8000:8000"
    environment:
      - MONGO_URL=mongodb://mongo:27017
      - DATABASE_NAME=storygen
      - OPENAI_API_KEY=你的大模型API密钥
    depends_on:
      - mongo

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: storygen-frontend
    restart: always
    ports:
      - "80:80"
    depends_on:
      - backend

volumes:
  mongo_data:
```

---

## 十四、Docker 部署步骤

### 1. 进入项目根目录

```bash
cd 2026-luoyigang-storygen
```

### 2. 构建并启动容器

```bash
docker compose up -d --build
```

如果系统使用的是旧版本 Docker Compose，可以使用：

```bash
docker-compose up -d --build
```

### 3. 查看容器运行状态

```bash
docker ps
```

正常情况下应看到以下容器：

```text
storygen-frontend
storygen-backend
storygen-mongo
```

### 4. 查看后端日志

```bash
docker logs -f storygen-backend
```

### 5. 查看前端日志

```bash
docker logs -f storygen-frontend
```

### 6. 访问系统

前端访问地址：

```text
http://服务器IP
```

后端接口地址：

```text
http://服务器IP:8000
```

接口文档地址：

```text
http://服务器IP:8000/docs
```

---

## 十五、常用 Docker 命令

### 停止服务

```bash
docker compose down
```

### 重新构建并启动

```bash
docker compose up -d --build
```

### 查看日志

```bash
docker compose logs -f
```

### 查看指定服务日志

```bash
docker compose logs -f backend
```

### 删除容器和网络

```bash
docker compose down
```

### 删除容器、网络和数据卷

```bash
docker compose down -v
```

注意：执行 `docker compose down -v` 会删除 MongoDB 数据，请谨慎使用。

---

## 十六、主要接口说明

以下接口名称可根据实际项目代码进行调整。

### 1. 文本需求生成用户故事

```http
POST /generate_story
```

请求示例：

```json
{
  "requirement": "用户可以找回密码"
}
```

响应示例：

```json
{
  "stories": [
    {
      "role": "用户",
      "goal": "找回密码",
      "benefit": "在忘记密码时重新登录系统"
    }
  ]
}
```

---

### 2. 流式生成用户故事

```http
GET /generate_story_stream?requirement=用户可以找回密码
```

该接口用于实时返回多智能体协作过程，前端可以通过 EventSource 接收流式数据。

前端示例：

```js
const eventSource = new EventSource(
  `/generate_story_stream?requirement=${encodeURIComponent(requirement)}`
)

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data)
  console.log(data)
}
```

---

### 3. 用户故事质量评估

```http
POST /evaluate_story
```

请求示例：

```json
{
  "story": "作为一名用户，我希望能够找回密码，以便在忘记密码时重新登录系统。"
}
```

响应示例：

```json
{
  "score": 86,
  "invest": {
    "independent": 14,
    "negotiable": 15,
    "valuable": 15,
    "estimable": 14,
    "small": 13,
    "testable": 15
  },
  "suggestion": "用户故事整体较完整，但可以进一步补充验收条件。"
}
```

---

### 4. 导出 PDF

```http
POST /export_pdf
```

请求示例：

```json
{
  "requirement": "用户可以找回密码",
  "sub_requirements": ["输入邮箱", "接收验证码", "重置密码"],
  "final_stories": [
    "作为一名用户，我希望能够通过邮箱找回密码，以便在忘记密码时重新登录系统。"
  ]
}
```

响应示例：

```json
{
  "filename": "user_story_20260513_120000.pdf",
  "url": "/outputs/user_story_20260513_120000.pdf"
}
```

---

### 5. 查询历史记录

```http
GET /history
```

响应示例：

```json
[
  {
    "id": "xxx",
    "type": "text",
    "requirement": "用户可以找回密码",
    "stories": [],
    "created_at": "2026-05-13 12:00:00"
  }
]
```

---

## 十七、前端功能页面说明

### 1. 首页

用于输入需求并生成用户故事。

### 2. 多智能体对话页面

展示产品经理、架构师、测试智能体等角色之间的协作过程。

### 3. 评分分析页面

展示 INVEST 各维度评分结果，可通过雷达图和折线图查看用户故事质量变化。

### 4. 历史记录页面

用于查看历史生成记录，包括：

- 文本需求生成记录；
- 代码生成记录；
- 需求文档生成记录；
- 项目源码生成记录。

### 5. PDF 导出功能

支持将用户需求、子需求、最终用户故事和评分结果导出为 PDF 文件。

---

## 十八、系统运行流程

系统整体运行流程如下：

```text
用户输入需求
    ↓
需求解析与任务分解
    ↓
多智能体协作生成初始用户故事
    ↓
基于 INVEST 原则进行质量评估
    ↓
生成结构化反馈建议
    ↓
根据反馈进行用户故事优化
    ↓
判断是否达到质量要求
    ↓
输出最终用户故事
    ↓
结果展示与 PDF 导出
```

---

## 十九、常见问题

### 1. 前端无法访问后端接口

请检查以下内容：

1. 后端服务是否正常启动；
2. 前端配置的接口地址是否正确；
3. Docker 部署时 Nginx 是否正确配置代理；
4. 后端是否允许跨域请求。

FastAPI 可配置 CORS：

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### 2. Docker 部署后前端页面空白

可以检查：

```bash
docker logs -f storygen-frontend
```

并确认前端是否成功执行：

```bash
npm run build
```

同时检查 `nginx.conf` 中是否配置：

```nginx
try_files $uri $uri/ /index.html;
```

该配置用于解决 Vue Router 刷新页面后 404 的问题。

---

### 3. 后端连接 MongoDB 失败

如果使用 Docker Compose 部署，后端连接地址不能写成：

```text
mongodb://localhost:27017
```

应写成：

```text
mongodb://mongo:27017
```

因为在 Docker Compose 网络中，服务之间通过服务名访问。

---

### 4. PDF 中文乱码

如果导出的 PDF 中文显示异常，需要确认 ReportLab 是否正确注册中文字体。

示例：

```python
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(TTFont("SimSun", "SimSun.ttf"))
```

同时确保服务器中存在对应字体文件。

---

### 5. 流式接口连接一段时间后断开

如果使用 `StreamingResponse` 或 SSE，需要注意：

1. 前端应使用 `EventSource` 接收；
2. 后端返回类型应为 `text/event-stream`；
3. Nginx 代理需要关闭缓冲。

Nginx 可添加：

```nginx
proxy_buffering off;
proxy_cache off;
proxy_read_timeout 3600s;
```

---

## 二十、开发说明

### 后端开发启动

```bash
cd backend
uvicorn app.main:app --reload
```

### 前端开发启动

```bash
cd frontend
npm run dev
```

### 前端打包

```bash
npm run build
```

### 查看 MongoDB 数据

进入 MongoDB 容器：

```bash
docker exec -it storygen-mongo mongosh
```

切换数据库：

```bash
use storygen
```

查看集合：

```bash
show collections
```

查看历史记录：

```bash
db.history.find()
```

---

## 二十一、项目特色

1. 引入多智能体协作机制，模拟软件工程中不同角色的协同需求分析过程；
2. 支持文本、代码、需求文档和项目源码等多种输入方式；
3. 基于 INVEST 原则构建用户故事质量评估机制；
4. 支持用户故事多轮反馈优化，提高生成结果质量；
5. 提供评分图表、历史记录和 PDF 导出功能；
6. 支持 Docker 容器化部署，便于在服务器环境中运行。

---

## 二十二、适用场景

本系统适用于以下场景：

- 敏捷开发中的用户故事编写；
- 需求分析阶段的需求整理；
- 代码逆向需求理解；
- 软件工程课程实验；
- 毕业设计系统实现；
- AIGC 辅助软件工程研究；
- 多智能体协作生成实验。

---

## 二十三、后续优化方向

后续可以从以下方面继续优化系统：

1. 引入更精细的用户故事验收标准生成机制；
2. 支持更多类型的需求文档格式解析；
3. 增强项目源码分析能力；
4. 增加用户故事版本对比功能；
5. 引入人工反馈参与优化过程；
6. 完善权限管理和用户登录功能；
7. 提高多智能体协作过程的可解释性；
8. 增加更多实验指标用于论文验证。

---

## 二十四、许可证

本项目仅用于毕业设计、课程设计与学术研究学习使用。

如需用于商业用途，请根据实际情况补充许可证说明。

---

## 二十五、作者信息

项目名称：多智能体用户故事生成与优化系统  
项目类型：毕业设计 / 软件工程实践项目  
主要技术：Vue3、FastAPI、MongoDB、Docker、大语言模型、多智能体协作  
研究方向：AIGC 辅助需求工程、用户故事自动生成、软件工程智能化
