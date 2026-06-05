import assert from "node:assert/strict";
import { parseIssueField } from "./sync-project-fields.mjs";

const sampleBody = `## 小タスク作成ガイド

### 作業内容（必須）

テスト作業

### インパクト

大

### 時間負荷

重い

### 気軽さ

普通

### 予想時間

1時間
`;

assert.equal(parseIssueField(sampleBody, "時間負荷"), "重い");
assert.equal(parseIssueField(sampleBody, "気軽さ"), "普通");
assert.equal(parseIssueField(sampleBody, "予想時間"), "1時間");
assert.equal(parseIssueField(sampleBody, "インパクト"), "大");

const largeTaskBody = `### ② 届け先の種類

上司

### ③ 成功状態（必須）

テスト
`;

assert.equal(parseIssueField(largeTaskBody, "② 届け先の種類"), "上司");

const deadlineBody = `### ⑤ 期限

2026-06-30
`;

assert.equal(parseIssueField(deadlineBody, "⑤ 期限"), "2026-06-30");

console.log("All parser tests passed.");
