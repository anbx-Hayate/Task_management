---
name: 中タスク
description: 大タスクの中間分解単位（成果物単位）
title: "[中タスク] "
labels: ["中タスク"]
assignees: []
body:
  - type: markdown
    attributes:
      value: |
        ## 使い方
        1. 親の大タスク Issue から **Sub-Issue として作成**する
        2. Projects の `タスク階層` を「中タスク」、`Status` を「未着手」に設定する
        3. 小タスクを Sub-Issue として分解する

  - type: textarea
    id: deliverable
    attributes:
      label: この中タスクで作るもの
      description: 1文で成果物を定義する
      placeholder: "例：プレゼン資料の構成案"
    validations:
      required: true

  - type: textarea
    id: small_tasks
    attributes:
      label: 小タスク一覧
      description: Sub-Issue 作成後に Issue 番号を追記する
      value: |
        | # | 小タスク名 | Status | 予想時間 | Sub-Issue |
        |---|------------|--------|----------|-----------|
        | 1 | | 未着手 | | # |
        | 2 | | 未着手 | | # |
        | 3 | | 未着手 | | # |
    validations:
      required: false

  - type: checkboxes
    id: checklist
    attributes:
      label: 作成時チェックリスト
      options:
        - label: 親の大タスクから Sub-Issue として作成した
          required: true
        - label: Projects の `タスク階層` を「中タスク」に設定した
          required: true
        - label: 小タスクを Sub-Issue として分解した
          required: false
