#!/usr/bin/env python3
"""ノートのフォルダ・type・フロントマターのルールを検証する。

ルールの説明は AGENTS.md にあり、正はこのファイルの定義。

使い方:
  check_notes.py [FILE...]   指定したファイルを検証（省略時はノート全体）
  check_notes.py --changed   git で変更・未追跡の .md だけを検証
  check_notes.py --staged    git でステージ済みの .md だけを検証
  check_notes.py --hook      Claude Code の PostToolUse / Stop フックとして動く
"""

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

ALL_TYPES = {
    "daily", "meeting", "note", "decision", "concept",
    "howto", "research", "spec", "report", "person", "reference", "index",
}

DATED = re.compile(r"^\d{4}-\d{2}-\d{2}_.+\.md$")
PERIOD = re.compile(r"^\d{4}(-(H[12]|Q[1-4]))?$")

# projects/ と areas/ のファイル名に付ける type ごとの接頭辞（YYYY-MM-DD_<接頭辞>_<タイトル>.md）。note は接頭辞なし
PREFIXES = {"meeting": "mtg", "decision": "dec", "research": "rsc", "spec": "spec", "howto": "howto", "report": "rpt"}
PREFIX = re.compile(r"^\d{4}-\d{2}-\d{2}_([a-z]+)_")

# people/ のファイル名は <会社名>_<名前>.md。自社の人は tags に internal、それ以外は external を入れる
# 自社名（ファイル名に使う表記）。グループ会社なども社内扱いにするならここに追加する
INTERNAL_ORGS = {"XYZ"}
PERSON_NAME = re.compile(r"^([^_]+)_(.+)\.md$")

# フォルダ → 許可する type とファイル名ルール（index.md はどこでも type: index）
FOLDERS = {
    "daily": {"types": {"daily"}, "name": re.compile(r"^\d{4}-\d{2}-\d{2}_daily\.md$")},
    "projects": {"types": {"meeting", "note", "decision", "research", "spec", "report"}, "name": DATED, "prefixed": True},
    "areas": {"types": {"meeting", "note", "decision", "howto", "report"}, "name": DATED, "prefixed": True},
    "knowledge": {"types": {"concept", "howto", "reference"}, "name": "undated"},
    "people": {"types": {"person"}, "name": "undated"},
    "inbox": {"types": {"note"}, "name": DATED},
    "archive": {"types": ALL_TYPES - {"index"}, "name": None},
}

FOLDER_LIST = ", ".join(f"{f}/" for f in sorted(FOLDERS))
ROOT_ALLOWED = {"README.md", "AGENTS.md", "CLAUDE.md", "GEMINI.md"}
IGNORED_DIRS = {".git", ".vscode", ".claude", ".githooks", "scripts", "node_modules"}

REQUIRED_KEYS = ["type", "title", "description", "tags", "timestamp"]
TIMESTAMP = re.compile(r"^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}(:\d{2})?(Z|[+-]\d{2}:?\d{2})?)?$")


def parse_frontmatter(text):
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    fm = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return fm
        m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if m:
            fm[m.group(1)] = m.group(2).strip().strip("\"'")
    return None


def check_location(rel):
    """パスからフォルダルールを返す。エラーなら文字列のリスト。"""
    parts = rel.parts
    if len(parts) == 1:
        if parts[0] in ROOT_ALLOWED:
            return None, []
        return None, [f"ルート直下にノートは置けません。{FOLDER_LIST} のいずれかに置いてください"]
    top = parts[0]
    if top not in FOLDERS:
        return None, [f"未定義のフォルダ '{top}/' です。使えるのは {FOLDER_LIST} です"]
    errors = []
    if parts[-1] != "index.md":
        if top == "projects" and (len(parts) != 4 or not PERIOD.match(parts[2])):
            errors.append("projects のノートは projects/<プロジェクト名>/<期間>/<ファイル> に置いてください（期間の例: 2026, 2026-H1, 2026-Q3）")
        if top == "areas" and len(parts) != 3:
            errors.append("areas のノートは areas/<担当名>/<ファイル> に置いてください")
        if top in ("daily", "knowledge", "people", "inbox") and len(parts) != 2:
            errors.append(f"{top}/ にはサブフォルダを作らず直下に置いてください")
    return FOLDERS[top], errors


