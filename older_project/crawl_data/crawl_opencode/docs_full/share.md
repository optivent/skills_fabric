[Skip to content](https://opencode.ai/docs/share/#_top)
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
  * [ Overview ](https://opencode.ai/docs/share/#_top)
  * [ How it works ](https://opencode.ai/docs/share/#how-it-works)
  * [ Sharing ](https://opencode.ai/docs/share/#sharing)
    * [ Manual (default) ](https://opencode.ai/docs/share/#manual-default)
    * [ Auto-share ](https://opencode.ai/docs/share/#auto-share)
    * [ Disabled ](https://opencode.ai/docs/share/#disabled)
  * [ Un-sharing ](https://opencode.ai/docs/share/#un-sharing)
  * [ Privacy ](https://opencode.ai/docs/share/#privacy)
    * [ Data retention ](https://opencode.ai/docs/share/#data-retention)
    * [ Recommendations ](https://opencode.ai/docs/share/#recommendations)
  * [ For enterprises ](https://opencode.ai/docs/share/#for-enterprises)


## On this page
  * [ Overview ](https://opencode.ai/docs/share/#_top)
  * [ How it works ](https://opencode.ai/docs/share/#how-it-works)
  * [ Sharing ](https://opencode.ai/docs/share/#sharing)
    * [ Manual (default) ](https://opencode.ai/docs/share/#manual-default)
    * [ Auto-share ](https://opencode.ai/docs/share/#auto-share)
    * [ Disabled ](https://opencode.ai/docs/share/#disabled)
  * [ Un-sharing ](https://opencode.ai/docs/share/#un-sharing)
  * [ Privacy ](https://opencode.ai/docs/share/#privacy)
    * [ Data retention ](https://opencode.ai/docs/share/#data-retention)
    * [ Recommendations ](https://opencode.ai/docs/share/#recommendations)
  * [ For enterprises ](https://opencode.ai/docs/share/#for-enterprises)


# Share
Share your OpenCode conversations.
OpenCode’s share feature allows you to create public links to your OpenCode conversations, so you can collaborate with teammates or get help from others.
Shared conversations are publicly accessible to anyone with the link.
* * *
## [How it works](https://opencode.ai/docs/share/#how-it-works)
When you share a conversation, OpenCode:
  1. Creates a unique public URL for your session
  2. Syncs your conversation history to our servers
  3. Makes the conversation accessible via the shareable link — `opncd.ai/s/<share-id>`


* * *
## [Sharing](https://opencode.ai/docs/share/#sharing)
OpenCode supports three sharing modes that control how conversations are shared:
* * *
### [Manual (default)](https://opencode.ai/docs/share/#manual-default)
By default, OpenCode uses manual sharing mode. Sessions are not shared automatically, but you can manually share them using the `/share` command:
```

/share

```

This will generate a unique URL that’ll be copied to your clipboard.
To explicitly set manual mode in your [config file](https://opencode.ai/docs/config):
opencode.json```

{



  "$schema": "https://opncd.ai/config.json",




  "share": "manual"



}

```

* * *
### [Auto-share](https://opencode.ai/docs/share/#auto-share)
You can enable automatic sharing for all new conversations by setting the `share` option to `"auto"` in your [config file](https://opencode.ai/docs/config):
opencode.json```

{



  "$schema": "https://opncd.ai/config.json",




  "share": "auto"



}

```

With auto-share enabled, every new conversation will automatically be shared and a link will be generated.
* * *
### [Disabled](https://opencode.ai/docs/share/#disabled)
You can disable sharing entirely by setting the `share` option to `"disabled"` in your [config file](https://opencode.ai/docs/config):
opencode.json```

{



  "$schema": "https://opncd.ai/config.json",




  "share": "disabled"



}

```

To enforce this across your team for a given project, add it to the `opencode.json` in your project and check into Git.
* * *
## [Un-sharing](https://opencode.ai/docs/share/#un-sharing)
To stop sharing a conversation and remove it from public access:
```

/unshare

```

This will remove the share link and delete the data related to the conversation.
* * *
## [Privacy](https://opencode.ai/docs/share/#privacy)
There are a few things to keep in mind when sharing a conversation.
* * *
### [Data retention](https://opencode.ai/docs/share/#data-retention)
Shared conversations remain accessible until you explicitly unshare them. This includes:
  * Full conversation history
  * All messages and responses
  * Session metadata


* * *
### [Recommendations](https://opencode.ai/docs/share/#recommendations)
  * Only share conversations that don’t contain sensitive information.
  * Review conversation content before sharing.
  * Unshare conversations when collaboration is complete.
  * Avoid sharing conversations with proprietary code or confidential data.
  * For sensitive projects, disable sharing entirely.


* * *
## [For enterprises](https://opencode.ai/docs/share/#for-enterprises)
For enterprise deployments, the share feature can be:
  * **Disabled** entirely for security compliance
  * **Restricted** to users authenticated through SSO only
  * **Self-hosted** on your own infrastructure


[Learn more](https://opencode.ai/docs/enterprise) about using opencode in your organization.
[](https://github.com/sst/opencode/edit/dev/packages/web/src/content/docs/share.mdx)[](https://github.com/sst/opencode/issues/new)[](https://opencode.ai/discord)
© [Anomaly](https://anoma.ly)
Dec 30, 2025
