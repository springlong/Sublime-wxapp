English | [简体中文](./docs/README.zh-ch.md)


# Sublime-wxapp

Sublime Text 3 syntax highlighting and auto completion for `.wxml` file(WeChat 'mini apps').

## Install

- Package Control

Search `Sublime wxapp` via Package Control: Install Package

- Git

Git clone this repository to Sublime Packages Path.

- Zip

Download zip and unzip to Sublime Packages Path.

## Setting

In order to improve WXML completion efficiency,you shuld edit your Preferences.sublime-settings and add config below:

```js
"auto_complete_triggers":
[
  {
    "characters": "abcdefghijklmnopqrstuvwxyz< :.",
    "selector": "text.wxml"
  }
],
```

![](assets/images/sublime-setting.png)

## Feature

### `.wxml` file syntax highlighting

![](assets/images/wxml-syntax-highlight.png)

### `.wxss` file syntax highlighting

![](assets/images/wxss-syntax-highlight.png)

### WeChat 'mini apps' components auto completion

1： Support `view:if`、`view:for`、`view:class`.

![](assets/images/wxml-complete-1.gif)

2: Support `view.class` and `view#id`.

![](assets/images/wxml-complete-2.gif)

3: Will complement different content depending on the type of attribute values.

![](assets/images/wxml-complete-3.gif)

4: Support colon (:) matching.

![](assets/images/wxml-complete-4.gif)


### WeChat 'mini apps' apis auto completion

![](assets/images/wxapp-api.gif)
