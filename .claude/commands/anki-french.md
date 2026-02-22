---
description: Generate French language learning Anki cards
---

Generate French Anki flashcards directly in this conversation.

**Input:** $ARGUMENTS

---

## Step 1 – Generate YAML

Parse the input, determine note type, and produce YAML output.

### Input Types

#### YAML File Input

User provides filepath: `/anki-french tmp/language-input.yml`

Use the Read tool to load the file. Expected structure:

```yaml
cloze:
  - "s'avérer" # French word or phrase — you create an example sentence with **bold**

pattern:
  - "礼儀正しい" # Japanese word — you create French synonyms

polysemy:
  - "courir" # French word that has multiple meanings

vocab:
  - "風景がきれいって意味のフランス語" # Japanese — you translate into French word or phrase
```

#### CLI String Input

User provides direct input: `/anki-french polysemy: "courir"`

Common CLI patterns:
- `polysemy: "<french word>"` → language_polysemy
- `synonyms for "<japanese word>"` → language_pattern
- `vocab: "<japanese description>"` → language_vocab
- `cloze: "<french word>"` → language_cloze

### Note Type Processing

#### language_cloze

**When to use**: User provides sentences with **bolded** words/phrases for fill-in-the-blank

**Input example**: `"Avant de partir, **avez-vous des questions** ou **voulez-vous dire quelque chose**?"`

**Processing**:
1. Extract each **bolded phrase**
2. Generate a hint for each phrase (see hint guidelines below)
3. Replace `**phrase**` with `{{c1::phrase::hint}}`, `{{c2::phrase::hint}}`, etc.
4. Only fill `clozeHint` if there is additional contextual information to provide

**Bracket hint guidelines (CRITICAL)**:
The hint inside `{{c1::phrase::hint}}` should be what the learner **naturally comes up with** — the casual Japanese expression or "Japanesey" French/English they would think of before recalling the correct phrase. The goal is to bridge from what the learner already knows to the target expression.

- **Use casual Japanese** when appropriate (e.g., `なんか質問ある？` NOT `何か質問がありますか`)
- **OR use "Japanesey" French** that a Japanese learner would naturally produce
- Avoid dictionary-style Japanese translations — use the words the learner actually thinks in
- When it's hard to make it casual, keep the straightforward Japanese as is (e.g., `商業的利益で`)

**`clozeHint` guidelines (CRITICAL)**:
- `clozeHint` is for **additional contextual clues only** — NOT a repeat of the bracket hints
- Fill only when there is extra context that helps recall (e.g., register notes, grammar rules)
- Leave as `""` when there is nothing extra to add
- **NEVER** put the same content in both the bracket hint and `clozeHint`

**Good example**:

```yaml
# Bracket hint is casual Japanese; clozeHint adds register context
Text: "{{c1::Il s'avère que::わかったんやけど}} cette entreprise avait un conflit d'intérêts."
clozeHint: "formal/written register"
```

**Good example (no extra context needed)**:

```yaml
Text: "Avant de partir, {{c1::avez-vous des questions::なんか質問ある？}} ou {{c2::voulez-vous dire quelque chose::なんか言いたいことある？}}?"
clozeHint: ""
```

**Bad example**:

```yaml
# Stiff Japanese; clozeHint duplicates bracket hint
Text: "Avant de partir, {{c1::avez-vous des questions::何か質問がありますか}}?"
clozeHint: "何か質問がありますか"  # Redundant!
```

**Output YAML**:

```yaml
note_type: language_cloze
deck: French
fields:
  Text: "Avant de partir, {{c1::avez-vous des questions::なんか質問ある？}} ou {{c2::voulez-vous dire quelque chose::なんか言いたいことある？}}?"
  clozeHint: ""
  hintNegative: ""
  followUp: ""
tags:
  - language::french::phrases
```

**Field guidelines**:
- `Text`: Required. Sentence with `{{c1::word::hint}}` markers
- `clozeHint`: Optional. Only for additional context — never duplicate bracket hints
- `hintNegative`: Optional. Include if there are confusing near-synonyms
- `followUp`: Optional. Include if additional context would help

#### language_pattern

**When to use**: User provides Japanese word/phrase and wants French synonyms

**Input example**: `"礼儀正しい"` or `"synonyms for 礼儀正しい"`

**Processing**:
1. Identify 2-5 French synonyms/expressions
2. For each, provide:
   - Optional description of nuance/usage
   - Example sentence with `**synonym**` marker
   - Same sentence without markers for answer
3. Keep `**word**` markers (formatted to HTML in Step 2)

**Output YAML**:

