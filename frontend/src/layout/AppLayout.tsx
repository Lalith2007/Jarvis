import { Outlet } from "react-router-dom";
import { CommandPalette } from "../components/layout/CommandPalette";
import { Sidebar } from "../components/layout/Sidebar";
import { Topbar } from "../components/layout/Topbar";
import { ErrorBoundary } from "../components/ui/ErrorBoundary";

console.log("[DIAGNOSIS] AppLayout.tsx executes");

export function AppLayout() {
  console.log("[DIAGNOSIS] AppLayout component renders");
  return (
    <div className="app-shell">
      <ErrorBoundary name="Sidebar"><Sidebar /></ErrorBoundary>
      <div className="app-workspace">
        <ErrorBoundary name="Topbar"><Topbar /></ErrorBoundary>
        <main id="main-content" className="page-stage">
          <ErrorBoundary name="PageContent"><Outlet /></ErrorBoundary>
        </main>
      </div>
      <ErrorBoundary name="CommandPalette"><CommandPalette /></ErrorBoundary>
    </div>
  );
}
