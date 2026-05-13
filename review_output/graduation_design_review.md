# 毕业设计符合性检查报告

## 1. 项目总体判断

当前项目围绕“多智能体角色扮演的用户故事自动生成与优化系统”展开，已具备前端、后端、接口、模型调用、历史记录、文档/代码/项目源码分析、导出和 Docker 部署等较完整工程结构；论文和 PPT 的主题与本地代码总体一致，云端部署地址也能访问到前端页面和后端接口文档。项目不是简单页面壳子，具备答辩展示基础。但当前仍存在较明显短板：密钥与 `.env` 管理不合规，INVEST 评分实现与论文/PPT叙述不一致，README 与实际运行方式有多处偏差，测试材料偏示例化，PPT 缺少真实系统截图和结果数据。整体判断为“基本框架已具备，但还有较明显短板，需要补强”。

## 2. 已识别的主要材料

- 代码目录：`Backend/user_story_system/`，FastAPI 后端，包含 `app/api/`、`app/services/`、`app/agents/`、`outputs/`、`requirements.txt`、`Dockerfile`。
- 代码目录：`frontend/`，Vue 前端，包含 `src/views/`、`src/components/`、`src/services/api.js`、`src/router/index.js`、`package.json`、`nginx.conf`、`Dockerfile`。
- 部署编排：`docker-compose.yml`，包含 MongoDB、backend、frontend 三个服务。
- 论文文件：`论文PPT/多智能体角色扮演的用户故事自动生成与优化系统设计与实现.doc`，Word 97-2003 格式，文件元数据显示约 110 页、38531 词；因格式限制只能抽取到部分文本和代码片段。
- PPT 文件：`论文PPT/多智能体角色扮演的用户故事自动生成与优化系统-毕业答辩.pptx`，共 16 页。
- 说明文档：根目录 `README.md` 较完整；`frontend/README.md` 为 Vue CLI 默认简要说明。
- 测试材料：`测试数据/需求文档到用户故事测试文档.docx`、`测试数据/vdecoder.zip`、`Backend/user_story_system/outputs/code_story/*.json`。
- GitHub 链接：可访问，仓库为公开仓库，页面显示 5 次提交，并包含 `.env`、后端、前端、测试数据等。
- 部署平台链接：`http://47.237.103.96:8080` 可访问，前端入口、`/api/docs`、`/api/openapi.json`、`/api/agents/config` 均有响应。

## 3. 项目主要优点

- 前后端结构较完整，后端有多类接口，前端有文本需求、代码、文档、项目源码、用户故事优化、历史记录、智能体配置等页面。
- 系统功能与选题特色基本匹配，不是普通管理系统，核心围绕用户故事生成、优化和 INVEST 评价展开。
- 后端有文档解析、源码解析、代码单元拆分、历史记录、导出等服务，能支撑论文中“多来源输入”的叙述。
- 已提供 Docker Compose、Nginx 代理、MongoDB 服务和云端部署，具备基本展示条件。
- 论文和 PPT 均围绕同一题目展开，PPT 的总体逻辑覆盖背景、设计、协作机制、实现与测试总结。

## 4. 主要问题

