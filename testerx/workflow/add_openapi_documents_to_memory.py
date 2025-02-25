from testerx.utils.parsing_openapi_json import OpenAPIParser
from testerx.data_access.json_data_access import JsonDataAccess
from testerx.utils.dataframe_exporter import DataFrameToStringConverter
import pandas as pd
import config
import os


def add_openapi_documents_to_memory(spec_path: str):  # 移除 memory_data_dir 参数
    """
    解析 OpenAPI 规范文件并将 API 文档信息添加到 JsonDataAccess 内存中。

    Args:
        spec_path: OpenAPI 规范文件路径
    """
    parser = OpenAPIParser(spec_path=spec_path)
    api_details_iterator = parser.iter_api_details_by_path()
    converter = DataFrameToStringConverter()
    project_name = parser.get_info()["title"]
    # 构建新的 memory_data_dir 路径
    memory_data_dir = os.path.join(config.PROJECT_PATH, project_name, "api_doc_memory_data")
    data_access_api_doc = JsonDataAccess(memory_data_dir)  # 使用新的路径

    for item in api_details_iterator:
        content_string = converter.convert_to_string(item)

        # 提取 API 文档的关键信息, 确保处理 DataFrame 并转换为字符串
        api_path = str(item.iloc[0]['path']) if 'path' in item.columns and pd.notna(
            item.iloc[0]['path']
        ) else None  # 使用 item.iloc[0]['path']
        method = str(item.iloc[0]['method']) if 'method' in item.columns and pd.notna(
            item.iloc[0]['method']
        ) else None  # 使用 item.iloc[0]['method']
        summary = str(item.iloc[0]['summary']) if 'summary' in item.columns and pd.notna(
            item.iloc[0]['summary']
        ) else None  # 使用 item.iloc[0]['summary']
        description = str(item.iloc[0]['description']) if 'description' in item.columns and pd.notna(
            item.iloc[0]['description']
        ) else None  # 使用 item.iloc[0]['description']

        # 创建 metadata 作为标准 Python 字典, 确保值为字符串
        metadata = {
            'api_title': str(item.iloc[0]['api_title']) if 'api_title' in item.columns and pd.notna(
                item.iloc[0]['api_title']
            ) else None,  # 使用 item.iloc[0]['api_title']
            'api_version': str(item.iloc[0]['api_version']) if 'api_version' in item.columns and pd.notna(
                item.iloc[0]['api_version']
            ) else None,  # 使用 item.iloc[0]['api_version']
            'api_description': str(item.iloc[0]['api_description']) if 'api_description' in item.columns and pd.notna(
                item.iloc[0]['api_description']
            ) else None,  # 使用 item.iloc[0]['api_description']
            'base_url': str(item.iloc[0]['base_url']) if 'base_url' in item.columns and pd.notna(
                item.iloc[0]['base_url']
            ) else None,  # 使用 item.iloc[0]['base_url']
            'full_url': str(item.iloc[0]['full_url']) if 'full_url' in item.columns and pd.notna(
                item.iloc[0]['full_url']
            ) else None,  # 使用 item.iloc[0]['full_url']
            'operationId': str(item.iloc[0]['operationId']) if 'operationId' in item.columns and pd.notna(
                item.iloc[0]['operationId']
            ) else None,  # 使用 item.iloc[0]['operationId']
            # ... 其他 metadata 字段也需要类似处理
        }
        metadata = {k: v for k, v in metadata.items() if v is not None}

        # 添加 API 文档记忆
        try:
            memory = data_access_api_doc.add_api_doc_memory(
                content=content_string,
                api_path=api_path,
                method=method,
                summary=summary,
                description=description,
                metadata=metadata,
                tags=["openapi", "api_doc"]
            )
            print(f"已添加API文档记忆: {api_path} - {method}, Memory ID: {memory['id']}")
        except TypeError as e:
            print(f"添加API文档记忆出错: {api_path} - {method}")
            print(f"错误信息: {e}")
            import traceback
            traceback.print_exc()

    return True


if __name__ == '__main__':
    openapi_spec_path = 'res/2.json'

    add_openapi_documents_to_memory(openapi_spec_path)
