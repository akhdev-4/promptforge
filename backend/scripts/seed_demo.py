"""Seed the running PromptForge API with realistic, DETAILED demo login prompts.

Each prompt is a comprehensive, production-grade master prompt (role, exact
stack, full design spec, auth flow, state, a11y, security, edge cases, testing,
file structure, acceptance criteria) paired with an "expected output" and an
**animated** self-contained HTML preview of the UI it produces.

Usage (against the Docker stack on http://localhost):
    python scripts/seed_demo.py                 # defaults to http://localhost
    python scripts/seed_demo.py http://localhost:8000
Idempotent: existing demo prompts (by title) are replaced.
"""

from __future__ import annotations

import sys

import httpx

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost").rstrip("/") + "/api/v1"

AUTHOR = {
    "email": "demo@promptforge.io",
    "password": "password123",
    "username": "promptforge",
    "full_name": "PromptForge Demo",
}

# --- Animated login preview generator ---------------------------------------
_TEMPLATE = """<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><style>
*{box-sizing:border-box;margin:0;font-family:__FONT__}
body{min-height:100vh;display:grid;place-items:center;background:__BG__;overflow:hidden}
.stage{animation:cardIn 6s ease-in-out infinite}
.card{position:relative;width:340px;padding:32px 28px;border-radius:__RADIUS__;__CARD__;color:__TEXT__}
.chip{display:inline-block;font-size:11px;padding:2px 9px;border-radius:999px;margin-bottom:12px;__CHIP__}
h1{font-size:21px;margin-bottom:4px;line-height:1.2}.sub{font-size:13px;opacity:.72;margin-bottom:18px}
label{display:block;font-size:12px;opacity:.8;margin:13px 0 6px}
.field{display:flex;align-items:center;min-height:42px;padding:0 13px;border-radius:10px;__INPUT__;font-size:14px}
.val{display:inline-block;overflow:hidden;white-space:nowrap;width:0}
.email .val{animation:emailType 6s infinite}
.f2 .val{animation:f2Type 6s infinite;letter-spacing:__F2LS__}
.caret{display:inline-block;width:2px;height:18px;background:__TEXT__;margin-left:2px;opacity:0}
.email .caret{animation:emailCaret 6s infinite}
.f2 .caret{animation:f2Caret 6s infinite}
.btn{position:relative;margin-top:20px;height:46px;border-radius:10px;display:flex;align-items:center;
justify-content:center;font-weight:600;font-size:14px;__BTN__;animation:press 6s ease-in-out infinite}
.btn .label{animation:labelFade 6s infinite}
.spin{position:absolute;width:20px;height:20px;border-radius:50%;border:2px solid rgba(255,255,255,.35);
border-top-color:__SPIN__;opacity:0;animation:spin 6s linear infinite}
.social{margin-top:10px;height:42px;border-radius:10px;display:flex;align-items:center;justify-content:center;
gap:8px;font-size:13px;__SOCIAL__}
.done{position:absolute;inset:0;border-radius:__RADIUS__;display:flex;flex-direction:column;gap:12px;
align-items:center;justify-content:center;background:__DONE_BG__;color:__DONE_FG__;opacity:0;
animation:doneIn 6s ease-in-out infinite}
.check{width:48px;height:48px;border-radius:50%;background:__DONE_FG__;color:__DONE_BG_SOLID__;display:flex;
align-items:center;justify-content:center;font-size:26px;transform:scale(.5);animation:checkPop 6s ease-in-out infinite}
.done .msg{font-size:14px;font-weight:600}
@keyframes cardIn{0%{opacity:0;transform:translateY(16px) scale(.97)}5%,93%{opacity:1;transform:none}99%,100%{opacity:0}}
@keyframes emailType{0%,8%{width:0}8%{animation-timing-function:steps(__EMAILCH__)}26%{width:__EMAILW__}100%{width:__EMAILW__}}
@keyframes emailCaret{0%,7%{opacity:0}9%,25%{opacity:1}27%,100%{opacity:0}}
@keyframes f2Type{0%,30%{width:0}30%{animation-timing-function:steps(__F2CH__)}50%{width:__F2W__}100%{width:__F2W__}}
@keyframes f2Caret{0%,29%{opacity:0}31%,49%{opacity:1}51%,100%{opacity:0}}
@keyframes press{0%,56%{transform:scale(1)}59%{transform:scale(.97)}62%,100%{transform:scale(1)}}
@keyframes labelFade{0%,60%{opacity:1}63%,79%{opacity:0}81%,100%{opacity:1}}
@keyframes spin{0%,62%{opacity:0;transform:rotate(0)}64%{opacity:1}79%{opacity:1;transform:rotate(1080deg)}81%,100%{opacity:0}}
@keyframes doneIn{0%,79%{opacity:0}85%,93%{opacity:1}98%,100%{opacity:0}}
@keyframes checkPop{0%,80%{transform:scale(.5)}87%{transform:scale(1.1)}91%,93%{transform:scale(1)}100%{transform:scale(.5)}}
</style></head><body>
<div class="stage"><form class="card" onsubmit="return false">
<span class="chip">__CHIP_LABEL__</span>
<h1>__TITLE__</h1><div class="sub">__SUB__</div>
<label>Email</label><div class="field email"><span class="val">__EMAIL__</span><span class="caret"></span></div>
__FIELD2_BLOCK__
__SOCIAL_BLOCK__
<div class="btn"><span class="label">__ACTION__</span><span class="spin"></span></div>
<div class="done"><div class="check">&#10003;</div><div class="msg">__SUCCESS__</div></div>
</form></div></body></html>"""


def build_anim(t: dict) -> str:
    field2_block = ""
    if t.get("f2"):
        field2_block = (
            f'<label>{t["f2_label"]}</label>'
            f'<div class="field f2"><span class="val">{t["f2"]}</span><span class="caret"></span></div>'
        )
    social_block = f'<div class="social">{t["social"]}</div>' if t.get("social") else ""
    email = t["email"]
    tokens = {
        "__FONT__": t.get("font", "system-ui,-apple-system,sans-serif"),
        "__BG__": t["bg"], "__RADIUS__": t.get("radius", "18px"), "__CARD__": t["card"],
        "__TEXT__": t["text"], "__CHIP__": t["chip_css"], "__CHIP_LABEL__": t["chip"],
        "__TITLE__": t["title"], "__SUB__": t["sub"], "__INPUT__": t["input"],
        "__BTN__": t["btn"], "__SPIN__": t.get("spin", "#fff"),
        "__SOCIAL__": t.get("social_css", ""),
        "__DONE_BG__": t["done_bg"], "__DONE_FG__": t["done_fg"],
        "__DONE_BG_SOLID__": t["done_bg_solid"], "__SUCCESS__": t["success"],
        "__ACTION__": t["action"], "__EMAIL__": email, "__EMAILCH__": str(len(email)),
        "__EMAILW__": f"{len(email)}ch", "__F2LS__": t.get("f2_ls", "normal"),
        "__F2CH__": str(len(t.get("f2", "x"))), "__F2W__": t.get("f2_w", "9ch"),
        "__FIELD2_BLOCK__": field2_block, "__SOCIAL_BLOCK__": social_block,
    }
    html = _TEMPLATE
    for k, v in tokens.items():
        html = html.replace(k, v)
    return html


# --- Backend: animated API terminal (request -> response) -------------------
_API_TPL = """<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><style>
*{box-sizing:border-box;margin:0;font-family:ui-monospace,'SF Mono',Menlo,Consolas,monospace}
body{min-height:100vh;display:grid;place-items:center;background:__BG__;overflow:hidden;padding:16px}
.win{width:470px;max-width:100%;border-radius:12px;overflow:hidden;background:#0b1020;border:1px solid #1e293b;
box-shadow:0 24px 60px rgba(0,0,0,.45);animation:winIn 6s ease-in-out infinite}
.bar{display:flex;align-items:center;gap:6px;padding:10px 12px;background:#111827;border-bottom:1px solid #1e293b}
.dot{width:10px;height:10px;border-radius:50%}.r{background:#ef4444}.y{background:#eab308}.g{background:#22c55e}
.title{margin-left:8px;color:#94a3b8;font-size:11px}
.body{padding:16px;font-size:12.5px;line-height:1.9;color:#e2e8f0;min-height:238px}
.mut{color:#64748b}.method{color:__ACCENT__;font-weight:700}.path{color:#e2e8f0}
.cmd{display:inline-block;overflow:hidden;white-space:nowrap;width:0;vertical-align:bottom;animation:typeCmd 6s infinite}
.sending{color:#64748b;opacity:0;animation:sending 6s infinite}
.status{font-weight:700;color:__STATUS_COLOR__;opacity:0;animation:statusIn 6s infinite}
.resp{margin-top:6px}.k{color:#7dd3fc}.s{color:#86efac}.n{color:#fca5a5}
__ROWS_CSS__
@keyframes winIn{0%{opacity:0;transform:translateY(14px) scale(.98)}5%,95%{opacity:1;transform:none}100%{opacity:0}}
@keyframes typeCmd{0%,8%{width:0}8%{animation-timing-function:steps(__CMDCH__)}40%{width:__CMDW__}100%{width:__CMDW__}}
@keyframes sending{0%,46%{opacity:0}48%,56%{opacity:.9}58%,100%{opacity:0}}
@keyframes statusIn{0%,57%{opacity:0}60%,95%{opacity:1}100%{opacity:0}}
</style></head><body>
<div class="win"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span>
<span class="title">__TITLE__</span></div>
<div class="body">
<div><span class="mut">$ curl -s -X </span><span class="cmd"><span class="method">__METHOD__</span> <span class="path">__PATH__</span></span></div>
<div class="sending">... sending request</div>
<div style="margin-top:12px"><span class="status">&#9679; HTTP __STATUS__</span></div>
<div class="resp">__ROWS_HTML__</div>
</div></div></body></html>"""


def build_api(t: dict) -> str:
    cmd = f'{t["method"]} {t["path"]}'
    rows_css = rows_html = ""
    for i, ln in enumerate(t["resp_lines"]):
        start = 60 + i * 4
        rows_css += (
            f".jl{i}{{opacity:0;animation:jl{i} 6s infinite}}"
            f"@keyframes jl{i}{{0%,{start}%{{opacity:0;transform:translateY(4px)}}"
            f"{min(start + 3, 96)}%,96%{{opacity:1;transform:none}}100%{{opacity:0}}}}"
        )
        rows_html += f'<div class="jl{i}">{ln}</div>'
    tokens = {
        "__BG__": t.get("bg", "#0f172a"), "__ACCENT__": t["accent"], "__TITLE__": t["title"],
        "__METHOD__": t["method"], "__PATH__": t["path"],
        "__CMDCH__": str(len(cmd)), "__CMDW__": f"{len(cmd)}ch",
        "__STATUS__": t["status"], "__STATUS_COLOR__": t.get("status_color", "#22c55e"),
        "__ROWS_CSS__": rows_css, "__ROWS_HTML__": rows_html,
    }
    html = _API_TPL
    for k, v in tokens.items():
        html = html.replace(k, v)
    return html


# --- Database: animated SQL query -> result grid ----------------------------
_DB_TPL = """<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><style>
*{box-sizing:border-box;margin:0;font-family:ui-monospace,'SF Mono',Menlo,Consolas,monospace}
body{min-height:100vh;display:grid;place-items:center;background:__BG__;overflow:hidden;padding:16px}
.win{width:500px;max-width:100%;border-radius:12px;overflow:hidden;background:#0b1020;border:1px solid #1e293b;
box-shadow:0 24px 60px rgba(0,0,0,.45);animation:winIn 6s ease-in-out infinite}
.bar{display:flex;align-items:center;gap:8px;padding:10px 12px;background:#111827;border-bottom:1px solid #1e293b}
.title{color:#94a3b8;font-size:11px}
.run{margin-left:auto;font-size:11px;color:#04121a;background:__ACCENT__;padding:3px 10px;border-radius:6px;
font-weight:700;animation:runPress 6s ease-in-out infinite}
.editor{padding:14px 16px;font-size:12.5px;color:#e2e8f0;border-bottom:1px solid #1e293b}
.mut{color:#64748b}
.q{display:inline-block;overflow:hidden;white-space:nowrap;width:0;vertical-align:bottom;animation:typeQ 6s infinite}
.grid{padding:4px 8px 6px}
.tr{display:grid;grid-template-columns:repeat(__NCOL__,1fr)}
.th{padding:8px 10px;font-size:10px;text-transform:uppercase;letter-spacing:.05em;color:#64748b;
border-bottom:1px solid #1e293b;opacity:0;animation:headIn 6s infinite}
.td{padding:8px 10px;font-size:12px;color:#cbd5e1;border-bottom:1px solid #0f172a}
.foot{padding:8px 16px 12px;font-size:11px;color:#64748b;opacity:0;animation:footIn 6s infinite}
__ROWS_CSS__
@keyframes winIn{0%{opacity:0;transform:translateY(14px) scale(.98)}5%,95%{opacity:1;transform:none}100%{opacity:0}}
@keyframes typeQ{0%,8%{width:0}8%{animation-timing-function:steps(__QCH__)}40%{width:__QW__}100%{width:__QW__}}
@keyframes runPress{0%,42%{transform:scale(1);filter:none}45%{transform:scale(.93);filter:brightness(1.25)}48%,100%{transform:scale(1)}}
@keyframes headIn{0%,49%{opacity:0}52%,95%{opacity:1}100%{opacity:0}}
@keyframes footIn{0%,86%{opacity:0}90%,95%{opacity:1}100%{opacity:0}}
</style></head><body>
<div class="win"><div class="bar"><span class="title">__TITLE__</span><span class="run">Run &#9654;</span></div>
<div class="editor"><span class="q">__QUERY__</span></div>
<div class="grid"><div class="tr">__HEADER__</div>__ROWS_HTML__</div>
<div class="foot">__FOOTER__</div></div></body></html>"""


