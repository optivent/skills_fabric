[Skip to content](https://opencode.ai/docs/troubleshooting/#_top)
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
  * [ Overview ](https://opencode.ai/docs/troubleshooting/#_top)
    * [ Logs ](https://opencode.ai/docs/troubleshooting/#logs)
    * [ Storage ](https://opencode.ai/docs/troubleshooting/#storage)
  * [ Getting help ](https://opencode.ai/docs/troubleshooting/#getting-help)
  * [ Common issues ](https://opencode.ai/docs/troubleshooting/#common-issues)
    * [ OpenCode won’t start ](https://opencode.ai/docs/troubleshooting/#opencode-wont-start)
    * [ Authentication issues ](https://opencode.ai/docs/troubleshooting/#authentication-issues)
    * [ Model not available ](https://opencode.ai/docs/troubleshooting/#model-not-available)
    * [ ProviderInitError ](https://opencode.ai/docs/troubleshooting/#provideriniterror)
    * [ AI_APICallError and provider package issues ](https://opencode.ai/docs/troubleshooting/#ai_apicallerror-and-provider-package-issues)
    * [ Copy/paste not working on Linux ](https://opencode.ai/docs/troubleshooting/#copypaste-not-working-on-linux)


## On this page
  * [ Overview ](https://opencode.ai/docs/troubleshooting/#_top)
    * [ Logs ](https://opencode.ai/docs/troubleshooting/#logs)
    * [ Storage ](https://opencode.ai/docs/troubleshooting/#storage)
  * [ Getting help ](https://opencode.ai/docs/troubleshooting/#getting-help)
  * [ Common issues ](https://opencode.ai/docs/troubleshooting/#common-issues)
    * [ OpenCode won’t start ](https://opencode.ai/docs/troubleshooting/#opencode-wont-start)
    * [ Authentication issues ](https://opencode.ai/docs/troubleshooting/#authentication-issues)
    * [ Model not available ](https://opencode.ai/docs/troubleshooting/#model-not-available)
    * [ ProviderInitError ](https://opencode.ai/docs/troubleshooting/#provideriniterror)
    * [ AI_APICallError and provider package issues ](https://opencode.ai/docs/troubleshooting/#ai_apicallerror-and-provider-package-issues)
    * [ Copy/paste not working on Linux ](https://opencode.ai/docs/troubleshooting/#copypaste-not-working-on-linux)


# Troubleshooting
Common issues and how to resolve them.
To debug any issues with OpenCode, you can check the logs or the session data that it stores locally.
* * *
### [Logs](https://opencode.ai/docs/troubleshooting/#logs)
Log files are written to:
  * **macOS/Linux** : `~/.local/share/opencode/log/`
  * **Windows** : `%USERPROFILE%\.local\share\opencode\log\`


Log files are named with timestamps (e.g., `2025-01-09T123456.log`) and the most recent 10 log files are kept.
You can set the log level with the `--log-level` command-line option to get more detailed debug information. For example, `opencode --log-level DEBUG`.
* * *
### [Storage](https://opencode.ai/docs/troubleshooting/#storage)
opencode stores session data and other application data on disk at:
  * **macOS/Linux** : `~/.local/share/opencode/`
  * **Windows** : `%USERPROFILE%\.local\share\opencode`


This directory contains:
  * `auth.json` - Authentication data like API keys, OAuth tokens
  * `log/` - Application logs
  * `project/` - Project-specific data like session and message data 
    * If the project is within a Git repo, it is stored in `./<project-slug>/storage/`
    * If it is not a Git repo, it is stored in `./global/storage/`


* * *
## [Getting help](https://opencode.ai/docs/troubleshooting/#getting-help)
If you’re experiencing issues with OpenCode:
  1. **Report issues on GitHub**
The best way to report bugs or request features is through our GitHub repository:
[**github.com/sst/opencode/issues**](https://github.com/sst/opencode/issues)
Before creating a new issue, search existing issues to see if your problem has already been reported.
  2. **Join our Discord**
For real-time help and community discussion, join our Discord server:
[**opencode.ai/discord**](https://opencode.ai/discord)


* * *
## [Common issues](https://opencode.ai/docs/troubleshooting/#common-issues)
Here are some common issues and how to resolve them.
* * *
### [OpenCode won’t start](https://opencode.ai/docs/troubleshooting/#opencode-wont-start)
  1. Check the logs for error messages
  2. Try running with `--print-logs` to see output in the terminal
  3. Ensure you have the latest version with `opencode upgrade`


* * *
### [Authentication issues](https://opencode.ai/docs/troubleshooting/#authentication-issues)
  1. Try re-authenticating with the `/connect` command in the TUI
  2. Check that your API keys are valid
  3. Ensure your network allows connections to the provider’s API


* * *
### [Model not available](https://opencode.ai/docs/troubleshooting/#model-not-available)
  1. Check that you’ve authenticated with the provider
  2. Verify the model name in your config is correct
  3. Some models may require specific access or subscriptions


If you encounter `ProviderModelNotFoundError` you are most likely incorrectly referencing a model somewhere. Models should be referenced like so: `<providerId>/<modelId>`
Examples:
  * `openai/gpt-4.1`
  * `openrouter/google/gemini-2.5-flash`
  * `opencode/kimi-k2`


To figure out what models you have access to, run `opencode models`
* * *
### [ProviderInitError](https://opencode.ai/docs/troubleshooting/#provideriniterror)
If you encounter a ProviderInitError, you likely have an invalid or corrupted configuration.
To resolve this:
  1. First, verify your provider is set up correctly by following the [providers guide](https://opencode.ai/docs/providers)
  2. If the issue persists, try clearing your stored configuration:
Terminal window```


rm -rf ~/.local/share/opencode


```

  3. Re-authenticate with your provider using the `/connect` command in the TUI.


* * *
### [AI_APICallError and provider package issues](https://opencode.ai/docs/troubleshooting/#ai_apicallerror-and-provider-package-issues)
If you encounter API call errors, this may be due to outdated provider packages. opencode dynamically installs provider packages (OpenAI, Anthropic, Google, etc.) as needed and caches them locally.
To resolve provider package issues:
  1. Clear the provider package cache:
Terminal window```


rm -rf ~/.cache/opencode


```

  2. Restart opencode to reinstall the latest provider packages


This will force opencode to download the most recent versions of provider packages, which often resolves compatibility issues with model parameters and API changes.
* * *
### [Copy/paste not working on Linux](https://opencode.ai/docs/troubleshooting/#copypaste-not-working-on-linux)
Linux users need to have one of the following clipboard utilities installed for copy/paste functionality to work:
**For X11 systems:**
Terminal window```


apt install -y xclip



# or



apt install -y xsel


```

**For Wayland systems:**
Terminal window```


apt install -y wl-clipboard


```

**For headless environments:**
Terminal window```


apt install -y xvfb



# and run:



Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &




export DISPLAY=:99.0


```

opencode will detect if you’re using Wayland and prefer `wl-clipboard`, otherwise it will try to find clipboard tools in order of: `xclip` and `xsel`.
[](https://github.com/sst/opencode/edit/dev/packages/web/src/content/docs/troubleshooting.mdx)[](https://github.com/sst/opencode/issues/new)[](https://opencode.ai/discord)
© [Anomaly](https://anoma.ly)
Dec 30, 2025
