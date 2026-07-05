console.log(`[TIMELINE] ${Date.now()} main.tsx before imports`);
import React from "react";
import ReactDOM from "react-dom/client";

window.addEventListener("error", (event) => {
    console.error("[RENDERER FATAL ERROR]", event.error?.message || event.message, "\\nStack:", event.error?.stack, "\\nFile:", event.filename, "Line:", event.lineno);
});

window.addEventListener("unhandledrejection", (event) => {
    console.error("[RENDERER UNHANDLED PROMISE]", event.reason);
});

console.log(`[TIMELINE] ${Date.now()} main.tsx executes`);

import { App } from "./App";
import "./index.css";

console.log(`[TIMELINE] ${Date.now()} main.tsx before createRoot`);
const root = ReactDOM.createRoot(document.getElementById("root")!);
console.log(`[TIMELINE] ${Date.now()} main.tsx after createRoot`);
try {
  root.render(
      <React.StrictMode>
          <App />
      </React.StrictMode>
  );
  console.log(`[TIMELINE] ${Date.now()} main.tsx after render`);
} catch (error: any) {
  console.error(`[TIMELINE] ${Date.now()} React crash:`, error.stack || error);
}

setTimeout(() => {
    const root = document.getElementById("root");
    console.log("[DIAGNOSIS] Body HTML length:", document.body.innerHTML.length);
    console.log("[DIAGNOSIS] Root HTML length:", root?.innerHTML.length);
    if (root && root.innerHTML.length < 500) {
        console.log("[DIAGNOSIS] Root HTML snippet:", root.innerHTML.substring(0, 500));
    }
}, 2000);


