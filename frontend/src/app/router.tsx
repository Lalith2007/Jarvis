import {
    Navigate,
    RouterProvider,
    createHashRouter,
    createBrowserRouter,
} from "react-router-dom";

import { AppLayout } from "../layout/AppLayout";
import { DashboardPage } from "../pages/DashboardPage";
import { AgentsPage, ChatPage, MissionsPage, ProjectsPage } from "../pages/IntelligencePages";
import { KnowledgePage, MemoryPage, ModelsPage, RuntimePage } from "../pages/SystemPages";
import { AutomationPage, BrowserPage, FilesPage, SettingsPage, TerminalPage } from "../pages/ToolPages";

const createRouter = window.jarvisNative ? createHashRouter : createBrowserRouter;

const router = createRouter([
    {
        path: "/",
        element: <AppLayout />,
        children: [
            {
                index: true,
                element: <Navigate to="/dashboard" replace />,
            },
            {
                path: "dashboard",
                element: <DashboardPage />,
            },
            {
                path: "chat",
                element: <ChatPage />,
            },
            {
                path: "missions",
                element: <MissionsPage />,
            },
            {
                path: "agents",
                element: <AgentsPage />,
            },
            {
                path: "runtime",
                element: <RuntimePage />,
            },
            {
                path: "memory",
                element: <MemoryPage />,
            },
            {
                path: "knowledge",
                element: <KnowledgePage />,
            },
            {
                path: "files",
                element: <FilesPage />,
            },
            {
                path: "browser",
                element: <BrowserPage />,
            },
            {
                path: "terminal",
                element: <TerminalPage />,
            },
            {
                path: "models",
                element: <ModelsPage />,
            },
            {
                path: "projects",
                element: <ProjectsPage />,
            },
            {
                path: "automation",
                element: <AutomationPage />,
            },
            {
                path: "settings",
                element: <SettingsPage />,
            },
            { path: "*", element: <Navigate to="/dashboard" replace /> },
        ],
    },
]);

console.log("[DIAGNOSIS] router.tsx executes");

export function AppRouter() {
  console.log("[DIAGNOSIS] AppRouter component renders, returning RouterProvider");
  return <RouterProvider router={router} />;
}

