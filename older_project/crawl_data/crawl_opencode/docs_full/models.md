[Skip to content](https://opencode.ai/docs/models/#_top)
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
  * [ Overview ](https://opencode.ai/docs/models/#_top)
  * [ Providers ](https://opencode.ai/docs/models/#providers)
  * [ Select a model ](https://opencode.ai/docs/models/#select-a-model)
  * [ Recommended models ](https://opencode.ai/docs/models/#recommended-models)
  * [ Set a default ](https://opencode.ai/docs/models/#set-a-default)
  * [ Configure models ](https://opencode.ai/docs/models/#configure-models)
  * [ Loading models ](https://opencode.ai/docs/models/#loading-models)


## On this page
  * [ Overview ](https://opencode.ai/docs/models/#_top)
  * [ Providers ](https://opencode.ai/docs/models/#providers)
  * [ Select a model ](https://opencode.ai/docs/models/#select-a-model)
  * [ Recommended models ](https://opencode.ai/docs/models/#recommended-models)
  * [ Set a default ](https://opencode.ai/docs/models/#set-a-default)
  * [ Configure models ](https://opencode.ai/docs/models/#configure-models)
  * [ Loading models ](https://opencode.ai/docs/models/#loading-models)


# Models
Configuring an LLM provider and model.
OpenCode uses the [AI SDK](https://ai-sdk.dev/) and [Models.dev](https://models.dev) to support for **75+ LLM providers** and it supports running local models.
* * *
## [Providers](https://opencode.ai/docs/models/#providers)
Most popular providers are preloaded by default. If you’ve added the credentials for a provider through the `/connect` command, they’ll be available when you start OpenCode.
Learn more about [providers](https://opencode.ai/docs/providers).
* * *
## [Select a model](https://opencode.ai/docs/models/#select-a-model)
Once you’ve configured your provider you can select the model you want by typing in:
```

/models

```

* * *
## [Recommended models](https://opencode.ai/docs/models/#recommended-models)
There are a lot of models out there, with new models coming out every week.
Consider using one of the models we recommend.
However, there are only a few of them that are good at both generating code and tool calling.
Here are several models that work well with OpenCode, in no particular order. (This is not an exhaustive list):
  * GPT 5.1
  * GPT 5.1 Codex
  * Claude Sonnet 4.5
  * Claude Haiku 4.5
  * Kimi K2
  * GLM 4.6
  * Qwen3 Coder
  * Gemini 3 Pro


* * *
## [Set a default](https://opencode.ai/docs/models/#set-a-default)
To set one of these as the default model, you can set the `model` key in your OpenCode config.
opencode.json```

{



  "$schema": "https://opencode.ai/config.json",




  "model": "lmstudio/google/gemma-3n-e4b"



}

```

Here the full ID is `provider_id/model_id`. For example, if you’re using [OpenCode Zen](https://opencode.ai/docs/zen), you would use `opencode/gpt-5.1-codex` for GPT 5.1 Codex.
If you’ve configured a [custom provider](https://opencode.ai/docs/providers#custom), the `provider_id` is key from the `provider` part of your config, and the `model_id` is the key from `provider.models`.
* * *
## [Configure models](https://opencode.ai/docs/models/#configure-models)
You can globally configure a model’s options through the config.
opencode.jsonc```

{



  "$schema": "https://opencode.ai/config.json",




  "provider": {




    "openai": {




      "models": {




        "gpt-5": {




          "options": {




            "reasoningEffort": "high",




            "textVerbosity": "low",




            "reasoningSummary": "auto",




            "include": ["reasoning.encrypted_content"],




          },




        },




      },




    },




    "anthropic": {




      "models": {




        "claude-sonnet-4-5-20250929": {




          "options": {




            "thinking": {




              "type": "enabled",




              "budgetTokens": 16000,




            },




          },




        },




      },




    },




  },



}

```

Here we’re configuring global settings for two built-in models: `gpt-5` when accessed via the `openai` provider, and `claude-sonnet-4-20250514` when accessed via the `anthropic` provider. The built-in provider and model names can be found on [Models.dev](https://models.dev).
You can also configure these options for any agents that you are using. The agent config overrides any global options here. [Learn more](https://opencode.ai/docs/agents/#additional).
You can also define custom models that extend built-in ones and can optionally use specific options by referring to their id:
opencode.jsonc```

{



  "$schema": "https://opencode.ai/config.json",




  "provider": {




    "opencode": {




      "models": {




        "gpt-5-high": {




          "id": "gpt-5",




          "name": "MyGPT5 (High Reasoning)",




          "options": {




            "reasoningEffort": "high",




            "textVerbosity": "low",




            "reasoningSummary": "auto",




          },




        },




        "gpt-5-low": {




          "id": "gpt-5",




          "name": "MyGPT5 (Low Reasoning)",




          "options": {




            "reasoningEffort": "low",




            "textVerbosity": "low",




            "reasoningSummary": "auto",




          },




        },




      },




    },




  },



}

```

* * *
## [Loading models](https://opencode.ai/docs/models/#loading-models)
When OpenCode starts up, it checks for models in the following priority order:
  1. The `--model` or `-m` command line flag. The format is the same as in the config file: `provider_id/model_id`.
  2. The model list in the OpenCode config.
opencode.json```

{



  "$schema": "https://opencode.ai/config.json",




  "model": "anthropic/claude-sonnet-4-20250514"



}

```

The format here is `provider/model`.
  3. The last used model.
  4. The first model using an internal priority.


[](https://github.com/sst/opencode/edit/dev/packages/web/src/content/docs/models.mdx)[](https://github.com/sst/opencode/issues/new)[](https://opencode.ai/discord)
© [Anomaly](https://anoma.ly)
Dec 30, 2025
