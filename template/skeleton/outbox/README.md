# Outbox

Directives waiting to go to the public hub. One TOML file per directive, `d-YYYYMMDD-n.toml`:

```toml
id = "d-20261018-1"
directive = "Pause the weekly digest until further notice."   # at most 280 characters, no reasons
scope = ["all"]                                                # or family ids from the hub's family.yaml
pause = ["kb-curator"]                                         # optional, names from hub.toml
until = "2026-11-01"                                           # optional
status = "queued"                                              # queued, then sent or cancelled
```

- Write one only when the person has said yes to the directive.
- Run `python3 scripts/outbox_check.py` before committing. It refuses reasons, links, note names,
  private names and more than three queued entries.
- A scheduled Claude session (or the person, by hand) opens each queued directive as a pull request
  in the hub, and marks it `sent` with the PR number. It acts only when the hub's owner merges it.
- Nothing in this repo writes to a public repo by itself: there is no token for it here.
