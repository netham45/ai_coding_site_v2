import { createElement } from "react";

export default function StatusBadge({ label = "ready", tone = "info" }) {
  return createElement(
    "span",
    {
      className: `status-badge status-badge--${tone}`,
      "data-testid": `status-badge-${label.toLowerCase().replace(/\s+/g, "-")}`,
    },
    label,
  );
}
