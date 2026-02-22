---
name: anki-generator
description:
  Convert structured content into valid AnkiConnect JSON requests and send them
  to Anki. Handles language learning content and academic content (from files or conversation).
allowed-tools: Read,Bash(pgrep:*),Bash(uv run python:*),Bash(trash:*)
---

# Anki Generator

## Your Role

Convert structured content from two sources into AnkiConnect JSON format:

1. **Language learning content** from Language Tutor agents (YAML strings) - **auto-send without confirmation**
2. **Academic content** from markdown files or conversation history - **ask for confirmation before sending**

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
  source: "効率化する"
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
   - For pattern: `**word**` in sentence → `<span>[...]</span>`, in answer → `<span>word</span>`
   - For vocab: `**word**` → `<span>word</span>` with light orange color
   - For cloze: No transformation (already has {{c1::...}})
   - For polysemy: No transformation (plain text)
3. **Validate fields** against note-type.json
4. **Generate AnkiConnect JSON**
5. **Send to Anki**
6. **Clean up** temp JSON file (no YAML cleanup needed - strings only)

### 2. Academic Content (Files or Conversation)

Academic content can come from two sources:

**From markdown files:**
- Read file contents (use Read tool, not shell commands)
- Extract YAML frontmatter for tags and metadata
- Parse content to identify concepts, definitions, formulas

**From conversation history:**
- Extract relevant content based on user's description (e.g., "standard errorについて")
- Identify key concepts, definitions, formulas from the conversation
- May reference content that academic tutors have already written to files

**For both sources:**
- Determine note type (usually `academic_cloze`)
- Create cloze deletions from content
- Determine appropriate deck and tags

## Workflow for Language Notes (YAML Input)

When receiving YAML string from language tutor agents:

### Step 1: Parse YAML String

The tutor provides a YAML string (or list of YAML strings for multiple notes).

**Single note example:**

```yaml
note_type: language_vocab
deck: English
fields:
  front: "Japanese people are a bit more **reserved**."
  back: "日本人はもうちょっと**控えめ**やね"
  pronunciation: "rɪˈzɜːvd"
tags:
  - language::english::vocabulary
```

**Multiple notes example:**

```yaml
- note_type: language_cloze
  deck: English
  fields:
    Text: "Before we go, {{c1::do you have any questions::何か質問ある}}?"
  tags:
    - language::english::phrases

- note_type: language_vocab
  deck: English
  fields:
    front: "reserved"
    back: "控えめ"
  tags:
    - language::english
```

### Step 2: Apply HTML Formatting

Use formatter.py to transform `**word**` markers to HTML:

**For language_pattern:**
- In `sentence1-5`: `**word**` → `<span style="color: rgb(251, 159, 42);">[...]</span>`
- In `sentenceAnswer1-5`: `**word**` → `<span style="color: rgb(251, 159, 42);">word</span>`

**For language_vocab:**
- In `front` and `back`: `**word**` → `<span style="color: rgb(255, 170, 127);">word</span>`

**For language_cloze:**
- No transformation (already formatted as `{{c1::word::hint}}`)

**For language_polysemy:**
- No transformation (plain text)

### Step 3: Validate Fields

Check against note-type.json to ensure all required fields are present.

### Step 4: Generate AnkiConnect JSON

Create the JSON request with formatted fields.

### Step 5: Display and Send

**For Language Learning Content (from Language Tutors):**
- Display a brief summary (number of cards, deck)
- **Immediately send to Anki** via send_anki_request.py (no confirmation)
- Report success/failure

### Step 6: Clean Up

Remove temporary JSON file (no YAML file to clean - strings only).

## Workflow for Academic Notes

### Step 1: Determine Deck Name

**For Academic Notes:**

From file frontmatter tags:
- Read `tags` field: `tags: [statistics/regression/multi-variate-regression]`
- Match to available decks using longest hierarchy match:
  - `statistics/*` or `mathematics/*` → `Learn::Math-Stat`
  - `development/*` or `economics/*` or other academic → `Learn::Academic`

From conversation history:
- Infer topic from conversation context
- Use same matching rules as above based on inferred topic
- Fallback: `Learn::Academic` for general academic content

Fallback: `Default` (only when cannot determine)

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
  - `title`: From heading, concept name, or conversation context
  - `Text`: Content converted to cloze format
  - `source`: Source file path (if from file) or "conversation" (if from conversation history)
  - `spoiler`: Hidden hints (optional)
- If extracting from conversation history, identify the relevant explanations, definitions, and concepts discussed

### Step 4: Create Cloze Deletions (for academic_cloze)

**Your role in creating cloze deletions:**

- Identify key concepts, formulas, conditions, predicates
- Convert to `{{c1::text}}` format (NO hints after `::`)
- Use sequential numbering: `{{c1::...}}`, `{{c2::...}}`, etc.
- Keep content concise (few sentences max)
- Avoid lengthy derivations; focus on understanding

**Cloze creation principles:**

1. **Minimum information**: Cloze the smallest meaningful unit (a key term, a
   variable name, a short formula), not an entire explanatory phrase. The
   surrounding sentence should stay visible as the recall prompt.

   - Bad: `{{c1::the derivative with respect to <anki-mathjax>X_2</anki-mathjax> of the marginal effect of <anki-mathjax>X_1</anki-mathjax> on <anki-mathjax>Y</anki-mathjax>}}`
   - Good: `the derivative with respect to {{c1::<anki-mathjax>X_2</anki-mathjax>}} of the {{c2::marginal effect of <anki-mathjax>X_1</anki-mathjax>}} on <anki-mathjax>Y</anki-mathjax>`