def build_db(t: dict) -> str:
    cols, rows, q = t["columns"], t["rows"], t["query"]
    header = "".join(f'<div class="th">{c}</div>' for c in cols)
    rows_css = rows_html = ""
    for i, r in enumerate(rows):
        start = 52 + i * 7
        rows_css += (
            f".rw{i}{{opacity:0;animation:rw{i} 6s infinite}}"
            f"@keyframes rw{i}{{0%,{start}%{{opacity:0;transform:translateX(-6px)}}"
            f"{min(start + 4, 94)}%,94%{{opacity:1;transform:none}}100%{{opacity:0}}}}"
        )
        cells = "".join(f'<div class="td">{c}</div>' for c in r)
        rows_html += f'<div class="rw{i} tr">{cells}</div>'
    tokens = {
        "__BG__": t.get("bg", "#0b1020"), "__ACCENT__": t["accent"], "__TITLE__": t["title"],
        "__QUERY__": q, "__QCH__": str(len(q)), "__QW__": f"{len(q)}ch",
        "__NCOL__": str(len(cols)), "__HEADER__": header,
        "__ROWS_CSS__": rows_css, "__ROWS_HTML__": rows_html, "__FOOTER__": t["footer"],
    }
    html = _DB_TPL
    for k, v in tokens.items():
        html = html.replace(k, v)
    return html


def render(theme: dict) -> str:
    kind = theme.get("kind", "login")
    if kind == "api":
        return build_api(theme)
    if kind == "db":
        return build_db(theme)
    return build_anim(theme)


THEMES = {
    "glass": {
        "bg": "linear-gradient(135deg,#6d28d9,#2563eb 55%,#0891b2)",
        "card": ("background:rgba(255,255,255,.12);-webkit-backdrop-filter:blur(16px);"
                 "backdrop-filter:blur(16px);border:1px solid rgba(255,255,255,.25);"
                 "box-shadow:0 24px 60px rgba(0,0,0,.35)"),
        "text": "#fff", "chip": "JWT", "chip_css": "background:rgba(255,255,255,.18);color:#fff",
        "title": "Welcome back", "sub": "Sign in to your account",
        "input": "background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.3)",
        "btn": "background:#fff;color:#4c1d95", "spin": "#4c1d95",
        "email": "jordan@acme.com", "f2": "&#8226;&#8226;&#8226;&#8226;&#8226;&#8226;&#8226;&#8226;&#8226;",
        "f2_label": "Password", "f2_ls": "2px", "f2_w": "10ch",
        "action": "Sign in", "success": "Signed in &middot; token issued",
        "done_bg": "rgba(30,20,70,.94)", "done_fg": "#fff", "done_bg_solid": "#4c1d95",
    },
    "apple": {
        "bg": "#f5f5f7", "font": "-apple-system,system-ui,sans-serif",
        "card": "background:#fff;box-shadow:0 10px 40px rgba(0,0,0,.08);border:1px solid #ececec",
        "text": "#1d1d1f", "radius": "18px",
        "chip": "OAuth 2.0", "chip_css": "background:#eef2ff;color:#3730a3",
        "title": "Sign in", "sub": "Use your account to continue",
        "input": "background:#f5f5f7;border:1px solid #d2d2d7;color:#1d1d1f",
        "btn": "background:#0071e3;color:#fff", "spin": "#fff",
        "email": "jordan@acme.com", "f2": "&#8226;&#8226;&#8226;&#8226;&#8226;&#8226;&#8226;&#8226;",
        "f2_label": "Password", "f2_ls": "2px", "f2_w": "9ch",
        "social": "&#63743;&nbsp; Continue with Apple", "social_css": "background:#000;color:#fff",
        "action": "Continue", "success": "Authorized &middot; redirecting",
        "done_bg": "rgba(0,113,227,.96)", "done_fg": "#fff", "done_bg_solid": "#0071e3",
    },
    "dark2fa": {
        "bg": "#0b0f19", "card": "background:#111827;border:1px solid #1f2937",
        "text": "#e5e7eb", "radius": "16px",
        "chip": "&#128274; Two-factor", "chip_css": "background:#2e1065;color:#c4b5fd",
        "title": "Verify it's you", "sub": "Enter your password, then your 2FA code",
        "input": "background:#0b0f19;border:1px solid #374151;color:#e5e7eb",
        "btn": "background:linear-gradient(90deg,#8b5cf6,#6366f1);color:#fff", "spin": "#fff",
        "email": "jordan@acme.com", "f2": "123456", "f2_label": "Authenticator code",
        "f2_ls": "8px", "f2_w": "12ch",
        "action": "Verify &amp; sign in", "success": "2FA verified",
        "done_bg": "rgba(17,24,39,.97)", "done_fg": "#a78bfa", "done_bg_solid": "#111827",
    },
    "magic": {
        "bg": "linear-gradient(135deg,#eef2ff,#e0f2fe)",
        "card": "background:#fff;box-shadow:0 12px 44px rgba(30,64,175,.12);border:1px solid #e5e7eb",
        "text": "#0f172a", "radius": "18px",
        "chip": "Passwordless", "chip_css": "background:#dbeafe;color:#1e40af",
        "title": "Sign in with a link", "sub": "We'll email you a one-time sign-in link",
        "input": "background:#f8fafc;border:1px solid #cbd5e1;color:#0f172a",
        "btn": "background:#2563eb;color:#fff", "spin": "#fff", "email": "jordan@acme.com",
        "action": "Send magic link", "success": "&#9993; Check your inbox",
        "done_bg": "rgba(37,99,235,.96)", "done_fg": "#fff", "done_bg_solid": "#2563eb",
    },
    "stripe": {
        "bg": "linear-gradient(120deg,#635bff 0 42%,#f6f9fc 42% 100%)",
        "card": "background:#fff;box-shadow:0 15px 50px rgba(60,66,87,.15);border:1px solid #eceef1",
        "text": "#1a1f36", "radius": "14px",
        "chip": "Secure session", "chip_css": "background:#eef2ff;color:#4338ca",
        "title": "Sign in to Console", "sub": "Welcome back — please enter your details",
        "input": "background:#fff;border:1px solid #d5dbe6;color:#1a1f36",
        "btn": "background:#635bff;color:#fff", "spin": "#fff",
        "email": "jordan@acme.com", "f2": "&#8226;&#8226;&#8226;&#8226;&#8226;&#8226;&#8226;&#8226;",
        "f2_label": "Password", "f2_ls": "2px", "f2_w": "9ch",
        "action": "Sign in", "success": "Session started",
        "done_bg": "rgba(45,42,120,.96)", "done_fg": "#fff", "done_bg_solid": "#635bff",
    },
    "passkey": {
        "bg": "#fde68a", "card": "background:#fff;border:3px solid #111;box-shadow:8px 8px 0 #111",
        "text": "#111", "radius": "14px",
        "chip": "&#128273; Passkey", "chip_css": "background:#111;color:#fde047;border-radius:6px",
        "title": "Sign in", "sub": "Use your fingerprint, face, or device PIN",
        "input": "background:#fff;border:2px solid #111;color:#111",
        "btn": "background:#111;color:#fde047;border:0", "spin": "#fde047", "email": "jordan@acme.com",
        "action": "&#128273; Sign in with a passkey", "success": "&#128273; Passkey verified",
        "done_bg": "rgba(17,17,17,.97)", "done_fg": "#fde047", "done_bg_solid": "#111",
    },
}

THEMES.update({
    # --- Backend (animated API terminal) ---
    "rest_api": {
        "kind": "api", "bg": "#0f172a", "accent": "#38bdf8", "title": "orders-service — bash",
        "method": "POST", "path": "https://api.acme.dev/v1/orders",
        "status": "201 Created", "status_color": "#22c55e",
        "resp_lines": [
            '<span class="mut">{</span>',
            '  <span class="k">"id"</span>: <span class="s">"ord_8f2a91"</span>,',
            '  <span class="k">"status"</span>: <span class="s">"confirmed"</span>,',
            '  <span class="k">"total_cents"</span>: <span class="n">4200</span>,',
            '  <span class="k">"created_at"</span>: <span class="s">"2026-07-15T10:12:04Z"</span>',
            '<span class="mut">}</span>',
        ],
    },
    "auth_api": {
        "kind": "api", "bg": "#111027", "accent": "#a78bfa", "title": "auth-service — bash",
        "method": "POST", "path": "https://api.acme.dev/v1/auth/login",
        "status": "200 OK", "status_color": "#22c55e",
        "resp_lines": [
            '<span class="mut">{</span>',
            '  <span class="k">"access_token"</span>: <span class="s">"eyJhbGciOiJIUzI1NiIsIn..."</span>,',
            '  <span class="k">"token_type"</span>: <span class="s">"bearer"</span>,',
            '  <span class="k">"expires_in"</span>: <span class="n">900</span>',
            '<span class="mut">}</span>',
            '<span class="mut"># refresh token set as httpOnly cookie</span>',
        ],
    },
    "jobs_api": {
        "kind": "api", "bg": "#1a1020", "accent": "#f472b6", "title": "reports-worker — bash",
        "method": "POST", "path": "https://api.acme.dev/v1/reports:generate",
        "status": "202 Accepted", "status_color": "#eab308",
        "resp_lines": [
            '<span class="mut">{</span>',
            '  <span class="k">"task_id"</span>: <span class="s">"9b1c-4e2a"</span>,',
            '  <span class="k">"state"</span>: <span class="s">"queued"</span>,',
            '  <span class="k">"poll"</span>: <span class="s">"/v1/tasks/9b1c-4e2a"</span>',
            '<span class="mut">}</span>',
            '<span class="mut"># worker picks it up, retries with backoff</span>',
        ],
    },
    # --- Database (animated SQL -> result grid) ---
    "db_multitenant": {
        "kind": "db", "bg": "#0b1220", "accent": "#34d399", "title": "rls_demo.sql",
        "query": "SELECT id, tenant_id, name FROM projects;",
        "columns": ["id", "tenant_id", "name"],
        "rows": [["prj_1", "acme", "Marketing site"], ["prj_2", "acme", "Mobile app"]],
        "footer": "2 rows · RLS enforced · tenant = 'acme' (others hidden)",
    },
    "db_ecommerce": {
        "kind": "db", "bg": "#101012", "accent": "#fbbf24", "title": "orders.sql",
        "query": "SELECT id, total, status FROM orders LIMIT 3;",
        "columns": ["order_id", "total", "status"],
        "rows": [["1042", "$84.00", "paid"], ["1043", "$12.50", "pending"],
                 ["1044", "$220.00", "shipped"]],
        "footer": "3 rows · 6 ms · index: orders(status, created_at)",
    },
    "db_optimize": {
        "kind": "db", "bg": "#08131a", "accent": "#22d3ee", "title": "explain.sql",
        "query": "SELECT * FROM events WHERE user_id = 42;",
        "columns": ["id", "user_id", "type"],
        "rows": [["9a1", "42", "login"], ["9a2", "42", "view"], ["9a3", "42", "purchase"]],
        "footer": "3 rows · 4 ms — Index Scan (was 1.2 s Seq Scan)",
    },
})


