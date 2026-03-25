# Axiom Language RFC v0.1

## 一门面向 AI 协作开发的静态强类型编译语言

**状态**：Draft
**版本**：0.1
**目标读者**：语言设计者、编译器实现者、工具链开发者、早期用户
**关键词**：AI 原生、静态类型、低隐式、显式副作用、结构化错误、固定模块结构

------

# 目录

1. 引言
2. 设计目标
3. 非目标
4. 核心设计原则
5. 语言概览
6. 语法风格总览
7. 类型系统
8. 值与绑定
9. 结构体、枚举与 newtype
10. 函数与泛型
11. Option / Result
12. 模式匹配
13. 错误处理
14. 副作用系统
15. async/await 并发模型
16. 模块系统与可见性
17. trait / protocol 抽象系统
18. 标准项目结构
19. 测试系统
20. 文档系统
21. 编译模型
22. 调试模型
23. 部署模型
24. 互操作设计
25. 编译器结构化输出
26. Linter / Formatter / AI 协议
27. 安全性与可维护性原则
28. 示例项目
29. 语言限制与刻意取舍
30. MVP 实现建议
31. 未来演进方向
32. 附录：示例语法与 JSON Schema 草案

------

# 1. 引言

Axiom 是一门为 **AI 协作编程（AI-assisted / agentic coding / Vibecoding）** 而设计的编译型语言。

现有主流语言大多围绕“人类程序员”构建，后续再由 IDE、LSP、框架和 lint 工具去弥补可维护性与自动化理解的问题。Axiom 的目标不同：它从语言层、模块层、编译器层、工具链层一开始就把 **“可被 AI 稳定理解、生成、验证、修改”** 作为一级设计目标。

Axiom 并不追求极限简洁语法、极限抽象能力或极限运行时魔法。相反，它强调：

- 静态强类型
- 结构化错误
- 显式副作用
- 固定项目与模块结构
- 高可读性与高局部性
- 可机器消费的编译语义摘要
- 与现有生态务实互操作

Axiom 试图回答一个问题：

> 如果编程语言从第一天起就是为“人类 + AI 共同开发”而设计，它应该长什么样？

------

# 2. 设计目标

Axiom 的目标分为三层。

------

## 2.1 语言层目标

Axiom 必须提供以下语言级能力：

- 静态强类型
- 泛型
- 枚举 / sum type
- Option / Result
- 默认不可变
- 模块系统
- 显式可见性
- 显式副作用
- 结构化错误处理
- async/await
- 模式匹配

------

## 2.2 工程层目标

Axiom 必须可用于真实工程：

- 编译型
- 可测试
- 可调试
- 可部署
- 可生成文档
- 可与现有生态互操作

------

## 2.3 AI 友好层目标

Axiom 必须天然适合 AI 协作：

- 固定模块结构
- 编译器输出结构化摘要
- 低魔法
- 低隐式
- 高可读性
- 高局部性

------

# 3. 非目标

Axiom v0.1 明确不追求以下目标：

1. **不追求成为极低层系统语言**
   - 不以裸内存控制和手写 allocator 为主要卖点
   - 不优先替代 C/C++ 在内核、驱动等领域的地位
2. **不追求极致类型体操**
   - 不优先支持高度复杂的类型级编程
   - 不以 HKT、依赖类型、证明系统为 MVP 目标
3. **不追求框架魔法**
   - 不依赖注解、反射或运行时扫描生成核心行为
   - 不鼓励“看不见的控制流”
4. **不追求语法最短**
   - 优先可读、可生成、可维护，而不是最少字符数
5. **不追求兼容所有编程范式**
   - 优先支持：可读的函数式 + 显式工程化 + 数据导向建模
   - 不鼓励复杂继承层级和隐式多态魔法

------

# 4. 核心设计原则

------

## 4.1 显式优先于隐式

Axiom 中以下语义必须尽量显式：

- 可变性
- 错误传播
- 副作用
- 可见性
- 导入
- async 边界
- 依赖关系

------

## 4.2 局部可理解性

开发者和 AI 应尽量只依赖当前文件和少量直接依赖，就能理解一段代码的主要语义：

- 输入输出
- 可能失败方式
- 是否有副作用
- 是否异步
- 依赖哪些模块

