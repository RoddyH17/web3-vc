# Contributing to web3-vc

This plugin follows the [Claude Code plugin architecture](https://docs.claude.com/). The structure intentionally mirrors `anthropics/financial-services` so future contributors familiar with that codebase can navigate immediately.

## Adding a new skill

A skill is a directory under `skills/` containing a single `SKILL.md` file.

1. Create `skills/<skill-name>/SKILL.md`
2. The file must start with YAML frontmatter:

   ```yaml
   ---
   name: <skill-name>
   description: <one-paragraph description with trigger keywords>
   ---
   ```

   Triggers in the description are what Claude uses to decide when to load the skill. Be specific.

3. The body is markdown — workflow steps, methodology, output format, important notes, failure modes.

4. Match the upstream pattern: `## Workflow` with numbered steps, `## Important Notes`, `## Failure modes` if applicable.

5. Add a corresponding command in `commands/<command-name>.md`:

   ```markdown
   ---
   description: <short description shown in the slash-command picker>
   argument-hint: "[expected argument format]"
   ---

   Load the `<skill-name>` skill and ...
   ```

## Adding a new connector

A connector is an MCP server, either hosted (HTTP) or local (stdio).

### Hosted MCP (preferred when available)

Add an entry to `.mcp.json`:

```json
{
  "mcpServers": {
    "<name>": {
      "type": "http",
      "url": "https://..."
    }
  }
}
```

### Local stdio MCP (e.g., wrapping a free REST API)

1. Create `connectors/<name>/` with a `pyproject.toml`, `src/<name>_mcp/`, `tests/`, and `README.md`
2. Implement the server using `mcp.server.fastmcp.FastMCP` — see `connectors/defillama/` for the canonical pattern
3. Add to `.mcp.json`:

   ```json
   {
     "mcpServers": {
       "<name>": {
         "command": "uv",
         "args": [
           "--directory",
           "${CLAUDE_PLUGIN_ROOT}/connectors/<name>",
           "run",
           "python",
           "-m",
           "<name>_mcp.server"
         ]
       }
     }
   }
   ```

4. Write at least one integration test against the live API. Mark it `@pytest.mark.integration` so it's skippable in CI.

## Design principles (non-negotiable)

These are the principles that distinguish this plugin from a generic "AI does VC research" tool. Future contributions should respect them or be rejected:

1. **Skills produce data, not opinions.** No skill outputs "buy", "pass", "bullish", "bearish", or position-sizing recommendations.
2. **Data provenance is mandatory.** Every output includes the pull timestamp and source URL.
3. **Explicit gaps over false comprehensiveness.** When a connector can't answer something, the output says so — never silently substitute.
4. **Phase 0 must work end-to-end with $0 budget.** Premium API connectors are Phase 2, not Phase 0.
5. **The human owns the thesis.** The `/thesis` skill is explicitly composition + stress-test, not generation.

## Issues, PRs

Open as you would any GitHub repo. Be honest about what works and what doesn't.
