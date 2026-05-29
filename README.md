# 北京交通大学就餐仿真系统 — 源代码说明

## 一、项目概述

本项目为北京交通大学食堂就餐仿真系统，采用 B/S 前后端分离架构。前端包含学生端、后厨端、保洁端、管理员端四个 Vue 3 应用，后端使用 Flask 提供 RESTful API，数据库使用 SQLite，预测模块使用 XGBoost 算法。

## 二、目录结构

```
canteen/
├── 启动服务.py              # 一键启动脚本
├── backend/                 # 后端（Flask + SQLite）
│   ├── app.py               # 应用入口
│   ├── config.py            # 配置文件
│   ├── models.py            # 数据库模型定义
│   ├── init_db.py           # 数据库初始化脚本
│   ├── requirements.txt     # Python 依赖
│   ├── routes/              # API 路由
│   │   ├── auth.py          # 认证接口（登录/退出）
│   │   ├── orders.py        # 学生点餐接口
│   │   ├── admin.py         # 管理员后台接口
│   │   ├── seats.py         # 座位查询与释放接口
│   │   ├── kitchen.py       # 后厨业务接口
│   │   └── prediction.py    # 预测触发接口
│   ├── utils/               # 工具模块
│   │   ├── predict_algo.py  # XGBoost 预测算法
│   │   └── dispatch_algo.py # 窗口调度算法
│   ├── data/                # 数据与模型文件
│   │   ├── manual_sales_template_*.csv  # 训练样本
│   │   ├── xgb_dish_sales_model.json    # 训练好的模型
│   │   └── xgb_dish_sales_model.meta.json  # 模型元信息
│   └── static/images/       # 菜品图片资源
├── student-app/             # 学生端（Vue 3 + Vite，端口 5173）
│   ├── src/views/
│   │   ├── LoginView.vue         # 学生登录
│   │   ├── MenuView.vue          # 今日菜单与下单
│   │   ├── PartySizeView.vue     # 就餐人数选择
│   │   └── OrderResultView.vue   # 订单结果展示
│   └── src/api/axios.js          # Axios 请求配置
├── kitchen-app/             # 后厨端（Vue 3 + Vite，端口 5174）
│   ├── src/views/
│   │   ├── WindowSelectView.vue  # 窗口选择
│   │   └── OrderListView.vue     # 订单列表与出餐
│   └── src/api/axios.js
├── cleaner-app/             # 保洁端（Vue 3 + Vite，端口 5175）
│   ├── src/views/
│   │   └── SeatView.vue          # 座位状态查看与释放
│   └── src/api/axios.js
└── admin-app/               # 管理员端（Vue 3 + Vite，端口 5176）
    ├── src/views/
    │   ├── LoginView.vue         # 管理员登录
    │   ├── DishesView.vue        # 菜品管理
    │   ├── WindowsView.vue       # 窗口管理
    │   ├── SeatGroupsView.vue    # 座位组管理
    │   ├── SeatsView.vue         # 座位管理
    │   ├── StudentsView.vue      # 学生管理
    │   ├── PredictionView.vue    # 预测与调整
    │   ├── ReportsView.vue       # 数据报表
    │   └── ConfigView.vue        # 系统配置
    └── src/api/axios.js
```

## 三、后端说明

**app.py** — 应用入口。创建 Flask 应用、加载配置、注册蓝图路由、配置 CORS、初始化数据库，并统一处理 HTTP 错误。

**config.py** — 配置文件。定义 Flask 密钥、SQLite 数据库路径、调度相关配置。

**models.py** — 数据库模型定义。包含以下表：

| 表名 | 说明 |
|------|------|
| Student | 学生信息（学号、姓名、密码哈希） |
| Window | 窗口信息（名称、编号、在线状态） |
| SeatGroup | 座位组（名称、容量） |
| Seat | 座位（编号、所属组、占用状态） |
| Dish | 菜品（名称、价格、图片、上下架状态） |
| DailyMenu | 每日菜单（菜品、窗口、日期、库存、售罄状态） |
| Order | 订单（学生、窗口、人数、完成状态、时间） |
| OrderDish | 订单菜品明细（菜品、数量、价格） |
| OrderSeat | 订单座位关联（订单、座位） |
| DishPrediction | 菜品预测（菜品、日期、预测量、调整量） |
| SystemConfig | 系统配置（键值对） |
| AdminUser | 管理员账号（用户名、密码哈希） |