------

## 4.3 结构稳定性

同一类代码应有稳定写法和稳定落点：

- 固定目录结构
- 固定模块文件布局
- 固定测试组织方式
- 固定文档生成方式
- 官方 formatter 统一风格

------

## 4.4 语义可提取性

编译器必须能够静态提取：

- 类型签名
- effect 摘要
- error 摘要
- 调用依赖图
- public API 变化
- 模块语义边界

并以结构化格式提供给工具和 AI。

------

## 4.5 低魔法原则

Axiom 避免以下高魔法特性成为主流：

- 强宏系统
- 隐式注入
- 隐式转换
- 隐式异常
- 深层反射式框架机制
- 大量基于注解的隐藏控制流

------

# 5. 语言概览

Axiom 是一门：

- 静态强类型语言
- 编译型语言
- 默认不可变
- 使用 `Result` 进行结构化错误传播
- 支持 enum/sum type 和模式匹配
- 支持 async/await
- 函数级显式副作用声明
- 具备简单、可控的泛型和 trait 机制
- 面向模块化工程开发
- 内建测试、文档与机器可读编译摘要

------

# 6. 语法风格总览

Axiom 采用接近现代主流语言的块状语法：

- 花括号作用域
- `fn` 定义函数
- `struct` / `enum` 定义数据
- `match` 做模式匹配
- `let` 不可变绑定
- `var` 可变绑定
- `pub` / `internal` / private 控制可见性
- `async fn` + `await`
- `effects [...]` 声明副作用

示例：

axiom



```
module domain.user.service

use domain.user.model.{User, UserId, CreateUserInput}
use domain.user.errors.CreateUserError

pub fn create_user(input: CreateUserInput) -> Result<User, CreateUserError>
    effects [db.read, db.write]
{
    if input.name.trim() == "" {
        return Err(CreateUserError::InvalidName)
    }

    let user = User {
        id: generate_user_id(),
        name: input.name,
        email: input.email
    }

    save_user(user)?
    Ok(user)
}
```

------

# 7. 类型系统

------

## 7.1 设计目标

Axiom 的类型系统必须具备：

- 静态检查
- 强类型约束
- 适度推断
- 容易阅读与理解
- 支持业务建模
- 对 AI 生成和 refactor 友好

------

## 7.2 基本类型

内建基本类型包括：

axiom



```
Int
Float
Bool
String
Char
Bytes
Unit
```

其中：

- `Unit` 表示无意义返回值
- 不存在“隐式 null”
- 空值通过 `Option<T>` 表示

------

## 7.3 复合类型

Axiom 支持以下复合类型：

- `List<T>`
- `Map<K, V>`
- `Set<T>`
- 元组 `(A, B)`
- 函数类型（由编译器内部表示，语言表面可以后续暴露）

------

## 7.4 类型推断

Axiom 允许**局部类型推断**，但避免全局复杂推断。

允许：

axiom



```
let name = "alice"
let count = 1
```

允许：

axiom



```
let user = User {
    id: UserId("u1"),
    name: "Alice",
    email: Email("a@test.com")
}
```

不鼓励：

- 需要跨多个模块才能理解的复杂推断
- 深层泛型推断导致报错难以理解

原则：

> 推断用于减少重复，不用于隐藏语义。

------

## 7.5 类型等价

Axiom 区分：

- 结构上的相似
- 语义上的不同

因此鼓励 `newtype` 来表达语义边界：

axiom



```
pub newtype UserId = String
pub newtype Email = String
```

这样 `UserId` 与 `Email` 虽底层都是 `String`，但不可混用。

这对 AI 非常重要，因为它减少“字符串都一样”的误用。

------

# 8. 值与绑定

------

## 8.1 不可变绑定

默认使用 `let` 创建不可变绑定：

axiom



```
let name = "Alice"
let user_id = UserId("u1")
```

------

## 8.2 可变绑定

只有显式使用 `var` 才可变：

axiom



```
var count = 0
count = count + 1
```

------

## 8.3 设计原则

默认不可变的理由：

- 降低状态空间
- 降低并发复杂度
- 降低 AI 修改时引入副作用的风险
- 提高代码局部可推理性

------

## 8.4 更新不可变数据

推荐使用“复制并更新”的语法：

