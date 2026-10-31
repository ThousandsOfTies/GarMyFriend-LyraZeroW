# 共通ソースの再利用確認

このProductは公開済みの共有ソースをサブモジュールで固定します。
汎用入力の修正はgar-toolsへ戻し、Product内に専用の読取処理を複製しません。

| ソース | 固定コミット |
| --- | --- |
| gar-my-friend | `09c365f2896ccfd7b28887da59f2b6a9d7b15fec` |
| gar-tools | `d9816199c0732be1857211a3e195ecfed19d6621` |

## 共用する実装

| 用途 | gar-tools内の場所 |
| --- | --- |
| 液晶とRGB565変換 | `web-simulator/components/display.mjs`、`framebuffer.mjs` |
| 回転・押下の見た目と操作 | `web-simulator/components/rotary.mjs` |
| GPIO v2と回転判定 | `targets/linux-device/runtime/rotary-input/` |
| GC9A01初期化 | `targets/linux-device/runtime/gc9a01-output/` |
| 仮想SPI液晶 | `targets/linux-device/runtime/gc9a01-stub/`と共有DCSモデル |
| GPIO・画素の中継 | `targets/linux-device/runtime/web-bridge/` |

Productに残すのはCSVの割当、部品の配置、Bridgeへの接続、実機と専用VMの運用です。
顔の選択・描画処理をProductやBridgeへコピーしません。

## 確認方法

- `npm test`: 共通アプリ、Product CSV、画素だけを描くPanelと入力の接続。
- `npm run test:shared`: 共有ライブラリー自身のページを使う独立した部品試験。
  液晶は解像度の違う2インスタンス、ノブは2インスタンスを配置し、独立性と公開APIを確認します。
- `npm run test:parts`: 実際のLinux GPIO/SPI、アプリ停止中の画素不変、Panel停止中のアプリ継続。
- `npm run test:vm`: ノブの回転・押下、SPIドライバの画素と表示canvasの一致。

`artifacts/shared-parts.json`と`artifacts/reuse-report.json`に試験結果と固定ソースの状態を残します。

## 2026-10-30の確認結果

共通アプリとgar-toolsの作業ツリーは両方とも変更なしです。
共有液晶9項目・共有入力6項目のブラウザー単体試験、GPIOデコーダーとGC9A01初期化の
ネイティブ試験、ProductのCSV・接続試験を通過しました。
専用Linux VMでは回転・押下、アプリとPanelの独立動作、仮想SPIの画素とcanvasの一致を
確認しました。`artifacts/vm-webpanel.png`は接続中の実行画面です。

## 2026-10-31の実機導入

同じ固定ソースのまま、Luckfox SDKのGCC 10.3でARMv7 hard-float版をビルドしました。
GPIO v2の定義にはSDKのLinux 6.1 UAPIヘッダーを使いました。初回導入時は両方の共有ソースを変更せずに実行しました。
公式配布のNode.js v22.23.4 ARMv7版をSHA256確認後に導入し、Buildroot 2024.02で実行しています。
gpio0のoffset 3〜7とSPI0 CS0を実機で照合し、共有GPIO読取のreadyと液晶への最初のフレーム書込を確認しました。
利用者が液晶の配線を修正した後、1MHzと8MHzで顔の表示を確認しました。
ノブも利用者による再接続後、アプリに正負両方の回転と押下が記録されました。
利用者も表情の切替と押下時のまばたきを確認しました。この時点では操作が届くことだけを確認しました。
再起動後の自動起動と、8MHzでのSPIエラー・タイムアウトが0であることも確認しました。
実機の記録は`artifacts/device-report.json`にあります。

## 2026-10-31の回転応答の初期回避策

その後、20クリック中2回しか採用されない問題を再現しました。
gar-toolsのGPIO読取がrequest全体の`seqno`の飛びを欠落扱いしていましたが、
本機の記録では各端子の`line_seqno`は連続しており、20クリックすべてを復元できました。
欠落判定を端子ごとの番号へ修正し、記録の再生テストと本当の欠落・初回読取・番号周回のテストを追加しました。
修正はgar-toolsの固定コミットに含まれ、共有アプリgar-my-friendの変更はありません。
実機でも右10回・左10回と押下1回を記録し、利用者が毎クリックの表情切替を確認しました。
詳細は[ロータリー入力の確認記録](ROTARY_INPUT.md)を参照してください。

## 現在の恒久設定

入力層の比較検査で、Linux GPIO v2に1000µsのデバウンスを要求すると
通知が必要な82件に整理され、番号の不連続が0となりました。
この結果から初期回避策を置き換え、gar-toolsの番号判定を元の`seqno`方式へ戻しました。
共有読取へ任意の`--debounce-us`を追加し、共通アプリにはProduct CSVの任意列を
渡す処理だけを追加しました。表情・描画・回転デコーダーは変更していません。
Lyraの物理プロファイルだけが`debounce_us=1000`を指定し、設定のないProductは従来動作を保ちます。
通常アプリで右10回・左10回・押下1回、再起動後の同じ設定での自動起動を確認しました。

## 2026-11-01の基板コンポジション

基板情報を`gar-board-lyra-zero-w`へ分離し、Productの3つ目のsubmoduleとして固定しました。
`product.json`が共通アプリ・gar-tools・基板プロファイルと配線CSVを組み合わせます。
導入・起動ファイルの生成はgar-toolsの`composition/`へ移し、Productの入口は委譲だけにしました。
新しい構成での実機再導入は未実施です。[構成の説明](COMPOSITION.md)を参照してください。
