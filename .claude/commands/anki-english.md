---
description: Generate English language learning Anki cards
---

Generate English Anki flashcards directly in this conversation.

**Input:** $ARGUMENTS

---

## Step 1 – Generate YAML

Parse the input, determine note type, and produce YAML output.

### Input Types

#### YAML File Input

User provides filepath: `/anki-english tmp/language-input.yml`

Use the Read tool to load the file. Expected structure:

```yaml
cloze:
  - "relate to" # word or phrase you create an example sentence

pattern:
  - "効率化する" # japanese word you create synonyms

polysemy:
  - "stumble" # english word that has multiple meanings

vocab:
  - "控えめ" # japanese you translate into english word or phrase
```

#### CLI String Input

User provides direct input: `/anki-english polysemy: "stumble"`

Common CLI patterns:
- `polysemy: "<english word>"` → language_polysemy
- `synonyms for "<japanese word>"` → language_pattern
- `vocab: "<japanese description>"` → language_vocab
- `cloze: "<english word>"` → language_cloze

### Note Type Processing

#### language_cloze

**When to use**: User provides sentences with **bolded** words/phrases for fill-in-the-blank

**Input example**: `"Before we go, **do you have any questions** or **is there anything**?"`

**Processing**:
1. Extract each **bolded phrase**
2. Generate a hint for each phrase (see hint guidelines below)
3. Replace `**phrase**` with `{{c1::phrase::hint}}`, `{{c2::phrase::hint}}`, etc.
4. Only fill `clozeHint` if there is additional contextual information to provide

**Bracket hint guidelines (CRITICAL)**:
The hint inside `{{c1::phrase::hint}}` should be what the learner **naturally comes up with** — the casual Japanese expression or "Japanesey" translated English they would think of before recalling the correct phrase. The goal is to bridge from what the learner already knows to the target expression.

- **Use casual Japanese** when appropriate (e.g., `〜って言ってる情報を見つけた` NOT `〜を示唆する情報を見つけた`)
- **OR use "Japanesey" English** that a Japanese learner would naturally produce (e.g., `saw some people saying` instead of formal translations)
- Avoid dictionary-style Japanese translations — use the words the learner actually thinks in
- When it's hard to make it casual, keep the straightforward Japanese as is (e.g., `商業的利益で`)

**`clozeHint` guidelines (CRITICAL)**:
- `clozeHint` is for **additional contextual clues only** — NOT a repeat of the bracket hints
- Fill it only when there is extra context that helps recall the answer
- Leave as `""` when there is nothing extra to add
- **NEVER** put the same content in both the bracket hint and `clozeHint`

**Good example**:

```yaml
# Bracket hint is casual Japanese; clozeHint provides extra context about "this" vs "it"
Text: "Let me {{c1::bring this to a close::終わりにしよか}} by summarising the three main points we've covered today."
clozeHint: "この内容を締めくくる (your own content)"
```

**Good example (Japanesey English as hint)**:

```yaml
# Bracket hints are the "translated" English a Japanese learner would naturally come up with
Text: "I {{c1::came across information suggesting::saw some people saying}} that a former Monsanto employee was {{c2::appointed to::hired and the position is...}} a newly created editorial position before the retraction."
clozeHint: ""
```

**Bad example**:

```yaml
# Bracket hints use stiff dictionary Japanese; clozeHint duplicates them
Text: "I {{c1::came across information suggesting::〜を示唆する情報を見つけた}} that..."
clozeHint: "示唆する情報を見つけた"  # Redundant!
```

**Output YAML**:

```yaml
note_type: language_cloze
deck: English
fields:
  Text: "Before we go, {{c1::do you have any questions::なんか質問ある？}} or {{c2::is there anything::なんかある？}}?"
  clozeHint: ""
  hintNegative: ""
  followUp: ""
tags:
  - language::english::phrases
```

