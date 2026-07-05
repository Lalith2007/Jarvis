import { useEffect, useState } from "react";
import { ChatPanel } from "../components/dashboard/ChatPanel";
import { DiagnosticsPanel } from "../components/dashboard/DiagnosticsPanel";
import { MissionTimelinePanel } from "../components/dashboard/MissionTimelinePanel";
import {
  AgentsPanel, BackendNotice, BottomPanels, CapabilitiesPanel,
  LiveMetricsPanel, MissionQueuePanel, ProjectPanel, ResourcePanel,
  ServicesPanel, TerminalPanel,
} from "../components/dashboard/DashboardWidgets";
import { JarvisRuntimePanel } from "../components/reactor/JarvisRuntimePanel";
import { ReactorCore } from "../components/reactor/ReactorCore";
import { ErrorBoundary } from "../components/ui/ErrorBoundary";

function W({ name, children }: { name: string; children: React.ReactNode }) {
  return <ErrorBoundary name={name}>{children}</ErrorBoundary>;
}

console.log(`[TIMELINE] ${Date.now()} DashboardPage.tsx executes`);

export function DashboardPage() {
  console.log(`[TIMELINE] ${Date.now()} DashboardPage component renders`);
  const [showDiagnostics, setShowDiagnostics] = useState(false);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Toggle on Ctrl+Shift+D or Cmd+Shift+D
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key.toLowerCase() === "d") {
        e.preventDefault();
        setShowDiagnostics((prev) => !prev);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  return (
    <div className="dashboard-page">
      {showDiagnostics && (
        <div className="developer-console-overlay" style={{ 
          position: 'fixed', 
          top: '20px', 
          bottom: '20px', 
          right: '20px', 
          zIndex: 9999, 
          width: '400px', 
          background: 'var(--panel-bg)', 
          border: '1px solid var(--border)', 
          borderRadius: '8px', 
          boxShadow: '0 8px 32px rgba(0,0,0,0.8)',
          display: 'flex',
          flexDirection: 'column',
          gap: '16px',
          padding: '16px',
          overflowY: 'auto'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3 style={{ margin: 0, fontSize: '14px', color: 'var(--text)' }}>Developer Console</h3>
            <button className="icon-button" onClick={() => setShowDiagnostics(false)} aria-label="Close Developer Console">
              ✕
            </button>
          </div>
          <DiagnosticsPanel />
          <MissionTimelinePanel />
        </div>
      )}
      <W name="BackendNotice"><BackendNotice /></W>
      <div className="dashboard-primary">
        <div className="dashboard-left">
          <W name="ResourcePanel"><ResourcePanel /></W>
          <W name="CapabilitiesPanel"><CapabilitiesPanel /></W>
        </div>
        <div className="reactor-panel">
          <W name="ReactorCore"><ReactorCore /></W>
          <W name="JarvisRuntimePanel"><JarvisRuntimePanel /></W>
        </div>
        <div className="dashboard-right">
          <W name="ProjectPanel"><ProjectPanel /></W>
          <W name="AgentsPanel"><AgentsPanel /></W>
          <W name="MissionQueuePanel"><MissionQueuePanel /></W>
        </div>
      </div>
      <div className="dashboard-secondary">
        <W name="ServicesPanel"><ServicesPanel /></W>
        <W name="TerminalPanel"><TerminalPanel /></W>
        <W name="LiveMetricsPanel"><LiveMetricsPanel /></W>
        <W name="ChatPanel"><ChatPanel /></W>
      </div>
      <div className="dashboard-bottom">
        <W name="BottomPanels"><BottomPanels /></W>
      </div>
    </div>
  );
}
