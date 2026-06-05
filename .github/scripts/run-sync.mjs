#!/usr/bin/env node
/**
 * ローカル実行用: Issue の評価軸を Projects へ同期
 * 使い方: node .github/scripts/run-sync.mjs <issue番号>
 * 要: gh auth login（project スコープ）
 */

import { execSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { findSyncConfig, syncIssueToProject } from "./sync-project-fields.mjs";

function findGh() {
  const candidates = [
    "gh",
    "C:\\Program Files\\GitHub CLI\\gh.exe",
    path.join(os.homedir(), "AppData", "Local", "Programs", "GitHub CLI", "gh.exe"),
  ];
  for (const candidate of candidates) {
    try {
      execSync(`"${candidate}" --version`, { stdio: "ignore" });
      return candidate;
    } catch {
      /* try next */
    }
  }
  throw new Error("GitHub CLI (gh) が見つかりません。");
}

const GH = findGh();
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const allConfig = JSON.parse(
  fs.readFileSync(path.join(__dirname, "../project-sync-config.json"), "utf8")
);

const issueNumber = Number(process.argv[2]);
if (!issueNumber) {
  console.error("Usage: node .github/scripts/run-sync.mjs <issue番号>");
  process.exit(1);
}

const owner = "anbx-Hayate";
const repo = "Task_management";

function ghGraphql(query, variables = {}) {
  const args = ["api", "graphql", "-f", `query=${query}`];
  for (const [key, value] of Object.entries(variables)) {
    const flag = typeof value === "number" ? "-F" : "-f";
    args.push(flag, `${key}=${value}`);
  }
  const out = execSync(`"${GH}" ${args.map((a) => `"${a}"`).join(" ")}`, {
    encoding: "utf8",
    shell: true,
  });
  const data = JSON.parse(out);
  if (data.errors) {
    throw new Error(JSON.stringify(data.errors, null, 2));
  }
  return data.data;
}

const issueJson = execSync(
  `"${GH}" issue view ${issueNumber} --repo ${owner}/${repo} --json body,labels`,
  { encoding: "utf8", shell: true }
);
const issue = JSON.parse(issueJson);

const config = findSyncConfig(allConfig, issue.labels);
if (!config) {
  console.error(`Issue #${issueNumber} に大タスク / 小タスク ラベルがありません`);
  process.exit(1);
}

const updates = await syncIssueToProject({
  graphql: ghGraphql,
  config: { projectId: allConfig.projectId, ...config },
  owner,
  repo,
  issueNumber,
  issueBody: issue.body ?? "",
});

console.log(
  updates.length
    ? `同期完了 (#${issueNumber}): ${updates.join(", ")}`
    : `更新なし (#${issueNumber})`
);
