# Setup Requirements

## PAT_TOKEN Secret

To enable automatic GitHub release creation when new typos versions are mirrored, you need to set up a Personal Access Token (PAT) as a repository secret.

### Why is PAT_TOKEN needed?

GitHub Actions has a security limitation where workflows triggered by events from other workflows using the default `GITHUB_TOKEN` do not trigger additional workflows. This prevents the release workflow from being triggered when the mirror workflow creates and pushes tags.

### Setting up PAT_TOKEN:

1. Go to GitHub Settings → Developer settings → Personal access tokens → Fine-grained tokens
2. Create a new token with the following permissions for this repository:
   - **Contents**: Write (to push commits and tags)
   - **Actions**: Write (to trigger other workflows)
   - **Metadata**: Read (required)
3. Copy the generated token
4. Go to your repository Settings → Secrets and variables → Actions
5. Add a new repository secret named `PAT_TOKEN` with the token value

### How it works:

- The `mirror.yml` workflow will use `PAT_TOKEN` if available, otherwise fall back to `GITHUB_TOKEN`
- When `PAT_TOKEN` is used, tag pushes will properly trigger the `release.yml` workflow
- The `release.yml` workflow will automatically create GitHub releases for new tags

Without the `PAT_TOKEN`, the mirror workflow will still work but releases will need to be created manually.