---
title: 字符串比较中NSNumericSearch选项的工作原理
categories: ObjC
tags: [ObjC, NSNumericSearch, NSStringCompareOptions, NSString, 比较, 版本]
date: 2019-02-28
---

相信研究过怎么在 ObjC 中进行版本字符串比对的朋友，大多都看过这一篇 StackOverflow 的问答：

[Compare version numbers in Objective-C](https://stackoverflow.com/a/1990854/2562905)

里面提到的 `[versionStrA compare:versionStrB options:NSNumericSearch]` 的方案应该是最优雅的方案了。

但是不理解这个 NSNumericSearch 的具体工作原理就去盲目使用是危险的，今天我就来研究下它的具体工作原理。

<!--more-->

# 官方文档 

参照[官方文档](https://developer.apple.com/documentation/foundation/nsstringcompareoptions/nsnumericsearch)里的说明：

```
Numbers within strings are compared using numeric value, that is,
Name2.txt < Name7.txt < Name25.txt.

Numeric comparison only applies to the numerals in the string, not other characters that
would have meaning in a numeric representation such as a negative sign, a comma, or a
decimal point.
```

粗略的直译一下：

```
在字符串中的数字将被用数值进行比较，就是说，Name2.txt < Name7.txt < Name25.txt。

数值比较仅仅对字符串中的纯数字（0-9）生效，而不对其它在数字表达中含有意义的字符生效，例如负号，逗号或小数点。
```

这段说明略有歧义，导致很多人第一次看的时候被绕晕。例如刚刚那篇 StackOverflow 问答里的 dooleyo 就理解成 `"1.2.3"` 和 `"1.1.12"` 进行比较时，会抛弃所有非数字的字符变成 `123` 和 `1112` 进行比较，最后得到 `"1.2.3" < "1.1.12"` 的结论。问答里不少其它朋友也有类似的想法。

# 探求真相

真相只有经过实验才能得到，所以写了一些测试代码来试一下具体的结果：

```
- (void)testExample {
    [self compareString:@"1.2.3" andString:@"1.1.12"];
    [self compareString:@"1.8" andString:@"1.7.2.3.55"];
    [self compareString:@"1.44" andString:@"1.5"];
    [self compareString:@"7.4.1" andString:@"7.5"];
}
    
- (void)compareString:(NSString *)stringA andString:(NSString *)stringB {
    NSComparisonResult result = [stringA compare:stringB options:NSNumericSearch];
    switch (result) {
        case NSOrderedDescending:
            NSLog(@"%@ > %@", stringA, stringB);
            break;
        case NSOrderedAscending:
            NSLog(@"%@ < %@", stringA, stringB);
            break;
        default:
            NSLog(@"%@ = %@", stringA, stringB);
            break;
    }
}
```

得到的结果是：

```
1.2.3 > 1.1.12
1.8 > 1.7.2.3.55
1.44 > 1.5
7.4.1 < 7.5
```

看上去结果都是正确的，那么看来 `NSNumericSearch` 并不是粗暴的去掉所有非数字字符后进行数值比对。

结合原回答里答主说的一句话：`keeping in mind that "1" < "1.0" < "1.0.0"`，忽然想到了一些什么，继续进行下一步的实验，得到的结果如下：

```
1 < 1.0
1.0 < 1.0.0
a10 < b2
a2 < b10
c10 > b2
c2 > b10
2a < 10b
10a > 2b
2c < 10b
10c > 2b
```

大家看到这里应该可以猜到官方文档的意思是什么了，其实文档的意思是整个字串**非数字的部分仍然进行常规的字符比较逻辑，只有在遇到数字的时候会把连续的数字转换成数值再进行比对**。具体的比较过程示例参照下图：

![28-A](/2019/02/28-A.png)

这时候一些奇特的比对结果就可以解释明白了，比如使用这种比较模式会得出 `"01" = "1"`。

# 继续深入

那么还剩下一个问题，如果和数字字符比较的是非数字字符，会怎么样？我们可以挑一些 ASCII 码在数字字符周围的字符进行试验，结果如下：

```
a/c < a100c
a:c > a100c
a/c < a1c
a:c > a1c
```

注意这里出现的部分字符 ASCII 码为：

```
/ = 47
0 = 48
1 = 49
...
9 = 57
: = 58
```

可以看出现了比较的字符一边是数字，一边是非数字时，是按照常规的 ASCII 码进行比对的。

# 总结

那么分析到这里就基本结束了，剩下的一些场景类推一下都很容易理解。

其实在各大 OS 里的文件系统下文件排序用的就是这种比较方法，一开始没有想到这点所以理解上绕了一些弯路。

用 `NSNumericSearch` 来进行版本字符串的比对也是十分有效的，不是特殊需要的话就再也不用傻傻的自己分割字符串再分段比较啦。
