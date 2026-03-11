import { useEffect, useRef, useState, useCallback } from "react";
import { getJobStatus } from "../api";
import { CheckCircle2, Loader2, XCircle, Clock } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

const STATUS_ICONS = {
  queued: <Clock className="h-4 w-4 text-slate-400" />,
  processing: <Loader2 className="h-4 w-4 animate-spin text-cyan-500" />,
  done: <CheckCircle2 className="h-4 w-4 text-emerald-500" />,
  error: <XCircle className="h-4 w-4 text-red-500" />,
};

const STATUS_LABELS = {
  queued: "Queued",
  processing: "Extracting…",
  done: "Complete",
  error: "Failed",
};

const STATUS_COLOR = {
  queued: "text-slate-500",
  processing: "text-cyan-600",
  done: "text-emerald-600",
  error: "text-red-600",
};

function ProcessingStatusPanel({ jobs, onAllJobsDone }) {
  const [jobStatuses, setJobStatuses] = useState({});
  const intervalRef = useRef(null);
  const onAllJobsDoneRef = useRef(onAllJobsDone);

  // Keep callback ref in sync so the interval doesn't capture stale values.
  useEffect(() => {
    onAllJobsDoneRef.current = onAllJobsDone;
  }, [onAllJobsDone]);

  const poll = useCallback(async () => {
    if (!jobs.length) return;

    const updates = {};
    for (const job of jobs) {
      try {
        const res = await getJobStatus(job.job_id);
        updates[job.job_id] = res.data;
      } catch {
        updates[job.job_id] = { status: "error", error: "Status check failed", result: null };
      }
    }

    setJobStatuses((prev) => {
      const next = { ...prev, ...updates };

      // Check if all jobs finished
      const allDone = jobs.every((j) => {
        const s = next[j.job_id]?.status;
        return s === "done" || s === "error";
      });

      if (allDone) {
        clearInterval(intervalRef.current);

        const results = jobs
          .filter((j) => next[j.job_id]?.status === "done")
          .map((j) => next[j.job_id].result)
          .filter(Boolean);

        if (results.length > 0) {
          // Defer so state update settles first
          setTimeout(() => onAllJobsDoneRef.current?.(results), 0);
        }
      }

      return next;
    });
  }, [jobs]);

  useEffect(() => {
    if (!jobs.length) return;
    poll();
    intervalRef.current = setInterval(poll, 3000);
    return () => clearInterval(intervalRef.current);
  }, [jobs, poll]);

  if (!jobs.length) return null;

  const doneCount = jobs.filter(
    (j) => jobStatuses[j.job_id]?.status === "done"
  ).length;
  const errorCount = jobs.filter(
    (j) => jobStatuses[j.job_id]?.status === "error"
  ).length;
  const activeCount = jobs.length - doneCount - errorCount;

  return (
    <Card className="enterprise-card mb-6">
      <CardHeader className="pb-3">
        <CardTitle>Processing Status</CardTitle>
        <CardDescription>
          AI extraction is running in the background.{" "}
          {activeCount > 0
            ? `${activeCount} still processing…`
            : `All ${jobs.length} file${jobs.length > 1 ? "s" : ""} finished.`}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          {jobs.map((job) => {
            const statusData = jobStatuses[job.job_id];
            const status = statusData?.status || "queued";
            const progress = status === "processing" ? null : status === "done" ? 100 : null;

            return (
              <div
                key={job.job_id}
                className="flex items-center gap-3 rounded-lg border bg-white/70 px-4 py-3"
              >
                <div className="shrink-0">{STATUS_ICONS[status]}</div>
                <div className="min-w-0 flex-1">
                  <p className="max-w-xs truncate text-sm font-medium text-slate-700">
                    {job.filename}
                  </p>
                  {status === "processing" && (
                    <div className="mt-1.5 h-1.5 w-full overflow-hidden rounded-full bg-slate-200">
                      <div className="h-full w-3/5 animate-pulse rounded-full bg-cyan-400" />
                    </div>
                  )}
                  {status === "done" && progress !== null && (
                    <div className="mt-1.5 h-1.5 w-full overflow-hidden rounded-full bg-slate-200">
                      <div className="h-full w-full rounded-full bg-emerald-400" />
                    </div>
                  )}
                  {statusData?.error && (
                    <p className="mt-0.5 truncate text-xs text-red-500">
                      {statusData.error}
                    </p>
                  )}
                </div>
                <span
                  className={`shrink-0 text-xs font-semibold ${STATUS_COLOR[status]}`}
                >
                  {STATUS_LABELS[status]}
                </span>
              </div>
            );
          })}
        </div>

        {(doneCount > 0 || errorCount > 0) && (
          <div className="mt-3 flex gap-4 text-xs text-muted-foreground">
            {doneCount > 0 && (
              <span className="text-emerald-600">{doneCount} completed</span>
            )}
            {errorCount > 0 && (
              <span className="text-red-500">{errorCount} failed</span>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export default ProcessingStatusPanel;
