"use client";

import { useEffect, useState } from "react";
import { ArrowDownRight, ArrowUpRight } from "lucide-react";

import RequireAuth, { useAuth } from "@/components/RequireAuth";
import DashboardSidebar from "@/components/Sidebar";
import { User } from "@/lib/types";
import { apiRequest } from "@/lib/api";

type QuickRange = {
  id: string;
  label: string;
};

type TrendDirection = "up" | "down";

type MetricSnapshot = {
  value: number;
  change: string;
  trend: TrendDirection;
  comparison: string;
};

type MetricSource = {
  label: string;
  values: Record<string, number>;
  note?: string;
};

type MetricSection = {
  id: string;
  title: string;
  description: string;
  timeframeData: Record<string, MetricSnapshot>;
  sources: MetricSource[];
};

type StatsResponse = {
  ranges: QuickRange[];
  metrics: MetricSection[];
};

export default function Page() {
  return (
    <RequireAuth>
      <Content />
    </RequireAuth>
  );
}

function Content() {
  const user = useAuth() as User | null;
  const userNavigation = user?.navigation ?? [];
  const [ranges, setRanges] = useState<QuickRange[]>([]);
  const [metrics, setMetrics] = useState<MetricSection[]>([]);
  const [selectedRange, setSelectedRange] = useState<string>("24h");
  const [isLoadingStats, setIsLoadingStats] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = (await apiRequest("get", "/stats/")) as StatsResponse;
        const fetchedRanges = data?.ranges ?? [];
        setRanges(fetchedRanges);
        setMetrics(data?.metrics ?? []);
        setSelectedRange((previous) => {
          if (fetchedRanges.some((range) => range.id === previous)) {
            return previous;
          }
          return fetchedRanges[0]?.id ?? previous;
        });
      } catch (error) {
        console.error("Unable to load stats", error);
      } finally {
        setIsLoadingStats(false);
      }
    };

    fetchStats();
  }, []);

  const selectedRangeLabel =
    ranges.find((range) => range.id === selectedRange)?.label ?? "";

  const formatNumber = (value: number) =>
    value.toLocaleString("en-US", { maximumFractionDigits: 0 });

  return (
    <div className="min-h-screen bg-muted/20 py-10">
      <div className="mx-auto flex w-full max-w-[1400px] flex-col gap-6 px-4 md:flex-row lg:gap-12 xl:gap-16">
        <aside className="lg:w-72 lg:flex-none">
          <DashboardSidebar
            navSections={userNavigation}
            userName={
              user ? `${user.first_name} ${user.last_name}`.trim() : undefined
            }
          />
        </aside>

        <main className="flex-1 space-y-6 lg:flex-[1.2] xl:flex-[1.4]">
          <section className="rounded-3xl border border-border bg-card p-6 shadow-sm lg:p-10">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <h2 className="text-xl font-semibold text-foreground">
                  Signals
                </h2>
                <p className="text-sm text-muted-foreground">
                  Follow prescriptions and payments in real time, compare
                  against past periods, and pinpoint which sources are pulling
                  the load.
                </p>
              </div>
              <div className="flex flex-col gap-3 md:flex-row md:items-center">
                <div className="flex items-center gap-2 rounded-2xl bg-muted p-1">
                  {ranges.length === 0 ? (
                    <span className="px-3 py-1 text-sm text-muted-foreground">
                      {isLoadingStats ? "Loading ranges..." : "No ranges"}
                    </span>
                  ) : (
                    ranges.map((range) => (
                      <button
                        key={range.id}
                        type="button"
                        onClick={() => setSelectedRange(range.id)}
                        className={`rounded-2xl px-3 py-1 text-sm font-semibold transition-colors cursor-pointer ${
                          selectedRange === range.id
                            ? "bg-background text-foreground shadow-sm"
                            : "text-muted-foreground hover:text-foreground"
                        }`}
                      >
                        {range.label}
                      </button>
                    ))
                  )}
                </div>
              </div>
            </div>

            <div className="mt-6 text-xs text-muted-foreground">
              {selectedRangeLabel
                ? `Showing ${selectedRangeLabel}`
                : "Awaiting stats"}
            </div>

            <div className="mt-6 grid gap-6 lg:grid-cols-2">
              {metrics.length === 0 && !isLoadingStats ? (
                <div className="rounded-2xl border border-dashed border-border bg-muted/20 p-6 text-sm text-muted-foreground">
                  No metrics available right now.
                </div>
              ) : null}

              {metrics.map((section) => {
                const snapshot =
                  section.timeframeData[selectedRange] ??
                  ({
                    value: 0,
                    change: "Awaiting data",
                    trend: "up",
                    comparison: "",
                  } as MetricSnapshot);
                const TrendIcon =
                  snapshot.trend === "up" ? ArrowUpRight : ArrowDownRight;
                const totalValue = snapshot.value;

                return (
                  <div
                    key={section.id}
                    className="rounded-2xl border border-border/60 bg-muted/30 p-6"
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <p className="text-sm font-medium text-muted-foreground">
                          {section.title}
                        </p>
                        <p className="mt-1 text-3xl font-semibold tracking-tight">
                          {section.id === "payments"
                            ? `$${formatNumber(totalValue)}`
                            : formatNumber(totalValue)}
                        </p>
                        <p className="mt-1 text-xs text-muted-foreground">
                          {section.description}
                        </p>
                      </div>
                      <div
                        className={`inline-flex items-center gap-1 rounded-full px-3 py-1 text-xs font-semibold ${
                          snapshot.trend === "up"
                            ? "bg-emerald-50 text-emerald-700"
                            : "bg-rose-50 text-rose-700"
                        }`}
                      >
                        <TrendIcon className="h-4 w-4" />
                        {snapshot.change}
                      </div>
                    </div>

                    <div className="mt-4 rounded-2xl border border-border bg-background/80 p-4">
                      <p className="text-xs font-semibold uppercase text-muted-foreground">
                        Source detail
                      </p>
                      <div className="mt-3 space-y-3">
                        {section.sources.map((source) => {
                          const sourceValue = source.values[selectedRange] ?? 0;
                          const percentage =
                            totalValue === 0
                              ? 0
                              : Math.round((sourceValue / totalValue) * 100);
                          return (
                            <div
                              key={`${section.id}-${source.label}`}
                              className="space-y-1"
                            >
                              <div className="flex items-center justify-between text-xs font-medium">
                                <div className="flex items-center gap-2">
                                  <span>{source.label}</span>
                                  {source.note ? (
                                    <span className="rounded-full bg-muted px-2 py-0.5 text-[10px] font-semibold text-muted-foreground">
                                      {source.note}
                                    </span>
                                  ) : null}
                                </div>
                                <span>
                                  {section.id === "payments"
                                    ? `$${formatNumber(sourceValue)}`
                                    : formatNumber(sourceValue)}
                                </span>
                              </div>
                              <div className="h-2 rounded-full bg-muted">
                                <div
                                  className="h-full rounded-full bg-primary transition-all"
                                  style={{
                                    width: `${Math.min(percentage, 100)}%`,
                                  }}
                                />
                              </div>
                            </div>
                          );
                        })}
                      </div>
                      <p className="mt-4 text-[11px] text-muted-foreground">
                        {snapshot.comparison
                          ? `Compared to ${snapshot.comparison}`
                          : ""}
                      </p>
                    </div>
                  </div>
                );
              })}
            </div>
          </section>
        </main>
      </div>
    </div>
  );
}
