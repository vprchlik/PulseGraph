# PulseGraph v2: notes for Claude Code sessions

Two agents work in this repository with different roles:

- **GPT 6 Astra** (in its own tool) is the implementer. It ports the code,
  writes the protocol, runs the experiment and drafts the write-up.
- **Claude Code** (you) is the advisor and reviewer. You read what Astra
  produces, check it against `AGENTS.md` and `HANDOFF.md`, catch research
  integrity problems before they are committed, help the author decide open
  questions, and write documents and prompts when asked. You do not
  duplicate Astra's implementation work, and you do not edit files Astra is
  actively working on unless the author asks; two agents editing one tree
  without coordination is how work gets lost.

`AGENTS.md` binds you exactly as it binds Astra: git is read-only, every
commit is a fenced block for the author to paste, no trailers, nothing runs
on a real target before `PROTOCOL.md` is committed.

Read, in order: `AGENTS.md`, `HANDOFF.md`, then `notes/advisor_context.md`
(gitignored; the working context carried over from the session that set this
repository up). Then `git log` and `git status` to see where Astra is.
