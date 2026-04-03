---
name: article-saver
description: Organize saved articles, especially WeChat article links and pasted article content, into standardized Markdown notes under the local notes library. Use when Codex needs to classify articles, extract tags, create or update article notes from the local template, maintain the article index, or list/search/report on the existing article knowledge base.
---

# Article Saver

Follow this workflow:

1. Identify the requested outcome before acting.
2. Use `scripts/batch_processor.py` for `list`, `search`, and `stats` on the existing local library.
3. Read `config.json` before creating or updating notes so category paths and output rules stay consistent.
4. Read `templates/note-template.md` before generating note content.
5. If the user provides only URLs, prefer fetching article content when tooling is available and allowed.
6. If article content cannot be fetched in the current environment, do not claim full extraction. Ask for pasted content, or create a scaffold note only when the user explicitly wants a placeholder.
7. When article content is available, classify the note from both title and content. Use the config keywords as the baseline, then override the category if the article clearly belongs elsewhere.
8. Fill the template with concrete metadata. Keep unknown fields explicit instead of inventing facts.
9. Save notes into the configured category directory and update `data/index.json` when a new note is created.
10. Keep generated notes generic. Do not inject unrelated boilerplate, trend sections, or topic-specific material that is not grounded in the source article.

## Resources

- `config.json`: category keywords, output paths, and filename rules.
- `templates/note-template.md`: canonical note structure and placeholders.
- `scripts/batch_processor.py`: local helper CLI for `list`, `search`, and `stats`, plus note/index helper methods.
- `data/index.json`: article index used by local management commands.
- `data/example-urls.txt`: example input file for batch URL processing.

## Note Creation Rules

- Preserve the original source URL.
- Preserve author and publish date only when known.
- Keep the summary short and factual.
- Keep key points as concise bullets.
- Put unverified gaps into placeholders instead of fabricating content.
- Keep filenames short and filesystem-safe.
- Reuse existing index entries for duplicate URLs instead of creating silent duplicates.

## Validation

- After editing the template, config, or script, run `python -B skills/article-saver/scripts/batch_processor.py stats`.
- If you changed indexing or search-related behavior, also run `python -B skills/article-saver/scripts/batch_processor.py list` and `python -B skills/article-saver/scripts/batch_processor.py search Transformer`.
- If a validation command fails because of missing local dependencies or sandbox restrictions, report that clearly.
