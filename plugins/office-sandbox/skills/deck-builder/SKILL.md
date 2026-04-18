---
name: deck-builder
description: "Generate a real PowerPoint deck (.pptx) from an outline using a curated template library. Picks a template (with thumbnail preview), fills slides via python-pptx in the sandbox container, and returns a download URL. Use when the user asks to 'build a deck', 'make slides about X', 'turn this into a presentation', 'render a PowerPoint'."
compatibility: "Requires the mcpcentral-office MCP server (auto-wired by the office-sandbox plugin)."
metadata:
  author: mcpcentral.io
  version: "1.0.0"
---

# deck-builder

Render a `.pptx` from an outline using one of the bundled PowerPoint templates and return a shareable download URL.

## Workflow

1. **Initialize** the container (`container_initialize`).
2. **Discover templates.** `container_template_categories` → `container_template_list` (optionally filtered by category).
3. **Pick a template.** If the user named one, use it. Otherwise pick based on tone (executive, creative, minimal, technical).
4. **Preview** with `container_template_preview(template_name)` — surface the thumbnail grid before committing if the user is undecided.
5. **Inspect layout slots.** `container_template_info(template_name)` returns theme colors, fonts, layouts, master elements. Use this to map outline sections → layout types.
6. **Build the deck.** Inside the container, use `python-pptx` (install if missing) to open the template and write slides. Save to `/tmp/<deck>.pptx`.
7. **Return a download URL.** `container_file_download_url("/tmp/<deck>.pptx")` → share with the user.

## Outline → Slides Mapping

The outline the user provides should map to layouts like this:

| Outline element | Suggested layout |
|---|---|
| Title (1 line) | Title slide |
| Section heading | Section header |
| Bulleted list (3-5 bullets) | Title + content |
| Compare/contrast (2 columns) | Two content |
| Image + caption | Picture with caption |
| Closing | Title slide (reused) |

If the outline doesn't fit any of these, fall back to "Title + content" and warn the user.

## Output Template

```
Template: <template_name>  (category: <cat>, theme: <colors/fonts>)
Slides:   N
Download: <download_url>

Slide-by-slide:
  1. <Title>           layout: Title slide
  2. <Section heading> layout: Section header
  3. <Bullets>         layout: Title + content
  ...
```

## Gotchas

- **`python-pptx` is not preinstalled.** `pip install python-pptx` in the container before running the build script.
- **Templates have specific layout indices.** `container_template_info` returns the available layouts; using a layout index that doesn't exist raises an exception. Always read the info before writing slides.
- **Don't hardcode theme colors.** The template defines theme colors — read them from `container_template_info` and use `MSO_THEME_COLOR` references in `python-pptx` so the deck stays on-brand if the template is later updated.
- **Image inserts need files in the container.** Upload images first via `container_file_write` (or `container_file_upload_url` for large binaries) — `python-pptx` reads from a path, not a URL.
- **Download URLs are signed and expire.** Don't paste a URL in chat without telling the user it has a TTL — they should download promptly.
- **One template at a time.** Picking a template mid-build (e.g. swapping after slide 3) doesn't carry slide content over cleanly. Decide first, then build.

## Examples

**User:** "Build me a 5-slide intro deck on reinforcement learning."
→ `container_template_list(category="executive")` → pick → `container_template_info` → write build script using python-pptx → return download URL.

**User:** "Make slides from this outline using the minimal template."
→ Skip discovery, jump straight to `container_template_info("minimal")` → build → return URL.
