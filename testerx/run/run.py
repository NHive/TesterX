import argparse
from testerx.workflow.add_openapi_documents_to_memory import add_openapi_documents_to_memory


def main():
    parser = argparse.ArgumentParser(description="运行 testerx 项目的入口脚本，支持多种 AI 测试工程师功能。")
    subparsers = parser.add_subparsers(title='子命令', dest='subcommand', help='可用的子命令')

    # 1. 添加 OpenAPI 文档到知识库 (add_api_docs 子命令)
    add_api_docs_parser = subparsers.add_parser('add_api_docs', help='将 OpenAPI 规范文档添加到知识库')
    add_api_docs_parser.add_argument('--spec_path', type=str, required=True, help='OpenAPI 规范文件路径')
    add_api_docs_parser.set_defaults(func=run_add_openapi_documents)

    # 2. 通过文档链接导入数据到知识库 (import_link 子命令)
    import_link_parser = subparsers.add_parser('import_link', help='通过文档链接导入数据到知识库')
    import_link_parser.add_argument('--link', type=str, required=True, help='文档链接 (例如: URL)')
    import_link_parser.set_defaults(func=run_import_from_link)

    # 3. 通过文件导入数据到知识库 (import_file 子命令)
    import_file_parser = subparsers.add_parser('import_file', help='通过文件导入数据到知识库')
    import_file_parser.add_argument('--file_path', type=str, required=True, help='文件路径')
    import_file_parser.add_argument(
        '--file_type', type=str, default='txt', choices=['txt', 'json', 'yaml', 'pdf', 'docx'],
        help='文件类型 (txt, json, yaml, pdf, docx), 默认为 txt'
    )  # 示例文件类型
    import_file_parser.set_defaults(func=run_import_from_file)

    # 4. 通过知识库 + 问题生成对话 (generate_chat 子命令)
    generate_chat_parser = subparsers.add_parser('generate_chat', help='使用知识库和问题生成对话')
    generate_chat_parser.add_argument('--question', type=str, required=True, help='用户问题')
    generate_chat_parser.set_defaults(func=run_generate_conversation)

    # 5. 通过知识库 + 要求生成测试用例 (generate_testcase 子命令)
    generate_testcase_parser = subparsers.add_parser('generate_testcase', help='使用知识库和要求生成测试用例')
    generate_testcase_parser.add_argument('--requirements', type=str, required=True, help='测试用例需求描述')
    generate_testcase_parser.set_defaults(func=run_generate_testcase)

    args = parser.parse_args()

    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()


def run_add_openapi_documents(args):
    """执行 add_openapi_documents_to_memory 函数"""
    spec_path = args.spec_path
    print(f"执行 add_openapi_documents_to_memory 函数，OpenAPI 规范文件路径: {spec_path}")
    add_openapi_documents_to_memory(spec_path)


def run_import_from_link(args):
    """执行通过链接导入数据的功能 (占位符)"""
    link = args.link
    print(f"执行通过链接导入数据的功能，文档链接: {link} (功能待完善)")


def run_import_from_file(args):
    """执行通过文件导入数据的功能 (占位符)"""
    file_path = args.file_path
    file_type = args.file_type
    print(f"执行通过文件导入数据的功能，文件路径: {file_path}, 文件类型: {file_type} (功能待完善)")
    print(f"支持的文件类型: txt, json, yaml, pdf, docx。当前文件类型: {file_type}")


def run_generate_conversation(args):
    """执行基于知识库生成对话的功能 (占位符)"""
    question = args.question
    print(f"执行基于知识库生成对话的功能，用户问题: {question} (功能待完善，将结合知识库进行对话生成)")


def run_generate_testcase(args):
    """执行基于知识库生成测试用例的功能 (占位符)"""
    requirements = args.requirements
    print(f"执行基于知识库生成测试用例的功能，测试用例需求: {requirements} (功能待完善，将结合知识库生成测试用例)")


if __name__ == "__main__":
    main()
