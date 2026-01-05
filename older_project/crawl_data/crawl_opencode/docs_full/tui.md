[Skip to content](https://opencode.ai/docs/tui/#_top)
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
  * [ Overview ](https://opencode.ai/docs/tui/#_top)
  * [ File references ](https://opencode.ai/docs/tui/#file-references)
  * [ Bash commands ](https://opencode.ai/docs/tui/#bash-commands)
  * [ Commands ](https://opencode.ai/docs/tui/#commands)
    * [ connect ](https://opencode.ai/docs/tui/#connect)
    * [ compact ](https://opencode.ai/docs/tui/#compact)
    * [ details ](https://opencode.ai/docs/tui/#details)
    * [ editor ](https://opencode.ai/docs/tui/#editor)
    * [ exit ](https://opencode.ai/docs/tui/#exit)
    * [ export ](https://opencode.ai/docs/tui/#export)
    * [ help ](https://opencode.ai/docs/tui/#help)
    * [ init ](https://opencode.ai/docs/tui/#init)
    * [ models ](https://opencode.ai/docs/tui/#models)
    * [ new ](https://opencode.ai/docs/tui/#new)
    * [ redo ](https://opencode.ai/docs/tui/#redo)
    * [ sessions ](https://opencode.ai/docs/tui/#sessions)
    * [ share ](https://opencode.ai/docs/tui/#share)
    * [ themes ](https://opencode.ai/docs/tui/#themes)
    * [ undo ](https://opencode.ai/docs/tui/#undo)
    * [ unshare ](https://opencode.ai/docs/tui/#unshare)
  * [ Editor setup ](https://opencode.ai/docs/tui/#editor-setup)
  * [ Configure ](https://opencode.ai/docs/tui/#configure)
    * [ Options ](https://opencode.ai/docs/tui/#options)
  * [ Customization ](https://opencode.ai/docs/tui/#customization)


## On this page
  * [ Overview ](https://opencode.ai/docs/tui/#_top)
  * [ File references ](https://opencode.ai/docs/tui/#file-references)
  * [ Bash commands ](https://opencode.ai/docs/tui/#bash-commands)
  * [ Commands ](https://opencode.ai/docs/tui/#commands)
    * [ connect ](https://opencode.ai/docs/tui/#connect)
    * [ compact ](https://opencode.ai/docs/tui/#compact)
    * [ details ](https://opencode.ai/docs/tui/#details)
    * [ editor ](https://opencode.ai/docs/tui/#editor)
    * [ exit ](https://opencode.ai/docs/tui/#exit)
    * [ export ](https://opencode.ai/docs/tui/#export)
    * [ help ](https://opencode.ai/docs/tui/#help)
    * [ init ](https://opencode.ai/docs/tui/#init)
    * [ models ](https://opencode.ai/docs/tui/#models)
    * [ new ](https://opencode.ai/docs/tui/#new)
    * [ redo ](https://opencode.ai/docs/tui/#redo)
    * [ sessions ](https://opencode.ai/docs/tui/#sessions)
    * [ share ](https://opencode.ai/docs/tui/#share)
    * [ themes ](https://opencode.ai/docs/tui/#themes)
    * [ undo ](https://opencode.ai/docs/tui/#undo)
    * [ unshare ](https://opencode.ai/docs/tui/#unshare)
  * [ Editor setup ](https://opencode.ai/docs/tui/#editor-setup)
  * [ Configure ](https://opencode.ai/docs/tui/#configure)
    * [ Options ](https://opencode.ai/docs/tui/#options)
  * [ Customization ](https://opencode.ai/docs/tui/#customization)


# TUI
Using the OpenCode terminal user interface.
OpenCode provides an interactive terminal interface or TUI for working on your projects with an LLM.
Running OpenCode starts the TUI for the current directory.
Terminal window```

opencode

```

Or you can start it for a specific working directory.
Terminal window```


opencode /path/to/project


```

Once you’re in the TUI, you can prompt it with a message.
```

Give me a quick summary of the codebase.

```

* * *
## [File references](https://opencode.ai/docs/tui/#file-references)
You can reference files in your messages using `@`. This does a fuzzy file search in the current working directory.
You can also use `@` to reference files in your messages.
```


How is auth handled in @packages/functions/src/api/index.ts?


```

The content of the file is added to the conversation automatically.
* * *
## [Bash commands](https://opencode.ai/docs/tui/#bash-commands)
Start a message with `!` to run a shell command.
```


!ls -la


```

The output of the command is added to the conversation as a tool result.
* * *
## [Commands](https://opencode.ai/docs/tui/#commands)
When using the OpenCode TUI, you can type `/` followed by a command name to quickly execute actions. For example:
```

/help

```

Most commands also have keybind using `ctrl+x` as the leader key, where `ctrl+x` is the default leader key. [Learn more](https://opencode.ai/docs/keybinds).
Here are all available slash commands:
* * *
### [connect](https://opencode.ai/docs/tui/#connect)
Add a provider to OpenCode. Allows you to select from available providers and add their API keys.
```

/connect

```

* * *
### [compact](https://opencode.ai/docs/tui/#compact)
Compact the current session. _Alias_ : `/summarize`
```

/compact

```

**Keybind:** `ctrl+x c`
* * *
### [details](https://opencode.ai/docs/tui/#details)
Toggle tool execution details.
```

/details

```

**Keybind:** `ctrl+x d`
* * *
### [editor](https://opencode.ai/docs/tui/#editor)
Open external editor for composing messages. Uses the editor set in your `EDITOR` environment variable. [Learn more](https://opencode.ai/docs/tui/#editor-setup).
```

/editor

```

**Keybind:** `ctrl+x e`
* * *
### [exit](https://opencode.ai/docs/tui/#exit)
Exit OpenCode. _Aliases_ : `/quit`, `/q`
```

/exit

```

**Keybind:** `ctrl+x q`
* * *
### [export](https://opencode.ai/docs/tui/#export)
Export current conversation to Markdown and open in your default editor. Uses the editor set in your `EDITOR` environment variable. [Learn more](https://opencode.ai/docs/tui/#editor-setup).
```

/export

```

**Keybind:** `ctrl+x x`
* * *
### [help](https://opencode.ai/docs/tui/#help)
Show the help dialog.
```

/help

```

**Keybind:** `ctrl+x h`
* * *
### [init](https://opencode.ai/docs/tui/#init)
Create or update `AGENTS.md` file. [Learn more](https://opencode.ai/docs/rules).
```

/init

```

**Keybind:** `ctrl+x i`
* * *
### [models](https://opencode.ai/docs/tui/#models)
List available models.
```

/models

```

**Keybind:** `ctrl+x m`
* * *
### [new](https://opencode.ai/docs/tui/#new)
Start a new session. _Alias_ : `/clear`
```

/new

```

**Keybind:** `ctrl+x n`
* * *
### [redo](https://opencode.ai/docs/tui/#redo)
Redo a previously undone message. Only available after using `/undo`.
Any file changes will also be restored.
Internally, this uses Git to manage the file changes. So your project **needs to be a Git repository**.
```

/redo

```

**Keybind:** `ctrl+x r`
* * *
### [sessions](https://opencode.ai/docs/tui/#sessions)
List and switch between sessions. _Aliases_ : `/resume`, `/continue`
```

/sessions

```

**Keybind:** `ctrl+x l`
* * *
### [share](https://opencode.ai/docs/tui/#share)
Share current session. [Learn more](https://opencode.ai/docs/share).
```

/share

```

**Keybind:** `ctrl+x s`
* * *
### [themes](https://opencode.ai/docs/tui/#themes)
List available themes.
```

/theme

```

**Keybind:** `ctrl+x t`
* * *
### [undo](https://opencode.ai/docs/tui/#undo)
Undo last message in the conversation. Removes the most recent user message, all subsequent responses, and any file changes.
Any file changes made will also be reverted.
Internally, this uses Git to manage the file changes. So your project **needs to be a Git repository**.
```

/undo

```

**Keybind:** `ctrl+x u`
* * *
### [unshare](https://opencode.ai/docs/tui/#unshare)
Unshare current session. [Learn more](https://opencode.ai/docs/share#un-sharing).
```

/unshare

```

* * *
## [Editor setup](https://opencode.ai/docs/tui/#editor-setup)
Both the `/editor` and `/export` commands use the editor specified in your `EDITOR` environment variable.
  * [ Linux/macOS ](https://opencode.ai/docs/tui/#tab-panel-4)
  * [ Windows (CMD) ](https://opencode.ai/docs/tui/#tab-panel-5)
  * [ Windows (PowerShell) ](https://opencode.ai/docs/tui/#tab-panel-6)


Terminal window```

# Example for nano or vim



export EDITOR=nano




export EDITOR=vim







# For GUI editors, VS Code, Cursor, VSCodium, Windsurf, Zed, etc.


# include --wait



export EDITOR="code --wait"


```

To make it permanent, add this to your shell profile; `~/.bashrc`, `~/.zshrc`, etc.
Terminal window```


set EDITOR=notepad







# For GUI editors, VS Code, Cursor, VSCodium, Windsurf, Zed, etc.


# include --wait



set EDITOR=code --wait


```

To make it permanent, use **System Properties** > **Environment Variables**.
Terminal window```


$env:EDITOR = "notepad"







# For GUI editors, VS Code, Cursor, VSCodium, Windsurf, Zed, etc.


# include --wait



$env:EDITOR = "code --wait"


```

To make it permanent, add this to your PowerShell profile.
Popular editor options include:
  * `code` - Visual Studio Code
  * `cursor` - Cursor
  * `windsurf` - Windsurf
  * `nvim` - Neovim editor
  * `vim` - Vim editor
  * `nano` - Nano editor
  * `notepad` - Windows Notepad
  * `subl` - Sublime Text


Some editors like VS Code need to be started with the `--wait` flag.
Some editors need command-line arguments to run in blocking mode. The `--wait` flag makes the editor process block until closed.
* * *
## [Configure](https://opencode.ai/docs/tui/#configure)
You can customize TUI behavior through your OpenCode config file.
opencode.json```

{



  "$schema": "https://opencode.ai/config.json",




  "tui": {




    "scroll_speed": 3,




    "scroll_acceleration": {




      "enabled": true




    }




  }



}

```

### [Options](https://opencode.ai/docs/tui/#options)
  * `scroll_acceleration` - Enable macOS-style scroll acceleration for smooth, natural scrolling. When enabled, scroll speed increases with rapid scrolling gestures and stays precise for slower movements. **This setting takes precedence over`scroll_speed` and overrides it when enabled.**
  * `scroll_speed` - Controls how fast the TUI scrolls when using scroll commands (minimum: `1`). Defaults to `1` on Unix and `3` on Windows. **Note: This is ignored if`scroll_acceleration.enabled` is set to `true`.**


* * *
## [Customization](https://opencode.ai/docs/tui/#customization)
You can customize various aspects of the TUI view using the command palette (`ctrl+x h` or `/help`). These settings persist across restarts.
* * *
#### [Username display](https://opencode.ai/docs/tui/#username-display)
Toggle whether your username appears in chat messages. Access this through:
  * Command palette: Search for “username” or “hide username”
  * The setting persists automatically and will be remembered across TUI sessions


[](https://github.com/sst/opencode/edit/dev/packages/web/src/content/docs/tui.mdx)[](https://github.com/sst/opencode/issues/new)[](https://opencode.ai/discord)
© [Anomaly](https://anoma.ly)
Dec 30, 2025
