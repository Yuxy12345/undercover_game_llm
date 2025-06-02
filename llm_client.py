from abc import ABC, abstractmethod
import os

from openai import OpenAI
import ollama 
import re
import logging
from logging.handlers import RotatingFileHandler

API_BASE_URL = "YOUR_API_BASE_URL"  # 替换为你的API基础URL
API_KEY = "YOUR_API_KEY"  # 替换为你的API密钥

class LLMClient(ABC):
    @abstractmethod
    def chat(self, messages, model):
        """与LLM交互
        
        Args:
            messages: 消息列表
            model: 使用的LLM模型
        
        Returns:
            tuple: (content, reasoning_content)
        """
        pass

class OpenAIClient(LLMClient):
    def __init__(self, api_key=API_KEY, base_url=API_BASE_URL):
        """初始化OpenAI客户端"""
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        self.logger = logging.getLogger("llm")
        os.makedirs("log", exist_ok=True)
        log_handler = RotatingFileHandler("log/llm.log", maxBytes=50*1024*1024, backupCount=5, encoding="utf-8")
        log_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
        self.logger.handlers = []  # 移除已有的handler，防止重复
        self.logger.addHandler(log_handler)
        self.logger.propagate = False  # 不向上冒泡到root logger
        self.logger.setLevel(logging.INFO)

        
    def chat(self, messages, model):
        """与OpenAI LLM交互
        
        Args:
            messages: 消息列表
            model: 使用的LLM模型
        
        Returns:
            tuple: (content, reasoning_content)
        """
        try:
            self.logger.info(f"LLM请求: {messages}")
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
            )
            if response.choices:
                message = response.choices[0].message
                content = message.content if message.content else ""
                reasoning_content = getattr(message, "reasoning_content", "")
                self.logger.info(f"LLM推理内容: {content}")
                return content, reasoning_content
            self.logger.warning("LLM没有返回有效内容")
            return "", ""
                
        except Exception as e:
            self.logger.error(f"LLM调用出错: {str(e)}")
            return "", ""


class OllamaClient(LLMClient):
    def __init__(self):
        """初始化Ollama客户端"""
        self.logger = logging.getLogger("llm")
        os.makedirs("log", exist_ok=True)
        log_handler = RotatingFileHandler("log/llm.log", maxBytes=50*1024*1024, backupCount=5, encoding="utf-8")
        log_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
        self.logger.handlers = []  # 移除已有的handler，防止重复
        self.logger.addHandler(log_handler)
        self.logger.propagate = False  # 不向上冒泡到root logger
        self.logger.setLevel(logging.INFO)
        
    def chat(self, messages, model="deepseek-r1:14b"):
        """与Ollama交互
        
        Args:
            messages: 消息列表
            model: 使用的LLM模型
        
        Returns:
            tuple: (content, reasoning_content)
        """
        try:
            self.logger.info("-" * 5 + model + "-" * 5)
            self.logger.info(f"Question: \n{messages[0]['content']}")
            self.logger.info("")

            response: ollama.ChatResponse = ollama.chat(model, messages=messages)
            full_content = response['message']['content']
            
            # for deepseek
            # 提取<think></think>中的内容
            reasoning_matches = re.findall(r'<think>(.*?)</think>', full_content, re.DOTALL)
            reasoning_content = "\n".join(reasoning_matches)
            
            # 移除<think></think>内容后的剩余部分
            content = re.sub(r'<think>.*?</think>', '', full_content, flags=re.DOTALL).strip()
            
            if reasoning_content != "":
                self.logger.info(f"Think: \n{reasoning_content}")
            self.logger.info(f"Answer: \n{content}")
            self.logger.info("-" * 5 + model + "-" * 5)
            return content, reasoning_content
        except ollama.ResponseError as e:
            self.logger.error(f"Ollama调用出错: {str(e)}")
            if e.status_code == 404:
                ollama.pull(model)
                
            return "", ""
        

# 使用示例
if __name__ == "__main__":
    llm = OllamaClient()
    messages = [
        {"role": "user", "content": "1+1为什么等于2"}
    ]
    response = llm.chat(messages, "llama3.1:8b")
    print(f"响应: {response}")