# Good first issues

Maintainers can apply `good first issue`, `help wanted`, `documentation`, `testing`,
`frontend` and `backend` labels. Starter issue specifications:

1. **Test S3 pagination and quoted keys** — add botocore stub tests for two listing
   pages, prefix handling and keys containing apostrophes. No live credentials.
2. **Improve empty-state guidance** — show the latest successful sync time and a
   clear empty-corpus prompt. Include a component test and keyboard navigation check.
3. **Add a model-enabled smoke suite** — behind the `models` marker, validate a tiny
   PDF and FastEmbed query with documented downloads and cache behavior.
4. **Write a restore drill** — reproduce a stopped-volume backup, restore into a fresh
   directory, and document count/query checks. No promises about live snapshots.

Keep PRs scoped; discuss expected behavior in the issue before starting larger work.
