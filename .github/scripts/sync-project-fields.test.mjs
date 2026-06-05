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

console.log("All parser tests passed.");
