
"""
智能体
"""


import json
import time
import warnings
from pathlib import Path

from tools.llm_manager import LLMManager
from tools.json_tool import *
from tools.function_call_toolbox import extract_params_to_json, get_func_name

warnings.filterwarnings("ignore")

# 获取提示词
from prompts.agent_prompts import (
    SERIES_INTENTION_RECOGNITION_SYSTEM_PROMPT,
    PROCESS_INFO_PROMPT,
    AGENT_SYSTEM_PROMPT,
    TOOLS_GUIDE
)

# 加载工具配置
from tools_configs import (
    CHAT_TOOL,
)



# 财务报告分析撰写Agent
class fin_agent:
    def execute(self, **kwargs):
        conversations = kwargs.get("conversations", "")

        prompt = """

"""




class Agent():

    def __init__(self, main_model, tool_model, flash_model, conversationID="666"):
        self.conversationID = conversationID
        self.main_model = main_model
        self.tool_model = tool_model
        self.flash_model = flash_model
        self.llm = LLMManager(self.main_model)
        self.agents = {
            "fin_agent": fin_agent()
        }
        self.tools = {                 
        }
        self.tools_prompt_config = [ 
            CHAT_TOOL
        ]
        # 创建Files/conversationID文件夹
        Path(f"files/{self.conversationID}").mkdir(parents=True, exist_ok=True)
        print(f"创建文件夹：files/{self.conversationID}")
        agent_system_prompt = AGENT_SYSTEM_PROMPT.format(
            TOOLS_GUIDE=TOOLS_GUIDE
        )
        self.conversations = [{"role": "system", "content": agent_system_prompt}]
        self.tool_conversations = [{"role": "system", "content": "You must follow my instructions."}]

        self.display_conversations = ""

    # 保存聊天记录为json文件
    def save_conversation(self, conversation):
        with open("data/conversation.json", "w", encoding="utf-8") as f:
            json.dump(conversation, f, ensure_ascii=False)
    
    # 重置聊天记录
    def reset_conversation(self):
        self.conversations = [{"role": "system", "content": "You must follow my instructions."}]
        self.tool_conversations = [{"role": "system", "content": "You must follow my instructions."}]
        self.display_conversations = ""
        
    # 判断意图
    def get_conversation_intention_tools(self):
        self.tool_conversations = [{"role": "system", "content": "你必须根据我的要求输出JSON"}]
        tool_judge_prompt = SERIES_INTENTION_RECOGNITION_SYSTEM_PROMPT.format(
            TOOLS_GUIDE=TOOLS_GUIDE
            , TOOLS_CONFIGS=self.tools_prompt_config
            , display_conversations=self.display_conversations
        )
        # 更改系统提示
        self.tool_conversations.append({"role": "user", "content": tool_judge_prompt})
        ans = ""
        llm = LLMManager(self.tool_model)
        for char in llm.generate_char_stream(tool_judge_prompt):
            ans += char if char else ""
            print(char, end="", flush=True)
        self.tool_conversations.append({"role": "assistant", "content": ans})
        print()
        intention_tools = get_json(ans)["tools"] # type: ignore
        with open(f"files/{self.conversationID}/tool_conversations.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(self.tool_conversations, ensure_ascii=False, indent=2))
        # 保存display_conversations到txt
        with open(f"files/{self.conversationID}/display_conversations.txt", "w", encoding="utf-8") as f:
            f.write(self.display_conversations)
        return intention_tools

    
    def work_flow(self, question):
        self.conversations.append({"role": "user", "content": question})
        self.display_conversations += f"我：{question}\n------\n\n"
        ans = ""
        for char in self.llm.generate_char_conversation(self.conversations):
            yield char
            ans += char if char else ""
        yield "\n"
        self.conversations.append({"role": "assistant", "content": ans})
        self.display_conversations += f"你：{ans}\n------\n\n"

        intention_tool = self.get_conversation_intention_tools()[0]
        while intention_tool != "END_CONVERSATION()":
            func_name = get_func_name(intention_tool)
            print(f"func_name: {func_name}")
            tool_kwargs = json.loads(extract_params_to_json(intention_tool))
            print()
            print(tool_kwargs)
            print()
            tool_kwargs["func_name"] = func_name
            tool_kwargs["question"] = question
            tool_kwargs["model"] = self.main_model
            tool_kwargs["conversationID"] = self.conversationID
            if func_name in list(self.agents.keys()):
                ans = ""
                for char in self.agents[func_name].execute(**tool_kwargs): 
                    yield char
                    ans += char if char else "" 
                yield "\n"
                self.conversations.append({"role": "assistant", "content": ans})
                self.display_conversations += f"你：{ans}\n"
            else:
                info = self.tools[func_name].execute(**tool_kwargs) # type: ignore
                yield "__thinking...__\n\n"
                llm_info = f""""以下是TCM-Agent系统的分析结果：\n{info}\n"""
                self.display_conversations += f"工具执行结果：{llm_info}\n------\n\n"
                self.conversations.append({"role": "assistant", "content": llm_info})

                process_info_prompt = PROCESS_INFO_PROMPT.format(question=question)  
                self.display_conversations += f"我：{process_info_prompt}\n------\n\n"

                self.conversations.append({"role": "user", "content": process_info_prompt})
                ans = ""
                for char in self.llm.generate_char_conversation(self.conversations):
                    yield char
                    ans += char if char else "" 
                yield "\n"
                                
                self.conversations.append({"role": "assistant", "content": ans})
                self.display_conversations += f"你：{ans}\n------\n\n"
                intention_tool = self.get_conversation_intention_tools()[0]
                if intention_tool == "END_CONVERSATION()":
                    break

            self.save_conversation(self.conversations)


if __name__ == "__main__":

    model_1, model_2, model_3, model_4 = "doubao-pro", "deepseek", "glm-4-plus", "qwen-plus"
    model = model_1
    start_time = time.time()
    agent = Agent(
        conversationID="test",
        main_model=model,
        tool_model=model,
        flash_model=model
    )

    question = "你好，你能做什么"

    for char in agent.work_flow(question):
        if char:
            print(char, end="", flush=True)

    end_time = time.time()
    print(f"\n程序执行时间: {end_time - start_time:.4f} 秒")

