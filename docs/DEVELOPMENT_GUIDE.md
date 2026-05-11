# Simple AI Novel App 开发指南

## 当前技术主线

- Python 3
- PyQt6
- sqlite3
- python-docx

## 运行

```powershell
cd F:\项目\simple_ai_novel_py
python main.py
```

## 测试

```powershell
python -m compileall novel_app
python -m unittest -v
```

## 健康检查

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\health_check.ps1
```

## 开发约定

- 新 UI 和新功能只接入 PyQt6 主线。
- 所有耗时 AI 调用必须进入后台线程。
- 写回正文必须绑定目标章节 id。
- 覆盖正文前必须创建快照。
- 数据库只能做增量迁移，避免破坏旧数据。
- 外部项目只做机制级学习，代码级复用必须先确认 license。

## AI 功能约定

- `writing`：续写、润色。
- `outline`：同步大纲。
- `detector`：AI 概率检测。
- `import`：智能导入分类。
- `skills`：Skills 提炼。
- `book_analysis`：全书分析。
- `review`：多智能体生成与多智能体审查。

“多智能体生成”已经替代旧的单模型按大纲生成正文入口。
