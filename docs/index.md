---
layout: home

hero:
  name: "Axiom"
  text: "为 AI 协作与后端工程而设计的语言项目 / A language project for AI collaboration and backend engineering"
  tagline: "显式语义、固定结构、结构化编译输出 / Explicit semantics, fixed structure, structured compiler output."
  actions:
    - theme: brand
      text: 阅读愿景 / Vision
      link: /vision
    - theme: alt
      text: 查看规范 / Spec
      link: /spec/glossary
    - theme: alt
      text: 仓库地址 / GitHub
      link: https://github.com/tqtq-Wang/Aximo

features:
  - title: AI-Friendly by Design / 原生面向 AI 协作
    details: 固定模块结构、低魔法、可机器消费的 compiler summary，从语言层面服务 AI 协作。 Stable layout, low magic, and machine-readable compiler summaries are first-class concerns.
  - title: Backend-Oriented / 面向后端工程
    details: 目标是逐步承载真实后端服务开发，强调错误建模、effect 边界和稳定可维护性。 The project is aimed at real backend service development with explicit error and effect boundaries.
  - title: Specification First / 规范先行
    details: 当前阶段优先建立 spec、schema、example、tests 和协作规则，而不是抢跑复杂实现。 The repository prioritizes contracts and collaboration rules before heavy implementation.
---

## 中文简介

这个站点是 Axiom 语言项目的工作型文档入口。

当前目标不是展示一个已经完成的编译器，而是为后续多个 AI 与人类协作开发建立统一的事实源、统一的契约边界和统一的实现起点。

仓库地址：

- [GitHub: tqtq-Wang/Aximo](https://github.com/tqtq-Wang/Aximo)

作者署名：

- Tyler Wang

## English Overview

This site is the working documentation surface for the Axiom language monorepo.

The repository is intentionally organized to support:

- language design clarification
- compiler front-end implementation planning
- AI-assisted parallel development
- future backend service experimentation

Repository:

- [GitHub: tqtq-Wang/Aximo](https://github.com/tqtq-Wang/Aximo)

Copyright:

- Tyler Wang

## 推荐阅读 / Read Order

1. [愿景 / Vision](./vision)
2. [架构 / Architecture](./architecture)
3. [术语表 / Glossary](./spec/glossary)
4. [语法 / Syntax](./spec/syntax)
5. [Effects](./spec/effects)
6. [编译摘要 / Compiler Summary](./spec/compiler-summary)
7. [流程概览 / Process Overview](./process/)
8. [分支与提交 / Branching and Commits](./process/branching-and-commits)
9. [开发环境 / Development Environment](./process/development-environment)
10. [实现启动 / Implementation Kickoff](./process/implementation-kickoff)
