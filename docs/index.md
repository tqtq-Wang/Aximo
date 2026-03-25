---
layout: home

hero:
  name: "Axiom"
  text: "为 AI 协作与后端工程而设计的语言项目"
  tagline: "显式语义、固定结构、结构化编译输出。"
  actions:
    - theme: brand
      text: 阅读愿景
      link: /vision
    - theme: alt
      text: 查看规范
      link: /spec/glossary

features:
  - title: AI-Friendly by Design
    details: 固定模块结构、低魔法、可机器消费的 compiler summary，从语言层面服务 AI 协作。
  - title: Backend-Oriented
    details: 目标是逐步承载真实后端服务开发，强调错误建模、effect 边界和稳定可维护性。
  - title: Specification First
    details: 当前阶段优先建立 spec、schema、example、tests 和协作规则，而不是抢跑复杂实现。
---

## Repository Intent

This site is the working documentation surface for the Axiom language monorepo.

The repository is intentionally organized to support:

- language design clarification
- compiler front-end implementation planning
- AI-assisted parallel development
- future backend service experimentation

## Read Order

1. [Vision](./vision)
2. [Architecture](./architecture)
3. [Glossary](./spec/glossary)
4. [Syntax](./spec/syntax)
5. [Effects](./spec/effects)
6. [Compiler Summary](./spec/compiler-summary)
7. [Process Overview](./process/)
