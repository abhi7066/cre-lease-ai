import { useEffect, useState } from "react";
import { getPortfolioAnalytics } from "../api";
import { AlertTriangle, ChartNoAxesColumn, RotateCcw, ShieldCheck } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

function MetricTile({ label, value, icon }) {
  const IconComponent = icon;
  return (
    <div className="rounded-lg border bg-white/60 p-4">
      <div className="flex items-center justify-between">
        <p className="text-xs uppercase tracking-widest text-muted-foreground">{label}</p>
        <IconComponent className="h-4 w-4 text-slate-500" />
      </div>
      <p className="mt-2 text-2xl font-semibold">{value}</p>
    </div>
  );
}

function AnalyticsCard({ refreshToken = 0 }) {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    getPortfolioAnalytics()
      .then((res) => {
        setData(res.data);
        setError("");
      })
      .catch(() => setError("Analytics service unavailable"));
  }, [refreshToken]);

  if (error) {
    return (
      <Card className="enterprise-card">
        <CardHeader>
          <CardTitle>Portfolio Analytics</CardTitle>
          <CardDescription>{error}</CardDescription>
        </CardHeader>
      </Card>
    );
  }

  if (!data) {
    return (
      <Card className="enterprise-card">
        <CardHeader>
          <CardTitle>Portfolio Analytics</CardTitle>
          <CardDescription>Loading strategic analytics metrics...</CardDescription>
        </CardHeader>
      </Card>
    );
  }

  return (
    <Card className="enterprise-card">
      <CardHeader>
        <CardTitle>Portfolio Analytics</CardTitle>
        <CardDescription>Warehouse-backed KPI rollup for optionality, risk, and effective rents.</CardDescription>
      </CardHeader>
      <CardContent className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <MetricTile
          label="Avg Effective Rent / SF"
          value={data.avg_effective_rent_psf ?? "-"}
          icon={ChartNoAxesColumn}
        />
        <MetricTile
          label="Avg Renewal Risk"
          value={data.avg_renewal_risk_score ?? "-"}
          icon={AlertTriangle}
        />
        <MetricTile
          label="With Renewal Option"
          value={data.leases_with_renewal_option ?? 0}
          icon={RotateCcw}
        />
        <MetricTile
          label="With Termination Option"
          value={data.leases_with_termination_option ?? 0}
          icon={ShieldCheck}
        />
      </CardContent>
    </Card>
  );
}

export default AnalyticsCard;
