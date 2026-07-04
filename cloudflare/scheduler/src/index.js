const GITHUB_API_VERSION = "2022-11-28";
const GITHUB_ACCEPT = "application/vnd.github+json";
const USER_AGENT = "bicycle-road-event-alarm-scheduler";

const DISPATCH_INPUTS = Object.freeze({
  dry_run: "false",
  enable_telegram_publish: "true",
  force_fallback: "false",
  apply_migrations: "false",
});

function requiredEnv(env, name) {
  const value = env[name];
  if (typeof value !== "string" || value.trim() === "") {
    throw new Error(`Missing required environment variable: ${name}`);
  }
  return value;
}

export function buildWorkflowDispatchRequest(env) {
  const owner = requiredEnv(env, "GITHUB_OWNER");
  const repo = requiredEnv(env, "GITHUB_REPO");
  const workflow = requiredEnv(env, "GITHUB_WORKFLOW");
  const ref = requiredEnv(env, "GITHUB_REF");
  const token = requiredEnv(env, "GITHUB_TOKEN");
  const encodedWorkflow = encodeURIComponent(workflow);

  return {
    url: `https://api.github.com/repos/${owner}/${repo}/actions/workflows/${encodedWorkflow}/dispatches`,
    init: {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        Accept: GITHUB_ACCEPT,
        "Content-Type": "application/json",
        "X-GitHub-Api-Version": GITHUB_API_VERSION,
        "User-Agent": USER_AGENT,
      },
      body: JSON.stringify({
        ref,
        inputs: DISPATCH_INPUTS,
      }),
    },
  };
}

export async function triggerWorkflowDispatch(env, fetcher = fetch) {
  const request = buildWorkflowDispatchRequest(env);
  const response = await fetcher(request.url, request.init);
  if (!response.ok) {
    const body = await response.text();
    throw new Error(`GitHub workflow dispatch failed: ${response.status} ${body}`);
  }
}

export async function handleRequest(request, env, fetcher = fetch) {
  const url = new URL(request.url);
  const smokeToken = env.SMOKE_TRIGGER_TOKEN;
  const authorization = request.headers.get("Authorization");
  if (
    url.pathname === "/__internal/run-scheduled" &&
    typeof smokeToken === "string" &&
    smokeToken.trim() !== "" &&
    authorization === `Bearer ${smokeToken}`
  ) {
    await triggerWorkflowDispatch(env, fetcher);
    return new Response("scheduled dispatch accepted", {
      status: 202,
    });
  }

  if (url.pathname === "/__internal/run-scheduled") {
    return new Response("not found", {
      status: 404,
    });
  }

  return new Response("bicycle-road-event-alarm scheduler is deployed", {
    status: 200,
  });
}

export default {
  async scheduled(_event, env, ctx) {
    ctx.waitUntil(triggerWorkflowDispatch(env));
  },

  async fetch(request, env) {
    return handleRequest(request, env);
  },
};
