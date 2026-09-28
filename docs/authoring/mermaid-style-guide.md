# Mermaid 图表详细格式规范（附录）

本附录是《[报告与设计文档写作规范](report-style-guide.md)》的图表部分附录，给出本仓库
所有 Mermaid 图表必须遵循的书写规则与**可直接复用的合规示例**。

## 核心规则

- **文本语言**：主要使用中文；英文术语作为补充时，格式为"中文术语（English Term）"，
  其中括号一律使用**全角**符号"（"与"）"。
- **严禁英文圆括号**：Mermaid 文本中不得出现英文圆括号 `(` `)`。所有括号场景（含中英
  对照）统一用全角"（""）"，外层容器用方括号 `[]`。
- **换行符**：一律使用 `<br>`，不使用 `\n` 或直接回车。
- **注释**：一律以 `%%` 开头，并单独占据一行。
- **图例（Legend）**：若有，一律置顶；技术场景使用专业配色（通过 `classDef` 定义）。
- **业务流序号**：流程/数据流图中的步骤应带层级分明的序号，如"1、""2、"。

## 命名规则

- **模块命名规则**：`大写缩写[中文名称（英文术语）]`，例如 `DI[数据输入（Data Input）]`。
- **节点命名规则**：`标识[中文名称（英文术语）]`，括号统一全角、外层用 `[]`，例如
  `A2[格式校验（Validation）]`。

下面是命名规则的最小示例，可作为模板：

```mermaid
graph TD
    %% 模块命名规则示例："大写缩写[中文名称（英文术语）]"
    subgraph DI[数据输入（Data Input）]
        A1[文件上传（File Upload）] --> A2[格式校验（Validation）]
        A3[接口接入（API Ingestion）] --> A2
    end
    subgraph DP[数据处理（Data Processing）]
        A2 --> B1[文本分块（Chunking）]
        B1 --> B2[向量编码（Embedding）]
    end
    DI --> DP
```

## 架构图（Architecture Diagram）示例

架构图描述系统内部模块的层次与依赖关系。图例置顶、专业配色、`%%` 注释独占一行：

```mermaid
graph TD
    %% 图例置顶，技术场景专业配色
    subgraph LG[图例（Legend）]
        L1[输入层（Input）]:::inputCls
        L2[处理层（Process）]:::procCls
        L3[存储层（Storage）]:::storeCls
    end

    %% 业务模块：大写缩写[中文名称（英文术语）]
    subgraph DI[数据输入（Data Input）]
        A1[文件上传（File Upload）] --> A2[格式校验（Validation）]
        A3[接口接入（API Ingestion）] --> A2
    end
    subgraph DP[数据处理（Data Processing）]
        A2 --> B1[文本分块（Chunking）]
        B1 --> B2[向量编码（Embedding）]
    end
    subgraph ST[结果存储（Storage）]
        B2 --> C1[向量库（Vector Store）]
    end
    DI --> DP --> ST

    classDef inputCls fill:#dbeafe,stroke:#1e40af,color:#1e3a8a;
    classDef procCls fill:#dcfce7,stroke:#166534,color:#14532d;
    classDef storeCls fill:#fef3c7,stroke:#92400e,color:#78350f;
    class A1,A3 inputCls;
    class A2,B1,B2 procCls;
    class C1 storeCls;
```

## 部署图（Deployment Diagram）示例

部署图描述组件、节点及其运行时关系。用外层子图表示节点（Node），内层节点表示运行
组件（Component），边上标注协议：

```mermaid
graph LR
    %% 图例置顶
    subgraph LG[图例（Legend）]
        LN[物理或虚拟节点（Node）]:::nodeCls
        LC[运行组件（Component）]:::compCls
    end

    subgraph N1[开发机节点（Dev Host）]
        C1[命令行客户端（Claude Code CLI）]:::compCls
        C2[Python 运行时（Runtime）]:::compCls
        C1 --> C2
    end
    subgraph N2[外部服务节点（External Services）]
        C3[大模型服务（Anthropic API）]:::compCls
        C4[无授权检索（DuckDuckGo）]:::compCls
    end
    C2 -->|HTTPS 调用| C3
    C2 -->|HTTPS 检索| C4

    classDef nodeCls fill:#e0e7ff,stroke:#3730a3,color:#312e81;
    classDef compCls fill:#f1f5f9,stroke:#334155,color:#0f172a;
    class N1,N2 nodeCls;
```

## 组件时序图（Sequence Diagram）示例（可选）

时序图描述核心业务场景下模块间的交互与调用顺序，`autonumber` 自动生成步骤序号：

```mermaid
sequenceDiagram
    autonumber
    participant U as 用户（User）
    participant CC as 命令行客户端（Claude Code）
    participant RN as 运行器（Runner）
    participant API as 大模型服务（Anthropic API）
    U->>CC: 提交主题（Topic）
    CC->>RN: 后台启动（Background Run）
    RN->>API: 生成请求（Completion）
    API-->>RN: 返回文本（Response）
    RN-->>CC: 落盘摘要（Summary）
    CC-->>U: 呈现结果（Result）
```

## 数据流/控制流图（Data Flow Diagram）示例（可选）

数据流图展示核心业务的数据流转与控制逻辑，步骤带层级分明的序号：

```mermaid
flowchart TD
    %% 业务流序号层级分明
    S1[1、接收主题（Topic In）] --> S2[2、检索取证（Retrieve）]
    S2 --> S3[3、多视角提问（Perspective QA）]
    S3 --> S4[4、生成大纲（Outline）]
    S4 --> S5[5、成文与引用（Draft and Cite）]
    S5 --> S6[6、润色落盘（Polish and Save）]
```

## 常见违规对照

以下为**反例**（仅作说明，不可照抄）：

```text
错误：A[文件上传(File Upload)]      %% 使用了英文圆括号
正确：A[文件上传（File Upload）]     %% 全角括号

错误：A[第一步\n第二步]             %% 使用了 \n 换行
正确：A[第一步<br>第二步]           %% 使用 <br>

错误：A --> B  // 注释                %% 使用了非 %% 注释
正确：%% 注释独占一行
      A --> B
```

## 落地校验

本仓库以自动化测试守护上述规则：`integrations/claude_code/tests/test_mermaid_style.py`
会扫描 `docs/` 下所有 Markdown 的 ```mermaid 代码块，若出现英文圆括号或 `\n` 字面量即
判失败，从而使本规范在提交环节切实生效。
