import { cn } from "@/lib/utils";
import { CheckCircle2, FileText } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";

function BatchResultsPanel({ uploadedLeases, activeLeaseId, onSelect }) {
  if (!uploadedLeases || uploadedLeases.length <= 1) return null;

  return (
    <Card className="enterprise-card mb-6">
      <CardHeader className="pb-3">
        <CardTitle>Batch Results</CardTitle>
        <CardDescription>
          {uploadedLeases.length} leases processed — click any row to make it the active context for chat and reports.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b text-xs uppercase tracking-widest text-muted-foreground">
                <th className="pb-2 text-left font-medium">File</th>
                <th className="pb-2 text-left font-medium">Tenant</th>
                <th className="pb-2 text-left font-medium">Lease Start</th>
                <th className="pb-2 text-left font-medium">Lease End</th>
                <th className="pb-2 text-left font-medium">Risk</th>
                <th className="pb-2 text-left font-medium">Flags</th>
              </tr>
            </thead>
            <tbody>
              {uploadedLeases.map((lease, i) => {
                const data = lease.structured_data || {};
                const tenant =
                  data.tenant_name ||
                  data.parties?.tenantName ||
                  data.tenantName ||
                  "—";
                const start =
                  data.lease_start_date ||
                  data.commencementDate ||
                  data.leaseDates?.commencementDate ||
                  "—";
                const end =
                  data.lease_end_date ||
                  data.expirationDate ||
                  data.leaseDates?.expirationDate ||
                  "—";
                const risk = lease.analytics_result?.renewal_risk_score ?? 0;
                const flags = lease.sanity_flags?.length ?? 0;
                const isActive = lease.lease_id === activeLeaseId;

                return (
                  <tr
                    key={lease.lease_id ?? i}
                    onClick={() => onSelect(lease)}
                    className={cn(
                      "cursor-pointer border-b transition-colors last:border-0",
                      isActive
                        ? "bg-cyan-50 text-slate-900"
                        : "hover:bg-slate-50 text-slate-700"
                    )}
                  >
                    <td className="py-3 pr-4 font-medium">
                      <div className="flex items-center gap-2">
                        {isActive && <CheckCircle2 className="h-4 w-4 shrink-0 text-cyan-600" />}
                        {!isActive && <FileText className="h-4 w-4 shrink-0 text-slate-400" />}
                        <span className="max-w-[160px] truncate">{lease.filename || `Lease ${i + 1}`}</span>
                      </div>
                    </td>
                    <td className="py-3 pr-4 max-w-[140px] truncate">{tenant}</td>
                    <td className="py-3 pr-4">{start}</td>
                    <td className="py-3 pr-4">{end}</td>
                    <td className="py-3 pr-4">
                      <span
                        className={cn(
                          "inline-flex rounded-full px-2 py-0.5 text-xs font-semibold",
                          risk > 0.5 ? "bg-red-100 text-red-700" : "bg-emerald-100 text-emerald-700"
                        )}
                      >
                        {Number(risk).toFixed(2)}
                      </span>
                    </td>
                    <td className="py-3">{flags}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
}

export default BatchResultsPanel;
