import { defineConfig } from "vitepress"

export default defineConfig({
  lang: "zh-CN",
  title: "Axiom",
  description: "面向 AI 协作与后端工程的静态强类型语言项目 · A statically typed language project for AI collaboration and backend engineering.",
  cleanUrls: true,
  lastUpdated: true,
  themeConfig: {
    nav: [
      { text: "首页 / Home", link: "/" },
      { text: "愿景 / Vision", link: "/vision" },
      { text: "架构 / Architecture", link: "/architecture" },
      { text: "规范 / Spec", link: "/spec/glossary" },
      { text: "流程 / Process", link: "/process/" },
      { text: "RFC", link: "/rfc/0001-language-goals" },
      { text: "决策 / Decisions", link: "/decisions/DEC-0001-no-macros" },
      { text: "GitHub", link: "https://github.com/tqtq-Wang/Aximo" }
    ],
    sidebar: [
      {
        text: "概览 / Overview",
        items: [
          { text: "首页 / Home", link: "/" },
          { text: "愿景 / Vision", link: "/vision" },
          { text: "架构 / Architecture", link: "/architecture" }
        ]
      },
      {
        text: "规范 / Specification",
        items: [
          { text: "术语表 / Glossary", link: "/spec/glossary" },
          { text: "项目结构 / Project Layout", link: "/spec/project-layout" },
          { text: "语法 / Syntax", link: "/spec/syntax" },
          { text: "语义 / Semantics", link: "/spec/semantics" },
          { text: "类型系统 / Type System", link: "/spec/type-system" },
          { text: "Effects", link: "/spec/effects" },
          { text: "模块 / Modules", link: "/spec/modules" },
          { text: "诊断 / Diagnostics", link: "/spec/diagnostics" },
          { text: "编译摘要 / Compiler Summary", link: "/spec/compiler-summary" }
        ]
      },
      {
        text: "流程 / Process",
        items: [
          { text: "概览 / Overview", link: "/process/" },
          { text: "准备度 / Readiness", link: "/process/multi-agent-readiness" },
          { text: "协作流 / Workflow", link: "/process/multi-codex-workflow" },
          { text: "CLI 操作手册 / CLI Playbook", link: "/process/multi-agent-cli-playbook" },
          { text: "任务切片 / Task Slices", link: "/process/task-slices" },
          { text: "分支与提交 / Branching and Commits", link: "/process/branching-and-commits" },
          { text: "开发环境 / Development Environment", link: "/process/development-environment" },
          { text: "实现启动 / Implementation Kickoff", link: "/process/implementation-kickoff" }
        ]
      },
      {
        text: "RFC",
        items: [
          { text: "0001 Language Goals", link: "/rfc/0001-language-goals" },
          { text: "0002 Module System", link: "/rfc/0002-module-system" },
          { text: "0003 Type System", link: "/rfc/0003-type-system" },
          { text: "0004 Effects", link: "/rfc/0004-effects" },
          { text: "0005 Error Handling", link: "/rfc/0005-error-handling" },
          { text: "0006 Async", link: "/rfc/0006-async" },
          { text: "0007 Compiler Summary", link: "/rfc/0007-compiler-summary" }
        ]
      },
      {
        text: "决策 / Decisions",
        items: [
          { text: "无宏系统 / No Macros", link: "/decisions/DEC-0001-no-macros" },
          { text: "默认不可变 / Default Immutable", link: "/decisions/DEC-0002-default-immutable" },
          { text: "显式 Effects / Explicit Effects", link: "/decisions/DEC-0003-explicit-effects" },
          { text: "无隐式导入 / No Implicit Imports", link: "/decisions/DEC-0004-no-implicit-imports" }
        ]
      }
    ],
    socialLinks: [
      { icon: "github", link: "https://github.com/tqtq-Wang/Aximo" }
    ],
    search: {
      provider: "local"
    },
    outline: {
      level: [2, 3],
      label: "本页内容 / On This Page"
    },
    footer: {
      message: "Axiom 文档站 · GitHub: https://github.com/tqtq-Wang/Aximo",
      copyright: "Copyright © 2026 Tyler Wang. All rights reserved."
    }
  }
})
