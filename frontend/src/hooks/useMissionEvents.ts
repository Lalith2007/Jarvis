import { useMemo } from "react";
import { usePlatformEvents } from "./usePlatformEvents";
import type { PlatformEvent } from "../services/platformEvents";

/**
 * Filter Platform Events by mission_id.
 *
 * When mission_id is null/undefined, returns all events.
 */
export function useMissionEvents(missionId?: string | null) {
  const { events } = usePlatformEvents();

  const missionEvents = useMemo<PlatformEvent[]>(() => {
    if (!missionId) return events;
    return events.filter((e) => e.mission_id === missionId);
  }, [events, missionId]);

  // Derive current status from the latest mission event
  const latestStatus = useMemo<string | null>(() => {
    if (!missionId) return null;
    const relevantEvents = missionEvents
      .filter((e) => e.subsystem === "mission")
      .reverse();
    const statusMap: Record<string, string> = {
      MissionCreated: "created",
      MissionStarted: "analyzing",
      PlanningStarted: "planning",
      ExecutionStarted: "executing",
      MissionCompleted: "completed",
      MissionFailed: "failed",
    };
    for (const event of relevantEvents) {
      if (event.event_type in statusMap) {
        return statusMap[event.event_type];
      }
    }
    return null;
  }, [missionEvents, missionId]);

  return { missionEvents, latestStatus };
}
