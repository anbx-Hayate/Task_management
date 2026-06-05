# Projects ビュー設定

## 現在のビュー一覧

| ビュー | レイアウト | 用途 | URL |
|--------|-----------|------|-----|
| **View 1（新）** | ボード | 全体の進捗管理（Status 列） | [views/7](https://github.com/users/anbx-Hayate/projects/3/views/7) |
| **全体ボード** | ボード | 同上（メイン推奨） | [views/3](https://github.com/users/anbx-Hayate/projects/3/views/3) |
| **大タスク一覧** | テーブル | 大タスクの俯瞰 | [views/4](https://github.com/users/anbx-Hayate/projects/3/views/4) |
| **今週の作業** | ボード | 小タスクの作業管理 | [views/5](https://github.com/users/anbx-Hayate/projects/3/views/5) |
| **工数・振り返り** | テーブル | 予実・差異理由の確認 | [views/6](https://github.com/users/anbx-Hayate/projects/3/views/6) |

## Status 列（未着手 / 着手中 / 完了 / 保留）

ボードビューで Status 列を表示する手順（初回のみ）：

1. [タスク管理ボード](https://github.com/users/anbx-Hayate/projects/3) を開く
2. **View 1（views/7）** または **全体ボード** を選択
3. ビュー右上の **「Group by」**（グループ化）→ **Status** を選択

これで以下の4列が表示されます。

- 未着手
- 着手中
- 完了
- 保留

## 古い View 1 について

プロジェクト作成時のデフォルト View 1（テーブル形式・列なし）は API で更新できないため、そのまま残っています。

**推奨対応：**

1. 新しい **View 1（views/7）** または **全体ボード** を使う
2. 古い View 1（views/1）はビュー名横の `...` から削除して整理する

## ビュー再作成

```bash
cd scripts
bash setup_views.sh
```
