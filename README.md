![Elephantfish](logo/elephantfish.jpg)

## 介绍 

elephantfish 是受到 [sunfish](https://github.com/thomasahle/sunfish) 启发而撰写的纯python的中国象棋引擎， 整个象棋引擎核心代码只有124行（见[compressed.py](compressed.py)）,棋力方面我仅进行过其与象棋小巫师傻瓜难度的一场对局，在我测试的对剧中，elephantfish赢得了比赛。

在几天前看到了[sunfish](https://github.com/thomasahle/sunfish)这个项目(是一个国际象棋引擎，只有111行)，觉得很有意思，于是做了一个类似中国象棋版本，中国象棋和国际象棋略有不同，我仅仅单独完成了棋规部分，子力价值表直接的参考了 [象眼](https://www.xqbase.com/league/elephanteye.htm) ,mtd search部分的代码由于原版sunfish写的非常通用，我也就一行未改。

如果你对于程序中的mtd search看不懂建议先看一些对弈基础理论,比如articles下的几篇文章，如[对弈程序基本技术](articles/对弈程序基本技术.pdf)，其官方网址：https://www.xqbase.com/computer/outline.htm

elephantfish默认会进行5秒钟的思考，当然实际一般会比5秒多一些，如果你想要它进行更长时间搜索以获得更好的性能可以对源码相应位置进行更改。

如同sunfish一样，我认为elephantfish会是一个很好的平台，由于其代码非常少，可以很方便的进行各种实验，希望各位感兴趣的同学可以尝试对其进行优化. 如果在优化后想要评估和目前版本的棋力差别，可以使用test.py中的self_arena来将你的代码和elephantfish进行对弈。

如果你觉得这个版本的象棋ai实力不够强，可以看看 [XQpy](https://github.com/bupticybee/XQPy)

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

简单的使用命令```python elephantfish.py``` 或者```pypy elephantfish.py``` 就可以运行象棋程序,程序会利用自带一个命令行工具进行对局.

# 特性

1. 使用简单而高效的 MTD 二分搜索算法（见[对弈程序基本技术](articles/对弈程序基本技术.pdf)）.
2. 使用众所周知的现代象棋引擎trick 比如空着裁剪.
3. 通过简单的子力价值表进行局面评估.
4. 使用python标准数据结构.

# License

[GNU GPL v3](https://www.gnu.org/licenses/gpl-3.0.en.html)
