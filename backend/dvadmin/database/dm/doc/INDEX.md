# 达梦数据库集成文档索引

欢迎使用达梦数据库集成文档！

## 📚 文档导航

### 1. [README.md](README.md) - 完整文档
**适合**：需要全面了解达梦数据库集成的开发者

**包含内容**：
- 📋 概述和架构
- ⚙️ 配置说明
- 🔀 数据库路由详解
- 🗄️ Schema 管理
- 📦 迁移管理
- ❓ 常见问题
- ✨ 最佳实践

**阅读时间**：15-20分钟

---

### 2. [QUICKSTART.md](QUICKSTART.md) - 快速入门
**适合**：需要快速上手的开发者

**包含内容**：
- ⚡ 5分钟快速配置
- 🚀 基本使用示例
- 🔧 常用命令
- 🐛 快速故障排查

**阅读时间**：5分钟

---

### 3. [FAQ.md](FAQ.md) - 常见问题
**适合**：遇到具体问题需要解决的开发者

**包含内容**：
- ❓ 18+ 常见问题解答
- 🔍 详细的错误排查
- 💡 调试技巧
- 📖 代码示例

**阅读时间**：按需查阅

---

## 🚀 快速链接

### 新手入门
1. 先读 [QUICKSTART.md](QUICKSTART.md) 快速上手
2. 遇到问题查 [FAQ.md](FAQ.md)
3. 需要深入了解再读 [README.md](README.md)

### 常见任务

#### 配置新模块路由
```python
# backend/dvadmin/utils/db_router.py
app_db_map = {
    'your_app': 'dm',  # 使用 app_label，不是完整路径
}
```
👉 详见 [README.md - 数据库路由](README.md#数据库路由)

#### 执行迁移
```bash
python manage.py migrate your_app --database=dm
```
👉 详见 [README.md - 迁移管理](README.md#迁移管理)

#### 验证路由
```python
from your_app.models import YourModel
print(YourModel._meta.app_label)  # 查看 app_label
```
👉 详见 [FAQ.md - Q2](FAQ.md#q2-如何知道应用的-app_label-是什么)

#### 解决跨数据库关联
👉 详见 [FAQ.md - Q5](FAQ.md#q5-报错-cannot-assign--prevents-this-relation)

#### Schema 问题
👉 详见 [FAQ.md - Q10-Q12](FAQ.md#schema问题)

---

## 📌 核心概念速查

### app_label 是什么？
Django 从 `apps.py` 的 `name` 中提取的最后一部分：
```python
name = "dvadmin_twodev.basedata.park"
# ↓
app_label = "park"  # 用这个配置路由
```

### 为什么不用完整路径？
因为路由器使用 `model._meta.app_label`，它是自动提取的简称。

### 如何验证配置？
```python
from your_app.models import YourModel
from dvadmin.utils.db_router import DatabaseRouter
router = DatabaseRouter()
print(router.db_for_read(YourModel))  # 应该输出 'dm'
```

---

## 🛠️ 代码文件位置

| 文件 | 说明 |
|------|------|
| `backend/application/settings.py` | 数据库配置 |
| `backend/dvadmin/utils/db_router.py` | 路由器配置 |
| `backend/dvadmin/database/dm/base.py` | 达梦数据库连接 |
| `backend/dvadmin/database/dm/compiler.py` | SQL 编译器 |
| `backend/dvadmin/database/dm/operations.py` | 数据库操作 |

---

## 🐛 问题排查流程

```
遇到问题
    ↓
查看错误信息
    ↓
在 FAQ.md 搜索关键词
    ↓
    找到 → 按文档解决
    ↓
    未找到 → 查看 README.md 相关章节
    ↓
    仍未解决 → 开启 DEBUG 日志查看详细信息
    ↓
    联系开发团队
```

---

## 📞 获取帮助

1. **查阅文档**：先查看本目录的文档
2. **查看日志**：开启 Django DEBUG 模式
3. **测试连接**：使用 `python manage.py shell` 测试
4. **查看源码**：检查相关 Python 文件
5. **联系团队**：提供详细的错误信息和环境信息

---

## 📝 文档维护

- **创建日期**：2025-10-27
- **最后更新**：2025-10-27
- **维护者**：王晨
- **版本**：1.0.0

---

## ⭐ 文档评价

如果这些文档对您有帮助，请给个 Star ⭐

如果发现文档有误或需要补充，欢迎提 Issue 或 PR。

---

**Happy Coding!** 🎉

