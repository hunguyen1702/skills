import { mkdirSync, mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { beforeEach, describe, expect, it } from "vitest";
import journal from "../extensions/journal.js";
import { mockPi } from "./helpers/mock-pi.js";

let root: string;

function ctx(session = "s1") {
	return { cwd: join(root, "sub"), sessionManager: { getSessionId: () => session } };
}

function agentStartEvent() {
	return { systemPromptOptions: { sections: {} as Record<string, string> } };
}

function writeStatus(sessions: Record<string, { active: boolean; log: string | null }>) {
	mkdirSync(join(root, "journal"), { recursive: true });
	writeFileSync(join(root, "journal", "status.json"), JSON.stringify({ sessions }));
}

async function sectionsFor(session: string) {
	const { pi, emit } = mockPi();
	journal(pi);
	const event = agentStartEvent();
	await emit("before_agent_start", event, ctx(session));
	return event.systemPromptOptions.sections;
}

beforeEach(() => {
	root = mkdtempSync(join(tmpdir(), "journal-"));
	mkdirSync(join(root, ".git"));
	mkdirSync(join(root, "sub"));
});

describe("journal extension", () => {
	it("adds nothing when there is no status file", async () => {
		expect(await sectionsFor("s1")).toEqual({});
	});

	it("reminds only the session that turned logging on", async () => {
		writeStatus({ s1: { active: true, log: "journal/a.md" } });
		expect((await sectionsFor("s1")).journal).toContain("Log: journal/a.md.");
		expect(await sectionsFor("s2")).toEqual({});
	});

	it("tells the agent how to create the log when there is none yet", async () => {
		writeStatus({ s1: { active: true, log: null } });
		expect((await sectionsFor("s1")).journal).toContain("No log file yet");
	});

	it("stays silent once logging is off", async () => {
		writeStatus({ s1: { active: false, log: "journal/a.md" } });
		expect(await sectionsFor("s1")).toEqual({});
	});
});
