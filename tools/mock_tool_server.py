#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代码审核 Agent · 模拟工具网关（mock_tool_server）

作用：模拟一台"提前设置好问题的业务代码服务"，让 AgentTeams 的 4 个 Agent 能像处理
真实代码审查一样：拉取待审代码 / 跑测试 / 提交修复并验证。

它对应官方教程 opspilot-zero-demo 里的 tools/mock_tool_server.py（运维故障版），
这里是"代码审查版"，自带三个场景：
  - buggy_find_max   ：find_max 函数有 2 个 bug（空列表返回 0、全负数返回 0），共 14 条测试
  - pr_security_issue：一个直接拼接用户输入的 SQL 查询接口（SQL 注入风险）

仅用 Python 标准库，在本机（Windows）的 Git Bash 里直接 `python3 mock_tool_server.py` 即可（脚本默认监听 0.0.0.0:18089），无需 pip 安装。

⚠️ 这是演示用的 mock：apply_fix 会真的执行提交过来的代码（放在子进程里、带超时）。
   仅用于本地/云演示环境，不要接到真实生产。
"""

import http.server
import json
import os
import subprocess
import tempfile
import textwrap
from urllib.parse import urlparse

PORT = 18089

# ---------------------------------------------------------------------------
# 场景一：buggy_find_max
# ---------------------------------------------------------------------------
BUGGY_FIND_MAX = '''def find_max(nums):
    """返回列表中的最大值。"""
    max_val = 0
    for n in nums:
        if n > max_val:
            max_val = n
    return max_val
'''

# 14 条测试用例：(输入列表, 期望输出)；空列表期望 None
TESTS_FIND_MAX = [
    ([1, 2, 3], 3),
    ([3, 2, 1], 3),
    ([5], 5),
    ([-1, -2, -3], -1),
    ([-5, -2, -9], -2),
    ([0, 0, 0], 0),
    ([1, 1, 2, 2, 3, 3], 3),
    ([-10, 10, 0], 10),
    ([100, 99, 98, 97], 100),
    ([-1, -1, -1], -1),
    ([2, -2, 2, -2], 2),
    ([7], 7),
    ([0, -1], 0),
    ([], None),
]


def build_find_max_runner(user_code: str) -> str:
    """生成一个测试运行脚本：导入用户提交的 find_max，跑 14 条用例。"""
    tests_literal = repr(TESTS_FIND_MAX)
    return textwrap.dedent(f'''
        import sys, json
        sys.path.insert(0, sys.path[0])
        try:
            import usercode
        except Exception as e:
            print(json.dumps({{"passed": 0, "total": {len(TESTS_FIND_MAX)},
                               "failures": ["导入失败: " + str(e)]}}))
            sys.exit(0)
        TESTS = {tests_literal}
        failures = []
        for inp, exp in TESTS:
            try:
                got = usercode.find_max(inp)
            except Exception as e:
                got = "ERROR: " + str(e)
            if got != exp:
                failures.append({{"input": inp, "expected": exp, "got": got}})
        print(json.dumps({{"passed": len(TESTS) - len(failures),
                           "total": len(TESTS), "failures": failures}}))
    ''')


# ---------------------------------------------------------------------------
# 场景二：pr_security_issue（SQL 注入风险）
# ---------------------------------------------------------------------------
PR_DIFF = '''diff --git a/app/db.py b/app/db.py
--- a/app/db.py
+++ b/app/db.py
@@ def get_user(conn, username):
+    query = "SELECT id, name FROM users WHERE name = '" + username + "'"
+    return conn.execute(query).fetchall()
'''

VULNERABLE_SNIPPET = '''def get_user(conn, username):
    # 注意：这里直接把用户输入拼进 SQL 语句
    query = "SELECT id, name FROM users WHERE name = '" + username + "'"
    return conn.execute(query).fetchall()
'''


def check_sql_injection(user_code: str) -> dict:
    """轻量静态检查：是否仍把原始输入拼进 SQL（有注入风险）。"""
    has_param = ("?" in user_code) or ("%s" in user_code) or (".execute(" in user_code and "params" in user_code)
    still_concat = ("+ username" in user_code) or ("+ user" in user_code) or ("format(" in user_code and "username" in user_code)
    vulnerable = still_concat and not has_param
    return {
        "passed": (not vulnerable),
        "total": 1,
        "failures": ["仍存在 SQL 注入风险：直接拼接用户输入到查询语句"] if vulnerable else [],
        "note": "已使用参数化查询" if not vulnerable else "请改用参数化查询（占位符 + 参数）",
    }


# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# HTTP 处理
# ---------------------------------------------------------------------------
class Handler(http.server.BaseHTTPRequestHandler):
    def _send(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/health":
            self._send(200, {"ok": True, "service": "coding-review-mock-tool-gateway"})
        elif path == "/scenarios/buggy_find_max/code":
            self._send(200, {"scenario_id": "buggy_find_max",
                             "file": "utils/math.py", "language": "python",
                             "code": BUGGY_FIND_MAX})
        elif path == "/scenarios/buggy_find_max/tests":
            self._send(200, {"scenario_id": "buggy_find_max",
                             "total": len(TESTS_FIND_MAX),
                             "cases": [{"input": i, "expected": e} for i, e in TESTS_FIND_MAX]})
        elif path == "/scenarios/pr_security_issue/code":
            self._send(200, {"scenario_id": "pr_security_issue",
                             "file": "app/db.py", "language": "python",
                             "code": VULNERABLE_SNIPPET, "diff": PR_DIFF})
        elif path == "/scenarios/pr_security_issue/tests":
            self._send(200, {"scenario_id": "pr_security_issue",
                             "note": "审查重点：是否存在 SQL 注入；修复后是否用参数化查询且功能不变"})
        else:
            self._send(404, {"error": "unknown path", "path": path})

    def do_POST(self):
        path = urlparse(self.path).path
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            payload = json.loads(raw.decode("utf-8"))
        except Exception:
            payload = {}

        if path == "/scenarios/buggy_find_max/apply_fix":
            user_code = payload.get("code", "")
            self._send(200, self._run_find_max(user_code))
        elif path == "/scenarios/pr_security_issue/apply_fix":
            user_code = payload.get("code", "")
            self._send(200, check_sql_injection(user_code))
        else:
            self._send(404, {"error": "unknown path", "path": path})

    def _run_find_max(self, user_code: str) -> dict:
        """把用户提交的代码放进子进程跑 14 条测试，带超时。"""
        try:
            with tempfile.TemporaryDirectory() as d:
                with open(os.path.join(d, "usercode.py"), "w", encoding="utf-8") as f:
                    f.write(user_code)
                runner = os.path.join(d, "runner.py")
                with open(runner, "w", encoding="utf-8") as f:
                    f.write(build_find_max_runner(user_code))
                proc = subprocess.run(
                    ["python", runner], cwd=d, capture_output=True, text=True, timeout=15
                )
                if proc.returncode != 0 and not proc.stdout.strip():
                    return {"ran": False, "passed": 0, "total": len(TESTS_FIND_MAX),
                            "regression": "代码执行出错", "log": proc.stderr.strip()[:500]}
                _lines = [l for l in proc.stdout.strip().splitlines() if l.strip()]
                result = json.loads(_lines[-1]) if _lines else {}
                passed = result["passed"]
                total = result["total"]
                return {
                    "ran": True,
                    "passed": passed,
                    "total": total,
                    "regression": "改前改后功能一致" if passed == total else "仍有用例不通过",
                    "log": result.get("failures", []),
                }
        except subprocess.TimeoutExpired:
            return {"ran": False, "passed": 0, "total": len(TESTS_FIND_MAX),
                    "regression": "执行超时", "log": "代码运行超过 15 秒"}
        except Exception as e:
            return {"ran": False, "passed": 0, "total": len(TESTS_FIND_MAX),
                    "regression": "执行异常", "log": str(e)[:500]}

    def log_message(self, *args):  # 静默默认访问日志
        pass


def main():
    server = http.server.ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"mock tool gateway 已启动，监听 0.0.0.0:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n已关闭网关")
        server.shutdown()


if __name__ == "__main__":
    main()
