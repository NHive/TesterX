from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import json
from collections import OrderedDict
import csv
import pandas as pd
import os


@dataclass
class OpenAPIComponent:
    """表示 OpenAPI 组件的基类"""
    description: Optional[str] = None


@dataclass
class Parameter:
    """表示 API 参数"""
    name: str
    in_: str  # path, query, header, cookie
    schema: Dict[str, Any]
    description: Optional[str] = None
    required: bool = False


@dataclass
class RequestBody:
    """表示请求体"""
    content: Dict[str, Dict[str, Any]]
    description: Optional[str] = None
    required: bool = False


@dataclass
class Response:
    """表示 API 响应"""
    content: Dict[str, Dict[str, Any]]
    description: Optional[str] = None


@dataclass
class Operation:
    """表示 API 操作"""
    responses: Dict[str, Response]
    description: Optional[str] = None
    parameters: Optional[List[Parameter]] = None
    requestBody: Optional[RequestBody] = None
    operationId: Optional[str] = None
    summary: Optional[str] = None
    tags: Optional[List[str]] = None


class OpenAPIParser:
    """OpenAPI 3.1 规范解析器"""

    def __init__(self, spec_path: str = None, spec_dict: dict = None):
        """
        初始化解析器

        Args:
            spec_path: OpenAPI 规范文件路径
            spec_dict: OpenAPI 规范字典
        """
        if spec_path:
            with open(spec_path, 'r', encoding='utf-8') as f:
                self.spec = json.load(f)
        elif spec_dict:
            self.spec = spec_dict
        else:
            raise ValueError("必须提供 spec_path 或 spec_dict 之一")

        self.validate_version()

    def validate_version(self):
        """验证 OpenAPI 版本"""
        openapi_version = self.spec.get('openapi', '')
        if not openapi_version.startswith('3.1'):
            raise ValueError(f"不支持的 OpenAPI 版本: {openapi_version}, 需要 3.1.x")

    def parse_parameter(self, param_dict: Dict) -> Parameter:
        """解析参数定义"""
        return Parameter(
            name=param_dict['name'],
            in_=param_dict['in'],
            schema=param_dict.get('schema', {}),
            description=param_dict.get('description'),
            required=param_dict.get('required', False)
        )

    def parse_request_body(self, body_dict: Dict) -> RequestBody:
        """解析请求体定义"""
        return RequestBody(
            content=body_dict['content'],
            description=body_dict.get('description'),
            required=body_dict.get('required', False)
        )

    def parse_response(self, response_dict: Dict) -> Response:
        """解析响应定义"""
        return Response(
            content=response_dict.get('content', {}),
            description=response_dict.get('description')
        )

    def parse_operation(self, operation_dict: Dict) -> Operation:
        """解析操作定义"""
        responses = {
            code: self.parse_response(resp)
            for code, resp in operation_dict['responses'].items()
        }

        parameters = None
        if 'parameters' in operation_dict:
            parameters = [
                self.parse_parameter(param)
                for param in operation_dict['parameters']
            ]

        request_body = None
        if 'requestBody' in operation_dict:
            request_body = self.parse_request_body(operation_dict['requestBody'])

        return Operation(
            responses=responses,
            description=operation_dict.get('description'),
            parameters=parameters,
            requestBody=request_body,
            operationId=operation_dict.get('operationId'),
            summary=operation_dict.get('summary'),
            tags=operation_dict.get('tags')
        )

    def get_paths(self) -> Dict[str, Dict[str, Operation]]:
        """获取所有路径及其操作，按路径和方法排序"""
        paths = OrderedDict()
        for path in sorted(self.spec.get('paths', {}).keys()):
            path_item = self.spec['paths'][path]
            operations = OrderedDict()
            for method in sorted(['get', 'post', 'put', 'delete', 'patch']):
                if method in path_item:
                    operations[method] = self.parse_operation(path_item[method])
            paths[path] = operations
        return paths

    def get_components(self) -> Dict[str, Any]:
        """获取组件定义"""
        return self.spec.get('components', {})

    def get_servers(self) -> Dict[str, Any]:
        return self.spec.get('servers', {})

    def get_info(self) -> Dict[str, Any]:
        """获取 API 信息"""
        return self.spec.get('info', {})

    def compress_spec(self) -> Dict[str, Any]:
        """生成压缩后的 OpenAPI 规范"""
        compressed = {
            'info': self.get_info(),
            'servers': self.get_servers(),
            'paths': {}
        }

        paths = self.get_paths()
        for path, operations in paths.items():
            compressed_path = {}
            for method, operation in operations.items():
                compressed_op = {
                    'summary': operation.summary,
                    'description': operation.description,
                    'operationId': operation.operationId,
                    'tags': operation.tags,
                    'parameters': [
                        {
                            'name': param.name,
                            'in': param.in_,
                            'required': param.required,
                            'schema': param.schema
                        }
                        for param in operation.parameters or []
                    ],
                    'requestBody': {
                        'required': operation.requestBody.required if operation.requestBody else False,
                        'content': operation.requestBody.content if operation.requestBody else {}
                    },
                    'responses': {
                        code: {
                            'description': resp.description,
                            'content': resp.content
                        }
                        for code, resp in operation.responses.items()
                    }
                }
                compressed_path[method] = compressed_op
            compressed['paths'][path] = compressed_path

        return compressed

    def save_compressed_spec(self, output_path: str):
        """保存压缩后的 OpenAPI 规范到文件"""
        compressed_spec = self.compress_spec()
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(compressed_spec, f, indent=2, ensure_ascii=False)

    def to_csv(self, output_path: str):
        """
        将 OpenAPI 文档转换为 CSV 格式并保存到文件

        Args:
            output_path: 输出 CSV 文件路径
        """
        # 定义 CSV 表头
        headers = [
            "path", "method", "summary", "description", "operationId", "tags",
            "parameters", "requestBody", "responses"
        ]

        # 准备数据行
        rows = []
        paths = self.get_paths()
        for path, operations in paths.items():
            for method, operation in operations.items():
                # 扁平化参数
                parameters = ";".join(
                    [
                        f"{param.name}({param.in_})"
                        for param in operation.parameters or []
                    ]
                )

                # 扁平化请求体
                request_body = ""
                if operation.requestBody:
                    request_body = ";".join(
                        [
                            f"{content_type}({schema.get('type', 'object')})"
                            for content_type, schema in operation.requestBody.content.items()
                        ]
                    )

                # 扁平化响应
                responses = ";".join(
                    [
                        f"{code}({resp.description})"
                        for code, resp in operation.responses.items()
                    ]
                )

                # 扁平化标签
                tags = ";".join(operation.tags or [])

                # 构建一行数据
                row = [
                    path, method, operation.summary or "", operation.description or "",
                                  operation.operationId or "", tags, parameters, request_body, responses
                ]
                rows.append(row)

        # 写入 CSV 文件
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)  # 写入表头
            writer.writerows(rows)  # 写入数据行

    def to_dataframe(self) -> pd.DataFrame:
        """
        将 OpenAPI 文档转换为 pandas DataFrame

        Returns:
            pd.DataFrame: 包含 API 信息的 DataFrame
        """
        # 准备数据行
        rows = []
        paths = self.get_paths()

        # 获取全局信息
        api_title = self.get_info().get('title', '')
        api_version = self.get_info().get('version', '')
        api_description = self.get_info().get('description', '')

        # 获取服务器信息
        servers = self.get_servers()
        server_urls = [server.get('url', '') for server in servers] if isinstance(servers, list) else []
        base_url = server_urls[0] if server_urls else ''

        for path, operations in paths.items():
            for method, operation in operations.items():
                # 创建参数的详细信息
                parameters_info = []
                if operation.parameters:
                    for param in operation.parameters:
                        param_type = param.schema.get('type', 'unknown')
                        param_format = param.schema.get('format', '')
                        param_info = {
                            'name': param.name,
                            'in': param.in_,
                            'required': param.required,
                            'type': param_type,
                            'format': param_format,
                            'description': param.description or ''
                        }
                        parameters_info.append(param_info)

                # 请求体信息
                request_body_info = {}
                if operation.requestBody:
                    for content_type, content_schema in operation.requestBody.content.items():
                        schema = content_schema.get('schema', {})
                        properties = schema.get('properties', {})
                        required_props = schema.get('required', [])

                        prop_details = {}
                        for prop_name, prop_details_raw in properties.items():
                            prop_details[prop_name] = {
                                'type': prop_details_raw.get('type', 'unknown'),
                                'description': prop_details_raw.get('description', ''),
                                'required': prop_name in required_props
                            }

                        request_body_info[content_type] = {
                            'schema_type': schema.get('type', 'object'),
                            'properties': prop_details
                        }

                # 响应信息
                response_info = {}
                for status_code, response in operation.responses.items():
                    response_content = {}
                    for content_type, content_schema in response.content.items():
                        schema = content_schema.get('schema', {})
                        response_content[content_type] = {
                            'schema_type': schema.get('type', 'object'),
                            'description': schema.get('description', '')
                        }

                    response_info[status_code] = {
                        'description': response.description or '',
                        'content': response_content
                    }

                # 构建一行完整数据
                row = {
                    'api_title': api_title,
                    'api_version': api_version,
                    'api_description': api_description,
                    'base_url': base_url,
                    'path': path,
                    'method': method.upper(),
                    'full_url': f"{base_url}{path}",
                    'summary': operation.summary or '',
                    'description': operation.description or '',
                    'operationId': operation.operationId or '',
                    'tags': operation.tags or [],
                    'parameters': parameters_info,
                    'request_body': request_body_info,
                    'responses': response_info
                }
                rows.append(row)

        # 创建 DataFrame
        return pd.DataFrame(rows)

    def _extract_schema_details(self, schema):
        """提取schema的详细信息但保持紧凑"""
        if not schema:
            return {}

        details = {}
        schema_type = schema.get('type', 'object')

        # 对象类型
        if schema_type == 'object':
            properties = schema.get('properties', {})
            required = schema.get('required', [])

            prop_details = {}
            for name, prop in properties.items():
                # 简化属性信息，保留关键字段
                is_required = name in required
                prop_type = prop.get('type', 'unknown')
                desc = prop.get('description', '')

                # 递归处理嵌套对象，但限制深度
                if prop_type == 'object' and 'properties' in prop:
                    nested_props = {}
                    for nested_name, nested_prop in prop.get('properties', {}).items():
                        nested_props[nested_name] = {
                            'type': nested_prop.get('type', 'unknown'),
                            'description': nested_prop.get('description', '')[:50]  # 限制描述长度
                        }
                    prop_details[name] = {
                        'type': prop_type,
                        'required': is_required,
                        'description': desc[:50],  # 限制描述长度
                        'properties': nested_props
                    }
                # 处理数组类型
                elif prop_type == 'array' and 'items' in prop:
                    items = prop.get('items', {})
                    items_type = items.get('type', 'unknown')
                    prop_details[name] = {
                        'type': f'array[{items_type}]',
                        'required': is_required,
                        'description': desc[:50]  # 限制描述长度
                    }
                else:
                    # 基本类型
                    format_str = prop.get('format', '')
                    enum = prop.get('enum', [])
                    type_str = f"{prop_type}{f'({format_str})' if format_str else ''}"
                    if enum and len(enum) <= 5:  # 最多显示5个枚举值
                        type_str = f"{type_str} enum:{','.join(str(e) for e in enum)}"

                    prop_details[name] = {
                        'type': type_str,
                        'required': is_required,
                        'description': desc[:50]  # 限制描述长度
                    }

            return {'type': schema_type, 'properties': prop_details}

        # 数组类型
        elif schema_type == 'array' and 'items' in schema:
            items = schema.get('items', {})
            items_details = self._extract_schema_details(items)
            return {'type': 'array', 'items': items_details}

        # 其他基本类型
        else:
            return {
                'type': schema_type,
                'format': schema.get('format', ''),
                'enum': schema.get('enum', [])[:5]  # 最多保留5个枚举值
            }

    def to_model_dataframe(self) -> pd.DataFrame:
        """
        将 OpenAPI 文档转换为适合提供给模型使用的 pandas DataFrame，
        提供详细的请求参数和返回参数，但控制token使用量

        Returns:
            pd.DataFrame: 优化后的 API 信息 DataFrame
        """
        # 准备数据
        all_data = []
        paths = self.get_paths()

        # 获取API基本信息
        api_info = self.get_info()
        api_title = api_info.get('title', '')
        api_version = api_info.get('version', '')

        # 获取服务器信息
        servers = self.get_servers()
        server_urls = [server.get('url', '') for server in servers] if isinstance(servers, list) else []
        base_url = server_urls[0] if server_urls else ''

        # 解析API路径
        for path, operations in paths.items():
            for method, operation in operations.items():
                # 处理请求参数
                parameters_list = []
                if operation.parameters:
                    for param in operation.parameters:
                        schema_details = self._extract_schema_details(param.schema)
                        required_mark = "必填" if param.required else "可选"
                        param_desc = param.description or ""
                        param_str = f"{param.name} ({param.in_}, {schema_details.get('type', 'unknown')}, {required_mark}): {param_desc[:100]}"
                        parameters_list.append(param_str)

                # 处理请求体
                request_body_info = []
                if operation.requestBody:
                    for content_type, content_info in operation.requestBody.content.items():
                        schema = content_info.get('schema', {})
                        schema_details = self._extract_schema_details(schema)

                        # 添加内容类型
                        request_body_info.append(f"Content-Type: {content_type}")

                        # 处理请求体属性
                        if schema_details.get('type') == 'object' and 'properties' in schema_details:
                            for prop_name, prop_info in schema_details['properties'].items():
                                required_mark = "必填" if prop_info.get('required', False) else "可选"
                                prop_desc = prop_info.get('description', '')
                                prop_str = f"- {prop_name} ({prop_info.get('type', 'unknown')}, {required_mark}): {prop_desc}"
                                request_body_info.append(prop_str)

                # 处理响应信息
                response_info = []
                for status_code, response in operation.responses.items():
                    resp_desc = response.description or ""
                    response_info.append(f"状态码 {status_code}: {resp_desc[:100]}")

                    # 处理响应内容
                    for content_type, content_info in response.content.items():
                        schema = content_info.get('schema', {})
                        schema_details = self._extract_schema_details(schema)

                        response_info.append(f"Content-Type: {content_type}")

                        # 处理响应体属性
                        if schema_details.get('type') == 'object' and 'properties' in schema_details:
                            for prop_name, prop_info in schema_details['properties'].items():
                                prop_desc = prop_info.get('description', '')
                                prop_str = f"- {prop_name} ({prop_info.get('type', 'unknown')}): {prop_desc}"
                                response_info.append(prop_str)

                # 构建行数据
                row_data = {
                    'api_name': api_title,
                    'version': api_version,
                    'endpoint': f"{method.upper()} {path}",
                    'full_url': f"{base_url}{path}",
                    'summary': operation.summary or '',
                    'description': operation.description or '',
                    'tags': ', '.join(operation.tags or []),
                    'parameters': '\n'.join(parameters_list),
                    'request_body': '\n'.join(request_body_info),
                    'responses': '\n'.join(response_info)
                }
                all_data.append(row_data)

        return pd.DataFrame(all_data)

    def save_model_dataframe(self, output_path: str, format: str = 'csv'):
        """
        保存模型友好的DataFrame到文件

        Args:
            output_path: 输出文件路径
            format: 输出格式，支持 'csv', 'excel', 'json'
        """
        df = self.to_model_dataframe()

        if format.lower() == 'csv':
            df.to_csv(output_path, index=False, encoding='utf-8')
        elif format.lower() == 'excel':
            df.to_excel(output_path, index=False)
        elif format.lower() == 'json':
            df.to_json(output_path, orient='records', force_ascii=False, indent=2)
        else:
            raise ValueError(f"不支持的输出格式: {format}，请使用 'csv', 'excel' 或 'json'")

    def get_api_context_for_model(self, path_filter=None, method_filter=None, max_endpoints=None) -> str:
        """
        生成适合提供给模型作为上下文的API描述文本

        Args:
            path_filter: 路径过滤条件，可以是字符串或正则表达式
            method_filter: HTTP方法过滤条件，如'GET'、'POST'等
            max_endpoints: 最大端点数量，控制输出token数量

        Returns:
            str: 格式化的API上下文描述
        """
        df = self.to_model_dataframe()

        # 应用过滤器
        if path_filter:
            df = df[df['endpoint'].str.contains(path_filter, case=False)]

        if method_filter:
            method_upper = method_filter.upper()
            df = df[df['endpoint'].str.startswith(method_upper)]

        # 限制端点数量
        if max_endpoints and len(df) > max_endpoints:
            df = df.head(max_endpoints)

        # 构建上下文文本
        context_lines = [
            f"# {df['api_name'].iloc[0]} API (版本: {df['version'].iloc[0]})",
            "\n## 可用端点\n"
        ]

        for _, row in df.iterrows():
            context_lines.append(f"### {row['endpoint']}")
            if row['summary']:
                context_lines.append(f"**概要**: {row['summary']}")
            if row['description']:
                context_lines.append(f"**描述**: {row['description']}")

            # 参数信息
            if row['parameters']:
                context_lines.append("\n**参数**:")
                context_lines.append(row['parameters'])

            # 请求体信息
            if row['request_body']:
                context_lines.append("\n**请求体**:")
                context_lines.append(row['request_body'])

            # 响应信息
            if row['responses']:
                context_lines.append("\n**响应**:")
                context_lines.append(row['responses'])

            context_lines.append("\n---\n")  # 端点分隔符

        return "\n".join(context_lines)

    def iter_api_details_by_path(self):
        """
        返回一个迭代器，输出每个API路径的详细信息，
        同一路径的不同请求方法合并为一个DataFrame。
        JSON结构被扁平化为字符串格式，以减少token使用量。

        Yields:
            pd.DataFrame: 每个API路径及其关联操作的DataFrame，包含扁平化的信息
        """
        paths = self.get_paths()

        # 获取全局信息
        api_title = self.get_info().get('title', '')
        api_version = self.get_info().get('version', '')
        api_description = self.get_info().get('description', '')

        # 获取服务器信息
        servers = self.get_servers()
        server_urls = [server.get('url', '') for server in servers] if isinstance(servers, list) else []
        base_url = server_urls[0] if server_urls else ''

        for path, operations in paths.items():
            rows = []
            for method, operation in operations.items():
                # 扁平化参数信息为字符串
                parameters_str = ""
                if operation.parameters:
                    param_items = []
                    for param in operation.parameters:
                        required = "必填" if param.required else "可选"
                        param_type = param.schema.get('type', 'unknown')
                        param_format = param.schema.get('format', '')
                        type_str = f"{param_type}{f'({param_format})' if param_format else ''}"
                        desc = param.description or ""
                        param_items.append(f"{param.name} ({param.in_}, {type_str}, {required}): {desc}")
                    parameters_str = "\n".join(param_items)

                # 扁平化请求体为字符串
                request_body_str = ""
                if operation.requestBody:
                    req_body_items = []
                    for content_type, content_schema in operation.requestBody.content.items():
                        req_body_items.append(f"Content-Type: {content_type}")

                        schema = content_schema.get('schema', {})
                        properties = schema.get('properties', {})
                        required_props = schema.get('required', [])

                        for prop_name, prop_details in properties.items():
                            required = "必填" if prop_name in required_props else "可选"
                            prop_type = prop_details.get('type', 'unknown')
                            prop_desc = prop_details.get('description', '')
                            req_body_items.append(f"- {prop_name} ({prop_type}, {required}): {prop_desc}")

                    request_body_str = "\n".join(req_body_items)

                # 扁平化响应信息为字符串
                response_str = ""
                if operation.responses:
                    resp_items = []
                    for status_code, response in operation.responses.items():
                        resp_desc = response.description or ""
                        resp_items.append(f"状态码 {status_code}: {resp_desc}")

                        for content_type, content_schema in response.content.items():
                            resp_items.append(f"Content-Type: {content_type}")

                            schema = content_schema.get('schema', {})
                            if schema:
                                schema_type = schema.get('type', 'object')
                                resp_items.append(f"Schema类型: {schema_type}")

                                # 处理对象类型的schema
                                if schema_type == 'object' and 'properties' in schema:
                                    for prop_name, prop_details in schema.get('properties', {}).items():
                                        prop_type = prop_details.get('type', 'unknown')
                                        prop_desc = prop_details.get('description', '')
                                        resp_items.append(f"- {prop_name} ({prop_type}): {prop_desc}")

                    response_str = "\n".join(resp_items)

                # 构建一行完整数据，使用扁平化的字符串
                row = {
                    'api_title': api_title,
                    'api_version': api_version,
                    'api_description': api_description,
                    'base_url': base_url,
                    'path': path,
                    'method': method.upper(),
                    'full_url': f"{base_url}{path}",
                    'summary': operation.summary or '',
                    'description': operation.description or '',
                    'operationId': operation.operationId or '',
                    'tags': ', '.join(operation.tags or []),  # 将列表转换为逗号分隔的字符串
                    'parameters': parameters_str,  # 扁平化的参数字符串
                    'request_body': request_body_str,  # 扁平化的请求体字符串
                    'responses': response_str  # 扁平化的响应字符串
                }
                rows.append(row)
            yield pd.DataFrame(rows)


