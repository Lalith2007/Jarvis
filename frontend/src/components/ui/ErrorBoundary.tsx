import { Component, type ErrorInfo, type ReactNode } from "react";

interface Props {
  children: ReactNode;
  /** Rendered instead of the crashed tree. Defaults to a generic fallback. */
  fallback?: ReactNode;
  /** Optional label shown in the fallback (e.g. "Dashboard", "Sidebar") */
  name?: string;
}

interface State {
  error: Error | null;
}

/**
 * Catches runtime exceptions in any React subtree so a single widget crash
 * never tears down the entire application shell.
 */
export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { error };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error(`[ErrorBoundary:${this.props.name ?? "unknown"}] Caught error:`, error, info.componentStack);
  }

  reset = () => this.setState({ error: null });

  render() {
    if (this.state.error) {
      if (this.props.fallback) return this.props.fallback;
      return (
        <div className="error-boundary-fallback" role="alert">
          <span>⚠</span>
          <div>
            <strong>{this.props.name ?? "Component"} crashed</strong>
            <code>{this.state.error.message}</code>
            <button onClick={this.reset}>Retry</button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}
