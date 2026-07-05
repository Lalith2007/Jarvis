import { Search, X } from "lucide-react";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useJarvisStore } from "../../stores/use-jarvis-store";

const commands = [
  ["Open dashboard", "/dashboard"], ["Start a conversation", "/chat"], ["Inspect missions", "/missions"],
  ["View active agents", "/agents"], ["Open runtime", "/runtime"], ["Search memory", "/memory"],
  ["Open browser", "/browser"], ["Open terminal", "/terminal"], ["Manage models", "/models"],
];

export function CommandPalette() {
  const open = useJarvisStore((state) => state.commandPaletteOpen);
  const setOpen = useJarvisStore((state) => state.setCommandPaletteOpen);
  const [query, setQuery] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    const handleKey = (event: KeyboardEvent) => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") { event.preventDefault(); setOpen(!open); }
      if (event.key === "Escape") setOpen(false);
    };
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [open, setOpen]);

  if (!open) return null;
  const filtered = commands.filter(([label]) => label.toLowerCase().includes(query.toLowerCase()));
  const choose = (path: string) => { navigate(path); setOpen(false); setQuery(""); };
  return (
    <div className="palette-backdrop" role="presentation" onMouseDown={() => setOpen(false)}>
      <div className="command-palette" role="dialog" aria-modal="true" aria-label="Command palette" onMouseDown={(event) => event.stopPropagation()}>
        <div className="palette-input"><Search size={18} /><input autoFocus value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search systems and commands…" /><button className="icon-button" onClick={() => setOpen(false)} aria-label="Close"><X size={17} /></button></div>
        <div className="palette-results">
          {filtered.map(([label, path]) => <button key={path} onClick={() => choose(path)}><span>{label}</span><small>{path}</small></button>)}
        </div>
      </div>
    </div>
  );
}

