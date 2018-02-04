---
title: iOS系统的键盘window
subtitle: 从iOS7到iOS10的变更历史
categories: iOS
tags: [window, 键盘, keyboard, iOS, 开源]
---

具体某些细节内容和我的开源库[TopmostView](https://github.com/HarrisonXi/TopmostView)相关。

发现这个键盘window需要调研一下的原因，就是在这个开源库调试过程中，发现新建的自定义window连状态栏都能盖住的情况下，居然盖不住键盘。

让我们从iOS7开始慢慢调研起。

<!--more-->

# iOS7/8的键盘window

先写一些日志来方便观察一个App的window结构：

```objc
for (UIWindow *win in [UIApplication sharedApplication].windows) {
    NSLog(@"window class: %@, window level: %.0f", NSStringFromClass([win class]), win.windowLevel);
    for (UIView *subview in win.subviews) {
        NSLog(@"    subview class: %@", NSStringFromClass([subview class]));
    }
}
```

在iOS7里运行可能得到以下两种结果：

```objc
window class: UIWindow, window level: 0
window class: UITextEffectsWindow, window level: 1
    subview class: UIPeripheralHostView
    subview class: TopmostView
```

```objc
window class: UIWindow, window level: 0
window class: UITextEffectsWindow, window level: 1
    subview class: UIPeripheralHostView
window class: UITextEffectsWindow, window level: 2100
    subview class: TopmostView
```

这里window level为0的window就是我们的application window了。通常情况下出现的键盘window的class为UITextEffectsWindow，window level为1，会盖住我们的app界面。在长按文本框出现弹出菜单之后会出现一个window level为2100的UITextEffectsWindow，应该是为了确保可以盖住状态栏和应用内Alert弹窗。

在这种情况下想要盖住键盘其实比较简单，再创建一个level大于2100的自定义window就可以了。

iOS8的层次和iOS7基本一致，仅仅是subview的class有变化：

```objc
window class: UIWindow, window level: 0
window class: UITextEffectsWindow, window level: 1
    subview class: UIInputSetContainerView
window class: UITextEffectsWindow, window level: 2100
    subview class: TopmostView
```

再深入的话，iOS7和iOS8的键盘window有个区别：iOS7的键盘window是frame始终恒定，通过transform来变换旋转方向。细节可以参考我的后一篇博客，在此不深入讨论。

# iOS9/10的键盘window

iOS9的window层次如下：

```objc
window class: UIWindow, window level: 0
window class: UITextEffectsWindow, window level: 1
    subview class: UIInputSetContainerView
window class: UITextEffectsWindow, window level: 2100
    subview class: UICalloutBar
    subview class: UIApplicationRotationFollowingControllerView
window class: UIRemoteKeyboardWindow, window level: 10000000
    subview class: UIInputSetContainerView
    subview class: TopmostView
```

iOS10仅有一个区别就是UICalloutBar不见了，这个暂时不是关注的重点。

重点在于多了一个level为1000万的window……导致了我建一个level两千多的window没办法盖住键盘window了。

建立一个level比1000万还大的window我个人就不太建议了（能不能创建成功是另一码事），所以iOS9之后想要做一些盖住键盘的提示之类，还是建议在这个UIRemoteKeyboardWindow上增加subview来做了。

比较有趣的事情是，我的开源库是在UITextEffectsWindow上addSubview的，结果实际上这个TopmostView被增加到了UIRemoteKeyboardWindow上。应该是UITextEffectsWindow做了一些代理或者转发的工作，所以按照iOS7/8的逻辑直接在顶层的UITextEffectsWindow上addSubview也可以。

# 总结

App有盖住键盘的提示之类需求，建议的统一方案是从高层往低层逆序遍历所有的window，找到第一个UITextEffectsWindow，在上面新增一个subview然后在这个subview上做剩余的操作。找到这个window的具体代码示例如下：

```objc
for (UIWindow *window in [[UIApplication sharedApplication].windows reverseObjectEnumerator]) {
    if ([window isKindOfClass:NSClassFromString(@"UITextEffectsWindow")] && window.hidden == NO && window.alpha > 0) {
        return window;
    }
}
return nil;
```

当然还有一些旋转和尺寸问题等着你处理。

如果你不想自己处理这些，那么请移步至开源库：[TopmostView](https://github.com/HarrisonXi/TopmostView)
