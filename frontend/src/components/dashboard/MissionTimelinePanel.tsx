import { Workflow, CheckCircle2, Clock, PlayCircle, AlertCircle } from "lucide-react";
import { useMissionEvents } from "../../hooks/useMissionEvents";
import { Panel } from "../ui/Panel";
import { formatTime } from "../../utils/format";
import type { PlatformEvent } from "../../services/platformEvents";

function getEventIcon(eventType: string) {
  if (eventType.includes("Failed") || eventType.includes("Error")) return <AlertCircle size={14} className="error" />;
  if (eventType.includes("Completed")) return <CheckCircle2 size={14} className="success" />;
  if (eventType.includes("Started")) return <PlayCircle size={14} className="info" />;
  return <Clock size={14} className="muted" />;
}

export function MissionTimelinePanel({ missionId }: { missionId?: string }) {
  const { missionEvents, latestStatus } = useMissionEvents(missionId);

  // Group events by stage if needed, but a linear timeline is fine for now
  const timelineEvents = missionEvents.slice(-20); // show last 20

  return (
    <Panel 
      title="Mission Timeline" 
      icon={<Workflow size={15} />}
      action={<span className="micro-copy">{latestStatus ? latestStatus.toUpperCase() : "IDLE"}</span>}
      className="mission-timeline-panel"
    >
      <div className="timeline-container">
        {timelineEvents.length === 0 ? (
          <div className="empty-state">
            <b>No active mission</b>
            <p>Submit a request to JARVIS to start a mission.</p>
          </div>
        ) : (
          <div className="timeline-list">
            {timelineEvents.map((event: PlatformEvent, idx) => (
              <div key={event.id || idx} className="timeline-item">
                <div className="timeline-icon">
                  {getEventIcon(event.event_type)}
                </div>
                <div className="timeline-content">
                  <div className="timeline-header">
                    <b>{event.event_type.replace(/([A-Z])/g, ' $1').trim()}</b>
                    <time>{formatTime(event.timestamp)}</time>
                  </div>
                  <div className="timeline-details">
                    <span className="muted">{event.subsystem}</span>
                    {event.duration_ms && <span className="duration"> • {event.duration_ms}ms</span>}
                  </div>
                  {event.payload && Object.keys(event.payload).length > 0 && (
                    <pre className="timeline-payload">
                      {JSON.stringify(event.payload, null, 2)}
                    </pre>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </Panel>
  );
}
