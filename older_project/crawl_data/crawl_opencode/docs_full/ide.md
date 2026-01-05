[Skip to content](https://opencode.ai/docs/ide/#_top)
[ ![](https://opencode.ai/docs/_astro/logo-dark.DOStV66V.svg) ![](https://opencode.ai/docs/_astro/logo-light.B0yzR0O5.svg) OpenCode  ](https://opencode.ai/)
[Home](https://opencode.ai/)[Docs](https://opencode.ai/docs/)
[ ](https://github.com/sst/opencode)[ ](https://opencode.ai/discord)
Search ` `Ctrl``K` `
Cancel 
  * [ Intro ](https://opencode.ai/docs/)
  * [ Config ](https://opencode.ai/docs/config/)
  * [ Providers ](https://opencode.ai/docs/providers/)
  * [ Network ](https://opencode.ai/docs/network/)
  * [ Enterprise ](https://opencode.ai/docs/enterprise/)
  * [ Troubleshooting ](https://opencode.ai/docs/troubleshooting/)
  * [ Migrating to 1.0 ](https://opencode.ai/docs/1-0/)
  * Usage
    * [ TUI ](https://opencode.ai/docs/tui/)
    * [ CLI ](https://opencode.ai/docs/cli/)
    * [ IDE ](https://opencode.ai/docs/ide/)
    * [ Zen ](https://opencode.ai/docs/zen/)
    * [ Share ](https://opencode.ai/docs/share/)
    * [ GitHub ](https://opencode.ai/docs/github/)
    * [ GitLab ](https://opencode.ai/docs/gitlab/)
  * Configure
    * [ Tools ](https://opencode.ai/docs/tools/)
    * [ Rules ](https://opencode.ai/docs/rules/)
    * [ Agents ](https://opencode.ai/docs/agents/)
    * [ Models ](https://opencode.ai/docs/models/)
    * [ Themes ](https://opencode.ai/docs/themes/)
    * [ Keybinds ](https://opencode.ai/docs/keybinds/)
    * [ Commands ](https://opencode.ai/docs/commands/)
    * [ Formatters ](https://opencode.ai/docs/formatters/)
    * [ Permissions ](https://opencode.ai/docs/permissions/)
    * [ LSP Servers ](https://opencode.ai/docs/lsp/)
    * [ MCP servers ](https://opencode.ai/docs/mcp-servers/)
    * [ ACP Support ](https://opencode.ai/docs/acp/)
    * [ Agent Skills ](https://opencode.ai/docs/skills/)
    * [ Custom Tools ](https://opencode.ai/docs/custom-tools/)
  * Develop
    * [ SDK ](https://opencode.ai/docs/sdk/)
    * [ Server ](https://opencode.ai/docs/server/)
    * [ Plugins ](https://opencode.ai/docs/plugins/)
    * [ Ecosystem ](https://opencode.ai/docs/ecosystem/)


[GitHub](https://github.com/sst/opencode)[Discord](https://opencode.ai/discord)
Select theme Dark Light Auto
On this page
Overview 
  * [ Overview ](https://opencode.ai/docs/ide/#_top)
  * [ Usage ](https://opencode.ai/docs/ide/#usage)
  * [ Installation ](https://opencode.ai/docs/ide/#installation)
    * [ Manual Install ](https://opencode.ai/docs/ide/#manual-install)
    * [ Troubleshooting ](https://opencode.ai/docs/ide/#troubleshooting)


## On this page
  * [ Overview ](https://opencode.ai/docs/ide/#_top)
  * [ Usage ](https://opencode.ai/docs/ide/#usage)
  * [ Installation ](https://opencode.ai/docs/ide/#installation)
    * [ Manual Install ](https://opencode.ai/docs/ide/#manual-install)
    * [ Troubleshooting ](https://opencode.ai/docs/ide/#troubleshooting)


# IDE
The OpenCode extension for VS Code, Cursor, and other IDEs
OpenCode integrates with VS Code, Cursor, or any IDE that supports a terminal. Just run `opencode` in the terminal to get started.
* * *
## [Usage](https://opencode.ai/docs/ide/#usage)
  * **Quick Launch** : Use `Cmd+Esc` (Mac) or `Ctrl+Esc` (Windows/Linux) to open OpenCode in a split terminal view, or focus an existing terminal session if one is already running.
  * **New Session** : Use `Cmd+Shift+Esc` (Mac) or `Ctrl+Shift+Esc` (Windows/Linux) to start a new OpenCode terminal session, even if one is already open. You can also click the OpenCode button in the UI.
  * **Context Awareness** : Automatically share your current selection or tab with OpenCode.
  * **File Reference Shortcuts** : Use `Cmd+Option+K` (Mac) or `Alt+Ctrl+K` (Linux/Windows) to insert file references. For example, `@File#L37-42`.


* * *
## [Installation](https://opencode.ai/docs/ide/#installation)
To install OpenCode on VS Code and popular forks like Cursor, Windsurf, VSCodium:
  1. Open VS Code
  2. Open the integrated terminal
  3. Run `opencode` - the extension installs automatically


If on the other hand you want to use your own IDE when you run `/editor` or `/export` from the TUI, you’ll need to set `export EDITOR="code --wait"`. [Learn more](https://opencode.ai/docs/tui/#editor-setup).
* * *
### [Manual Install](https://opencode.ai/docs/ide/#manual-install)
Search for **OpenCode** in the Extension Marketplace and click **Install**.
* * *
### [Troubleshooting](https://opencode.ai/docs/ide/#troubleshooting)
If the extension fails to install automatically:
  * Ensure you’re running `opencode` in the integrated terminal.
  * Confirm the CLI for your IDE is installed: 
    * For VS Code: `code` command
    * For Cursor: `cursor` command
    * For Windsurf: `windsurf` command
    * For VSCodium: `codium` command
    * If not, run `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux) and search for “Shell Command: Install ‘code’ command in PATH” (or the equivalent for your IDE)
  * Ensure VS Code has permission to install extensions


[](https://github.com/sst/opencode/edit/dev/packages/web/src/content/docs/ide.mdx)[](https://github.com/sst/opencode/issues/new)[](https://opencode.ai/discord)
© [Anomaly](https://anoma.ly)
Dec 30, 2025
