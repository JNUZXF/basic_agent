
"""
解析文本为JSON，返回工具参数，示例：
{
"gene_names": ["TP53", "BRCA1", "EGFR", "MYC", "AKT1"],
"database": ["DisGeNET", "KEGG"],
"disease_names": ["Fibrosis"]
}
"""

import re
import json
import ast
from typing import List, Dict, Any, Optional, Tuple


def get_func_name(text):
    """
    提取文本中的函数名称
    """
    pattern = r'([a-zA-Z_]\w*)\('
    function_name = re.search(pattern, text)
    return function_name.group(1) if function_name else None


def extract_code_blocks(text: str) -> List[str]:
    """
    提取 ```...``` 代码块内部文本；若没有代码块，返回 [text]
    """
    pattern = re.compile(r"```(?:[a-zA-Z0-9_+-]*)\s*(.*?)```", re.DOTALL)
    blocks = pattern.findall(text)
    if blocks:
        return blocks
    return [text]

def find_function_call_spans(text: str) -> List[Tuple[str, int, int]]:
    """
    在文本中找到形如 name(...平衡括号...) 的函数调用。
    返回列表: [(函数名, 起始索引, 结束索引(含右括号))...]
    """
    results = []
    # 找所有可能的 name(
    for m in re.finditer(r'([a-zA-Z_]\w*)\s*\(', text):
        fname = m.group(1)
        start = m.start(1)
        # 从 '(' 开始做括号匹配
        paren_start = text.find('(', m.end(1)-0)
        if paren_start == -1:
            continue
        depth = 0
        i = paren_start
        in_string = False
        string_quote = ''
        escape = False
        while i < len(text):
            ch = text[i]
            if in_string:
                if escape:
                    escape = False
                elif ch == '\\':
                    escape = True
                elif ch == string_quote:
                    in_string = False
            else:
                if ch in ('"', "'"):
                    in_string = True
                    string_quote = ch
                elif ch == '(':
                    depth += 1
                elif ch == ')':
                    depth -= 1
                    if depth == 0:
                        # 完成匹配
                        end = i
                        results.append((fname, start, end+1))
                        break
            i += 1
    return results

def extract_first_function_call(text: str) -> Optional[str]:
    """
    提取第一个函数调用的完整文本，如 gene_enrichment(a=1, b=[2])
    """
    for block in extract_code_blocks(text):
        spans = find_function_call_spans(block)
        if spans:
            fname, s, e = spans[0]
            return block[s:e]
    return None

def split_top_level_params(param_str: str) -> List[str]:
    """
    将参数字符串按顶层逗号分割，忽略括号 / 中括号 / 花括号 / 字符串内部的逗号。
    允许末尾多余逗号。
    返回每个形如 key=... 的片段（不做 strip 在后续会 strip）。
    """
    parts = []
    i = 0
    n = len(param_str)
    start = 0
    stack = []  # 用于括号匹配
    in_string = False
    string_quote = ''
    escape = False
    while i < n:
        ch = param_str[i]
        if in_string:
            if escape:
                escape = False
            elif ch == '\\':
                escape = True
            elif ch == string_quote:
                in_string = False
        else:
            if ch in ('"', "'"):
                in_string = True
                string_quote = ch
            elif ch in '([{':
                stack.append(ch)
            elif ch in ')]}':
                if stack:
                    stack.pop()
            elif ch == ',' and not stack:
                # 顶层逗号
                segment = param_str[start:i].strip()
                if segment:
                    parts.append(segment)
                start = i + 1
        i += 1
    # 最后一个
    last_seg = param_str[start:].strip()
    if last_seg:
        # 去掉可能的尾随逗号
        if last_seg.endswith(','):
            last_seg = last_seg[:-1].strip()
        if last_seg:
            parts.append(last_seg)
    return parts

def parse_params(param_str: str) -> Dict[str, Any]:
    """
    将类似 "a=1, b=['X','Y'], c='zzz'" 解析为 dict
    """
    params = {}
    for seg in split_top_level_params(param_str):
        if '=' not in seg:
            # 可能是不带值的裸参数（位置参数），此处可按需要处理；先忽略
            continue
        key, value_str = seg.split('=', 1)
        key = key.strip()
        value_str = value_str.strip()
        # 去掉末尾多余逗号
        if value_str.endswith(','):
            value_str = value_str[:-1].strip()
        # 尝试安全解析
        try:
            value = ast.literal_eval(value_str)
        except Exception:
            # 回退：如果是裸标识符(如 True/False/None 失败情况极少)，再做一次特殊处理
            low = value_str.lower()
            if low == 'true':
                value = True
            elif low == 'false':
                value = False
            elif low == 'none' or low == 'null':
                value = None
            else:
                # 去掉首尾引号（如果是简单包裹）
                if (value_str.startswith("'") and value_str.endswith("'")) or \
                   (value_str.startswith('"') and value_str.endswith('"')):
                    value = value_str[1:-1]
                else:
                    value = value_str
        params[key] = value
    return params

def extract_params_to_json_from_text(text: str, first_only: bool = True) -> str:
    """
    从任意文本中找到函数调用并解析参数，返回 JSON（默认只解析第一个）。
    若 first_only=False，返回 {函数名: {参数...}, ...}
    """
    collected = {}
    for block in extract_code_blocks(text):
        spans = find_function_call_spans(block)
        for fname, s, e in spans:
            call_text = block[s:e]
            # 拿出括号里的内容
            open_paren = call_text.find('(')
            inner = call_text[open_paren+1:-1]  # 去掉最后一个 ')'
            params = parse_params(inner)
            collected[fname] = params
            if first_only:
                return json.dumps(params, ensure_ascii=False, indent=4)
    # 没找到
    return json.dumps({} if first_only else collected, ensure_ascii=False, indent=4)

# 兼容你原函数名
def extract_params_to_json(function_call_or_text: str) -> str:
    return extract_params_to_json_from_text(function_call_or_text, first_only=True)

if __name__ == "__main__":
    test_case = """# JSON
```json
{
    "tools": ["gene_enrichment(gene_names=['TP53', 'BRCA1', 'EGFR', 'MYC', 'AKT1'], database=['DisGeNET', 'KEGG'], disease_names=['Fibrosis'])"]
}
```"""
    print(extract_params_to_json(test_case))
