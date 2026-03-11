import { createElement } from "react";
import { QueryClientProvider } from "@tanstack/react-query";
import { queryClient } from "./client.js";

export default function QueryProvider({ children }) {
  return createElement(QueryClientProvider, { client: queryClient }, children);
}