# --- Detailed master prompts ------------------------------------------------
GLASS = """# Modern Glassmorphism Login — React + TypeScript + JWT

## 1. Role & objective
You are a **senior front-end engineer**. Build a **complete, production-ready,
accessible login feature** for a React SPA. Deliver **every file in full** — no
placeholders, no `TODO`, no `any`. The result must compile, pass its tests, and
be ready to drop into a real codebase.

## 2. Tech stack (use exactly these)
- React **18.3** + TypeScript **5.x** (`"strict": true`)
- **Vite** build tooling
- **Tailwind CSS 3.4** utility classes only — no component library
- **react-hook-form 7** + **zod 3** for form state & validation
- **@tanstack/react-query 5** for the login mutation
- **axios** for HTTP (single shared instance with interceptors)
- **lucide-react** for icons

## 3. Visual / design spec (glassmorphism)
- **Background:** full-viewport animated gradient, `135deg`, stops
  `#6d28d9 → #2563eb (55%) → #0891b2`; animate `background-position` over `12s`
  `ease-in-out infinite` (define the keyframes in `index.css`).
- **Card:** max-width `360px`, padding `36px 32px`, radius `20px`, centered
  vertically + horizontally.
- **Glass surface:** `background: rgba(255,255,255,.12)`,
  `backdrop-filter: blur(16px) saturate(140%)`, `1px` border
  `rgba(255,255,255,.25)`, shadow `0 24px 60px rgba(0,0,0,.35)`.
- **Typography:** heading `22px/600` white; labels `12px` white @ 80%; body `14px`.
- **Inputs:** height `44px`, radius `10px`, translucent bg, white text,
  placeholder `rgba(255,255,255,.6)`; focus → `2px` ring `rgba(255,255,255,.7)`.
- **Primary button:** solid white bg, `#4c1d95` text, `600`, height `46px`,
  radius `10px`; hover `scale(.99)` + shadow; disabled `opacity .5`.
- **Motion:** honour `prefers-reduced-motion: reduce` (disable gradient + transitions).

## 4. Markup & layout
`<main>` centering wrapper → `<form>` glass card containing: brand mark + `<h1>`
"Welcome back" + subtitle; **email** field; **password** field with a show/hide
toggle; a row with a **"Remember me"** checkbox and a **"Forgot password?"**
link; **submit** button; an **error region**; an "or" divider with placeholder
Google/GitHub buttons; footer "Don't have an account? Sign up".

## 5. Fields & validation (zod schema)
- `email`: required, valid email, trimmed + lowercased.
- `password`: required, min **8**, max **128**.
- `rememberMe`: boolean (default false).
- Validate `onBlur` **and** `onSubmit`; disable submit while invalid or pending.
- Render inline field errors beneath each input, wired via `aria-describedby`.

## 6. Authentication flow (JWT access + refresh)
1. On submit → `POST /api/auth/login { email, password }`.
2. Response `{ accessToken, user }`; server also sets the **refresh token** as an
   **httpOnly, Secure, SameSite=Strict** cookie.
3. Store the **access token in memory only** (module variable / context) —
   **never** `localStorage`/`sessionStorage`.
4. An axios request interceptor attaches `Authorization: Bearer <accessToken>`.
5. A response interceptor: on **401**, call `POST /api/auth/refresh` (cookie sent
   automatically) → new access token → **retry the original request once**. If
   refresh fails, clear auth and redirect to `/login`.
6. **Dedupe** concurrent refreshes into a single in-flight promise (no stampede).
7. On success, redirect to `location.state.from ?? "/dashboard"`.

Expose a `useAuth()` hook (`{ user, accessToken, login, logout }`) and an
`AuthProvider`. **No auth logic inside the component.**

## 7. State & UX
- **Loading:** button shows spinner + "Signing in…"; inputs disabled; block
  double-submit.
- **Error:** `400/401` → "Incorrect email or password" in an
  `aria-live="polite"` banner (generic — no user enumeration); network/`5xx` →
  "Something went wrong. Please try again."; `429` → "Too many attempts, try
  again shortly."
- **Password toggle:** button with correct `aria-pressed` + `aria-label`.

## 8. Accessibility (WCAG 2.1 AA)
- Every input has a real `<label>`; errors linked via `aria-describedby`; the
  error banner is `aria-live`.
- Visible focus rings (never remove outline without a replacement).
- Text contrast ≥ **4.5:1** (verify against the translucent surface).
- Full keyboard operability, logical tab order, `Enter` submits.

## 9. Security
- Access token in memory only; refresh token httpOnly cookie.
- No tokens or PII in logs; generic auth errors.
- CSRF: refresh relies on `SameSite=Strict` (document a double-submit fallback).
- Respect server `429`/rate-limit; exponential backoff on retry.

## 10. Edge cases (handle all)
Empty/invalid fields · wrong credentials · `429` · `5xx` · offline · slow
network (persistent spinner, no double submit) · access token expiring
mid-session · refresh failure · browser autofill styling.

## 11. Testing
- **Unit:** zod schema; `useAuth` (success, 401→refresh→retry, refresh failure).
- **Component (React Testing Library):** render, validation, submit success,
  error banner, password toggle, keyboard submit.
- Mock HTTP with **MSW**.

## 12. File structure
```
src/
  features/auth/
    components/LoginForm.tsx
    components/PasswordInput.tsx
    hooks/useAuth.tsx          # AuthProvider + context
    api/authApi.ts             # login, refresh, logout
    lib/httpClient.ts          # axios instance + interceptors
    schemas/loginSchema.ts
    __tests__/LoginForm.test.tsx
  app/routes/login.tsx
  index.css                    # gradient keyframes
```

## 13. Acceptance criteria (all must pass)
- [ ] Valid credentials → redirect to `/dashboard` (or `from`).
- [ ] Wrong credentials → `aria-live` error, no redirect.
- [ ] Access token never in web storage; refresh is an httpOnly cookie.
- [ ] `401` → auto refresh → retry once; refresh failure → logout.
- [ ] Keyboard-only login works; screen reader announces errors.
- [ ] Lighthouse a11y ≥ 95; zero console errors/warnings.

## Out of scope
Sign-up, password reset, and MFA are separate prompts.
"""

APPLE = """# Apple-Style Minimal Login — Next.js + OAuth (Google & Apple)

## 1. Role & objective
You are a **senior full-stack engineer**. Build a calm, minimal, Apple-ID-style
sign-in for a Next.js app supporting **email/password and social OAuth**.
Deliver all files complete and typed — no placeholders.

## 2. Tech stack (exact)
- **Next.js 14+** App Router + TypeScript (strict)
- **Auth.js / NextAuth v5** (`@auth/core`) with Credentials + Google + Apple providers
- **Tailwind CSS 3.4**; **react-hook-form** + **zod** for the credentials form
- **Prisma** adapter (Postgres) for accounts/sessions

## 3. Visual / design spec
- Background `#f5f5f7`; single centered column, max-width `360px`, lots of whitespace.
- SF-like system font stack; heading `26px/600` letter-spacing `-.02em`.
- Inputs: radius `12px`, `1px #d2d2d7` border, height `46px`, focus ring blue.
- Primary button: `#0071e3`, white text, radius `12px`, full width.
- Social buttons: outlined, `44px`, with provider glyph; an **"or"** divider
  (thin `#d2d2d7` rules) between primary and social.
- Subtle, tasteful motion; respect `prefers-reduced-motion`.

## 4. Auth flows
### Credentials
`POST` via NextAuth Credentials provider → verify with **argon2/bcrypt** hash →
issue session. Never reveal whether the email exists.
### Social (OAuth 2.0 / OIDC)
"Continue with Apple" and "Continue with Google" call
`signIn('apple' | 'google')`. Configure providers + secrets **server-side only**
in `auth.ts`. Handle the `OAuthAccountNotLinked` error with a friendly inline
message ("This email is already registered with a different method").

## 5. Sessions & security
- Session strategy: database sessions via the Prisma adapter; cookies
  **httpOnly, Secure, SameSite=Lax**.
- CSRF handled by NextAuth; never expose `AUTH_SECRET` or client secrets to the browser.
- Redirect to `/dashboard` (or `callbackUrl`) on success; validate `callbackUrl`
  is same-origin.
- Rate-limit the credentials route (per IP + email).

## 6. Validation & UX
- zod: `email` valid + required; `password` min 8.
- States: loading spinner on the pressed button; disabled while pending;
  `aria-live` error region; inline field errors.
- Middleware guards `/dashboard`; unauthenticated → `/login?callbackUrl=…`.

## 7. Accessibility (WCAG 2.1 AA)
Labelled inputs; visible focus; social buttons are real `<button>`s with
`aria-label`; contrast ≥ 4.5:1; keyboard-first; announce errors politely.

## 8. Edge cases
Invalid creds · `OAuthAccountNotLinked` · provider cancel/timeout · disabled
account · expired session · open-redirect attempts on `callbackUrl` · JS disabled
(credentials form still posts).

## 9. Testing
Unit: zod + credentials authorize(). Integration: NextAuth callbacks. E2E
(Playwright): credentials happy path, bad password, Google sign-in stub,
protected-route redirect.

## 10. File structure
```
app/(auth)/login/page.tsx
components/auth/LoginForm.tsx
components/auth/SocialButtons.tsx
auth.ts                       # NextAuth config + providers
app/api/auth/[...nextauth]/route.ts
middleware.ts                 # protect /dashboard
lib/validation/login.ts
prisma/schema.prisma          # User, Account, Session
```

## 11. Acceptance criteria
- [ ] Email/password sign-in creates a session and redirects to `/dashboard`.
- [ ] Google & Apple OAuth complete and link/create the account.
- [ ] `OAuthAccountNotLinked` shows a friendly inline message.
- [ ] Secrets stay server-side; cookies httpOnly/Secure/SameSite=Lax.
- [ ] `callbackUrl` cannot open-redirect off-origin.
- [ ] Works without client JS for the credentials path; a11y ≥ 95.

## Out of scope
Registration UI and account settings.
"""

DARK2FA = """# Dark SaaS Login with Two-Factor (TOTP) — React

## 1. Role & objective
You are a **senior product engineer** building a secure, dark-themed two-step
login (password → TOTP) for a SaaS app. Ship every file, fully typed, tested.

## 2. Tech stack (exact)
- React 18 + TypeScript (strict), Vite
- Tailwind 3.4; react-hook-form + zod; TanStack Query
- `otpauth`/server-side `speakeasy` for TOTP verification (client only submits the code)

## 3. Visual / design spec (dark, Linear/Vercel feel)
- Background `#0b0f19`; card `#111827`, `1px #1f2937`, radius `16px`.
- Muted gray labels `#9ca3af`; body text `#e5e7eb`.
- CTA: gradient `linear-gradient(90deg,#8b5cf6,#6366f1)`, white text.
- A pill "step indicator" (1 Credentials · 2 Verify). 6 individual OTP boxes,
  monospace, auto-advancing, `12px` gap.

## 4. Flow
### Step 1 — credentials
`POST /api/auth/login { email, password }`.
- If the account has no 2FA → session issued, redirect.
- If 2FA is enabled → API returns `{ status: "mfa_required", mfaToken }` (short-lived).
### Step 2 — TOTP (RFC 6238)
Render 6 single-digit inputs: auto-focus next on entry, backspace moves back,
**paste a 6-digit code fills all boxes**, only digits allowed. Submit
`POST /api/auth/2fa/verify { mfaToken, code }`. On success → session + redirect.
- "Use a backup code instead" link swaps to a single backup-code input.
- **Lock the form after 5 failed attempts** (server-enforced; reflect in UI with
  a cooldown timer).

## 5. State & UX
Reducer-driven step state (`credentials | mfa | locked`). `aria-live` for verify
errors; resend/cooldown timer; both steps share one accessible card; back button
returns to step 1 without losing the email.

## 6. Security
- TOTP secret **never** touches the client; browser submits only the 6-digit code.
- `mfaToken` is short-lived + single-use; constant-time compare server-side.
- Generic errors; rate-limit + lockout; no user enumeration.

## 7. Accessibility (WCAG 2.1 AA)
OTP group has a `role="group"` + `aria-label`; each box labelled; announce
"code incorrect" politely; visible focus; full keyboard + paste support.

## 8. Edge cases
Wrong password · wrong/expired code · expired `mfaToken` · 5-attempt lockout ·
paste with spaces/dashes · autofill of one-time codes (`autocomplete="one-time-code"`) ·
user without 2FA · backup-code path.

## 9. Testing
Unit: OTP input (auto-advance, paste, digit-only), reducer transitions.
Component: full two-step happy path, wrong code, lockout. MSW mocks.

## 10. File structure
```
src/features/auth/
  components/LoginStepCredentials.tsx
  components/LoginStepMfa.tsx
  components/OtpInput.tsx
  state/loginReducer.ts
  api/authApi.ts
  hooks/useLogin.ts
  __tests__/…
```

## 11. Acceptance criteria
- [ ] No-2FA account signs in directly.
- [ ] 2FA account transitions to the code step and verifies per RFC 6238.
- [ ] OTP boxes auto-advance and accept a pasted 6-digit code.
- [ ] 5 failures → server lockout reflected with a cooldown.
- [ ] Backup-code fallback works; secret never sent to the client.
- [ ] Keyboard + screen-reader complete the flow; a11y ≥ 95.

## Out of scope
2FA enrollment/QR setup (separate prompt).
"""

