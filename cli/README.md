# PromptForge CLI

Pull PromptForge **starter kits** (full codebases) and **prompts** straight into your terminal.

## Install

```bash
pip install -e .          # from this folder (cli/)
# or, once published:
# pip install promptforge-cli
```

This adds a `promptforge` command.

## Log in

Create an API key in the app (**Settings → API keys**), then:

```bash
promptforge login
# PromptForge API URL [https://promptforge.fastapicloud.dev]:
# API key (Settings → API keys): ****
```

Your key is saved to `~/.promptforge/config.json` (chmod 600 on POSIX). You can also
skip the file entirely with env vars:

```bash
export PROMPTFORGE_API_URL="https://promptforge.fastapicloud.dev"
export PROMPTFORGE_API_KEY="pf_..."
```

## Commands

```bash
promptforge whoami                       # verify your key

promptforge kits list                    # browse starter kits
promptforge kits list -c ecommerce       # filter by category
promptforge kits pull <KIT_ID>           # download a kit into ./<slug>
promptforge kits pull <KIT_ID> -d myapp  # ...into ./myapp
promptforge kits pull <KIT_ID> --ref v2  # pin a branch/tag/commit

promptforge prompts search "stripe checkout"
promptforge prompts get <PROMPT_ID>      # print full prompt content
```

`kits pull` downloads the codebase (streamed through PromptForge, so the source
repo stays private-to-you infrastructure), unpacks it into your folder, and writes
a `PROMPTFORGE.md` listing the prompts behind the kit — fetch any with
`promptforge prompts get <id>`.

## Notes

- Access is **read-only** and limited to published, public prompts/kits.
- The public API is rate limited; the CLI surfaces a friendly message with a
  retry hint if you hit it.
