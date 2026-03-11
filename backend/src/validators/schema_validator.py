"""
Schema validation for CRE Lease data
Ensures extracted data conforms to the expected structure and types.
"""

import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import re


class SchemaValidator:
    """Validates lease extraction output against the defined schema."""
    
    VALID_LEASE_TYPES = [
        "Full Service",
        "Modified Gross",
        "Triple Net",
        "Absolute NNN",
        None
    ]
    
    VALID_RENT_ESCALATION_TYPES = [
        "Fixed Percentage",
        "CPI",
        "FMV",
        "Fixed Increase",
        None
    ]
    
    VALID_EXPENSE_PASSTHROUGH_TYPES = [
        "NNN",
        "Base Year",
        "Expense Stop",
        "Gross",
        None
    ]
    
    VALID_RENEWAL_RENT_BASIS = [
        "FMV",
        "Fixed",
        "CPI",
        "Percentage of Market",
        None
    ]
    
    @staticmethod
    def validate_date(date_str: Any) -> Tuple[bool, str]:
        """
        Validate date format (YYYY-MM-DD or null).
        
        Args:
            date_str: Date string to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if date_str is None:
            return True, ""
        
        if not isinstance(date_str, str):
            return False, f"Date must be string or null, got {type(date_str)}"
        
        # Check ISO format
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True, ""
        except ValueError:
            return False, f"Invalid date format '{date_str}'. Expected YYYY-MM-DD"
    
    @staticmethod
    def validate_lease_identification(data: Dict[str, Any]) -> List[str]:
        """Validate leaseIdentification section."""
        errors = []
        
        if "leaseIdentification" not in data:
            errors.append("Missing 'leaseIdentification' section")
            return errors
        
        section = data["leaseIdentification"]

        lease_id = section.get("leaseId")
        if lease_id is not None and not isinstance(lease_id, str):
            errors.append(f"leaseIdentification.leaseId: Must be string or null, got {type(lease_id)}")
        
        # Validate leaseExecutionDate
        is_valid, error = SchemaValidator.validate_date(section.get("leaseExecutionDate"))
        if not is_valid:
            errors.append(f"leaseIdentification.leaseExecutionDate: {error}")
        
        # Validate leaseType
        lease_type = section.get("leaseType")
        if lease_type not in SchemaValidator.VALID_LEASE_TYPES:
            errors.append(f"leaseIdentification.leaseType: Invalid value '{lease_type}'. Must be one of {SchemaValidator.VALID_LEASE_TYPES}")
        
        return errors
    
    @staticmethod
    def validate_parties(data: Dict[str, Any]) -> List[str]:
        """Validate parties section."""
        errors = []
        
        if "parties" not in data:
            errors.append("Missing 'parties' section")
            return errors
        
        section = data["parties"]
        
        # Validate string or null fields
        for field in ["landlordName", "tenantName", "parentTenantId", "guarantorName"]:
            value = section.get(field)
            if value is not None and not isinstance(value, str):
                errors.append(f"parties.{field}: Must be string or null, got {type(value)}")
        
        # Validate boolean
        is_guaranteed = section.get("isGuaranteed")
        if not isinstance(is_guaranteed, bool):
            errors.append(f"parties.isGuaranteed: Must be boolean, got {type(is_guaranteed)}")
        
        return errors
    
    @staticmethod
    def validate_premises(data: Dict[str, Any]) -> List[str]:
        """Validate premises section."""
        errors = []
        
        if "premises" not in data:
            errors.append("Missing 'premises' section")
            return errors
        
        section = data["premises"]
        
        # Validate string or null fields
        for field in ["propertyId", "market", "propertyAddress", "premisesDescription"]:
            value = section.get(field)
            if value is not None and not isinstance(value, str):
                errors.append(f"premises.{field}: Must be string or null, got {type(value)}")
        
        # Validate rentableSquareFeet
        rsf = section.get("rentableSquareFeet")
        if rsf is not None and not isinstance(rsf, (int, float)):
            errors.append(f"premises.rentableSquareFeet: Must be number or null, got {type(rsf)}")
        elif rsf is not None and rsf <= 0:
            errors.append(f"premises.rentableSquareFeet: Must be positive, got {rsf}")
        
        return errors
    
    @staticmethod
    def validate_lease_term(data: Dict[str, Any]) -> List[str]:
        """Validate leaseTerm section."""
        errors = []
        
        if "leaseTerm" not in data:
            errors.append("Missing 'leaseTerm' section")
            return errors
        
        section = data["leaseTerm"]
        
        # Validate dates
        for field in ["commencementDate", "expirationDate", "rentCommencementDate"]:
            is_valid, error = SchemaValidator.validate_date(section.get(field))
            if not is_valid:
                errors.append(f"leaseTerm.{field}: {error}")
        
        # Check logical date order
        commencement = section.get("commencementDate")
        expiration = section.get("expirationDate")
        if commencement and expiration:
            try:
                comm_date = datetime.strptime(commencement, "%Y-%m-%d")
                exp_date = datetime.strptime(expiration, "%Y-%m-%d")
                if exp_date <= comm_date:
                    errors.append("leaseTerm: Expiration date must be after commencement date")
            except:
                pass
        
        return errors
    
    @staticmethod
    def validate_financial_terms(data: Dict[str, Any]) -> List[str]:
        """Validate financialTerms section."""
        errors = []
        
        if "financialTerms" not in data:
            errors.append("Missing 'financialTerms' section")
            return errors
        
        section = data["financialTerms"]
        
        # Validate baseRentSchedule
        schedule = section.get("baseRentSchedule")
        if not isinstance(schedule, list):
            errors.append(f"financialTerms.baseRentSchedule: Must be array, got {type(schedule)}")
        else:
            for i, entry in enumerate(schedule):
                if not isinstance(entry, dict):
                    errors.append(f"financialTerms.baseRentSchedule[{i}]: Must be object")
                    continue
                
                # Validate dates
                is_valid, error = SchemaValidator.validate_date(entry.get("startDate"))
                if not is_valid:
                    errors.append(f"financialTerms.baseRentSchedule[{i}].startDate: {error}")
                elif entry.get("startDate") is None:
                    errors.append(f"financialTerms.baseRentSchedule[{i}].startDate: Cannot be null")
                
                is_valid, error = SchemaValidator.validate_date(entry.get("endDate"))
                if not is_valid:
                    errors.append(f"financialTerms.baseRentSchedule[{i}].endDate: {error}")
                
                annual_rent = entry.get("annualRent")
                annual_base_rent = entry.get("annualBaseRent")
                if annual_rent is None and annual_base_rent is None:
                    errors.append(
                        f"financialTerms.baseRentSchedule[{i}]: Must include annualRent or annualBaseRent"
                    )

                for field in ["annualRent", "annualBaseRent", "monthlyRent"]:
                    value = entry.get(field)
                    if value is None:
                        continue
                    if not isinstance(value, (int, float)):
                        errors.append(f"financialTerms.baseRentSchedule[{i}].{field}: Must be number, got {type(value)}")
                    elif value < 0:
                        errors.append(f"financialTerms.baseRentSchedule[{i}].{field}: Cannot be negative")

                currency = entry.get("currency")
                if currency is not None and not isinstance(currency, str):
                    errors.append(f"financialTerms.baseRentSchedule[{i}].currency: Must be string or null")
        
        # Validate rentEscalationType
        escalation = section.get("rentEscalationType")
        if escalation not in SchemaValidator.VALID_RENT_ESCALATION_TYPES:
            errors.append(f"financialTerms.rentEscalationType: Invalid value '{escalation}'")
        
        # Validate numeric or null fields
        for field in ["securityDeposit", "proRataShare", "tenantImprovementAllowance", "annualBaseRent"]:
            value = section.get(field)
            if value is not None and not isinstance(value, (int, float)):
                errors.append(f"financialTerms.{field}: Must be number or null, got {type(value)}")
        
        # Validate operatingExpensePassThrough
        passthrough = section.get("operatingExpensePassThrough")
        if passthrough not in SchemaValidator.VALID_EXPENSE_PASSTHROUGH_TYPES:
            errors.append(f"financialTerms.operatingExpensePassThrough: Invalid value '{passthrough}'")
        
        return errors
    
    @staticmethod
    def validate_options(data: Dict[str, Any]) -> List[str]:
        """Validate options section."""
        errors = []
        
        if "options" not in data:
            errors.append("Missing 'options' section")
            return errors
        
        section = data["options"]
        
        # Validate booleans
        for field in ["hasRenewalOption", "hasTerminationOption"]:
            value = section.get(field)
            if not isinstance(value, bool):
                errors.append(f"options.{field}: Must be boolean, got {type(value)}")
        
        # Validate renewalNoticePeriodDays
        days = section.get("renewalNoticePeriodDays")
        if days is not None and not isinstance(days, (int, float)):
            errors.append(f"options.renewalNoticePeriodDays: Must be number or null, got {type(days)}")
        elif days is not None and days < 0:
            errors.append(f"options.renewalNoticePeriodDays: Cannot be negative")
        
        termination_days = section.get("terminationNoticePeriodDays")
        if termination_days is not None and not isinstance(termination_days, (int, float)):
            errors.append(f"options.terminationNoticePeriodDays: Must be number or null, got {type(termination_days)}")
        elif termination_days is not None and termination_days < 0:
            errors.append(f"options.terminationNoticePeriodDays: Cannot be negative")

        # Validate renewalRentBasis
        basis = section.get("renewalRentBasis")
        if basis not in SchemaValidator.VALID_RENEWAL_RENT_BASIS:
            errors.append(f"options.renewalRentBasis: Invalid value '{basis}'")
        
        return errors
    
    @staticmethod
    def validate_risk_flags(data: Dict[str, Any]) -> List[str]:
        """Validate riskFlags section."""
        errors = []
        
        if "riskFlags" not in data:
            errors.append("Missing 'riskFlags' section")
            return errors
        
        section = data["riskFlags"]
        
        # Validate booleans
        for field in ["coTenancyClause", "exclusiveUseClause", "sndaInPlace"]:
            value = section.get(field)
            if not isinstance(value, bool):
                errors.append(f"riskFlags.{field}: Must be boolean, got {type(value)}")
        
        return errors
    
    @staticmethod
    def validate_confidence_score(data: Dict[str, Any]) -> List[str]:
        """Validate confidenceScore."""
        errors = []
        
        score = data.get("confidenceScore")
        if not isinstance(score, (int, float)):
            errors.append(f"confidenceScore: Must be number, got {type(score)}")
        elif score < 0 or score > 100:
            errors.append(f"confidenceScore: Must be between 0 and 100, got {score}")
        
        return errors
    
    @classmethod
    def validate(cls, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate complete lease extraction output.
        
        Args:
            data: Extracted lease data dictionary
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Validate root structure
        if not isinstance(data, dict):
            return False, ["Root data must be a dictionary/object"]
        
        # Validate each section
        errors.extend(cls.validate_lease_identification(data))
        errors.extend(cls.validate_parties(data))
        errors.extend(cls.validate_premises(data))
        errors.extend(cls.validate_lease_term(data))
        errors.extend(cls.validate_financial_terms(data))
        errors.extend(cls.validate_options(data))
        errors.extend(cls.validate_risk_flags(data))
        errors.extend(cls.validate_confidence_score(data))
        
        return len(errors) == 0, errors
    
    @classmethod
    def validate_json_string(cls, json_string: str) -> Tuple[bool, List[str]]:
        """
        Validate lease extraction output from JSON string.
        
        Args:
            json_string: JSON string to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        try:
            data = json.loads(json_string)
            return cls.validate(data)
        except json.JSONDecodeError as e:
            return False, [f"Invalid JSON: {str(e)}"]


