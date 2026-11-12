---
name: ste
description: Writes and examines documentation in ASD-STE100 Simplified Technical English (STE), Issue 9 — the controlled language with a dictionary of approved words, technical nouns and verbs, and strict sentence rules. Use it when a project instruction file (CLAUDE.md, AGENTS.md, GEMINI.md) tells you to write in STE, when you write or change documentation, procedures, specs, tickets, README files or commit messages in that project, or when the user asks for an STE check of a text or file, asks if a word is approved in STE, or asks to write or rewrite text in Simplified Technical English. Changes sentences that you did not write only when the user tells you to do it.
---

# STE: ASD-STE100 Simplified Technical English

STE is a controlled language for technical documentation (ASD-STE100, Issue 9, 2025-01-15). It has two parts:
- **Writing rules**: short sentences, one topic per sentence, active voice, simple verb tenses, vertical lists, limits on words per sentence and sentences per paragraph.
- **A dictionary**: about 880 approved words, each with one meaning and one part of speech, plus about 1,300 words that are not approved, with the approved alternatives.

Readers who are not native English speakers, and translation tools, understand STE text with fewer errors. That is the purpose: every sentence has one meaning.

Write STE only where the project or the user asks for it, and only for documentation. Chat with the user stays in normal English.

## The tool

`STE` below means `python3 ~/.claude/skills/ste/scripts/ste.py`.

| Task | Command |
|---|---|
| Find words in the dictionary | `STE lookup allow tests "according to"` |
| Examine files | `STE check docs/guide.md README.md` |
| Examine only your new and changed sentences | `STE check docs/guide.md --since HEAD` |
| Examine a procedure file that `.ste.toml` does not describe | `STE check steps.md --kind procedural` |
| Examine a commit message (the subject is a title) | `printf '# %s\n\n%s\n' "$SUBJECT" "$BODY" \| STE check -` |
| Machine-readable output | add `--json` |

The tool needs the local copy of the standard (one Markdown file per page, `page_NNN.md`). It looks in this sequence: the option `--standard-dir`, the environment variable `STE_STANDARD_DIR`, then `~/.local/share/ste/ASD-STE100_ISSUE9/`. If it does not find the standard, `lookup` stops and `check` does only the checks without the dictionary, with exit code 2. Tell the user, and do not say that a text has no errors.

ASD owns the copyright of the standard. Never copy its pages, dictionary rows or example sentences into project files or git. Use them only to decide, and quote at most a word and its alternatives.

## Workflow: write or change documentation in STE

1. **Select the scope.** Write in STE the new text and each sentence that you change. Do not rewrite the other sentences of a document unless the user tells you to: the project often has old text that is not in STE yet.
2. **Select the text kind.** A procedure (instructions, steps) has a maximum of 20 words in each sentence. Descriptive text (descriptions, requirements, reports) has a maximum of 25. A specification is descriptive text that can also use the verbs of law and regulations (for example "comply with").
3. **Write with the core rules below.** For details, read [references/rules.md](references/rules.md): it gives each rule of the standard with its number and page. Read the sections that you need one time in a task.
4. **Avoid the frequent errors.** [references/frequent-errors.md](references/frequent-errors.md) lists words that agents often use but STE does not approve, for example "allow", "provide", "via", "ensure", "require", with their alternatives.
5. **Look up each word that you are not sure about** with `STE lookup`. The entry gives the part of speech and the meaning that STE approves. A word can be approved as a noun and not as a verb ("test", "check").
6. **Examine the result** with `STE check FILE --since REV`. REV is the git revision before your first change: `HEAD` if you did not commit yet, else for example `HEAD~1` or `main`. For a new file, leave out `--since`. For a procedure, add `--kind procedural` if `.ste.toml` does not give the kind. The header line shows "(N of M)" sentences: if N is 0, the check did not examine your text.
7. **Correct and examine.** Correct every `error` in the sentences that you wrote. Examine every `question` (see "Read the report"). Then run the check again. The questions that you examined and kept stay in the report: this is correct. Stop when only those questions remain.
8. **Do the checks that only you can do** (see the last section). The script cannot see meaning.

## Core rules (the details are in references/rules.md)