axiom



```
let user2 = user with {
    name = "Bob"
}
```

语义上表示：基于 `user` 创建一个新值，仅替换 `name` 字段。

------

# 9. 结构体、枚举与 newtype

------

## 9.1 结构体

axiom



```
pub struct User {
    pub id: UserId
    pub name: String
    pub email: Email
}
```

字段是否公开必须显式声明。

------

## 9.2 枚举 / sum type

Axiom 中 `enum` 是一等公民，可用于表达状态机、错误、业务结果等。

axiom



```
pub enum PaymentStatus {
    Pending
    Paid(receipt_id: String)
    Failed(reason: String)
}
```

也支持命名字段形式：

axiom



```
pub enum ApiResponse {
    Success(data: String)
    Error(code: Int, message: String)
}
```

------

## 9.3 newtype

`newtype` 用于为底层类型赋予新语义：

axiom



```
pub newtype UserId = String
pub newtype Email = String
pub newtype OrderId = String
```

优点：

- 避免类型混用
- 明确业务语义
- 提升自动生成和自动修复的安全性

------

# 10. 函数与泛型

------

## 10.1 基础函数定义

axiom



```
pub fn add(a: Int, b: Int) -> Int {
    a + b
}
```

------

## 10.2 返回值必须显式

Axiom 中函数返回类型应显式声明。
局部 lambda 或测试辅助函数可在后续版本允许更灵活推断，但 public API 必须显式。

------

## 10.3 泛型

axiom



```
pub fn first<T>(items: List<T>) -> Option<T> {
    ...
}
```

泛型目标：

- 表达通用逻辑
- 避免重复代码
- 保持可读性

------

## 10.4 泛型约束

通过 trait/protocol 约束：

axiom



```
pub trait Display {
    fn display(self) -> String
}

pub fn show<T: Display>(value: T) -> String {
    value.display()
}
```

Axiom 的泛型系统追求工程可读性，不追求高难度类型体操。

------

## 10.5 函数签名的完整性

Axiom 强调函数签名应成为“局部契约”，尽量包含：

- 参数类型
- 返回类型
- 错误类型（通过 `Result`）
- effect 集
- async 属性

例如：

axiom



```
pub async fn fetch_user(id: UserId) -> Result<User, FetchUserError>
    effects [net.call]
```

仅看签名就能理解大部分关键语义。

------

# 11. Option / Result

------

## 11.1 Option

表示“可能有值，也可能无值”：

axiom



```
Option<T> = Some(T) | None
```

示例：

axiom



```
pub fn find_user_name(id: UserId) -> Option<String> {
    ...
}
```

------

## 11.2 Result

表示“可能成功，也可能失败”：

axiom



```
Result<T, E> = Ok(T) | Err(E)
```

示例：

axiom



```
pub fn parse_email(input: String) -> Result<Email, ParseEmailError> {
    ...
}
```

------

## 11.3 语言级地位

`Option` 和 `Result` 是语言概念的一部分，而不仅是普通库类型。编译器理解其语义，用于：

- 错误传播检查
- 模式匹配穷尽分析
- 文档生成
- 结构化摘要输出

------

# 12. 模式匹配

------

## 12.1 基本形式

axiom



```
match result {
    Ok(value) => value,
    Err(err) => handle_error(err)
}
```

------

## 12.2 穷尽性

默认要求穷尽所有分支：

axiom



```
match status {
    PaymentStatus::Pending => ...,
    PaymentStatus::Paid(receipt_id) => ...,
    PaymentStatus::Failed(reason) => ...
}
```

编译器必须检查是否缺失分支。

------

## 12.3 `_` 分支

允许 `_` 作为兜底匹配，但编译器可对 public API 代码发出建议性警告：

- 可能遮蔽未来新增枚举分支
- 可能降低错误处理显式性

------

## 12.4 解构

支持解构结构体、元组和 enum：

axiom



```
match user {
    User { id, name, email } => ...
}
```

axiom



```
match pair {
    (a, b) => ...
}
```

------

# 13. 错误处理

------

## 13.1 原则

Axiom 使用 **结构化错误处理**，而非异常驱动控制流。

原则：

1. 业务错误使用 `Result<T, E>`
2. `E` 应是可枚举、可文档化的错误类型
3. 异常/崩溃仅用于不可恢复系统错误
4. 错误传播必须显式

