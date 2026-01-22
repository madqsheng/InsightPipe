#!/usr/bin/env python3
"""
解析 Gemini raw 数据文件，生成 Markdown 格式的对话记录
修复了 AI 回答路径解析失败的问题
"""
import json
import re
import os

def parse_raw_file(raw_path):
    """解析 raw 文件，返回对话列表"""
    with open(raw_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 找到包含 wrb.fr 的行
    lines = content.split('\n')
    target_line = None
    
    # 取最后一行包含 wrb.fr 的（通常包含最全的历史）
    for line in reversed(lines):
        if 'wrb.fr' in line:
            match = re.search(r'(\[\["wrb\.fr".*)$', line)
            if match:
                target_line = match.group(1)
                break
    
    if not target_line:
        raise ValueError("未找到 wrb.fr 数据行")
    
    try:
        outer_data = json.loads(target_line)
        inner_json_str = outer_data[0][2]
        inner_data = json.loads(inner_json_str)
    except Exception as e:
        raise ValueError(f"JSON 解析失败: {e}")
    
    # 提取标题
    title = "Gemini 对话记录"
    try:
        if len(inner_data[0]) > 2:
            title_node = inner_data[0][2]
            if isinstance(title_node, list) and len(title_node) > 1:
                title = str(title_node[1])
            else:
                title = str(title_node)
    except: pass
    
    conv_list = inner_data[0][1]
    turns = []
    
    for item in conv_list:
        if not isinstance(item, list) or len(item) < 4:
            continue
        
        user_text = None
        model_text = None
        
        # 1. User 文本 - item[2][0][0]
        try:
            user_text = item[2][0][0]
        except: pass
        
        # 2. Model 文本 - 尝试多级深度搜索
        # 路径 A (常见): item[3][0][0][1][0]
        # 路径 B (简化): item[3][0][1][0]
        try:
            candidates_container = item[3]
            if isinstance(candidates_container, list) and len(candidates_container) > 0:
                first_node = candidates_container[0]
                if isinstance(first_node, list) and len(first_node) > 0:
                    # 尝试更深的路径 A: item[3][0][0][1][0]
                    content_node = first_node[0]
                    if isinstance(content_node, list) and len(content_node) > 1 and isinstance(content_node[1], list):
                        model_text = content_node[1][0]
                    # 尝试路径 B: item[3][0][1][0]
                    elif len(first_node) > 1 and isinstance(first_node[1], list):
                        model_text = first_node[1][0]
        except: pass

        if user_text or model_text:
            turns.append({
                'user': user_text,
                'model': model_text
            })
    
    return {
        'title': title,
        'turns': turns
    }

def save_as_markdown(data, output_path):
    """保存为 Markdown"""
    lines = [f"# {data['title']}\n", f"*共 {len(data['turns'])} 轮对话*\n", "---\n\n"]
    
    for turn in data['turns']:
        if turn['user']:
            lines.append(f"**User:** {turn['user']}\n\n")
        
        if turn['model']:
            lines.append(f"**AI:** {turn['model']}\n\n")
        else:
            lines.append(f"**AI:** *[未成功解析回答内容]*\n\n")
        
        lines.append("---\n\n")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)

def main():
    data_dir = 'gemini_data_samples'
    raw_files = [f for f in os.listdir(data_dir) if f.endswith('_raw.txt')]
    
    for raw_file in raw_files:
        raw_path = os.path.join(data_dir, raw_file)
        md_file = raw_file.replace('_raw.txt', '_parsed.md')
        md_path = os.path.join(data_dir, md_file)
        
        try:
            data = parse_raw_file(raw_path)
            save_as_markdown(data, md_path)
            print(f"✅ {raw_file} -> {len(data['turns'])} 轮 (标题: {data['title']})")
        except Exception as e:
            print(f"❌ {raw_file} 失败: {e}")

if __name__ == '__main__':
    main()
