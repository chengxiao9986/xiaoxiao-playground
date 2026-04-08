---
name: english-learner
description: Automatically organize English learning materials from conversations into structured markdown files. Use this skill whenever the user asks for translation, English help, meeting preparation in English, or mentions learning English vocabulary/expressions. Also trigger when the user asks to save or organize English learning content from the current conversation.
---

# English Learner

This skill helps organize English learning materials from conversations into a structured knowledge base following the user's existing format in the `English/` folder.

## When to Use

Trigger this skill when the user:
- Asks for translation (e.g., "translate this paragraph", "how do I say X in English")
- Requests help preparing for English meetings or presentations
- Asks about English vocabulary, expressions, or grammar
- Explicitly asks to organize or save English learning materials
- Wants to create learning resources from the current conversation

## Output Structure

The English learning system consists of:

```
English/
├── vocabulary.md          # Consolidated vocabulary bank by category
├── expressions.md         # Reusable expression patterns with examples
├── daily/                 # Daily learning logs
│   └── YYYY-MM-DD.md
└── meeting/               # Meeting preparation materials
    └── YYYY-MM-DD-topic.md
```

## Core Tasks

### 1. Extract Learning Materials

From the conversation, identify and extract:
- **New vocabulary**: words, pronunciation, meaning, context/collocation
- **Useful expressions**: sentence patterns with grammar notes and examples
- **Meeting content**: scripts, slides structure, speaking notes
- **Real examples**: actual sentences from the conversation showing usage

### 2. Create Daily Log (for general learning)

When the user requests translation or English help for general content (not meeting-specific), create or append to `English/daily/YYYY-MM-DD.md`:

**Format:**
```markdown
# YYYY-MM-DD | [Topic/Context]

> Source: [where the content came from]

## New Words

| Word | Pronunciation | Meaning | Context |
|------|--------------|---------|---------|
| word | /pronunciation/ | 中文释义 | example usage |

## Key Sentences

**1.** "The original English sentence."
- 中文翻译
- **Grammar point** explanation; **key structure** explanation

## Useful Patterns

| Pattern | Template | Example |
|---------|----------|---------|
| 用途描述 | [Template structure] | Real example |
```

### 3. Create Meeting Preparation File

When the user asks to prepare for a meeting or presentation, create `English/meeting/YYYY-MM-DD-topic.md`:

**Format:**
```markdown
# [Meeting Name] | YYYY-MM-DD

## Project/Topic Name

### PPT Slides

**[Slide Title] — Status: [Status]**

- Key point 1
- Key point 2

### Speaking Script

> [Full speaking script in English with natural flow]

---

## Learning Notes

### New Words

| Word | Pronunciation | Meaning | Context |
|------|--------------|---------|---------|
| word | /pronunciation/ | 中文释义 | usage from the script |

### Key Takeaways

- **Expression** 中文解释 — usage note
```

### 4. Update Consolidated Banks

After creating daily/meeting files, update the consolidated reference files:

**vocabulary.md**: Add new words under appropriate category headers (e.g., `## #settings`, `## #meeting`). Use existing categories or create new ones with `## #category-name` format.

**Format:**
```markdown
| Word | Pronunciation | Meaning | Collocation |
|------|--------------|---------|-------------|
| word | /pronunciation/ | 中文释义 | key collocation example |
```

**expressions.md**: Add new expression patterns under appropriate section (e.g., `## #reading | 阅读场景`, `## #meeting | 会议场景`).

**Format:**
```markdown
### [Pattern Template]
用途描述

- "Real example sentence from conversation."
- Grammar: [grammar explanation]
- Source: YYYY-MM-DD[-optional-context]
```

## Quality Guidelines

### Vocabulary Extraction
- Include IPA pronunciation (use //) for all new words
- Provide Chinese translation that fits the specific context
- For "Context" or "Collocation", use the actual phrase from conversation, not invented examples
- Categorize by topic/scenario (settings, meeting, technical, etc.)

### Expression Patterns
- Extract **reusable** patterns, not one-off sentences
- Template should use [brackets] for variable parts
- Include grammar notes explaining why the structure works
- Always include the source date and optional context
- Add 中文说明 for the pattern's purpose
- Organize by scenario tags (#reading, #meeting, #writing, etc.)

### Meeting Scripts
- Scripts should sound natural and conversational, not robotic
- Include Chinese translation or key takeaways for difficult phrases
- Structure by project/topic with clear sections
- Add a Learning Notes section at the end with vocabulary and key expressions from the script

### File Organization
- Use ISO date format: YYYY-MM-DD
- For meetings, include topic in filename: `YYYY-MM-DD-topic.md`
- Always include a source line at the top indicating where content came from
- Keep table formatting clean and aligned

## Workflow

1. **Identify the request type**:
   - Translation/general learning → create daily log
   - Meeting preparation → create meeting file
   - Just organizing existing materials → update consolidated banks

2. **Extract materials** from the conversation:
   - Scan for new vocabulary
   - Identify useful sentence patterns
   - Note grammar points
   - Capture real examples

3. **Create the primary file** (daily or meeting):
   - Use proper formatting
   - Include all extracted materials
   - Add source attribution

4. **Update consolidated banks**:
   - Check if category exists in vocabulary.md/expressions.md
   - Add new entries under appropriate headers
   - Maintain alphabetical order within categories where it makes sense

5. **Confirm with user**: Show what was created and ask if they want any adjustments.

## Examples

### Example 1: General Translation Request

**User:** "Translate 'incremental import' and explain what it means in the context of data synchronization"

**Action:**
- Create `English/daily/2026-04-02.md` with vocabulary entry for "incremental"
- Add to vocabulary.md under `## #technical` category
- Extract the explanation as a key sentence if it's a useful pattern

### Example 2: Meeting Preparation

**User:** "Help me prepare for tomorrow's shiproom meeting. I need to talk about the World Cup campaign progress."

**Action:**
- Create `English/meeting/2026-04-03-shiproom.md`
- Include PPT structure outline
- Write natural speaking script
- Add Learning Notes section with vocabulary like "campaign", "kick off", "metrics"
- Update vocabulary.md and expressions.md with new terms

### Example 3: Pattern Learning

**User:** "How do I express 'according to' in formal writing?"

**Action:**
- Create daily log entry showing pattern: "[Something] will be [done] according to [basis]"
- Add to expressions.md under appropriate category with real example
- Include grammar note about formal usage

## Important Notes

- Always use Chinese for translations and explanations
- Keep tables properly formatted (align columns)
- Use actual examples from the conversation, not made-up ones
- Date format must be YYYY-MM-DD
- Pronunciations use IPA notation with forward slashes: /ˈprɒpərti/
- Grammar notes should be educational, explaining WHY something works
- For meeting files, prioritize natural, conversational English over literal translation