------

## 13.2 错误类型建模

axiom



```
pub enum CreateUserError {
    InvalidName
    InvalidEmail
    AlreadyExists
    StorageUnavailable
}
```

------

## 13.3 错误传播

Axiom 支持 `?` 传播 `Result` 错误：

axiom



```
let user = repo.find(id)?
```

要求：

- 上层函数返回兼容的 `Result`
- 错误转换如有需要，必须显式

axiom



```
let user = repo.find(id).map_err(map_repo_error)?
```

------

## 13.4 panic / abort

允许存在 `panic` 或 `abort`，但仅用于：

- 逻辑不变量被破坏
- 运行环境损坏
- 明确不可恢复状态

不应用于正常业务控制流。

------

## 13.5 错误文档化

public 函数如果返回 `Result`，文档生成系统必须列出：

- 错误类型名
- 枚举分支
- 可能来源

------

# 14. 副作用系统

这是 Axiom 的核心特性之一。

------

## 14.1 目标

显式副作用系统用于回答：

- 这个函数是否纯？
- 它会不会读写数据库？
- 会不会发网络请求？
- 会不会写日志？
- 会不会修改状态？

这样，人和 AI 在修改代码时都能更可靠地判断边界。

------

## 14.2 语法

axiom



```
pub fn save_user(user: User) -> Result<Unit, SaveUserError>
    effects [db.write, log.write]
{
    ...
}
```

纯函数可省略 `effects`，等价于无 effect。

------

## 14.3 内建 effect 类别

建议 v0.1 内建如下 effect 命名空间：

- `io.read`
- `io.write`
- `fs.read`
- `fs.write`
- `db.read`
- `db.write`
- `net.call`
- `clock.read`
- `random.read`
- `process.exec`
- `log.write`
- `state.mutate`

------

## 14.4 自定义 effect

支持受控自定义：

axiom



```
effects [payment.charge]
```

但必须在项目或包清单中注册，以便：

- 文档生成
- lint 检查
- 编译器结构化输出标准化

------

## 14.5 编译器检查规则

编译器必须检查：

1. 函数体内调用的 effect 是否被声明
2. 被调用函数的 effect 是否被上层涵盖
3. 纯函数中是否意外引入副作用
4. public API effect 集变化是否构成 breaking change

------

## 14.6 设计边界

Axiom 的 effect system 不追求学术完备性，而追求：

- 可读
- 可检查
- 可摘要
- 可被工程团队采用

------

# 15. async/await 并发模型

------

## 15.1 基本形式

axiom



```
pub async fn fetch_user(id: UserId) -> Result<User, FetchUserError>
    effects [net.call]
{
    let response = await http.get("/users/" + id)?
    decode_user(response.body)
}
```

------

## 15.2 规则

- 异步函数必须显式 `async`
- 挂起点必须显式 `await`
- 不允许隐式 async 提升
- 异步 effect 仍由 `effects [...]` 描述，不另设特殊语法

------

## 15.3 并发组合

建议标准库提供：

- `join(a, b)`
- `race(a, b)`
- `timeout(duration, task)`
- cancellation token

示例：

axiom



```
let (user, orders) = await join(
    fetch_user(id),
    fetch_orders(id)
)
```

------

## 15.4 设计目标

Axiom 的 async 模型必须：

- 明确
- 可调试
- 可静态分析
- 不依赖隐藏调度魔法

------

# 16. 模块系统与可见性

------

## 16.1 模块声明

axiom



```
module domain.user.service
```

模块名与文件路径对应。

------

## 16.2 导入

axiom



```
use domain.user.model.{User, UserId}
use domain.user.errors.CreateUserError
```

规则：

- 必须显式导入
- 禁止通配导入
- 导入路径稳定、可预测

------

## 16.3 可见性

Axiom 支持：

- `pub`：公开
- `internal`：包内或模块树内可见
- 默认 private

示例：

axiom



```
pub fn create_user(...) -> ...
internal fn normalize_email(...) -> ...
fn helper(...) -> ...
```

------

## 16.4 设计原则

显式可见性的价值：

- 明确 API 边界
- 降低无意耦合
- 帮助 AI 区分“稳定接口”和“可替换实现细节”