1. 严重问题：模型接口密钥写入 `Backend/user_story_system/app/config.py`，根目录还存在 `.env` 且 GitHub 页面显示仓库中包含 `.env`。这会影响项目归档、安全合规和答辩可信度。
2. 严重问题：INVEST 评分实现与论文、README、PPT 的“百分制/质量闭环”表述不一致。后端 `calculate_invest_score_hybrid()` 的总分上限实际约为 50，但 `need_improve()` 阈值为 60；前端 `useChat.js` 又自行重算 `/60` 总分并对维度分数做额外处理，容易被认为评分结果不严谨。
3. 较严重问题：README 与实际项目不完全一致。实际后端路径是 `Backend/user_story_system`，README 多处写 `cd backend`；前端实际脚本是 `npm run serve`，README 写 `npm run dev`；环境变量名在 README、docker-compose、代码中不统一。
4. 较严重问题：前后端字段存在疑似不匹配。后端文档解析返回 `requirements[].user_stories`，但 `DocumentStoryView.vue` 读取 `selectedRequirement.user_story` 和 `acceptance_criteria`，可能导致“需求文档到用户故事”页面无法展示生成的用户故事。
5. 较严重问题：测试支撑不足。当前有示例需求文档、示例源码压缩包和两份代码逆向输出 JSON，但缺少正式测试用例表、测试过程截图、失败/边界场景、性能或可用性结果分析。
6. PPT 偏概念介绍，缺少真实系统页面截图、接口返回截图、输入输出样例、评分变化数据和部署演示路径；第 15 页“系统测试与结果分析”目前更像结论描述，不像测试结果。
7. 论文可抽取内容显示包含大量研究背景、公式、引用和代码片段，但当前材料不足以确认测试章节是否有足够真实截图、测试表和结果分析；同时论文/PPT中提到的 Developer Agent、故事点、优先级、依赖关系等内容，在代码中没有统一落地。
8. 云端部署能访问前端和接口文档，但本次未执行会调用大模型或写入历史记录的完整生成流程，因此“核心主流程是否稳定完成”仍需学生现场补充演示证据。

## 5. 代码与系统实现检查结果

### 已有基础

- 后端采用 FastAPI，入口为 `Backend/user_story_system/app/main.py`，注册了文本生成、PDF、文档解析、项目源码解析、用户故事优化、代码逆向、历史记录和智能体配置等路由。
- 后端服务层较完整：`story_service.py` 实现文本需求拆分、PM/QA/Architect 协作、INVEST 评分和历史保存；`code_story_service.py` 支持代码片段/文件到用户故事；`document_story_service.py` 支持 docx/pdf/md/txt 解析；`project_story_service.py` 支持 zip/tar/源码文件解析；`history_service.py` 使用 MongoDB 保存历史。
- 前端页面覆盖较多：`ChatView.vue`、`CodeStoryView.vue`、`DocumentStoryView.vue`、`ProjectStoryView.vue`、`UserStoryOptimizationView.vue`、`HistoryStoryView.vue`、`AgentView.vue`、雷达图和折线图页面等。
- Docker 部署结构具备：`docker-compose.yml` 包含 MongoDB、backend、frontend；前端 Nginx 已配置 `/api/` 代理、长请求和上传大小。
- 存在少量输出样例：`Backend/user_story_system/outputs/code_story/*.json`。

### 存在问题

- `app/config.py` 中存在硬编码密钥，且没有实际读取 `OPENAI_API_KEY` 等环境变量；这与 `docker-compose.yml` 和 README 中的环境变量说明不一致。
- `invest_score.py` 的评分公式与阈值有明显问题，总分上限与 `need_improve(score, threshold=60)` 不匹配；大模型评分解析失败时 `llm_details` 为空，还可能引发后续维度取值异常。
- `frontend/src/composables/useChat.js` 没有直接使用后端 `final_score`，而是重新汇总维度并对分数做额外处理，导致前端展示与后端结果不一致。
- `DocumentStoryView.vue` 读取字段与后端返回结构不一致，可能影响文档用户故事展示。
- README 运行命令、目录名、技术栈描述与实际项目有差异，答辩前按 README 复现可能失败。
- 缺少自动化测试目录，未发现后端接口测试、前端组件测试、端到端测试或正式测试报告。
- 项目中存在 `__pycache__`、本地 `.idea`、`.env` 等不应归档材料，工程归档整洁度不足。

### 建议补充

