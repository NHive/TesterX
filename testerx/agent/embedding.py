from openai import OpenAI
from config import API_INFO, EMBEDDING_MODEL
from testerx.agent.logger import ModelLogger
from typing import List


class OpenAIClient:
    """封装 OpenAI API 调用"""

    def __init__(self, provider, model):
        self.client = OpenAI(
            base_url=API_INFO[provider]["BASE_URL"],
            api_key=API_INFO[provider]["KEY"]
        )
        self.model = model

    def create_chat_completion(self, messages, tools=None, temperature=0, stream=False, max_tokens=None):
        params = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "stream": stream
        }
        if tools:
            params["tools"] = tools
        if max_tokens:
            params["max_tokens"] = max_tokens
        return self.client.chat.completions.create(**params)

    def create_embedding(self, input_text, encoding_format="float"):
        params = {
            "model": self.model,
            "input": input_text,
            "encoding_format": encoding_format  # 可以根据需要选择 "float" 或 "base64"
        }
        return self.client.embeddings.create(**params)


class EmbeddingModel:
    def __init__(self):
        self.provider = EMBEDDING_MODEL["provider"]
        self.model = EMBEDDING_MODEL["model"]
        self.logger = ModelLogger(log_file="res/embedding_operations.log")
        self.openai_client = OpenAIClient(self.provider, self.model)

    def get_embedding(self, input_text: str) -> List[float]:
        """
        获取文本的 embedding 向量

        Args:
            input_text: 输入文本

        Returns:
            文本的 embedding 向量 (List[float])
        """
        self._log_request(input_text)
        response = self.openai_client.create_embedding(input_text)
        embedding_vector = self._log_response(response)
        return embedding_vector

    def _log_request(self, input_text):
        """记录 embedding 请求日志"""
        self.logger.log(
            "embedding_request", {
                "model": self.model,
                "input_text": input_text,
            }
        )

    def _log_response(self, response):
        """记录 embedding 响应日志, 并提取 embedding 向量"""
        response_dict = {
            "object": response.object,
            "data": [
                {
                    "index": data.index,
                    "embedding": data.embedding
                } for data in response.data
            ],
            "model": response.model,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "total_tokens": response.usage.total_tokens
            }
        }
        self.logger.log("embedding_response", {"response": response_dict})
        return response_dict["data"][0]["embedding"]


if __name__ == '__main__':
    embedding_model = EmbeddingModel()
    text_to_embed = "这是一段用于测试 EmbeddingModel 的文本。"
    embedding = embedding_model.get_embedding(text_to_embed)
    print(f"文本: {text_to_embed}")
    print(f"Embedding 向量 (部分展示): {embedding[:10]}...")
    print(f"Embedding 向量长度: {len(embedding)}")
