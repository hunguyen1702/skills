import { mkdirSync, mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { beforeEach, describe, expect, it } from "vitest";
import secretary from "../extensions/secretary.js";
import { mockPi } from "./helpers/mock-pi.js";

let root: string;

function ctx(session = "s1") {
	return { cwd: join(root, "sub"), sessionManager: { getSessionId: () => session } };
}

function agentStartEvent() {
	return { systemPromptOptions: { sections: {} as Record<string, string> } };
}

function writeStatus(sessions: Record<string, { active: boolean; log: string | null }>) {
	mkdirSync(join(root, "secretary"), { recursive: true });
	writeFileSync(join(root, "secretary", "status.json"), JSON.stringify({ sessions }));
}

async function sectionsFor(session: string) {
	const { pi, emit } = mockPi();
	secretary(pi);
	const event = agentStartEvent();
	await emit("before_agent_start", event, ctx(session));
	return event.systemPromptOptions.sections;
}

beforeEach(() => {
	root = mkdtempSync(join(tmpdir(), "secretary-"));
	mkdirSync(join(root, ".git"));
	mkdirSync(join(root, "sub"));
});

describe("secretary extension", () => {
	it("adds nothing when there is no status file", async () => {
		expect(await sectionsFor("s1")).toEqual({});
	});

	it("reminds only the session that turned logging on", async () => {
		writeStatus({ s1: { active: true, log: "secretary/a.md" } });
		expect((await sectionsFor("s1")).secretary).toContain("Log: secretary/a.md.");
		expect(await sectionsFor("s2")).toEqual({});
	});

	it("tells the agent how to create the log when there is none yet", async () => {
		writeStatus({ s1: { active: true, log: null } });
		expect((await sectionsFor("s1")).secretary).toContain("No log file yet");
	});

	it("stays silent once logging is off", async () => {
		writeStatus({ s1: { active: false, log: "secretary/a.md" } });
		expect(await sectionsFor("s1")).toEqual({});
	});
});
