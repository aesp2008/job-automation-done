import { describe, expect, it } from "vitest";

import { getBackendUrl } from "./api";

describe("getBackendUrl", () => {
  it("returns a usable URL string", () => {
    const url = getBackendUrl();
    expect(typeof url).toBe("string");
    expect(url.length).toBeGreaterThan(0);
    expect(url.startsWith("http")).toBe(true);
  });
});

