const GITHUB_ACCEPT = "application/vnd.github+json";
const USER_AGENT = "bicycle-road-event-alarm-scheduler";

const DISPATCH_INPUTS = Object.freeze({
  dry_run: "false",
  enable_telegram_publish: "true",
  force_fallback: "true",
  apply_migrations: "false",
});

const SAFE_DRY_RUN_INPUTS = Object.freeze({
  dry_run: "true",
  enable_telegram_publish: "false",
  force_fallback: "true",
  apply_migrations: "false",
});

function requiredEnv(env, name) {
  const value = env[name];
  if (typeof value !== "string" || value.trim() === "") {
    throw new Error(`Missing required environment variable: ${name}`);
  }
  return value.trim();
}

function normalizeGitHubToken(value) {
  const tokenText = value
    .replace(/^(bearer|token)\s+/i, "")
    .replace(/\s+/g, "");
  const tokenMatch = tokenText.match(/(?:github_pat_[A-Za-z0-9_]+|gh[pousr]_[A-Za-z0-9_]+)/);
  return tokenMatch === null ? tokenText : tokenMatch[0];
}

function buildWorkflowUrl(env) {
  const owner = requiredEnv(env, "GITHUB_OWNER");
  const repo = requiredEnv(env, "GITHUB_REPO");
  const workflow = requiredEnv(env, "GITHUB_WORKFLOW");
  const encodedWorkflow = encodeURIComponent(workflow);

  return `https://api.github.com/repos/${owner}/${repo}/actions/workflows/${encodedWorkflow}`;
}

function buildGitHubHeaders(env, authorizationScheme = "Bearer") {
  const token = normalizeGitHubToken(requiredEnv(env, "GITHUB_TOKEN"));

  return {
    Authorization: `${authorizationScheme} ${token}`,
    Accept: GITHUB_ACCEPT,
    "Content-Type": "application/json",
    "User-Agent": USER_AGENT,
  };
}

export function buildWorkflowDispatchRequest(
  env,
  inputs = DISPATCH_INPUTS,
  authorizationScheme = "Bearer",
) {
  const ref = requiredEnv(env, "GITHUB_REF");

  return {
    url: `${buildWorkflowUrl(env)}/dispatches`,
    init: {
      method: "POST",
      headers: buildGitHubHeaders(env, authorizationScheme),
      body: JSON.stringify({
        ref,
        inputs,
      }),
    },
  };
}

export function buildWorkflowStatusRequest(env, authorizationScheme = "Bearer") {
  return {
    url: buildWorkflowUrl(env),
    init: {
      method: "GET",
      headers: buildGitHubHeaders(env, authorizationScheme),
    },
  };
}

export async function triggerWorkflowDispatch(env, fetcher = fetch, inputs = DISPATCH_INPUTS) {
  const request = buildWorkflowDispatchRequest(env, inputs);
  let response = await fetcher(request.url, request.init);
  if (response.status === 400 || response.status === 401) {
    const fallbackRequest = buildWorkflowDispatchRequest(env, inputs, "token");
    response = await fetcher(fallbackRequest.url, fallbackRequest.init);
  }
  if (!response.ok) {
    const body = await response.text();
    throw new Error(`GitHub workflow dispatch failed: ${response.status} ${body}`);
  }
  console.log("GitHub workflow dispatch accepted");
}

async function runScheduledDispatch(env) {
  console.log("Cloudflare scheduled dispatch started");
  try {
    await triggerWorkflowDispatch(env);
    console.log("Cloudflare scheduled dispatch finished");
  } catch (error) {
    console.error("Cloudflare scheduled dispatch failed", error);
    throw error;
  }
}

function isAuthorizedSmokeRequest(request, env) {
  const smokeToken = env.SMOKE_TRIGGER_TOKEN;
  const authorization = request.headers.get("Authorization");
  const normalizedSmokeToken =
    typeof smokeToken === "string" ? smokeToken.trim() : "";

  return (
    normalizedSmokeToken !== "" &&
    authorization === `Bearer ${normalizedSmokeToken}`
  );
}

export async function handleRequest(request, env, fetcher = fetch) {
  const url = new URL(request.url);
  if (
    url.pathname === "/__internal/run-scheduled" &&
    isAuthorizedSmokeRequest(request, env)
  ) {
    await triggerWorkflowDispatch(env, fetcher);
    return new Response("scheduled dispatch accepted", {
      status: 202,
    });
  }

  if (
    url.pathname === "/__internal/run-safe-dry-run" &&
    isAuthorizedSmokeRequest(request, env)
  ) {
    await triggerWorkflowDispatch(env, fetcher, SAFE_DRY_RUN_INPUTS);
    return new Response("safe dry-run dispatch accepted", {
      status: 202,
    });
  }

  if (
    url.pathname === "/__internal/github-workflow-status" &&
    isAuthorizedSmokeRequest(request, env)
  ) {
    const githubRequest = buildWorkflowStatusRequest(env);
    let response = await fetcher(githubRequest.url, githubRequest.init);
    if (response.status === 400 || response.status === 401) {
      const fallbackRequest = buildWorkflowStatusRequest(env, "token");
      response = await fetcher(fallbackRequest.url, fallbackRequest.init);
    }
    return new Response(await response.text(), {
      status: response.status,
      headers: {
        "Content-Type": response.headers.get("Content-Type") || "text/plain",
      },
    });
  }

  if (url.pathname.startsWith("/__internal/")) {
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
    ctx.waitUntil(runScheduledDispatch(env));
  },

  async fetch(request, env) {
    return handleRequest(request, env);
  },
};
