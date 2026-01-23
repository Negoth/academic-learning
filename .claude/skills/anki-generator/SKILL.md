---
name: anki-generator
description:
  Convert structured content into valid AnkiConnect JSON requests and send them
  to Anki. Handles language learning content and academic markdown files.
allowed-tools: Read,Bash(pgrep:*),Bash(uv run python:*),Bash(trash:*)
---

# Anki Generator

## Your Role

Convert structured content from two sources into AnkiConnect JSON format:

1. **Language learning content** from Language Tutor
2. **Academic content** from Markdown files (you parse these yourself)

## Reference Files

- Note type specifications: @.claude/skills/anki-generator/note-type.json
- AnkiConnect wrapper: @src/anki_connect/__init__.py
- Request sender: @.claude/skills/anki-generator/scripts/send_anki_request.py

## Input Sources

### 1. YAML String from Language Tutors (NEW PRIMARY INPUT)

Language tutor agents (english-tutor, french-tutor) provide YAML strings:

```yaml
note_type: language_pattern
deck: English
fields:
  source: "efficient"
  description1: "to make something work more efficiently"
  sentence1: "I'm trying to make the process more **efficient**"
  sentenceAnswer1: "I'm trying to make the process more efficient"
  description2: "to organize a system so it operates more smoothly"
  sentence2: "I'm trying to **streamline** the process"
  sentenceAnswer2: "I'm trying to streamline the process"
tags:
  - language::english::vocabulary::business
```

**Your processing workflow:**

1. **Parse YAML** string using yaml_parser.py
2. **Apply HTML formatting** using formatter.py:
   - For pattern: `**word**` in sentence -> `<span>[...]</span>`, in answer -> `<span>word</span>`
   - For vocab: `**word**` -> `<span>word</span>` with light orange color
   - For cloze: No transformation (already has {{c1::...}})
   - For polysemy: No transformation (plain text)
3. **Validate fields** against note-type.json
4. **Generate AnkiConnect JSON**
5. **Send to Anki**
6. **Clean up** temp JSON file (no YAML cleanup needed - strings only)

### 2. Academic Markdown Files

You parse these files yourself:

- Read file contents (use Read tool, not shell commands)
- Extract YAML frontmatter for tags and metadata
- Parse content to identify concepts, definitions, formulas
- Determine note type (usually `academic_cloze`)
- Create cloze deletions from content

## Workflow for Language Notes (YAML Input)

When receiving YAML string from language tutor agents:

### Step 1: Parse YAML String

The tutor provides a YAML string (or list of YAML strings for multiple notes).

**Single note example:**

```yaml
note_type: language_vocab
deck: English
fields:
  front: "Someone who is a bit more **reserved**."
  back: "A **reserved** person is quiet and shy"
  pronunciation: "ri'zervd"
tags:
  - language::english::vocabulary
```

**Multiple notes example:**

```yaml
- note_type: language_cloze
  deck: English
  fields:
    Text: "Before we go, {{c1::do you have any questions::any questions}}?"
  tags:
    - language::english::phrases

- note_type: language_vocab
  deck: English
  fields:
    front: "reserved"
    back: "quiet and shy"
  tags:
    - language::english
```

### Step 2: Apply HTML Formatting

Use formatter.py to transform `**word**` markers to HTML:

**For language_pattern:**
- In `sentence1-5`: `**word**` -> `<span style="color: rgb(251, 159, 42);">[...]</span>`
- In `sentenceAnswer1-5`: `**word**` -> `<span style="color: rgb(251, 159, 42);">word</span>`

**For language_vocab:**
- In `front` and `back`: `**word**` -> `<span style="color: rgb(255, 170, 127);">word</span>`

**For language_cloze:**
- No transformation (already formatted as `{{c1::word::hint}}`)

**For language_polysemy:**
- No transformation (plain text)

### Step 3: Validate Fields

Check against note-type.json to ensure all required fields are present.

### Step 4: Generate AnkiConnect JSON

Create the JSON request with formatted fields.

### Step 5: Display and Confirm

Show JSON to user and get confirmation.

### Step 6: Send to Anki

Send via send_anki_request.py.

### Step 7: Clean Up

Remove temporary JSON file (no YAML file to clean - strings only).

## Workflow for Academic Notes (Markdown Files)

### Step 1: Determine Deck Name

**For Academic Notes (from frontmatter tags):**

- Read `tags` field: `tags: [statistics/regression/multi-variate-regression]`
- Match to available decks using longest hierarchy match:
  - `statistics/*` or `mathematics/*` -> `Learn::Math-Stat`
  - `development/*` or `economics/*` or other academic -> `Learn::Academic`
- Fallback: `Default` (only when cannot determine)

**For Language Notes (from Language Tutor):**

- Already specified in Language Tutor output
- Usually: `English`, `French`, or `<language_name>`

**Available decks:** `French`, `English`, `Learn::Academic`, `Learn::Math-Stat`

### Step 2: Validate Note Type

Check against @.claude/skills/anki-generator/note-type.json:

- `language_cloze`, `language_pattern`, `language_polysemy`, `language_vocab`
- `academic_cloze`, `image_occlusion`

### Step 3: Extract and Validate Fields

**For Language Notes:**

- Fields already provided by Language Tutor
- Validate all required fields are present
- Reference @.claude/skills/anki-generator/note-type.json for required fields

**For Academic Notes:**

- Determine note type (usually `academic_cloze`)
- Extract required fields:
  - `title`: From heading or concept name
  - `Text`: Content converted to cloze format
  - `source`: Source file path (optional)
  - `spoiler`: Hidden hints (optional)

### Step 4: Create Cloze Deletions (for academic_cloze)

**Your role in creating cloze deletions:**

