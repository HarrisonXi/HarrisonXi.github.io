---
title: 苹果梨的博客 - iOS系统window的旋转及自定义window的问题
category: iOS
tag: window, 旋转, 自定义, iOS, 开源
---

# iOS系统window的旋转及自定义window的问题

### 玩转window，真的是玩『转』

| 更新时间       | 更新内容 |
| ---------- | ---- |
| 2017-02-15 | 发布   |

具体某些细节内容和我的开源库[TopmostView](https://github.com/HarrisonXi/TopmostView)相关。

大家的App都会有全屏的引导页或者Loading界面之类吧？如果你的App结构比较简单，比如RootController是一个NavigationController，而且需要展示全屏页面的时候不存在present新VC或正在做VC切换动画之类的情况，那么直接在RootController的view上面做这些就可以。但是因为这种方案下还有各种意想不到的情况会导致全屏页面展示出问题，所以大家一般又会选择在application window上加一个subview来处理全屏页面的展示。

在App不存在旋转的情况下，这个方法就是最终最优解了。

在App支持旋转的情况下，要处理的问题就比较多了，下面整理我遇到的一些问题。

#### iOS7的window和之后版本iOS系统的表现不一致

在一个iOS7的iPad上创建一个自定义window，再呼起键盘确保键盘window出现，在横屏的状态下断点并打印一下所有window的列表（过滤了一些我们不需要的信息）：

```
<__NSArrayM 0x165c5d20>(
<UIWindow: 0x1656e710; frame = (0 0; 768 1024)>,
<UITextEffectsWindow: 0x165bcdc0; frame = (0 0; 768 1024); transform = [0, 1, -1, 0, -128, 128]>,
<UIWindow: 0x1659bc70; frame = (0 0; 768 1024); userInteractionEnabled = NO>,
)
```

可以看到两点：

- window的宽高始终固定是768x1024，即竖屏的状态
- 键盘window自带了一个transform属性，正好可以将竖屏的window旋转成横屏的大小&位置

键盘window是iOS7里，系统唯一自动处理了的window，因此维持其subview在横屏的时候frame = (0 0; 1024 768)，竖屏的时候frame = (0 0; 768 1024)就可以保证展示正常。

而其它window的frame和transform都没有被处理，系统是怎么保证我们的界面显示正常呢？打印application window的subview看一下就明白了（过滤了一些我们不需要的信息）：

```
<__NSArrayM 0x165c09f0>(
<UILayoutContainerView: 0x16570400; frame = (0 0; 768 1024); transform = [0, 1, -1, 0, 0, 0]; autoresize = W+H;>
)
```

原来系统是处理了window的subview，给它加上了一个transform。所以在iOS7下面给键盘window外其它window加subview的时候，需要在设备旋转的时候处理一下subview的transform属性，保持和系统管理的那个subview一致。

#### iOS8-10的window

先拿个iOS8的iPhone做类似的实验（过滤了一些我们不需要的信息）：

```
<__NSArrayM 0x78977ab0>(
<UIWindow: 0x7889e8e0; frame = (0 0; 568 320)>,
<UITextEffectsWindow: 0x788ae8c0; frame = (0 0; 568 320); autoresize = W+H>,
<UIWindow: 0x788d9fa0; frame = (0 0; 568 320); userInteractionEnabled = NO>
)
```

可以看到横屏的时候，系统为window维护了正确的宽高，即使我并没有给自定义window增加autoresize = W+H的属性。

顺带看一下application window的subview是什么样子的（过滤了一些我们不需要的信息）：

```
<__NSArrayM 0x788aeb90>(
<UILayoutContainerView: 0x7863bdc0; frame = (0 0; 568 320); autoresize = W+H>
)
```

系统管理的view加了autoresize = W+H属性，应该就是利用这个保证了横竖屏旋转时subview的尺寸正确。

在iOS9/10的表现基本一致，总体来说我们要做的就是在设备旋转时保证我们自己添加的subview尺寸正确。

#### 设备旋转事件的系统通知

在iOS中，设备方向相关的定义都是叫做StatusBarOrientation，下面列出一些常用的定义：

```objective-c
// 取得当前的设备方向
[UIApplication sharedApplication].statusBarOrientation
// 设备即将改变方向的通知事件name
UIApplicationWillChangeStatusBarOrientationNotification
// 设备已经改变方向的通知事件name
UIApplicationDidChangeStatusBarOrientationNotification
// 通知事件数据字典里自定义数据的key
UIApplicationStatusBarOrientationUserInfoKey
// 旋转动画时长
[UIApplication sharedApplication].statusBarOrientationAnimationDuration
```

因为iOS7和之后系统表现不一致，所以我们最好是自己监视通知，自己维护加到window的subview的状态。

因为我们期望跟着系统旋转动画的时候一起处理好我们的subview，所以应该监视WillChange通知。

WillChange通知发生的时候，statusBarOrientation会取得旋转前的方向，通知内的数据会是要旋转到的方向。

DidChange通知发生的时候，statusBarOrientation会取得旋转后的方向，通知内的数据会是旋转前的方向。

取得了将要旋转到的方向，对我们的subview做一个和系统旋转动画时长相同的动画就可以。需要注意的是，这个statusBarOrientationAnimationDuration是旋转90度用的时长，旋转180度时要x2（不过其实可以不太在意）。

#### 关于WindowLevel

系统定义了三种WindowLevel，值其实都是CGFloat型的：

```objective-c
// 普通window的level，实际值是0
UIWindowLevel UIWindowLevelNormal;
// Alert弹窗window的level，实际值是2000
UIWindowLevel UIWindowLevelAlert;
// 状态栏window的level，实际值是1000
UIWindowLevel UIWindowLevelStatusBa;
```

这三个我注释的默认值没变过，但是不知道以后会不会变，使用的时候还是应该要使用对应的常量定义。

值得一提的是UIWindowLevelAlert，系统创建的alert window实际的level会有一定的偏差（[参照资料](https://stackoverflow.com/questions/15422898/how-to-show-a-uiwindow-over-the-keyboard-but-under-a-uialertview)，我也遇到过），需要比alert window层级高或者低的时候建议+50或者-50（因为键盘window的level是2100，折中）。

#### 自定义window的其他注意点

userInteractionEnabled需要记得设置成NO，不然上层的window会截获各种触摸事件，App就点不动了。

如果有多处代码需要同时管理userInteractionEnabled属性，最好写一个计数的manager来统一管理。

另外很诡异的一点是，一定要给window设置一个空的rootViewController：

```objective-c
window.rootViewController = [UIViewController new];
```

如果不设置这个rootViewController，系统在某些设备上无法正确的维护window的尺寸和旋转状态。

自定义window是不需要makeKeyAndVisible的，只需要将hidden设为NO就会显示，设为YES就会消失。

#### 诞生的开源库

实验完所有这些东西，诞生了开源库：[TopmostView](https://github.com/HarrisonXi/TopmostView)

如果你不想自己再处理一遍这些问题，可以直接使用这个库。

有些最新的尝试我会放在[develop](https://github.com/HarrisonXi/TopmostView/tree/develop)分支，遇到问题也欢迎带着[issue](https://github.com/HarrisonXi/TopmostView/issues)来。

------

© 2017 苹果梨    [首页](/)    [关于](/about.html)    [GitHub](https://github.com/HarrisonXi)    [Email](mailto:gpra8764@gmail.com)