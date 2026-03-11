import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";

function Field({ label, value }) {
  return (
    <div className="rounded-lg border bg-white/60 p-4">
      <p className="text-xs uppercase tracking-widest text-muted-foreground">{label}</p>
      <p className="mt-1.5 text-sm font-semibold break-words">{value || <span className="text-muted-foreground">—</span>}</p>
    </div>
  );
}

function LeaseCard({ leaseData }) {
  const d = leaseData.structured_data || {};
  const risk = leaseData.analytics_result?.renewal_risk_score ?? 0;

  // Support both flat and nested structured_data shapes
  const tenant    = d.tenant_name     || d.parties?.tenantName   || d.tenantName   || "—";
  const landlord  = d.landlord_name   || d.parties?.landlordName || d.landlordName || "—";
  const start     = d.lease_start_date|| d.commencementDate      || d.leaseDates?.commencementDate || "—";
  const end       = d.lease_end_date  || d.expirationDate        || d.leaseDates?.expirationDate   || "—";
  const rent      = d.base_rent       || d.financialTerms?.baseRentSchedule?.[0]?.annualBaseRent   || "—";
  const currency  = d.currency        || d.financialTerms?.currency || "";
  const escalation= d.escalation_percent != null ? `${d.escalation_percent}%` : "—";
  const renewal   = d.renewal_years   != null ? `${d.renewal_years} yr` : "—";
  const region    = d.region          || d.premises?.propertyAddress || "—";
  const termination = d.termination_clause_present ? "Present" : "Not present";
  const forceMajeure = d.force_majeure_present ? "Present" : "Not present";

  return (
    <Card className="enterprise-card">
      <CardHeader>
        <CardTitle>Lease Analysis</CardTitle>
        <CardDescription>Extracted fields, validation flags, and risk posture for the active lease.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Key Fields Grid */}
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <Field label="Tenant" value={tenant} />
          <Field label="Landlord" value={landlord} />
          <Field label="Region / Property" value={region} />
          <Field label="Base Rent" value={rent ? `${currency} ${rent}` : "—"} />
          <Field label="Commencement" value={start} />
          <Field label="Expiry" value={end} />
          <Field label="Escalation" value={escalation} />
          <Field label="Renewal Term" value={renewal} />
          <Field label="Termination Clause" value={termination} />
          <Field label="Force Majeure" value={forceMajeure} />
        </div>

        {/* Risk + Flags */}
        <div className="grid gap-4 md:grid-cols-2">
          <div className="rounded-lg border bg-white/60 p-4">
            <p className="text-xs uppercase tracking-widest text-muted-foreground">Renewal Risk Score</p>
            <div className={cn(
              "mt-2 inline-flex rounded-md px-3 py-1 text-sm font-semibold",
              risk > 0.5 ? "bg-red-100 text-red-700" : "bg-emerald-100 text-emerald-700"
            )}>
              {Number(risk).toFixed(2)}
            </div>
          </div>
          <div className="rounded-lg border bg-white/60 p-4">
            <p className="text-xs uppercase tracking-widest text-muted-foreground">Sanity Flags</p>
            <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-muted-foreground">
              {leaseData.sanity_flags?.length
                ? leaseData.sanity_flags.map((flag, i) => <li key={i}>{flag}</li>)
                : <li>No flags detected.</li>}
            </ul>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export default LeaseCard;