def check_file(path):
    path = Path(path).resolve()
    try:
        rel = path.relative_to(ROOT)
    except ValueError:
        return []
    if path.suffix != ".md" or rel.parts[0] in IGNORED_DIRS:
        return []
    rule, errors = check_location(rel)
    if rule is None and not errors:
        return []
    if not path.exists():
        return errors

    name = path.name
    fm = parse_frontmatter(path.read_text(encoding="utf-8"))
    if fm is None:
        return errors + ["先頭に --- で囲んだ OKF フロントマターがありません"]

    for key in REQUIRED_KEYS:
        if key not in fm:
            errors.append(f"フロントマターに '{key}' がありません")
    t = fm.get("type", "")
    if not t:
        errors.append("type が空です")
    elif t not in ALL_TYPES:
        errors.append(f"type '{t}' は未定義です。使えるのは {', '.join(sorted(ALL_TYPES))} です")
    elif name == "index.md":
        if t != "index":
            errors.append("index.md の type は index にしてください")
    elif t == "index":
        errors.append("type: index は index.md 専用です")
    elif rule and t not in rule["types"]:
        errors.append(f"{rel.parts[0]}/ に置ける type は {', '.join(sorted(rule['types']))} です（現在: {t}）")
    if "title" in fm and not fm["title"]:
        errors.append("title が空です")
    if fm.get("timestamp") and not TIMESTAMP.match(fm["timestamp"]):
        errors.append(f"timestamp '{fm['timestamp']}' が ISO 8601 形式ではありません（例: 2026-10-13T14:05:00+09:00）")

    if rule and name != "index.md":
        pattern = rule["name"]
        if pattern == "undated" and re.match(r"^\d{4}-\d{2}-\d{2}", name):
            errors.append("このフォルダのファイル名に日付を付けないでください（例: okr.md）")
        elif isinstance(pattern, re.Pattern) and not pattern.match(name):
            expected = "YYYY-MM-DD_daily.md" if rel.parts[0] == "daily" else "YYYY-MM-DD_<タイトル>.md"
            errors.append(f"ファイル名は {expected} の形式にしてください")
        elif rule.get("prefixed") and t in rule["types"]:
            m = PREFIX.match(name)
            actual = m.group(1) if m and m.group(1) in PREFIXES.values() else None
            want = PREFIXES.get(t)
            if actual != want:
                expected = f"YYYY-MM-DD_{want}_<タイトル>.md" if want else "YYYY-MM-DD_<タイトル>.md（接頭辞なし）"
                errors.append(f"type: {t} のファイル名は {expected} にしてください")
        if rel.parts[0] == "people" and t == "person":
            m = PERSON_NAME.match(name)
            if not m:
                errors.append("ファイル名は <会社名>_<名前>.md にしてください（例: ABC商事_田中.md）")
            else:
                tags = {x.strip().strip("\"'") for x in fm.get("tags", "").strip("[]").split(",")}
                want = "internal" if m.group(1) in INTERNAL_ORGS else "external"
                other = "external" if want == "internal" else "internal"
                if want not in tags or other in tags:
                    who = "自社" if want == "internal" else "社外"
                    errors.append(f"{m.group(1)} は{who}なので tags に {want} を入れてください（{other} は入れない。自社名は scripts/check_notes.py の INTERNAL_ORGS）")
    return errors


def git_files(*args):
    out = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True).stdout
    return [ROOT / line for line in out.splitlines() if line.endswith(".md")]


def all_notes():
    return [p for p in ROOT.rglob("*.md") if p.relative_to(ROOT).parts[0] not in IGNORED_DIRS]


def report(paths):
    problems = {}
    for p in paths:
        errs = check_file(p)
        if errs:
            problems[Path(p).resolve().relative_to(ROOT)] = errs
    lines = []
    for rel, errs in problems.items():
        lines.append(f"{rel}:")
        lines.extend(f"  - {e}" for e in errs)
    return lines


def run_hook():
    data = json.load(sys.stdin)
    if data.get("hook_event_name") == "Stop":
        if data.get("stop_hook_active"):
            return 0
        paths = git_files("ls-files", "--modified", "--others", "--exclude-standard")
    else:
        fp = data.get("tool_input", {}).get("file_path") or data.get("tool_response", {}).get("filePath")
        paths = [fp] if fp else []
    lines = report(paths)
    if lines:
        print("ノートのルール違反があります。AGENTS.md に従って修正してください:", file=sys.stderr)
        print("\n".join(lines), file=sys.stderr)
        return 2
    return 0


def main(argv):
    if argv[:1] == ["--hook"]:
        return run_hook()
    if argv[:1] == ["--changed"]:
        paths = git_files("ls-files", "--modified", "--others", "--exclude-standard")
    elif argv[:1] == ["--staged"]:
        paths = git_files("diff", "--cached", "--name-only", "--diff-filter=ACMR")
    else:
        paths = argv or all_notes()
    lines = report(paths)
    if lines:
        print("\n".join(lines), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
