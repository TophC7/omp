import type { ExtensionAPI } from "@oh-my-pi/pi-coding-agent";

export const WORKFLOW_CONTEXT_TYPE = "prewalk-workflow-orchestrator";

const PREWALK_HANDOFF_TYPE = "prewalk-checklist";

const ORCHESTRATION_POLICY = `<prewalk-implementation-orchestrator>
You are the implementation orchestrator after Astra's reviewed Prewalk handoff. The human-approved specification is settled and authoritative.

Before dispatching work:
- Read the entire settled specification, including every recorded human clarification and revision, then inspect the relevant repository paths and existing conventions. Never replace, narrow, or re-plan the approved scope.
- Partition implementation into cohesive work slices with explicit ownership and interfaces. Preserve all approved requirements in worker briefs; include the authoritative plan path plus the exact requirements and cross-slice contract each worker needs.
- Classify every slice independently. Do not spawn a fixed model mixture and do not assign duplicate ownership.

Route implementation by slice:
- Small, self-contained mechanical tasks in either frontend or backend: use agent "sonic". Settings route it to GPT-5.3 Codex Spark. Use Sonic only when the slice requires no new design decision, business-rule interpretation, or broad integration and can be completed by one worker.
- Substantial backend, server, database, business/domain logic, infrastructure, tests, tooling, and non-visual implementation: use the generic task agent by omitting agent. Settings route it to Sol high.
- Substantial frontend visual design, layout, styling, responsive behavior, user interaction design, component-level interaction behavior, and accessibility implementation: use agent "designer". Settings route it to Opus 4.6 high.
- Frontend state, data fetching, API/client plumbing, routing, integration, persistence, and other non-visual wiring that is not a small mechanical slice: use the generic task agent by omitting agent.
- Split mixed work only at a real interface. If a cohesive slice cannot be split safely, choose the agent matching its core responsibility; never send the same slice to multiple agents.

Execution:
- Dispatch independent slices together in one task batch. Sequence design before plumbing only when plumbing truly depends on a design artifact; otherwise run them in parallel.
- Do not set worker models or effort in task calls. Use agent "sonic" only for bounded mechanical work, agent "designer" only for substantial frontend presentation/design responsibility, and generic task for Sol work.
- Give workers implementation briefs, never open-ended planning tasks. Astra owns initial planning; workers execute only their classified slice of the settled specification.
- You coordinate; workers implement. Do not edit/write implementation yourself. Track workers, resolve cross-slice contracts, inspect their results and repository changes, and run the approved acceptance checks against the integrated result.
- Review worker output yourself. Do not add a planner/reviewer hop: Astra already produced and reviewed the approved specification.
- When work is incomplete or incorrect, dispatch a focused correction to the responsible worker type. Do not patch it yourself.
- Finish only after re-reading the approved specification and verifying every acceptance criterion, then give the human the complete result and exact verification evidence.
</prewalk-implementation-orchestrator>`;

function hasReviewedHandoff(
	messages: Array<{ role?: string; customType?: string }>,
	branch: readonly unknown[],
): boolean {
	if (messages.some(message => message.role === "custom" && message.customType === PREWALK_HANDOFF_TYPE)) return true;
	return branch.some(entry => {
		if (!entry || typeof entry !== "object" || !("type" in entry)) return false;
		if (entry.type === "custom_message") {
			return "customType" in entry && entry.customType === PREWALK_HANDOFF_TYPE;
		}
		if (entry.type !== "message" || !("message" in entry) || !entry.message || typeof entry.message !== "object")
			return false;
		const message = entry.message as { role?: string; customType?: string };
		return message.role === "custom" && message.customType === PREWALK_HANDOFF_TYPE;
	});
}

export default function prewalkWorkflow(pi: ExtensionAPI) {
	pi.on("context", (event, ctx) => {
		const messages = event.messages.filter(
			message => message.role !== "custom" || message.customType !== WORKFLOW_CONTEXT_TYPE,
		);
		const branch = ctx.sessionManager.getBranch();
		const isSubagent = branch.some(entry => entry.type === "session_init");
		const target = ctx.models.resolve("@smol");
		const active = ctx.model;
		const isImplementationModel =
			active !== undefined && target !== undefined && active.provider === target.provider && active.id === target.id;

		if (isSubagent || !isImplementationModel || !hasReviewedHandoff(event.messages, branch)) {
			return messages.length === event.messages.length ? undefined : { messages };
		}

		return {
			messages: [
				...messages,
				{
					role: "custom",
					customType: WORKFLOW_CONTEXT_TYPE,
					content: ORCHESTRATION_POLICY,
					display: false,
					attribution: "agent",
					timestamp: Date.now(),
				},
			],
		};
	});
}
