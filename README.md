# 🛡️ SkillGuard Security Scanner

Automatically scans SKILL.md files for malicious instructions, data exfiltration patterns, and security vulnerabilities on every Pull Request.

## What it detects

- 🔍 **Static analysis**: Base64 encoded payloads, invisible Unicode characters, suspicious URLs, exfiltration patterns
- 🤖 **Semantic analysis**: Social engineering disguised as documentation, tool redirection, silencing instructions
- ☠️ **Real threats**: Credential theft, conversation exfiltration, safety bypass attempts

## Usage

Add this to your repository at `.github/workflows/skillguard.yml`:

    name: SkillGuard Security Scan

    on:
      pull_request:
        paths:
          - '**SKILL.md'
          - '**skill.md'

    jobs:
      scan:
        runs-on: ubuntu-latest
        permissions:
          pull-requests: write
          contents: read

        steps:
          - name: Checkout
            uses: actions/checkout@v4

          - name: Find changed SKILL.md files
            id: changed-files
            uses: tj-actions/changed-files@v44
            with:
              files: |
                **SKILL.md
                **skill.md

          - name: Set changed files env
            run: echo "CHANGED_FILES=${{ steps.changed-files.outputs.all_changed_files }}" >> $GITHUB_ENV

          - name: SkillGuard Scan
            uses: irefunky/skillguard-action@v1
            with:
              github-token: ${{ secrets.GITHUB_TOKEN }}

## Score guide

| Score | Veredicto | Action |
|-------|-----------|--------|
| 0 | ✅ LIMPIO | Safe to merge |
| 1-29 | ⚠️ BAJO RIESGO | Review recommended |
| 30-59 | 🚨 SOSPECHOSO | Manual review required |
| 60-100 | ☠️ ALTO RIESGO | Do not merge |

## Links

- 🌐 [SkillGuard Web Scanner](https://skillguard-frontend.vercel.app)