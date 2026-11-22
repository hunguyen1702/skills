// Pi counterpart of the secretary hook in hooks/hooks.json, which runs
// skills/secretary/scripts/secretary.py hook. The skill turns logging on and
// off by running that script, which reads PI_SESSION_ID and writes
// secretary/status.json; this extension only reads that file and adds the
// reminder while logging is on. Keep the reminder in step with secretary.py.
import { existsSync, readFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

const skillDir = join(dirname(fileURLToPath(import.meta.url)), "..", "skills", "secretary");
const skillMd = join(skillDir, "SKILL.md");
const script = join(skillDir, "scripts", "secretary.py");

type Entry = { active: boolean; log: string | null };

function repoRoot(start: string): string {
	let dir = resolve(start);
	for (;;) {
		if (existsSync(join(dir, ".git"))) return dir;
		const parent = dirname(dir);
		if (parent === dir) return resolve(start);
		dir = parent;
	}
}

function entryFor(root: string, session: string): Entry | undefined {
	try {
		return JSON.parse(readFileSync(join(root, "secretary", "status.json"), "utf8")).sessions?.[session];
	} catch {
		return undefined;
	}
}

export function reminder(entry: Entry): string {
	const where = entry.log
		? `Log: ${entry.log}.`
		: `No log file yet. When there is something to record, create it with \`python3 ${script} new --slug <english-slug> --title <title>\`.`;
	return (
		`secretary is active. After replying to each user message, update the log as ${skillMd} describes. ${where} ` +
		"If you are writing a handoff document, add to it: trigger the secretary skill in the new " +
		`session and continue the log at ${entry.log ?? "<log path>"}.`
	);
}

export default function (pi: ExtensionAPI) {
	pi.on("before_agent_start", async (event, ctx) => {
		const entry = entryFor(repoRoot(ctx.cwd), ctx.sessionManager.getSessionId());
		if (!entry?.active) return;
		event.systemPromptOptions.sections.secretary = reminder(entry);
	});
}
