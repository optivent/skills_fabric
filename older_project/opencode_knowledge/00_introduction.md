[![Code Wiki logo](https://www.gstatic.com/_/boq-sdlc-agents-ui/_/r/JA1YkbZh5pk.svg)![Code Wiki logo](https://www.gstatic.com/_/boq-sdlc-agents-ui/_/r/Mvosg4klCA4.svg)](https://codewiki.google/)
dark_mode
sharespark Chat 
On this page
Agent Orchestration and Core System 
Agent Definitions and Architecture 
Command-Line Interface (CLI) Management 
Configuration Management 
Feature Orchestration 
Lifecycle Hooks and Behavior Modification 
Built-in Tools and Utilities 
Google Antigravity OAuth 2.0 Integration 
Health Diagnostics and Environment Checks 
Built-in Commands and Skills 
Micro-Component Providers (MCPs) 
Context Window Limit Recovery 
Language Server Protocol (LSP) Integrations 
Publishing and Release Management 
Automated Publishing Workflow 
Automated Changelog and Release Note Generation 
Identifying Unpublished Changes and Version Bump Recommendations 
This wiki was automatically generated on Jan 2, 2026 based on commit [`d0694e5`](https://github.com/code-yeongyu/oh-my-opencode/tree/d0694e5aa4ecd5e0179718e190136f8b213200d9). Gemini can make mistakes, so double-check it. 
#  code-yeongyu/oh-my-opencode
sparkPowered by Gemini
[](https://github.com/code-yeongyu/oh-my-opencode)
On this page
Agent Orchestration and Core System 
Agent Definitions and Architecture 
Command-Line Interface (CLI) Management 
Configuration Management 
Feature Orchestration 
Lifecycle Hooks and Behavior Modification 
Built-in Tools and Utilities 
Google Antigravity OAuth 2.0 Integration 
Health Diagnostics and Environment Checks 
Built-in Commands and Skills 
Micro-Component Providers (MCPs) 
Context Window Limit Recovery 
Language Server Protocol (LSP) Integrations 
Publishing and Release Management 
Automated Publishing Workflow 
Automated Changelog and Release Note Generation 
Identifying Unpublished Changes and Version Bump Recommendations 
This wiki was automatically generated on Jan 2, 2026 based on commit [`d0694e5`](https://github.com/code-yeongyu/oh-my-opencode/tree/d0694e5aa4ecd5e0179718e190136f8b213200d9). Gemini can make mistakes, so double-check it. 

This software repository provides an AI agent system for the OpenCode environment. It orchestrates multi-model AI agents to collaboratively execute complex development tasks. The system enables AI agents to interact with the local file system, execute shell commands, perform code analysis, and manage development workflows.
The system's primary purpose is to empower AI agents to autonomously perform a wide array of software development activities. It employs a specialist-orchestrator pattern where a central orchestrator agent, [`Sisyphus`](https://github.com/code-yeongyu/oh-my-opencode/blob/d0694e5aa4ecd5e0179718e190136f8b213200d9/README.md?plain=1#L161), directs various specialized agents to achieve defined goals. This involves dynamic prompt generation to guide agent decision-making and advanced context window management to ensure continuous operation with large language models.
Functional components include:
  * An agent orchestration layer that coordinates multi-model AI agents using a specialist-orchestrator pattern. See [Agent Orchestration and Core System](https://codewiki.google/github.com/code-yeongyu/oh-my-opencode#agent-orchestration-and-core-system).
  * A collection of callable tools that enable agents to perform actions such as code manipulation, file system operations, and multimodal analysis. See [Built-in Tools and Utilities](https://codewiki.google/github.com/code-yeongyu/oh-my-opencode#built-in-tools-and-utilities).
  * A system of lifecycle hooks to intercept and modify agent behavior, manage context, and handle session recovery. See [Lifecycle Hooks and Behavior Modification](https://codewiki.google/github.com/code-yeongyu/oh-my-opencode#lifecycle-hooks-and-behavior-modification).
  * Centralized configuration management that defines and validates application settings, including agent behaviors and feature enablement. See [Configuration Management](https://codewiki.google/github.com/code-yeongyu/oh-my-opencode#configuration-management).
  * A command-line interface for installation, health diagnostics, and runtime management of AI tasks. See [Command-Line Interface (CLI) Management](https://codewiki.google/github.com/code-yeongyu/oh-my-opencode#command-line-interface-cli-management).