------

# 17. trait / protocol 抽象系统

------

## 17.1 目标

Axiom 需要抽象能力，但不能引入过多隐式复杂性。

trait/protocol 用于：

- 表达接口
- 支持泛型约束
- 提高测试替身实现便利性

------

## 17.2 定义

axiom



```
pub trait UserRepo {
    fn exists_by_email(email: Email) -> Result<Bool, RepoError>
        effects [db.read]

    fn insert(user: User) -> Result<Unit, RepoError>
        effects [db.write]
}
```

------

## 17.3 实现

axiom



```
impl UserRepo for SqlUserRepo {
    fn exists_by_email(email: Email) -> Result<Bool, RepoError>
        effects [db.read]
    {
        ...
    }

    fn insert(user: User) -> Result<Unit, RepoError>
        effects [db.write]
    {
        ...
    }
}
```

------

## 17.4 限制

Axiom v0.1 不鼓励：

- 复杂的隐式实例解析
- 多层 trait 魔法推导
- 依赖导入顺序影响类型选择

trait 的可见性与实现应尽量稳定、可预测。

------

# 18. 标准项目结构

Axiom 强制或强烈约定固定工程结构。

------

## 18.1 项目根结构

text



```
my-app/
  axiom.toml
  src/
    app.ax
    domain/
      user/
        model.ax
        service.ax
        repo.ax
        errors.ax
        tests.ax
      order/
        model.ax
        service.ax
        repo.ax
        errors.ax
        tests.ax
    infra/
      db/
        client.ax
      http/
        server.ax
  docs/
  tests/
```

------

## 18.2 原则

固定结构是 Axiom AI 友好性的核心：

- AI 能预测代码位置
- 自动生成文件时更稳定
- 工具链能机械化处理
- 领域建模更清晰

------

## 18.3 模块模板

推荐每个领域模块包含：

- `model.ax`
- `service.ax`
- `repo.ax`
- `errors.ax`
- `tests.ax`

必要时可扩展，但不鼓励任意风格漂移。

------

# 19. 测试系统

------

## 19.1 内建测试

Axiom 提供语言级测试语法：

axiom



```
test "parse valid email" {
    let result = parse_email("a@test.com")
    assert_eq(result, Ok(Email("a@test.com")))
}
```

------

## 19.2 测试目标

- 易写
- 易读
- 易生成
- 易维护
- 与模块结构稳定对应

------

## 19.3 测试类型

建议支持：

- 单元测试
- 表驱动测试
- 集成测试
- golden test
- compile-fail test（后续）

------

## 19.4 表驱动测试

axiom



```
test "email validation cases" {
    let cases = [
        ("a@test.com", true),
        ("bad", false),
        ("", false)
    ]

    for (input, expected) in cases {
        assert_eq(is_valid_email(input), expected)
    }
}
```

------

## 19.5 替身与 mock

Axiom 倾向通过 trait 实现替身，而不是依赖运行时 mock 框架魔法。

------

# 20. 文档系统

------

## 20.1 文档生成原则

Axiom 所有 public API 应能自动生成文档。

文档来源：

- 源码注释
- 类型签名
- 错误类型
- effect 声明
- 示例代码

------

## 20.2 注释格式

axiom



```
/// Create a new user.
/// Effects: db.read, db.write
/// Errors:
/// - InvalidEmail
/// - AlreadyExists
pub fn create_user(input: CreateUserInput) -> Result<User, CreateUserError>
    effects [db.read, db.write]
```

------

## 20.3 文档生成内容

生成文档时应展示：

- 模块介绍
- 类型定义
- 函数签名
- errors
- effects
- 示例
- 模块依赖
- 版本变化与 breaking changes

------

# 21. 编译模型

------

## 21.1 编译目标

Axiom 是编译型语言，建议支持：

- 原生可执行文件
- 静态/动态库
- WASM
- C ABI 导出

------

## 21.2 中间表示

建议编译器分层：

1. Parser → AST
2. Name resolution
3. Type checking
4. Effect checking
5. Error-flow analysis
6. Lowering to MIR/IR
7. Backend（LLVM / C / WASM）

------

## 21.3 编译输出

标准输出包括：

