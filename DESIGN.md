# Lyra Zero W版の役割分担

WebPanelの範囲はGC9A01円形液晶とKY-040ノブの2点です。
共有部品の外観と基本操作を残し、表情選択用の別UIやダッシュボードは追加しません。

| 所有者 | 役割 |
| --- | --- |
| gar-my-friend | 表情データ、選択、補間、まばたき、描画、GPIO/SPIアプリI/O |
| gar-tools | 汎用GPIO回転読取、GC9A01初期化、CUSE SPIドライバ、Bridge、表示・ノブWeb Components |
| gar-board-lyra-zero-w | 基板の資源、OS・ABI、SDKレイアウト、起動順、基板準備の指定 |
| Product hardware | 型番、Zero Wの配線案、仮想・物理のCSV割当 |
| Product simulation | 共有Bridgeからの画素受信とGPIO入力の中継、Panelへの部品配置 |
| Product tools / infra | 専用VM・ローカル接続、共通のビルド・配布・起動管理へ渡すProduct指定 |

顔アプリはHTTPやWebPanelをimportしません。Bridgeは表情名を知りません。
WebPanelの操作は共有Bridgeに渡す回転・押下だけです。画面はアプリがSPIへ
書き込んだRGB565を表示し、独自の顔アニメーションを生成しません。

シミュレータは専用VMの`/dev/gpiochip0`と`/dev/spidev0.0`を使います。
GPIO/SPI割当の正本は`hardware/gpio.csv`・`spi.csv`で、実機がそのまま読みます。
シミュレータ用は`simulation-overrides.csv`の差分から`.gar/hardware/simulation/`へ生成し、顔アプリと仮想ドライバが同じ生成物を読みます。
物理ボードのプロファイルは`hardware/`で、gpio0・SPI0 CS0の列挙と要求を実機で確認しています。
物理ピン番号とLinux line offsetは混同しません。
