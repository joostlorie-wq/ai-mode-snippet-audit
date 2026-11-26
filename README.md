# ai-mode-snippet-audit

Check whether the sentences on your page survive Google AI Mode's snippet selection: roughly the **first 160 characters** of a block.

Based on Dan Petrovic's analysis at DEJAN: [How AI Mode selects snippets](https://dejan.ai/blog/how-ai-mode-selects-snippets/) (May 2025).

## What the article observed

| # | Observation | Strength |
|---|---|---|
| 1 | A snippet is about 160 characters, cut with "…", but usually on a full sentence | Consistent observation |
| 2 | A short, already concise line is not truncated | Observation |
| 3 | A clear USP or value proposition gets picked more often | Observation |
| 4 | The brand name often appears first or prominently | Observation |
| 5 | Second person ("you", "your team") is common | Observation |
| 6 | High density of query-relevant terms | Observation |
| 7 | All page positions occur; slight lean to headings, intro and closing | Weak |
| 8 | H1 to H3, feature boxes, bullets and bold text are picked more often | Weak, semantic vs visual untested |

**Read this before you trust the numbers:** no sample size, no control group, an unexplained `metrics_array`, schema markup effect untested, and a single niche (custom football shirts). These are hypotheses, not laws. Present recommendations as "likely", not "proven", and verify on your own data.

## What the script does

```bash
python snippet_audit.py https://example.com/page --kw "work orders,field service" --brand Acme
```

It extracts headings, paragraphs, list items, summaries and bold text, takes the first 160 characters of each, and scores seven yes/no criteria:

1. **Standalone**: the first 160 characters form a complete, understandable sentence
2. **Concrete value**: a number, price, "without X" promise or immediate result
3. **Brand** present in or right next to the sentence
4. **Second person** address (NL/EN/DE patterns built in)
5. **Keyword coverage** of your target terms
6. **Structure**: sits in a heading, bullet, summary or bold element
7. **Key info before the cutoff**

Criteria 1 and 2 are regex approximations, so check outliers by hand. Criterion 6 scores on nearly every page: use it as a hygiene check, not a priority.

## Rewrite formula

`[Brand] + [concrete benefit or number] + [for whom / what]`, as one complete sentence, with the main message inside the first 160 characters. Repeat the core message in several places (heading, feature box, closing) with different wording. Use only verified facts.

## Measure it yourself

The article has no numbers of its own, so test it:
- Search Console: impressions on AI-feature queries for the page, before and after
- Run the same 3 to 5 prompts in AI Mode before and after, and note which text appears as the snippet
- Re-measure after 4 weeks, not 4 days

## Output you want

```
Page: <url> | language: xx
Summary: X of Y blocks score 5/7 or higher
Table: block | first 160 chars | score | what is missing
Top 5 rewrites: before → after (with character count)
Evidence note: one sentence on the limits of the source
```

## Related

[aeo-toolkit](https://github.com/joostlorie-wq/aeo-toolkit) covers structure-level checks (answer position, tables, entities, freshness). This repo covers the sentence level.
