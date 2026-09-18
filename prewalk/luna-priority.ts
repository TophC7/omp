import type { ExtensionAPI } from "@oh-my-pi/pi-coding-agent";

export default function lunaPriority(pi: ExtensionAPI) {
	pi.on("before_provider_request", (event, ctx) => {
		if (ctx.model?.provider !== "openai-codex" || ctx.model.id !== "gpt-5.6-luna") return;
		// Codex ignores compat.extraBody; set the tier on its outgoing payload instead.
		return { ...(event.payload as Record<string, unknown>), service_tier: "priority" };
	});
}
