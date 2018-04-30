import sublime, sublime_plugin
import re

def match(rex, str):
    # 返回正则匹配结果
    m = rex.match(str)
    if m:
        return m.group(0)
    else:
        return None


def make_completion(tag):
    # 返回标签的completion内容
    return (tag + '\tTag', tag + '>$0</' + tag + '>')


class GetSettingsPrepare():
    def init(self):

        # 读取自己的设置文件
        settings = sublime.load_settings('WXML_completions.sublime-settings')
        # print('settings:', settings)

        # 标签私有属性的配置对象
        tag_data = settings.get('tag_data')

        # 标签的全局属性
        global_attributes = settings.get('global_attributes')

        # 标签列表
        tag_list = list(tag_data.keys())

        # 自定义标签的completion列表
        custom_completion = settings.get('custom_completion')

        # 按标签首字母，对标签的comple列表进行分组
        self.prefix_completion_tag_dict = {}

        for tag in tag_list:
            prefix = tag[0]
            tag_completion = make_completion(tag)
            custom_list = []

            # 将自定义标签的completion列表合并到tag_dict
            for item in custom_completion:
                tag_name = item[0].split('\t')
                custom_tag = tag_name[0]
                tag_name = tag_name[0].split(':')[0]
                if custom_tag == tag:
                    tag_completion = 'false'
                if tag_name == tag:
                    custom_list.append(item)

            # 如果自定义的completion为原标签，则覆盖
            # 否则还需要将原标签的completion注入到tag_dict
            if tag_completion != 'false':
                self.prefix_completion_tag_dict.setdefault(prefix, []).append(tag_completion)
            self.prefix_completion_tag_dict.setdefault(prefix, []).extend(custom_list)

        # 获取标签对应的属性列表
        self.tag_data = tag_data
        self.global_attributes = global_attributes

        # 打印测试
        # print(self.tag_data)
        # print(self.global_attributes)
        # print(self.prefix_completion_tag_dict.get('b'))
        # print(self.prefix_completion_tag_dict.get('i'))


# Sublime Text 3的资源加载都是异步，在试图访问之前使用 plugin_loaded() 的回调
setting_cache = GetSettingsPrepare()

if int(sublime.version()) < 3000:
  setting_cache.init()
else:
  def plugin_loaded():
    global setting_cache
    setting_cache.init()


