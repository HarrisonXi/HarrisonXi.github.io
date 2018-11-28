---
title: EasyReact的简单试用及和RAC的对比
categories: iOS
tags: [iOS, EasyReact, RAC, Reactive Cocoa, MVVM]
date: 2018-08-16
---

美团开源了船新的响应式框架 [EasyReact](https://tech.meituan.com/react_programming_framework_easyreact_opensource.html)，GayHub地址：[https://github.com/meituan/EasyReact](https://github.com/meituan/EasyReact)

作为热爱响应式的程序猿，一定是要试用评测一下这传说中又快又好用的新框架的，事不宜迟我们开始。（虽然这框架已经开源一个月了🙄）

<!--more-->

# 使用 EasyReact 的 MvvmDemo

评测的具体方案是用我以前的 [MvvmDemo](http://blog.harrisonxi.com/2017/07/iOS%E4%BD%BF%E7%94%A8RAC%E5%AE%9E%E7%8E%B0MVVM%E7%9A%84%E6%AD%A3%E7%BB%8F%E5%A7%BF%E5%8A%BF.html) 改造一下，旧 demo 的代码参照 [GitHub](https://github.com/HarrisonXi/MvvmDemo)。使用这个改造的方案，可以更方便的进行 EasyReact 和 RAC 的对比。

首先进行 EasyReact 的安装，不得不说支持 CocoaPods 的库安装起来还是方便。但是 EasyReact 是没有提供打包好的 Framework 或者对应的 Framework 工程的，这就不太方便进行一次打包多处直接使用二进制包了。

| EasyReact 优缺点           |
| -------------------------- |
| ✅ 支持 CocoaPods           |
| ❌ 没有提供二进制 Framework |

为了方便对比，我把使用 EasyReact 和 RAC 的对比做成了一个独立的 [commit 0feb1cb](https://github.com/HarrisonXi/MvvmDemo/commit/0feb1cbc35467fb1e75f3c10199d5987ec2cb573)。可以看到其实从语法上来说，它们的常规使用方法十分的相似。然后我们来一点点比较细节的差异。

# EZRNode vs RACSignal

RACSignal 的设计概念是表示一个可以被订阅的信号流，最主要的意义是表示其内部的值是变化的。而 RACSubject 是表示一个热信号流，热信号和冷信号的内容后面再说，当前主要先要说的 RACSubject 的特征是可以手动发送信号。

EZRNode 从设计上看上去更像是一个存着 value 的 model，这个使得初学者很容易理解它的用途。而 EZRMutableNode 使得 node 存着的 value 可以被修改，然后修改这个 value 的时候就会对外发出信号。说起来我个人觉得这种设计的确可以让过程式编程的开发者更容易理解和过渡到响应式编程中，但是有点略二不像的设计也会带来对应的困扰。

## 1. 到底 EZRNode 的 value 是不是可变的

如果我们认为 EZRNode 的 value 是不可变的，那么 EZRNode 提供 `listenedBy:` 就会很奇怪，一个不可变的值我们监听它干什么呢？

如果我们认为 EZRNode 的 value 是可变的，那么有些接口的设计又看上去很怪，典型的代表就是响应式编程最常用到的宏定义 `EZR_PATH` 的实现类 `EZRPathTrampoline`，在其内部都默认认为 EZRMutableNode 才可以进行绑定。

我觉得从总体设计上来看，其实应该认为 EZRNode 的 value 值是可变的，`EZRNode+Operation.h` 中的变换都是基于 EZRNode 来实现的可以证明这一点。另一种理解是哪怕是不可变的值，其实也可以变换和监听的嘛，这样看起来 EZRNode 的意义和 RACSignal 其实是十分接近的。

另外 `EZRPathTrampoline.m` 里面有个小细节：

```
- (void)setObject:(EZRNode *)node forKeyedSubscript:(NSString *)keyPath {
    NSParameterAssert(node);
    NSParameterAssert(keyPath);
    
    EZRMutableNode *keyPathNode = self[keyPath];
    [_cancelBag addCancelable:[keyPathNode syncWith:node]];
}
```

可以看到在头文件里定义的 `node` 参数是 EZRMutableNode，但是类实现里其实用的是 EZRNode，让我不禁怀疑是不是头文件里的类型写错了……😓

得出的第一个结论：姑且认为 EZRNode 的意义和 RACSignal 相同，是信号的最基础单元。

## 2. EZRNode 还是 EZRMutableNode

这个问题和问题1其实有点重叠，主要原因的根源还是宏定义 `EZR_PATH` 的实现类 `EZRPathTrampoline`。

对外暴露 EZRNode 类似于对外暴露一个 readonly 的属性，用户表面上可以感知到不可以修改其内部的 value。但是面临的一个问题是，用户想要使用 `EZR_PATH` 宏进行绑定时还是要进行一次 `mutablify` 的转换。

对外直接暴露 EZRMutableNode 的话相当于暴露了一个 readwrite 的属性，用户不仅可以监听它，同时也具备了可以修改其 value 的能力，这对于维持一个 ViewModel 的封装性来说可是个灾难。

还有一点是，EZRNode 转成 EZRMutableNode 时，复用了原先的内存地址。

```
EZRNode *node = [EZRNode new];
EZRMutableNode *mutableNode = [node mutablify];
```

上面代码里 `node` 和 `mutableNode` 的指针是完全相等的，当然它们的 class 也都会是 EZRMutableNode。这样的好处就是转换前后，它们的逻辑都是连续的；坏处是类型原地转换的逻辑会导致使用方比较混乱（可能前一秒还是 EZRNode 的实例，下一秒就被别人变成 EZRMutableNode 了），另外 `mutablify` 的转换也是不可逆的。

这样设计应该也是没有办法：虽然说起来它们和 NSString & NSMutableString 组合有很多相似的地方，但是要支持 copy 协议是很麻烦的。比如想要维持监听的链路不被打断，信号源这种东西在支持 copy 时是很容易出大问题的，要复制要维持的状态多得难以想象。

综上所诉，我们设计接口时到底是暴露 EZRNode 还是 EZRMutableNode 类型会有很大的困扰。相比较而言，RAC 就没有这个困扰，不想让别人知道这是个可以手动发信号的 RACSubject，包装成 RACSignal 暴露出去就好。其实我还是觉得 EasyReact 去修改下 `EZRPathTrampoline` 应该也可以达成类似的效果😓。

不过关于 Node 可变状态的转换的确也没有想到什么好的办法，现在的这个设计模式，即使用 readonly 式的 EZRNode 暴露接口给外界也是形同虚设，毕竟外界拿到这个 EZRNode 之后手动  `mutablify` 一下，然后想怎么改就怎么改。

## 3. 冷信号热信号

冷信号一直是 RAC 里面一个让响应式编程新手懵逼的概念，详细的概念我在《[RAC中的冷信号与热信号](http://blog.harrisonxi.com/2017/09/RAC%E4%B8%AD%E7%9A%84%E5%86%B7%E4%BF%A1%E5%8F%B7%E4%B8%8E%E7%83%AD%E4%BF%A1%E5%8F%B7.html)》中介绍过。

既然容易让新手懵逼，那么 EasyReact 是怎么处理的呢？EasyReact 里好像就压根没有提供冷信号的概念😂。

这样倒是也挺好的，让使用者自己基于 block 和各种事件倒是也能完成类似的逻辑，省得新手在理解上有错误而导致写出的代码有严重问题。

| EasyReact 优缺点                                             |
| ------------------------------------------------------------ |
| ✅ 易理解，抛弃了大量对初学者很晦涩的响应式概念               |
| ❌ 框架内部接口的设计对 EZRNode & EZRMutableNode 的理解貌似本身就不一致 |
| ❌ 不可变和可变 node 的无缝转换过程可能引发其它业务方的逻辑混乱 |
| ❌ EZRNode 完全做不到 readonly 的效果，形同虚设                |
| ⚠️ 抛弃了冷信号的概念，这个优劣参半吧                         |

# 宏定义 EZR_PATH

`EZR_PATH` 宏是和 RAC 中的 `RAC` & `RACObserve` 两个宏相同地位的核心宏方法，最大的不同点是它把 RAC 中的两个宏合并成了一个宏。

这是个好事儿还是坏事儿呢？我个人觉得两面都有。

```
// RAC
RAC(self.loginButton, enabled) = RACObserve(self.viewModel, loginEnabled);
// EasyReact
EZR_PATH(self.loginButton, enabled) = EZR_PATH(self.viewModel, loginEnabled);
```

参照上面的代码示例还有 `EZRPathTrampoline` 的实现：

1. 首先我觉得用一个类同时实现监听和被监听两件事，从内聚性上来说讲的过去，可能的确是利大于弊的。
2. 从代码的阅读和书写上来说，书写只要记住一个宏，写起来会略方便一点点，阅读时也没什么障碍，毕竟一眼就可以看出来是等号左边的表达式监听了等号右边的表达式。
3. 从工程维护的大角度来说，只用一个宏，很难区分这个宏出现的地方是实现监听者还是被监听者。

第三点我们拓展开来举个例子，用之前 MvvmDemo 里的代码来看，我想要知道哪些人监听过 ViewModel 的 username 属性，哪些人让 ViewModel 的 username 属性监听过其它信号：

![20-A](/2018/08/20-A.png)

![20-B](/2018/08/20-B.png)

快速定位，精准无误有木有！只用一个 `EZR_PATH` 宏的话这些就无法简单精准定位了，写复杂的正则或许能搞定，但是也会麻烦很多。这个需要自行体会，基础架构实现的底层模块的属性，被监听和监听其它属性的信号流多如牛毛，能让定位的复杂度降低是提高工作效率的重要保证。

| EasyReact 优缺点                                             |
| ------------------------------------------------------------ |
| ⚠️ EZR_PATH 宏易用、二合一，但是也导致难以区分是实现监听者还是被监听者 |

# 对系统类的扩展

基于刚刚提到的 [commit 0feb1cb](https://github.com/HarrisonXi/MvvmDemo/commit/0feb1cbc35467fb1e75f3c10199d5987ec2cb573) 的 MvvmDemo 是不完整的，一个很重要的原因就是 UITextField 这类 UI 控件，是不可以通过监听它的 text 属性就能简单实现响应式的。所以我们必须要一个新的 [commit ad46b53](https://github.com/HarrisonXi/MvvmDemo/commit/ad46b53d99920a377de01a4da4f95c44022ef896)，来把 UITextField 依然通过 delegate 的方式链接到 ViewModel 上，说起来就是还是抛弃不了过程式的开发方法。

这点我相信美团内部应该还是有对应的一些封装吧，日后或许也会渐渐开源出来。毕竟如果一套响应式框架如果没有办法很便捷的应用到业务层的 UI 上，实用性就会大打折扣。

相比较来说沉淀了多年的 RAC 强大的多，不光连 UI 控件的扩展封装很完备，还为了具体的场景需要实现了 RACCommand 和 RACChannel 等类，甚至于连 UserDefaults 都做了对应的扩展封装。

| EasyReact 优缺点                     |
| ------------------------------------ |
| ❌ 没有对系统类的扩展，易用性大打折扣 |

# 性能对比

美团官博写着的 EasyReact 还有一个最大的亮点就是性能起飞！不过当然要实践出真知，不能盲目的相信当事人自己的数据。基于上面的 MvvmDemo，我来自己做一个简单的性能对比试验一下：

```
- (void)testPerformance {
    [self measureBlock:^{
        TestObject *object = [TestObject new];
        ViewModel *viewModel = [ViewModel new];
        NSArray *array = @[@"0", @"1", @"2", @"3", @"4", @"5", @"6", @"7", @"8", @"9"];
        EZR_PATH(viewModel, username) = EZR_PATH(object, username);
        EZR_PATH(viewModel, password) = EZR_PATH(object, password);
        EZR_PATH(object, usernameColor) = ConvertInputStateToColor(EZR_PATH(viewModel, usernameInputState));
        EZR_PATH(object, passwordColor) = ConvertInputStateToColor(EZR_PATH(viewModel, passwordInputState));
        EZR_PATH(object, loginEnabled) = EZR_PATH(viewModel, loginEnabled);
        for (int i = 0; i < 1000; i++) {
            object.username = array[i % 10];
            object.password = array[i % 10];
        }
    }];
}
```

如上单元测试，在 RAC 的分支和 EasyReact 的分支各实现一次，运行完了之后对比总耗时：

![20-C](/2018/08/20-C.png)

可以看到，在综合了 combine、listen、map 等操作的实验下，EasyReact 的效率在 RAC 的三倍以上。

| EasyReact 优缺点                     |
| ------------------------------------ |
| ✅✅ EasyReact 的效率在 RAC 的三倍以上 |

# 调试复杂度

EasyReact 的 EZRNode 概念比起 RACSignal 来说，是确确实实的持有了一个 value 的，所以调试起来有相当大的优势。举几个例子：

1. 可以给 `setValue:` 加个断点，设置进来的新值和之前的旧值都可以轻松获得。
2. 任何时机可以方便的直接用 `.value` 拿到现在的节点值，按照文档描述这个值是线程安全的，放心使用。
3. 堆栈的深度上及调用的逻辑上看上去**可能**会更简单。

还有很多其它的可能性，不过这里先展开说一下第3点。下面是同一个单元测试，EasyReact 下的堆栈状态：

![20-D](/2018/08/20-D.png)

对应的 RAC 下的堆栈状态：

![20-G](/2018/08/20-G.png)

……

![20-F](/2018/08/20-F.png)

堆栈长度从22激增到了52（这也是 RAC 效率低一些的重要原因吧🙄）。

倒是如果把代码隐藏起来（非代码展开，直接使用打包好的 Framework），其实 RAC 的堆栈也会比较清晰：

![20-E](/2018/08/20-E.png)

可以看到虽然堆栈长度还是很大，但是层级上只展示了几个关键层。

这种信号流调试起来，说起来谁更方便些真的没有定论，因为毕竟都很麻烦😂。加上跨线程调用的情况，更是难上加难，所以我在这里也就不硬比个高低了。倒是总体说起来 EasyReact 概念简单，设计也简单，应该调试难度肯定会更低一些的。

| EasyReact 优缺点         |
| ------------------------ |
| ✅ EasyReact 调试难度更低 |

# 文档 & 社区

文档也是重要的一点，这里长话短说了。

RAC 的文档一直是比较差的，这么难的框架还只能靠自己还有零散的博文来啃，的确有些吃力。看 RAC 各种复杂高级变换时，很多时候是借助 ReactiveX 框架的示意图（[例如这个 zip 的示意图](http://reactivex.io/documentation/operators/zip.html)）来理解的，这些示意图很好很强大，学习响应式的朋友也可以去观摩学习下。

EasyReact 的设计比较简单，文档相对来说就好理解些，而且官方中文文档这点对于国人开发者来说太友好了！

社区的活跃度这点目前就不清楚会怎样了，国内的社区氛围一直比较差，还不清楚遇到具体的问题时，美团官方的跟进及各大社区的讨论会如何，只能说不抱很大期望。

| EasyReact 优缺点                 |
| -------------------------------- |
| ✅ 文档齐全，官方中文             |
| ⚠️ 本人个人对社区氛围不抱太大期望 |

# 总结

老实说光性能这一点，EasyReact 就值得推荐。对于学习响应式框架的初学者来说，EasyReact 是可以尝试的，整体来说它的概念更简单。但是就完备程度来说，EasyReact 还有一段很长的路要走，对 RAC 熟悉程度比较高的程序猿，开发效率肯定还是更高的。所以说从开发效率、运行性能和学习成本等各方面考虑，选择适合你们自己团队的响应式框架吧。

