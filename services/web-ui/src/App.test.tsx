import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import App from "./App";

describe("App", () => {
  it("makes the synthetic and human-review boundaries visible", () => {
    render(<App />);
    expect(screen.getByText(/Synthetic demonstration/)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Run assisted assessment/ })).toBeInTheDocument();
    expect(screen.getByText(/Human decision required/)).toBeInTheDocument();
  });
});

