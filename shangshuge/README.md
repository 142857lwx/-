# 校园图书借阅系统

## 项目概述

这是一个完整的校园图书借阅系统，基于 Flask + Vue.js + MySQL 技术栈开发，提供以下核心功能：

### 主要功能

1. **智能精准荐书**：根据专业、选课、成绩自动推送适配书籍
2. **逾期自动提醒+线上续借**：短信/校园消息推送
3. **校园二手图书闲置互换板块**：学生间图书交易
4. **阅读时长统计、班级阅读数据可视化大屏**：数据统计分析
5. **无人自助借还扫码功能**：简化线下流程
6. **图书库存智能预警、缺书一键登记采购**：库存管理

### 用户角色

- **管理员**：系统管理、用户管理、图书管理
- **图书管理员**：图书管理、借阅管理、库存预警处理
- **学生**：图书借阅、二手交易、阅读统计、采购申请

## 技术架构

### 后端技术栈
- **框架**: Flask 2.3.3
- **数据库**: MySQL
- **认证**: JWT
- **定时任务**: APScheduler
- **二维码**: qrcode + Pillow

### 前端技术栈
- **框架**: Vue.js 2.6.14
- **UI**: Bootstrap 4.6
- **图标**: Font Awesome 5
- **图表**: Chart.js

## 项目结构

```
shangshuge/
├── backend/                    # 后端 Flask 项目
│   ├── app.py                 # 主应用入口
│   ├── config.py              # 配置文件
│   ├── models.py              # 数据库模型
│   ├── routes.py              # API 路由
│   └── requirements.txt       # 依赖列表
├── database/                   # 数据库脚本
│   └── schema.sql             # 数据库初始化脚本
├── frontend/                   # 前端 Vue.js 项目
│   ├── index.html             # 主页面
│   └── app.js                 # Vue 应用逻辑
└── README.md                  # 项目说明
```

## 快速开始

### 环境要求

- Python 3.8+
- MySQL 5.7+
- Node.js (可选，用于前端开发)

### 后端部署

1. **安装依赖**
```bash
cd backend
pip install -r requirements.txt
```

2. **配置数据库**
```bash
# 创建数据库
mysql -u root -p
CREATE DATABASE library_system DEFAULT CHARACTER SET utf8mb4;
```

3. **初始化数据**
```bash
mysql -u root -p library_system < database/schema.sql
```

4. **修改配置**

编辑 `backend/config.py`，修改数据库连接配置：
```python
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:your_password@localhost/library_system'
```

5. **启动服务**
```bash
cd backend
python app.py
```

服务将在 http://localhost:5000 启动

### 前端部署

直接使用浏览器打开 `frontend/index.html`，或使用本地服务器：

```bash
cd frontend
python -m http.server 8080
```

前端页面将在 http://localhost:8080 访问

## API 接口

### 认证接口
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/login | 用户登录 |
| POST | /api/register | 用户注册 |
| GET | /api/user | 获取用户信息 |

### 图书管理
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/books | 获取图书列表 |
| POST | /api/books | 添加图书（管理员） |
| PUT | /api/books/:id | 更新图书（管理员） |
| DELETE | /api/books/:id | 删除图书（管理员） |
| GET | /api/books/:id/qr | 获取图书二维码 |

### 借阅管理
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/borrow | 借阅图书 |
| POST | /api/borrow/:id/renew | 续借图书 |
| POST | /api/borrow/:id/return | 归还图书 |
| POST | /api/borrow/scan | 扫码借阅 |
| POST | /api/borrow/scan/return | 扫码归还 |

### 智能推荐
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/recommendations | 获取推荐列表 |
| POST | /api/recommendations/generate | 生成推荐 |

### 二手图书
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/second_hand | 获取二手图书列表 |
| POST | /api/second_hand | 发布二手图书 |
| POST | /api/second_hand/:id/buy | 购买二手图书 |

### 阅读统计
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/reading | 添加阅读记录 |
| GET | /api/reading/stats | 获取阅读统计 |

### 数据统计
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/stats/dashboard | 数据看板 |
| GET | /api/stats/class | 班级统计 |

### 库存预警
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/stock_alerts | 获取库存预警 |
| POST | /api/stock_alerts/:id/resolve | 处理预警 |

### 采购申请
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/book_requests | 获取采购申请 |
| POST | /api/book_requests | 提交采购申请 |
| PUT | /api/book_requests/:id | 更新申请状态 |

### 通知管理
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/notifications | 获取通知列表 |
| POST | /api/notifications/read_all | 全部标为已读 |

## 测试账户

| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin | password | 管理员 |
| librarian | password | 图书管理员 |
| student1 | password | 学生（张三） |
| student2 | password | 学生（李四） |
| student3 | password | 学生（王五） |

## 数据库表结构

### 核心表

1. **users** - 用户表
2. **books** - 图书表
3. **borrow_records** - 借阅记录表
4. **courses** - 课程表
5. **user_courses** - 用户选课表
6. **recommendations** - 推荐表
7. **second_hand_books** - 二手图书表
8. **second_hand_transactions** - 二手交易表
9. **reading_records** - 阅读记录表
10. **stock_alerts** - 库存预警表
11. **book_requests** - 采购申请表
12. **notifications** - 通知表

## 功能特点

### 智能推荐算法
- 专业匹配（30分）：根据用户专业与图书分类匹配
- 课程匹配（20分）：根据用户选课与图书关键词匹配
- 借阅记录（15分）：优先推荐用户曾借阅过的相关图书
- 库存状态（10分）：优先推荐有库存的图书

### 定时任务
- 每天 8:00 检查逾期图书并发送提醒
- 每天 9:00 检查库存预警

### 借阅规则
- 每次最多借阅 5 本
- 借阅期限 30 天
- 最多续借 2 次
- 逾期每天罚款 0.5 元

## License

MIT License