# 商品价格查询系统

基于企业微信智能表格API的商品价格查询系统，通过企微自建应用搭建查询表单，实时查询数据并展示报价。

## 项目特点

- 🚀 前端：HTML5 + CSS3 + JavaScript（响应式设计，支持PC和移动端）
- 🔧 后端：Python + Flask（RESTful API）
- 📊 数据源：企业微信智能表格（实时查询，无缓存）
- 🔒 安全：敏感字段后端过滤，access\_token自动管理
- 🎨 界面：卡片式展示，表格化参数，简洁美观

## 目录结构

```
├── .env.example          # 配置文件模板
├── backend/              # 后端代码
│   ├── app.py            # Flask应用入口
│   ├── utils/            # 工具函数
│   │   ├── access_token.py  # access_token管理
│   │   ├── api_client.py    # API调用封装
│   │   └── config.py        # 配置管理
│   └── routes/           # 路由
│       └── query.py      # 查询接口
├── frontend/             # 前端代码
│   ├── index.html        # 主页面
│   ├── css/style.css     # 样式文件
│   └── js/               # 脚本文件
│       ├── main.js       # 主脚本
│       └── api.js        # API调用
└── README.md             # 项目说明
```

## 配置方式

### 1. 创建配置文件

```bash
# 复制配置模板
cp .env.example .env
```

### 2. 编辑配置文件

编辑 `.env` 文件，填入企业微信和智能表格的配置信息：

```ini
# 企业微信配置
corpid=YOUR_CORPID
corpsecret=YOUR_CORPSECRET

# 智能表格配置
docid=YOUR_DOCID
sheet_id=YOUR_SHEET_ID

# Flask配置（开发环境设为True，生产环境设为False）
FLASK_DEBUG=False

# CORS配置（可选，多个域名用逗号分隔）
# CORS_ORIGINS=https://your-domain.com,https://another-domain.com
```

### 3. 获取配置参数

1. **corpid 和 corpsecret**：在企业微信管理后台 -> 应用管理 -> 自建应用中获取
2. **docid**：在企业微信智能表格中创建表格后，从URL中获取
3. **sheet\_id**：在智能表格中获取工作表ID

## 启动方式

### 一键启动（推荐）

项目根目录提供了 `start.py` 脚本，可以一键启动前后端服务：

```bash
# 在项目根目录执行
python start.py
```

启动后会显示：
- 📱 前端访问地址（默认端口8000）
- 🔧 后端API地址（默认端口5000）
- 自动在浏览器中打开查询界面

按 `Ctrl+C` 可停止所有服务。

### 开发环境（分别启动）

#### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

#### 2. 启动后端服务

```bash
# Windows
python -m backend.app

# Linux/Mac
python3 -m backend.app
```

后端服务将在 `http://localhost:5000` 启动。

#### 3. 启动前端服务

```bash
# 需要安装http-server
npm install -g http-server

cd frontend
http-server -p 8080
```

前端页面将在 `http://localhost:8080` 启动。

#### 4. 访问系统

在浏览器中打开 `http://localhost:8080` 即可访问查询界面。

### 生产环境

#### 1. 使用Gunicorn启动后端

```bash
# 安装gunicorn
pip install gunicorn

# 启动服务（4个工作进程）
cd backend
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

#### 2. 配置Nginx（可选）

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /path/to/frontend;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # 后端API代理
    location /api/ {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### 3. 部署前端到企业微信自建应用

将 `frontend/` 目录下的所有文件部署到企业微信自建应用，或配置为外部链接访问。

## 部署方式

### 方案一：单服务器部署（推荐）

1. 将项目代码上传到服务器
2. 配置 `.env` 文件
3. 安装Python依赖：`pip install -r requirements.txt`
4. 使用Gunicorn启动后端服务
5. 配置Nginx反向代理
6. 配置企业微信自建应用指向后端API地址

### 方案二：前后端分离部署

**前端部署：**

- 部署到企业微信自建应用
- 或部署到静态文件服务器（如Nginx、CDN）
- 修改 `frontend/js/api.js` 中的 `baseURL` 为后端API地址

**后端部署：**

- 部署到企业服务器
- 使用Gunicorn + Nginx部署
- 配置CORS允许前端域名访问

### 环境变量配置（可选）

生产环境建议使用环境变量而非 `.env` 文件：

```bash
export corpid=YOUR_CORPID
export corpsecret=YOUR_CORPSECRET
export docid=YOUR_DOCID
export sheet_id=YOUR_SHEET_ID
export FLASK_DEBUG=False
export CORS_ORIGINS=https://your-domain.com
```

## 使用说明

1. 打开查询界面
2. 输入产品名（可选）
3. 选择发电机组功率、柴油发动机型号、发电机型号（可选）
4. 点击"查询"按钮
5. 系统实时从企业微信智能表格获取数据并展示报价

## 查询字段

- **产品名**：文本框输入，支持模糊查询
- **发电机组功率(KVA/KW)**：下拉菜单选择
- **柴油发动机型号**：下拉菜单选择
- **发电机型号**：下拉菜单选择

## 注意事项

1. 确保 `.env` 文件中的配置正确
2. 确保企业微信智能表格已正确创建并包含数据
3. 确保服务器能访问企业微信API（需要外网访问权限）
4. 价格数据仅对内部员工和管理层开放
5. 所有查询实时从智能表格读取，无本地缓存

##
