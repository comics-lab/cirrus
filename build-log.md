### Node / Codex installation
- nodejs & npm installed via `apt` (Debian Trixie).
- Global npm prefix set to user: `npm config set prefix '~/.npm-global'`.
- Updated PATH: `export PATH=$HOME/.npm-global/bin:$PATH` (ensure present in ~/.bashrc or shell profile).
- Installed codex CLI: `npm install -g @openai/codex` → `codex-cli 0.87.0` verified with `codex --version`.
