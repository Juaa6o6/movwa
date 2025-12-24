import { describe, it, expect } from "vitest";

const makeClickHandler = (status) => () =>
  status === "rated" ? "clear-rate" : null;

describe("MovieActions rate button handler", () => {
  it("returns clear-rate when status is rated", () => {
    const onClick = makeClickHandler("rated");
    expect(onClick()).toBe("clear-rate");
  });

  it("returns null when status is not rated", () => {
    const onClick = makeClickHandler(null);
    expect(onClick()).toBeNull();
  });
});
