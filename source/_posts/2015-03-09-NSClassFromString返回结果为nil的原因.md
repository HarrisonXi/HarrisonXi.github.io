---
title: NSClassFromString返回结果为nil的原因
categories: iOS
tags: [iOS, ObjC, NSClassFromString, nil, 返回, 结果, library, 静态库]
---

NSClassFromString算是ObjC动态化的精华之一，在运行时可以从一个NSString动态获得对应的Class，再创建其对应实例，调用实例内部方法。

可最近有一次写代码碰到了NSClassFromString结果总是为nil的问题，debug了半天才找到原因。

<!--more-->

# 因为未加载对应类导致的nil结果

先看看[StackOverflow传送门](https://stackoverflow.com/questions/2227085/nsclassfromstring-returns-nil)和苹果的NSClassFromString函数[官方文档](https://developer.apple.com/reference/foundation/1395135-nsclassfromstring)。

Return Value: The class object named by aClassName, or nil if no class by that name is **currently loaded**. If aClassName is nil, returns nil.

关键点就是标记的这里，NSClassFromString只能返回当前已经加载过的Class。所以在某些类并没有被使用过或加载过时，就会得到nil的结果。比如想要用NSClassFromString获得一个静态库里的类，通常就会遇到这种情况。这种时候我们要做的就是在**主工程的编译选项**里加一个参数：

![09-A](/2015/03/09-A.png)

如图，先选中工程的target，然后在Build Settings里搜一下Other Linker Flags，双击添加一个『-ObjC』，就OK了。如果你想要了解『-ObjC』这个flag具体是做什么的，可以参考[这个链接](https://developer.apple.com/library/content/qa/qa1490/_index.html)。

# 因为未实现对应类导致的nil结果

当然我碰到的问题不是这个……我的问题在于光写了`@interface`，忘记写`@implementation`了……也是醉了……

下图里面这个comment的人就是我，当然这位大哥说的.m文件忘记加到工程里也会导致同样的问题。

![09-B](/2015/03/09-B.png)

所以各位一定也要记得检查下，自己是不是也犯二了233。
