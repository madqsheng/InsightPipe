#!/usr/bin/env python3
"""
解析 Gemini raw 数据文件，生成 Markdown 格式的对话记录
"""
import json
import re
import os
import sys

def parse_raw_file(raw_path):
    """解析 raw 文件，返回对话列表"""
    with open(raw_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 找到包含 wrb.fr 的行
    lines = content.split('\n')
    target_line = None
    
    for line in lines:
        if 'wrb.fr' in line:
            # 提取 JSON 部分
            match = re.search(r'(\[\["wrb\.fr".*)$', line)
            if match:
                target_line = match.group(1)
                break
    
    if not target_line:
        raise ValueError("未找到 wrb.fr 数据行")
    
    # 解析外层 JSON
    try:
        outer_data = json.loads(target_line)
    except json.JSONDecodeError as e:
        raise ValueError(f"外层 JSON 解析失败: {e}")
    
    # 提取内层 JSON 字符串
    inner_json_str = outer_data[0][2]
    inner_data = json.loads(inner_json_str)
    
    # 提取标题和对话列表
    title = "Gemini 对话记录"
    if len(inner_data[0]) > 2:
        title_raw = inner_data[0][2]
        # 标题可能是 list，取第二个元素
        if isinstance(title_raw, list) and len(title_raw) > 1:
            title = str(title_raw[1])
        else:
            title = str(title_raw)
    
    conv_list = inner_data[0][1]
    
    # 解析每轮对话
    turns = []
    for item in conv_list:
        if not isinstance(item, list) or len(item) < 4:
            continue
        
        user_text = None
        model_text = None
        
        # 提取 User 文本 - 路径: item[2][0][0]
        try:
            user_text = item[2][0][0]
        except (IndexError, TypeError):
            pass
        
        # 提取 Model 文本 - 路径: item[3][0][1][0]
        try:
            # item[3] 是 candidates list
            candidates = item[3]
            if len(candidates) > 0 and isinstance(candidates[0], list):
                # candidates[0] 是 ['rc_id', [response_text, ...]]
                if len(candidates[0]) > 1 and isinstance(candidates[0][1], list):
                    model_text = candidates[0][1][0]
        except (IndexError, TypeError):
            pass
        
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
    """将对话数据保存为 Markdown 文件"""
    lines = []
    
    # 标题
    lines.append(f"# {data['title']}\n")
    lines.append(f"*共 {len(data['turns'])} 轮对话*\n")
    lines.append("---\n\n")
    
    # 对话内容
    for i, turn in enumerate(data['turns'], 1):
        if turn['user']:
            lines.append(f"**User:** {turn['user']}\n\n")
        
        if turn['model']:
            lines.append(f"**AI:** {turn['model']}\n\n")
        
        lines.append("---\n\n")
    
    # 写入文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f"✅ 已保存: {output_path}")

def main():
    # 处理所有 _raw.txt 文件
    data_dir = 'gemini_data_samples'
    
    if not os.path.exists(data_dir):
        print(f"❌ 目录不存在: {data_dir}")
        return
    
    raw_files = [f for f in os.listdir(data_dir) if f.endswith('_raw.txt')]
    
    if not raw_files:
        print(f"❌ 没有找到 _raw.txt 文件")
        return
    
    print(f"找到 {len(raw_files)} 个 raw 文件\n")
    
    for raw_file in raw_files:
        raw_path = os.path.join(data_dir, raw_file)
        md_file = raw_file.replace('_raw.txt', '_parsed.md')
        md_path = os.path.join(data_dir, md_file)
        
        try:
            print(f"🔄 解析: {raw_file}")
            data = parse_raw_file(raw_path)
            save_as_markdown(data, md_path)
            print(f"   标题: {data['title']}")
            print(f"   轮数: {len(data['turns'])}\n")
        except Exception as e:
            print(f"❌ 失败: {raw_file}")
            print(f"   错误: {e}\n")

if __name__ == '__main__':
    main()
