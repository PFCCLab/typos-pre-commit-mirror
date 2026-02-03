# typos-pre-commit-mirror

Mirror of the `typos` pre-commit hook for `pre-commit`. Supports `pre-commit` versions 2.9.2 and later.

## Usage

Add this to your `.pre-commit-config.yaml`:

```yaml
- repo: https://github.com/PFCCLab/typos-pre-commit-mirror.git
  rev: v1.43.0
  hooks:
    - id: typos
      args: [--force-exclude]
```