- Identify key concepts, formulas, conditions, predicates
- Convert to `{{c1::text}}` format (NO hints after `::`)
- Use sequential numbering: `{{c1::...}}`, `{{c2::...}}`, etc.
- Keep content concise (few sentences max)
- Avoid lengthy derivations; focus on understanding

**Example:**

```text
Source: "The correlation coefficient takes values between -1 and 1. It equals +/-1 only when all data points lie on a straight line."
Cloze: "The correlation coefficient takes values between {{c1::-1 and 1}}. It becomes {{c2::+/-1}} only when all data points {{c3::lie on a straight line}}."
```

### Step 5: Format Tags

**From Academic Markdown frontmatter:**

- Input: `tags: [statistics/regression/multi-variate-regression]`
- Convert `/` to `::`: `statistics::regression::multi-variate-regression`
- Output as array: `["statistics::regression::multi-variate-regression"]`
- Use lowercase kebab-case

**From Language Notes:**

- Already formatted by Language Tutor
- Should follow pattern: `language::<language>::<category>::<subcategory>`
- Maximum 4 levels

### Step 6: Generate AnkiConnect JSON

**Output format:**

```json
{
  "action": "addNotes",
  "version": 6,
  "params": {
    "notes": [
      {
        "deckName": "<deck_name>",
        "modelName": "<note_type>",
        "fields": {
          "<field1>": "<value1>",
          "<field2>": "<value2>"
        },
        "tags": ["<tag1>", "<tag2>"]
      }
    ]
  }
}
```

**Multiple notes:** You can include multiple note objects in the `notes` array
for batch creation.

### Step 7: Display and Confirm

1. **Display generated JSON** to user in code block
2. **Show summary:**
   - Number of notes
   - Decks used
   - Note types used
3. **Ask for confirmation** before sending

### Step 8: Send to AnkiConnect

**After user confirmation:**

```bash
# 1. Check if Anki is running
if ! pgrep -f "Anki" > /dev/null; then
  echo "Anki is not running. Please launch Anki first."
  exit 1
fi

# 2. Save to temporary file
echo '<json_content>' > /tmp/anki_request.json

# 3. Send request
uv run python .claude/skills/anki-generator/scripts/send_anki_request.py -f /tmp/anki_request.json
```

**Handle response:**

- Success: `{"result": [note_id1, note_id2, ...], "error": null}`
- Failure: `{"result": null, "error": "error message"}`

## Examples

### Academic Cloze

**Input (Markdown file):**

```markdown
---
tags: [statistics/correlation]
---

# Correlation Coefficient Range

The correlation coefficient takes values between -1 and 1. It becomes +/-1 only
when all data points lie on a straight line.
```

**Output (AnkiConnect JSON):**

```json
{
  "action": "addNotes",
  "version": 6,
  "params": {
    "notes": [
      {
        "deckName": "Learn::Math-Stat",
        "modelName": "academic_cloze",
        "fields": {
          "title": "Correlation Coefficient Range",
          "Text": "The correlation coefficient takes values between {{c1::-1 and 1}}. It becomes {{c2::+/-1}} only when all data points {{c3::lie on a straight line}}.",
          "spoiler": "Derived from standardized scores",
          "source": "path/to/source.md"
        },
        "tags": ["statistics::correlation"]
      }
    ]
  }
}
```

### Language Vocab

**Input (from Language Tutor):**

```text
Note Type: language_vocab
Deck: English
Fields:
  - front: "Someone who is a bit more <span style=\"color: #fb9f2a;\">reserved</span>."
  - back: "A <span style=\"color: #fb9f2a;\">reserved</span> person is quiet and shy"
  - pronunciation: "ri'zervd"
Tags: ["language::english::vocabulary"]
```

**Output (AnkiConnect JSON):**

```json
{
  "action": "addNotes",
  "version": 6,
  "params": {
    "notes": [
      {
        "deckName": "English",
        "modelName": "language_vocab",
        "fields": {
          "front": "Someone who is a bit more <span style=\"color: #fb9f2a;\">reserved</span>.",
          "back": "A <span style=\"color: #fb9f2a;\">reserved</span> person is quiet and shy",
          "pronunciation": "ri'zervd"
        },
        "tags": ["language::english::vocabulary"]
      }
    ]
  }
}
```

## Field Validation

Before generating JSON, validate against
@.claude/skills/anki-generator/note-type.json:

**Required fields by note type:**

- `language_vocab`: front, back
- `language_cloze`: Text
- `language_pattern`: source, description1, sentence1, sentenceAnswer1
- `language_polysemy`: vocabulary, pronunciation, coreMeaning, inputDefinition1,
  example1
- `academic_cloze`: Text, title
- `image_occlusion`: image

## Error Handling

**Common issues:**

- Missing required fields -> Ask user for missing information
- Invalid deck name -> Use `Default` and warn user
- Anki not running -> Show clear message to launch Anki
- AnkiConnect error -> Display error message from response

## Important Notes

- **Never skip validation:** Always check required fields before generating JSON
- **Use Read tool for files:** Never use shell `cat` for reading Markdown files
- **Keep cloze concise:** Few sentences max, avoid full derivations
- **Sequential execution:** Check Anki running -> Generate JSON -> Display ->
  Confirm -> Send
- **Clean up:** Remove temporary files after successful send

## Options to Offer User

After generating JSON, offer:

1. **Send now** - Send directly to AnkiConnect
2. **Save to file** - Save for later review/modification
3. **Modify** - Let user request changes before sending
4. **Cancel** - Discard the generated request

## Tools Available

- **Read**: Read Markdown files
- **Bash**: Check if Anki is running, execute send script
- Reference files using `@` syntax (e.g.,
  @.claude/skills/anki-generator/note-type.json)
