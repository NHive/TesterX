# TesterX

TesterX 是一个由 AI 驱动的自动化 API 测试引擎,它可以根据 OpenAPI 规范自动生成全面的 API 测试用例,确保现代软件开发的质量保证工作更加高效和可靠。

## 特性

- 🤖 基于 LLM 的智能测试用例生成
- 📚 支持 OpenAPI 3.1.x 规范解析
- 🎯 自动生成业务场景测试用例
- 📊 集成 Allure 测试报告
- ⚡ 基于 pytest 的高性能测试执行
- 🔄 支持测试用例的自动维护和更新

## 快速开始

1. 准备你的 OpenAPI 规范文件 (JSON/YAML 格式)

2. 运行测试生成命令:

```bash
testerx generate --spec api-spec.json --output tests/
```

3. 执行测试:

```bash
testerx run
```

## 项目结构

```bash
├── projects/ # 测试项目数据目录
│ └── project_name/ # 具体项目
│ ├── api/ # API 接口定义
│ └── config.json # 项目配置
├── testcases/ # 测试用例目录
│ └── project_name/ # 项目测试用例
│ ├── api_tests/ # API 单接口测试
│ └── scenarios/ # 场景集成测试
├── testerx/ # 源代码目录
│ ├── run/ # 运行时核心代码
│ └── utils/ # 工具类
└── tools/ # AI 工具集
```

### projects 目录

存放各个测试项目的数据,由 AI 分析并生成:

- API 接口功能描述
- 请求/响应数据结构
- 业务规则定义
- 测试数据模板

### testcases 目录

包含自动生成的测试用例:

- api_tests: 单接口测试用例
- scenarios: 业务场景测试用例

### testerx 目录

项目核心源码:

- 测试用例生成引擎
- OpenAPI 规范解析器
- 测试执行器
- 工具类库

### tools 目录

AI 辅助工具集:

- 代码生成器
- 测试数据生成器
- 用例优化工具

## 工作原理

TesterX 通过以下步骤工作:

1. 解析 OpenAPI 规范文件,提取 API 接口信息
2. 利用 LLM 分析接口的业务语义和数据结构
3. 智能生成测试用例,包括:
   - 基础功能测试
   - 参数边界测试
   - 业务场景测试
   - 异常情况测试
4. 执行测试并生成详细报告

## 项目进度

- 实现 OpenAPI 解析基础功能
- 完成 curl 命令生成与验证
- 搭建记忆系统基础框架
- 实现测试代码生成引擎
- 开发变更监控基础能力
- 构建对话交互原型
- 添加智能参数推断
- 实现跨接口场景测试
- 完善测试执行引擎
- 添加 CI/CD 集成能力
- 开发监控仪表盘
- 编写使用文档

### 目前完成的工作

- 实现 OpenAPI 解析基础功能
- 完成 curl 命令生成与验证

## 项目状态

项目正在积极开发中，目前还未达到可用标准。

## 后续可能的工作

- 微调 Qwen2.5-Coder 模型，尽量做到离线部署，不依赖第三方 API

## 使用示例

### 1. 创建项目配置

```json
{
  "project_name": "demo_api",
  "openapi_spec": "./openapi.json",
  "base_url": "https://api.example.com",
  "test_data": {
    "users": ["test1", "test2"],
    "tokens": ["token1", "token2"]
  }
}
```

### 2. 生成测试用例

```bash
# 生成单接口测试
testerx generate api-tests

# 生成场景测试
testerx generate scenarios
```

### 3. 执行测试

```bash
# 执行所有测试
testerx run

# 执行指定场景
testerx run --scenario login_flow

# 执行单接口测试
testerx run --api user_login
```

## 测试报告

TesterX 使用 Allure 生成详细的测试报告:

```bash
# 生成报告
testerx report

# 打开报告
allure serve reports/allure
```

## 许可证

本项目采用 Apache-2.0 许可证 - 详见 [LICENSE](LICENSE) 文件
