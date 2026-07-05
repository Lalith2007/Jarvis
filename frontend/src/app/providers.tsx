import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "react-hot-toast";

import { AppRouter } from "./router";

const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            retry: 1,
            refetchOnWindowFocus: false,
            staleTime: 30_000,
        },
    },
});

console.log("[DIAGNOSIS] providers.tsx executes");

export function AppProviders() {
    console.log("[DIAGNOSIS] AppProviders component renders");
    return (
        <QueryClientProvider client={queryClient}>
            <AppRouter />
            <Toaster position="bottom-right" toastOptions={{ className: "jarvis-toast" }} />
        </QueryClientProvider>
    );
}
