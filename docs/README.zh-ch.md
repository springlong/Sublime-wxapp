# Sublime-wxapp

Sublime Text 3 微信小程序语法高亮、代码提示插件！

微信开发者工具的编辑器虽然自带代码提示功能，但是就其编码体验和主题选择，个人觉得还是不太好用。

而VS Code虽然有完善的小程序插件，而且挺好用，功能齐全，但是个人还是更偏向于简洁的Sublime Text。

所以还是想在自己熟悉的Sublime Text3上进行代码的编写工作，于是带着学习的目的，诞生了这款Sublime Text的微信小程序语法高亮、代码提示插件。

## 安装

- Package Control

通过 Package Control: Install Package 搜索 `Sublime wxapp` 进行安装。

- Git

用git克隆到Sublime的插件安装目录。

- Zip

下载zip包，将其解压到Sublime的插件安装目录。

Windows的安装目录，可以从Sublime的菜单中依次选择：Preferences > Browse Packages 到达。

Mac的安装目录，可以从Sublime的菜单中依次选择：Sublime Text > Preferences > Browse Packages 到达。

## 设置

为了提高wxml的补全效率，需要选择菜单(Preferences > Settings)，在打开的Preferences.sublime-settings用户配置文件中加入下面的代码：

```js
"auto_complete_triggers":
[
  {
    "characters": "abcdefghijklmnopqrstuvwxyz< :.",
    "selector": "text.wxml"
  }
],
```

![](../assets/images/sublime-setting.png)

## 插件功能1：wxml文件的语法高亮

除了基本的标签语法高亮外，还有以下两个特点：

1： 自动识别wxs标签，内部使用JavaScript语法高亮和代码提示。

2： Mustache语法等表示JS操作的属性值均高亮显示，用于区分其他常规属性值和文本内容。

![](../assets/images/wxml-syntax-highlight.png)

## 插件功能2：wxss文件的语法高亮

目前是将其设置为css语法，rpx单位和内部组件标签无法高亮显示。

小程序的css不建议直接使用组件的标签选择器进行样式书写，建议统一采用class书写。

而rpx单位没有高亮显示，恰巧可以体现该单位的特殊性，因而不打算再单独编写针对wxss的语法文件。

这样也方便共用css原有的代码提示和补全。

![](../assets/images/wxss-syntax-highlight.png)

## 插件功能3：微信内置组件的代码提示和自动补全

基本的标签补全和属性提示都已实现，具体功能点如下：

1： 标签的自动补全，并为常用标签添加辅助输入：`view:if`、`view:for`、`view:class` 等。

![](../assets/images/wxml-complete-1.gif)

2: 通过 `view.class` 和 `view#id` 快速输入类名和id属性。

![](../assets/images/wxml-complete-2.gif)

3: 标签属性以及属性值的自动提示和补全，将根据属性值的类型补全不一样的内容。

![](../assets/images/wxml-complete-3.gif)

4: 标签属性支持冒号(:)匹配。

![](../assets/images/wxml-complete-4.gif)

## 插件功能4：微信API的代码提示和自动补全

微信API的提示，统一通过 `wx` 前缀触发，输入期间不支持 `.` 匹配。

![](../assets/images/wxapp-api.gif)

## 后续

1. wxml标签暂不支持自动闭合。
2. wxml标签和属性以及属性值的描述文本，受限于Sublime本身的Completion UI，暂时没有比较好的显示方式。
3. 微信API的代码提示和自动补全还不是很全，但基本够用。
4. 暂时没有提供 JSON 配置的提示功能。
5. 暂时缺少文档快速查询便捷功能。
6. 有任何需求和疑问，欢迎提交[issues](https://github.com/springlong/Sublime-wxapp/issues)
