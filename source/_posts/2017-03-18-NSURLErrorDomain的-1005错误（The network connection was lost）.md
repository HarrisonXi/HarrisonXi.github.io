---
title: 苹果梨的博客 - NSURLErrorDomain的-1005错误（The network connection was lost）
category: iOS
tag: iOS, NSURLErrorDomain, -1005, 长连接, HTTP, SDWebImage, YYWebImage
---

# NSURLErrorDomain的-1005错误

#### （NSURLErrorNetworkConnectionLost，The network connection was lost）

| 更新时间       | 更新内容 |
| ---------- | ---- |
| 2017-03-18 | 发布   |

#### 关于HTTP 1.1和HTTP长连接

HTTP 1.0中，默认进行的都是短连接。一个HTTP请求会产生一个TCP连接，请求结束后就会关闭这个TCP连接。而自HTTP 1.1开始，默认进行的都是[长连接](https://zh.wikipedia.org/wiki/HTTP%E6%8C%81%E4%B9%85%E8%BF%9E%E6%8E%A5)。在一个HTTP请求结束之后，客户端和服务端之间的TCP连接并不会立即断开，而是按照约定的Keep-Alive时长维持一定时间的连接状态。这样在下一次HTTP请求发生时，如果TCP连接还存在就会复用之前的TCP连接，省去重新建立TCP连接的时间。

#### iOS的-1005错误

我们的团队是在使用SDWebImage的时候遇到这个问题的，经搜索发现早在iOS 8时代就有人在使用AFNetworking的时候遇到这个问题：[NSURLErrorDomain的-1005错误](http://stackoverflow.com/questions/25372318/error-domain-nsurlerrordomain-code-1005-the-network-connection-was-lost)

```objective-c
Error Domain=NSURLErrorDomain Code=-1005 "The network connection was lost."
```

具体的原因参照[这个回答](http://stackoverflow.com/a/25996971/2562905)的描述：NSURLRequest的实现有问题，在维持长连接的时候维持时长超过了服务器约定的时长，在第二次HTTP请求准备复用TCP连接的时候实际上连接已经被服务器断开了。

我没有去调研&测试NSURLRequest的实现是不是真的有问题，倒是觉得移动设备的一些极端网络情况可能的确会面临这样的问题。

那么接下来就是要解决这个问题。

#### 由服务端解决这个问题

##### 1. 提高服务器Keep-Alive时长至30秒以上

我在简书上也看到有人将Keep-Alive时长设置成了60秒，对应问题可以解决。

但是这个设置对于服务器是有风险的。延长Keep-Alive时长无疑会浪费服务器的性能，毕竟同时需要维持的连接数变多了。很多用户其实也不需要这么长时间的长连接。所以这个方案需要斟酌之后再确定要不要实行。

##### 2. 针对iOS客户端禁用长连接

不同的服务器设置方法不一样，具体方法就不多说了。

这个方案的风险在于，抛弃了长连接会对HTTP请求的速度产生些许影响。

#### 由客户端解决这个问题

##### 1. 重新实现HTTP请求底层，降低客户端Keep-Alive时长

这是个大工程，我们需要写一个完备的底层，使客户端的Keep-Alive时长比服务端传回的时长短一些。这样的话就更低概率甚至不会出现服务端比客户端早断开TCP连接的情况。在出现长连接断开的情况下，底层也应该负责进行一次重试，再开一个新的TCP连接进行HTTP请求。

##### 2. 由业务层或框架层重试HTTP请求

出现错误的时候重试一次HTTP请求就好。在框架或者业务代码里仍然用NSURLRequest实现请求，捕获到-1005错误的时候进行一次重试。虽然说总体用时会更长，但是正确的结果更加重要些。

#### SDWebImage里的问题

在SDWebImage中遇到此问题的现象：有些图片一旦请求失败一次就再也没法刷出来。

归根结底在于SDWebImage维护了一个**failedURLs**列表，请求失败的图片URL都会被加入到这个表中。下次请求的时候如果没有带上SDWebImageRetryFailed选项，SDWebImage就会自动忽略这些URL直接返回错误。

某些特殊的网络错误会被判定是网络连接问题，请求失败时SDWebImage不会将图片URL加入**failedURLs**列表。而这个特殊的网络错误列表里之前没有包含-1005错误，导致出现-1005错误后这些图片就再也不会被重加载。

好在2个月前（2017-1-6）有人提交了对应的修改：[add a network error situation](https://github.com/rs/SDWebImage/commit/57502a9d1d3044a2c2f7969e5241619a697625fb)，我们的SDWebImage是太久没更新了才会遇到这个问题。

#### YYWebImage里的实现

参照[YYWebImageOperation](https://github.com/ibireme/YYWebImage/blob/master/YYWebImage/YYWebImageOperation.m)类的实现。

和SDWebImage实现不同的是：

1. YYWebImage默认是不会记录**URLInBlackList**的，只有带上YYWebImageOptionIgnoreFailedURL选项，请求图片失败时才会把图片URL加入**URLInBlackList**。
2. YYWebImage默认是会重试**URLInBlackList**的，必须带上YYWebImageOptionIgnoreFailedURL选项，才会忽略URLInBlackList中的图片URL。

介于以上原因，实际上按照默认行为使用YYWebImage时如果加载图片失败，下一次加载还是会重试的，所以不会导致图片一直刷不出的严重问题。

当然YYWebImage处理的网络连接问题列表里也没有包含-1005错误，所以我已经提了[pull request](https://github.com/ibireme/YYWebImage/pull/172)。

#### 总结

对于大部分团队来说，应该还是用客户端方案2来处理比较方便。

需要做的就是在客户端请求服务API和图片资源时，出现-1005错误就进行一次重试。

当然如果使用了以上图片库，记得更新下最新版或者手动加上对-1005错误的处理。

------

© 2017 苹果梨　　[首页](/)　　[关于](/about.html)　　[GitHub](https://github.com/HarrisonXi)　　[Email](mailto:gpra8764@gmail.com)
