---
title: 苹果梨的博客 - iOS从MRC（手动引用计数）过渡到ARC（自动引用计数）
category: iOS
tag: iOS, ObjC, MRC, ARC, 内存, 引用计数, 手动, 自动
---

# iOS从MRC过渡到ARC

### 手动引用计数过渡到自动引用计数

| 更新时间       | 更新内容        |
| ---------- | ----------- |
| 2013-05-22 | 发布          |
| 2017-04-05 | 修订内容，新增部分内容 |

Apple Developer原文：[Transitioning to ARC Release Notes](https://developer.apple.com/library/content/releasenotes/ObjectiveC/RN-TransitioningToARC/Introduction/Introduction.html)

#### ARC简介

ARC是一个支持自动管理ObjC对象内存的**编译器功能**。这里要划个重点，注意ARC是编译期就完成的，不是在运行时进行处理的。它所做的事情就是在编译时自动在正确的位置插入`retian`和`release`等代码。

有了ARC之后就不用自己手写`retain`、`relase`和`autorelease`了。如果没有什么**非ObjC对象实例**的资源需要手动销毁，`dealloc`也不需要我们自己处理了。

（注：非ObjC对象实例的资源类似于C#里的非托管资源，诸如用`malloc`直接分配的内存区域，就是ObjC不知道怎么去销毁的那些资源。）

自动完成？那会不会导致性能问题？事实证明完全不需要担心，上文也提到这是编译器功能，和程序员手动管理引用计数相比性能相当，错误率更低而且不会对运行时产生较大负担。

从iOS4开始就支持ARC了，不过要注意的是从iOS5开始才支持弱引用。

用官方的例子来说一下，现在实现一个Person类，只需要这些代码：

```objective-c
@interface Person : NSObject
@property NSString *firstName;
@property NSString *lastName;
@property NSNumber *yearOfBirth;
@property Person *spouse;
@end

@implementation Person
@end
```

（注意这些属性默认都会是`strong`类型的，关于`strong`类型会在后面说到。）

然后，你可以像下面这样实现一个方法，而不用去关心内存管理问题：

```objective-c
- (void)contrived {
    Person *aPerson = [[Person alloc] init];
    [aPerson setFirstName:@"William"];
    [aPerson setLastName:@"Dudney"];
    [aPerson setYearOfBirth:[[NSNumber alloc] initWithInteger:2011]];
    NSLog(@"aPerson: %@", aPerson);
}
```

ARC会搞定内存管理，Person实例和NSNumber实例都不会产生泄漏。

你也可以像下面这样实现一个方法，不用担心变量被过早的释放：

```objective-c
- (void)takeLastNameFrom:(Person *)person {
    NSString *oldLastname = [self lastName];
    [self setLastName:[person lastName]];
    NSLog(@"Lastname changed from %@ to %@", oldLastname, [self lastName]);
}
```

总体来说代码变得更加简洁，程序员可以更加关注代码逻辑和结构等，以后大家全部使用ARC是一个必然趋势。

#### ARC的强制规则

- 不可以显示的调用`dealloc`方法，不可以调用或实现`retian`、`release`、`autorelease`或`retianCount`方法。使用`@selector(retain)`之类的方法去进行调用也是不可以的。

  对于某些非ObjC对象实例的资源你还是需要在`dealloc`里手动处理的，一些非ARC实现的老的系统对象实例我们也得注意需要手动调用一下`[systemClassInstance setDelegate:nil]`。在ARC的`dealloc`方法里不需要也无法调用`[super dealloc]`方法（会编译错误）。

  在一些Core Foundation风格的类里面，仍然可以手动调用`CFRetain`、 `CFRelease`之类的方法。

- 不可以使用`NSAllocateObject`或`NSDeallocateObject`。直接使用`alloc`创建对象就好，系统运行时会处理好销毁工作。

- 在C结构体里无法使用ObjC对象指针。相比较使用C结构体，你其实可以创建一个ObjC类来替代完成对应的功能。

- `id`和`void *`将无法相互转换。

- `NSAutoreleasePool`将无法再使用，但可以使用更灵活的`@autoreleasepool` block来替代。

- Memory zones将无法再使用，它没有再被使用的必要了。

- 存取器（accessor）的名字不能以`new`开头。

#### ARC引入的新的生命周期修饰词

最主要的改变莫过于新增了弱引用，弱引用对象在没有人再对其进行强引用之后会自动变成`nil`。

ARC没办法解决强引用导致的循环引用问题，所以新增了弱引用让大家使用弱引用来打破循环引用。

##### 属性特性（Property Attributes）

新的属性特性`strong`和`weak`，其中`strong`是ARC里默认的属性特性。

```objective-c
// 相当于MRC里面的 @property(retain) MyClass *myObject;
@property(strong) MyClass *myObject;
 
// 类似于MRC里面的 @property(assign) MyClass *myObject;
// 不同的是，一旦myObject的内存被释放，指针值将被置成nil，不会成为野指针。
@property(weak) MyClass *myObject;
```

##### 变量修饰词（Variable Qualifiers）

- `__strong`是默认值。只要有任意一个强引用指向对象，这个对象将一直『存活』于内存里。
- `__weak`指定了一个弱引用，并不会阻止对象被销毁。当一个对象没有被强引用的话，这个对象就会被销毁，并且弱引用指针会被自动置`nil`。
- `__unsafe_unretained`兼容iOS4会用到的修饰词，并不会阻止对象被销毁。和弱引用不同的是，对象被销毁后引用指针不会被自动置`nil`，而是会变成野指针，所以这是『unsafe』的。
- `__autoreleasing`用来指示通过引用（`id *`）传递的参数，将会在return的时候被自动释放。通常我们不需要手动使用这个修饰词。

具体的使用例子如下：

```objective-c
MyClass * __weak myWeakReference;
MyClass * __unsafe_unretained myUnsafeReference;
```

需要注意弱引用不能乱用，看下面的例子：

```objective-c
NSString * __weak string = [[NSString alloc] initWithFormat:@"First Name: %@", [self firstName]];
NSLog(@"string: %@", string);
```

这里的`string`虽然在下一句代码里用到了，但是它并没有被任何地方强引用，所以其实它是会被立即释放掉的，下一句的日志也只能打出`nil`了。

#### 使用新的修饰词来避免循环引用问题

父子关系等等可能导致的循环引用问题很好处理，这是大家都了解的。通常来说父->子使用强引用，子->父使用弱引用就可以了。但是其它一些情况就复杂点，比如说block中的循环引用问题。

在MRC模式下，`__block id x`是不会对`x`进行引用计数加一操作的。在ARC模式下，`__block id x`是会对`x`产生一个强引用的。基于这个差别，如果在ARC模式下想要用`__block`修饰词还不想触发循环引用问题，某些时候需要用`__weak __block id x`来处理。或者另一种方案就是在block内部的末尾，手动写一句`x = nil;`来打破循环引用（确保block和对应变量都是一次性使用的）。

对于堆block（可以查阅NSMallocBlock）中引用到的`strong`和`retain`类型的对象实例，在MRC和ARC里都是一致会产生强引用的，如果存在循环引用一定要处理下。具体的处理方法教程多如牛毛，在这里就不多赘述了。

额外要一提的是，在block内使用弱引用指针也是存在风险的，一定要做好空判断；如果操作具有连续性，还要注意把弱引用先强引用化一次，然后在block内使用对应的强引用指针。

而且并不是所有的block都会产生循环引用，不要产生过分的恐惧。例如UIView的动画block还有GCD的dispatch操作block，会在有限时间内执行完，而且这些block也并没有被我们强引用，所以不会触发引用循环。

#### 新的Autorelease Pool管理方式

```objective-c
@autoreleasepool {
     // 需要用到Autorelease Pool特性的代码，例如在一个循环中反复创建大量临时对象。
}
```

#### 堆变量会自动初始化成nil

ARC模式下的各种堆变量，无论强弱引用，初始化的时候都会是nil的了。

#### 用编译标志来开启或禁用ARC

在MRC工程里对单独文件添加`-fobjc-arc`编译标志来启用ARC模式，在ARC工程里对单独文件添加`-fno-objc-arc`编译标志来禁用ARC模式。编译标志的添加方法是在工程属性界面TARGETS->Build Phases->Compile Sources里选中指定的文件后双击，就会看到编译标志的编辑框了，编辑完之后回车就好。

------

© 2017 苹果梨　　[首页](/)　　[关于](/about.html)　　[GitHub](https://github.com/HarrisonXi)　　[Email](mailto:gpra8764@gmail.com)
