import { describe, expect, it } from "vitest";

import { getEmptyFieldsState } from "./empty-state";
import type { CaseRecord } from "../types";

const baseCase: CaseRecord = {
  id: "empty-case",
  name: "Empty case",
  status: "needs_review",
  decision: null,
  progress: 100,
  documents: [],
  fields: [],
  validations: [],
  metadata: {},
  created_at: "2026-08-13T00:00:00Z",
  updated_at: "2026-08-13T00:00:00Z",
};

describe("empty extraction guidance", () => {
  it("explains an unavailable vision provider and links setup guidance", () => {
    const state = getEmptyFieldsState({
      ...baseCase,
      documents: [
        {
          id: "scan",
          file_name: "scan.png",
          media_type: "image/png",
          kind: "unknown",
          kind_label: "Unknown document",
          status: "processed",
          size_bytes: 12,
          page_count: 1,
          fields: [],
          error: null,
        },
      ],
      metadata: { provider_available: false },
    });

    expect(state.kind).toBe("vision-unavailable");
    expect(state.title).toContain("unavailable");
    expect(state.providerHref).toContain("#ai-providers");
  });

  it("gives image guidance when a provider has not been configured", () => {
    const state = getEmptyFieldsState({
      ...baseCase,
      documents: [
        {
          id: "scan",
          file_name: "scan.png",
          media_type: "image/png",
          kind: "unknown",
          kind_label: "Unknown document",
          status: "processed",
          size_bytes: 12,
          page_count: 1,
          fields: [],
          error: null,
        },
      ],
    });

    expect(state.kind).toBe("image-only");
    expect(state.providerHref).toContain("#ai-providers");
  });

  it("does not tell a text-only review to install a vision model", () => {
    const state = getEmptyFieldsState({
      ...baseCase,
      documents: [
        {
          id: "text",
          file_name: "notes.txt",
          media_type: "text/plain",
          kind: "unknown",
          kind_label: "Unknown document",
          status: "processed",
          size_bytes: 12,
          page_count: 1,
          fields: [],
          error: null,
        },
      ],
    });

    expect(state.kind).toBe("text-empty");
    expect(state.providerHref).toBeUndefined();
  });
});
