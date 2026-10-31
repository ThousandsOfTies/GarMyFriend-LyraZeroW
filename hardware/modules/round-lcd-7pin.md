# YMS PARTSの7ピン円形液晶

既存Productで同定した1.28インチ、240×240、GC9A01互換のSPI液晶です。
商品モデル番号は`YMS-circlelcd-pinari`、Amazon ASINは`B0G4JW94KZ`です。
実物の端子はRST / CS / DC / SDA / SCL / GND / VCCの7点で、BLK端子はありません。
SDAはSPIのMOSI、SCLはSPIクロックです。

Zero Wへの接続は[配線計画](../WIRING.md)と`connections.csv`を使います。
VCCと信号は3.3Vとします。既存の別ボードでの表示確認記録を、Zero W上での
動作確認として扱いません。コントローラーIDの読取は未実施です。
2026-10-31、Zero Wでも利用者による配線修正後に1MHzと8MHzで顔の表示を確認しました。

汎用初期化はgar-toolsの`gc9a01-output/gc9a01_init.h`、顔の描画はgar-my-friendが担当します。