- 可执行/库文件
- 调试信息
- 文档元数据
- 结构化编译摘要 JSON
- 诊断报告

------

# 22. 调试模型

------

## 22.1 调试需求

Axiom 必须可调试，支持：

- 断点
- 变量查看
- 调用栈
- async 栈追踪
- 源码位置映射

------

## 22.2 调试构建

支持 debug / release 区分：

- debug：保留更多符号和检查
- release：优化和裁剪

------

## 22.3 调试辅助

语言可提供：

axiom



```
debug value
```

仅在 debug build 可用。

------

# 23. 部署模型

------

## 23.1 部署目标

Axiom 程序应容易：

- 打包
- 发布
- 容器化
- 集成到现有运维系统
- 审计依赖与构建元数据

------

## 23.2 构建目标类型

- `exe`
- `lib`
- `wasm`

------

## 23.3 工具链输出

建议工具链支持：

- lockfile
- checksums
- SBOM
- license report
- reproducible builds

------

# 24. 互操作设计

------

## 24.1 原则

Axiom 不能孤立存在，必须务实接入现有生态。

------

## 24.2 C ABI

优先支持 C ABI 互操作。

导入：

axiom



```
extern c fn sqlite_open(path: String) -> Int
```

导出：

axiom



```
export c fn add(a: Int, b: Int) -> Int {
    a + b
}
```

------

## 24.3 数据协议互操作

工具层建议支持：

- JSON
- Protobuf
- OpenAPI
- gRPC
- SQL schema binding

------

## 24.4 生态桥接

后续可支持：

- Python 扩展
- Node 原生模块
- JVM 桥接
- .NET 桥接

但 v0.1 以 C ABI + WASM + API schema 为主。

------

# 25. 编译器结构化输出

这是 Axiom 与其他语言最关键的差异化之一。

------

## 25.1 目标

编译器不应只输出人类可读错误信息，还必须输出**机器可读语义摘要**，供：

- IDE
- LSP
- AI agent
- 自动重构工具
- API 比较工具
- 文档系统

消费。

------

## 25.2 输出内容

每个模块至少应输出：

- 模块名
- 导出符号
- 类型定义
- 函数签名
- effect 集
- 错误类型
- async 属性
- 依赖列表
- 调用图
- breaking change 分析
- diagnostics

------

## 25.3 示例

JSON



```
{
  "module": "domain.user.service",
  "exports": [
    {
      "name": "create_user",
      "kind": "function",
      "visibility": "public",
      "signature": "(CreateUserInput) -> Result<User, CreateUserError>",
      "effects": ["db.read", "db.write"],
      "errors": [
        "CreateUserError::InvalidName",
        "CreateUserError::InvalidEmail",
        "CreateUserError::AlreadyExists",
        "CreateUserError::StorageUnavailable"
      ],
      "async": false,
      "calls": [
        "domain.user.service.parse_email",
        "domain.user.repo.UserRepo.exists_by_email",
        "domain.user.repo.UserRepo.insert"
      ]
    }
  ],
  "types": [
    {
      "name": "CreateUserError",
      "kind": "enum",
      "variants": [
        "InvalidName",
        "InvalidEmail",
        "AlreadyExists",
        "StorageUnavailable"
      ]
    }
  ],
  "diagnostics": [],
  "breaking_changes": []
}
```

------

## 25.4 价值

结构化编译输出能让 AI 更可靠地：

- 定位错误
- 发现缺失依赖
- 做批量重构
- 生成测试
- 分析 effect 扩散
- 验证 public API 是否稳定

------

# 26. Linter / Formatter / AI 协议

------

## 26.1 Formatter

Axiom 官方必须提供统一 formatter：

- 一个主流风格
- 尽量少配置
- 保持语法树稳定格式化
- 让 AI 自动改代码后易于标准化

------

## 26.2 Linter

建议内建以下规则：

- public API 缺注释
- match 未穷尽
- effect 未声明
- effect 过大
- 错误类型过于宽泛
- 函数过长
- 模块职责漂移
- 未使用导入或定义
- `_` 分支掩盖显式枚举分支

------

## 26.3 AI 协议

Axiom 工具链建议提供面向 AI 的标准接口：

- Symbol graph
- Type graph
- Effect graph
- Error-flow graph
- Suggested fixes
- Breaking change report

