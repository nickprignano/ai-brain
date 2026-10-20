# park-it: a shelf for side ideas

A Claude skill that parks a side idea in the private layer: what was checked, why it's set aside,
and what would bring it back, one note per idea in `notes/parked/`. It also checks that bucket
before an idea gets researched again. The skill itself is [SKILL.md](SKILL.md).

## Why a bucket in the private layer

Parked ideas are personal judgment about what's worth doing, so they belong with the person's
other decisions and goals, not in a public KB or a repo of their own. One bucket with one note per
idea keeps a single home for each, and `stale_check.py` brings them back up for review.

## Install

1. Copy [SKILL.md](SKILL.md) into a new skill in your Claude account.
2. Fill in the settings block: your private layer's repo and, if you moved them, the bucket,
   index and rules paths.
3. Make sure your private layer has `notes/parked/_template.md` and a "Parked ideas" section in
   `notes/index.md`. Copies made from the template after this skill shipped have both; an older
   copy adopts them from the template.