MAGIC = """# Passwordless Magic-Link Login — Next.js

## 1. Role & objective
You are a **senior full-stack engineer** implementing passwordless email
magic-link sign-in end to end (UI + API + email). Ship everything, typed, tested.

## 2. Tech stack (exact)
- Next.js 14+ App Router + TypeScript (strict)
- Tailwind 3.4; react-hook-form + zod
- `jose` for signing JWTs; Prisma (Postgres) for users + `jti` store; Resend/SES for email

## 3. Visual / design spec
- Soft `#eef2ff → #e0f2fe` gradient; white card, radius `18px`.
- One email field + primary "Send magic link" button.
- After submit, swap to a **"Check your inbox"** confirmation showing a **masked**
  email (`j•••@acme.com`) and a **Resend** button with a **30s cooldown**.

## 4. Flow
1. `POST /api/auth/magic-link { email }`. Always respond `200` with the same body
   (**never reveal whether the account exists**).
2. If the email maps to a user, sign a **single-use, 15-minute JWT** (`sub`, `jti`,
   `exp`) and persist the `jti` as unused; email a link to
   `/api/auth/callback?token=…`.
3. Callback verifies signature + expiry, checks the `jti` is unused, **marks it
   used (single-use)**, creates a session cookie, and redirects to `/dashboard`.
4. Expired/used/invalid token → friendly "This link has expired — request a new
   one" screen with a resend action.

## 5. Security
- Tokens single-use (jti invalidated on use) + short TTL; constant-time compare.
- Rate-limit by **email + IP**; generic responses (no enumeration).
- Session cookie httpOnly/Secure/SameSite=Lax; validate redirect target is same-origin.
- Sign with a strong secret from env; rotate-friendly (`kid` supported).

## 6. UX & validation
zod email validation; disabled button while sending; `aria-live` status; masked
email; cooldown timer; clear expired-link recovery screen. Provide the **email
template as clean, inlined, responsive HTML** (dark-mode friendly).

## 7. Accessibility (WCAG 2.1 AA)
Labelled input; status announced politely; visible focus; keyboard-first; the
confirmation is readable by screen readers.

## 8. Edge cases
Unknown email (same confirmation) · expired token · already-used token · tampered
token · resend spam (cooldown + rate-limit) · email delivery failure (log, show
neutral message) · clock skew tolerance.

## 9. Testing
Unit: token sign/verify + jti single-use; masking; rate-limit. Integration:
callback success, expired, reused. E2E: request → follow link → session.

## 10. File structure
```
app/(auth)/login/page.tsx
app/(auth)/login/sent/page.tsx
app/api/auth/magic-link/route.ts
app/api/auth/callback/route.ts
lib/tokens.ts                 # sign/verify + jti store
lib/email/magicLink.tsx       # inlined HTML template
lib/rateLimit.ts
```

## 11. Acceptance criteria
- [ ] Submitting any email shows the same neutral "check your inbox" state.
- [ ] Valid link signs the user in once; a second click is rejected.
- [ ] Links expire after 15 min; expired → recovery screen.
- [ ] Resend is rate-limited with a visible cooldown.
- [ ] No password field anywhere; no user enumeration; a11y ≥ 95.

## Out of scope
Account linking and social login.
"""

STRIPE = """# Stripe-Style Split-Screen Login — Django (Server Sessions)

## 1. Role & objective
You are a **senior Django engineer**. Build a polished, server-rendered
split-screen login using Django's session auth. Ship templates, forms, views,
URLs, settings, and tests — production-ready, works without JavaScript.

## 2. Tech stack (exact)
- Django 5.x + Django templates (no SPA)
- `django.contrib.auth` session framework
- `django-axes` (or equivalent) for login rate-limiting
- Vanilla CSS (or Tailwind via django-tailwind) — no JS required for the core flow

## 3. Visual / design spec
- Two panes: **left** = gradient marketing panel (`#635bff`) with a headline,
  value prop, and a rotating testimonial; **right** = the form. Collapses to a
  single column below `768px`.
- Card inputs radius `8–10px`; primary button `#635bff`; clear non-field error banner.

## 4. Form & auth
- `LoginForm` (in `forms.py`): `email` + `password` + `remember_me`; server-side
  validation; a **non-field error** ("Incorrect email or password") on failure —
  never reveal which field was wrong.
- View authenticates via `authenticate()` + `login()`; **thin view**, all
  validation in the form.
- **CSRF token** in the form (`{% csrf_token %}`).
- "Remember me" toggles `request.session.set_expiry` (0 = browser session vs a
  longer age).
- Safe post-login redirect: honour `next` only if `url_has_allowed_host_and_scheme`.

## 5. Security (settings.py)
- `SESSION_COOKIE_HTTPONLY = True`, `SESSION_COOKIE_SECURE = True`,
  `SESSION_COOKIE_SAMESITE = "Lax"`, `CSRF_COOKIE_SECURE = True`.
- `SECURE_SSL_REDIRECT`, HSTS in prod.
- Login rate-limiting/lockout via django-axes; generic error messages.
- Password hashing left to Django's default (argon2 recommended).

## 6. Accessibility (WCAG 2.1 AA)
Labelled inputs; error summary linked to fields; visible focus; contrast ≥ 4.5:1;
fully operable and submittable with keyboard and **without JavaScript**.

## 7. Edge cases
Invalid creds · inactive user · locked-out (axes) · unsafe `next` · already
authenticated (redirect away) · CSRF failure page · very long inputs.

## 8. Testing (pytest-django)
Form validation; view GET/POST (success, failure, lockout); `next` redirect
safety; session expiry with/without remember-me; CSRF enforced.

## 9. File structure
```
accounts/forms.py            # LoginForm
accounts/views.py            # LoginView (thin)
accounts/urls.py
templates/accounts/login.html
templates/base.html
project/settings.py          # cookie/security settings
accounts/tests/test_login.py
```

## 10. Acceptance criteria
- [ ] Valid login creates a session and redirects to a safe `next`/dashboard.
- [ ] Invalid login shows a non-field error; no field-level enumeration.
- [ ] Works fully without JavaScript.
- [ ] Cookies httpOnly/Secure/SameSite=Lax; CSRF enforced.
- [ ] Rate-limit/lockout active; unsafe `next` ignored.
- [ ] Responsive split → single column; a11y ≥ 95.

## Out of scope
Registration, password reset (Django's built-in views can be wired separately).
"""

PASSKEY = """# Passkey (WebAuthn) Login — Neobrutalist, React

## 1. Role & objective
You are a **senior engineer specializing in auth**. Build a striking,
passwordless **passkey (WebAuthn)** login with a graceful fallback. Ship the
client, the server ceremony endpoints' contracts, and tests — fully typed.

## 2. Tech stack (exact)
- React 18 + TypeScript (strict), Vite
- **@simplewebauthn/browser** (client) targeting **@simplewebauthn/server** (API)
- Tailwind 3.4 (neobrutalist styling)

## 3. Visual / design spec (neobrutalism)
- Background `#fde68a`; white card with **`3px` solid black border** and a **hard
  offset shadow** `8px 8px 0 #111`; radius `14px`.
- Chunky primary button (black bg, `#fde047` text): "🔑 Sign in with a passkey".
- High-contrast blocks; bold labels; a subtle biometric hint line.

## 4. Ceremony (WebAuthn)
### Authentication
1. `GET /api/webauthn/authenticate/options?email=` → server returns
   `PublicKeyCredentialRequestOptions` (base64url challenge, `rpId`, allowCredentials).
2. `startAuthentication(options)` → assertion → `POST /api/webauthn/authenticate/verify`.
3. Server verifies signature, **origin, and RP ID**, checks the signature counter,
   issues a session → redirect.
### Registration (first-time / "Register a passkey")
`GET /options` → `startRegistration()` → `POST /verify` stores the credential.

## 5. Fallback & capability detection
- On mount, detect support:
  `window.PublicKeyCredential && isUserVerifyingPlatformAuthenticatorAvailable()`.
- If unsupported/no authenticator → show and route to an **email magic-link**
  fallback with a short explanation.
- Handle **user cancellation** (`NotAllowedError`) quietly — no scary red errors.

## 6. Security
- Challenges are server-generated, single-use, base64url; verify origin + RP ID
  server-side; enforce the signature counter (clone detection).
- Never fabricate credentials client-side; never trust client-sent verification.
- Session cookie httpOnly/Secure/SameSite=Lax.

## 7. Accessibility (WCAG 2.1 AA)
Real `<button>`s with `aria-label`; status via `aria-live`; visible focus;
keyboard-triggerable; the biometric hint is text, not icon-only.

## 8. Edge cases
No platform authenticator · user cancels · timeout · unknown email · counter
regression (possible clone → reject) · multiple passkeys (allowCredentials) ·
cross-device (hybrid) flow · fallback path when WebAuthn unavailable.

## 9. Testing
Unit: capability detection, option decoding, error mapping. Component: support
vs unsupported render, cancel handling, fallback route. Mock the WebAuthn API.

## 10. File structure
```
src/features/auth/
  components/PasskeyLogin.tsx
  components/MagicLinkFallback.tsx
  lib/webauthnClient.ts        # options fetch + start + verify
  lib/capabilities.ts          # platform authenticator detection
  hooks/usePasskeyLogin.ts
  __tests__/…
```

## 11. Acceptance criteria
- [ ] Primary action runs the WebAuthn assertion and signs in on success.
- [ ] Origin + RP ID + signature counter verified server-side.
- [ ] First-time users can register a passkey.
- [ ] No authenticator → magic-link fallback with explanation.
- [ ] User-cancel handled quietly; no passwords anywhere; a11y ≥ 95.

## Out of scope
Passkey management (rename/revoke) in account settings.
"""


# ---------------------------------------------------------------------------
# Re-scoped content: the login prompts are FRONTEND (client-side) in scope —
# visuals, component structure, client validation, states, and the API
# *contract* they call. Server internals (hashing, token rotation, sessions,
# RLS, rate-limiting) live in the Backend prompts. These reassignments override
# the verbose full-stack versions above for the prompt list built below.
# ---------------------------------------------------------------------------
GLASS = """# Modern Glassmorphism Login — React (Frontend)

## 1. Role & objective
You are a **senior frontend engineer**. Build a complete, accessible login
**screen component** in React. Scope is the client: visuals, structure,
validation, states, and the API contract it calls — not the server. Ship every
file, fully typed.

## 2. Tech stack (exact)
- React 18 + TypeScript (strict), Vite, **Tailwind CSS 3.4** (no UI kit)
- **react-hook-form 7** + **zod 3** (client validation)
- **@tanstack/react-query 5** for the login mutation

## 3. Visual / design spec (glassmorphism)
- Full-viewport animated gradient (135deg `#6d28d9 → #2563eb → #0891b2`, 12s loop)
- Frosted card: max-w 360px, radius 20px, `rgba(255,255,255,.12)` + `backdrop-blur(16px)`,
  1px translucent border, soft shadow
- Inputs 44px / radius 10px translucent; white primary button (`#4c1d95` text)
- Honour `prefers-reduced-motion`

## 4. Component structure
`<LoginScreen>` → `<LoginForm>` (email, password with show/hide toggle, remember-me,
forgot link, submit, error region, social divider). Keep small presentational
pieces: `PasswordInput`, `FieldError`.

## 5. Client validation (zod)
email required + valid + lowercased; password required, min 8; validate on blur +
submit; inline errors wired via `aria-describedby`; disable submit while invalid/pending.

## 6. States & UX
loading (spinner + disabled, block double-submit); `aria-live` error banner for
"incorrect email or password"; password show/hide with `aria-pressed`; on success
redirect to `/dashboard`.

## 7. API contract (client-side only — the login API is a separate Backend prompt)
- Call `POST /api/auth/login { email, password }` via the mutation.
- Expect `{ accessToken, user }`; keep the access token **in memory** (context),
  assume the refresh token is an httpOnly cookie the server set.
- On `401` show the credentials error. (Refresh/rotation is the API's job.)
Expose a thin `useLogin()` hook wrapping the mutation + redirect.

## 8. Accessibility (WCAG 2.1 AA)
Labelled inputs; visible focus rings; `aria-live` errors; full keyboard; `Enter`
submits; contrast ≥ 4.5:1 on the translucent surface.

## 9. Testing (React Testing Library + MSW)
render; validation; submit success → redirect; `401` → error; password toggle;
keyboard submit.

## 10. File structure
`src/features/auth/{LoginScreen,LoginForm,PasswordInput}.tsx`,
`hooks/useLogin.ts`, `schemas/loginSchema.ts`, `__tests__/…`

## 11. Acceptance criteria
- [ ] Frosted card over animated gradient; responsive + reduced-motion aware
- [ ] Zod validation with accessible inline + `aria-live` errors
- [ ] Calls the login endpoint; access token kept in memory (not web storage)
- [ ] Loading / disabled / success states correct; keyboard + SR friendly
- [ ] Component tests pass; no `any`

## Out of scope (see the Backend prompts)
Password hashing, token issuance/rotation, sessions, rate-limiting.
"""