**init_db.py** — 数据库初始化脚本。创建所有数据表，写入初始数据（管理员账号、窗口、座位、菜品、学生账号）。

**routes/auth.py** — 认证接口。学生登录、管理员登录、退出登录，使用 Flask Session 保存登录态。

**routes/orders.py** — 学生点餐接口。创建订单（含库存扣减与座位分配）、查询订单详情、查询今日菜单。

**routes/admin.py** — 管理员后台接口。菜品/窗口/座位/学生 CRUD、每日菜单管理、预测查看与调整、订单处理与完成、报表统计（日订单/窗口出餐/座位使用率）、系统配置。

**routes/seats.py** — 座位接口。按座位组查询座位占用情况、手动释放座位。

**routes/kitchen.py** — 后厨接口。查询窗口列表、查询待处理订单、完成订单（出餐）。

**routes/prediction.py** — 预测触发接口。管理员手动触发模型训练、手动触发预测入库。

**utils/predict_algo.py** — XGBoost 预测算法。包含训练函数（train_model）、预测函数（predict_and_upsert）、特征构建、CLI 入口。支持从 CSV 训练样本训练模型，并根据日期、天气、窗口在线状态等特征预测各菜品销量，自动写入 DishPrediction 和 DailyMenu。

**utils/dispatch_algo.py** — 窗口调度算法。根据窗口负载情况分配订单到合适的窗口。

**data/** — 数据目录。包含手动编写的训练样本 CSV（约 30 天数据）、训练好的 XGBoost 模型文件（.json）、模型元信息（.meta.json）。

**static/images/** — 菜品展示图片，供前端菜单页面渲染使用。

## 四、前端说明

四个前端应用均使用 Vue 3 + Vite + Axios 构建，结构一致：
- `src/views/` — 页面视图
- `src/api/axios.js` — 统一请求配置（baseURL 指向 http://localhost:5000，withCredentials 开启以支持 Session）
- `src/router/index.js` — 路由配置
- `vite.config.js` — 端口与代理配置

**学生端（端口 5173）**：学生刷卡登录 → 查看今日菜单 → 选择就餐人数 → 下单 → 查看订单结果与取餐窗口。

**后厨端（端口 5174）**：选择窗口 → 查看该窗口待处理订单 → 完成出餐。

**保洁端（端口 5175）**：查看各区域座位占用状态 → 释放已离开学生的座位。

**管理员端（端口 5176）**：登录 → 菜品/窗口/座位/学生管理 → 手动预测 → 调整预测量 → 查看每日菜单 → 查看数据报表 → 系统配置。

## 五、启动方式

**环境要求：** Python 3.10+、Node.js 18+

**第一步：安装后端依赖**
```bash
cd backend
pip install -r requirements.txt
```

**第二步：初始化数据库**
```bash
cd backend
python init_db.py
```

**第三步：安装前端依赖**
```bash
cd student-app && npm install && cd ..
cd kitchen-app && npm install && cd ..
cd cleaner-app && npm install && cd ..
cd admin-app && npm install && cd ..
```

**第四步：一键启动**
```bash
python 启动服务.py
```

启动脚本会自动清理端口残留、启动后端（5000）和四个前端（5173/5174/5175/5176），并打开浏览器。

**手动启动各服务：**
```bash
# 后端
cd backend ; python app.py

# 学生端
cd student-app ; npx vite --port 5173 --host

# 后厨端
cd kitchen-app ; npx vite --port 5174 --host

# 保洁端
cd cleaner-app ; npx vite --port 5175 --host

# 管理员端
cd admin-app ; npx vite --port 5176 --host
```

**默认账号：**
- 管理员：admin / admin123
- 学生：24281143（王禹凡）、24281135（李佳睿）、24281170（任笑语），默认密码 wyfnb ljrnb rxynb
