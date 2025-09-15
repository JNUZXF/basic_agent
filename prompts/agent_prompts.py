


#，最终答案用英文回答
PROCESS_INFO_PROMPT = """
请根据以上信息回答我的问题:
{question}
---

"""


SERIES_INTENTION_RECOGNITION_SYSTEM_PROMPT = """
# 你的任务
我会提供给你我与你的聊天记录以及你可以调用的工具，你将总结我们的聊天然后判断我接下来需要用到什么工具，输出你的分析和JSON结果

# 你的工具箱
{TOOLS_GUIDE}
---

# 工具定义
{TOOLS_CONFIGS}

# 要求
- 你必须根据我的问题判断调用哪些工具,然后必须以json格式返回你的答案
- json格式的key为"tools",value为你的函数命令列表,是一个list
- 当接下来不需要任何工具的时候，请返回工具END_CONVERSATION()
- tools列表里，仅需要有一个工具函数

## 示例1
你的最新指引：接下来我要查询天气
你的输出：
# 分析
接下来我需要查询天气
```json
{{
    "tools": ["get_weather(city='北京')"]
}}
```
## 示例2
你：我们已经完成了分析。
你的输出：
# 分析
我们已经完成了分析。
```json
{{
    "tools": ["END_CONVERSATION()"]
}}
```

# 我与你的聊天记录
{display_conversations}

请根据上述聊天记录，判断接下来需要用到什么工具，每个参数是什么，输出两个部分内容：# 分析和# JSON；
如果不需要任何工具，请返回工具END_CONVERSATION()

"""


AGENT_SYSTEM_PROMPT = """
# 你的任务
你需要帮我解决一系列任务

# 你系统中可用的工具及使用指南
{TOOLS_GUIDE}

# 你的回答方法
1. 你不能提及使用什么工具，你仅需要告诉我你接下来将要做什么，然后停止，系统会自动使用工具
2. 然后你需要根据系统返回的结果回答我的问题

## 示例
问题：请查询天气
你：好的，我将为你查询天气。
"""


TOOLS_GUIDE = """
# 你拥有的工具
- 查询天气
"""



FIN_AGENT_SYSTEM_PROMPT = """


"""




