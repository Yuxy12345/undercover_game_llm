# 在这里配置AI玩家信息，name为对外显示名称，model为使用的LLM模型，local为True代表本地ollama模型，False为OpenAI模型
player_configs = [
    {
        "name": "DeepSeek",
        "model": "deepseek-r1:14b",
        "local": True
    },
    {
        "name": "Llama3.1",
        "model": "llama3.1:8b",
        "local": True
    },
    {
        "name": "Phi4",
        "model": "phi4",
        "local": True
    },
    {
        "name": "Qwen",
        "model": "qwen2.5:14b",
        "local": True
    },
    {
        "name": "Gemma3",
        "model": "gemma3:12b",
        "local": True
    },
    {
        "name": "ChatGPT",
        "model": "gpt-3.5-turbo",
        "local": False
    }
]