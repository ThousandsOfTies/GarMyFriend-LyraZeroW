# 配線・部品の正本

| ファイル | 役割 |
| --- | --- |
| `components.csv` | Zero W、YMS PARTS 7ピン液晶、KY-040の型番 |
| `connections.csv` | Zero Wの40ピンヘッダーからの物理配線案 |
| `gpio.csv`・`spi.csv` | シミュレータのGPIO/SPI割当 |
| `lyra-zero-w/gpio.csv`・`spi.csv` | 実機用。gpiochip0のgpio0とspidev0.0を実機で照合済み |
| `WIRING.md` | 端子表、電源、pinmux、未確認事項と根拠 |

仮想側もDC=3、RST=4、ノブ=5・6・7、SPI0 CS0として、同じ共通アプリを使います。
共有のCSV読込がアプリと仮想ドライバへ値を渡し、Bridgeも同じCSVを読みます。
GPIO番号の一致は電気的な再現や実機の列挙確認を意味しません。

`orangepi-zero2w/`は基底Productから引き継いだ旧プロファイルです。
このProductの起動・配布処理は選択しません。Zero Wの配線は`connections.csv`を使います。
