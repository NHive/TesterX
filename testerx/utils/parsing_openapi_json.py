from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import json
from collections import OrderedDict
import csv

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

    # for k, v in paths.items():
    #     print(k)
    #     print(v)
    #
    # print(server)

    # 生成并保存压缩后的规范
    compressed_spec = parser.compress_spec()
    print(json.dumps(compressed_spec, ensure_ascii=False))

    parser.to_csv('test.csv')

    # 保存到文件
    parser.save_compressed_spec('compressed_spec.json')
