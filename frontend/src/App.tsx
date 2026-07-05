import { AppProviders } from "./app/providers";

console.log(`[TIMELINE] ${Date.now()} App.tsx executes`);

export function App() {
    console.log(`[TIMELINE] ${Date.now()} App.tsx first render`);
    return (
        <AppProviders />
    );
}

