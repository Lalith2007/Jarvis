import type { ReactNode } from "react";
import { clsx } from "clsx";

interface PanelProps {
  title?: string;
  eyebrow?: string;
  action?: ReactNode;
  icon?: ReactNode;
  children: ReactNode;
  className?: string;
  contentClassName?: string;
}

export function Panel({ title, eyebrow, action, icon, children, className, contentClassName }: PanelProps) {
  return (
    <section className={clsx("panel", className)}>
      {(title || action) && (
        <header className="panel-header">
          <div className="panel-title-wrap">
            {icon && <span className="panel-icon">{icon}</span>}
            <div>
              {eyebrow && <span className="eyebrow">{eyebrow}</span>}
              {title && <h2 className="panel-title">{title}</h2>}
            </div>
          </div>
          {action && <div className="panel-action">{action}</div>}
        </header>
      )}
      <div className={clsx("panel-content", contentClassName)}>{children}</div>
    </section>
  );
}

export function StatusDot({ status }: { status: string }) {
  return <span className={`status-dot status-${status}`} aria-label={status} />;
}

