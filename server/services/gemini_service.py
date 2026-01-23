import requests
import json
import re
from typing import Optional

# Gemini分享链接的RPC端点
BASE_URL = "https://gemini.google.com/_/BardChatUi/data/batchexecute"

# 最小化的查询参数（已验证有效）
QUERY_PARAMS_TEMPLATE = {
    "rpcids": "ujx1Bf",
    "hl": "zh-CN",
    "rt": "c"
}

# 黄金Headers（来自用户提供的有效session）
HEADERS = {
    "content-type": "application/x-www-form-urlencoded;charset=UTF-8",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
    "cookie": "_gcl_au=1.1.1678809549.1769051420; NID=528=XZyVJ9pubNj3FwezA4SUDWyr3CJLvv829fBf4Y_vsT30EKqIwlcX-yHsPI8Wzml-HwQfpMmoY5cS3EfMukb3pxoI_Ff2r7S_DP6owRZ_LkP7Y0AsCA2RGizxQ3tcCav7L63nmmiyq44LSZx-pvNmopVxXa4b0tUNIcr6KsaJqgFIbOOiCFDcBodklSEe8Zwl20x4KkciT_oWI78; _ga_WC57KJ50ZZ=GS2.1.s1769051419$o1$g0$t1769051419$j60$l0$h0; _ga=GA1.1.946165692.1769051420; COMPASS=gemini-pd=CjwACWuJV93jFYb_b6k1ZbZc5AVi75OXfwVJx6huPFdJgLZgT-iphNSBtyIyTho-2Gurv4U86El7hPmdVFUQnM3LywYaTQAJa4lXIkN3sOK5jSzDLo2KoxQKl9Bgki7C7N4fLHso4yScK57z7OtHDPXawsZ63IvG9HHHWfhbYkNI8LQLixZ0PclguOc_5RUrTwfQIAEwAQ; _ga_BF8Q35BMLM=GS2.1.s1769051420$o1$g0$t1769051420$j60$l0$h0"
}

class GeminiService:
    @staticmethod
    def extract_id(url: str) -> Optional[str]:
        """从Gemini分享链接中提取share ID"""
        match = re.search(r'share/([a-zA-Z0-9]+)', url)
        return match.group(1) if match else None

    @staticmethod
    def fetch_conversation(share_url: str) -> dict:
        """
        从Gemini分享链接获取对话内容
        返回: {'title': str, 'content': str, 'turns': list}
        """
        share_id = GeminiService.extract_id(share_url)
        if not share_id:
            raise ValueError("Invalid Gemini Share URL")

        # 构建请求参数（完全按照batch_validate.py的方式）
        params = QUERY_PARAMS_TEMPLATE.copy()
        params["source-path"] = f"/share/{share_id}"
        
        # Payload Construction - 完全按照验证通过的方式
        inner_req = f'[null,"{share_id}",[4]]'
        payload = {
            "f.req": f'[[["ujx1Bf","{inner_req.replace(chr(34), chr(92)+chr(34))}",null,"generic"]]]',
            "at": ""
        }
        
        try:
            resp = requests.post(BASE_URL, params=params, data=payload, headers=HEADERS, timeout=20)
            if resp.status_code != 200:
                raise Exception(f"Google API returned HTTP {resp.status_code}")
                
            return GeminiService._parse_response(resp.text)
            
        except Exception as e:
            raise Exception(f"Failed to fetch conversation: {str(e)}")

    @staticmethod
    def _parse_response(raw_text: str) -> dict:
        """解析Gemini RPC响应，提取对话内容（完全按照parse_raw_to_md.py的逻辑）"""
        lines = raw_text.split('\n')
        target_line = None
        
        # 找到包含 wrb.fr 的行（取最后一行）
        for line in reversed(lines):
            if 'wrb.fr' in line:
                match = re.search(r'(\[\["wrb\.fr".*)$', line)
                if match:
                    target_line = match.group(1)
                    break
        
        if not target_line:
            raise ValueError("Could not find data payload in response")
        
        try:
            # 解析外层JSON
            outer_data = json.loads(target_line)
            inner_json_str = outer_data[0][2]
            inner_data = json.loads(inner_json_str)
            
            # 提取标题
            title = "Gemini对话记录"
            try:
                if len(inner_data[0]) > 2:
                    title_node = inner_data[0][2]
                    if isinstance(title_node, list) and len(title_node) > 1:
                        title = str(title_node[1])
                    else:
                        title = str(title_node)
            except:
                pass
            
            # 提取对话列表
            conv_list = inner_data[0][1]
            turns = []
            markdown_lines = []
            
            for item in conv_list:
                if not isinstance(item, list) or len(item) < 4:
                    continue
                
                user_text = None
                model_text = None
                
                # 提取User内容: item[2][0][0]
                try:
                    user_text = item[2][0][0]
                except:
                    pass
                
                # 提取Model内容 - 尝试多种路径
                try:
                    candidates = item[3]
                    if isinstance(candidates, list) and len(candidates) > 0:
                        first_node = candidates[0]
                        if isinstance(first_node, list) and len(first_node) > 0:
                            # 尝试路径 A: item[3][0][0][1][0]
                            content_node = first_node[0]
                            if isinstance(content_node, list) and len(content_node) > 1 and isinstance(content_node[1], list):
                                model_text = content_node[1][0]
                            # 尝试路径 B: item[3][0][1][0]
                            elif len(first_node) > 1 and isinstance(first_node[1], list):
                                model_text = first_node[1][0]
                except:
                    pass
                
                if user_text or model_text:
                    turns.append({
                        'user': user_text,
                        'model': model_text
                    })
                    
                    if user_text:
                        markdown_lines.append(f"## 🙋‍♂️ User\n\n{user_text}\n")
                    if model_text:
                        markdown_lines.append(f"## 🤖 AI\n\n{model_text}\n")
                    
                    markdown_lines.append("---\n")
            
            return {
                "title": title,
                "content": "\n".join(markdown_lines),
                "turns": turns
            }
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to decode JSON response: {str(e)}")
        except Exception as e:
            raise ValueError(f"Parsing error: {str(e)}")