APPLE = """# Apple-Style Minimal Login — Next.js (Frontend)

## 1. Role & objective
You are a **senior frontend engineer**. Build a minimal, Apple-ID-style login
**screen** in Next.js (App Router) + TS. Client-focused: visuals, the credentials
+ social UI, and the auth calls via the client SDK. Ship all files, typed.

## 2. Tech stack (exact)
Next.js 14+ App Router, TypeScript, Tailwind 3.4, react-hook-form + zod, and the
**NextAuth client** (`signIn`). Provider/secret config is a Backend/config prompt.

## 3. Visual / design spec
Off-white `#f5f5f7`; centered column max-w 360px; SF-like system font; 12px-radius
inputs; single blue primary (`#0071e3`); outlined social buttons; thin "or"
divider; tasteful motion; reduced-motion aware.

## 4. Structure & behaviour
`<LoginForm>`: email + password → `signIn('credentials')`; "Continue with Apple/
Google" → `signIn('apple' | 'google')`. Loading spinner on the pressed button;
inline `OAuthAccountNotLinked` message; redirect to `callbackUrl`/`/dashboard`.

## 5. Client validation (zod)
email valid + required; password min 8; disabled while pending; `aria-live` errors.

## 6. API contract (client-side)
Uses NextAuth `signIn(...)`; on error render the friendly message; on success let
NextAuth handle the redirect. (Providers, secrets, session strategy = Backend/config prompt.)

## 7. Accessibility (WCAG 2.1 AA)
Real `<button>`s + `aria-label`; labelled inputs; visible focus; contrast ≥ 4.5:1;
keyboard-first; announce errors.

## 8. Testing (RTL + Playwright)
credentials happy path; bad password; social buttons call `signIn`; error render.

## 9. File structure
`app/(auth)/login/page.tsx`, `components/auth/{LoginForm,SocialButtons}.tsx`,
`lib/validation/login.ts`

## 10. Acceptance criteria
- [ ] Minimal centered layout; blue CTA; social buttons; "or" divider
- [ ] Credentials + social via `signIn`; friendly `OAuthAccountNotLinked` message
- [ ] Client validation + `aria-live` errors; keyboard + a11y ≥ 95
- [ ] Component / E2E tests pass

## Out of scope (Backend/config prompt)
Provider + secret config, session strategy, callback validation.
"""

DARK2FA = """# Dark SaaS Login with 2FA — React (Frontend)

## 1. Role & objective
You are a **senior frontend engineer**. Build the **two-step login UI** (password
→ 6-digit TOTP) for a dark SaaS app. Client-focused: the flow, the OTP input, and
states. Ship all files, typed + tested.

## 2. Tech stack (exact)
React 18 + TS, Vite, Tailwind 3.4, react-hook-form + zod, TanStack Query.

## 3. Visual / design spec
Navy `#0b0f19` bg; `#111827` card; violet→indigo gradient CTA; muted labels;
Linear/Vercel feel; a step indicator (1 Credentials · 2 Verify); six auto-advancing
OTP boxes.

## 4. Flow (client)
Step 1: email + password → `POST /api/auth/login`. If the response is
`{ status: 'mfa_required', mfaToken }` → go to step 2. Step 2: 6-digit code →
`POST /api/auth/2fa/verify { mfaToken, code }` → redirect. "Use a backup code"
swaps to a single input. Reflect a server lockout as a cooldown timer.

## 5. OTP input component
6 single-digit boxes: auto-focus next, backspace to previous, **paste fills all**,
digits only, `autocomplete="one-time-code"`, `role="group"` + `aria-label`.

## 6. States & a11y
reducer step state (`credentials | mfa | locked`); `aria-live` verify errors;
visible focus; full keyboard + paste; step indicator announced.

## 7. API contract (client-side)
Submits credentials, then the 6-digit code. Never handles secrets — TOTP
verification + lockout enforcement are the API's job.

## 8. Testing
OTP input (auto-advance, paste, digit-only), reducer transitions, two-step happy
path, wrong code, lockout render.

## 9. File structure
`src/features/auth/{LoginStepCredentials,LoginStepMfa,OtpInput}.tsx`,
`state/loginReducer.ts`, `hooks/useLogin.ts`

## 10. Acceptance criteria
- [ ] Two-step UI; transitions on `mfa_required`
- [ ] OTP boxes auto-advance + accept a pasted 6-digit code
- [ ] Backup-code toggle; lockout cooldown reflected
- [ ] Keyboard + SR complete the flow; tests pass

## Out of scope (Backend prompt)
TOTP secret + verification, `mfaToken` issuance, server-side lockout.
"""

MAGIC = """# Passwordless Magic-Link Login — Next.js (Frontend)

## 1. Role & objective
You are a **senior frontend engineer**. Build the **request + confirmation UI** for
passwordless magic-link sign-in. Client-focused. Ship files, typed + tested.

## 2. Tech stack (exact)
Next.js 14+ App Router, TS, Tailwind 3.4, react-hook-form + zod.

## 3. Visual / design spec
Soft `#eef2ff → #e0f2fe` gradient; white card radius 18px; one email field +
"Send magic link"; after submit, swap to a "Check your inbox" state.

## 4. Flow (client)
Submit email → `POST /api/auth/magic-link { email }` → always show the same neutral
"check your inbox" confirmation with a **masked** email (`j•••@acme.com`) and a
**Resend** button (30s cooldown). No password field. When routed back with an
error, show an "expired link" recovery view.

## 5. Validation & states
zod email; disabled while sending; `aria-live` status; cooldown timer; masked email;
expired-link recovery view.

## 6. API contract (client-side)
POST the email; treat all responses identically (no enumeration in the UI). Token
signing/verification/rate-limit are the API's concern.

## 7. Accessibility
Labelled input; status announced; visible focus; keyboard-first.

## 8. Testing
submit → confirmation; email masking; resend cooldown; expired-link view.

## 9. File structure
`app/(auth)/login/page.tsx`, `app/(auth)/login/sent/page.tsx`,
`components/auth/MagicLinkForm.tsx`

## 10. Acceptance criteria
- [ ] One email field; neutral "check your inbox" with a masked email
- [ ] Rate-limited resend with a visible cooldown
- [ ] Expired-link recovery screen; no password anywhere
- [ ] a11y ≥ 95; tests pass

## Out of scope (Backend prompt)
Token signing / single-use jti, email delivery, rate-limiting.
"""

STRIPE = """# Stripe-Style Split-Screen Login — UI (Frontend / Templates)

## 1. Role & objective
You are a **senior frontend engineer**. Build the **split-screen login UI**: a
marketing panel + a login form, server-rendered with Django templates. Focus on
markup, styling, responsiveness, and form UX. Ship the template + styles; it must
work **without JavaScript**.

## 2. Visual / design spec
Left pane: gradient marketing panel (`#635bff`) with a headline + rotating
testimonial. Right pane: the form card. Collapses to one column below 768px.

## 3. Form UI
email + password + remember-me; a `{% csrf_token %}` field; a **non-field error
banner** slot ("Incorrect email or password"); primary `#635bff` button.

## 4. Behaviour (client)
Standard form POST to the login route; render the server-provided error banner;
"remember me" is a checkbox the server reads. No client-side auth logic.

## 5. Accessibility (WCAG 2.1 AA)
Labelled inputs; an error summary linked to fields; visible focus; contrast ≥ 4.5:1;
fully operable and submittable **without JavaScript**.

## 6. Deliverables
`login.html` + `base.html` + the CSS, plus a short note on where the form posts and
which context variables it expects (`form`, `next`, error flags).

## 7. Acceptance criteria
- [ ] Responsive two-pane → single column
- [ ] Accessible form with a non-field error slot; CSRF field present
- [ ] Works without JavaScript; contrast + focus correct

## Out of scope (Backend prompt)
The Django view/auth, session + cookie settings, CSRF/rate-limit handling.
"""

PASSKEY = """# Passkey (WebAuthn) Login — Neobrutalist, React (Frontend)

## 1. Role & objective
You are a **senior frontend engineer**. Build the **client WebAuthn login UI** with
a graceful fallback. The ceremony runs in the browser; the server endpoints are a
contract. Ship the client + tests, typed.

## 2. Tech stack (exact)
React 18 + TS, Vite, Tailwind 3.4, **@simplewebauthn/browser**.

## 3. Visual / design spec (neobrutalism)
`#fde68a` bg; white card with a **3px black border** and a hard **8px offset
shadow**; a chunky black "🔑 Sign in with a passkey" button (yellow text);
high-contrast blocks.

## 4. Client ceremony (WebAuthn)
1. `GET /api/webauthn/authenticate/options?email=` → options.
2. `startAuthentication(options)` (browser prompts biometric) → assertion.
3. `POST /api/webauthn/authenticate/verify` → on success, redirect.
"Register a passkey" runs `startRegistration()` against the register endpoints.

## 5. Capability detection & fallback
On mount detect support (`PublicKeyCredential` +
`isUserVerifyingPlatformAuthenticatorAvailable()`); if unsupported → route to a
magic-link fallback with a short explanation. Handle `NotAllowedError` (user
cancel) quietly.

## 6. API contract (client-side)
Fetch options + submit the assertion only. Challenge generation and origin / RP-ID
/ signature-counter verification are the API's concern.

## 7. Accessibility
Real `<button>` + `aria-label`; `aria-live` status; visible focus; the biometric
hint is text, not icon-only.

## 8. Testing (mock the WebAuthn API)
support vs unsupported render; start/verify flow; cancel handling; fallback route.

## 9. File structure
`src/features/auth/{PasskeyLogin,MagicLinkFallback}.tsx`,
`lib/{webauthnClient,capabilities}.ts`, `hooks/usePasskeyLogin.ts`

## 10. Acceptance criteria
- [ ] Primary action runs the WebAuthn assertion + redirects on success
- [ ] First-time passkey registration works
- [ ] No authenticator → magic-link fallback; cancel handled quietly
- [ ] Tests pass; no passwords anywhere

## Out of scope (Backend prompt)
Challenge issuance, origin/RP-ID/counter verification, credential storage.
"""


# --- UI / Design prompts (visual & UX; framework-agnostic) -----------------
UI_DS = """# Glassmorphism Auth — Visual Design System & Tokens

## 1. Role & objective
You are a **product/UI designer + design engineer**. Define the **visual design
system** for a glassmorphism authentication surface — tokens and a spec, **not** a
full app. Framework-agnostic: any stack can implement it.

## 2. Deliverables
1. A **design-token set** — CSS custom properties **and** a JSON theme — for color,
   surface, blur, radius, spacing, shadow, typography, and motion.
2. An annotated **single-screen visual spec** for the login card.
3. **Light + dark** variants.

## 3. Color & surface
- Backdrop: animated gradient (violet `#6d28d9` → blue `#2563eb` → cyan `#0891b2`).
- Glass surface: `rgba(255,255,255,.12)`, `backdrop-blur(16px) saturate(140%)`,
  1px border `rgba(255,255,255,.25)`, shadow `0 24px 60px rgba(0,0,0,.35)`.
- Document the **safe text colors** that keep ≥ 4.5:1 on the translucent surface.

## 4. Type & spacing
A type scale (12/14/16/22px) with weights + letter-spacing; an 8px spacing grid;
radii 10/16/20px. Deliver **tokens**, not prose.

## 5. States & motion
Tokens for hover / focus / active / disabled / error; a focus-ring token; a
reduced-motion rule; gradient + press-scale motion durations.

## 6. Accessibility
WCAG 2.1 AA contrast on the translucent surface (list the tested pairs); visible
focus; motion-safe defaults.

## 7. Acceptance criteria
- [ ] Token set (CSS vars + JSON) for color/surface/blur/radius/space/type/motion
- [ ] Light + dark variants that both pass contrast
- [ ] Annotated single-screen spec; focus + reduced-motion defined
- [ ] Framework-agnostic — no component code required

## Out of scope
The React/Vue/etc. implementation — that's a Frontend prompt.
"""

UI_LAYOUT = """# Authentication Screens — Layout & UX Patterns

## 1. Role & objective
You are a **UX/product designer**. Produce a **pattern guide** for authentication
screens (sign-in, sign-up, reset, verify): layout, flows, states, and microcopy.
Framework-agnostic — the output is design guidance + wireframe specs.

## 2. Layouts (specify each)
Centered card vs **split-screen** (marketing + form) vs full-bleed; when to use
each; responsive behaviour (breakpoints, single-column collapse < 768px); a safe
content width (~360–420px form column).

## 3. Flows & states
For each screen define default, focus, loading, success, and **every error** state
(invalid field, wrong credentials, rate-limited, expired link), plus empty/first-run
states. Include a simple flow diagram of the happy path + recovery paths.

## 4. Microcopy
Button labels ("Sign in", "Send reset link"), error messages (explain + fix, no
blame), and neutral security copy (no user enumeration). Deliver a **copy table**.

## 5. Accessibility & inclusivity
Form labelling, the error-summary pattern, focus order, password-manager/autofill
friendliness, reduced-motion, and RTL notes.

## 6. Acceptance criteria
- [ ] Layout patterns with when-to-use + responsive rules
- [ ] A full state matrix per screen incl. error/empty/loading
- [ ] A microcopy table (labels + errors) that's clear and non-enumerating
- [ ] A11y + RTL guidance; a simple flow diagram

## Out of scope
Visual theme/tokens (see the design-system prompt) and implementation code.
"""

