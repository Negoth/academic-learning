---
allowed-tools: Read,Edit
description: Add tags to markdown file frontmatter
---

Add tags to yaml frontmatter of markdown files: $ARGUMENTS.

## Find files

If directory given, find all `.md` files.
If single file, use that file.

## Instructions

1. **Read the file** and understand its content
2. **Check frontmatter**: Create if missing, add `tags` field if missing
3. **Generate 3-7 relevant tags** based on content

## Tag Format

- Hierarchical with `/` separator: `statistics/regression`
- Lowercase kebab-case: `machine-learning/neural-networks`
- Merge with existing tags (don't remove any)

## Core Categories

- **statistics/**: regression, hypothesis-testing, bayesian, time-series, distributions
- **econometrics/**: causal-inference, panel-data, instrumental-variables, difference-in-differences
- **math/**: calculus, linear-algebra, optimization, probability
- **machine-learning/**: supervised, unsupervised, deep-learning, neural-networks, nlp
- **development/**: poverty-reduction, policy-analysis, impact-evaluation
- **engineering/**: software, systems, design
- **tools/**: python, r, stata, latex
- **language/**: japanese, english, french

Create new subcategories freely if needed. Keep it simple - add tags that help find the file later.
