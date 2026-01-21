import Link from "next/link";
import type { LucideIcon } from "lucide-react";
import {
  Activity,
  LayoutDashboard,
  LifeBuoy,
  Settings,
  Shield,
  User2,
  Users,
  LineChart,
  CheckCheck,
  Building,
  Stethoscope,
} from "lucide-react";

import type { NavSection } from "@/lib/types";

const iconMap: Record<string, LucideIcon> = {
  "layout-dashboard": LayoutDashboard,
  activity: Activity,
  users: Users,
  shield: Shield,
  "life-buoy": LifeBuoy,
  "line-chart": LineChart,
  check: CheckCheck,
  building: Building,
  stethoscope: Stethoscope,
};

const getIcon = (iconKey?: string) => iconMap[iconKey ?? ""] ?? LayoutDashboard;

type SidebarProps = {
  navSections: NavSection[];
  userName?: string | null;
  className?: string;
};

export default function DashboardSidebar({
  navSections = [],
  userName,
  className = "",
}: SidebarProps) {
  return (
    <div className={`lg:sticky lg:top-10 ${className}`.trim()}>
      <div className="flex h-full min-h-[24rem] flex-col rounded-3xl bg-sidebar/90 p-6 text-sidebar-foreground shadow-lg ring-1 ring-sidebar-border/80 lg:h-[calc(100vh-5rem)] lg:min-h-[calc(100vh-5rem)] lg:max-h-[calc(100vh-5rem)] lg:overflow-hidden">
        <div className="flex shrink-0 items-center gap-3 text-lg font-semibold">
          <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-sidebar-primary text-sidebar-primary-foreground">
            <LayoutDashboard className="h-4 w-4" />
          </div>
          <div>
            <p>SKNV</p>
            <p className="text-xs font-normal text-sidebar-foreground/70">
              Nextgen Portal
            </p>
          </div>
        </div>
        <div className="mt-6 flex-1 min-h-0 overflow-hidden">
          <div className="flex h-full flex-col overflow-y-auto pr-2">
            {navSections.map((section, sectionIndex) => (
              <div key={section.section} className="mt-6 first:mt-0">
                <p className="text-xs uppercase tracking-wide text-sidebar-foreground/60">
                  {section.section}
                </p>
                <nav className="mt-3 space-y-1">
                  {section.links.map((link, linkIndex) => {
                    const Icon = getIcon(link.icon);
                    return (
                      <Link
                        key={link.href}
                        href={link.href}
                        className="flex items-center gap-3 rounded-2xl px-4 py-2.5 text-sm font-medium text-sidebar-foreground transition-colors hover:bg-sidebar-accent data-[active=true]:bg-sidebar-primary data-[active=true]:text-sidebar-primary-foreground"
                        data-active={sectionIndex === 0 && linkIndex === 0}
                      >
                        <Icon className="h-4 w-4" />
                        <span>{link.label}</span>
                      </Link>
                    );
                  })}
                </nav>
              </div>
            ))}
            <div className="flex-1" />
            <div className="space-y-4">
              <div className="rounded-2xl border border-sidebar-border bg-sidebar-accent/40 p-4 text-sm">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-sidebar-primary/30 text-sidebar-primary">
                    <User2 className="h-5 w-5" />
                  </div>
                  <div>
                    <p className="text-sm font-semibold">
                      {userName ?? "Guest"}
                    </p>
                    <p className="text-xs text-sidebar-foreground/70">
                      Profile
                    </p>
                  </div>
                </div>
                <div className="mt-4 grid gap-2">
                  <Link
                    href="/settings"
                    className="inline-flex items-center gap-2 rounded-xl border border-sidebar-border px-3 py-2 text-xs font-medium"
                  >
                    <Settings className="h-4 w-4" />
                    Settings
                  </Link>
                  <Link
                    href="/logout"
                    className="inline-flex items-center justify-center gap-2 rounded-xl border border-sidebar-border px-3 py-2 text-sm font-semibold"
                  >
                    Log out
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
