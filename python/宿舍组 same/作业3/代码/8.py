# -*- coding: utf-8 -*-
"""
智慧农博士 - 基于命令行的农业聊天助手
功能：
1. 用户可选择不同农业类别的助手（如种植、养殖、病虫害、气象、土壤等）
2. 使用 Qwen3 API 通过 HTTP 请求获取回答
3. 回答结果逐字显示，增强交互体验
4. 支持循环切换助手类型并持续提问
"""

import requests
import time
import sys

# ==================== 配置区 ====================
# 请在此处填写你的阿里云 DashScope API Key
API_KEY = "sk-9a99fd4363564f589d7809c8bfbe215f"  # 替换为你的实际 API Key
MODEL_NAME = "qwen3-max"  # 使用的模型名称，例如 qwen3

# 农业助手类别定义
AGRICULTURE_CATEGORIES = {
    "1": "大田作物种植（如水稻、小麦、玉米）",
    "2": "经济作物种植（如棉花、油菜、甘蔗）",
    "3": "果蔬种植（如番茄、苹果、草莓）",
    "4": "畜牧养殖（如猪、牛、鸡）",
    "5": "水产养殖（如鱼、虾、蟹）",
    "6": "病虫害防治",
    "7": "土壤与肥料管理",
    "8": "农业气象与灾害应对",
    "9": "农业机械与智能农业",
    "0": "通用农业知识"
}

# ==================== 函数定义区 ====================

def get_qwen3_response(prompt: str) -> str:
    """
    调用 Qwen3 API 获取模型回答
    :param prompt: 用户输入的问题（已包含角色设定）
    :return: 模型生成的回答文本
    """
    url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": MODEL_NAME,
        "input": {
            "messages": [
                {"role": "user", "content": prompt}
            ]
        },
        "parameters": {
            "result_format": "message"
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()  # 检查 HTTP 错误
        
        # 解析 JSON 响应
        result = response.json()
        
        # 提取回答内容
        # 注意：Qwen API 的响应结构可能因版本略有不同，此处按 DashScope 文档处理
        if "output" in result and "choices" in result["output"]:
            message = result["output"]["choices"][0]["message"]["content"]
            return message.strip()
        else:
            return "抱歉，模型返回格式异常，无法解析回答。"
            
    except requests.exceptions.RequestException as e:
        return f"网络请求出错：{e}"
    except KeyError as e:
        return f"响应解析错误，缺少字段：{e}"
    except Exception as e:
        return f"未知错误：{e}"


def print_char_by_char(text: str, delay: float = 0.03):
    """
    逐字打印文本，模拟打字效果
    :param text: 要打印的文本
    :param delay: 每个字符之间的延迟（秒）
    """
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()  # 打印完换行


def display_category_menu():
    """显示农业助手类别菜单"""
    print("\n" + "="*50)
    print("🌱 欢迎使用【智慧农博士】农业聊天助手 🌾")
    print("="*50)
    print("请选择您要咨询的农业类别：")
    for key, desc in AGRICULTURE_CATEGORIES.items():
        print(f"  [{key}] {desc}")
    print("  [q] 退出程序")
    print("-"*50)


def get_user_category_choice() -> str:
    """获取用户选择的类别"""
    while True:
        choice = input("请输入类别编号（如 1、2...0 或 q）：").strip()
        if choice.lower() == 'q':
            return 'q'
        if choice in AGRICULTURE_CATEGORIES:
            return choice
        else:
            print("❌ 无效输入，请输入 0-9 或 q。")


def get_user_question(category_desc: str) -> str:
    """获取用户的具体问题"""
    print(f"\n✅ 已选择：{category_desc}")
    print("请输入您的农业问题（输入 'back' 返回类别选择）：")
    question = input("问题：").strip()
    return question


# ==================== 主程序逻辑 ====================

def main():
    # 检查 API Key 是否配置
    if API_KEY == "your_api_key_here":
        print("⚠️  请先在代码中配置您的 DashScope API Key！")
        return

    while True:
        # 显示菜单并获取用户选择
        display_category_menu()
        category_choice = get_user_category_choice()
        
        if category_choice == 'q':
            print("\n👋 感谢使用智慧农博士，祝您丰收！")
            break
        
        category_desc = AGRICULTURE_CATEGORIES[category_choice]
        
        while True:
            question = get_user_question(category_desc)
            
            if question.lower() == 'back':
                break  # 返回类别选择
            
            if not question:
                print("⚠️  问题不能为空，请重新输入。")
                continue
            
            # 构造带角色设定的提示词
            system_prompt = (
                f"你是一位专业的农业专家，专注于【{category_desc}】领域。"
                "请用中文、简洁、准确、实用的方式回答以下农民提出的问题。"
                "避免使用专业术语过多，尽量通俗易懂。"
                "你是一位精通古代农业和诗词的AI,请在回答专业问题的同时,恰当地引用相关的古代诗词来增加文采。"
            )
            full_prompt = f"{system_prompt}\n\n用户问题：{question}"
            
            print("\n🧠 农博士正在思考中，请稍候...")
            answer = get_qwen3_response(full_prompt)
            
            print("\n💬 智慧农博士的回答：")
            print_char_by_char(answer)
            
            print("\n" + "-"*50)
            print("您可以继续提问，或输入 'back' 返回选择其他农业类别。")

if __name__ == "__main__":
    main()
