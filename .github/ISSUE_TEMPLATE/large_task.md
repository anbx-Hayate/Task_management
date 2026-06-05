---
name: 大タスク
description: 背景・目的から振り返りまで一貫管理する大タスク用テンプレート
title: "[大タスク] "
labels: ["大タスク"]
assignees: []
body:
  - type: markdown
    attributes:
      value: |
        ## 使い方
        1. ①②③④ を記入してから Issue を作成する
        2. Projects の `タスク階層` を「大タスク」、`Status` を「未着手」に設定する
        3. 中タスクを Sub-Issue として分解し、⑤ の表にリンクを追記する
        4. 全小タスク完了後、⑥ 振り返りを記入する

  - type: textarea
    id: background
    attributes:
      label: ① 背景・目的
      description: なぜこのタスクを行うのか。会社・チーム・自分にとっての意味を書く
      placeholder: |
        例：
        - AI研修の第6回で「時間管理の仕組み化」が課題として挙がった
        - 現状は成果をまとめるツールがなく、振り返りが属人化している
    validations:
      required: true

  - type: input
    id: recipient
    attributes:
      label: ② 届け先
      description: 誰に成果物を届けるのか。名前・役割を具体的に
      placeholder: "例：研修担当の上司 / チームメンバー"
    validations:
      required: true

  - type: input
    id: recipient_relation
    attributes:
      label: ② 届け先との関係
      description: レビュー依頼先・報告先など
      placeholder: "例：研修FBの提出先"
    validations:
      required: false

  - type: textarea
    id: success_state
    attributes:
      label: ③ 成功状態（相手のゴール）
      description: 相手がどのような状態になれば成功か。「資料を作る」ではなく「上司が意思決定できる」レベルまで
      placeholder: |
        例：
        - 上司が「この仕組みで進めてよい」と判断できる
        - 自分が次のタスクでも同じ手順で再現できる
    validations:
      required: true

  - type: textarea
    id: deliverables
    attributes:
      label: ④ 成果物
      description: 最終的に何を納品するか（チェックリスト形式）
      placeholder: |
        - [ ] GitHub Projects 設計書
        - [ ] Issue テンプレート
        - [ ] 運用ルールドキュメント
    validations:
      required: true

  - type: textarea
    id: medium_tasks
    attributes:
      label: ⑤ 中タスク一覧
      description: 大タスクを分解した中タスク。Sub-Issue 作成後に Issue 番号を追記する
      value: |
        | # | 中タスク名 | Status | 担当 | Sub-Issue |
        |---|------------|--------|------|-----------|
        | 1 | | 未着手 | | # |
        | 2 | | 未着手 | | # |
        | 3 | | 未着手 | | # |
    validations:
      required: false

  - type: markdown
    attributes:
      value: |
        ---

        ## ⑥ 振り返り（大タスク完了後に記入）

        > 全小タスク完了後、この Issue を編集して以下を記入してください。

  - type: textarea
    id: retrospective_good
    attributes:
      label: 何がうまくいったか
      placeholder: "- "
    validations:
      required: false

  - type: textarea
    id: retrospective_waste
    attributes:
      label: 何が無駄だったか
      placeholder: "- "
    validations:
      required: false

  - type: textarea
    id: retrospective_improve
    attributes:
      label: 次回どう改善するか
      placeholder: "- "
    validations:
      required: false

  - type: textarea
    id: time_summary
    attributes:
      label: 工数サマリー（任意）
      value: |
        | 項目 | 値 |
        |------|-----|
        | 小タスク合計予想時間 | |
        | 小タスク合計実時間（分） | |
        | 主な差異理由 | |
    validations:
      required: false

  - type: checkboxes
    id: checklist
    attributes:
      label: 作成時チェックリスト
      options:
        - label: Projects の `タスク階層` を「大タスク」に設定した
          required: true
        - label: Projects の `Status` を「未着手」に設定した
          required: true
        - label: 中タスクを Sub-Issue として分解した
          required: false
        - label: 各中タスクに小タスクを Sub-Issue として分解した
          required: false
