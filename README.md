# 农业数据一体化平台

一个基于 Django + Vue.js 的全栈数据管理平台，集成了数据存储、数据处理、数据可视化和 AI 分析功能。

## 🚀 功能特性

### 后端功能
- 数据存储与管理
- 数据清洗与处理  
- AI 模型训练
- RESTful API 接口
- 用户认证与权限管理

### 前端功能
- 数据可视化看板
- 交互式图表
- 实时数据监控
- 响应式界面设计

## 📁 项目结构
```
Integrated-Data-Platform/
├── Integrated-Data-Platform-frontend/ # Vue.js 前端
├── Integrated-Data-Platform-backend/ # Django 后端
└── README.md # 项目说明
```

## 🛠️ 技术栈

### 后端技术
- **框架**: Django 5.2.7 + Django REST Framework
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **AI/ML**: Scikit-learn, OpenAI API
- **数据处理**: Pandas, NumPy
- **异步任务**: Celery + Redis

### 前端技术  
- **框架**: Vue 3 + TypeScript
- **UI组件**: Element Plus
- **图表**: ECharts + Vue-ECharts
- **状态管理**: Pinia
- **构建工具**: Vite

## ⚡ 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+
- Git

### 1. 克隆项目
```bash
git clone https://github.com/your-username/Integrated-Data-Platform.git
cd Integrated-Data-Platform


2. 后端设置
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

# 数据库迁移
python manage.py migrate

# 创建超级用户（可选）
python manage.py createsuperuser

# 启动开发服务器
python manage.py runserver

3. 前端设置

cd Integrated-Data-Platform-frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```
### 访问应用
🌐 **前端应用:** http://localhost:5173

🔧 **后端API:** http://localhost:8000

⚙️ **管理后台:** http://localhost:8000/admin

## 📊 功能模块

| 模块 | 功能描述 |
|------|----------|
| 用户管理 | 用户注册、登录、权限管理 |
| 数据管理 | 数据集上传、存储、查询 |
| 数据处理 | 数据清洗、转换、预处理 |
| 可视化 | 图表展示、数据看板 |
| AI分析 | 机器学习模型训练与预测 |

## 🔧 配置说明

### 环境变量
在 `Integrated-Data-Platform-backend/.env` 中配置：
```env
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=True
OPENAI_API_KEY=your-openai-key
DATABASE_URL=sqlite:///db.sqlite3 //请根据实际需求选择数据库
```

## 🤝 贡献指南

1. Fork 本项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 目前项目缺陷
1.模型训练只支持部分模型，其余模型还待开发
2.AI分析并不完善，只是提出了框架

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 联系方式

- 项目主页: [GitHub Repository](https://github.com/YycKop/Integrated-Data-Platform)
- 问题反馈: [Issues](https://github.com/YycKop/Integrated-Data-Platform/issues)
- 邮箱: 2974873045@qq.com
```
