import { createElement } from "react";

export default function LoadingState({ label = "Loading content" }) {
  return createElement(
    "div",
    {
      className: "state-card state-card--loading",
      "data-testid": "loading-state",
      role: "status",
    },
    createElement("strong", null, "Loading"),
    createElement("p", null, label),
  );
}
