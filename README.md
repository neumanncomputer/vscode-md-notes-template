# vscode-md-notes-template

VS Code で Markdown ノートを管理するための設定とテンプレート集です。

## フォルダ構成

```text
.
├── .vscode/
│   ├── settings.json            # ワークスペース設定
│   └── templates.code-snippets  # ノート用テンプレート（スニペット）
├── daily/                       # デイリーノート
│   ├── YYYY-MM-DD_daily.md
│   └── attachments/             # 貼り付けた画像の保存先（自動作成）
└── projects/                    # プロジェクトごとのノート
    └── <プロジェクト名>/
        └── <期間>/              # 例: 2026-H1
            ├── YYYY-MM-DD_mtg_<ミーティングタイトル>.md
            ├── YYYY-MM-DD_<クイックノートタイトル>.md
            └── attachments/     # 貼り付けた画像の保存先（自動作成）
```

## テンプレート

Markdown ファイルでプレフィックスを入力して `Tab` を押すと展開されます。

| プレフィックス | 用途           | 見出し                                                                               |
| -------------- | -------------- | ------------------------------------------------------------------------------------ |
| `daily`        | デイリーノート | 今日のタスク / メモ                                                                  |
| `mtg`          | 議事録         | 事前タスク / 共有事項 / 確認事項 / 参加者 / 議事内容 / 決定事項 / ネクストアクション |
| `note`         | クイックノート | タイトルのみ                                                                         |

どのテンプレートも、1 行目に `# YYYY-MM-DD_` 形式の日付付きタイトルが入ります。

## 設定内容

`.vscode/settings.json` では次の設定をしています。

- `editor.tabCompletion: "on"`: プレフィックス + `Tab` でテンプレートを展開する
- `explorer.sortOrder: "modified"`: エクスプローラーを更新日時順に並べ、最近触ったノートを上に出す
- `markdown.copyFiles.destination`: Markdown に貼り付けた画像を、そのファイルと同じ階層の `attachments/` に保存する

## ファイル命名規則

- `YYYY-MM-DD_<タイトル>.md` の形式にする
- ファイル名と 1 行目の見出しをそろえる