这样 AI 不是“读原始文本猜”，而是“读语义摘要推理”。

------

# 27. 安全性与可维护性原则

------

## 27.1 防御常见错误

Axiom 通过以下方式降低错误率：

- 默认不可变
- 无隐式 null
- 显式错误传播
- 显式 effect
- 穷尽匹配
- 明确可见性

------

## 27.2 提升长期可维护性

Axiom 通过以下方式优化长期维护：

- 模块结构固定
- 文档与类型签名强绑定
- 编译器输出 breaking change
- trait 抽象简单
- 框架魔法最小化

------

# 28. 示例项目

以下展示一个简化的用户模块。

------

## 28.1 model.ax

axiom



```
module domain.user.model

pub newtype UserId = String
pub newtype Email = String

pub struct User {
    pub id: UserId
    pub name: String
    pub email: Email
}

pub struct CreateUserInput {
    pub name: String
    pub email: String
}
```

------

## 28.2 errors.ax

axiom



```
module domain.user.errors

pub enum CreateUserError {
    InvalidName
    InvalidEmail
    AlreadyExists
    StorageUnavailable
}
```

------

## 28.3 repo.ax

axiom



```
module domain.user.repo

use domain.user.model.{User, Email}

pub enum RepoError {
    ConnectionFailed
    Conflict
    Unknown
}

pub trait UserRepo {
    fn exists_by_email(email: Email) -> Result<Bool, RepoError>
        effects [db.read]

    fn insert(user: User) -> Result<Unit, RepoError>
        effects [db.write]
}
```

------

## 28.4 service.ax

axiom



```
module domain.user.service

use domain.user.model.{User, UserId, Email, CreateUserInput}
use domain.user.errors.CreateUserError
use domain.user.repo.{UserRepo, RepoError}

/// Create a new user.
/// Effects: db.read, db.write
/// Errors:
/// - InvalidName
/// - InvalidEmail
/// - AlreadyExists
/// - StorageUnavailable
pub fn create_user<R: UserRepo>(
    repo: R,
    input: CreateUserInput
) -> Result<User, CreateUserError>
    effects [db.read, db.write]
{
    if input.name.trim() == "" {
        return Err(CreateUserError::InvalidName)
    }

    let email = parse_email(input.email)?
    let exists = repo.exists_by_email(email)
        .map_err(map_repo_error)?

    if exists {
        return Err(CreateUserError::AlreadyExists)
    }

    let user = User {
        id: UserId("generated-id"),
        name: input.name,
        email: email
    }

    repo.insert(user).map_err(map_repo_error)?
    Ok(user)
}

fn parse_email(input: String) -> Result<Email, CreateUserError> {
    if input.contains("@") {
        Ok(Email(input))
    } else {
        Err(CreateUserError::InvalidEmail)
    }
}

fn map_repo_error(err: RepoError) -> CreateUserError {
    match err {
        RepoError::Conflict => CreateUserError::AlreadyExists,
        RepoError::ConnectionFailed => CreateUserError::StorageUnavailable,
        RepoError::Unknown => CreateUserError::StorageUnavailable
    }
}
```

------

## 28.5 tests.ax

axiom



```
module domain.user.tests

use domain.user.service.create_user
use domain.user.model.CreateUserInput
use domain.user.errors.CreateUserError

test "invalid email returns InvalidEmail" {
    let repo = FakeUserRepo::new()

    let result = create_user(repo, CreateUserInput {
        name: "Alice",
        email: "bad-email"
    })

    assert_eq(result, Err(CreateUserError::InvalidEmail))
}
```

------

# 29. 语言限制与刻意取舍

Axiom 的一些能力并非“做不到”，而是**刻意暂缓或限制**。

------

## 29.1 宏系统

v0.1 不支持强 AST 宏系统。
原因：

- 降低语义隐藏
- 保持代码可直接阅读
- 提高 AI 生成稳定性

仅允许有限 `derive` 类功能。

------

## 29.2 隐式转换

不支持隐式转换。
原因：

- 减少类型歧义
- 让报错更清晰
- 避免 AI 在生成时误判

------

## 29.3 继承式 OOP

不以继承为核心抽象机制，优先：

- struct
- enum
- trait
- 组合

------

