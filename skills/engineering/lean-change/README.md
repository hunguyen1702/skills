# lean-change

The mindset for a task that has to change code: solve the whole task with the change that disturbs the codebase least. Lazy means least impact, not fewest lines.

The skill ranks the options by four goals, and the higher goal wins when they conflict:

1. Complete and correct: the change reaches every caller, test, fixture, config, and export it touches.
2. Smallest blast radius: easy to roll back, no multi-step migration, more important features left alone.
3. Reuse: the codebase's own patterns and helpers, then the standard library, then installed dependencies.
4. Least new code.

It also covers when to add an abstraction, how to write comments, how to mark a deliberate shortcut (`shortcut: <the limit>, <when to upgrade>`), and what never to cut.

The skill applies only to choices that the agreed spec, design, or plan leaves open. It loads on its own when an agent implements, fixes, or refactors code, and other skills such as `implement` can load it by name. It does not cover module design, technical design, or code review.

## Credits

Adapted from the `ponytail` skill in [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) by Dietrich Gebert, released under the MIT License. This skill keeps its "Before you write" step, the reuse ladder, the `shortcut:` marker, and the "never cut" list. It reorders the priorities around blast radius and drops the levels, the push-back behaviour, and the closing report line.
