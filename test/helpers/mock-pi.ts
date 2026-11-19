// Minimal fake ExtensionAPI: records handlers registered with pi.on() so a test
// can fire events without a real Pi session.
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

type Handler = (event: unknown, ctx: unknown) => unknown;

export function mockPi() {
	const handlers = new Map<string, Handler[]>();

	const pi = {
		on(event: string, handler: Handler) {
			const list = handlers.get(event) ?? [];
			list.push(handler);
			handlers.set(event, list);
		},
	};

	return {
		pi: pi as unknown as ExtensionAPI,
		/** Run every handler for an event in registration order and return their results. */
		async emit(event: string, payload: unknown = {}, ctx: unknown = {}) {
			const results: unknown[] = [];
			for (const handler of handlers.get(event) ?? []) {
				results.push(await handler(payload, ctx));
			}
			return results;
		},
	};
}
