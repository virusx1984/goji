<!-- README.md -->
# Goji 制造协同规划系统

Goji 是一个强大且高度可扩展的、基于 API 的制造协同规划系统（MES/ERP）。它专门为高密度连接板（HDI PCB）等复杂制造业的场景设计，提供从用户权限、组织架构、主数据、生产流程到客户需求的全链路管理能力。

## ✨ 核心特性

  * **精细的权限管理 (RBAC)**：内置完整且灵活的用户、角色、权限管理体系。通过自定义的装饰器为 API 提供精细到单个操作的访问控制。
  * **动态前端菜单**：提供 `/api/menus` 接口，可根据当前登录用户的权限动态生成前端UI的菜单树，实现前端界面的权限自适应。
  * \-**模块化的应用架构**：采用 Flask Blueprints 设计，将不同业务领域（如用户管理、工艺流程、客户需求）的代码清晰地分离，易于维护和扩展。
  * **深度的制造过程建模**：
      * **工艺路线 (Routing)**：支持定义产品制造的每一个工序。
      * **物料清单 (BOM)**：能够关联到具体工序，并精细定义用量、基数和损耗率。
      * **工作中心与产能**：可定义生产资源（设备、产线）及其有效产出率（OEE）。
  * **一键数据填充**：项目包含一个强大的 `flask seed` 命令，能够一键清空并填充一套完整、真实的演示数据，极大地方便了开发、测试和功能演示。
  * **现代化的技术栈**：使用 Flask, SQLAlchemy, JWT 等业界主流技术，保证了项目的稳定性和先进性。

## 🛠️ 技术栈

  * **后端框架**: Flask
  * **数据库**: PostgreSQL
  * **ORM 与迁移**: SQLAlchemy, Flask-Migrate (Alembic)
  * **API 认证**: JSON Web Tokens (Flask-JWT-Extended)
  * **密码安全**: Bcrypt (Flask-Bcrypt)
  * **数据序列化与校验**: Marshmallow (Flask-Marshmallow)

## 🚀 快速开始

请遵循以下步骤来在本地环境中设置和运行 Goji 项目。

### 1\. 环境准备

```bash
# 克隆项目仓库
git clone <your-repository-url>
cd goji

# 创建并激活 Python 虚拟环境 (推荐)
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate  # Windows
```

### 2\. 安装依赖

```bash
pip install -r requirements.txt
```

*(注意: 请确保项目中已包含 `requirements.txt` 文件)*

### 3\. 配置环境变量

项目通过环境变量加载数据库等敏感配置。请创建一个 `.env` 文件，并参考 `config.py` 设置以下变量：

```.env
FLASK_APP=run.py
FLASK_CONFIG=development

# PostgreSQL 数据库连接信息
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=gojidb
```

### 4\. 数据库迁移

此命令将根据 models 定义创建或更新数据库表结构。

```bash
flask db upgrade
```

### 5\. 填充示例数据 (强烈推荐)

运行 `seed` 命令来填充一套完整的演示数据，这将帮助你快速了解系统功能。

```bash
flask seed
```

成功后，你可以使用以下示例账户登录：

  * **管理员**: `admin` / `supersecret`
  * **计划员**: `planner1` / `password123`

### 6\. 启动应用

```bash
flask run
```

现在，Goji API 服务已在本地运行，你可以通过 Postman 或其他 API 工具进行访问和测试。
