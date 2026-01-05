[Skip to content](https://opencode.ai/docs/formatters/#_top)
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
  * [ Overview ](https://opencode.ai/docs/formatters/#_top)
  * [ Built-in ](https://opencode.ai/docs/formatters/#built-in)
  * [ How it works ](https://opencode.ai/docs/formatters/#how-it-works)
  * [ Configure ](https://opencode.ai/docs/formatters/#configure)
    * [ Disabling formatters ](https://opencode.ai/docs/formatters/#disabling-formatters)
    * [ Custom formatters ](https://opencode.ai/docs/formatters/#custom-formatters)


## On this page
  * [ Overview ](https://opencode.ai/docs/formatters/#_top)
  * [ Built-in ](https://opencode.ai/docs/formatters/#built-in)
  * [ How it works ](https://opencode.ai/docs/formatters/#how-it-works)
  * [ Configure ](https://opencode.ai/docs/formatters/#configure)
    * [ Disabling formatters ](https://opencode.ai/docs/formatters/#disabling-formatters)
    * [ Custom formatters ](https://opencode.ai/docs/formatters/#custom-formatters)


# Formatters
OpenCode uses language specific formatters.
OpenCode automatically formats files after they are written or edited using language-specific formatters. This ensures that the code that is generated follows the code styles of your project.
* * *
## [Built-in](https://opencode.ai/docs/formatters/#built-in)
OpenCode comes with several built-in formatters for popular languages and frameworks. Below is a list of the formatters, supported file extensions, and commands or config options it needs.
Formatter | Extensions | Requirements  
---|---|---  
gofmt | .go |  `gofmt` command available  
mix | .ex, .exs, .eex, .heex, .leex, .neex, .sface |  `mix` command available  
prettier | .js, .jsx, .ts, .tsx, .html, .css, .md, .json, .yaml, and [more](https://prettier.io/docs/en/index.html) |  `prettier` dependency in `package.json`  
biome | .js, .jsx, .ts, .tsx, .html, .css, .md, .json, .yaml, and [more](https://biomejs.dev/) |  `biome.json(c)` config file  
zig | .zig, .zon |  `zig` command available  
clang-format | .c, .cpp, .h, .hpp, .ino, and [more](https://clang.llvm.org/docs/ClangFormat.html) |  `.clang-format` config file  
ktlint | .kt, .kts |  `ktlint` command available  
ruff | .py, .pyi |  `ruff` command available with config  
uv | .py, .pyi |  `uv` command available  
rubocop | .rb, .rake, .gemspec, .ru |  `rubocop` command available  
standardrb | .rb, .rake, .gemspec, .ru |  `standardrb` command available  
htmlbeautifier | .erb, .html.erb |  `htmlbeautifier` command available  
air | .R |  `air` command available  
dart | .dart |  `dart` command available  
ocamlformat | .ml, .mli |  `ocamlformat` command available and `.ocamlformat` config file  
terraform | .tf, .tfvars |  `terraform` command available  
gleam | .gleam |  `gleam` command available  
nixfmt | .nix |  `nixfmt` command available  
shfmt | .sh, .bash |  `shfmt` command available  
oxfmt (Experimental) | .js, .jsx, .ts, .tsx |  `oxfmt` dependency in `package.json` and an [experimental env variable flag](https://opencode.ai/docs/cli/#experimental)  
So if your project has `prettier` in your `package.json`, OpenCode will automatically use it.
* * *
## [How it works](https://opencode.ai/docs/formatters/#how-it-works)
When OpenCode writes or edits a file, it:
  1. Checks the file extension against all enabled formatters.
  2. Runs the appropriate formatter command on the file.
  3. Applies the formatting changes automatically.


This process happens in the background, ensuring your code styles are maintained without any manual steps.
* * *
## [Configure](https://opencode.ai/docs/formatters/#configure)
You can customize formatters through the `formatter` section in your OpenCode config.
opencode.json```

{



  "$schema": "https://opencode.ai/config.json",




  "formatter": {}



}

```

Each formatter configuration supports the following:
Property | Type | Description  
---|---|---  
`disabled` | boolean | Set this to `true` to disable the formatter  
`command` | string[] | The command to run for formatting  
`environment` | object | Environment variables to set when running the formatter  
`extensions` | string[] | File extensions this formatter should handle  
Let’s look at some examples.
* * *
### [Disabling formatters](https://opencode.ai/docs/formatters/#disabling-formatters)
To disable **all** formatters globally, set `formatter` to `false`:
opencode.json```

{



  "$schema": "https://opencode.ai/config.json",




  "formatter": false



}

```

To disable a **specific** formatter, set `disabled` to `true`:
opencode.json```

{



  "$schema": "https://opencode.ai/config.json",




  "formatter": {




    "prettier": {




      "disabled": true




    }




  }



}

```

* * *
### [Custom formatters](https://opencode.ai/docs/formatters/#custom-formatters)
You can override the built-in formatters or add new ones by specifying the command, environment variables, and file extensions:
opencode.json```

{



  "$schema": "https://opencode.ai/config.json",




  "formatter": {




    "prettier": {




      "command": ["npx", "prettier", "--write", "$FILE"],




      "environment": {




        "NODE_ENV": "development"




      },




      "extensions": [".js", ".ts", ".jsx", ".tsx"]




    },




    "custom-markdown-formatter": {




      "command": ["deno", "fmt", "$FILE"],




      "extensions": [".md"]




    }




  }



}

```

The **`$FILE`placeholder** in the command will be replaced with the path to the file being formatted.
[](https://github.com/sst/opencode/edit/dev/packages/web/src/content/docs/formatters.mdx)[](https://github.com/sst/opencode/issues/new)[](https://opencode.ai/discord)
© [Anomaly](https://anoma.ly)
Dec 30, 2025
