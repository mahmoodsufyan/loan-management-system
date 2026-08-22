import io
from datetime import date
from decimal import Decimal
from typing import Dict, Any

class LoanPDFService:
    """
    Generates downloadable loan repayment schedule PDF documents.
    """
    @classmethod
    def generate_schedule_pdf(cls, schedule_data: Dict[str, Any], applicant_name: str = "Client") -> bytes:
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib import colors

            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
            elements = []
            styles = getSampleStyleSheet()

            title_style = ParagraphStyle(
                'DocTitle',
                parent=styles['Heading1'],
                fontSize=18,
                leading=22,
                textColor=colors.HexColor("#1A365D"),
                alignment=1
            )
            subtitle_style = ParagraphStyle(
                'DocSubTitle',
                parent=styles['Normal'],
                fontSize=11,
                leading=14,
                textColor=colors.HexColor("#4A5568"),
                alignment=1
            )

            elements.append(Paragraph("Enterprise Loan Repayment Schedule", title_style))
            elements.append(Paragraph(f"Applicant: {applicant_name} | Generated: {date.today().isoformat()}", subtitle_style))
            elements.append(Spacer(1, 15))

            # Summary Info Box
            summary_data = [
                ["Principal Amount:", f"${schedule_data['principal']:,.2f}", "Annual Rate / APR:", f"{schedule_data['annual_rate']}%"],
                ["Tenor (Months):", f"{schedule_data['tenor_months']} M", "Calculation Method:", schedule_data['method'].replace('_', ' ').title()],
                ["Total Profit:", f"${schedule_data['total_profit']:,.2f}", "Total Repayable:", f"${schedule_data['total_payable']:,.2f}"]
            ]
            summary_table = Table(summary_data, colWidths=[130, 140, 130, 140])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F7FAFC")),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor("#2D3748")),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ]))
            elements.append(summary_table)
            elements.append(Spacer(1, 15))

            # Schedule Table
            table_header = ["#", "Due Date", "Opening", "Principal", "Profit", "Installment", "Closing"]
            table_rows = [table_header]

            for item in schedule_data["schedule"][:60]: # up to 60 rows for clean display
                table_rows.append([
                    str(item["installment_number"]),
                    str(item["due_date"]),
                    f"${item['opening_balance']:,.2f}",
                    f"${item['principal']:,.2f}",
                    f"${item['profit']:,.2f}",
                    f"${item['total_installment']:,.2f}",
                    f"${item['closing_balance']:,.2f}",
                ])

            schedule_table = Table(table_rows, colWidths=[30, 75, 85, 85, 80, 95, 90])
            schedule_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2B6CB0")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#EDF2F7")]),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            elements.append(schedule_table)

            doc.build(elements)
            return buffer.getvalue()

        except ImportError:
            # Fallback text/binary if reportlab is not installed
            fallback_text = f"LOAN REPAYMENT SCHEDULE\nApplicant: {applicant_name}\nPrincipal: {schedule_data['principal']}\nTotal Payable: {schedule_data['total_payable']}\n"
            return fallback_text.encode("utf-8")
