# Copyright (c) 2025 YycKop
# MIT License
# ai/llm/base.py
import openai
import os
from django.conf import settings
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class BaseLLMClient(ABC):
    @abstractmethod
    def chat_completion(self, prompt, **kwargs):
        pass

    @abstractmethod
    def generate_insights(self, data, analysis_type):
        pass


class LLMClient(BaseLLMClient):
    def __init__(self):
        self.api_key = getattr(settings, 'OPENAI_API_KEY', os.getenv('OPENAI_API_KEY'))
        self.base_url = getattr(settings, 'OPENAI_BASE_URL', 'https://api.openai.com/v1')

        # 初始化客户端
        if self.api_key:
            openai.api_key = self.api_key
            if self.base_url:
                openai.base_url = self.base_url

    def chat_completion(self, prompt, model="gpt-3.5-turbo", temperature=0.7, max_tokens=1000):
        """调用LLM进行对话补全"""
        try:
            if not self.api_key:
                return "LLM服务未配置，请设置OPENAI_API_KEY环境变量"

            response = openai.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system",
                     "content": "你是一个农产品市场分析专家，擅长分析农产品价格趋势、产量预测和市场动态。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"LLM调用失败: {str(e)}")
            return f"分析服务暂时不可用: {str(e)}"

    def generate_insights(self, data, analysis_type):
        """生成数据洞察"""
        prompts = {
            'price_trend': f"""
            分析以下农产品价格数据，提供关键洞察：
            {data}

            请重点关注：
            1. 价格趋势和季节性模式
            2. 异常波动和可能原因
            3. 不同产品间的价格关联
            4. 预测未来价格走势
            """,
            'yield_analysis': f"""
            分析以下农产品产量数据：
            {data}

            请提供：
            1. 产量变化趋势
            2. 影响产量的关键因素
            3. 产量预测和建议
            4. 优化建议
            """,
            'market_analysis': f"""
            分析以下农产品市场数据：
            {data}

            请提供：
            1. 市场供需状况
            2. 竞争格局分析
            3. 市场机会识别
            4. 战略建议
            """
        }

        prompt = prompts.get(analysis_type, prompts['price_trend'])
        return self.chat_completion(prompt)