UI_MOTION = """# Login Micro-interactions & Motion Spec

## 1. Role & objective
You are a **motion/interaction designer**. Specify the **micro-interactions** for a
login screen so any engineer implements them consistently. Framework-agnostic
motion spec (timings, easings, states) + a small self-contained CSS reference.

## 2. Interactions to define
- Card entrance (fade + rise) — timing + easing.
- Input focus (border/ring transition) + label behaviour.
- Password show/hide toggle transition.
- Button: hover, **press (scale)**, loading (spinner), success (checkmark).
- Error: shake vs fade-in of an `aria-live` banner (make the accessible choice).
- Success → redirect transition.

## 3. Timing system
A duration scale (e.g. 120/200/320ms) + easing tokens (standard, decelerate,
spring-ish) and which interaction uses which. **No magic numbers.**

## 4. Accessibility
**prefers-reduced-motion**: define the reduced variant for every interaction (no
shake, instant state changes). Never rely on motion alone to convey state.

## 5. Deliverables
A motion spec table (interaction → property, duration, easing, reduced-motion
fallback) + a small self-contained CSS reference demonstrating the key ones.

## 6. Acceptance criteria
- [ ] Every listed interaction has duration + easing + reduced-motion fallback
- [ ] A consistent timing/easing token system (no magic numbers)
- [ ] Accessible error signalling (not motion-only)
- [ ] The CSS reference matches the spec

## Out of scope
Full component build (Frontend prompt) and visual tokens (design-system prompt).
"""


PROMPTS: list[dict] = [
    {
        "title": "Modern Glassmorphism Login — React + JWT",
        "description": "Frosted-glass login over an animated gradient with in-memory JWT + httpOnly refresh, Zod validation, and full WCAG AA a11y.",
        "prompt_type": "frontend", "complexity": "advanced",
        "framework": "React", "language": "TypeScript", "ai_model": "claude-opus-4-8",
        "estimated_tokens": 1500,
        "tags": ["login", "glassmorphism", "jwt", "react", "tailwind"],
        "theme": "glass", "content": GLASS,
        "expected_output": (
            "A complete, typed React feature: a frosted-glass `LoginForm` over an animated "
            "gradient, Zod + React Hook Form validation, a `useAuth` hook/provider that keeps the "
            "access token in memory and the refresh token in an httpOnly cookie, an axios "
            "interceptor doing 401 → refresh → retry-once with stampede dedupe, accessible error "
            "states, and RTL + MSW tests — ready to drop in."
        ),
    },
    {
        "title": "Apple-Style Minimal Login — OAuth (Google & Apple)",
        "description": "Minimal Apple-ID-style Next.js sign-in with credentials + Google/Apple OAuth via Auth.js, secure sessions, and open-redirect-safe callbacks.",
        "prompt_type": "frontend", "complexity": "intermediate",
        "framework": "Next.js", "language": "TypeScript", "ai_model": "claude-opus-4-8",
        "estimated_tokens": 1300,
        "tags": ["login", "oauth", "minimal", "nextjs", "social-auth"],
        "theme": "apple", "content": APPLE,
        "expected_output": (
            "A Next.js App Router `/login` with a minimalist centered form (email + password) plus "
            "'Continue with Apple/Google' wired to Auth.js providers, Prisma-backed database "
            "sessions, httpOnly/SameSite=Lax cookies, `OAuthAccountNotLinked` handling, "
            "middleware-guarded `/dashboard`, same-origin `callbackUrl` validation, and Playwright "
            "E2E — secrets server-side only."
        ),
    },
    {
        "title": "Dark SaaS Login with Two-Factor (TOTP)",
        "description": "Two-step dark login (password → 6-digit TOTP) with auto-advancing OTP boxes, paste support, backup codes, and a 5-attempt lockout.",
        "prompt_type": "frontend", "complexity": "advanced",
        "framework": "React", "language": "TypeScript", "ai_model": "claude-opus-4-8",
        "estimated_tokens": 1400,
        "tags": ["login", "2fa", "totp", "dark-mode", "security"],
        "theme": "dark2fa", "content": DARK2FA,
        "expected_output": (
            "A reducer-driven two-step React login: credentials then, when the API returns "
            "`mfa_required`, an accessible 6-box TOTP input (auto-advance, backspace, paste-to-fill, "
            "digit-only, `one-time-code` autofill) verified per RFC 6238, with a backup-code "
            "fallback and server-enforced 5-attempt lockout. The TOTP secret never reaches the "
            "client. Includes unit + component tests."
        ),
    },
    {
        "title": "Passwordless Magic-Link Login",
        "description": "End-to-end passwordless email magic-link auth: single-use 15-min JWT (jti), no user enumeration, rate-limited resend, and an inlined email template.",
        "prompt_type": "frontend", "complexity": "intermediate",
        "framework": "Next.js", "language": "TypeScript", "ai_model": "claude-sonnet-5",
        "estimated_tokens": 1300,
        "tags": ["login", "passwordless", "magic-link", "email", "nextjs"],
        "theme": "magic", "content": MAGIC,
        "expected_output": (
            "A Next.js passwordless flow: a one-field request page that always returns the same "
            "neutral 'check your inbox' state (masked email, 30s-cooldown resend), a signing route "
            "issuing a single-use 15-minute JWT (jti invalidated on use), a callback that verifies + "
            "starts a session + redirects, a friendly expired-link screen, an inlined responsive "
            "email template, and tests for single-use + rate-limit + no enumeration."
        ),
    },
    {
        "title": "Stripe-Style Split-Screen Login (Server Sessions)",
        "description": "Server-rendered Django split-screen login with session auth, CSRF, safe `next` redirects, rate-limiting, and full no-JavaScript support.",
        "prompt_type": "frontend", "complexity": "intermediate",
        "framework": "Django", "language": "Python", "ai_model": "claude-opus-4-8",
        "estimated_tokens": 1200,
        "tags": ["login", "split-screen", "sessions", "django", "csrf"],
        "theme": "stripe", "content": STRIPE,
        "expected_output": (
            "A Django feature: a responsive two-pane login template (gradient marketing panel + "
            "form), a thin `LoginView` backed by a `LoginForm` doing validation, CSRF-protected "
            "session auth with a non-field error (no enumeration), 'remember me' session expiry, "
            "`url_has_allowed_host_and_scheme`-checked `next`, hardened cookie/security settings, "
            "django-axes lockout, and pytest-django tests — works entirely without JavaScript."
        ),
    },
    {
        "title": "Passkey (WebAuthn) Login — Neobrutalist",
        "description": "Passwordless passkey/WebAuthn login (SimpleWebAuthn) with capability detection, magic-link fallback, origin/RP-ID + counter verification, and quiet cancel handling.",
        "prompt_type": "frontend", "complexity": "expert",
        "framework": "React", "language": "TypeScript", "ai_model": "claude-opus-4-8",
        "estimated_tokens": 1500,
        "tags": ["login", "passkeys", "webauthn", "neobrutalism", "passwordless"],
        "theme": "passkey", "content": PASSKEY,
        "expected_output": (
            "A neobrutalist React passkey login using @simplewebauthn/browser: a primary action that "
            "runs the WebAuthn authentication ceremony (server-generated single-use challenge, "
            "origin + RP-ID + signature-counter verification server-side), first-time passkey "
            "registration, on-mount platform-authenticator detection with a magic-link fallback, "
            "quiet `NotAllowedError` cancel handling, and tests mocking the WebAuthn API."
        ),
    },
]


BACKEND_REST = """# Production REST API — FastAPI CRUD Resource (Orders)

## 1. Role & objective
You are a **senior backend engineer**. Build a **production-ready REST resource**
(`/v1/orders`) with a FastAPI service: complete CRUD, pagination, filtering,
auth, validation, error handling, tests, and OpenAPI. Ship every file — no stubs.

## 2. Tech stack (exact)
- **Python 3.12**, **FastAPI**, **Pydantic v2**
- **SQLAlchemy 2.0 async** + **PostgreSQL** (asyncpg); **Alembic** migrations
- **pytest** + httpx `AsyncClient` for tests; **ruff** clean
- Layered architecture: `api → service → repository → model` (no ORM in controllers)

## 3. API contract
| Method | Path | Purpose | Success |
|---|---|---|---|
| POST | `/v1/orders` | Create | `201` + body + `Location` header |
| GET | `/v1/orders` | List (paginated/filtered/sorted) | `200` + page envelope |
| GET | `/v1/orders/{id}` | Retrieve | `200` |
| PATCH | `/v1/orders/{id}` | Partial update | `200` |
| DELETE | `/v1/orders/{id}` | Delete | `204` |

- **List query params:** `page` (≥1), `size` (1–100), `status`, `customer_id`,
  `sort` (`created_at|-created_at|total`), free-text `q`.
- **Envelope:** `{ items, total, page, size, pages }`.

## 4. Schemas (Pydantic v2)
- `OrderCreate { customer_id: UUID, items: list[OrderLine] (min 1), currency: str(3) }`
- `OrderLine { sku: str, qty: int > 0, unit_price_cents: int ≥ 0 }`
- `OrderRead { id, status, total_cents, currency, items, created_at, updated_at }`
- Compute `total_cents` server-side; never trust a client total.

## 5. Auth & authz
- **JWT bearer** (`Authorization: Bearer …`); reject with `401` + `WWW-Authenticate`.
- Row scoping: a caller may only read/modify their **own** orders unless role
  `admin`; otherwise `403`.

## 6. Validation & errors (RFC 9457 problem+json)
- `422` for schema errors (FastAPI default, documented); `404` not found;
  `409` on conflicting state transition; `400` for bad filters.
- Uniform error body: `{ type, title, status, detail, instance }`.

## 7. Idempotency & concurrency
- Support an **`Idempotency-Key`** header on POST (store key→response for 24h;
  replay returns the original result).
- Optimistic concurrency on PATCH via `updated_at`/`If-Match` (ETag) → `412` on mismatch.

## 8. Performance & reliability
- Async DB sessions; connection pooling; **keyset or offset** pagination
  (document tradeoff). Index `orders(customer_id, created_at)` and `orders(status)`.
- N+1-free reads (eager-load lines). Response times budget < 50 ms P50 for reads.

## 9. Observability
- Structured JSON logs with a **request id**; log latency + status.
- `/health` (liveness) and `/health/ready` (DB check). Prometheus `/metrics`
  (request count, latency histogram). OpenTelemetry-ready hooks.

## 10. Security
- Validate + bound all inputs; parameterized queries only (no string SQL).
- Rate-limit writes; CORS allowlist; never leak internal errors/stack traces.

## 11. Testing (pytest, async, in-memory or test DB)
CRUD happy paths; auth 401/403; validation 422; pagination/filter/sort;
idempotent POST replay; ETag `412`; not-found 404. Target ≥ 90% coverage on
service + api layers.

## 12. File structure
```
app/
  api/v1/orders.py            # thin controllers
  services/order_service.py   # business logic (totals, transitions)
  repositories/order_repo.py  # SQLAlchemy access
  models/order.py             # Order, OrderLine
  schemas/order.py            # Pydantic v2
  core/{errors,security,deps}.py
  main.py
alembic/versions/*
tests/test_orders.py
```

## 13. Acceptance criteria
- [ ] All 5 endpoints behave per the contract with correct status codes.
- [ ] `total_cents` computed server-side; client totals ignored.
- [ ] JWT required; users see only their orders (admin sees all).
- [ ] `Idempotency-Key` replays the original create response.
- [ ] Pagination/filter/sort work; queries use the documented indexes.
- [ ] OpenAPI at `/docs` is accurate; ruff clean; tests ≥ 90% pass.

## Out of scope
Payment capture and fulfilment (separate services).
"""

