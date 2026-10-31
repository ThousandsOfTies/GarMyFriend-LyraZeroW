# リポジトリの分担

このProductは次の3つをsubmoduleで取り込み、コミットを固定します。

| リポジトリ | 役割 |
| --- | --- |
| [gar-my-friend](https://github.com/ThousandsOfTies/gar-my-friend) | 共通の顔アプリ |
| [gar-tools](https://github.com/ThousandsOfTies/gar-tools) | 共通の実行・デバイス機構 |
| [gar-board-lyra-zero-w](https://github.com/ThousandsOfTies/gar-board-lyra-zero-w) | 基板・OSの定義と固有資産 |

Productは`product.json`で3つを組み合わせ、実際の配線・部品・初期化パラメータと起動指定を持ちます。
基板の資源情報とProductの用途・配線は別の所有物です。[構成と操作](COMPOSITION.md)を参照してください。
共有側の変更は先にcommit/pushし、その後でProductのgitlinkを更新します。
