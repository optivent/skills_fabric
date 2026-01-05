[Skip to content](https://opencode.ai/docs/permissions/#_top)
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
  * [ Overview ](https://opencode.ai/docs/permissions/#_top)
  * [ Tools ](https://opencode.ai/docs/permissions/#tools)
    * [ edit ](https://opencode.ai/docs/permissions/#edit)
    * [ bash ](https://opencode.ai/docs/permissions/#bash)
    * [ skill ](https://opencode.ai/docs/permissions/#skill)
    * [ webfetch ](https://opencode.ai/docs/permissions/#webfetch)
    * [ doom_loop ](https://opencode.ai/docs/permissions/#doom_loop)
    * [ external_directory ](https://opencode.ai/docs/permissions/#external_directory)
  * [ Agents ](https://opencode.ai/docs/permissions/#agents)


## On this page
  * [ Overview ](https://opencode.ai/docs/permissions/#_top)
  * [ Tools ](https://opencode.ai/docs/permissions/#tools)
    * [ edit ](https://opencode.ai/docs/permissions/#edit)
    * [ bash ](https://opencode.ai/docs/permissions/#bash)
    * [ skill ](https://opencode.ai/docs/permissions/#skill)
    * [ webfetch ](https://opencode.ai/docs/permissions/#webfetch)
    * [ doom_loop ](https://opencode.ai/docs/permissions/#doom_loop)
    * [ external_directory ](https://opencode.ai/docs/permissions/#external_directory)
  * [ Agents ](https://opencode.ai/docs/permissions/#agents)


# Permissions
Control which actions require approval to run.
By default, OpenCode allows most operations without approval, except `doom_loop` and `external_directory` which default to `ask`. You can configure this using the `permission` option.
opencode.json```

{



  "$schema": "https://opencode.ai/config.json",




  "permission": {




    "edit": "allow",




    "bash": "ask",




    "skill": "ask",




    "webfetch": "deny",




    "doom_loop": "ask",




    "external_directory": "ask"




  }



}

```

This lets you configure granular controls for the `edit`, `bash`, `skill`, `webfetch`, `doom_loop`, and `external_directory` tools.
  * `"ask"` — Prompt for approval before running the tool
  * `"allow"` — Allow all operations without approval
  * `"deny"` — Disable the tool


* * *
## [Tools](https://opencode.ai/docs/permissions/#tools)
Currently, the permissions for the `edit`, `bash`, `skill`, `webfetch`, `doom_loop`, and `external_directory` tools can be configured through the `permission` option.
* * *
### [edit](https://opencode.ai/docs/permissions/#edit)
Use the `permission.edit` key to control whether file editing operations require user approval.
opencode.json```

{



  "$schema": "https://opencode.ai/config.json",




  "permission": {




    "edit": "ask"




  }



}

```

* * *
### [bash](https://opencode.ai/docs/permissions/#bash)
You can use the `permission.bash` key to control whether bash commands as a whole need user approval.
opencode.json```

{



  "$schema": "https://opencode.ai/config.json",




  "permission": {




    "bash": "ask"




  }



}

```

Or, you can target specific commands and set it to `allow`, `ask`, or `deny`.
opencode.json```

{



  "$schema": "https://opencode.ai/config.json",




  "permission": {




    "bash": {




      "git push": "ask",




      "git status": "allow",




      "git diff": "allow",




      "npm run build": "allow",




      "ls": "allow",




      "pwd": "allow"




    }




  }



}

```

* * *
#### [Wildcards](https://opencode.ai/docs/permissions/#wildcards)
You can also use wildcards to manage permissions for specific bash commands.
You can use wildcards to manage permissions for specific bash commands.
For example, **disable all** Terraform commands.
opencode.json```

{



  "$schema": "https://opencode.ai/config.json",




  "permission": {




    "bash": {




      "terraform *": "deny"




    }




  }



}

```

You can also use the `*` wildcard to manage permissions for all commands. For example, **deny all commands** except a couple of specific ones.
opencode.json```

{



  "$schema": "https://opencode.ai/config.json",




  "permission": {




    "bash": {




      "*": "deny",




      "pwd": "allow",




      "git status": "ask"




    }




  }



}

```

Here a specific rule can override the `*` wildcard.
* * *
##### [Glob patterns](https://opencode.ai/docs/permissions/#glob-patterns)
The wildcard uses simple regex globbing patterns.
  * `*` matches zero or more of any character
  * `?` matches exactly one character
  * All other characters match literally


* * *
#### [Scope of the `"ask"` option](https://opencode.ai/docs/permissions/#scope-of-the-ask-option)
When the agent asks for permission to run a particular bash command, it will request feedback with the three options “accept”, “accept always” and “deny”. The “accept always” answer applies for the rest of the current session.
In addition, command permissions are applied to the first two elements of a command. So, an “accept always” response for a command like `git log` would whitelist `git log *` but not `git commit ...`.
When an agent asks for permission to run a command in a pipeline, we use tree sitter to parse each command in the pipeline. The “accept always” permission thus applies separately to each command in the pipeline.
* * *
### [skill](https://opencode.ai/docs/permissions/#skill)
Use the `permission.skill` key to control whether the model can load skills via the built-in `skill` tool.
You can apply a single rule to all skills:
opencode.json```

{



  "$schema": "https://opencode.ai/config.json",




  "permission": {




    "skill": "ask"




  }



}

```

Or configure per-skill rules (supports the same wildcard patterns as `permission.bash`):
opencode.json```

{



  "$schema": "https://opencode.ai/config.json",




  "permission": {




    "skill": {




      "*": "deny",




      "git-*": "allow",




      "frontend/*": "ask"




    }




  }



}

```

* * *
### [webfetch](https://opencode.ai/docs/permissions/#webfetch)
Use the `permission.webfetch` key to control whether the LLM can fetch web pages.
opencode.json```

{



  "$schema": "https://opencode.ai/config.json",




  "permission": {




    "webfetch": "ask"




  }



}

```

* * *
### [doom_loop](https://opencode.ai/docs/permissions/#doom_loop)
Use the `permission.doom_loop` key to control whether approval is required when a doom loop is detected. A doom loop occurs when the same tool is called 3 times in a row with identical arguments.
This helps prevent infinite loops where the LLM repeatedly attempts the same action without making progress.
opencode.json```

{



  "$schema": "https://opencode.ai/config.json",




  "permission": {




    "doom_loop": "ask"




  }



}

```

* * *
### [external_directory](https://opencode.ai/docs/permissions/#external_directory)
Use the `permission.external_directory` key to control whether file operations require approval when accessing files outside the working directory.
This provides an additional safety layer to prevent unintended modifications to files outside your project.
opencode.json```

{



  "$schema": "https://opencode.ai/config.json",




  "permission": {




    "external_directory": "ask"




  }



}

```

* * *
## [Agents](https://opencode.ai/docs/permissions/#agents)
You can also configure permissions per agent. Where the agent specific config overrides the global config. [Learn more](https://opencode.ai/docs/agents#permissions) about agent permissions.
opencode.json```

{



  "$schema": "https://opencode.ai/config.json",




  "permission": {




    "bash": {




      "git push": "ask"




    }




  },




  "agent": {




    "build": {




      "permission": {




        "bash": {




          "git push": "allow"




        }




      }




    }




  }



}

```

For example, here the `build` agent overrides the global `bash` permission to allow `git push` commands.
You can also configure permissions for agents in Markdown.
~/.config/opencode/agent/review.md```

---



description: Code review without edits




mode: subagent




permission:




  edit: deny




  bash: ask




  webfetch: deny



---






Only analyze code and suggest changes.

```

[](https://github.com/sst/opencode/edit/dev/packages/web/src/content/docs/permissions.mdx)[](https://github.com/sst/opencode/issues/new)[](https://opencode.ai/discord)
© [Anomaly](https://anoma.ly)
Dec 30, 2025
