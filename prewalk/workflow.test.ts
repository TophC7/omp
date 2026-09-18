import { describe, expect, it } from "bun:test";
import type { ExtensionAPI } from "@oh-my-pi/pi-coding-agent";
import prewalkWorkflow, { WORKFLOW_CONTEXT_TYPE } from "./workflow/index";

type Message = { role: string; customType?: string; [key: string]: unknown };
type ContextHandler = (
	event: { type: "context"; messages: Message[] },
	ctx: {
		model?: { provider: string; id: string };
		models: { resolve(spec: string): { provider: string; id: string } | undefined };
		sessionManager: { getBranch(): Array<Record<string, unknown>> };
	},
) => Promise<{ messages?: Message[] } | undefined> | { messages?: Message[] } | undefined;

const gemini = { provider: "google-antigravity", id: "gemini-3.8-flash" };
const astra = { provider: "openai-codex", id: "gpt-6-astra" };
const sol = { provider: "openai-codex", id: "gpt-5.6-sol" };
const handoff: Message = { role: "custom", customType: "prewalk-checklist" };
const handoffEntry = { type: "custom_message", customType: "prewalk-checklist" };

function installContextHandler(): ContextHandler {
	let handler: ContextHandler | undefined;
	const api = {
		on(event: string, candidate: ContextHandler) {
			if (event === "context") handler = candidate;
		},
	};
	prewalkWorkflow(api as unknown as ExtensionAPI);
	if (!handler) throw new Error("Workflow extension did not register its context handler");
	return handler;
}

function context(model: typeof gemini | undefined, branch: Array<Record<string, unknown>> = []) {
	return {
		model,
		models: { resolve: (spec: string) => (spec === "@smol" ? gemini : undefined) },
		sessionManager: { getBranch: () => branch },
	};
}

function policyCount(messages: Message[] | undefined): number {
	return (
		messages?.filter(message => message.role === "custom" && message.customType === WORKFLOW_CONTEXT_TYPE).length ?? 0
	);
}

describe("Prewalk workflow orchestration scope", () => {
	it("starts only after the Gemini handoff and stays single-copy on later and resumed requests", async () => {
		const handler = installContextHandler();

		expect(await handler({ type: "context", messages: [] }, context(gemini))).toBeUndefined();
		expect(await handler({ type: "context", messages: [handoff] }, context(astra))).toBeUndefined();

		const handedOff = await handler({ type: "context", messages: [handoff] }, context(gemini));
		expect(policyCount(handedOff?.messages)).toBe(1);

		const later = await handler(
			{ type: "context", messages: handedOff?.messages ?? [] },
			context(gemini, [handoffEntry]),
		);
		expect(policyCount(later?.messages)).toBe(1);

		const resumed = await handler({ type: "context", messages: [] }, context(gemini, [handoffEntry]));
		expect(policyCount(resumed?.messages)).toBe(1);
	});

	it("removes orchestration policy from non-Gemini and subagent requests", async () => {
		const handler = installContextHandler();
		const injected = await handler({ type: "context", messages: [handoff] }, context(gemini));
		const messages = injected?.messages ?? [];

		const switched = await handler({ type: "context", messages }, context(sol, [handoffEntry]));
		expect(policyCount(switched?.messages)).toBe(0);

		const childBranch = [{ type: "session_init" }, handoffEntry];
		const child = await handler({ type: "context", messages }, context(gemini, childBranch));
		expect(policyCount(child?.messages)).toBe(0);
	});
});