class TagCompletions(sublime_plugin.EventListener):
    global setting_cache

    def on_query_completions(self, view, prefix, locations):
        # 该函数当sublime触发自动完成时被执行
        # 在该回调函数中可以返回complete列表，用于sublime的自动完成提示
        #
        # view: 视图对象，提供相关操作函数
        # prefix: 当前输入的匹配字符串，匹配字符串为被换行符\n，制表符\t，空格' '，点号'.'，冒号':'隔断
        # locations: 当前输入的位置，由于可以多行编辑，所以这里是一个数组

        # 仅针对wxml有效
        if not view.match_selector(locations[0], "text.wxml"):
            return []

        # 检测当前作用域是否在标签内
        is_inside_tag = view.match_selector(locations[0],
                "text.wxml meta.tag - text.wxml punctuation.definition.tag.begin")

        # 返回complete列表
        return self.get_completions(view, prefix, locations, is_inside_tag)

    def get_completions(self, view, prefix, locations, is_inside_tag):

        # flags-sublime.INHIBIT_WORD_COMPLETIONS
        # 抑制文档中的单词生成的completion列表
        #
        # flags-sublime.INHIBIT_EXPLICIT_COMPLETIONS
        # 抑制从.sublime-completions中生成的completion列表

        # 获取ch，表示当前匹配字符串的前一个字符是什么
        pt = locations[0] - len(prefix) - 1
        ch = view.substr(sublime.Region(pt, pt + 1))
        completion_list = []

        # 打印测试
        # print('get_completions:', {'prefix':prefix, 'locations':locations, 'is_inside_tag':is_inside_tag, 'ch':ch})

        # 如果不在标签作用域下
        # 优先匹配 tag.class 和 tag#id 模式
        if not is_inside_tag:
            tag_attr_expr = self.expand_tag_attributes(view, locations)
            if tag_attr_expr != []:
                return (tag_attr_expr, sublime.INHIBIT_WORD_COMPLETIONS | sublime.INHIBIT_EXPLICIT_COMPLETIONS)

        # 如果在标签作用域下，且不以<开头
        # 则匹配标签属性
        if is_inside_tag and ch != '<':
            if ch in [' ', '"', '\t', '\n', ':', '.', '@']:
                completion_list = self.get_attribute_completions(view, locations, prefix, ch)
            return (completion_list, sublime.INHIBIT_WORD_COMPLETIONS | sublime.INHIBIT_EXPLICIT_COMPLETIONS)

        # 如果是在字符串中，则匹配为空
        if prefix == '':
            return ([], sublime.INHIBIT_WORD_COMPLETIONS | sublime.INHIBIT_EXPLICIT_COMPLETIONS)

        # 根据匹配字符串的第一个字符列出符合条件的标签列表
        completion_list = setting_cache.prefix_completion_tag_dict.get(prefix[0], [])

        # 如果匹配字符串没有<符号，则完成列表需要加上
        if ch != '<':
            completion_list = [(pair[0], '<' + pair[1]) for pair in completion_list]

        # 如果是在标签作用域下，则需要抑制单词的completion列表以及.sublime-completions列表
        # 如果非标签作用域下，但是成功匹配到了标签的completion列表，也需要抑制
        flags = 0
        if is_inside_tag:
            flags = sublime.INHIBIT_WORD_COMPLETIONS | sublime.INHIBIT_EXPLICIT_COMPLETIONS

        # 返回completion列表
        return (completion_list, flags)

    def expand_tag_attributes(self, view, locations):
        # 支持便捷方式
        # tag.class
        # tag#id

        # lines返回当前输入的所有字符内容
        lines = [view.substr(sublime.Region(view.line(l).a, l)) for l in locations]

        # 反转lines
        lines = [l[::-1] for l in lines]
        # print('lines', lines)

        # 正则匹配输入格式是否满足tag.attr，tag#attr的形式
        rex = re.compile("([\w-]+)([.#])(\w+)")
        expr = match(rex, lines[0])
        # print('expr', expr)

        # 如果不匹配，则completion为空
        if not expr:
            return []

        # 将语法格式的组成部分返回
        val, op, tag = rex.match(expr).groups()
        val = val[::-1]
        tag = tag[::-1]
        expr = expr[::-1]

        # 生成completion语法
        if op == '.':
            snippet = '<{0} class=\"{1}\">$0</{0}>'.format(tag, val)
        else:
            snippet = '<{0} id=\"{1}\">$0</{0}>'.format(tag, val)

        # 返回
        return [(expr, snippet)]

    def get_attribute_completions(self, view, locations, prefix, ch):

        # 以当前字符位置往前截取500个字符用于标签匹配查找
        SEARCH_LIMIT = 500
        pt = locations[0]
        search_start = max(0, pt - SEARCH_LIMIT - len(prefix))
        line = view.substr(sublime.Region(search_start, pt + SEARCH_LIMIT))

        # 表示当前位置之前的字符
        line_head = line[0:pt - search_start]

        # 标签当前位置之后的字符
        line_tail = line[pt - search_start:]

        # 已存在的属性列表
        exist_attr = []

        # 当前键入的属性名称
        attr = ''

        # 找到距离当前输入位置最近的标签名
        i = len(line_head) - 1
        tag = None
        space_index = len(line_head)
        while i >= 0:
            c = line_head[i]
            if c == '<':
                tag = line_head[i + 1:space_index]
                break
            elif c == ' ' or c == '\t' or c == '\n':
                space_index = i
            i -= 1

        # 找到当前tag当前位置之前已经键入的attr列表
        i = len(line_head) - 1
        space_index = len(line_head)
        while i >= 0:
            c = line_head[i]
            if c == ' ' or c == '\t' or c == '\n':
                attr_value = line_head[i + 1:space_index]
                if attr_value != '':
                    exist_attr.append(attr_value)
                space_index = i
            elif c == '<':
                break
            elif c == '=':
                space_index = i
            i -= 1

        # 找到当前tag当前位置之后已经键入的attr列表
        i = 0
        space_index = 0
        while i < len(line_tail):
            c = line_tail[i]
            if c == ' ' or c == '\t' or c == '\n':
                space_index = i
            elif c == '>' or c == '<':
                break
            elif c == '=':
                attr_value = line_tail[space_index+1:i]
                if attr_value != '':
                    exist_attr.append(attr_value)
                space_index = i
            i += 1

        # 这里如果没有成员，取索引0会报错
        if len(exist_attr) > 0:
            attr = exist_attr[0]

        # 打印测试
        # print('tag', tag, '____end')
        # print('exist_attr', exist_attr)
        # print('attr', attr)

        # 检测标签的有效性
        if not tag:
            return []

        # 如果标签没有结束，则自动加上>符号
        suffix = '>'
        for c in line_tail:
            if c == '>':
                # 找到了标签的结束标记
                suffix = ''
                break
            elif c == '<':
                # 发现了另一个打开的标签，则需要将当前标签结束
                break

        # 属性值的completion列表
        if ch == '"':
            attr_list = setting_cache.tag_data.get(tag, {}).get('attrs', {})
            value_list = []
            for item in attr_list:
                if item.get('name', '') == attr:
                    value_list = item.get('enum', [])
            value_completions = [(item.get('value') + '\tValue', item.get('value')) for item in value_list]
            return value_completions

         # 属性名称的completion列表
         # 如果在字符串作用下则不输出
        elif not view.match_selector(locations[0], "text.wxml string.quoted"):
            attr_data = {}
            attr_list = []
            attr_list.extend(setting_cache.tag_data.get(tag, {}).get('attrs', []))

            # 按键值对记录数据
            for item in attr_list:
                attr_data.setdefault(item.get('name', ''), item)

            # 合并公共属性
            for item in setting_cache.global_attributes:
                # 直接是一个字典
                if str(type(item)).find('dict') >= 0:
                    attr_list.append(item)
                    attr_data.setdefault(item.get('name', ''), item)
                # 还可以是字符串
                else:
                    attr_list.append({"name": item, "type": "string", "def": "", "desc": ""})
                    attr_data.setdefault(item, {"name": item, "type": "string", "def": "", "desc": ""})

            attr_name_list = [(item.get('name', '')) for item in attr_list]
            attr_completions = []

            # 如果为冒号，则需要对属性列表进行过滤
            temp_list = []
            temp_obj = {}
            if ch == ':' or ch == '.' or ch == '@':
                for name in attr_name_list:
                    match_result = name.find(attr) == 0
                    if match_result:
                        simple_attr = name.replace(attr, '')
                        temp_obj.setdefault(simple_attr, name)
                        temp_list.append(simple_attr)
                attr_name_list = temp_list

            # 将已存在属性移除
            for name in exist_attr:
                try:
                    # 如果list中不存在值，将报错
                    attr_name_list.remove(name)
                except ValueError:
                    test = ''

            # 生成最终的属性列表
            for name in attr_name_list:
                # 由于可能通过冒号或者点号进行了过滤，
                # 所以需要得出原配置列表的属性名称,
                # 并得出属性的相关数据。
                attr_name = name
                if temp_obj.get(name, False):
                    attr_name = temp_obj.get(name, '')
                attr_item = attr_data.get(attr_name, {})

                #获取属性数据
                type_value = attr_item.get('type', 'string')
                desc_value = attr_item.get('desc', '')
                def_value = attr_item.get('def', '')

                comp_name = name + '\tAttr'
                comp_value = name + '="${1:' + def_value + '}"'

                # 不同属性值类型，输出不一样的补全方案
                if type_value == 'mustache':
                    comp_value = name + '="{{$1}}"'
                elif type_value == 'prop':
                    comp_value = name
                elif type_value == 'boolean':
                    if def_value == 'false':
                        comp_value = name
                    else:
                        comp_value = name + '="{{' + '${1:false}' + '}}"'

                if suffix == '>':
                    comp_value += '$2' + suffix

                attr_completions.append((comp_name, comp_value))

            return attr_completions

    # def matchByFuzzy(self, cont, fuzzy):
    #     # 模糊匹配
    #     reStr = ''
    #     for char in fuzzy:
    #         if char == '.':
    #             reStr += '\.' + '.*'
    #         else:
    #             reStr += char + '.*'

    #     rex = re.compile(reStr)
    #     result = match(rex, cont)

    #     if not result:
    #         return False
    #     else:
    #         return True