2. **Test the hard part**: Hide what is genuinely hard to recall or reproduce.
   If the card involves a formula, cloze the formula itself rather than the
   trivial label or symbol it equals.

   - Bad: `<anki-mathjax>\\frac{\\partial^2 Y}{\\partial X_1 \\partial X_2} = {{c1::\\beta_3}}</anki-mathjax>` ($\beta_3$ is trivially recalled)
   - Good: `<anki-mathjax block="true">{{c1::\frac　{\partial^2 Y_i}　{\partial X_{1i} \partial X_{2i}　} }} = \beta_3</anki-mathjax>` (recalling the derivative expression is the hard part)

3. **No redundancy**: Do not create separate clozes for logically symmetric or
   implied content. If knowing one direction implies the other, test only one.

   - Bad: two clozes — `if <anki-mathjax>\\beta_3 > 0</anki-mathjax> then {{c1::larger}}` and `if <anki-mathjax>\\beta_3 < 0</anki-mathjax> then {{c2::smaller}}`
   - Good: one cloze — `if <anki-mathjax>\\beta_3 > 0</anki-mathjax> then {{c1::the larger}} the marginal effect becomes`

**Example:**

```text
Source: "The correlation coefficient takes values between -1 and 1. It equals ±1 only when all data points lie on a straight line."
Cloze: "The correlation coefficient (相関係数) takes values between {{c1::-1 and 1}}. It becomes {{c2::±1}} only when all data points {{c3::lie on a straight line}}."
```

**Japanese to English translation:**

- If source content is in Japanese, translate to English

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

### Step 7: Display and Send

**Behavior depends on content source:**

**For Language Learning Content (YAML from Language Tutors):**
1. **Display brief summary:**
   - Number of notes created
   - Deck(s) used
2. **Automatically send** to AnkiConnect (no confirmation needed)
3. Report success/failure

**For Academic Content:**
1. **Display generated JSON** to user in code block
2. **Show summary:**
   - Number of notes
   - Decks used
   - Note types used
3. **Ask for confirmation** before sending

### Step 8: Send to AnkiConnect

```bash
# 1. Check if Anki is running
if ! pgrep -f "Anki" > /dev/null; then
  echo "⚠️  Anki is not running. Please launch Anki first."
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

**Input (Example from markdown file):**

```markdown
---
tags: [statistics/correlation]
---

# Correlation Coefficient Range

The correlation coefficient takes values between -1 and 1. It becomes ±1 only
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
          "Text": "The correlation coefficient (相関係数) takes values between {{c1::-1 and 1}}. It becomes {{c2::±1}} only when all data points {{c3::lie on a straight line}}.",
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
  - front: "Japanese people are a bit more <span style=\"color: #fb9f2a;\">reserved</span>."
  - back: "日本人はもうちょっと<span style=\"color: #fb9f2a;\">控えめやね</span>"
  - pronunciation: "rɪˈzɜːvd"
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
          "front": "Japanese people are a bit more <span style=\"color: #fb9f2a;\">reserved</span>.",
          "back": "日本人はもうちょっと<span style=\"color: #fb9f2a;\">控えめやね</span>",
          "pronunciation": "rɪˈzɜːvd"
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

- Missing required fields → Ask user for missing information
- Invalid deck name → Use `Default` and warn user
- Anki not running → Show clear message to launch Anki
- AnkiConnect error → Display error message from response

## Math Formatting (Academic Cards)

For `academic_cloze` cards containing mathematical notation, use Anki's native
MathJax tags instead of plain Unicode or `\(...\)` delimiters:

- **Inline math:** `<anki-mathjax>expression</anki-mathjax>`
- **Block math:** `<anki-mathjax block="true">expression</anki-mathjax>`

**Rules:**

- Use standard LaTeX inside the tags (e.g., `\\beta_3`, `\\frac{a}{b}`)
- Cloze deletions `{{c1::...}}` can go **inside** `<anki-mathjax>` tags
- Double-escape backslashes in JSON strings (`\\\\beta` → renders as `\beta`)
- Add spaces before and after cloze `{{ }}` braces inside math for better
  rendering, especially with fractions (e.g., `\\frac{ {{c1::a}} }{b}` not `\\frac{{{c1::a}}}{b}`)

**Example field value in JSON:**

```text
"Text": "In the model <anki-mathjax>Y_i = \\beta_0 + \\beta_1 X_{1i}</anki-mathjax>, the slope is <anki-mathjax block=\"true\">\\frac{\\partial Y}{\\partial X_1} = {{c1::\\beta_1}}</anki-mathjax>"
```

**When to use:**

- Always use `<anki-mathjax>` for academic cards with formulas or math symbols
- Language cards do not need math formatting

## Important Notes

- **Never skip validation:** Always check required fields before generating JSON
- **Use Read tool for files:** Never use shell `cat` for reading markdown files; use Read tool
- **Extract from conversation when needed:** When academic content comes from conversation history, carefully extract the relevant explanations and concepts
- **Keep cloze concise:** Few sentences max, avoid full derivations
- **Sequential execution:** Check Anki running → Generate JSON → Display →
  Confirm → Send
- **Clean up:** Remove temporary files after successful send

## Options to Offer User

**For Academic Content only:**

After generating JSON, offer:

1. **Send now** - Send directly to AnkiConnect
2. **Save to file** - Save for later review/modification
3. **Modify** - Let user request changes before sending
4. **Cancel** - Discard the generated request

**For Language Learning Content:**

No options needed - automatically send and report result.

## Tools Available

- **Read**: Read markdown files and other reference files
- **Bash**: Check if Anki is running, execute send script
- Reference files using `@` syntax (e.g.,
  @.claude/skills/anki-generator/note-type.json)
- Access conversation history to extract academic content when needed
