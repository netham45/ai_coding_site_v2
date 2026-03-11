import { createElement } from "react";
import { RouterProvider } from "react-router-dom";
import { buildBrowserRouter } from "./routes/router.js";

const router = buildBrowserRouter();

export default function App() {
  return createElement(RouterProvider, { router });
}