- Use only approved words (UPPERCASE in the dictionary), technical nouns, and technical verbs (rule 1.1). Use an approved word only with its part of speech and its approved meaning (rules 1.2, 1.3). Use only the verb forms that the dictionary gives (rule 3.1).
- Technical nouns are names of things in your field (rule 1.5): `access token`, `database`, `pull request`, and numbers. Technical verbs are actions in your field that no approved verb describes (rule 1.12), for example the computer processes "click", "delete", "enable" (pp. 57 and 58). Use a technical verb only as a verb (rule 1.13), and one term for one thing (rule 1.11).
- Do not use more than three words in a noun group (rule 2.1).
- Use these verb forms only: infinitive, imperative, simple present, simple past, simple future, and the past participle as an adjective (rules 3.2, 3.3). Do not use "has/have/had" + past participle, or "is to be / can be / must be / will be" + past participle (rule 3.4). Use an "-ing" form only in a technical noun, for example a title such as "Troubleshooting", or as a modifier in a technical noun (rule 3.5). Use the active voice; in descriptive text, the passive is acceptable only when the agent is unknown (rule 3.6).
- Use a verb, not a noun, for an action: "before you install the agent", not "before the installation of the agent" (rule 3.7).
- Do not omit words to make a sentence short, and keep the articles (rules 4.2, 4.5). Do not use contractions (rule 4.2).
- Use a vertical list for a sentence with many parts (rule 4.3): a colon after the text before the list, an uppercase letter at the start of each item, no comma or semicolon at the end of an item, a period after the last item, no list in a list item.
- Procedures: maximum 20 words in each sentence, one instruction in each sentence, imperative form, the condition first ("If the light is red, stop the pump.") (rules 5.1 to 5.4). Notes give information, not instructions, and have a maximum of 25 words (rule 5.5).
- Descriptive text: maximum 25 words in each sentence, one topic in each sentence, maximum six sentences in each paragraph, the topic in the first sentence (rules 6.1 to 6.6).
- Safety: "WARNING" for a risk of injury or death, "CAUTION" for a risk of damage. Start with the command or the condition, then give the risk; maximum 20 words (section 7, rule 5.1).
- No semicolons (rule 8.1). For the word count, these items count as one word: a number, a number with its unit, an abbreviation, an identifier, inline code, quoted text, a title, a proper noun, a hyphenated word. Text in parentheses counts as one word, and it is a sentence of its own (rules 8.5 to 8.7).
- Do not use "he" or "she" (GR-7). The general recommendations are not rules, but follow them: write "that" after "make sure" and "show" (GR-1), and do not use "e.g.", "i.e." or "etc." (GR-6).
- If a word-for-word change does not work, write a different sentence (rule 9.1). Do not make phrasal verbs such as "set up" or "roll back" (rule 9.3).

## Read the report

The first line of each file gives the text kind, the scope ("all sentences" or "new and changed sentences since REV (N of M)") and the `.ste.toml` that the tool used. A line "NOT COMPLETE" tells what the tool could not do. Each result has this format:

`file:line:column: class rule message [N times, lines a, b, c] -> alternatives (p. PAGE)`

- `error`: a rule that the script can examine without grammar. The tool gives no error on the 3,005 STE examples of the standard. Correct it in the text that you wrote. If an error is on a sentence that you did not write, or is clearly wrong (a name, a title), do not change that text: tell the user.
- `question`: a possible problem that needs your judgment. Examine each one. A question about a word lists all the lines where the word occurs.

| Rule | What to do |
|---|---|
| 1.1 (not approved) | Replace the word with an alternative that keeps the meaning, or write a different sentence. Keep the word only if it is part of a technical noun or a technical verb here. If the message tells that the standard lists the word as a technical verb, it is correct only for that process and only as a verb. |
| 1.2 (part of speech) | The word is approved only as a different part of speech (for example "test" is a noun, not a verb). Change the sentence if your use is the wrong one. |
| 1.5 (not in the dictionary) | One line lists these words, each with its first line. Keep a word only if it is a technical noun or a technical verb of the project; replace ordinary words ("currently", "simple"). |
| 3.1 (unlisted form) | Use a form of the verb that the dictionary gives, or a different construction. |
| 3.4, 3.6 (verb constructions) | Use the active voice and a simple tense. A past participle that shows a condition, before a noun or after "be", "become" or "stay", is an adjective and is correct (rule 3.3). |
| 3.5 ("-ing") | Keep it only in a technical noun. |
| 2.1 (noun group) | Break the group with a preposition or a relative clause, or define a short term. |
| 5.1 (numbered item, 21 to 25 words) | If the item is a procedure step, shorten it to 20 words. |
| GR-1 | Write "that" after "make sure". |

Exit code: 0 = no error and a full check, 1 = errors, 2 = the check is not complete (no standard, a bad `.ste.toml`, an unknown git revision). Report a code 2 to the user.

**Long documents.** A full check of a long document can give hundreds of results. Do not read all of them at one time. Read the totals in the last line (`STE check FILE | tail -1`): they give the count for each rule. Correct the errors first (`STE check FILE | grep ": error "`), then examine the questions one section at a time. Use `--json` to process the results with a script.

## Project configuration

A project can put an optional `.ste.toml` in its root: the technical nouns and verbs, the glossaries to read terms from, the categories of technical verbs to accept, and the text kind of files and sections. Without it, every term of the project is reported as a question. To change it, read [references/configuration.md](references/configuration.md). If the project has no `.ste.toml`, do not make one without the user: give the terms that you found to the user in your report.

## Write a text again in STE

Rewrite a text only when the user tells you to do it. Keep the meaning exactly. Keep code, identifiers, commands, file paths, URLs, product names and labels on the screen unchanged: they are technical nouns. Divide long sentences, use vertical lists, and change passive sentences to active ones when you know the agent. Then run the check.

## Checks that only you can do

The script cannot examine these rules. Read each new sentence again for them:
- The approved meaning of each word (rule 1.3). For example, STE uses "follow" only for a position or a sequence (one item comes after another), and "agree" only when two things are the same or match.
- One topic in each sentence, one topic in each paragraph, the topic first (rules 6.1, 6.4, 6.5).
- One instruction in each sentence of a procedure, the condition before the command (rules 5.2, 5.4).
- No phrasal verbs that the dictionary does not list (rule 9.3), and the same term for the same thing everywhere (rules 1.11, 9.4).
- Notes give only information (rule 5.5). Warnings and cautions have the correct form (section 7).

When you report to the user, give the number of errors and the questions that you resolved. Say "the check found no errors", not "the text is STE compliant", because the script cannot examine meaning.
