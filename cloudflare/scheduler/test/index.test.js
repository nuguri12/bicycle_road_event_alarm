import assert from "node:assert/strict";
import { test } from "node:test";

import {
  default as worker,
  buildWorkflowDispatchRequest,
  buildWorkflowStatusRequest,
  handleRequest,
  triggerWorkflowDispatch,
} from "../src/index.js";

const env = {
  GITHUB_TOKEN: "github-token",
  GITHUB_OWNER: "nuguri12",
  GITHUB_REPO: "bicycle_road_event_alarm",
  GITHUB_WORKFLOW: "manual-batch.yml",
  GITHUB_REF: "main",
};

test("buildWorkflowDispatchRequest creates real publish dispatch request", () => {
  const request = buildWorkflowDispatchRequest(env);

  assert.equal(
    request.url,
    "https://api.github.com/repos/nuguri12/bicycle_road_event_alarm/actions/workflows/manual-batch.yml/dispatches",
  );
  assert.equal(request.init.method, "POST");
  assert.equal(request.init.headers.Authorization, "Bearer github-token");
  assert.equal(request.init.headers.Accept, "application/vnd.github+json");
  assert.equal(request.init.headers["X-GitHub-Api-Version"], undefined);
  assert.deepEqual(JSON.parse(request.init.body), {
    ref: "main",
    inputs: {
      dry_run: "false",
      enable_telegram_publish: "true",
      force_fallback: "false",
      apply_migrations: "false",
    },
  });
});

test("buildWorkflowDispatchRequest trims environment values", () => {
  const request = buildWorkflowDispatchRequest({
    ...env,
    GITHUB_TOKEN: "GITHUB_TOKEN='github_pat_abc_DEF123'",
    GITHUB_REF: "main\n",
  });

  assert.equal(request.init.headers.Authorization, "Bearer github_pat_abc_DEF123");
  assert.deepEqual(JSON.parse(request.init.body), {
    ref: "main",
    inputs: {
      dry_run: "false",
      enable_telegram_publish: "true",
      force_fallback: "false",
      apply_migrations: "false",
    },
  });
});

test("buildWorkflowStatusRequest creates workflow lookup request", () => {
  const request = buildWorkflowStatusRequest(env);

  assert.equal(
    request.url,
    "https://api.github.com/repos/nuguri12/bicycle_road_event_alarm/actions/workflows/manual-batch.yml",
  );
  assert.equal(request.init.method, "GET");
  assert.equal(request.init.headers.Authorization, "Bearer github-token");
});

test("triggerWorkflowDispatch throws when GitHub rejects the dispatch", async () => {
  const fetchCalls = [];
  const failingFetch = async (url, init) => {
    fetchCalls.push({ url, init });
    return {
      ok: false,
      status: 401,
      text: async () => "Bad credentials",
    };
  };

  await assert.rejects(
    () => triggerWorkflowDispatch(env, failingFetch),
    /GitHub workflow dispatch failed: 401 Bad credentials/,
  );
  assert.equal(fetchCalls.length, 2);
  assert.equal(fetchCalls[1].init.headers.Authorization, "token github-token");
});

test("triggerWorkflowDispatch retries with token auth after bearer failure", async () => {
  const fetchCalls = [];
  const fetcher = async (url, init) => {
    fetchCalls.push({ url, init });
    return {
      ok: fetchCalls.length === 2,
      status: fetchCalls.length === 1 ? 400 : 204,
      text: async () => "",
    };
  };

  await triggerWorkflowDispatch(env, fetcher);

  assert.equal(fetchCalls.length, 2);
  assert.equal(fetchCalls[0].init.headers.Authorization, "Bearer github-token");
  assert.equal(fetchCalls[1].init.headers.Authorization, "token github-token");
});

test("handleRequest runs dispatch for authorized smoke trigger", async () => {
  const fetchCalls = [];
  const okFetch = async (url, init) => {
    fetchCalls.push({ url, init });
    return {
      ok: true,
      text: async () => "",
    };
  };
  const response = await handleRequest(
    new Request("https://worker.example/__internal/run-scheduled", {
      headers: { Authorization: "Bearer smoke-token" },
    }),
    { ...env, SMOKE_TRIGGER_TOKEN: "smoke-token" },
    okFetch,
  );

  assert.equal(response.status, 202);
  assert.equal(await response.text(), "scheduled dispatch accepted");
  assert.equal(fetchCalls.length, 1);
});

test("handleRequest trims smoke trigger secret", async () => {
  const fetchCalls = [];
  const okFetch = async (url, init) => {
    fetchCalls.push({ url, init });
    return {
      ok: true,
      text: async () => "",
    };
  };
  const response = await handleRequest(
    new Request("https://worker.example/__internal/run-scheduled", {
      headers: { Authorization: "Bearer smoke-token" },
    }),
    { ...env, SMOKE_TRIGGER_TOKEN: "smoke-token\n" },
    okFetch,
  );

  assert.equal(response.status, 202);
  assert.equal(fetchCalls.length, 1);
});

test("handleRequest runs safe dry-run dispatch for authorized smoke trigger", async () => {
  const fetchCalls = [];
  const okFetch = async (url, init) => {
    fetchCalls.push({ url, init });
    return {
      ok: true,
      text: async () => "",
    };
  };
  const response = await handleRequest(
    new Request("https://worker.example/__internal/run-safe-dry-run", {
      headers: { Authorization: "Bearer smoke-token" },
    }),
    { ...env, SMOKE_TRIGGER_TOKEN: "smoke-token" },
    okFetch,
  );

  assert.equal(response.status, 202);
  assert.deepEqual(JSON.parse(fetchCalls[0].init.body), {
    ref: "main",
    inputs: {
      dry_run: "true",
      enable_telegram_publish: "false",
      force_fallback: "true",
      apply_migrations: "false",
    },
  });
});

test("handleRequest proxies GitHub workflow status for authorized smoke trigger", async () => {
  const response = await handleRequest(
    new Request("https://worker.example/__internal/github-workflow-status", {
      headers: { Authorization: "Bearer smoke-token" },
    }),
    { ...env, SMOKE_TRIGGER_TOKEN: "smoke-token" },
    async () =>
      new Response('{"state":"active"}', {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }),
  );

  assert.equal(response.status, 200);
  assert.equal(await response.text(), '{"state":"active"}');
});

test("handleRequest rejects smoke trigger without token", async () => {
  const response = await handleRequest(
    new Request("https://worker.example/__internal/run-scheduled"),
    { ...env, SMOKE_TRIGGER_TOKEN: "smoke-token" },
  );

  assert.equal(response.status, 404);
  assert.equal(await response.text(), "not found");
});

test("scheduled dispatches the workflow through waitUntil", async () => {
  const fetchCalls = [];
  const okFetch = async (url, init) => {
    fetchCalls.push({ url, init });
    return {
      ok: true,
      text: async () => "",
    };
  };
  const waitUntilCalls = [];
  const originalFetch = globalThis.fetch;
  globalThis.fetch = okFetch;
  try {
    await worker.scheduled({}, env, {
      waitUntil(promise) {
        waitUntilCalls.push(promise);
      },
    });
    assert.equal(waitUntilCalls.length, 1);
    await waitUntilCalls[0];
  } finally {
    globalThis.fetch = originalFetch;
  }

  assert.equal(fetchCalls.length, 1);
});