def main():
    """Example usage of SchemaValidator."""
    
    # Example valid data
    valid_data = {
        "leaseIdentification": {
            "leaseExecutionDate": "2024-01-15",
            "leaseType": "Triple Net"
        },
        "parties": {
            "landlordName": "ABC Properties LLC",
            "tenantName": "XYZ Corporation",
            "guarantorName": None,
            "isGuaranteed": False
        },
        "premises": {
            "propertyAddress": "1234 Main St",
            "premisesDescription": "Suite 500",
            "rentableSquareFeet": 5000
        },
        "leaseTerm": {
            "commencementDate": "2024-02-01",
            "expirationDate": "2029-01-31",
            "rentCommencementDate": "2024-02-01"
        },
        "financialTerms": {
            "baseRentSchedule": [
                {
                    "startDate": "2024-02-01",
                    "endDate": "2026-01-31",
                    "annualRent": 125000,
                    "monthlyRent": 10416.67,
                    "currency": "USD"
                }
            ],
            "rentEscalationType": "Fixed Percentage",
            "securityDeposit": 20000,
            "proRataShare": 12.5,
            "operatingExpensePassThrough": "NNN"
        },
        "options": {
            "hasRenewalOption": True,
            "renewalNoticePeriodDays": 180,
            "renewalRentBasis": "FMV",
            "hasTerminationOption": False
        },
        "riskFlags": {
            "coTenancyClause": False,
            "exclusiveUseClause": False,
            "sndaInPlace": False
        },
        "confidenceScore": 85
    }
    
    is_valid, errors = SchemaValidator.validate(valid_data)
    if is_valid:
        print("✓ Validation passed!")
    else:
        print("✗ Validation failed:")
        for error in errors:
            print(f"  - {error}")


if __name__ == "__main__":
    main()
