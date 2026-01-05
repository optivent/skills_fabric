[Skip to content](https://opencode.ai/docs/network/#_top)
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
  * [ Overview ](https://opencode.ai/docs/network/#_top)
  * [ Proxy ](https://opencode.ai/docs/network/#proxy)
    * [ Authenticate ](https://opencode.ai/docs/network/#authenticate)
  * [ Custom certificates ](https://opencode.ai/docs/network/#custom-certificates)


## On this page
  * [ Overview ](https://opencode.ai/docs/network/#_top)
  * [ Proxy ](https://opencode.ai/docs/network/#proxy)
    * [ Authenticate ](https://opencode.ai/docs/network/#authenticate)
  * [ Custom certificates ](https://opencode.ai/docs/network/#custom-certificates)


# Network
Configure proxies and custom certificates.
OpenCode supports standard proxy environment variables and custom certificates for enterprise network environments.
* * *
## [Proxy](https://opencode.ai/docs/network/#proxy)
OpenCode respects standard proxy environment variables.
Terminal window```

# HTTPS proxy (recommended)



export HTTPS_PROXY=https://proxy.example.com:8080







# HTTP proxy (if HTTPS not available)



export HTTP_PROXY=http://proxy.example.com:8080







# Bypass proxy for local server (required)



export NO_PROXY=localhost,127.0.0.1


```

The TUI communicates with a local HTTP server. You must bypass the proxy for this connection to prevent routing loops.
You can configure the server’s port and hostname using [CLI flags](https://opencode.ai/docs/cli#run).
* * *
### [Authenticate](https://opencode.ai/docs/network/#authenticate)
If your proxy requires basic authentication, include credentials in the URL.
Terminal window```


export HTTPS_PROXY=http://username:password@proxy.example.com:8080


```

Avoid hardcoding passwords. Use environment variables or secure credential storage.
For proxies requiring advanced authentication like NTLM or Kerberos, consider using an LLM Gateway that supports your authentication method.
* * *
## [Custom certificates](https://opencode.ai/docs/network/#custom-certificates)
If your enterprise uses custom CAs for HTTPS connections, configure OpenCode to trust them.
Terminal window```


export NODE_EXTRA_CA_CERTS=/path/to/ca-cert.pem


```

This works for both proxy connections and direct API access.
[](https://github.com/sst/opencode/edit/dev/packages/web/src/content/docs/network.mdx)[](https://github.com/sst/opencode/issues/new)[](https://opencode.ai/discord)
© [Anomaly](https://anoma.ly)
Dec 30, 2025
