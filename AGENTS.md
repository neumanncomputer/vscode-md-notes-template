# ノート運用ルール（エージェント向け）

このリポジトリで Markdown ノートを作成・編集・移動するエージェントは、以下のルールに必ず従うこと。
ルールの正は [scripts/check_notes.py](scripts/check_notes.py) にある。作業後は必ず次を実行し、エラーが 0 件になるまで修正すること。

```sh
python3 scripts/check_notes.py --changed
```

Claude Code ではファイル書き込みのたびに自動で検証され、違反があるとエラーが返る。git の pre-commit でも同じ検証が走る。

## 基本方針

- **フォルダ**は「どの文脈・どの期間のものか」を表す。**type** は「どんな形の文書か」を表す。
- プロジェクト名やテーマは `type` ではなく `tags` に入れる。
- 当てはまる type が無いときは `note` にする。新しい type やフォルダを勝手に追加しない（追加はユーザーに確認する）。

## フォルダ

| フォルダ | 置き場所 | 置ける type | ファイル名 |
| --- | --- | --- | --- |
| `daily/` | 直下 | `daily` | `YYYY-MM-DD_daily.md` |
| `projects/` | `projects/<プロジェクト名>/<期間>/`（期間: `2026` / `2026-H1` / `2026-Q3`） | `meeting` `note` `decision` `research` `spec` `report` | `YYYY-MM-DD_<接頭辞>_<タイトル>.md`（下記「ファイル名の接頭辞」） |
| `areas/` | `areas/<担当名>/` | `meeting` `note` `decision` `howto` `report` | `YYYY-MM-DD_<接頭辞>_<タイトル>.md`（下記「ファイル名の接頭辞」） |
| `knowledge/` | 直下 | `concept` `howto` `reference` | **日付なし**（例: `okr.md`） |
| `people/` | 直下 | `person` | `<会社名>_<名前>.md`（下記「人物ページ」） |
| `inbox/` | 直下 | `note` | `YYYY-MM-DD_<タイトル>.md` |
| `archive/` | 元のフォルダ構造のまま移す | `index` 以外のすべて | 元のまま |

- 各フォルダの `index.md` は `type: index` にする（`index` は `index.md` 専用）。
- ルート直下に置けるのは `README.md` / `AGENTS.md` / `CLAUDE.md` / `GEMINI.md` だけ。上記以外のフォルダは作らない。
- 画像などは各フォルダの `attachments/` に置く。

### ファイル名の接頭辞

`projects/` と `areas/` では type が混ざるため、日付の後ろに type ごとの接頭辞を付ける。`note` だけは接頭辞なし。

| type | 接頭辞 | 例 |
| --- | --- | --- |
| `meeting` | `mtg_` | `2026-10-13_mtg_定例.md` |
| `decision` | `dec_` | `2026-10-13_dec_ツール選定.md` |
| `research` | `rsc_` | `2026-10-13_rsc_競合比較.md` |
| `spec` | `spec_` | `2026-10-13_spec_問い合わせフォーム.md` |
| `howto` | `howto_` | `2026-10-13_howto_リリース手順.md` |
| `report` | `rpt_` | `2026-10-13_rpt_10月振り返り.md` |
| `note` | なし | `2026-10-13_アイデアメモ.md` |

type を変えたらファイル名の接頭辞と `title` も合わせて変える。

### 人物ページ

社内の人と社外の人（クライアントなど）を区別するため、`people/` は次のルールにする。プロジェクトのフォルダには置かず、関係者はプロジェクトの `index.md` からリンクする。

- ファイル名は社内・社外とも `<会社名>_<名前>.md`（例: `XYZ_山田.md`、`ABC商事_田中.md`）。
- 自社の人は tags に `internal`、それ以外の人は `external` を入れる。自社名は [scripts/check_notes.py](scripts/check_notes.py) の `INTERNAL_ORGS` で定義する。
- 同じ会社は毎回同じ表記にする（`ABC商事` と `ABC` を混ぜない）。

- 関わっているプロジェクトのタグ（例: `project-alpha`）も tags に入れる。
- 本文の「基本情報」に所属・役職・関わっているプロジェクトを書く。

## type

| type | 内容 |
| --- | --- |
| `daily` | デイリーログ |
| `meeting` | 議事録 |
| `note` | 形式の決まっていないメモ |
| `decision` | 決定記録（背景 / 選択肢 / 決定 / 理由） |
| `concept` | 用語・概念の解説 |
| `howto` | 手順書・ランブック |
| `research` | 調査・比較・検証の記録 |
| `spec` | 設計・仕様・企画書 |
| `report` | 週次・月次の振り返りや報告 |
| `person` | 人物ページ |
| `reference` | 本・記事・外部資料の要約 |
| `index` | フォルダの目次（`index.md`） |

## フロントマター（Open Knowledge Format）

すべてのノートの先頭に次のフロントマターを付ける。5 つのキーはすべて必須（`description` は空文字でもよい）。

```yaml
---
type: meeting
title: "2026-10-13_mtg_定例"
description: "週次定例。リリース日程を決定"
tags: [meeting, project-x]
timestamp: 2026-10-13T14:05:00+09:00
---
```

- `title` は本文の `#` 見出しと同じにする。
- `timestamp` は作成日時を ISO 8601（タイムゾーン付き）で書く。
- `daily` / `meeting` / `note` は [.vscode/templates.code-snippets](.vscode/templates.code-snippets) の見出し構成に従う。
