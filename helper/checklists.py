"""
Checklist templates. In production these would live in Supabase and be
editable per firm/client-type; for the demo they're defined here so the
whole flow is inspectable and easy to extend.
"""
from app.schema.models import ChecklistItemDefinition, ChecklistTemplateType

CHECKLISTS: dict[ChecklistTemplateType, list[ChecklistItemDefinition]] = {
    ChecklistTemplateType.NEW_BUSINESS_BOOKKEEPING: [
        ChecklistItemDefinition(
            key="ein_letter",
            label="EIN Confirmation Letter (IRS CP 575 or 147C)",
            description=(
                "An IRS-issued letter confirming the business's Employer "
                "Identification Number. Usually titled 'CP 575' or '147C'."
            ),
        ),
        ChecklistItemDefinition(
            key="formation_docs",
            label="Business Formation Documents",
            description=(
                "Articles of Organization (LLC), Articles of Incorporation, "
                "or a partnership agreement establishing the entity."
            ),
        ),
        ChecklistItemDefinition(
            key="prior_year_return",
            label="Prior-Year Business Tax Return",
            description="The most recently filed business tax return (e.g. Form 1120, 1120-S, 1065).",
        ),
        ChecklistItemDefinition(
            key="bank_statements",
            label="Last 3 Months of Business Bank Statements",
            description="Recent business checking/savings account statements, any bank.",
        ),
        ChecklistItemDefinition(
            key="voided_check",
            label="Voided Check or Bank Letter",
            description="A voided check or bank letter confirming account/routing numbers.",
        ),
        ChecklistItemDefinition(
            key="prior_bookkeeping_export",
            label="Prior Bookkeeping Export (if applicable)",
            description="QuickBooks/Xero export or spreadsheet from a prior bookkeeper, if one exists.",
            required=False,
        ),
    ],
    ChecklistTemplateType.INDIVIDUAL_TAX: [
        ChecklistItemDefinition(
            key="prior_year_1040",
            label="Prior-Year Form 1040",
            description="Most recently filed individual tax return.",
        ),
        ChecklistItemDefinition(
            key="w2_or_1099",
            label="Current-Year W-2s / 1099s",
            description="All wage and income statements for the current tax year.",
        ),
        ChecklistItemDefinition(
            key="id_document",
            label="Government-Issued ID",
            description="Driver's license or passport for identity verification.",
        ),
    ],
    ChecklistTemplateType.CROSS_BORDER: [
        ChecklistItemDefinition(
            key="visa_status",
            label="Visa / Immigration Status Documentation",
            description="E2, H1B, green card, or other status documentation relevant to tax residency.",
        ),
        ChecklistItemDefinition(
            key="foreign_income_docs",
            label="Foreign Income / Asset Documentation",
            description="Statements for foreign bank accounts, income, or investments (FBAR/FATCA relevant).",
        ),
        ChecklistItemDefinition(
            key="prior_year_1040",
            label="Prior-Year Form 1040 or 1040-NR",
            description="Most recently filed U.S. tax return, resident or non-resident.",
        ),
    ],
}