if __name__ == '__main__':
    # 从文件加载
    parser = OpenAPIParser(spec_path='res/2.json')

    # 获取所有路径和操作
    paths = parser.get_paths()

    # 获取组件定义
    components = parser.get_components()

    # 获取 API 信息
    info = parser.get_info()

    # 获取服务
    server = parser.get_servers()

    print(info)
    print(server)

    # 保存为模型友好的DataFrame
    parser.save_model_dataframe('res/api_for_model.csv')
    parser.save_model_dataframe('res/api_for_model.xlsx', format='excel')
    parser.save_model_dataframe('res/api_for_model.json', format='json')

    # 获取适合模型使用的API上下文
    api_context = parser.get_api_context_for_model(max_endpoints=10)
    with open('res/api_context.md', 'w', encoding='utf-8') as f:
        f.write(api_context)

    # 获取DataFrame用于自定义处理
    df = parser.to_model_dataframe()
    print(f"成功生成API DataFrame，共 {len(df)} 个端点")

    # 生成并保存压缩后的规范
    compressed_spec = parser.compress_spec()
    # print(json.dumps(compressed_spec, ensure_ascii=False))

    parser.to_csv('res/api.csv')

    # 保存到文件
    parser.save_compressed_spec('res/compressed_spec.json')

    print(df)

    # 使用新的迭代器函数
    api_details_iterator = parser.iter_api_details_by_path()

    from testerx.utils.dataframe_exporter import DataFrameToStringConverter

    converter = DataFrameToStringConverter()

    for item in api_details_iterator:  # 迭代时不进行解包，先查看 item 的结构
        print(converter.convert_to_string(item))
