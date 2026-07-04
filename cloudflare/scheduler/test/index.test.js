import assert from "node:assert/strict";
import { test } from "node:test";

import {
  buildWorkflowDispatchRequest,
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
  assert.equal(request.init.headers["X-GitHub-Api-Version"], "2022-11-28");
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
  assert.equal(fetchCalls.length, 1);
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

test("handleRequest rejects smoke trigger without token", async () => {
  const response = await handleRequest(
    new Request("https://worker.example/__internal/run-scheduled"),
    { ...env, SMOKE_TRIGGER_TOKEN: "smoke-token" },
  );

  assert.equal(response.status, 404);
  assert.equal(await response.text(), "not found");
});
