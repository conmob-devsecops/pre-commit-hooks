pre-commit-hooks
================

Some out-of-the-box hooks for pre-commit, inspired by [pre-commit-hooks](https://github.com/pre-commit/pre-commit) and
[pre-commit](https://pre-commit.com/).

See also: https://github.com/conmob-devsecops/pre-commit-hooks

### Using pre-commit-hooks with pre-commit

Add this to your `.pre-commit-config.yaml`

```yaml
- repo: https://github.com/conmob-devsecops/pre-commit-hooks
  rev: v1.0.0  # Use the ref you want to point at
  hooks:
    - id: check-git-user-email
      args: [ "--allowed-domains", "example.net",  "example.com" ]
    - id: check-prohibited-filenames
      args: [ "--prohibited-names", "node_modules",  ".DS_Store" ]
      # or/and
      # args: [ "--prohibited-patterns", "*.log",  "temp/*", "**/.env" ]
      # or/and
      # args: [ "--prohibited-regex", ".*\\.log$",  "^temp/.*", ".*/\\.env$" ]
  # -   id: ...
```

### Hooks available

#### check-git-user-email

Check that the user is using an allowed domain for the `user.email` setting of `git`.

- Specify allowed domains with `args: ["--allowed-domains", "example.net",  "example.com"]`.

#### check-prohibited-filenames

Works similar to a `.gitignore` file, but provides feedback if any files with prohibited names are
added to the commit.

- Specify prohibited filenames with `args: ["--prohibited-names", "node_modules",  ".DS_Store"]`.
- Supports Shell-style patterns, e.g. `args: ["--prohibited-patterns", "*.log",  "temp/*", "**/.env"]`.
- Supports Python-style regex patterns, e.g. `args: ["--prohibited-regex", ".*\\.log$",  "^temp/.*", ".*/\\.env$"]`.
