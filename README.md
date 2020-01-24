# README

## 実行方法

### 依存ライブラリのインストール

```
$ pip install numpy
$ pip install flask
$ pip install scipy
$ pip install gevent gevent-websocket
```

（この他に実行時要求された場合は逐次インストール）

### dumpファイルの作成

現在このファイルと同じディレクトリにいる場合

```
$ cd release/backend
$ python road_to_matrix.py
$ python make_shortest_path.py
```

### サーバ実行

現在このファイルと同じディレクトリにいる場合

```
$ cd release
$ python app.py
```

この状態で `http://localhost:8080` と表示されたらそのURLをブラウザで開く．
