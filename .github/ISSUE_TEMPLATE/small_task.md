---
name: 小タスク
description: 実作業単位（工数管理の最小単位）
title: "[小タスク] "
labels: ["小タスク"]
assignees: []
body:
  - type: markdown
    attributes:
      value: |
        ## 使い方
        1. 親の中タスク Issue から **Sub-Issue として作成**する
        2. Projects で `タスク階層=小タスク`、`予想時間`、`インパクト`、`時間負荷`、`気軽さ` を設定する
        3. 作業開始時に `Status` を「着手中」、完了時に `実時間（分）` と `差異理由` を記入する

  - type: textarea
    id: work_content
    attributes:
      label: 作業内容
      description: 何をすれば完了か。80点で一度見せる前提で書く
      placeholder: |
        例：
        - 研修テキストから学習ポイントを5つ抽出する
        - 構成案をA4 1枚で作成する
    validations:
      required: true

  - type: checkboxes
    id: completion_criteria
    attributes:
      label: 完了条件
      description: すべてチェックできたら作業完了
      options:
        - label: 作業内容が完了した
          required: false
        - label: 80点の成果物を関係者に共有した（必要な場合）
          required: false
        - label: Projects の `実時間（分）` を記入した
          required: false
        - label: 予想と差があれば `予想との差異理由` を記入した
          required: false

  - type: checkboxes
    id: checklist
    attributes:
      label: 作成時チェックリスト
      options:
        - label: 親の中タスクから Sub-Issue として作成した
          required: true
        - label: Projects の `タスク階層` を「小タスク」に設定した
          required: true
        - label: `予想時間`・`インパクト`・`時間負荷`・`気軽さ` を設定した
          required: true
