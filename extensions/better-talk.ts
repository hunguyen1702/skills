// Pi counterpart of hooks/hooks.json: keeps better-talk always on.
// Claude Code hooks can only remind the model to load the skill, so they fire
// at session start and on every prompt. Pi lets an extension edit the system
// prompt directly, so this puts the skill body into it once per run; the rules
// then survive compaction without reminders. SKILL.md stays the single source.
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

const skillPath = join(dirname(fileURLToPath(import.meta.url)), "..", "skills", "better-talk", "SKILL.md");

function loadRules(): string {
	const raw = readFileSync(skillPath, "utf8");
	// Drop YAML frontmatter; the model only needs the rules.
	return raw.replace(/^---\n[\s\S]*?\n---\n/, "").trim();
}

export default function (pi: ExtensionAPI) {
	let rules = "";

	pi.on("session_start", async () => {
		// Re-read on every start and /reload so edits to SKILL.md apply at once.
		rules = loadRules();
	});

	pi.on("before_agent_start", async (event) => {
		if (!rules) return;
		event.systemPromptOptions.sections["better-talk"] = rules;
	});
}
