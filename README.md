# 📊 数据一体化平台

> 基于 Django + Vue.js 的全栈数据管理平台，集成了数据存储、智能处理、可视化分析和 AI 预测功能，为现代农业提供全方位的数据解决方案。

## ✨ 核心特性

### 🗄️ 数据管理
- **多源数据集成** - 支持数据库、文件、API等多种数据源
- **智能数据清洗** - 自动化数据预处理和质量控制
- **统一数据存储** - 安全可靠的数据存储与管理

### 📊 可视化分析
- **交互式图表** - 丰富的可视化组件和图表类型
- **实时数据看板** - 动态监控数据指标
- **智能报表生成** - 自动化生成数据分析报告

### 🤖 AI 智能分析
- **机器学习模型** - 支持多种预测模型
- **智能决策支持** - 基于数据的智能分析与建议
- **预测分析** - 产品产量、价格趋势预测

### 🔐 系统管理
- **多用户权限** - 完善的用户角色和权限管理
- **操作审计** - 完整的操作日志和审计追踪
- **数据安全** - 多层次的数据安全保障

## 🏗️ 系统架构

```
🌐 前端展示层 (Vue 3 + Element Plus)
    │
🔄 API网关层 (RESTful API)
    │
⚙️ 业务逻辑层 (Django + DRF)
    │
🗃️ 数据服务层 (数据处理 + AI分析)
    │
💾 数据存储层 (SQLite/PostgreSQL + Redis)
```

## 🛠️ 技术栈

### 后端技术
| 技术 | 用途 | 版本 |
|------|------|------|
| **Django** | Web框架 | 5.2.7 |
| **Django REST Framework** | API开发 | 3.15+ |
| **Pandas** | 数据处理 | 2.0+ |
| **Scikit-learn** | 机器学习 | 1.3+ |
| **Celery** | 异步任务 | 5.3+ |
| **PostgreSQL** | 数据库 | 14+ |

### 前端技术
| 技术 | 用途 | 版本 |
|------|------|------|
| **Vue 3** | 前端框架 | 3.3+ |
| **TypeScript** | 类型安全 | 5.0+ |
| **Element Plus** | UI组件库 | 2.3+ |
| **ECharts** | 数据可视化 | 5.4+ |
| **Pinia** | 状态管理 | 2.1+ |
| **Vite** | 构建工具 | 4.4+ |

## 🚀 快速开始

### 环境要求
- **Python**: 3.8 或更高版本
- **Node.js**: 16.0 或更高版本  
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **内存**: 至少 4GB RAM

### 1️⃣ 克隆项目
```bash
git clone https://github.com/YycKop/Integrated-Data-Platform.git
cd Integrated-Data-Platform
```

### 2️⃣ 后端服务部署

```bash
# 进入后端目录
cd Integrated-Data-Platform-backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 环境配置
cp .env.example .env
# 编辑 .env 文件配置您的环境变量

# 数据库初始化
python manage.py migrate
python manage.py createsuperuser

# 启动开发服务器
python manage.py runserver
```

### 3️⃣ 前端服务部署

```bash
# 进入前端目录
cd Integrated-Data-Platform-frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

## ⚙️ 系统配置

### 环境变量配置
在 `Integrated-Data-Platform-backend/.env` 文件中配置：

```env
# Django 基础配置
DJANGO_SECRET_KEY=your-secure-secret-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# 数据库配置
DATABASE_URL=sqlite:///db.sqlite3
# 生产环境推荐使用 PostgreSQL
# DATABASE_URL=postgresql://user:password@localhost:5432/agriculture_data

# AI 服务配置
OPENAI_API_KEY=your-openai-api-key

