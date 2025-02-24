# 请修改为你自己的api配置,并将该文件重命名为config.py

# LLM接入配置,目前使用的第三方转发的openai接口
# 腾讯的DeepSeek接口暂时不支持函数调用,所以没用上
API_INFO = {
    "OHMYGPT": {
        "KEY": "sk-*",
        "BASE_URL": "https://c-z0-api-01.hash070.com/v1"
    },
    "TXYUN": {
        "KEY": "sk-*",
        "BASE_URL": "https://api.lkeap.cloud.tencent.com/v1"
    }
}

# format暂支持[OPENAI]
# format指定该模型的请求格式,是使用openai的风格还是Anthropic的风格
# provider指定使用的API
# model 为使用的模型名称
EMBEDDING_MODEL = {"format": "openai", "provider": "OHMYGPT", "model": "text-embedding-3-small", }
CHAT_MODEL = {"format": "openai", "provider": "OHMYGPT", "model": "gpt-4o"}

# 长记忆长度

# 短记忆长度
