#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GitHub Projects 自動セットアップ"""

import json
import os
import shutil
import subprocess
import sys

OWNER = "anbx-Hayate"
REPO = "Task_management"
PROJECT_TITLE = "タスク管理ボード"


def find_gh():
    for path in [
        r"C:\Program Files\GitHub CLI\gh.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\GitHub CLI\gh.exe"),
    ]:
        if os.path.exists(path):
            return path
    found = shutil.which("gh")
    if found:
        return found
    raise RuntimeError("GitHub CLI (gh) が見つかりません。")


GH = find_gh()


def run(args, check=True):
    result = subprocess.run([GH, *args], capture_output=True, text=True, encoding="utf-8")
    if check and result.returncode != 0:
        raise RuntimeError(result.stderr or result.stdout)
    return result.stdout.strip()


def graphql(query, variables=None):
    args = ["api", "graphql", "-f", f"query={query}"]
    if variables:
        for key, value in variables.items():
            flag = "-F" if isinstance(value, (int, float, bool)) else "-f"
            args.extend([flag, f"{key}={value}"])
    result = subprocess.run([GH, *args], capture_output=True, text=True, encoding="utf-8")
    data = json.loads(result.stdout)
    if data.get("errors"):
        raise RuntimeError(json.dumps(data["errors"], ensure_ascii=False, indent=2))
    return data["data"]


