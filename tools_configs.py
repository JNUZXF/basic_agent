

# extract_clean_text_from_pdf(pdf_path, method='pdfminer') 提取并清理PDF中的文本
PDF_TEXT_EXTRACT_TOOL = {
    "type": "function",
    "function": {
        "name": "extract_clean_text_from_pdf",
        "description": "提取并清理PDF/论文/报告中的文本",
        "parameters": {
            "type": "object",
            "properties": {
                "pdf_path": {
                    "type": "string",
                    "description": "PDF文件路径",
                },
                "method": {
                    "type": "string",
                    "description": "提取文本的方法",
                },
            },
            "required": ["pdf_path", "method"],
        },
    },
    "example": '''
    用户问题:请帮我提取并清理PDF中的文本
    你的输出:
    ```json
    {{
        "tools": ["extract_clean_text_from_pdf(pdf_path='path/to/pdf', method='pdfminer')"]
    }}
    '''
}

# 必应搜索:bing_searched_result(query, max_pages=2, max_results=10)
BING_SEARCH_TOOL = {
    "type": "function",
    "function": {
        "name": "bing_searched_result",
        "description": "使用必应搜索引擎搜索相关信息",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "搜索关键词，必须用中文或者中英文混合，不能用纯英文，关键词控制在6个字以内，例如:智能体论文、大模型量化、量化投资、AI Agents",
                },
                "max_pages": {
                    "type": "integer",
                    "description": "最大搜索页数",
                },
                "max_results": {
                    "type": "integer",
                    "description": "最大搜索结果数",
                },
            },
            "required": ["query", "max_pages", "max_results"],
        },
    },
    "example": '''
    用户问题:请帮我搜索关于AI的最新资讯
    你的输出:
    ```json
    {{
        "tools": ["bing_searched_result(query='AI最新新闻', max_pages=2, max_results=5)"]
    }}
    '''
}

# 论文搜索get_arxiv_papers(keyword, max_results=5, sort_by='relevance')
ARXIV_SEARCH_TOOL = {
    "type": "function",
    "function": {
        "name": "get_arxiv_papers",
        "description": "搜索arXiv上的论文",
        "parameters": {
            "type": "object",
            "properties": {
                "keyword": {
                    "type": "string",
                    "description": "搜索关键词，必须是英文，例如:AI, Agents, Reinforcement Learning, etc.",
                },
                "max_results": {
                    "type": "integer",
                    "description": "最大搜索结果数",
                },
                "sort_by": {
                    "type": "string",
                    "description": "排序方式",
                },
            },
            "required": ["keyword", "max_results", "sort_by"],
        },
    },
    "example": '''
    用户问题:请帮我搜索关于AI的最新论文
    你的输出:
    ```json
    {{
        "tools": ["get_arxiv_papers(keyword='AI', max_results=5, sort_by='relevance')"]
    }}
    '''
}

# chat(question)
CHAT_TOOL = {
    "type": "function",
    "function": {
        "name": "chat",
        "description": "当不需要使用到任何工具，仅仅是根据你的知识即可回答问题的时候调用这个工具",
        "parameters": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "用户的问题",
                },
            },
            "required": ["question"],
        },
    },

    "example": '''
    用户问题:什么是AI Agent？
    你的输出:chat(question='什么是AI Agent？')
    '''
}


# END_CONVERSATION_TOOL
END_CONVERSATION_TOOL = {
    "type": "function",
    "function": {"name": "END_CONVERSATION()", "description": "当问题已经解决的时候，调用这个工具"},
    "example": '''
    用户问题：至此，问题已经解决，如果还有其他问题，请告诉我
    你的输出：END_CONVERSATION()
    '''
}



