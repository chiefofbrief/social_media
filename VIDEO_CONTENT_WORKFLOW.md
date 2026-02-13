# Video Content Workflow

**Goal**: Transform Daily Digest insights into TikTok videos discussing financial news.

---

## Overview

This workflow takes the Daily Digest (daily financial/market analysis) and produces short-form TikTok video content. Each session produces one video in one of two formats:

* **Single Story** — One topic explored in depth (up to 60 seconds)
* **Quick Hits** — 3-5 stories delivered as rapid-fire segments (up to 60 seconds total)

The Daily Digest replaces the topic research phase—stories are already sourced, analyzed, and contextualized. The workflow focuses on selection, scripting, and visual production.

---

## Pipeline

```
Daily Digest → Story Selection → Script → Visuals → Production
```

### Step 1: Story Selection

Review the day's digest and select stories based on viral potential — which stories trigger the strongest emotions, have the most striking data, or will make someone stop scrolling?

**Decisions at this step:**
* Which stories have the strongest hooks?
* Single story deep-dive or quick hits?
* If quick hits: themed collection or best-of mix?

### Step 2: Script

Write narration optimized for spoken delivery in the chosen format.

* **Single story**: Hook → setup → reveal → impact (~45-60 seconds)
* **Quick hits**: Intro hook → story blocks (2-4 sentences each) → closer (~45-60 seconds)

Key principle: entertaining first, educational second. Conversational tone, specific figures, cut anything that doesn't support the hook.

### Step 3: Visuals

Break the script into scenes, create image and video prompts for AI generation.

* Establish visual style for the video
* Scene descriptions with subject, action, environment, atmosphere
* Identify which scenes benefit from AI video vs. static images
* Generate image prompts (all scenes) and video prompts (selected scenes)

### Step 4: Production

Generate images/videos from prompts, assemble in video editor, add captions, and publish. This step happens outside of the AI session.

---

## Session Prompt

Use `video/TikTok_Financial_News_Prompt.md` as the system prompt for AI content sessions. It contains the detailed instructions for each workflow step.

---

## Reference Files

| File | Purpose |
|------|---------|
| `video/TikTok_Financial_News_Prompt.md` | System prompt for AI content sessions |
| `General_Characteristics_of_Viral_Content.md` | Viral framework — primary guide for story selection |
| `video/Characteristics_of_Viral_Short-Form_Videos` | Video-specific viral patterns and platform approaches |
| `video/Characteristics_of_'News-Related'_Short-Form_AI_Videos` | AI video production techniques |
| `peters_digest/Daily_Digest_*.md` | Daily source material |

---

## Relationship to Other Workflows

* **`VIRAL_CONTENT_WORKFLOW.md`** — Text-based viral content for Reddit and X/Threads. Uses Perigon API for research and produces written posts.
* **This workflow** — Video content for TikTok. Uses the Daily Digest as source material and produces narrated video with AI-generated visuals.

Both workflows share the same account mission, viral content framework, and general characteristics documents.