```yaml
note_type: language_pattern
deck: French
fields:
  source: "礼儀正しい"
  description1: "showing good manners in a formal way"
  sentence1: "Il est très **poli** avec tout le monde"
  sentenceAnswer1: "Il est très **poli** avec tout le monde"
  description2: "polite, especially in difficult situations"
  sentence2: "Elle est toujours **courtoise** avec ses clients"
  sentenceAnswer2: "Elle est toujours **courtoise** avec ses clients"
  hintNegative1: ""
  followUp1: ""
tags:
  - language::french::vocabulary::manners
```

**Field guidelines**:
- `source`: Required. The Japanese word/phrase
- `description1-5`: Optional but recommended
- `sentence1-5`: Required for at least 1. Use `**word**` markers
- `sentenceAnswer1-5`: Required (matches sentence count). Use `**word**` markers
- `hintNegative1-5`: Optional
- `followUp1-5`: Optional

#### language_polysemy

**When to use**: User provides a French word with multiple meanings

**Input example**: `"courir"` or `"polysemy: courir"`

**Processing**:
1. Determine word type (verb, noun, adjective, etc.)
2. Generate conjugation forms (see French-Specific Rules below)
3. Provide French IPA pronunciation
4. Identify core meaning
5. Generate 2-5 distinct definitions with Japanese translations
6. Create natural example sentence for each definition

**Output YAML**:

```yaml
note_type: language_polysemy
deck: French
fields:
  vocabulary: "courir"
  vocabularyS: "court"
  vocabularyPast: "a couru"
  vocabularyPastPerfect: "couru"
  vocabularyIng: "courant"
  pronunciation: "kuʁiʁ"
  coreMeaning: "se déplacer rapidement ou être en cours"
  inputDefinition1: "走る"
  example1: "Il court tous les matins dans le parc."
  inputDefinition2: "～が進行中である"
  example2: "Le contrat court jusqu'à la fin de l'année."
tags:
  - language::french::polysemy::verbs
```

**Field guidelines**:
- `vocabulary`: Required. Infinitive form
- `vocabularyS/Past/PastPerfect/Ing`: Fill based on word type
- `pronunciation`: Required. French IPA
- `coreMeaning`: Required. Unifying core meaning
- `inputDefinition1-5`: Required for at least 1. Japanese translation
- `example1-5`: Required (matches definition count)

#### language_vocab

**When to use**: Simple vocabulary cards with one example

**Input example**: `"風景がきれいって意味のフランス語"` or `"C'est un très joli petit village"`

**Processing**:
1. Determine if user wants:
   - Translation example (Japanese description → French word in context)
   - Sentence example (French sentence → Japanese meaning)
2. Create front and back with `**word**` markers for highlighting
3. Add pronunciation if relevant

**Output YAML**:

```yaml
note_type: language_vocab
deck: French
fields:
  front: "C'est un très **joli** petit village."
  back: "とても**きれいな**小さな村だね"
  pronunciation: "ʒɔli"
tags:
  - language::french::vocabulary::adjectives
```

**Field guidelines**:
- `front`: Required. French sentence/phrase with `**word**` markers
- `back`: Required. Japanese translation with `**word**` markers
- `pronunciation`: Optional. Include for uncommon words or idioms

### Tagging Guidelines

**Structure**: `language::french::<category>::<subcategory>`

- Always start with `language::french`, lowercase kebab-case, maximum 4 levels
- Examples: `language::french::vocabulary::food`, `language::french::polysemy::verbs`, `language::french::idioms`

### French-Specific Rules

1. **Diacritical Marks (CRITICAL)**: é, è, à, ù, ê, î, ô, û, â, ç, ë, ï — verify all French words before outputting
2. **Gender Markers for Nouns**: always include articles (le/la/l'/les) to show gender
3. **Formal vs Informal Register**: note in `followUp` field when relevant — `"Informal register (tu form)"` / `"Formal register (vous form)"`
4. **Verb Conjugations** (for polysemy):
   - `vocabularyS`: 3rd person singular present (court)
   - `vocabularyPast`: passé composé auxiliary + past participle (a couru)
   - `vocabularyPastPerfect`: past participle only (couru)
   - `vocabularyIng`: present participle (courant)
5. **IPA Pronunciation**: French notation — `ʁ` for French R, `ɛ̃` for nasal vowels
6. **Liaison Notes**: include in `followUp` when relevant — e.g. `"Liaison: 'les_amis' [le.z‿a.mi]"`

### Output Format for Multiple Items

```yaml
- note_type: language_cloze
  deck: French
  fields:
    Text: "Premier item..."
  tags:
    - language::french::phrases

- note_type: language_pattern
  deck: French
  fields:
    source: "Deuxième item..."
  tags:
    - language::french::vocabulary
```

### Error Handling

- Missing accents: if unsure, look it up — never omit accents
- Unclear gender: default to "(le/la) mot" or ask user
- If YAML file is empty: error with helpful message
- If note type cannot be determined: ask user to clarify
- If polysemy word has unclear type: default to general conjugations
- If Japanese hint is difficult, use French/English paraphrase instead
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
