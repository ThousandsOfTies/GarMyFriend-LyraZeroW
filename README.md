# GarMyFriend-LyraZeroW

<!-- board-composition -->
このProductは **アプリ + gar-tools + 基板定義** の3つをsubmoduleで組み合わせます。
組み立て指定は[product.json](product.json)、所有範囲と生成物は[構成の説明](docs/COMPOSITION.md)で確認できます。
`npm run compose`で現在選んでいる部品と版を表示します。


Luckfox Lyra Zero Wの実機と専用Linux VMで、同じ顔アプリを使うProductです。
GC9A01の円形液晶とKY-040ノブの2部品を表示します。
ノブを回すと8つの表情が切り替わり、押すとまばたきします。

## 実機で動かす

USB OTGで接続したZero Wに、ARMv7用バイナリーと固定バージョンのNode.jsを導入します。
`config/device.example.json`を`.gar/device.json`へコピーして、接続先とSDKの保存場所を設定します。
Node.jsの版・配布元・チェック値は`product.json`、SDKのレイアウトは基板submoduleに固定しています。
以下の導入操作は実機の配置を更新します。今回の構成変更では実行していません。

```powershell
npm run device          # ARMv7ビルド・USB転送・SPI設定・起動
npm run device:status
npm run device:logs
npm run device:stop
```

実機の配線設定は`hardware/lyra-zero-w/`から読みます。
[ビルド・導入・停止の詳細](infra/lyra-zero-w/README.md)

## 開く

このProductのルートで実行します。

```powershell
npm ci
npm run sim
# http://127.0.0.1:8774
```

`sim`は専用VMを起動し、固定した共有ソースを配布・ビルドして、ローカル接続を用意します。
表示URLは`http://127.0.0.1:8774`です。VMを準備済みの場合は`npm run vm:start`でも再開できます。

```powershell
npm run sim:open     # ブラウザーで開く
npm run sim:status   # VMと3つのサービスを確認
npm run sim:deploy   # 編集内容を転送して再ビルド
npm run sim:stop     # このProductの専用VMを停止
```

専用VMは`gar-myfriend-lyra-zero-w-sim`、SSHは2232番です。
構築・再作成は[シミュレータの手順](SIMULATOR.md)を参照してください。

## 入出力の経路

```text
WebPanelのKY-040 → 共有Bridge → Linux gpio-sim
                                      ↓
                         共通の顔アプリ（独立プロセス）
                                      ↓
WebPanelのGC9A01 ← 共有Bridge ← GC9A01 CUSE / SPI
```

顔の描画と表情は`gar-my-friend`が担当します。WebPanelはノブの入力と、
実行アプリがSPIへ書いた画素を受け渡します。WebPanelを止めても顔アプリは動きます。

`gar-my-friend`は`09c365f2896ccfd7b28887da59f2b6a9d7b15fec`、
`gar-tools`と基板定義の固定コミットは`npm run compose`で確認できます。
液晶・ノブのWeb Components、GPIO読取、GC9A01初期化、仮想ドライバとBridgeを共用します。
[共有部分の確認方法](docs/REUSE.md)

## 配線と再現範囲

[配線計画](hardware/WIRING.md)と`hardware/connections.csv`が実機用の正本です。
VMのGPIOはDC=3、RST=4、ノブ=5・6・7とし、実機と同じGPIO/SPI割当を使います。

実機はSDからBuildrootを起動し、ARMv7版アプリを自動起動します。
利用者による配線修正後、SPI 8MHzで顔が表示されることを確認しました。
ノブも再接続後に両方向の回転と押下をログで確認し、利用者が表情の切替とまばたきを確認しました。
Lyra用GPIO CSVで1ミリ秒のデバウンスを要求し、共有GPIO読取の番号判定は元の`seqno`方式を使います。
この構成で右10回・左10回・押下1回すべての反応を確認しました。
[反応の改善と検証記録](docs/ROTARY_INPUT.md)
VMはx86_64 Linuxであり、RK3506のCPU、Buildroot、電圧、
SPIの電気的タイミング、実機性能を再現するものではありません。
物理ボードは`/dev/gpiochip0`のgpio0と`/dev/spidev0.0`を使用します。
Orange Pi用の基板資産は別の基板リポジトリに分離し、このProductから取り除きました。

基底Product：[GarMyFriend-OrangePiZero2W](https://github.com/ThousandsOfTies/GarMyFriend-OrangePiZero2W)。
共通アプリ：[gar-my-friend](https://github.com/ThousandsOfTies/gar-my-friend)。
