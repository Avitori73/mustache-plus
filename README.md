# Mustache Plus

通过 Mustache 模板引擎和模板配置文件生成框架代码。

## 要求

python 3.11+

## 安装

```bash
# 克隆当前仓库
git clone https://github.com/Avitori73/mustache-plus.git
# 进入项目目录
cd mustache-plus
# 安装工具
pip install -e .
```

## 使用

创建一个文件夹，将预设模板放入到该文件夹的 `templates` 子文件夹中。

在文件夹中开启一个终端，执行 `msh` 命令。

`msh` 会自动检测到 `templates` 文件夹中的模板，并提供一个交互式命令行界面，允许你选择模板并生成代码。

按照提示输入参数，`msh` 会根据模板配置文件和输入的参数生成代码。

生成结果会放在当前目录下的 `output` 文件夹中。

## 预设模板配置

在 `templates` 文件夹中，创建一个目录，目录名称即为模板名称。在该目录根目录中放置模板配置文件，文件名为 `template_meta.yaml`。该文件包含模板的元数据和配置选项。

模板配置文件的类型为 YAML，包含以下配置项：

```yaml
parameters:
  - name: group # [参数名称: str|必填]
    ask: true # [是否询问用户输入: bool|默认false]
    choices: # [可选项目: list[str]|默认None]
      - group1
      - group2
      - group3
    description: 首目录 # [参数描述: str|必填]
  - name: sub_group
    ask: true
    required: false # [是否必填: bool|默认true]
    description: 子目录
  - name: FIDXXXXXX
    ask: true
    description: 6位 FunctionID
    innerConvertor: # [内部转换器（当 ask 为 true 的时候固定使用用户输入的值）: dict|可选]
      - name: change_case # [内部转换器名称: str|必填]
        params: # [内部转换器参数: dict|可选]
          caseType: upper
  - name: path
    description: group 和 sub_group 的组合路径
    convertor: | # [转换器（自定义 convertor python 脚本，类型必须为 Callable[Dict[str,str], str], params 包含前面填入的 parameter）: callable|可选]
      def convertor(params) -> str:
          group = params.get('group', '')
          sub_group = params.get('sub_group', '')
          return f"{group}/{sub_group}" if sub_group else group
  - name: FIDXXXX
    target: FIDXXXXXX # [转换目标（innerConvertor 使用， ask 为 true 的时候固定使用当前目标，ask 为 false 的使用必须输入一个前面出现过的 parameter）: str|可选]
    innerConvertor: 
      - name: substr
        params:
          end: -2
    description: 4位 FunctionID
```

## 内部转换器

内部实现了一些常用的转换器，避免用户重复编写转换器代码。以下是转换器的列表：

- `change_case`
  - 描述：改变字符串的类型
  - 参数：
    - `caseType` 可选值为
      - `camel`：驼峰式命名法（如 `fooBarBaz`）
      - `capital`：首字母大写（如 `FooBarBaz`）
      - `const`：常量式（如 `FOO_BAR_BAZ`）
      - `lower`：小写（如 `foobarbaz`）
      - `pascal`：帕斯卡命名法（如 `FooBarBaz`）
      - `path`：路径式（如 `foo/bar/baz`）
      - `sentence`：句子式（如 `Foo bar baz`）
      - `snake`：蛇形命名法（如 `foo_bar_baz`）
      - `spinal`：脊椎式（如 `foo-bar-baz`）
      - `title`：标题式（如 `Foo Bar Baz`）
      - `trim`：去除首尾空格（如 `foo bar baz`）
      - `upper`：大写（如 `FOOBARBAZ`）
      - `alphanum`：只保留字母和数字（如 `fooBarBaz123`）
- `substr`
  - 描述：截取字符串的一部分，python 的 `str[start:end]` 语法
  - 参数：
    - `start`：起始位置
    - `end`：结束位置