def main():
    print("==> 認証確認...")
    run(["auth", "status"])

    print("==> ラベル作成...")
    labels = [
        ("大タスク", "7057ff", "大タスク（親 Issue）"),
        ("中タスク", "1d76db", "中タスク（Sub-Issue）"),
        ("小タスク", "0e8a16", "小タスク（実作業単位）"),
        ("振り返り待ち", "fbca04", "振り返り未記入の大タスク"),
    ]
    for name, color, desc in labels:
        check = subprocess.run(
            [GH, "api", f"repos/{OWNER}/{REPO}/labels/{name}"],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        if check.returncode != 0:
            run([
                "api", "-X", "POST", f"repos/{OWNER}/{REPO}/labels",
                "-f", f"name={name}",
                "-f", f"color={color}",
                "-f", f"description={desc}",
            ])
            print(f"  作成: {name}")
        else:
            print(f"  既存: {name}")

    print("==> ユーザー・リポジトリ ID 取得...")
    ids = graphql(
        "query($owner: String!, $repo: String!) { viewer { id login } repository(owner: $owner, name: $repo) { id name } }",
        {"owner": OWNER, "repo": REPO},
    )
    user_id = ids["viewer"]["id"]
    repo_id = ids["repository"]["id"]
    print(f"  User: {ids['viewer']['login']}")
    print(f"  Repo: {ids['repository']['name']}")

    print("==> 既存プロジェクト確認...")
    projects = graphql(
        "query($owner: String!, $title: String!) { user(login: $owner) { projectsV2(first: 20, query: $title) { nodes { id title url } } } }",
        {"owner": OWNER, "title": PROJECT_TITLE},
    )
    project = next(
        (p for p in projects["user"]["projectsV2"]["nodes"] if p["title"] == PROJECT_TITLE),
        None,
    )

    if not project:
        print("==> プロジェクト作成...")
        created = graphql(
            "mutation($ownerId: ID!, $title: String!) { createProjectV2(input: { ownerId: $ownerId, title: $title }) { projectV2 { id title url } } }",
            {"ownerId": user_id, "title": PROJECT_TITLE},
        )
        project = created["createProjectV2"]["projectV2"]
        print(f"  作成: {project['title']} - {project['url']}")
    else:
        print(f"  既存: {project['title']} - {project['url']}")

    project_id = project["id"]

    print("==> リポジトリをプロジェクトにリンク...")
    try:
        graphql(
            "mutation($projectId: ID!, $repoId: ID!) { linkProjectV2ToRepository(input: { projectId: $projectId, repositoryId: $repoId }) { repository { id name } } }",
            {"projectId": project_id, "repoId": repo_id},
        )
        print("  リンク完了")
    except RuntimeError:
        print("  リンク済みまたはスキップ")

    print("==> 既存フィールド取得...")
    fields_data = graphql(
        """query($projectId: ID!) {
          node(id: $projectId) {
            ... on ProjectV2 {
              fields(first: 50) {
                nodes {
                  ... on ProjectV2Field { id name }
                  ... on ProjectV2SingleSelectField { id name options { id name } }
                }
              }
            }
          }
        }""",
        {"projectId": project_id},
    )
    existing_fields = {
        f["name"]: f
        for f in fields_data["node"]["fields"]["nodes"]
        if f.get("name")
    }

    print("==> Status フィールド更新...")
    status_field = existing_fields.get("Status")
    if status_field:
        graphql(
            """mutation($fieldId: ID!) {
              updateProjectV2Field(input: {
                fieldId: $fieldId
                singleSelectOptions: [
                  { name: "未着手", color: GRAY, description: "まだ作業を開始していない" }
                  { name: "着手中", color: YELLOW, description: "現在作業中" }
                  { name: "完了", color: GREEN, description: "作業完了" }
                  { name: "保留", color: ORANGE, description: "一時停止" }
                ]
              }) {
                projectV2Field { ... on ProjectV2SingleSelectField { id name } }
              }
            }""",
            {"fieldId": status_field["id"]},
        )
        print("  Status 更新完了")

    def create_single_select(name, options):
        if name in existing_fields:
            print(f"  既存: {name}")
            return existing_fields[name]
        options_str = ", ".join(
            f'{{ name: "{opt["name"]}", color: {opt.get("color", "GRAY")}, description: "" }}'
            for opt in options
        )
        result = graphql(f"""mutation {{
          createProjectV2Field(input: {{
            projectId: "{project_id}"
            dataType: SINGLE_SELECT
            name: "{name}"
            singleSelectOptions: [ {options_str} ]
          }}) {{
            projectV2Field {{ ... on ProjectV2SingleSelectField {{ id name options {{ id name }} }} }}
          }}
        }}""")
        field = result["createProjectV2Field"]["projectV2Field"]
        existing_fields[name] = field
        print(f"  作成: {name}")
        return field

    def create_number(name):
        if name in existing_fields:
            print(f"  既存: {name}")
            return
        graphql(f"""mutation {{
          createProjectV2Field(input: {{
            projectId: "{project_id}"
            dataType: NUMBER
            name: "{name}"
          }}) {{
            projectV2Field {{ ... on ProjectV2Field {{ id name }} }}
          }}
        }}""")
        print(f"  作成: {name}")

    def create_text(name):
        if name in existing_fields:
            print(f"  既存: {name}")
            return
        graphql(f"""mutation {{
          createProjectV2Field(input: {{
            projectId: "{project_id}"
            dataType: TEXT
            name: "{name}"
          }}) {{
            projectV2Field {{ ... on ProjectV2Field {{ id name }} }}
          }}
        }}""")
        print(f"  作成: {name}")

    def create_date(name):
        if name in existing_fields:
            print(f"  既存: {name}")
            return
        graphql(f"""mutation {{
          createProjectV2Field(input: {{
            projectId: "{project_id}"
            dataType: DATE
            name: "{name}"
          }}) {{
            projectV2Field {{ ... on ProjectV2Field {{ id name }} }}
          }}
        }}""")
        print(f"  作成: {name}")

    print("==> カスタムフィールド作成...")
    create_single_select("タスク階層", [
        {"name": "大タスク", "color": "PURPLE"},
        {"name": "中タスク", "color": "BLUE"},
        {"name": "小タスク", "color": "GREEN"},
    ])
    create_single_select("インパクト", [
        {"name": "大", "color": "RED"},
        {"name": "中", "color": "YELLOW"},
        {"name": "小", "color": "GRAY"},
    ])
    create_single_select("時間負荷", [
        {"name": "すぐ終わる", "color": "GREEN"},
        {"name": "普通", "color": "YELLOW"},
        {"name": "重い", "color": "RED"},
    ])
    create_single_select("気軽さ", [
        {"name": "楽", "color": "GREEN"},
        {"name": "普通", "color": "YELLOW"},
        {"name": "気重", "color": "RED"},
    ])
    create_single_select("予想時間", [
        {"name": "15分"}, {"name": "30分"}, {"name": "1時間"}, {"name": "3時間"}, {"name": "それ以上"},
    ])
    create_number("実時間（分）")
    create_single_select("予想との差異理由", [
        {"name": "差異なし"},
        {"name": "調査時間が増加"},
        {"name": "手戻り発生"},
        {"name": "レビュー対応発生"},
        {"name": "想定以上に難しかった"},
        {"name": "その他"},
    ])
    create_text("差異理由（補足）")
    create_single_select("届け先", [
        {"name": "上司"}, {"name": "クライアント"}, {"name": "チーム"}, {"name": "自分"}, {"name": "その他"},
    ])
    create_date("完了日")
    create_single_select("振り返り済み", [
        {"name": "未実施", "color": "GRAY"},
        {"name": "実施済み", "color": "GREEN"},
    ])

    print("==> 初期大タスク Issue 確認...")
    issues_json = run([
        "issue", "list", "--repo", f"{OWNER}/{REPO}",
        "--label", "大タスク", "--json", "number,title", "--limit", "20",
    ])
    issues = json.loads(issues_json) if issues_json else []
    issue = next((i for i in issues if "タスク管理システム" in i["title"]), None)

    if not issue:
        print("==> 初期大タスク Issue 作成...")
        body = """## ① 背景・目的

AI研修第6回で「時間を効率的に使うための仕組み化」が課題として挙がった。
現状は①ゴール明確化②優先順位③段取り④80点提出⑤振り返りの成果をまとめるツールがなく、振り返りが属人化している。

## ② 届け先

| 項目 | 内容 |
|------|------|
| 届け先 | 研修担当・上司 |
| 関係 | 研修FBの提出先 |

## ③ 成功状態（相手のゴール）

- 自分が次のタスクでも同じ手順（背景→分解→工数→振り返り）で再現できる
- 上司が「この仕組みで進めてよい」と判断できる

## ④ 成果物

- [x] GitHub Projects 設計
- [x] Issue テンプレート
- [x] 運用ルールドキュメント
- [x] Projects 自動セットアップ

## ⑤ 中タスク一覧

| # | 中タスク名 | Status | 担当 | Sub-Issue |
|---|------------|--------|------|-----------|
| 1 | リポジトリ・テンプレート整備 | 完了 | | |
| 2 | Projects 初期設定 | 着手中 | | |
| 3 | 運用開始・最初のタスク分解 | 未着手 | | |

## ⑥ 振り返り（完了後に記入）

### 何がうまくいったか

-

### 何が無駄だったか

-

### 次回どう改善するか

-
"""
        body_path = os.path.join(os.path.dirname(__file__), "large_task_body.md")
        with open(body_path, "w", encoding="utf-8") as f:
            f.write(body)
        issue_url = run([
            "issue", "create", "--repo", f"{OWNER}/{REPO}",
            "--title", "[大タスク] タスク管理システム構築",
            "--label", "大タスク",
            "--body-file", body_path,
        ])
        issue_number = int(issue_url.rstrip("/").split("/")[-1])
        print(f"  作成: {issue_url}")
    else:
        issue_number = issue["number"]
        print(f"  既存: #{issue_number} {issue['title']}")

    print("==> Issue をプロジェクトに追加...")
    issue_data = graphql(
        "query($owner: String!, $repo: String!, $number: Int!) { repository(owner: $owner, name: $repo) { issue(number: $number) { id title } } }",
        {"owner": OWNER, "repo": REPO, "number": issue_number},
    )
    issue_id = issue_data["repository"]["issue"]["id"]

    add_result = graphql(
        "mutation($projectId: ID!, $contentId: ID!) { addProjectV2ItemById(input: { projectId: $projectId, contentId: $contentId }) { item { id } } }",
        {"projectId": project_id, "contentId": issue_id},
    )
    item_id = add_result["addProjectV2ItemById"]["item"]["id"]
    print(f"  プロジェクトに追加: item {item_id}")

    fields_data = graphql(
        """query($projectId: ID!) {
          node(id: $projectId) {
            ... on ProjectV2 {
              fields(first: 50) {
                nodes {
                  ... on ProjectV2SingleSelectField { id name options { id name } }
                }
              }
            }
          }
        }""",
        {"projectId": project_id},
    )
    field_map = {
        f["name"]: f
        for f in fields_data["node"]["fields"]["nodes"]
        if f.get("name")
    }

    def set_field(field_name, option_name):
        field = field_map.get(field_name)
        if not field:
            return
        option = next((o for o in field.get("options", []) if o["name"] == option_name), None)
        if not option:
            return
        graphql(
            """mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $optionId: String!) {
              updateProjectV2ItemFieldValue(input: {
                projectId: $projectId
                itemId: $itemId
                fieldId: $fieldId
                value: { singleSelectOptionId: $optionId }
              }) { projectV2Item { id } }
            }""",
            {
                "projectId": project_id,
                "itemId": item_id,
                "fieldId": field["id"],
                "optionId": option["id"],
            },
        )
        print(f"  設定: {field_name} = {option_name}")

    set_field("Status", "着手中")
    set_field("タスク階層", "大タスク")
    set_field("インパクト", "大")
    set_field("届け先", "上司")
    set_field("振り返り済み", "未実施")

    print()
    print("=" * 42)
    print("セットアップ完了!")
    print(f"プロジェクト: {project['url']}")
    print(f"Issue: https://github.com/{OWNER}/{REPO}/issues/{issue_number}")
    print("=" * 42)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"エラー: {e}", file=sys.stderr)
        sys.exit(1)
