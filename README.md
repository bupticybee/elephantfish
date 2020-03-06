![Elephantfish logo](logo/elephantfish.jpg)

## 介绍 

elephantfish 是受到 [sunfish](https://github.com/thomasahle/sunfish) 启发而撰写的纯python的中国象棋引擎， 整个象棋引擎核心代码只有124行（见[compressed.py](compressed.py)）。

## 运行截图

    Think depth: 6 My move: b9c7

      9 俥．象士将士象傌俥
      8 ．．．．．．．．．
      7 ．砲傌．．．．砲．
      6 卒．卒．卒．卒．卒
      5 ．．．．．．．．．
      4 ．．．．．．．．．
      3 兵．兵．兵．兵．兵
      2 ．炮．．炮．．．．
      1 ．．．．．．．．．
      0 车马相仕帅仕相马车
        ａｂｃｄｅｆｇｈｉ
        
    Your move:

# 运行elephantfish!

elephahtfish 自包含在 `elephantfish.py` 文件中，只是用了python的自带操作而没有使用任何第三方库. 建议使用 `pypy` 或者 `pypy3` 来获得更好的性能表现.

# 特性

1. 使用简单而高效的 MTD 二分搜索算法（见[对弈程序基本技术](articles/对弈程序基本技术.pdf)）.
2. 使用众所周知的现代象棋引擎trick 比如空着裁剪.
3. 通过简单的子力价值表进行局面评估.
4. 使用python标准数据结构.

# License

[GNU GPL v3](https://www.gnu.org/licenses/gpl-3.0.en.html)