- 立即移除硬编码密钥，改为从环境变量读取；清理 `.env` 的公开提交记录并更换密钥。
- 统一 INVEST 评分口径：后端明确输出 0-100 或 0-60，前端只展示后端返回值，论文/PPT同步更新。
- 修复文档解析前端字段映射，确保 `user_stories` 能正常展示多条故事和验收标准。
- 按实际目录更新 README：后端路径、前端启动脚本、Docker 访问方式、环境变量名、接口路径。
- 增加最小测试集：文本需求、代码片段、需求文档、项目源码、用户故事优化、导出、历史记录，各提供输入、操作步骤、预期输出、实际输出截图。

## 6. 论文检查结果

### 与系统一致的部分

- 论文题目与项目主题一致，均围绕多智能体角色协作、用户故事生成、优化和 INVEST 评价展开。
- 可抽取文本中出现了 `FastAPI`、`StreamingResponse`、`generate_story_stream`、`rule_based_score`、`calculate_invest_score_hybrid`、`ReportLab`、`PDF` 等实现内容，与本地代码存在对应关系。
- 论文中提到的文本需求、代码、需求文档、项目源码等多来源输入，在后端和前端均能找到对应模块。
- 论文中提到的 PM、QA、Architect、Appraiser、Optimizer 等角色，大体能在 `app/agents/` 和 `agent_config_service.py` 中找到对应配置或相近实现。

### 可疑或偏空泛的部分

- 当前论文为 `.doc` 老格式，无法完整抽取正文和图片，当前材料不足以判断全部测试表、截图、流程图是否充分。
- 可抽取文本显示论文理论背景和引用较多，实际系统截图、真实输入输出和测试结果是否足够，当前材料不足以判断。
- 论文中出现 Coordinator Agent、Analysis Agent、Generation Agent、Refinement Agent、Evaluation Agent、Developer Agent 等表述，但代码中的实际角色主要是 splitter、pm、qa、architect、appraiser、code_story、document_requirement、project_story、optimizer 等，命名和职责需要统一。
- 论文/PPT中提到优先级、故事点、依赖关系等结构化字段，但当前文本生成主流程和部分导出结果没有统一体现这些字段。
- 论文若将 INVEST 评分写成稳定百分制或质量闭环，需要补充对当前评分公式、阈值和前端展示口径的修正说明。

### 建议如何修改

- 将论文实现章节按真实代码模块重写：对应到 `app/api/`、`app/services/`、`app/agents/`、`frontend/src/views/`，避免使用代码中不存在或职责不一致的角色名。
- 在系统测试章节增加真实测试表：每个核心功能至少 1 个正常用例、1 个异常/边界用例，并附输入、输出、截图或导出文件编号。
- 对 INVEST 评分公式做一次校准，论文中明确评分范围、维度权重、阈值和前后端展示方式。
- 增加部署说明截图：前端首页、接口文档、核心功能页面、一次完整生成结果、导出文件。
- 减少泛泛介绍，补充“本系统实际实现了什么、代码在哪里、输出是什么、如何验证”。

## 7. PPT检查结果

### 可保留内容

- 选题背景、研究意义、国内外研究现状、系统总体设计、多智能体协作机制、用户故事生成与评估、系统实现与测试总结的整体结构可以保留。
- 第 7 页“多来源输入、质量评估、历史管理、结果导出”等内容与系统总体功能基本一致。
- 第 9 页分层架构、第 10 页工作流程、第 14 页 FastAPI、StreamingResponse、PDF 导出等内容与本地实现有对应关系。

### 建议强化内容

- 增加系统真实截图：文本需求生成、代码逆向、需求文档解析、项目源码生成、用户故事优化、历史记录、智能体配置、导出结果。
- 第 15 页应改成真实测试结果页：列出测试用例、输入内容、输出摘要、是否通过、截图编号。
- 增加部署展示页：云端访问地址、接口文档地址、核心演示路径。
- 增加一页“核心实现对应关系”：前端页面、后端接口、服务模块、输出结果。
- 增加一页“问题与改进”：说明评分校准、测试补充、配置安全等已完成整改。

### 建议删减或避免夸大的内容

