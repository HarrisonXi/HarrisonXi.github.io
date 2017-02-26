---
title: 苹果梨的博客 - 给nginx从Let's Encrypt申请个SSL证书
category: web
tag: web, HTTPS, SSL, 证书, nginx, CentOS
---

# 给nginx从Let's Encrypt申请个SSL证书

### 给自己的站点启用HTTPS，基于CentOS 6和nginx 1.10.3示例

| 更新时间       | 更新内容 |
| ---------- | ---- |
| 2017-02-26 | 发布   |

网站HTTPS化是迟早的事情了，一是国外各大厂都在推行HTTPS化（例如苹果），一是国内HTTP被劫持篡改的现象越来越严重了。

现在SSL证书也有免费的了，所以我们可以考虑给自己的站点申请一个免费的证书，让它也支持起HTTPS来。

国外两大提供免费SSL证书的机构就是[Let's Encrypt](https://letsencrypt.org/)和StartSSL了（别问我为什么不说国内的），然后StartSSL也是因为和国内的某厂产生了关系变得不可信任了，所以今天我能选择的就只有这么一家了。

#### 从Let's Encrypt申请证书

文中之后就简称Let's Encrypt为LE了。

LE只提供了DV（Domain Validation，域名验证）类型的SSL证书，只要你持有域名，就可以在验证通过后得到对应域名可用的SSL证书。具体的验证方法，就是在你域名的网站下建立一个**/.well-known/acme-challenge**文件，LE会去访问这个文件确认你的确持有这个域名。这里有个问题就是**.well-known**是用点开头的，在Linux中是隐藏文件，需要配置好你的nginx保证从外网可以访问到这个路径先。

整个过程还是比较繁琐的，所以LE推荐我们使用工具[Certbot](https://certbot.eff.org/)来搞定这件事。我的VPS是CentOS 6的，所以在Certbot首页选择好CentOS 6和nginx之后，打开了具体的[安装介绍页](https://certbot.eff.org/#centos6-nginx)。

```
wget https://dl.eff.org/certbot-auto
chmod a+x certbot-auto
```

在想要安装Certbot的路径下执行上述指令，就可以得到可执行文件centbot-auto了。这个文件神通广大，可以自动安装各种需要的依赖。装好了它之后，Certbot推荐我们使用[webroot插件](https://certbot.eff.org/docs/using.html#webroot)来获得证书。

```
$ ./certbot-auto certonly --webroot -w /var/www/example -d example.com -d www.example.com -w /var/www/thing -d thing.is -d m.thing.is
```

这是一个示例的指令。其中**/var/www/example**是第一个虚拟主机在VPS上的根路径，后面的**example.com**和**www.example.com**就是对应的已绑定的域名，也就是-d参数对应的域名会向前取最近一个-w参数对应的根路径。这样Certbot就会在**/var/www/example**路径下创建**/.well-known/acme-challenge**文件，然后通知LE去验证，最后获得签名好的SSL证书存在本地，最后删除刚刚创建的验证用文件并输出结果。

我安装的nginx默认虚拟主机根路径在/usr/share/nginx下，我改了个名，所以指令是这样的：

```
./certbot-auto certonly --webroot -w /usr/share/nginx/harrisonxi.com -d harrisonxi.com
```

确认后certbot-auto会调用yum安装各种依赖，都确认进行安装就好。

接下来会需要输入你的email地址，同意LE的协议，确认是否把email地址分享给EFF。

三步完成后没有什么问题应该就可以看到Congratulations的提示了，然后信息里也会提到你的证书存在哪里。

#### 配置nginx

nginx的配置文件一般是在/etc/nginx路径下，打开这个路径下的nginx.conf，可以看到实际上它是从其他文件import了server配置：

```
http {
  ...
  include /etc/nginx/conf.d/*.conf;
}
```

在这种情况下，就要再去/etc/nginx/conf.d路径下找到对应的*.conf文件来编辑server配置。如果server配置是直接写在nginx.conf里的，那就直接在nginx.conf里编辑server配置：

```
server {
    listen       80;
    listen       443  ssl;
    server_name  harrisonxi.com;
    ssl_certificate      /etc/letsencrypt/live/harrisonxi.com/fullchain.pem;
    ssl_certificate_key  /etc/letsencrypt/live/harrisonxi.com/privkey.pem;
    ssl_protocols        TLSv1 TLSv1.1 TLSv1.2;
    ssl_ciphers          HIGH:!aNULL:!MD5;
    ...
}
```

我的server配置示例就是这样了，记得改成你的证书对应地址。在这样配置的情况下，用HTTP和HTTPS都可以访问到网站。

用nginx -t验证一下配置文件没有问题，用nginx -s reload重启nginx，生效后就可以测试访问效果了。

#### 证书续期

LE提供的证书只有90天有效期，这点也是我觉得比较靠谱的一点，毕竟域名是个可能经常转手的东西。

Certbot工具也可以自动续期SSL证书，使用renew方法即可：

```
./certbot-auto renew
```

renew方法的详细介绍参考对应的[用户指导](https://certbot.eff.org/docs/using.html#renewal)。可以新建一个定期计划任务每隔几天自动运行指令：

```
./certbot-auto renew --quiet
```

------

© 2017 苹果梨    [首页](/)    [关于](/about.html)    [GitHub](https://github.com/HarrisonXi)    [Email](mailto:gpra8764@gmail.com)
