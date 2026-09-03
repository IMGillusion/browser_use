#!/usr/bin/env python3
"""browser_use 子项目冒烟测试

默认（无参数）：headless chromium 打开百度，读标题/URL、截图落地——
  证明浏览器能起、能连网、能读页面。这是最核心的"冒烟"，确定性强、不依赖 LLM。
加 --agent：额外跑一次极简 Agent 任务（打开百度并描述页面），
  证明 LLM + 浏览器的闭环能跑通（走 litellm 代理的 qwen3.8-27b）。

环境变量（--agent 用）：
  BU_LLM_MODEL  默认 qwen3.8-27b
  BU_LLM_BASE   默认 http://127.0.0.1:9000/v1
  BU_LLM_KEY    默认 sk-mykey
"""
import argparse
import asyncio
import os
import sys
from pathlib import Path

# 默认禁用 browser_use 自带的默认扩展(uBlock 等)：它们启动时会联网下载，
# 这台机器拉 github CDN 很慢/会超时，卡住整个启动。需要广告拦截时可设
# BROWSER_USE_DISABLE_EXTENSIONS=0 覆盖。必须在 import browser_use 之前设。
os.environ.setdefault("BROWSER_USE_DISABLE_EXTENSIONS", "1")

from browser_use.browser.session import BrowserSession

BAIDU = "https://www.baidu.com"
HERE = Path(__file__).parent


async def browser_smoke() -> bool:
    """headless chromium 打开百度，读标题/URL，截图落地。"""
    import base64
    session = BrowserSession(headless=True)
    await session.start()
    try:
        # new_page 返回的 Page 就是百度那个标签；用它读，
        # 别用 session 级的 get_current_page_*（那会指到默认 about:blank 页）
        page = await session.new_page(BAIDU)
        await asyncio.sleep(4)  # 等页面渲染完
        title = await page.get_title()
        url = await page.get_url()
        shot_path = HERE / "smoke_screenshot.png"
        b64 = await page.screenshot()  # base64 编码
        png = base64.b64decode(b64)
        shot_path.write_bytes(png)
        print(f"[browser] title={title!r}")
        print(f"[browser] url={url!r}")
        print(f"[browser] screenshot={shot_path} ({len(png)} bytes)")
        opened = "baidu" in (url or "").lower() or "百度" in (title or "")
        if not opened:
            print("[browser] 没打开到百度", file=sys.stderr)
            return False
        return True
    finally:
        await session.stop()


async def agent_smoke() -> bool:
    """跑一次极简 Agent 任务，验证 LLM + 浏览器闭环。"""
    from browser_use.agent.service import Agent
    from browser_use.llm import ChatOpenAI

    llm = ChatOpenAI(
        model=os.environ.get("BU_LLM_MODEL", "qwen3.8-27b"),
        base_url=os.environ.get("BU_LLM_BASE", "http://127.0.0.1:9000/v1"),
        api_key=os.environ.get("BU_LLM_KEY", "sk-mykey"),
    )
    session = BrowserSession(headless=True)
    agent = Agent(
        task="打开 https://www.baidu.com，告诉我页面上能看到什么",
        llm=llm,
        browser_session=session,
    )
    try:
        history = await agent.run(max_steps=5)
        print("[agent] history:", history)
        return True
    finally:
        await session.stop()


async def main() -> int:
    ap = argparse.ArgumentParser(description="browser_use 冒烟测试")
    ap.add_argument("--agent", action="store_true", help="额外跑一次 Agent LLM 闭环")
    args = ap.parse_args()

    print("=== browser_use smoke test ===")
    ok = await browser_smoke()
    if not ok:
        print("SMOKE FAIL (browser)")
        return 1

    if args.agent:
        await agent_smoke()

    print("SMOKE PASS")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