- 如果代码中没有独立 Developer Agent，就不要在 PPT 中强调 Developer Agent；可改为“架构师/测试/评价/优化等角色”。
- 如果主流程没有统一输出优先级、故事点、依赖关系，就不要把这些字段作为已实现亮点。
- 避免只说“质量提升”“可控性提高”，应给出同一输入优化前后的分数、故事文本、验收标准对比。
- PPT 目前缺少真实系统效果，不建议直接用于答辩终稿。

## 8. 部署平台检查结果

- 是否访问成功：成功。`http://47.237.103.96:8080` 返回前端入口 HTML，`/code-story` 等前端路由返回同一入口页面。
- 能看到哪些功能：通过 `/api/openapi.json` 能看到文本生成、文档解析、项目源码解析、代码逆向、用户故事优化、历史记录、智能体配置、PDF 导出等接口；`/api/agents/config` 能返回各智能体配置。
- 是否能支撑答辩展示：具备基本展示能力，至少前端和后端接口服务在线，不是单纯静态空页面。
- 还缺什么：本次未执行会调用大模型或写入历史的完整生成流程，因此还需要学生准备一套稳定演示数据和截图，证明文本需求、代码、文档、项目源码、优化、导出、历史记录能完整走通。

## 9. 是否满足毕业设计基本要求

判断：B. 基本框架已具备，但还有较明显短板，需要补强。

理由：项目有真实前后端代码、接口、部署、论文、PPT、测试输入材料，核心功能与毕业设计题目基本对应，具备继续准备答辩的基础。但当前在配置安全、评分逻辑可信度、前后端字段一致性、README 可复现性、测试证据和 PPT 展示材料方面存在明显问题。如果不整改，答辩时容易被追问“评分是否真实可靠”“系统是否能完整演示”“论文/PPT是否夸大实现”。

## 10. 最优先整改事项

1. 问题：硬编码密钥和 `.env` 入库。应补到代码/部署/README。建议移除 `config.py` 中密钥，改为环境变量读取，清理 `.env`，更换已暴露密钥，并更新部署说明。
2. 问题：INVEST 评分口径不一致。应补到代码/论文/PPT。建议统一为 0-100 或 0-60，修正阈值和公式，前端直接展示后端 `final_score`。
3. 问题：前端文档解析字段疑似不匹配。应补到代码。建议让 `DocumentStoryView.vue` 展示 `requirements[].user_stories[]` 和每条 `acceptance_criteria`。
4. 问题：README 运行路径和命令错误。应补到 README/部署。建议按真实目录写 `cd Backend/user_story_system`、`npm run serve`、`docker compose up -d --build`、`/api` 代理说明。
5. 问题：PPT 缺少系统真实截图。应补到 PPT。建议加入至少 6 张核心功能截图和 1 张导出报告截图。
6. 问题：测试材料不足。应补到论文/PPT/文档。建议新增测试用例表，覆盖文本、代码、文档、源码、优化、导出、历史记录。
7. 问题：论文角色命名与代码不完全一致。应补到论文/PPT。建议统一智能体名称和职责，不使用代码中不存在的角色。
8. 问题：论文/PPT提到的故事点、优先级、依赖关系没有统一实现。应补到论文/PPT/代码。建议要么补实现，要么降级为“设计预留/部分模块支持”。
9. 问题：部署演示仍缺完整流程证据。应补到部署/PPT。建议准备固定输入和演示脚本，提前生成可展示历史记录。
10. 问题：工程归档不整洁。应补到代码仓库。建议移除 `__pycache__`、`.idea`、本地环境文件，补 `.gitignore`。

## 11. 简短结论

当前项目可以进入答辩准备阶段，但不能直接作为最终材料提交。应先完成密钥清理、评分逻辑修正、README 校准、前后端字段修复、测试证据和 PPT 截图补强。完成这些整改后，项目整体更接近“基本满足毕业设计要求，可继续打磨后答辩”。
