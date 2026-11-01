# 配線・部品の正本

| ファイル | 役割 |
| --- | --- |
| `components.csv` | Zero W、YMS PARTS 7ピン液晶、KY-040の型番 |
| `connections.csv` | Zero Wの40ピンヘッダーからの物理配線案 |
| `gpio.csv`・`spi.csv` | GPIO/SPI割当と初期化値の唯一の正本。実機はこのまま使う |
| `simulation-overrides.csv` | シミュレータで変更する値だけ。配線番号は重ねて記載しない |
| `WIRING.md` | 端子表、電源、pinmux、未確認事項と根拠 |

正本はDC=3、RST=4、ノブ=5・6・7、SPI0 CS0、SPI 8MHz、ノブのデバウンス1ミリ秒です。
`python tools/product.py hardware --environment simulation`で、差分を適用したCSVを
`.gar/hardware/simulation/`へ生成します。配線番号は正本を引き継ぎ、ノブのデバウンスを0、
SPIを1MHz、仮想液晶ドライバを`gc9a01`にします。生成物はGit管理しません。
シミュレータの顔アプリ・仮想ドライバ・Bridgeは同じ生成済みCSVを読みます。
GPIO番号の一致は電気的な再現や実機の列挙確認を意味しません。

基板の資源・OS情報は`../sources/board-lyra-zero-w/`で管理します。
`components.csv`は部品一覧、`connections.csv`は物理ピン間の配線です。
GPIOの実行時割当と役割を分けて残し、同じ内容の別プロファイルは手で管理しません。
