import { createElement } from "react";

export default function ErrorState({ title = "Unable to load", body = "This is a placeholder error surface." }) {
  return createElement(
    "div",
    {
      className: "state-card state-card--error",
      "data-testid": "error-state",
      role: "alert",
    },
    createElement("strong", null, title),
    createElement("p", null, body),
  );
}
