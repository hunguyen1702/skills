import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import betterTalk from "../extensions/better-talk.js";
import { mockPi } from "./helpers/mock-pi.js";

const skill = readFileSync(new URL("../skills/better-talk/SKILL.md", import.meta.url), "utf8");

function agentStartEvent() {
	return { systemPromptOptions: { sections: {} as Record<string, string> } };
}

describe("better-talk extension", () => {
	it("puts the skill body into the system prompt as its own section", async () => {
		const { pi, emit } = mockPi();
		betterTalk(pi);

		await emit("session_start", { reason: "startup" });
		const event = agentStartEvent();
		await emit("before_agent_start", event);

		const section = event.systemPromptOptions.sections["better-talk"];
		expect(section).toMatch(/^# Better Talk/);
		expect(skill).toContain(section);
	});

	it("drops the YAML frontmatter", async () => {
		const { pi, emit } = mockPi();
		betterTalk(pi);

		await emit("session_start", { reason: "startup" });
		const event = agentStartEvent();
		await emit("before_agent_start", event);

		const section = event.systemPromptOptions.sections["better-talk"];
		expect(section).not.toContain("---");
		expect(section).not.toMatch(/^name:/m);
		expect(section).not.toMatch(/^description:/m);
	});

	it("adds nothing before the session has started", async () => {
		const { pi, emit } = mockPi();
		betterTalk(pi);

		const event = agentStartEvent();
		await emit("before_agent_start", event);

		expect(event.systemPromptOptions.sections).toEqual({});
	});
});
