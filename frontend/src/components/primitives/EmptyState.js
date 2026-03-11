import { createElement } from "react";

export default function EmptyState({ title = "No data yet", body = "This panel has not been populated yet." }) {
  return createElement(
    "div",
    {
      className: "state-card state-card--empty",
      "data-testid": "empty-state",
    },
    createElement("strong", null, title),
    createElement("p", null, body),
  );
}