**Field guidelines**:
- `Text`: Required. Sentence with `{{c1::word::hint}}` markers. Hints should be casual Japanese or Japanesey English (see above)
- `clozeHint`: Optional. Only for additional context — never duplicate the bracket hints
- `hintNegative`: Optional. Include if there are confusing near-synonyms
- `followUp`: Optional. Include if additional context would help

#### language_pattern

**When to use**: User provides Japanese word/phrase and wants English synonyms

**Input example**: `"効率化する"` or `"synonyms for 効率化する"`

**Processing**:
1. Identify 2-5 English synonyms/expressions
2. For each, provide:
   - Optional description of nuance/usage
   - Example sentence with `**synonym**` marker
   - Same sentence without markers for answer
3. Keep `**word**` markers (formatted to HTML in Step 2)

**Output YAML**:

```yaml
note_type: language_pattern
deck: English
fields:
  source: "効率化する"
  description1: "to make something work more efficiently"
  sentence1: "I'm trying to make the process more **efficient**"
  sentenceAnswer1: "I'm trying to make the process more **efficient**"
  description2: "to organize a system so it operates more smoothly"
  sentence2: "I'm trying to automate and **streamline** the process"
  sentenceAnswer2: "I'm trying to automate and **streamline** the process"
  hintNegative1: ""
  followUp1: ""
tags:
  - language::english::vocabulary::business
```

**Field guidelines**:
- `source`: Required. The Japanese word/phrase
- `description1-5`: Optional but recommended. Explain nuance differences
- `sentence1-5`: Required for at least 1, recommended 2-5. Use `**word**` markers
- `sentenceAnswer1-5`: Required (matches sentence count). Use `**word**` markers (same as sentence)
- `hintNegative1-5`: Optional. Include if synonym is easily confused
- `followUp1-5`: Optional. Additional context if helpful

#### language_polysemy

**When to use**: User provides an English word with multiple meanings

**Input example**: `"stumble"` or `"polysemy: stumble"`

**Processing**:
1. Determine word type (verb, noun, adjective, etc.)
2. Generate conjugation forms:
   - **Verbs**: vocabularyS (3rd person), vocabularyPast, vocabularyPastPerfect, vocabularyIng
   - **Nouns**: vocabularyS (plural)
   - **Adjectives**: vocabularyComparative and vocabularySuperlative
   - **Others**: leave blank
3. Provide IPA pronunciation (British English preferred)
4. Identify core meaning
5. Generate 2-5 distinct definitions with Japanese translations
6. Create natural example sentence for each definition

**Output YAML** (verb example):

```yaml
note_type: language_polysemy
deck: English
fields:
  vocabulary: "stumble"
  vocabularyS: "stumbles"
  vocabularyPast: "stumbled"
  vocabularyPastPerfect: "stumbled"
  vocabularyIng: "stumbling"
  vocabularyComparative: ""
  vocabularySuperlative: ""
  pronunciation: "ˈstʌmbl"
  coreMeaning: "to step awkwardly or speak haltingly"
  inputDefinition1: "躓く"
  example1: "She stumbled on a log and fell on the sand."
  inputDefinition2: "よろめく"
  example2: "We could hear her stumbling about in the dark."
  inputDefinition3: "つかえる（どもる）"
  example3: "He sort of stumbled on the pronunciation of the name."
tags:
  - language::english::polysemy::verbs
```

**Field guidelines**:
- `vocabulary`: Required. Base form of word
- `vocabularyS/Past/PastPerfect/Ing/Comparative/Superlative`: Fill based on word type
- `pronunciation`: Required. British English IPA
- `coreMeaning`: Required. Unifying core meaning
- `inputDefinition1-5`: Required for at least 1. Japanese translation
- `example1-5`: Required (matches definition count). Natural contemporary English

#### language_vocab

**When to use**: Simple vocabulary cards with one example

**Input example**: `"控えめって意味の英語"` or `"Shy bairns get nowt"`

**Processing**:
1. Determine if user wants:
   - Translation example (Japanese description → English word in context)
   - Idiom/phrase explanation (English phrase → Japanese meaning)
