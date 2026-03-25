import { defineConfig } from "vitepress"

export default defineConfig({
  lang: "zh-CN",
  title: "Axiom",
  description: "面向 AI 协作与后端工程的静态强类型语言项目。",
  cleanUrls: true,
  lastUpdated: true,
  themeConfig: {
    nav: [
      { text: "Overview", link: "/" },
      { text: "Vision", link: "/vision" },
      { text: "Architecture", link: "/architecture" },
      { text: "Spec", link: "/spec/glossary" },
      { text: "Process", link: "/process/" },
      { text: "RFC", link: "/rfc/0001-language-goals" },
      { text: "Decisions", link: "/decisions/DEC-0001-no-macros" }
    ],
    sidebar: [
      {
        text: "Overview",
        items: [
          { text: "Home", link: "/" },
          { text: "Vision", link: "/vision" },
          { text: "Architecture", link: "/architecture" }
        ]
      },
      {
        text: "Specification",
        items: [
          { text: "Glossary", link: "/spec/glossary" },
          { text: "Project Layout", link: "/spec/project-layout" },
          { text: "Syntax", link: "/spec/syntax" },
          { text: "Semantics", link: "/spec/semantics" },
          { text: "Type System", link: "/spec/type-system" },
          { text: "Effects", link: "/spec/effects" },
          { text: "Modules", link: "/spec/modules" },
          { text: "Diagnostics", link: "/spec/diagnostics" },
          { text: "Compiler Summary", link: "/spec/compiler-summary" }
        ]
      },
      {
        text: "Process",
        items: [
          { text: "Overview", link: "/process/" },
          { text: "Readiness", link: "/process/multi-agent-readiness" },
          { text: "Workflow", link: "/process/multi-codex-workflow" },
          { text: "Task Slices", link: "/process/task-slices" },
          { text: "Branching and Commits", link: "/process/branching-and-commits" },
          { text: "Development Environment", link: "/process/development-environment" },
          { text: "Implementation Kickoff", link: "/process/implementation-kickoff" }
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
        text: "Decisions",
        items: [
          { text: "No Macros", link: "/decisions/DEC-0001-no-macros" },
          { text: "Default Immutable", link: "/decisions/DEC-0002-default-immutable" },
          { text: "Explicit Effects", link: "/decisions/DEC-0003-explicit-effects" },
          { text: "No Implicit Imports", link: "/decisions/DEC-0004-no-implicit-imports" }
        ]
      }
    ],
    search: {
      provider: "local"
    },
    outline: {
      level: [2, 3],
      label: "On This Page"
    },
    footer: {
      message: "Axiom repository bootstrap.",
      copyright: "Copyright 2026"
    }
  }
})
