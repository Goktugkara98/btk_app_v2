# AI Scenarios Prompt Templates

This directory defines prompt templates for the AI chat system. The system now uses a simple, file-only convention: each scenario or quick-action has exactly two Markdown files that contain the complete prompt content.

## Structure

- `direct/`
  - `first.md`
  - `followup.md`
- `wrong_answer/`
  - `first.md`
  - `followup.md`
- `quick_action/`
  - `actions/`
    - `<action_name>/`
      - `first.md`
      - `followup.md`

Notes:
- No modular includes or JSON blocks are required. Author the full prompt directly in `first.md` and `followup.md`.
- Quick actions must live under `quick_action/actions/<action>/` with both `first.md` and `followup.md`.
 - There are no required JSON files for scenarios anymore. Backend routes use only the Markdown files; unknown/missing actions will return a 400 error.

## Available placeholders

Core placeholders available in Markdown templates:
- `{SYSTEM}`
- `{DIRECTIVE}`
- `{USER_MESSAGE}`
- `{HISTORY}`
- `{QUESTION_BLOCK}`

Question/session placeholders (if available in context):
- `{question_text}`
- `{options_bulleted}` / `{options_plain}`
- `{correct_answer_text}` / `{correct_option_letter}`
- `{SUBJECT}`, `{TOPIC}`, `{DIFFICULTY}`

## Authoring guidelines

- Keep prompts concise and task-focused; write all guidance directly in the template.
- For `first.md`, assume there may be no meaningful prior history.
- For `followup.md`, reference `{HISTORY}` sparingly.
- Avoid referencing removed include files; do not use modular blocks.
