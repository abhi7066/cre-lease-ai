REGION_BENCHMARK = {
    "London": 120,
    "Shanghai": 90,
    "Berlin": 100
}

def sanity_agent(state: dict):

    data = state.get("structured_data", {})
    flags = []
    lease_term = data.get("leaseTerm") or {}
    financial = data.get("financialTerms") or {}
    options = data.get("options") or {}
    risk_flags = data.get("riskFlags") or {}
    derived = data.get("derivedAnalytics") or {}

    if not lease_term.get("commencementDate"):
        flags.append("Missing commencement date")

    if not lease_term.get("expirationDate"):
        flags.append("Missing expiration date")

    if options.get("hasRenewalOption") and not options.get("renewalNoticePeriodDays"):
        flags.append("Renewal option exists but notice period missing")

    if options.get("hasTerminationOption"):
        flags.append("Early termination option present")

    if not risk_flags.get("sndaInPlace", False):
        flags.append("SNDA not identified")

    if not financial.get("securityDeposit"):
        flags.append("No security deposit found")

    # Financial deviation
    region = (data.get("premises") or {}).get("propertyAddress")
    rent = derived.get("effective_rent_psf")

    if region and rent is not None:
        benchmark_key = next((k for k in REGION_BENCHMARK if k.lower() in region.lower()), None)
    else:
        benchmark_key = None

    if benchmark_key:
        benchmark = REGION_BENCHMARK[benchmark_key]
        deviation = (float(rent) - benchmark) / benchmark
        if abs(deviation) > 0.2:
            flags.append("Effective rent deviation beyond 20% market benchmark")

        state.setdefault("structured_data", {}).setdefault("derivedAnalytics", {})["deviation_score"] = round(deviation, 3)

    if derived.get("expense_recovery_structure") == "Unknown":
        flags.append("Expense recovery structure could not be inferred")

    if risk_flags.get("coTenancyClause", False):
        flags.append("Co-tenancy clause detected")

    if risk_flags.get("exclusiveUseClause", False):
        flags.append("Exclusive-use clause may constrain future leasing")

    if len(flags) == 0:
        flags.append("No material sanity issues detected")

    # Keep the old-style deviation score field populated for compatibility.
    if "derivedAnalytics" in state.get("structured_data", {}):
        state["structured_data"]["deviation_score"] = state["structured_data"]["derivedAnalytics"].get("deviation_score", 0)

    if region in REGION_BENCHMARK:
        benchmark = REGION_BENCHMARK[region]
        if rent is not None:
            deviation = (float(rent) - benchmark) / benchmark
            if abs(deviation) > 0.2:
                flags.append("Financial deviation beyond 20%")

    state["sanity_flags"] = flags
    state.setdefault("execution_log", []).append("Sanity agent completed")
    return state