2. Create front and back with `**word**` markers for highlighting
3. Add pronunciation if relevant

**Output YAML** (translation example):

```yaml
note_type: language_vocab
deck: English
fields:
  front: "Japanese people are a bit more **reserved**."
  back: "日本人はもうちょっと**控えめ**やね"
  pronunciation: "rɪˈzɜːvd"
tags:
  - language::english::vocabulary::adjectives
```

**Output YAML** (idiom example):

```yaml
note_type: language_vocab
deck: English
fields:
  front: "Shy bairns get nowt (naught)."
  back: "言わぬは損 (欲しいものがあるなら言わなきゃ得られない)"
  pronunciation: "beən, nɔːt"
tags:
  - language::english::idioms::british
```

**Field guidelines**:
- `front`: Required. English sentence/phrase with `**word**` markers
- `back`: Required. Japanese translation with `**word**` markers
- `pronunciation`: Optional. Include for uncommon words or idioms

### Tagging Guidelines

**Structure**: `language::english::<category>::<subcategory>`

- Always start with `language::english`, lowercase kebab-case, maximum 4 levels
- Examples: `language::english::vocabulary::business`, `language::english::polysemy::verbs`, `language::english::idioms::british`

### English-Specific Rules

1. **British English (CRITICAL)**: colour, favour, realise, lift (not elevator), flat (not apartment), rubbish (not trash)
2. **IPA Pronunciation**: British English (Received Pronunciation) — e.g. `rɪˈzɜːvd` not `rɪˈzɜːrvd`
3. **Natural Examples**: contemporary, conversational British English
4. **Japanese Hints**: casual form (やね instead of ですね) when appropriate
5. **Conjugations**: fill all relevant forms for verbs

### Output Format for Multiple Items

```yaml
- note_type: language_cloze
  deck: English
  fields:
    Text: "First item..."
  tags:
    - language::english::phrases

- note_type: language_pattern
  deck: English
  fields:
    source: "Second item..."
  tags:
    - language::english::vocabulary
```

### Error Handling

- If YAML file is empty: error with helpful message
- If note type cannot be determined: ask user to clarify
- If polysemy word has unclear type: default to general conjugations
- If Japanese hint is difficult, use English paraphrase instead
- If unclear which note type to use: ask user

---

## Step 2 – Send to Anki

Convert the YAML to AnkiConnect JSON and send directly.

### HTML formatting (apply when building JSON)

- `language_pattern` — `sentence1-5` fields: `**word**` → `<span style="color: rgb(251, 159, 42);">[...]</span>`; `sentenceAnswer1-5` fields: `**word**` → `<span style="color: rgb(251, 159, 42);">word</span>`
- `language_vocab` — `front` and `back` fields: `**word**` → `<span style="color: rgb(255, 170, 127);">word</span>`
- `language_cloze` — no transformation (already `{{c1::word::hint}}`)
- `language_polysemy` — no transformation (plain text)

### AnkiConnect JSON format

```json
{
  "action": "addNotes",
  "version": 6,
  "params": {
    "notes": [
      {
        "deckName": "<deck from YAML>",
        "modelName": "<note_type from YAML>",
        "fields": { "<field>": "<value>" },
        "tags": ["<tag>"]
      }
    ]
  }
}
```

### Send steps

1. Check Anki is running: `pgrep -f "Anki"` — if not found, warn user and stop
2. Write JSON to file using Write tool: `/tmp/anki_request.json`
3. Send: `uv run python .claude/skills/anki-generator/scripts/send_anki_request.py -f /tmp/anki_request.json`
4. Report result (success: note IDs returned; failure: display error message)

### Required fields by note type

- `language_vocab`: front, back
- `language_cloze`: Text
- `language_pattern`: source, description1, sentence1, sentenceAnswer1
- `language_polysemy`: vocabulary, pronunciation, coreMeaning, inputDefinition1, example1
