# compactCHaserServer

これはコードのデバッグ作業をする際に毎回CHaserServerを起動するのは大変なのでCUIで簡単にCHaserの対戦を行うことができるものです

## Get Started
```py server.py <mappath>```
でサーバーを起動できます

後はクライアントを起動して接続するだけで対戦が開始します

[CHaserViewer](https://github.com/yugu0202/CHaserViewer)を使用することで生成されるダンプからグラフィカルに見ることも可能です

## Options
| option | short | description | type | default |
| --- | :---: | --- | :---: | --- |
| first-port | f | 先行のポート | int | 2009 |
| second-port | s | 後攻のポート | int | 2010 |
| non-dump | nd | ダンプファイルの出力抑制 | bool | False |
| dump-path | d | ダンプファイルの出力先(実行ディレクトリから相対パス) | string | "./chaser.dump" |

## Usages
### 先行のポートを3001にする
`py server.py <mappath> -f 3001`  
or  
`py server.py <mappath> --first-port 3001`

### ダンプファイルの出力先を```./dump.dump```に変える
`py server.py <mappath> -d ./dump.dump`  
or  
`py server.py <mappath> --dump-path ./dump.dump`

### ダンプファイルを出力しない
`py server.py <mappath> -nd`  
or  
`py server.py <mappath> --non-dump`