BACKEND_AUTH = """# JWT Authentication & Refresh API — FastAPI

## 1. Role & objective
You are a **senior backend/security engineer**. Build a complete, secure
authentication service: register, login, refresh (with rotation), logout, and
"me". Ship all files, migrations, and tests.

## 2. Tech stack (exact)
- Python 3.12, FastAPI, Pydantic v2
- SQLAlchemy 2.0 async + PostgreSQL; Alembic
- **argon2-cffi** for password hashing; **PyJWT/jose** for tokens
- Redis for refresh-token/rotation + denylist

## 3. Endpoints
| Method | Path | Body | Result |
|---|---|---|---|
| POST | `/v1/auth/register` | email, password, name | `201` user |
| POST | `/v1/auth/login` | email, password | `200` `{access_token, expires_in}` + refresh cookie |
| POST | `/v1/auth/refresh` | (refresh cookie) | `200` new access + **rotated** refresh |
| POST | `/v1/auth/logout` | (refresh cookie) | `204` (revoke) |
| GET | `/v1/auth/me` | bearer | `200` current user |

## 4. Token design
- **Access token:** JWT, 15 min, claims `sub, role, iat, exp, jti, typ=access`;
  signed HS256 (or RS256 with a documented key).
- **Refresh token:** opaque random (or JWT `typ=refresh`), **30 days**, stored
  **hashed** server-side, delivered as **httpOnly, Secure, SameSite=Strict** cookie.
- **Rotation:** each refresh issues a new refresh token and **invalidates the old
  one**; detect reuse of a revoked refresh → revoke the whole family (theft response).

## 5. Password & account rules
- argon2id hashing (tuned params); enforce min length 8, max 128; reject breached
  passwords (optional k-anonymity check). Constant-time verify.
- Email verification token flow (issue + verify endpoints stubbed but wired).
- Generic responses — **never reveal whether an email exists**.

## 6. Security hardening
- Rate-limit login + refresh per IP + account; lockout/backoff on abuse.
- Access denylist by `jti` for immediate revocation (Redis, TTL = token exp).
- CSRF: refresh cookie is `SameSite=Strict`; document double-submit fallback.
- No secrets/PII in logs; structured audit log for auth events.

## 7. Errors (problem+json)
`401` invalid credentials/expired token; `403` unverified/locked; `409` email
taken; `422` validation. Uniform error body.

## 8. Testing
Register (dupe 409), login success/fail, `/me` with/without token, refresh
rotation, **refresh reuse → family revoke**, logout revokes, lockout after N
fails, expired access → 401. ≥ 90% coverage.

## 9. File structure
```
app/
  api/v1/auth.py
  services/auth_service.py    # register/authenticate/rotate/revoke
  security/{tokens,passwords}.py
  repositories/{user_repo,refresh_repo}.py
  models/user.py
  schemas/auth.py
  core/deps.py                # get_current_user, roles
tests/test_auth.py
```

## 10. Acceptance criteria
- [ ] Access token 15 min; refresh 30 days as httpOnly/Secure/SameSite=Strict cookie.
- [ ] Refresh **rotates** and invalidates the previous token.
- [ ] Reusing a revoked refresh revokes the entire token family.
- [ ] Passwords argon2id; no user enumeration; constant-time verify.
- [ ] Logout + `jti` denylist revoke access immediately.
- [ ] Rate-limit/lockout active; tests ≥ 90% pass; ruff clean.

## Out of scope
OAuth/social login and MFA (separate prompts).
"""

BACKEND_JOBS = """# Async Background Jobs — Celery + Redis

## 1. Role & objective
You are a **senior backend engineer**. Add reliable **asynchronous background
processing** (e.g. report generation, email, thumbnails) to an API, with an
enqueue endpoint, workers, retries, idempotency, and status polling. Ship all files.

## 2. Tech stack (exact)
- Python 3.12, FastAPI (producer) + **Celery 5** workers
- **Redis** as broker + result backend (or RabbitMQ broker documented)
- SQLAlchemy async for a `jobs` table (source of truth for status)
- pytest + Celery eager mode for tests

## 3. Flow & endpoints
- `POST /v1/reports:generate { params }` → create a `jobs` row (`queued`),
  enqueue a Celery task, return **`202 Accepted`** + `{ task_id, poll }`.
- `GET /v1/tasks/{id}` → `{ state: queued|started|success|failure|retry, result?, error? }`.
- Worker updates the `jobs` row at each transition (single source of truth — do
  **not** rely on the result backend alone).

## 4. Reliability requirements
- **Idempotency:** tasks keyed so a duplicate enqueue (same idempotency key) does
  not run twice; use `acks_late=True` + `task_reject_on_worker_lost=True`.
- **Retries:** exponential backoff with jitter, capped attempts; only retry
  **transient** errors; send terminal failures to a **dead-letter** queue.
- **Timeouts:** soft + hard time limits per task; graceful shutdown drains tasks.
- **Concurrency:** separate queues/priorities (e.g. `emails`, `reports`); document
  prefetch + concurrency tuning.

## 5. Observability
- Correlate API request id → task id in logs; structured JSON logs.
- Metrics: queue depth, task latency, success/failure/retry counts (Flower or
  Prometheus exporter). Alert on DLQ growth.

## 6. Security & safety
- Validate task params (Pydantic) before enqueue; never enqueue untrusted callables.
- Enforce per-user quotas/rate-limits on enqueue; authorize the poll endpoint to
  the task owner.

## 7. Testing
Enqueue returns 202 + persists `queued`; task success updates row + result;
transient error retries then succeeds; permanent error → failure + DLQ;
idempotent double-enqueue runs once; poll authorization. Celery eager mode.

## 8. File structure
```
app/
  api/v1/reports.py           # enqueue + poll
  workers/celery_app.py       # Celery config (queues, retries, limits)
  workers/tasks/reports.py    # the task
  services/job_service.py     # create/update jobs rows
  models/job.py
  schemas/job.py
tests/test_jobs.py
docker-compose.worker.yml     # api + worker + redis
```

## 9. Acceptance criteria
- [ ] Enqueue returns `202` and a `jobs` row in `queued`; poll reflects transitions.
- [ ] Transient failures retry with capped exponential backoff + jitter.
- [ ] Terminal failures land in a dead-letter queue; row marked `failure`.
- [ ] Duplicate enqueue (idempotency key) executes exactly once.
- [ ] `acks_late` + time limits + graceful drain configured.
- [ ] Poll authorized to owner; tests pass; ruff clean.

## Out of scope
Cron/beat scheduling (can be added via Celery Beat separately).
"""

DB_MULTI = """# Multi-Tenant SaaS Schema with Row-Level Security (PostgreSQL)

## 1. Role & objective
You are a **senior data engineer / DBA**. Design a **secure multi-tenant**
PostgreSQL schema where every tenant's data is isolated via **Row-Level Security
(RLS)**. Deliver DDL, RLS policies, roles, indexes, migration, and tests.

## 2. Engine & approach
- **PostgreSQL 16**. Model: **shared database, shared schema, `tenant_id` column**
  on every tenant-owned table, enforced by **RLS** (not just app code).
- Tenant context set per request via `SET app.tenant_id = '<uuid>'` (or
  `set_config`), read in policies through `current_setting('app.tenant_id')`.

## 3. Core tables (DDL)
- `tenants(id uuid pk, name, plan, created_at)`
- `users(id uuid pk, tenant_id uuid not null → tenants, email citext, role, ...)`
  with **unique(tenant_id, email)** (emails unique *per tenant*).
- `projects(id uuid pk, tenant_id uuid not null → tenants, name, ...)`
- `audit_log(id, tenant_id, actor_id, action, target, at)`
- Every tenant-owned table: `tenant_id uuid not null references tenants(id)`,
  `created_at timestamptz default now()`, `updated_at` via trigger.

## 4. Row-Level Security
- `ALTER TABLE … ENABLE ROW LEVEL SECURITY; … FORCE ROW LEVEL SECURITY;`
- Policy per table:
  `USING (tenant_id = current_setting('app.tenant_id')::uuid)` for SELECT/UPDATE/
  DELETE, and `WITH CHECK (…)` for INSERT/UPDATE so rows can't be written into
  another tenant.
- A separate **`bypass_rls`** role for migrations/back-office only.

## 5. Roles & privileges
- `app_rw` (application) — DML only, subject to RLS; no DDL.
- `app_ro` (read replicas/reporting) — SELECT only, subject to RLS.
- `migrator` — owns objects, `BYPASSRLS`, used solely by migrations.

## 6. Integrity & indexes
- FKs `ON DELETE CASCADE` from tenant-owned rows to `tenants` (documented).
- Composite indexes lead with `tenant_id`, e.g. `projects(tenant_id, created_at)`,
  `users(tenant_id, email)`. Partial indexes for hot filters.
- `updated_at` maintained by a `BEFORE UPDATE` trigger.

## 7. Migrations & seeding
- Provide forward + rollback migrations (Alembic or raw SQL) that create tables,
  enable/force RLS, and install policies. Idempotent, reviewable.
- Seed 2 tenants with overlapping emails to prove per-tenant uniqueness + isolation.

## 8. Testing (pytest + psql)
- Set `app.tenant_id = A` → queries return only A's rows; **B's rows invisible**.
- Insert with A's context but B's `tenant_id` → **blocked by WITH CHECK**.
- Same email in two tenants allowed; duplicate within a tenant rejected.
- `app_rw` cannot bypass RLS; `migrator` can.

## 9. Deliverables
`schema.sql` (tables), `policies.sql` (RLS), `roles.sql`, migration up/down,
`seed.sql`, and a `README` explaining how the app sets tenant context.

## 10. Acceptance criteria
- [ ] Every tenant table has `tenant_id` + FORCE RLS + USING/WITH CHECK policies.
- [ ] Cross-tenant reads/writes are impossible for `app_rw`.
- [ ] Emails unique per tenant, not globally.
- [ ] Indexes lead with `tenant_id`; `updated_at` trigger works.
- [ ] Migrations apply and roll back cleanly; tests prove isolation.

## Out of scope
Sharding / database-per-tenant (a different isolation model).
"""

DB_ECOM = """# E-Commerce Orders & Inventory Schema (PostgreSQL)

## 1. Role & objective
You are a **senior data engineer**. Design a correct, concurrency-safe
**orders + inventory** schema in PostgreSQL that prevents overselling and keeps
money exact. Deliver DDL, constraints, indexes, key transactions, and tests.

## 2. Engine & principles
- **PostgreSQL 16**. Money as **integer cents** (`bigint`), never float.
- Enforce invariants in the **database** (constraints), not only the app.

## 3. Schema (DDL)
- `products(id, sku citext unique, name, active bool, created_at)`
- `product_variants(id, product_id → products, sku unique, price_cents bigint check ≥ 0)`
- `inventory(variant_id pk → product_variants, on_hand int check ≥ 0, reserved int check ≥ 0,
   check (reserved ≤ on_hand))`
- `customers(id, email citext unique, …)`
- `orders(id, customer_id → customers, status order_status not null default 'pending',
   currency char(3), total_cents bigint check ≥ 0, created_at, updated_at)`
- `order_items(id, order_id → orders on delete cascade, variant_id → product_variants,
   qty int check (qty > 0), unit_price_cents bigint check ≥ 0,
   unique(order_id, variant_id))`
- `payments(id, order_id → orders, amount_cents, provider, status, created_at)`
- ENUM `order_status = ('pending','paid','shipped','cancelled','refunded')`.

## 4. Integrity rules
- `orders.total_cents` = Σ(`qty * unit_price_cents`) — enforce via a trigger or a
  documented app-side recompute; add a `CHECK` where feasible.
- Valid status transitions only (pending→paid→shipped, →cancelled/refunded);
  enforce with a trigger or a transition table.
- Prices on `order_items` are **snapshots** (copied at purchase), independent of
  later variant price changes.

## 5. Concurrency — no overselling
- Reserving stock uses a single atomic statement:
  `UPDATE inventory SET reserved = reserved + :qty
   WHERE variant_id = :v AND on_hand - reserved >= :qty` and checks `rowcount = 1`.
- Wrap checkout in a transaction with appropriate isolation; document
  `SELECT … FOR UPDATE` vs the conditional-update approach and why.

## 6. Indexes & performance
- `orders(customer_id, created_at desc)`, `orders(status, created_at)`,
  `order_items(order_id)`, `product_variants(product_id)`.
- Partial index `orders(created_at) WHERE status = 'pending'` for reaping abandoned carts.

## 7. Migrations & seeding
- Forward + rollback migrations; seed a few products/variants/inventory and a
  sample paid order for tests.

## 8. Testing (pytest + psql)
- Concurrent reservations of the last unit: exactly one succeeds (no oversell).
- Negative/zero qty rejected; `reserved ≤ on_hand` enforced.
- Order total matches item sum; illegal status transition blocked.
- Item price snapshot unaffected by later variant price change.

## 9. Deliverables
`schema.sql`, `constraints_triggers.sql`, `indexes.sql`, migration up/down,
`seed.sql`, and a short doc of the checkout transaction.

## 10. Acceptance criteria
- [ ] Money is integer cents; all amounts `CHECK ≥ 0`.
- [ ] Concurrent last-unit checkout never oversells.
- [ ] `reserved ≤ on_hand` and positive quantities enforced by constraints.
- [ ] Item prices are purchase-time snapshots.
- [ ] Status transitions validated; totals consistent; indexes present.

## Out of scope
Tax/shipping calculation and payment-provider integration.
"""

