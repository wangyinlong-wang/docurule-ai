import { beforeEach, describe, expect, it } from "vitest";

import { resetShowcase, showcaseApi } from "./showcase";

describe("static showcase", () => {
  beforeEach(() => resetShowcase());

  it("opens the deterministic procurement case", async () => {
    const item = await showcaseApi.createProcurementDemo();

    expect(item.documents).toHaveLength(3);
    expect(item.fields).toHaveLength(8);
    expect(item.validations.filter((result) => result.status === "passed")).toHaveLength(4);
    expect(item.validations.filter((result) => result.status === "failed")).toHaveLength(2);
    expect((await showcaseApi.listCases())[0].id).toBe(item.id);
  });

  it("recomputes the six rules after the reviewer correction", async () => {
    const item = await showcaseApi.createProcurementDemo();
    const corrected = await showcaseApi.updateField(item.id, "received_quantity", 96);

    expect(corrected.validations.every((result) => result.status === "passed")).toBe(true);
    expect(corrected.fields.find((field) => field.key === "received_quantity")).toMatchObject({
      value: 96,
      reviewed: true,
      confidence: 1,
    });
    expect((corrected.metadata.audit_log as Array<{ action: string }>)[0].action).toBe(
      "field_updated",
    );
  });

  it("stores a human decision only in the browser-local case", async () => {
    const item = await showcaseApi.createProcurementDemo();
    const reviewed = await showcaseApi.review(item.id, "approved");

    expect(reviewed.status).toBe("approved");
    expect(reviewed.decision).toBe("approved");
    expect((reviewed.metadata.audit_log as Array<{ action: string }>)[0].action).toBe(
      "review_decision",
    );
  });
});
