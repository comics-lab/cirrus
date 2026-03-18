# Resume Checklist

## Minimum Handoff Items

- current branch and repo state if code or docs changed
- current host state if system changes were made
- exact next recommended work
- exact first checks for the next session

## Reboot Watch Triggers

Add a reboot-watch section when any of these are true:
- storage mount behavior was unstable
- network behavior changed
- login/session behavior changed
- suspend or power policy changed
- a CLI/tool path issue was fixed and should be rechecked after restart

## Good Restart Checks

Examples:

- `findmnt /mnt/phoenix`
- `ip -br addr`
- `getent hosts cirrus.local`
- `command -v codex`
- `codex --version`
- `loginctl list-sessions`
- `systemctl --failed --no-pager`
