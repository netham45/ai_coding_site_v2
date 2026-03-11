import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.js";
import QueryProvider from "./lib/query/QueryProvider.js";
import "./styles.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <QueryProvider>
      <App />
    </QueryProvider>
  </React.StrictMode>,
);
