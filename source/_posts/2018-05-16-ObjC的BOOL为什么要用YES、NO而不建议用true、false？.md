---
title: ObjC的BOOL为什么要用YES、NO而不建议用true、false？
subtitle: 使用BOOL类型的注意点
categories: ObjC
tags: [ObjC, BOOL, YES, NO, true, false]
date: 2018-05-16
---

嗯，昨天给自己挖了个坑，还是早填坑早完事儿，所以今天有了这篇：

朋友，ObjC 的 BOOL 类型了解一下？

可能有人告诉你 BOOL 是 `signed char` 类型的。放在以前，这个答案是对的，但是放在现在就不完全对了。接下来我来给大家一点点解释其中的细节。

<!--more-->

# ObjC 的 BOOL 到底是什么类型？ 

当前我的 Xcode 版本是 9.3.1，BOOL 的定义是这样的（有适当删减）：

```
#if TARGET_OS_OSX || (TARGET_OS_IOS && !__LP64__ && !__ARM_ARCH_7K)
#   define OBJC_BOOL_IS_BOOL 0
#else
#   define OBJC_BOOL_IS_BOOL 1
#endif

#if OBJC_BOOL_IS_BOOL
    typedef bool BOOL;
#else
#   define OBJC_BOOL_IS_CHAR 1
    typedef signed char BOOL; 
#endif
```

作为 iPhone 开发者（🙄），可以近似的理解为在 64-bit 设备上 BOOL 实际是 `bool` 类型，在 32-bit 设备上 BOOL 的实际类型是 `signed char`。

# YES / NO 是什么？

那么 `YES` / `NO` 又分别是什么值呢？我们看一下具体的定义：

```
#if __has_feature(objc_bool)
#define YES __objc_yes
#define NO  __objc_no
#else
#define YES ((BOOL)1)
#define NO  ((BOOL)0)
#endif
```

这里要先看一下 `__objc_yes` 和 `__objc_no` 是什么值，我们在 [LLVM 的文档](https://releases.llvm.org/3.1/tools/clang/docs/ObjectiveCLiterals.html)中可以得到答案：

```
The compiler implicitly converts __objc_yes and __objc_no to (BOOL)1 and (BOOL)0. The keywords are used to disambiguate BOOL and integer literals.
```

`__objc_yes` 和 `__objc_no` 其实就是 `(BOOL)1` 和 `(BOOL)0`，这么写的原因就是为了消除 BOOL 和整型数的歧义而已。

`(BOOL)1` 和 `(BOOL)0` 这个大家应该也都能很容易理解了，其实就是把 1 和 0 强转成了 BOOL 对应的实际类型。

所以综上所述为了类型的正确对应，在给 BOOL 类型设值时要用 `YES` / `NO`。

# true / false 是什么？

最早的标准 C 语言里是没有 `bool` 类型的，在 2000 年的 C99 标准里，新增了 `_Bool` 保留字，并且在 `stdbool.h` 里定义了 `true` 和 `false`。`stdbool.h` 的内容可以参照[这里](https://clang.llvm.org/doxygen/stdbool_8h_source.html)：

```
#define bool _Bool
#define true 1
#define false 0
```

这里只截取了标准 C 语言情况下的定义（C++ 是自带 bool 和 true、false 的）。可以看到这里只是定义了它们的值，但是却没有保证它们的类型，就是说 `true` / `false` 其实可以应用在各种数据类型上。

有些人还提到 `TRUE` / `FALSE` 这两个宏定义，它们其实不是某个标准定义里的内容，一般是早年没有标准定义时自定义出来替代 `true` / `false` 使用的，大部分情况下他们的定义和 `true` / `false` 一致。

我们可以写一段代码来验证下：

```
BOOL a = TRUE;
a = true;
a = YES;
```

使用 Xcode 的菜单进行预处理，展开宏定义：

![16-A](/2018/05/16-A.png)

然后我们就可以得到展开后的结果：

```
BOOL a = 1;
a = 1;
a = __objc_yes;
```

# 为什么要对 BOOL 用 YES / NO 而不是 true / false？

可以看到 ObjC 是自己定义了 BOOL 的类型，然后定义了对应要使用的值 `YES` / `NO`，理所当然的第一个原因是我们要按照标准来。

另一方面，既然 ObjC 的 BOOL 使用的不是标准 C 的定义，那么以后这个定义可能还会修改。虽然说概率很低，但是毕竟从上面的代码看就经历了 `signed char` 到 `bool` 的一次修改不是么？为了避免这种风险，建议还是要使用 `YES` / `NO`。

在某些情况下，类型不匹配会导致 warning，而 `YES` / `NO` 是带类型的，可以保证类型正确，所以建议要用 `YES` / `NO`。

# 使用 BOOL 类型的注意点

因为 BOOL 类型在不同设备有不同的表现，所以有一些地方我们要注意。

## 不要手贱写 "== YES" 和 "!= YES"

在 BOOL 为 `bool` 类型的时候，只有真假两个值，其实是可以写 "== YES" 和 "!= YES" 的。我们先举个例子：

```
BOOL a = 2;
if (a) {
    NSLog(@"a is YES");
} else {
    NSLog(@"a is NO");
}
if (a == YES) {
    NSLog(@"a == YES");
} else {
    NSLog(@"a != YES");
}
```

在 64-bit 设备我们将得到结果：

```
a is YES
a == YES
```

看上去没什么毛病，完美！

但是在 32-bit 设备我们将得到结果：

```
a is YES
a != YES
```

这是为什么呢？因为在 32-bit 设备上 BOOL 是 `signed char` 类型的。ObjC 对数值类型做 `(a)` 这种真假判断时为 0 则假、非 0 则真，所以我们可以得到 `a is YES` 这种结果。但是对数值类型做 `(a == YES)` 这种判断时逻辑是什么样的，想必不用我说大家也猜到了，代码翻译出来就是类似这样的：

```
signed char a = 2;
if (a == (signed char)1) {
    NSLog(@"a == YES");
} else {
    NSLog(@"a != YES");
}
```

我们当然只能得到 `a != YES` 这样的结果。

## 避免把超过 8-bit 的数据强转成 BOOL

同样在 64-bit 的设备上，也就是 `bool` 类型上不会有这个问题，但是在 `signed char` 类型上就会有这个问题。我们先看代码：

```
int a = 256;
if (a) {
    NSLog(@"a is YES");
} else {
    NSLog(@"a is NO");
}
BOOL b = a;
if (b) {
    NSLog(@"b is YES");
} else {
    NSLog(@"b is NO");
}
```

在 32-bit 设备上输出结果：

```
a is YES
b is NO
```

是不是有点魔幻？但是原因也惊人的简单：

- `a` 的二进制值为 00000000 00000000 00000001 00000000
- 转换为 `signed char` 类型的 `b` 时丢失了高位
- `b` 的二进制值为 00000000

所以千万不要做这样的蠢事，更常见的例子是一个 C 函数（十分直观）：

```
// 正确的用法
bool isDifferent(int a, int b) {
    return a - b;
}
// 错误的用法
signed char isDifferent(int a, int b) {
    return a - b;
}
```

# 总结

希望今天的介绍可以让你更深入的了解 ObjC 的 BOOL 类型，小心点不要在代码里埋出大 bug 哦。😁