# Luckfox Lyra Zero Wの配線計画

2026-10-30作成、2026-10-31実機導入。
利用者による配線修正後、SPI 8MHzで液晶に顔が表示されることを確認しました。
ノブも再接続後に両方向の回転と押下をログで確認し、利用者が表情の切替とまばたきを確認しました。
反応頻度の問題は、Lyra用GPIO CSVで1ミリ秒のデバウンスを要求して解消しました。
共通GPIO読取の番号判定は元の`seqno`方式へ戻し、右10クリック・左10クリックの全20回と押下1回を受信しています。[確認記録](../docs/ROTARY_INPUT.md)

制御ボードをLuckfox Lyra Zero W（RK3506B）へ変更し、既存と同じ
YMS PARTSのGC9A01互換7ピン液晶とKY-040を接続します。
型番は`components.csv`、接続は`connections.csv`、実行時割当は
`gpio.csv`・`spi.csv`を正本とします。

## 端子の数え方

表の「物理ピン」は40ピンヘッダーの1〜40番です。GPIO番号やRM_IO番号ではありません。
基板の向きを[公式ピン図](https://www.luckfox.com/image/catalog/development-board/Luckfox-Lyra-Zero-W/Luckfox-Lyra-Zero-W-inter.jpg)と照合し、
3V3_OUTの1番と隣のVSYSの2番を区別します。図のGPIOに添えられた青い数字
（3・4・41など）はGPIOの番号で、ヘッダーの物理ピン番号ではありません。
Raspberry PiやLyra PlusのSPI配線表を流用しません。

## 7ピン円形液晶

| 液晶端子 | Zero W物理ピン | 電源／割当 | 用途 |
| --- | ---: | --- | --- |
| VCC | 1 | 3V3_OUT | 3.3V電源 |
| GND | 9 | GND | 共通グラウンド |
| SCL | 27 | RM_IO24 → SPI0 SCLK | SPIクロック |
| SDA | 29 | RM_IO25 → SPI0 MOSI | 液晶へのデータ |
| CS | 33 | RM_IO27 → SPI0 CS0 | チップ選択 |
| DC | 11 | RM_IO3 / GPIO0_A3 | 命令／データ切替 |
| RST | 13 | RM_IO4 / GPIO0_A4 | 液晶リセット（Lowでリセット） |

SDA/SCLはこの液晶の**SPI端子名**です。I²Cには接続しません。
7ピン液晶にはMISOとBLKの配線を追加しません。
送信専用で使うためSPI0のMISOは無効です。RM_IO26（物理31番）は配線しません。

## KY-040

| ノブ端子 | Zero W物理ピン | 電源／割当 | 用途 |
| --- | ---: | --- | --- |
| ＋ | 17 | 3V3_OUT | 3.3V電源 |
| GND | 25 | GND | 共通グラウンド |
| CLK | 15 | RM_IO5 / GPIO0_A5 | 回転A相 |
| DT | 19 | RM_IO6 / GPIO0_A6 | 回転B相 |
| SW | 21 | RM_IO7 / GPIO0_A7 | 押下（Lowで押下） |

CLK・DT・SWはプルアップを要求します。共有の`gar_rotary_input`の
`--bias pull-up`を利用しています。実機で内部プルアップが使えない場合は、
3.3Vへの外付け抵抗（例えば10kΩ）を用意して未操作時のHighを確認します。
両方向の回転通知と押下通知は実機で確認済みです。回転による表情切替と押下による
まばたきは共通アプリが担当します。

実機用`gpio.csv`の任意列`debounce_us`に、CLK・DT・SWとも`1000`を指定します。
アプリがCSVを読み、共有読取へ`--debounce-us 1000`を渡します。共有読取はGPIOの確保時に
Linux GPIO v2の`GPIO_V2_LINE_ATTR_ID_DEBOUNCE`を要求します。値の正本はProductのCSVです。
ドライバーのソースやボード全体の固定値を書き換える処理ではありません。
本SDKではカーネル内のソフトウェアデバウンスが使われ、生の割り込みは引き続き発生します。
要求値1000µsは実際のタイマー精度・スケジューリングにより丸められる場合があります。

## 電源と未使用端子

ボード本体は電源用USB-C OTGポートから給電し、液晶とノブはヘッダーの3.3Vを使います。
VSYSの2・4番は今回の周辺部品には配線しません。GNDは同じボード上で共通です。
実配線の付け外しは給電を外した状態で行います。
UART0のRM_IO22・23（物理8・10番）は空け、デバッグ用接続を残します。
I²C2のRM_IO0・1も使用しません。MIPI DSIはこのSPI液晶には使いません。

## 実機の設定

`luckfox-config`のSPI0でSCLK=24、MOSI=25、CS=27、MISO無効を指定します。
Productの導入処理は`connections.csv`のRM_IOと物理用`spi.csv`の速度を読み、
メーカーの設定ツールを呼び出します。`/etc/luckfox-config.json`に保存されます。
DC・RST・ノブ用のRM_IO3〜7はGPIO v2で確保します。
実機で`/dev/gpiochip0`のラベルがgpio0であること、GPIO0_A3〜A7のoffsetが3〜7で
競合なく要求できること、SPIが`/dev/spidev0.0`に列挙されることを確認しました。

初回はSPI 1MHzで表示を確認し、現在は8MHzを使用しています。
全画面115200バイトの転送だけで理論上約0.115秒かかります。
20fpsを全画面転送する場合、画素データだけで18.432Mbpsが必要です。
シミュレータの描画速度を実機の転送性能として扱いません。

## シミュレータへのつなぎ方

WebPanelは液晶とノブの2部品だけを既存と同じ構成で使います。
専用Linux VMとローカルWebPanelで、この2部品の入出力を検証します。

| 役割 | そのまま使うソース | Product側の差分 |
| --- | --- | --- |
| 液晶の部品表示 | gar-toolsの`web-simulator/components/display.mjs`と`framebuffer.mjs` | 240×240の画素を接続 |
| KY-040の回転・押下 | gar-toolsの`web-simulator/components/rotary.mjs` | GPIO信号への接続 |
| GPIOの読取・回転判定 | gar-toolsの`targets/linux-device/runtime/rotary-input/` | chip・offset・pullをCSVで指定 |
| 液晶の初期化 | gar-toolsの`targets/linux-device/runtime/gc9a01-output/` | SPI・DC・RSTをCSVで指定 |
| 仮想デバイス・Bridge | gar-toolsのGC9A01 CUSEドライバとWeb Bridge | 独立したVMと仮想配線を構成 |
| 表情とアニメーション | 共通アプリ`gar-my-friend` | 共通アプリの改変は現時点で不要 |

`hardware/gpio.csv`・`spi.csv`は実機用の正本で、DC=3・RST=4・ノブ=5/6/7を指定します。
仮想側はこの割当を引き継ぎ、`simulation-overrides.csv`から`.gar/hardware/simulation/`へ生成します。
物理ピン番号とGPIO line offsetの区別は、基板プロファイルと`connections.csv`で確認します。
専用VM名・SSHポート2232・Panelポート8774・配布先は`config/simulator.json`に定義しています。
既存Orange Pi用の実機導入スクリプトやVM操作は、このZero Wには使用しません。

## 参照

- [Luckfox公式製品紹介](https://www.luckfox.com/Luckfox-Lyra-Zero-W)
- [公式ピン図](https://www.luckfox.com/image/catalog/development-board/Luckfox-Lyra-Zero-W/Luckfox-Lyra-Zero-W-inter.jpg)
- [luckfox-configのSPI設定例](https://wiki.luckfox.com/Luckfox-Lyra/luckfox-config/#34-spi-configuration)
- [購入ページ：ASIN B0FD9MXZST](https://www.amazon.co.jp/dp/B0FD9MXZST)
- [既存の液晶・ノブの確認記録](https://github.com/ThousandsOfTies/GarMyFriend-OrangePiZero2W/tree/main/hardware/modules)

公式ピン図のRM_IO割当と、公式SPI設定例を組み合わせたProductの配線案です。
購入済みの液晶・ノブは既存Productでの同定記録を引き継ぎ、Zero W上の動作確認と区別します。
