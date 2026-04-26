# Publishing the PRD to Confluence

This is a quick reference for publishing the finished PRD via the Atlassian connector. The relevant tools live under `mcp__<atlassian-connector>__` — the names you'll likely see are:

- `getAccessibleAtlassianResources` — get the cloud ID for the user's Atlassian site
- `getConfluenceSpaces` — list spaces the user has access to
- `getPagesInConfluenceSpace` — find a parent page to nest under
- `createConfluencePage` — create the page
- `updateConfluencePage` — update a page if you're publishing a revised version

## Title convention

Default: `[PRD] <Feature Name>`

Examples:
- `[PRD] Upload step redesign`
- `[PRD] Calendar sync v2`

If the user's team has a different convention (e.g., they prefix with a date or a project code), follow theirs. Ask once, then remember.

## Body format

`createConfluencePage` accepts page content. Different connectors handle the format differently — some accept Markdown, some require Atlassian Document Format (ADF) or Confluence storage format (an XHTML variant). When in doubt:

1. Try sending the markdown directly first. Many modern Confluence connectors auto-convert.
2. If the page renders as a wall of unformatted text, the connector is likely expecting ADF or storage format. Convert the headings, lists, and emphasis using these mappings:

| Markdown | Storage format |
|---|---|
| `# Heading 1` | `<h1>Heading 1</h1>` |
| `## Heading 2` | `<h2>Heading 2</h2>` |
| `**bold**` | `<strong>bold</strong>` |
| `- item` (list) | `<ul><li>item</li></ul>` |
| `1. item` (numbered) | `<ol><li>item</li></ol>` |
| `[text](url)` | `<a href="url">text</a>` |
| ` ``` ` (code block) | `<ac:structured-macro ac:name="code">…</ac:structured-macro>` |
| Blockquote `>` | `<blockquote>…</blockquote>` |

Don't over-engineer this. A high-level PRD uses headings, paragraphs, lists, bold, and links — that's it. Fancy macros (status badges, info panels) are nice but optional.

## Picking a space and parent page

If the user names a space (e.g., "Product space"), call `getConfluenceSpaces` and match by name. If the match is ambiguous, show the user the candidates and let them pick.

For the parent page: ask the user for a page title or area (e.g., "under our PRDs page" or "in the Q2 planning area"). Use `getPagesInConfluenceSpace` to find it. If they don't specify, publish at the space root and mention that — they can move it later.

## After publishing

Return the Confluence URL to the user. Don't paraphrase the PRD content back to them — they can read it themselves. A short confirmation is enough:

> Published — [PRD] Upload step redesign: <link>
>
> Two things flagged in the doc as needing input: the success metric target and whether to support .tsv files in v1.
