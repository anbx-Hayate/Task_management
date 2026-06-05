# テンプレート → タスク管理ボード 自動同期の設定

大タスク・小タスク Issue 作成時に、テンプレートの入力値を
GitHub Projects「タスク管理ボード」へ自動反映します。

## 同期される項目

### 大タスク

| Issue テンプレート | Projects フィールド |
|-------------------|-------------------|
| ② 届け先の種類 | 届け先 |
| ⑤ 期限 | 期限（日付） |
| （自動） | タスク階層 → 大タスク |
| （自動） | Status → 未着手 |
| （自動） | 振り返り済み → 未実施 |

### 小タスク

| Issue テンプレート | Projects フィールド |
|-------------------|-------------------|
| インパクト | インパクト |
| 時間負荷 | 時間負荷 |
| 気軽さ | 気軽さ |
| 予想時間 | 予想時間 |
| （自動） | タスク階層 → 小タスク |
| （自動） | Status → 未着手 |

## 1. GitHub Actions で自動同期（推奨）

ユーザー所有の Projects へ書き込むには **PAT（Personal Access Token）** が必要です。

### 手順

1. GitHub → **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
2. **Generate new token (classic)** をクリック
3. スコープに **`project`** と **`repo`** にチェック
4. トークンをコピー
5. リポジトリ [Task_management](https://github.com/anbx-Hayate/Task_management) → **Settings** → **Secrets and variables** → **Actions**
6. **New repository secret** をクリック
   - Name: `PROJECTS_TOKEN`
   - Secret: コピーしたトークン
7. 保存

これで小タスク Issue 作成・編集時にワークフロー `Sync Issue fields to Projects` が動きます。

## 2. ローカルで手動同期（PAT 設定前の代替）

```bash
# Issue #5 を同期する例
node .github/scripts/run-sync.mjs 5
```

要: `gh auth login`（`project` スコープ付き）

## 動作確認

1. [小タスクテンプレート](https://github.com/anbx-Hayate/Task_management/issues/new?template=small_task.yml) で Issue 作成
2. Actions タブでワークフロー成功を確認
3. [タスク管理ボード](https://github.com/users/anbx-Hayate/projects/3) でフィールドが反映されているか確認
