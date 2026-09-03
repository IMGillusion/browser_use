# browser_use

**浏览器自动化**子项目，基于 [browser-use](https://github.com/browser-use/browser-use) 库驱动
headless Chromium。两种用法：

1. **脚本式**：直接控制页面（打开、读标题/URL、截图），确定性强，不依赖 LLM。
2. **自主 Agent**（`--agent`）：挂一个 LLM 跑闭环——给个自然语言任务，Agent 自己
   点、搜、读页面、回话。

按需子项目（非常驻），要用的时候跑 `smoke_test.py`。

## 文件

| 文件 | 职责 |
|---|---|
| `smoke_test.py` | 冒烟测试 / 运行入口。默认 headless 开百度验证「能起、能联网、能读页」；加 `--agent` 跑一次 LLM 闭环 |
| `config.yaml` | 配置（headless / 视口 / 扩展开关 / LLM 端点） |

## 配置

`config.yaml`：

| 键 | 默认 | 说明 |
|---|---|---|
| `browser.headless` | true | 无界面模式（服务器环境） |
| `browser.viewport` | [1920, 1200] | 视口 |
| `browser.disable_default_extensions` | 1 | **关键**：默认扩展（uBlock 等）启动时要联网下载，慢/超时会卡死启动。设 1 跳过 |
| `llm.model` | qwen3.8-27b | Agent 用的模型 |
| `llm.base_url` | http://127.0.0.1:9000/v1 | **占位，换成你自己的 LLM 端点**（OpenAI 兼容 /v1） |
| `llm.api_key` | sk-mykey | 端点的 key |
| `smoke_url` | https://www.baidu.com | 冒烟测试打开的验证页 |

LLM 三项均可用环境变量覆盖（优先级更高）：`BU_LLM_MODEL` / `BU_LLM_BASE` / `BU_LLM_KEY`。

## 用法

```bash
# 装依赖（uv venv）
uv venv .venv --python 3.10
uv pip install --python .venv browser-use playwright
.venv/bin/python -m playwright install chromium   # 拉浏览器内核

# 冒烟：验证浏览器能起
.venv/bin/python smoke_test.py

# 冒烟 + LLM Agent 闭环（要配好 llm 端点）
BU_LLM_BASE=http://你的LLM:9000/v1 BU_LLM_KEY=xxx \
  .venv/bin/python smoke_test.py --agent
```

`SMOKE PASS` 即通过。

## 依赖

- Python 3.10+
- `browser-use`、`playwright`（需 `playwright install chromium`）
- Agent 模式需要一个 OpenAI 兼容的 LLM 端点

## 已知坑

- **默认扩展卡启动**：browser-use 自带 uBlock 等扩展，启动时要联网从 CDN 拉，
  内网/慢网会卡死整个浏览器启动。`BROWSER_USE_DISABLE_EXTENSIONS=1` 跳过
  （见 config，需在 import browser_use 之前设，smoke_test.py 已处理）。
- `new_page(url)` 返回的 Page 才是你打开的那个标签；用 session 级的
  `get_current_page_*` 会指到默认的 about:blank 页，读不到目标页。
- 截图返回 base64，要自己 `b64decode` 落盘。

## 赞助

如果这个项目对你有用，欢迎赞助支持一下，请我喝杯奶茶：

![sponsor](assets/sponsor.jpg)

—— 幻日出品
