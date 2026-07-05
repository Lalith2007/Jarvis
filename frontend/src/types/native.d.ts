export {};

declare global {
  interface Window {
    jarvisNative?: {
      isNative: true;
      platform: NodeJS.Platform;
      showDashboard: () => Promise<boolean>;
      hideDashboard: () => Promise<boolean>;
      getWakeDiagnostics: () => Promise<any>;
      consumePendingWake: () => Promise<string | null>;
      setWakeState: (awake: boolean) => void;
      logRuntime: (payload: Record<string, unknown>) => void;
      onNativeCommand: (callback: (payload: { type: string }) => void) => () => void;
    };
  }
}