## 29.4 反射驱动框架

不鼓励把主流程控制权交给运行时反射框架。
若提供注解，也必须能生成静态可审查摘要。

------

## 29.5 全局可变状态

强烈限制。
若必须使用，应通过明确模块能力边界表达。

------

# 30. MVP 实现建议

如果要在现实中启动这门语言，建议分阶段。

------

## 30.1 Phase 1：最小可用语言

实现：

- lexer / parser
- AST
- 基本类型
- struct / enum / newtype
- let / var
- fn
- module / use
- pub / private
- Option / Result
- match
- `?`
- tests
- formatter
- compiler JSON summary

暂不实现：

- async
- trait 高级部分
- effect 完整检查
- C ABI 全套
- WASM

------

## 30.2 Phase 2：工程化增强

加入：

- trait/protocol
- async/await
- effect 声明与检查
- 文档生成
- 基础 LSP
- C ABI

------

## 30.3 Phase 3：AI 原生工具链

加入：

- symbol graph
- breaking change analyzer
- effect graph
- error-flow graph
- AI action protocol
- OpenAPI / gRPC 生成

------

# 31. 未来演进方向

Axiom v0.1 之后可探索：

- 更完整 capability/effect 模型
- actor 或 structured concurrency
- schema-first API 生成
- 数据库查询静态检查
- 更强的增量编译
- 语义 diff 工具
- AI agent 专用编译模式
- 安全沙盒执行模型
- WASI 深度支持

------

# 32. 附录

------

## 32.1 EBNF 风格语法草案（简化）

ebnf



```
module_decl     = "module" ident_path ;
use_decl        = "use" ident_path [ "." "{" ident_list "}" ] ;

visibility      = "pub" | "internal" ;
mutability      = "let" | "var" ;

struct_decl     = [visibility] "struct" IDENT "{" field_list "}" ;
field           = [visibility] IDENT ":" type_expr ;

enum_decl       = [visibility] "enum" IDENT "{" variant_list "}" ;
variant         = IDENT [ "(" named_or_positional_types ")" ] ;

newtype_decl    = [visibility] "newtype" IDENT "=" type_expr ;

fn_decl         = [visibility] ["async"] "fn" IDENT
                  generic_params?
                  "(" param_list? ")"
                  "->" type_expr
                  effects_clause?
                  block ;

effects_clause  = "effects" "[" effect_list? "]" ;

trait_decl      = [visibility] "trait" IDENT
                  generic_params?
                  "{" trait_member_list "}" ;

test_decl       = "test" STRING block ;

match_expr      = "match" expr "{" match_arm_list "}" ;
match_arm       = pattern "=>" expr_or_block ;

result_type     = "Result" "<" type_expr "," type_expr ">" ;
option_type     = "Option" "<" type_expr ">" ;
```

------

## 32.2 编译器结构化输出 Schema（简化）

JSON



```
{
  "module": "string",
  "exports": [
    {
      "name": "string",
      "kind": "function|struct|enum|trait|const",
      "visibility": "public|internal|private",
      "signature": "string",
      "effects": ["string"],
      "errors": ["string"],
      "async": true,
      "calls": ["string"]
    }
  ],
  "types": [
    {
      "name": "string",
      "kind": "struct|enum|newtype|alias",
      "fields": [],
      "variants": []
    }
  ],
  "diagnostics": [
    {
      "level": "error|warning|info",
      "code": "string",
      "message": "string",
      "location": {
        "file": "string",
        "line": 0,
        "column": 0
      }
    }
  ],
  "breaking_changes": [
    {
      "kind": "removed_export|signature_changed|effect_expanded|enum_variant_removed",
      "symbol": "string",
      "message": "string"
    }
  ]
}
```

------

# 结语

Axiom 的核心不是“发明一种更酷的语法”，而是建立一种新的语言契约：

> 代码不仅要能运行、能被人读懂，还要能被 AI 稳定地理解、生成、验证、重构和维护。

因此，Axiom 的真正创新点在于：

- **把 effect、error、visibility、structure 变成语言一级要素**
- **把编译器从“报错器”升级为“语义输出平台”**
- **把项目结构稳定性作为语言设计的一部分**
- **用低魔法、低隐式换取 AI 协作时代更高的可靠性**