DB_OPT = """# Query Optimization & Indexing Playbook (PostgreSQL)

## 1. Role & objective
You are a **senior performance/database engineer**. Take a slow, real-world query
and make it fast the right way — with `EXPLAIN (ANALYZE, BUFFERS)`, correct
indexes, and query rewrites — and document the method as a reusable playbook.

## 2. Scenario
`events(id bigint, user_id bigint, type text, created_at timestamptz, payload jsonb)`
with tens of millions of rows. The endpoint runs:
```sql
SELECT * FROM events
WHERE user_id = $1 AND type = 'purchase'
  AND created_at >= now() - interval '30 days'
ORDER BY created_at DESC
LIMIT 50;
```
Baseline: a **Seq Scan**, ~1.2 s. Target: **< 10 ms**, index-only where possible.

## 3. Method (do in order, show output at each step)
1. **Measure:** `EXPLAIN (ANALYZE, BUFFERS)` the query; capture plan, rows, timing,
   buffers. Identify the bottleneck (Seq Scan, sort, heap fetches).
2. **Index for the access pattern:** a **composite** index matching filter +
   sort order:
   `CREATE INDEX CONCURRENTLY idx_events_user_type_created
      ON events (user_id, type, created_at DESC);`
   Explain why column order matters (equality cols first, range/sort last).
3. **Consider partial/covering:** partial index `WHERE type = 'purchase'` if that's
   hot; `INCLUDE (…)` columns to enable **Index-Only Scans** (watch visibility map).
4. **Rewrite anti-patterns:** avoid functions on indexed columns
   (`created_at::date` breaks the index), `SELECT *` when few columns are needed,
   `OR` that defeats indexes, and implicit type casts on `user_id`.
5. **Re-measure** and compare plans (Index Scan / Index-Only Scan) + timing + buffers.

## 4. Maintenance & correctness
- Use `CREATE INDEX CONCURRENTLY` in production (no long locks); note the tradeoffs.
- `ANALYZE` after large changes so the planner has fresh stats; discuss
  `default_statistics_target` for skewed columns.
- Beware over-indexing (write amplification); justify each index.
- For time-series growth, mention **partitioning by range(created_at)** and how
  indexes interact with partitions.

## 5. Deliverables
- The before/after `EXPLAIN (ANALYZE, BUFFERS)` plans.
- The `CREATE INDEX` statements (concurrent) + rationale for column order.
- The rewritten query (explicit columns, sargable predicates).
- A short **playbook** section others can reuse (measure → index → rewrite → verify).

## 6. Acceptance criteria
- [ ] Before/after plans included; bottleneck identified from `BUFFERS`.
- [ ] Composite index matches equality-then-range/sort; query hits it.
- [ ] Query rewritten to be sargable (no functions on indexed cols, no `SELECT *`).
- [ ] Index-Only or Index Scan replaces the Seq Scan; timing < 10 ms.
- [ ] Concurrency-safe index build + `ANALYZE`/partitioning notes included.

## Out of scope
Application-level caching (Redis) — complementary but a separate concern.
"""


PROMPTS += [
    {
        "title": "Production REST API — FastAPI CRUD Resource",
        "description": "A complete, layered FastAPI orders resource: CRUD, pagination/filtering, JWT authz, idempotency, ETags, problem+json errors, OpenAPI, and tests.",
        "prompt_type": "backend", "complexity": "advanced",
        "framework": "FastAPI", "language": "Python", "ai_model": "claude-opus-4-8",
        "estimated_tokens": 1600, "tags": ["api", "rest", "fastapi", "crud", "backend"],
        "theme": "rest_api", "content": BACKEND_REST,
        "expected_output": (
            "A layered FastAPI service exposing `/v1/orders` with full CRUD, paginated/filtered/"
            "sorted listing, JWT auth with per-user row scoping, server-computed totals, "
            "`Idempotency-Key` replay, ETag optimistic concurrency (412), RFC 9457 problem+json "
            "errors, health/metrics endpoints, Alembic migrations, accurate OpenAPI, and an async "
            "pytest suite — controllers stay thin, ORM lives only in repositories."
        ),
    },
    {
        "title": "JWT Authentication & Refresh API — FastAPI",
        "description": "Secure auth service: argon2id passwords, 15-min access JWT + rotating httpOnly refresh tokens with reuse detection, jti denylist, lockout, and tests.",
        "prompt_type": "backend", "complexity": "advanced",
        "framework": "FastAPI", "language": "Python", "ai_model": "claude-opus-4-8",
        "estimated_tokens": 1600, "tags": ["auth", "jwt", "security", "fastapi", "backend"],
        "theme": "auth_api", "content": BACKEND_AUTH,
        "expected_output": (
            "A FastAPI auth service (register/login/refresh/logout/me) with argon2id hashing, "
            "15-minute access JWTs, 30-day refresh tokens stored hashed and delivered as "
            "httpOnly/Secure/SameSite=Strict cookies, **refresh rotation with reuse→family-revoke**, "
            "a jti denylist for instant revocation, rate-limit + lockout, no user enumeration, and a "
            "≥90% pytest suite."
        ),
    },
    {
        "title": "Async Background Jobs — Celery + Redis",
        "description": "Reliable async processing: 202-accepted enqueue + status polling, idempotent tasks, exponential-backoff retries, dead-letter queue, time limits, and observability.",
        "prompt_type": "backend", "complexity": "advanced",
        "framework": "Celery", "language": "Python", "ai_model": "claude-opus-4-8",
        "estimated_tokens": 1500, "tags": ["async", "celery", "redis", "queue", "backend"],
        "theme": "jobs_api", "content": BACKEND_JOBS,
        "expected_output": (
            "A FastAPI producer + Celery/Redis workers: an enqueue endpoint returning `202` and a "
            "persisted `jobs` row, a status-poll endpoint, idempotent tasks (`acks_late`, exactly-"
            "once via idempotency key), capped exponential-backoff retries with jitter, a dead-letter "
            "queue for terminal failures, soft/hard time limits + graceful drain, per-queue "
            "concurrency, metrics/logging correlation, and Celery-eager tests."
        ),
    },
    {
        "title": "Multi-Tenant SaaS Schema with Row-Level Security (Postgres)",
        "description": "Shared-schema multi-tenancy enforced by PostgreSQL RLS: tenant_id everywhere, FORCE RLS USING/WITH CHECK policies, scoped roles, tenant-leading indexes, and isolation tests.",
        "prompt_type": "database", "complexity": "expert",
        "framework": "PostgreSQL", "language": "SQL", "ai_model": "claude-opus-4-8",
        "estimated_tokens": 1500, "tags": ["postgres", "multi-tenant", "rls", "security", "schema"],
        "theme": "db_multitenant", "content": DB_MULTI,
        "expected_output": (
            "A PostgreSQL multi-tenant schema where every tenant-owned table carries `tenant_id` and "
            "has FORCE ROW LEVEL SECURITY with USING + WITH CHECK policies keyed on "
            "`current_setting('app.tenant_id')`, scoped roles (`app_rw`/`app_ro`/`migrator` with "
            "BYPASSRLS), per-tenant unique emails, tenant-leading composite indexes, an `updated_at` "
            "trigger, up/down migrations, and pytest proving cross-tenant reads/writes are impossible."
        ),
    },
    {
        "title": "E-Commerce Orders & Inventory Schema (Postgres)",
        "description": "Concurrency-safe orders + inventory: integer-cents money, CHECK/constraint-enforced invariants, no-oversell atomic reservation, price snapshots, indexes, and tests.",
        "prompt_type": "database", "complexity": "advanced",
        "framework": "PostgreSQL", "language": "SQL", "ai_model": "claude-opus-4-8",
        "estimated_tokens": 1500, "tags": ["postgres", "ecommerce", "schema", "transactions", "inventory"],
        "theme": "db_ecommerce", "content": DB_ECOM,
        "expected_output": (
            "A PostgreSQL orders/inventory schema with money as integer cents, DB-enforced invariants "
            "(`on_hand ≥ 0`, `reserved ≤ on_hand`, positive quantities, `≥ 0` amounts), an atomic "
            "no-oversell reservation (`UPDATE … WHERE on_hand - reserved >= qty`), purchase-time price "
            "snapshots on order items, validated status transitions, the right composite/partial "
            "indexes, migrations + seed, and tests proving concurrent last-unit checkout never oversells."
        ),
    },
    {
        "title": "Query Optimization & Indexing Playbook (Postgres)",
        "description": "Turn a 1.2s Seq Scan into a <10ms Index Scan: EXPLAIN(ANALYZE,BUFFERS), a composite index matching filter+sort, sargable rewrites, CONCURRENTLY builds, and before/after plans.",
        "prompt_type": "database", "complexity": "advanced",
        "framework": "PostgreSQL", "language": "SQL", "ai_model": "claude-opus-4-8",
        "estimated_tokens": 1400, "tags": ["postgres", "performance", "indexing", "explain", "optimization"],
        "theme": "db_optimize", "content": DB_OPT,
        "expected_output": (
            "A step-by-step optimization: `EXPLAIN (ANALYZE, BUFFERS)` to find the Seq-Scan "
            "bottleneck, a composite index `(user_id, type, created_at DESC)` (equality-then-range/"
            "sort) built `CONCURRENTLY`, optional partial/covering index for Index-Only Scans, "
            "sargable query rewrites (no functions on indexed columns, explicit columns), and "
            "before/after plans showing ~1.2 s → < 10 ms — plus a reusable measure→index→rewrite→"
            "verify playbook and partitioning notes."
        ),
    },
]


PROMPTS += [
    {
        "title": "Glassmorphism Auth — Visual Design System & Tokens",
        "description": "A framework-agnostic design-token set (CSS vars + JSON) and annotated visual spec for a glassmorphism auth surface, with light/dark variants that pass contrast.",
        "prompt_type": "ui", "complexity": "intermediate",
        "framework": None, "language": None, "ai_model": "claude-opus-4-8",
        "estimated_tokens": 900, "tags": ["design-system", "tokens", "glassmorphism", "ui", "accessibility"],
        "theme": "glass", "content": UI_DS,
        "expected_output": (
            "A design-token set (CSS custom properties + a JSON theme) covering color, glass "
            "surface/blur, radius, spacing, shadow, typography, and motion, plus an annotated "
            "single-screen spec for the login card — with light and dark variants that both meet "
            "WCAG AA contrast and a defined focus ring + reduced-motion rule. No framework code."
        ),
    },
    {
        "title": "Authentication Screens — Layout & UX Patterns",
        "description": "A framework-agnostic pattern guide for sign-in/up/reset/verify: layouts, a full state matrix (error/empty/loading), non-enumerating microcopy, and a11y/RTL guidance.",
        "prompt_type": "ui", "complexity": "intermediate",
        "framework": None, "language": None, "ai_model": "claude-opus-4-8",
        "estimated_tokens": 900, "tags": ["ux", "layout", "patterns", "microcopy", "ui"],
        "theme": "apple", "content": UI_LAYOUT,
        "expected_output": (
            "A UX pattern guide for auth screens: when to use centered vs split-screen vs full-bleed "
            "layouts with responsive rules, a per-screen state matrix (default/focus/loading/success "
            "and every error + empty state), a clear non-enumerating microcopy table, a11y + RTL "
            "notes, and a simple happy-path/recovery flow diagram — no visual theme or code."
        ),
    },
    {
        "title": "Login Micro-interactions & Motion Spec",
        "description": "A framework-agnostic motion spec for a login screen: a duration/easing token system, per-interaction timings, accessible error signalling, and reduced-motion fallbacks + a CSS reference.",
        "prompt_type": "ui", "complexity": "intermediate",
        "framework": None, "language": None, "ai_model": "claude-sonnet-5",
        "estimated_tokens": 850, "tags": ["motion", "micro-interactions", "animation", "accessibility", "ui"],
        "theme": "dark2fa", "content": UI_MOTION,
        "expected_output": (
            "A motion spec table mapping each login micro-interaction (card entrance, input focus, "
            "password toggle, button press/loading/success, error banner, redirect) to a property, "
            "duration, and easing from a small consistent token system — with a prefers-reduced-motion "
            "fallback for every one and a self-contained CSS reference implementing the key ones."
        ),
    },
]


def main() -> None:
    with httpx.Client(base_url=BASE, timeout=30.0) as client:
        client.post("/auth/register", json=AUTHOR)  # 409 if present — fine
        tok = client.post(
            "/auth/login",
            data={"username": AUTHOR["email"], "password": AUTHOR["password"]},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        tok.raise_for_status()
        headers = {"Authorization": f"Bearer {tok.json()['access_token']}"}

        existing = {
            p["title"]: p["id"]
            for p in client.get("/prompts", params={"size": 100}).json()["items"]
        }

        for spec in PROMPTS:
            spec = dict(spec)
            theme = THEMES[spec.pop("theme")]
            anim = render(theme)

            # Replace any prior version so the detailed content is authoritative.
            if spec["title"] in existing:
                client.delete(f"/prompts/{existing[spec['title']]}", headers=headers)

            resp = client.post("/prompts", json=spec, headers=headers)
            resp.raise_for_status()
            pid = resp.json()["id"]
            client.post(
                f"/prompts/{pid}/assets",
                json={"kind": "generated_html", "content": anim,
                      "caption": "Animated result preview"},
                headers=headers,
            )
            print(f"seeded ({len(spec['content'])} chars): {spec['title']}")

        total = client.get("/prompts", params={"size": 1}).json()["total"]
        print(f"\nDone. Library has {total} detailed prompts, each with an animated preview.")


if __name__ == "__main__":
    main()