# 缓存配置
REDIS_URL=redis://localhost:6379/0
```

### 访问地址
| 服务 | 地址 | 说明 |
|------|------|------|
| 🌐 **前端应用** | http://localhost:5173 | 用户操作界面 |
| 🔧 **后端API** | http://localhost:8000 | REST API 接口 |
| ⚙️ **管理后台** | http://localhost:8000/admin | 系统管理界面 |
| 📊 **API文档** | http://localhost:8000/api/docs | 接口文档 |

## 📸 功能展示

### 🔐 用户认证
![登录页面](images/登录页.png)
*安全可靠的用户登录系统*

### 🏠 系统主页
![主页1](images/主页1.png)
![主页2](images/主页2.png)  
*直观的数据概览和快速导航*

### 🧑‍💻 个人信息页
![个人信息页](images/个人信息页.png)
*用户个人信息展示和管理*

### 📁 数据管理
![数据源页](images/数据源页.png)
![数据集页](images/数据集页.png)
*统一的数据源和数据集管理*

### 🔄 数据处理
![数据处理页](images/数据处理页.png)
*可视化的数据流程处理*

### 📈 数据可视化
![数据可视化页](images/数据可视化页.png)
*丰富的图表和可视化组件*

### 🎯 数据看板
![数据看板页](images/数据看板页.png)
*可定制的数据监控看板*

### 🤖 AI 智能分析
![AI模型](images/AI模型页.png)
![智能分析页](images/智能分析页.png)
*机器学习模型训练和智能分析*

## 📋 功能模块详情

| 模块 | 图标 | 功能描述 |
|------|------|----------|
| **用户管理** | 👥 | 用户注册、登录、权限管理、角色分配 |
| **数据管理** | 📊 | 多源数据接入、数据存储、数据查询 |
| **数据处理** | ⚙️ | 数据清洗、转换、预处理、质量检查 |
| **可视化** | 📈 | 图表展示、数据看板、报表生成 |
| **AI分析** | 🤖 | 模型训练、预测分析、智能决策 |

## 🗺️ 开发路线图

### ✅ 已完成功能
- [x] 基础框架搭建
- [x] 用户认证系统
- [x] 数据管理模块
- [x] 基础可视化功能
- [x] AI模型基础框架

### 🔄 开发中功能
- [ ] 更多机器学习模型支持
- [ ] 实时数据流处理
- [ ] 移动端适配
- [ ] 第三方数据源集成

### 📅 计划功能
- [ ] 多语言国际化
- [ ] 云端部署方案

## 👾 已知问题与限制

### 当前版本限制
- **模型支持有限**: 目前仅支持部分基础机器学习模型
- **AI分析功能**: 前端框架已搭建，功能待完善
- **性能优化**: 大数据量处理性能有待优化

### 解决方案
我们正在积极开发以下改进：
- 扩展更多专用AI模型
- 优化数据处理管道性能
- 增强系统的可扩展性

## 🤝 参与贡献

我们欢迎任何形式的贡献！请参阅我们的贡献指南：

### 贡献流程
1. **Fork 本项目**
2. **创建功能分支** (`git checkout -b feature/AmazingFeature`)
3. **提交更改** (`git commit -m 'Add some AmazingFeature'`)
4. **推送到分支** (`git push origin feature/AmazingFeature`)
5. **开启 Pull Request**

### 开发规范
- 遵循 PEP 8 (Python) 和 ESLint (JavaScript) 代码规范
- 提交信息使用约定式提交格式
- 新功能请添加相应的测试用例

## 📄 许可证

本项目采用 **MIT 许可证** - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系我们

如果您有任何问题或建议，欢迎通过以下方式联系我们：

- **项目主页**: [GitHub Repository](https://github.com/YycKop/Integrated-Data-Platform)
- **问题反馈**: [Issues](https://github.com/YycKop/Integrated-Data-Platform/issues)
- **邮箱联系**: 2974873045@qq.com
- **技术讨论**: 欢迎提交 Issue 或 Pull Request

---

**如果这个项目对您有帮助，请给个 ⭐️ 支持一下！**

![img.png](img.png)


