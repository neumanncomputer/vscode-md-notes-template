# vscode-md-notes-template

VS Code で Markdown ノートを管理するための設定とテンプレート集です。

## フォルダ構成

```text
.
├── .claude/
│   └── settings.json            # Claude Code のフック（ノートのルール検証）
├── .githooks/
│   └── pre-commit               # コミット時のノートのルール検証
├── .vscode/
│   ├── settings.json            # ワークスペース設定
│   └── templates.code-snippets  # ノート用テンプレート（スニペット）
├── scripts/
│   └── check_notes.py           # ノートのルール検証スクリプト（ルールの正）
├── AGENTS.md                    # ノート運用ルール（CLAUDE.md / GEMINI.md から読み込み）
├── CLAUDE.md
├── GEMINI.md
├── daily/                       # デイリーノート
│   └── YYYY-MM-DD_daily.md
├── projects/                    # 期限のあるプロジェクトのノート
│   └── <プロジェクト名>/
│       ├── index.md             # 目次・関係者へのリンク
│       └── <期間>/              # 例: 2026 / 2026-H2 / 2026-Q3
│           ├── YYYY-MM-DD_mtg_<タイトル>.md    # type ごとに接頭辞を付ける
│           ├── YYYY-MM-DD_dec_<タイトル>.md
│           └── YYYY-MM-DD_<タイトル>.md        # note は接頭辞なし
├── areas/                       # 継続的な担当領域のノート
│   └── <担当名>/                # 例: support
│       └── YYYY-MM-DD_howto_<タイトル>.md
├── knowledge/                   # 用語解説・手順・資料要約（日付なし）
│   └── <タイトル>.md
├── people/                      # 人物ページ
│   └── <会社名>_<名前>.md
├── inbox/                       # 置き場所が決まっていないメモ
│   └── YYYY-MM-DD_<タイトル>.md
└── archive/                     # 使い終わったノート（元のフォルダ構造のまま移す）
```

- 各フォルダの `index.md` は目次（`type: index`）です。
- 貼り付けた画像は、ノートと同じ階層の `attachments/` に自動で保存されます。

### フォルダごとの type

フォルダは「どの文脈・どの期間のものか」、`type` は「どんな形の文書か」を表します。プロジェクト名やテーマは `tags` に入れます。

| フォルダ     | 置ける type                                            |
| ------------ | ------------------------------------------------------ |
| `daily/`     | `daily`                                                |
| `projects/`  | `meeting` `note` `decision` `research` `spec` `report` |
| `areas/`     | `meeting` `note` `decision` `howto` `report`           |
| `knowledge/` | `concept` `howto` `reference`                          |
| `people/`    | `person`                                               |
| `inbox/`     | `note`                                                 |
| `archive/`   | `index` 以外のすべて                                   |

各 type の内容は [AGENTS.md](AGENTS.md) を参照してください。

## テンプレート

Markdown ファイルでプレフィックスを入力して `Tab` を押すと展開されます。

| プレフィックス | 用途           | 見出し                                                                               |
| -------------- | -------------- | ------------------------------------------------------------------------------------ |
| `daily`        | デイリーノート | 今日のタスク / メモ                                                                  |
| `mtg`          | 議事録         | 事前タスク / 共有事項 / 確認事項 / 参加者 / 議事内容 / 決定事項 / ネクストアクション |
| `note`         | クイックノート | タイトルのみ                                                                         |

どのテンプレートも、先頭に [Open Knowledge Format (OKF)](https://github.com/GoogleCloudPlatform/knowledge-catalog) のフロントマター（`type` / `title` / `description` / `tags` / `timestamp`）が入り、その下に `# YYYY-MM-DD_` 形式の日付付きタイトルが続きます。

## 設定内容

`.vscode/settings.json` では次の設定をしています。

- `editor.tabCompletion: "on"`: プレフィックス + `Tab` でテンプレートを展開する
- `explorer.sortOrder: "modified"`: エクスプローラーを更新日時順に並べ、最近触ったノートを上に出す
- `markdown.copyFiles.destination`: Markdown に貼り付けた画像を、そのファイルと同じ階層の `attachments/` に保存する
- `markdown.updateLinksOnFileMove.enabled: "always"`: ノートを移動・リネームしたとき、ほかのノートからのリンクを自動で書き換える

## ファイル命名規則

- `YYYY-MM-DD_<タイトル>.md` の形式にする（`knowledge/` と `people/` は日付なし）
- `projects/` と `areas/` では日付の後ろに type ごとの接頭辞を付ける（`mtg_` / `dec_` / `rsc_` / `spec_` / `howto_` / `rpt_`、`note` は接頭辞なし。一覧は [AGENTS.md](AGENTS.md)）
- `people/` は社内・社外とも `<会社名>_<名前>.md` にする。tags には自社の人なら `internal`、それ以外なら `external` を入れる（自社名は `scripts/check_notes.py` の `INTERNAL_ORGS`）
- ファイル名とフロントマターの `title`、本文の見出しをそろえる

## ノート運用ルールとエージェント

フォルダごとに置ける `type`、ファイル名、フロントマターのルールは [AGENTS.md](AGENTS.md) にまとめています（`CLAUDE.md` と `GEMINI.md` から読み込み）。ルールは次の 3 か所で自動検証されます。

- **Claude Code**: ファイル書き込みのたびと応答の終了時に [.claude/settings.json](.claude/settings.json) のフックが検証し、違反をエージェントに差し戻す
- **git commit**: [.githooks/pre-commit](.githooks/pre-commit) がステージしたノートを検証する（clone 後に `git config core.hooksPath .githooks` が必要）
- **手動**: `python3 scripts/check_notes.py`（全体）/ `--changed`（変更分のみ）
