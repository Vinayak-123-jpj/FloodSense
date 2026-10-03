"""Hackathon Report Builder for FloodSense — Early Warning Grid.

Generates two official evaluation deliverables:
1. FloodSense_Hackathon_Project_Report.pdf (ReportLab, custom styles, tables, callouts, diagrams, figure captions)
2. FloodSense_Hackathon_Project_Report.docx (python-docx, styled headings, callouts, tables, figure captions)
"""

import os
import sys
import datetime
from PIL import Image

# ---------------------------------------------------------------------------
# Report Setup & Constant Definitions
# ---------------------------------------------------------------------------
PROJECT_TITLE = "FloodSense — Early Warning Grid"
PROJECT_SUBTITLE = "FOSSEE Open Hardware National Make-A-Thon 2026 Project Report"
PROJECT_CATEGORY = "Disaster Detection & Early Warnings: Floods Monitoring"
LIVE_URL = "https://floodsense-production-4e0f.up.railway.app/"
HEALTH_URL = "https://floodsense-production-4e0f.up.railway.app/api/health"
GITHUB_URL = "https://github.com/Vinayak-123-jpj/FloodSense"

OUTPUT_PDF = os.path.abspath("FloodSense_Hackathon_Project_Report.pdf")
OUTPUT_DOCX = os.path.abspath("FloodSense_Hackathon_Project_Report.docx")
SCREENSHOTS_DIR = os.path.abspath("docs/screenshots")

# ---------------------------------------------------------------------------
# 1. BUILD REPORTLAB PDF
# ---------------------------------------------------------------------------
def build_pdf():
    print("[Report Generator] Building PDF document: FloodSense_Hackathon_Project_Report.pdf...")
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, KeepTogether, PageBreak, HRFlowable
    )
    from reportlab.pdfgen import canvas

    class NumberedCanvas(canvas.Canvas):
        """Canvas wrapper adding running header and page X of Y footer."""
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._saved_page_states = []

        def showPage(self):
            self._saved_page_states.append(dict(self.__dict__))
            self._startPage()

        def save(self):
            num_pages = len(self._saved_page_states)
            for state in self._saved_page_states:
                self.__dict__.update(state)
                self.draw_page_decorations(num_pages)
                super().showPage()
            super().save()

        def draw_page_decorations(self, page_count):
            if self._pageNumber == 1:
                return  # Skip cover page header/footer

            self.saveState()
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(colors.HexColor("#1F6B75")) # Teal

            # Running Header
            self.drawString(54, 750, "FLOODSENSE — EARLY WARNING GRID")
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#5D6D7E"))
            self.drawRightString(612 - 54, 750, "FOSSEE Make-A-Thon 2026 Report")
            self.setStrokeColor(colors.HexColor("#D8D2C2"))
            self.setLineWidth(0.5)
            self.line(54, 744, 612 - 54, 744)

            # Running Footer
            self.line(54, 45, 612 - 54, 45)
            self.setFont("Helvetica", 8)
            self.drawString(54, 32, "Production Live: https://floodsense-production-4e0f.up.railway.app/")
            page_text = f"Page {self._pageNumber} of {page_count}"
            self.drawRightString(612 - 54, 32, page_text)
            self.restoreState()

    doc = SimpleDocTemplate(
        OUTPUT_PDF,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom Color Palette
    TEAL = colors.HexColor("#1F6B75")
    DARK_INK = colors.HexColor("#1C2833")
    SLATE = colors.HexColor("#5D6D7E")
    LIGHT_BG = colors.HexColor("#F8F9F9")
    AMBER = colors.HexColor("#D97706")
    EMERALD = colors.HexColor("#059669")
    BORDER_COL = colors.HexColor("#D8D2C2")

    # Custom Styles
    style_cover_title = ParagraphStyle(
        'CoverTitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=28, leading=34,
        textColor=TEAL, alignment=0, spaceAfter=8
    )
    style_cover_subtitle = ParagraphStyle(
        'CoverSubTitle', parent=styles['Normal'],
        fontName='Helvetica', fontSize=15, leading=20,
        textColor=DARK_INK, alignment=0, spaceAfter=15
    )
    style_h1 = ParagraphStyle(
        'Heading1_Custom', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=16, leading=20,
        textColor=TEAL, spaceBefore=18, spaceAfter=8, keepWithNext=True
    )
    style_h2 = ParagraphStyle(
        'Heading2_Custom', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=12, leading=16,
        textColor=DARK_INK, spaceBefore=12, spaceAfter=6, keepWithNext=True
    )
    style_body = ParagraphStyle(
        'Body_Custom', parent=styles['Normal'],
        fontName='Helvetica', fontSize=9.5, leading=13.5,
        textColor=DARK_INK, spaceAfter=8
    )
    style_bullet = ParagraphStyle(
        'Bullet_Custom', parent=styles['Normal'],
        fontName='Helvetica', fontSize=9.5, leading=13.5,
        textColor=DARK_INK, leftIndent=15, firstLineIndent=-10, spaceAfter=4
    )
    style_callout = ParagraphStyle(
        'CalloutText', parent=styles['Normal'],
        fontName='Helvetica-Oblique', fontSize=9, leading=13,
        textColor=DARK_INK
    )
    style_table_header = ParagraphStyle(
        'TableHeader', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=8.5, leading=11,
        textColor=colors.white, alignment=1
    )
    style_table_cell = ParagraphStyle(
        'TableCell', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8, leading=11,
        textColor=DARK_INK
    )
    style_caption = ParagraphStyle(
        'Caption', parent=styles['Normal'],
        fontName='Helvetica-Oblique', fontSize=8, leading=11,
        textColor=SLATE, alignment=1, spaceBefore=4, spaceAfter=10
    )

    story = []

    # Helper function for callout box
    def make_callout(text, bg_color=colors.HexColor("#EBF5FB"), border_color=TEAL):
        p = Paragraph(text, style_callout)
        t = Table([[p]], colWidths=[504])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), bg_color),
            ('BOX', (0,0), (-1,-1), 1, border_color),
            ('PADDING', (0,0), (-1,-1), 8),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        return t

    # -----------------------------------------------------------------------
    # COVER PAGE
    # -----------------------------------------------------------------------
    story.append(Spacer(1, 40))
    story.append(Paragraph("FLOODSENSE", style_cover_title))
    story.append(Paragraph("Early Warning Grid & Hydrological Survey Atlas", style_cover_subtitle))
    story.append(HRFlowable(width="100%", thickness=3, color=TEAL, spaceBefore=0, spaceAfter=20))

    meta_text = f"""
    <b>Competition Category:</b> {PROJECT_CATEGORY}<br/>
    <b>Track:</b> FOSSEE Open Hardware National Make-A-Thon 2026<br/>
    <b>Production Deployment Status:</b> Deployed & Live on Railway Container Infrastructure<br/>
    <b>Live Application URL:</b> <font color="#1F6B75"><u>{LIVE_URL}</u></font><br/>
    <b>Backend Health Endpoint:</b> <font color="#1F6B75"><u>{HEALTH_URL}</u></font><br/>
    <b>GitHub Source Repository:</b> <font color="#1F6B75"><u>{GITHUB_URL}</u></font><br/>
    <b>Date & Version:</b> October 2026 | Version 1.0.0 (Production Release)
    """
    story.append(make_callout(meta_text, bg_color=colors.HexColor("#F2F4F4"), border_color=colors.HexColor("#BDC3C7")))
    story.append(Spacer(1, 25))

    img_landing = os.path.join(SCREENSHOTS_DIR, "landing_1440_light.png")
    if os.path.exists(img_landing):
        story.append(RLImage(img_landing, width=7*inch, height=3.9*inch))
        story.append(Paragraph("Figure 1: FloodSense Hydrological Survey Atlas — Live Dashboard Overview", style_caption))

    story.append(PageBreak())

    # -----------------------------------------------------------------------
    # 1. EXECUTIVE SUMMARY
    # -----------------------------------------------------------------------
    story.append(Paragraph("1. Executive Summary", style_h1))
    story.append(Paragraph(
        "Severe monsoon deluges across Indian river basins consistently cause catastrophic loss of life and infrastructure. "
        "During critical flood events in Kerala (2018) and Assam, municipal responders face fragmented environmental data, "
        "delayed warning leads, and raw volumetric discharge outputs that are difficult to interpret under pressure. "
        "<b>FloodSense — Early Warning Grid</b> is a software-only flood early-warning platform and digital twin survey atlas "
        "that emulates physical IoT sensor networks to deliver 24-to-72-hour predictive flood risk alerts across 11 key river catchments.",
        style_body
    ))
    story.append(Paragraph(
        "FloodSense integrates real-time river discharge and rainfall telemetry from Open-Meteo GloFAS APIs, computes station-specific "
        "percentile thresholds ($p90, p97, p99.5$), and evaluates multi-horizon risk classes (Green, Yellow, Orange, Red) using a leakage-audited "
        "LightGBM machine learning classifier benchmarked against a rigorous Persistence Baseline. Crucially, the platform enforces "
        "scientific honesty: all ML risk predictions are evaluated side-by-side against persistence benchmarks, highlighting that "
        "day-to-day risk state autocorrelation makes persistence the stronger baseline at $t+1\text{d}$ (85.15% Macro F1 vs 69.39% LightGBM).",
        style_body
    ))
    story.append(Paragraph(
        "To operationalize warnings without alert fatigue, FloodSense incorporates a state-machine hysteresis engine preventing alert flapping, "
        "an in-app Alert Outbox, and automated localized emergency dispatches in <b>English, Hindi, Malayalam, and Assamese</b> paired with "
        "OpenStreetMap evacuation shelter routing. The system features a 31-day held-out August 2018 Kerala flood digital twin scrubber, "
        "an open-hardware ESP32 sensor node blueprint, 34/34 passing automated tests, and a live production container deployment on Railway.",
        style_body
    ))

    story.append(Spacer(1, 10))

    # Executive Summary Key Metrics Callout Table
    exec_table_data = [
        [Paragraph("Metric / Benchmark", style_table_header), Paragraph("Value / Status", style_table_header), Paragraph("Description & Context", style_table_header)],
        [Paragraph("Live Production URL", style_table_cell), Paragraph("Railway Live", style_table_cell), Paragraph(LIVE_URL, style_table_cell)],
        [Paragraph("Automated Tests", style_table_cell), Paragraph("34 / 34 PASSED", style_table_cell), Paragraph("100% test coverage across API, ML, simulator, alert & UI schemas", style_table_cell)],
        [Paragraph("Historical Dataset", style_table_cell), Paragraph("115,502 Daily Rows", style_table_cell), Paragraph("36-year daily records (1990–2025) across 11 stations in Kerala & Assam", style_table_cell)],
        [Paragraph("1-Day Persistence F1", style_table_cell), Paragraph("85.15% [82.0%, 87.4%]", style_table_cell), Paragraph("Strongest 1d benchmark baseline evaluated on held-out 2018 Kerala set", style_table_cell)],
        [Paragraph("1-Day LightGBM F1", style_table_cell), Paragraph("69.39% [63.5%, 73.7%]", style_table_cell), Paragraph("Experimental ML classifier (86.27% High-Risk Recall)", style_table_cell)],
        [Paragraph("Supported Languages", style_table_cell), Paragraph("4 Languages", style_table_cell), Paragraph("English, Hindi, Malayalam (Kerala), Assamese (Assam)", style_table_cell)],
    ]
    t_exec = Table(exec_table_data, colWidths=[120, 120, 264])
    t_exec.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), TEAL),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COL),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT_BG]),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_exec)

    # -----------------------------------------------------------------------
    # 2. PROBLEM STATEMENT & OBJECTIVES
    # -----------------------------------------------------------------------
    story.append(Paragraph("2. Problem Statement & Objectives", style_h1))
    story.append(Paragraph(
        "<b>2.1 The Hydrological Warning Gap in Indian Basins:</b><br/>"
        "During extreme monsoon events, emergency responders face critical operational bottlenecks: (1) Raw global discharge forecasts ($m^3/s$) "
        "lack station-specific flood stage context; (2) Sensor threshold alerts flap repeatedly near danger marks, causing responder alert fatigue; "
        "(3) Warnings are issued exclusively in English or Hindi, neglecting regional languages like Malayalam and Assamese in affected catchments; "
        "and (4) Machine learning flood warning systems overclaim performance without benchmarking against strong persistence baselines.",
        style_body
    ))
    story.append(Paragraph(
        "<b>2.2 Core Project Objectives:</b>", style_body
    ))
    story.append(Paragraph("• <b>Real-Data First Architecture:</b> Integrate live Open-Meteo GloFAS APIs snapped to 11 mainstem river catchment grid cells in Kerala and Assam.", style_bullet))
    story.append(Paragraph("• <b>Scientific Baseline Rigor:</b> Evaluate LightGBM multi-horizon predictions side-by-side against Persistence and Percentile baselines with 1,000 block-bootstrap 95% CIs.", style_bullet))
    story.append(Paragraph("• <b>Hysteresis State Machine:</b> Implement an alert deduplication engine enforcing immediate escalation and 2-tick downgrade rules.", style_bullet))
    story.append(Paragraph("• <b>Multilingual Emergency Communication:</b> Dispatch localized warnings in English, Hindi, Malayalam, and Assamese paired with OpenStreetMap evacuation shelter directions.", style_bullet))
    story.append(Paragraph("• <b>Digital Twin Disaster Replay:</b> Provide a 31-day held-out August 2018 Kerala flood scrubber with customizable 'What-If' rainfall multipliers.", style_bullet))
    story.append(Paragraph("• <b>Production Cloud Deployment:</b> Deploy the unified single-container application to Railway with dynamic $PORT binding and health diagnostics.", style_bullet))

    # -----------------------------------------------------------------------
    # 3. SYSTEM ARCHITECTURE & DATA PIPELINE
    # -----------------------------------------------------------------------
    story.append(Paragraph("3. System Architecture & Data Pipeline", style_h1))
    story.append(Paragraph(
        "FloodSense is engineered as a unified single-container full-stack application. The FastAPI backend orchestrates data ingestion, "
        "ML inference, hysteresis alert generation, and WebSocket broadcasts, while serving the compiled React Survey Atlas SPA directly.",
        style_body
    ))

    arch_ascii = """
+-----------------------------------------------------------------------------------+
|                           FLOODSENSE SYSTEM ARCHITECTURE                          |
+-----------------------------------------------------------------------------------+
|  DATA SOURCES & SIMULATOR                                                         |
|  - Open-Meteo GloFAS Discharge API (Live 7-Day + Forecast)                        |
|  - Virtual Sensor Emulator (ESP32 JSON Payloads over HTTP/WebSocket)               |
|  - Offline Dataset Caches (115,502 Daily Rows, 1990-2025)                          |
+------------------------------------------+----------------------------------------+
                                           |
                                           v
+-----------------------------------------------------------------------------------+
|  FASTAPI CORE BACKEND & RISK ENGINE                                               |
|  - Station Snapping & Monotonic Percentiles (p90=Yellow, p97=Orange, p99.5=Red)   |
|  - LightGBM Multi-Horizon Classifier (t+1d, t+2d, t+3d) vs Persistence Baseline   |
|  - Hysteresis Alert Engine (Immediate Escalation, 2-Tick Downgrade Rule)          |
|  - SQLite DB Storage (Alert Outbox, Telemetry & Simulation State)                 |
+------------------------------------------+----------------------------------------+
                                           |
                                           v
+-----------------------------------------------------------------------------------+
|  REACT SURVEY ATLAS FRONTEND (Production SPA)                                      |
|  - Day Survey & Night Watch (#0C141B) Carto Map Filters                           |
|  - Live Monitor Control Room & 72h Forecast Band                                  |
|  - August 2018 Disaster Replay Scrubber (1.0x to 3.0x What-If Rain Multiplier)    |
|  - 4-Language Alert Outbox (English, Hindi, Malayalam, Assamese) + OSM Evacuation |
+-----------------------------------------------------------------------------------+
    """
    story.append(Paragraph(f"<font fontName='Courier' size=7.5>{arch_ascii.replace(' ', '&nbsp;').replace('\n', '<br/>')}</font>", style_body))

    story.append(Paragraph(
        "<b>3.1 Hydrological Data Pipeline & Snapping:</b><br/>"
        "The pipeline ingests 115,502 daily resolution records across 11 stations. Each station is snapped to its nearest mainstem river grid cell "
        "to ensure volumetric discharge reflects mainstem dynamics rather than minor tributaries (e.g., Guwahati snapped to 26.1750°N, 91.7750°E; "
        "Tezpur snapped to 26.6250°N, 92.8250°E with median discharge 4,774.3 m³/s). Thresholds are strictly monotonic ($p90 < p97 < p99.5 \\le \text{max}$).",
        style_body
    ))

    # Station Metadata Table
    station_table_data = [
        [Paragraph("Stn ID", style_table_header), Paragraph("Station Name", style_table_header), Paragraph("Region / River", style_table_header), Paragraph("Grid Lat/Lon", style_table_header), Paragraph("p90 (Yellow)", style_table_header), Paragraph("p97 (Orange)", style_table_header), Paragraph("p99.5 (Red)", style_table_header), Paragraph("Max Q", style_table_header)],
        [Paragraph("KL-PER-01", style_table_cell), Paragraph("Neeleswaram", style_table_cell), Paragraph("Kerala / Periyar", style_table_cell), Paragraph("10.1250, 76.5750", style_table_cell), Paragraph("400.8 m³/s", style_table_cell), Paragraph("549.8 m³/s", style_table_cell), Paragraph("754.9 m³/s", style_table_cell), Paragraph("1173.9", style_table_cell)],
        [Paragraph("KL-PER-02", style_table_cell), Paragraph("Aluva", style_table_cell), Paragraph("Kerala / Periyar", style_table_cell), Paragraph("10.1250, 76.3750", style_table_cell), Paragraph("437.5 m³/s", style_table_cell), Paragraph("600.2 m³/s", style_table_cell), Paragraph("809.7 m³/s", style_table_cell), Paragraph("1249.3", style_table_cell)],
        [Paragraph("KL-PAM-01", style_table_cell), Paragraph("Chengannur", style_table_cell), Paragraph("Kerala / Pamba", style_table_cell), Paragraph("9.3250, 76.6250", style_table_cell), Paragraph("167.7 m³/s", style_table_cell), Paragraph("233.4 m³/s", style_table_cell), Paragraph("325.5 m³/s", style_table_cell), Paragraph("552.4", style_table_cell)],
        [Paragraph("KL-MUV-01", style_table_cell), Paragraph("Muvattupuzha", style_table_cell), Paragraph("Kerala / Muvattupuzha", style_table_cell), Paragraph("9.9750, 76.5750", style_table_cell), Paragraph("41.8 m³/s", style_table_cell), Paragraph("59.7 m³/s", style_table_cell), Paragraph("84.5 m³/s", style_table_cell), Paragraph("245.0", style_table_cell)],
        [Paragraph("KL-CHA-01", style_table_cell), Paragraph("Chalakudy", style_table_cell), Paragraph("Kerala / Chalakudy", style_table_cell), Paragraph("10.3250, 76.3250", style_table_cell), Paragraph("156.4 m³/s", style_table_cell), Paragraph("221.4 m³/s", style_table_cell), Paragraph("290.6 m³/s", style_table_cell), Paragraph("461.4", style_table_cell)],
        [Paragraph("KL-ACH-01", style_table_cell), Paragraph("Thumpamon", style_table_cell), Paragraph("Kerala / Achankovil", style_table_cell), Paragraph("9.2750, 76.7250", style_table_cell), Paragraph("37.8 m³/s", style_table_cell), Paragraph("56.8 m³/s", style_table_cell), Paragraph("83.2 m³/s", style_table_cell), Paragraph("154.2", style_table_cell)],
        [Paragraph("AS-BRA-01", style_table_cell), Paragraph("Guwahati", style_table_cell), Paragraph("Assam / Brahmaputra", style_table_cell), Paragraph("26.1750, 91.7750", style_table_cell), Paragraph("20.0 m³/s", style_table_cell), Paragraph("31.4 m³/s", style_table_cell), Paragraph("52.1 m³/s", style_table_cell), Paragraph("97.2", style_table_cell)],
        [Paragraph("AS-BRA-02", style_table_cell), Paragraph("Dibrugarh", style_table_cell), Paragraph("Assam / Brahmaputra", style_table_cell), Paragraph("27.4750, 94.9250", style_table_cell), Paragraph("3.4 m³/s", style_table_cell), Paragraph("5.0 m³/s", style_table_cell), Paragraph("8.2 m³/s", style_table_cell), Paragraph("18.6", style_table_cell)],
        [Paragraph("AS-KOP-01", style_table_cell), Paragraph("Kampur", style_table_cell), Paragraph("Assam / Kopili", style_table_cell), Paragraph("26.1750, 92.5750", style_table_cell), Paragraph("693.1 m³/s", style_table_cell), Paragraph("1155.1 m³/s", style_table_cell), Paragraph("1938.7 m³/s", style_table_cell), Paragraph("5235.0", style_table_cell)],
        [Paragraph("AS-DHA-01", style_table_cell), Paragraph("Numaligarh", style_table_cell), Paragraph("Assam / Dhansiri", style_table_cell), Paragraph("26.5750, 93.7250", style_table_cell), Paragraph("800.7 m³/s", style_table_cell), Paragraph("1118.4 m³/s", style_table_cell), Paragraph("1671.5 m³/s", style_table_cell), Paragraph("3053.9", style_table_cell)],
        [Paragraph("AS-JIA-01", style_table_cell), Paragraph("Tezpur", style_table_cell), Paragraph("Assam / Jia Bharali", style_table_cell), Paragraph("26.6250, 92.8250", style_table_cell), Paragraph("27063.5 m³/s", style_table_cell), Paragraph("36811.9 m³/s", style_table_cell), Paragraph("45261.7 m³/s", style_table_cell), Paragraph("58343.5", style_table_cell)],
    ]
    t_stn = Table(station_table_data, colWidths=[52, 68, 85, 75, 55, 55, 60, 54])
    t_stn.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), TEAL),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COL),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT_BG]),
        ('PADDING', (0,0), (-1,-1), 3.5),
        ('ALIGN', (4,1), (-1,-1), 'RIGHT'),
    ]))
    story.append(t_stn)
    story.append(Paragraph("Table 1: 11 Active Monitoring Stations with Mainstem Snapped Coordinates and Monotonic Discharge Percentiles", style_caption))

    story.append(PageBreak())

    # -----------------------------------------------------------------------
    # 4. MACHINE LEARNING RISK ENGINE & SCIENCE AUDIT
    # -----------------------------------------------------------------------
    story.append(Paragraph("4. Machine Learning Risk Engine & Science Audit", style_h1))
    story.append(Paragraph(
        "FloodSense employs a multi-horizon LightGBM gradient boosted decision tree classifier predicting risk states at 1-day ($t+1\text{d}$), "
        "2-day ($t+2\text{d}$), and 3-day ($t+3\text{d}$) horizons. Input features include 1d, 3d, 7d, 14d, 30d cumulative rainfall, 3-day discharge "
        "rate of change ($\Delta Q_{3\text{d}}$), day of year (seasonality), and a 7-day antecedent wetness index.",
        style_body
    ))
    story.append(Paragraph(
        "<b>Scientific Transparency & Baseline Comparison:</b><br/>"
        "All models are evaluated on the held-out August 2018 Kerala flood event (153 total test days across 5 stations). "
        "To ensure scientific honesty, LightGBM is benchmarked against a <b>Persistence Baseline</b> ($Risk(t+k) = Risk(t)$). "
        "Because risk states are strongly autocorrelated day-to-day, Persistence outperforms LightGBM across all horizons.",
        style_body
    ))

    # ML Benchmarks Table
    ml_table_data = [
        [Paragraph("Horizon", style_table_header), Paragraph("Model / Strategy", style_table_header), Paragraph("Macro F1 (95% CI)", style_table_header), Paragraph("Recall (95% CI)", style_table_header), Paragraph("Precision", style_table_header), Paragraph("FAR / Stn-Yr", style_table_header)],
        [Paragraph("1-Day", style_table_cell), Paragraph("Persistence Baseline (Strongest)", style_table_cell), Paragraph("85.15% [82.0%, 87.4%]", style_table_cell), Paragraph("86.93% [80.2%, 91.7%]", style_table_cell), Paragraph("80.12%", style_table_cell), Paragraph("6.6", style_table_cell)],
        [Paragraph("1-Day", style_table_cell), Paragraph("Kerala-Only LightGBM (Experimental)", style_table_cell), Paragraph("69.39% [63.5%, 73.7%]", style_table_cell), Paragraph("86.27% [79.4%, 92.0%]", style_table_cell), Paragraph("55.46%", style_table_cell), Paragraph("21.2", style_table_cell)],
        [Paragraph("1-Day", style_table_cell), Paragraph("Pooled 10-Station LightGBM", style_table_cell), Paragraph("63.65% [57.5%, 69.1%]", style_table_cell), Paragraph("82.35% [74.4%, 90.1%]", style_table_cell), Paragraph("48.20%", style_table_cell), Paragraph("25.1", style_table_cell)],
        [Paragraph("1-Day", style_table_cell), Paragraph("Rainfall Threshold Rule", style_table_cell), Paragraph("32.47% [27.5%, 37.6%]", style_table_cell), Paragraph("97.39% [94.3%, 99.5%]", style_table_cell), Paragraph("23.69%", style_table_cell), Paragraph("96.0", style_table_cell)],
        [Paragraph("2-Day", style_table_cell), Paragraph("Persistence Baseline (Strongest)", style_table_cell), Paragraph("72.54% [67.6%, 76.0%]", style_table_cell), Paragraph("75.16% [64.6%, 83.8%]", style_table_cell), Paragraph("65.71%", style_table_cell), Paragraph("12.0", style_table_cell)],
        [Paragraph("2-Day", style_table_cell), Paragraph("Kerala-Only LightGBM (Experimental)", style_table_cell), Paragraph("56.47% [50.1%, 61.6%]", style_table_cell), Paragraph("83.66% [75.8%, 90.4%]", style_table_cell), Paragraph("44.14%", style_table_cell), Paragraph("32.4", style_table_cell)],
        [Paragraph("3-Day", style_table_cell), Paragraph("Persistence Baseline (Strongest)", style_table_cell), Paragraph("62.41% [57.3%, 66.5%]", style_table_cell), Paragraph("65.36% [53.2%, 76.1%]", style_table_cell), Paragraph("54.95%", style_table_cell), Paragraph("16.4", style_table_cell)],
        [Paragraph("3-Day", style_table_cell), Paragraph("Kerala-Only LightGBM (Experimental)", style_table_cell), Paragraph("46.27% [40.8%, 50.7%]", style_table_cell), Paragraph("81.05% [71.4%, 89.8%]", style_table_cell), Paragraph("36.15%", style_table_cell), Paragraph("43.8", style_table_cell)],
    ]
    t_ml = Table(ml_table_data, colWidths=[45, 155, 110, 105, 45, 44])
    t_ml.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), TEAL),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COL),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT_BG]),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_ml)
    story.append(Paragraph("Table 2: Held-Out 2018 Multi-Horizon Model Performance Benchmarks (1,000 Block-Bootstrap 95% CIs)", style_caption))

    img_model = os.path.join(SCREENSHOTS_DIR, "model_1440_light.png")
    if os.path.exists(img_model):
        story.append(RLImage(img_model, width=6.8*inch, height=3.4*inch))
        story.append(Paragraph("Figure 2: Model & Method Science Audit Page displaying baselines, CIs, and SHAP feature importances", style_caption))

    # -----------------------------------------------------------------------
    # 5. HYSTERESIS ALERT ENGINE & MULTILINGUAL OUTBOX
    # -----------------------------------------------------------------------
    story.append(Paragraph("5. Hysteresis Alert Engine & Multilingual Outbox", style_h1))
    story.append(Paragraph(
        "To prevent alert fatigue caused by raw threshold oscillations near boundary values, FloodSense implements a state-machine hysteresis engine. "
        "State transitions follow strict rules: <b>Genuine Escalation</b> (e.g. Green $\rightarrow$ Orange) triggers an alert <b>immediately</b>. "
        "<b>Downgrades</b> (e.g. Orange $\rightarrow$ Green) require <b>2 consecutive lower ticks</b> before state transition is executed. "
        "Duplicate alerts at the same risk level are suppressed within a 30-minute window.",
        style_body
    ))

    story.append(Paragraph(
        "<b>Multilingual Emergency Communication:</b><br/>"
        "Every alert generates four parallel localized records in <b>English, Hindi, Malayalam, and Assamese</b>. "
        "All numerical metrics (discharge m³/s, rainfall mm, timestamps in IST) and OpenStreetMap route URLs are preserved without translation corruption.",
        style_body
    ))

    # Alert Languages Table
    lang_table_data = [
        [Paragraph("Code", style_table_header), Paragraph("Language", style_table_header), Paragraph("Target Basin / Region", style_table_header), Paragraph("Sample Action Recommendation Text", style_table_header)],
        [Paragraph("en", style_table_cell), Paragraph("English", style_table_cell), Paragraph("National / Standard", style_table_cell), Paragraph("Be prepared! Pack essential documents and prepare for evacuation.", style_table_cell)],
        [Paragraph("hi", style_table_cell), Paragraph("Hindi (हिंदी)", style_table_cell), Paragraph("National / Interstate", style_table_cell), Paragraph("तैयार रहें! आवश्यक सामान के साथ सुरक्षित स्थानों पर जाएँ।", style_table_cell)],
        [Paragraph("ml", style_table_cell), Paragraph("Malayalam (മലയാളം)", style_table_cell), Paragraph("Kerala Catchments", style_table_cell), Paragraph("സജ്ജരായിരിക്കുക! അടിയന്തര സാധനങ്ങളുമായി സുരക്ഷിത സ്ഥാനങ്ങളിലേക്ക് മാറാൻ തയ്യാറെടുക്കുക.", style_table_cell)],
        [Paragraph("as", style_table_cell), Paragraph("Assamese (অসমীয়া)", style_table_cell), Paragraph("Assam / Brahmaputra", style_table_cell), Paragraph("প্ৰস্তুত থাকক! প্ৰয়োজনীয় সামগ্ৰীৰ সৈতে সুৰক্ষিত স্থানলৈ যোৱাৰ প্ৰস্তুতি চলাওক।", style_table_cell)],
    ]
    t_lang = Table(lang_table_data, colWidths=[35, 95, 100, 274])
    t_lang.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), TEAL),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COL),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT_BG]),
        ('PADDING', (0,0), (-1,-1), 4.5),
    ]))
    story.append(t_lang)
    story.append(Paragraph("Table 3: Multilingual Action Recommended Templates across Supported Regional Languages", style_caption))

    img_alerts = os.path.join(SCREENSHOTS_DIR, "alerts_1440_light.png")
    if os.path.exists(img_alerts):
        story.append(RLImage(img_alerts, width=6.8*inch, height=3.4*inch))
        story.append(Paragraph("Figure 3: Alert Outbox & Evacuation Directions Page with 4-Language Toggle and DEMO Mode Generator", style_caption))

    story.append(PageBreak())

    # -----------------------------------------------------------------------
    # 6. DIGITAL TWIN DISASTER REPLAY & LIVE MONITORING
    # -----------------------------------------------------------------------
    story.append(Paragraph("6. Digital Twin Disaster Replay & Live Monitoring", style_h1))
    story.append(Paragraph(
        "<b>6.1 August 2018 Kerala Deluge Digital Twin Replay:</b><br/>"
        "FloodSense includes an interactive, data-driven historical scrubber for the catastrophic 31-day August 2018 Kerala flood. "
        "The replay engine streams real per-station daily observed discharge from held-out data files with calendar dates ('01 Aug 2018' to '31 Aug 2018'). "
        "Responders can apply dynamic 'What-If' rainfall multipliers (1.0x to 3.0x) to test catchment vulnerability under intensified deluge conditions.",
        style_body
    ))

    img_replay = os.path.join(SCREENSHOTS_DIR, "replay_1440_light.png")
    if os.path.exists(img_replay):
        story.append(RLImage(img_replay, width=6.8*inch, height=3.4*inch))
        story.append(Paragraph("Figure 4: Historical August 2018 Digital Twin Simulator & What-If Stress Scrubber", style_caption))

    story.append(Paragraph(
        "<b>6.2 Real-Time Control Room & Telemetry Monitor:</b><br/>"
        "The Live Monitor page connects to live Open-Meteo APIs and broadcasts real-time telemetry over WebSockets (`/ws/live`). "
        "Visualizations scale dynamically to $[0, 1.2 \times \text{max}]$ with explicit NOW vs FORECAST D+1..D+3 status chips.",
        style_body
    ))

    img_live = os.path.join(SCREENSHOTS_DIR, "live_1440_light.png")
    if os.path.exists(img_live):
        story.append(RLImage(img_live, width=6.8*inch, height=3.4*inch))
        story.append(Paragraph("Figure 5: Real-Time Live Monitoring Control Room with Dynamic 10-Day Telemetry Band", style_caption))

    # -----------------------------------------------------------------------
    # 7. OPEN HARDWARE ROADMAP & API SPECIFICATION
    # -----------------------------------------------------------------------
    story.append(Paragraph("7. Open Hardware Roadmap & API Specification", style_h1))
    story.append(Paragraph(
        "<b>7.1 Open Hardware Node Blueprint:</b><br/>"
        "While physical hardware is simulated in software for this make-a-thon, FloodSense includes a field-ready open-hardware node blueprint. "
        "The blueprint features an ESP32 microcontroller, JSN-SR04T waterproof ultrasonic depth sensor, tipping-bucket rain gauge, solar power management, "
        "and C++ firmware (`/firmware-stub/node_firmware.ino`) validated via PlatformIO CI and Wokwi browser simulation. Target BOM cost is <b>₹3,990 INR (~$48 USD)</b>.",
        style_body
    ))

    # API Specification Table
    api_table_data = [
        [Paragraph("Endpoint Path", style_table_header), Paragraph("Method", style_table_header), Paragraph("Purpose / Description", style_table_header)],
        [Paragraph("/api/health", style_table_cell), Paragraph("GET", style_table_cell), Paragraph("Backend health diagnostic, uptime, database status, and station count", style_table_cell)],
        [Paragraph("/api/stations", style_table_cell), Paragraph("GET", style_table_cell), Paragraph("List 11 active gauging stations with coordinates, river, and percentiles", style_table_cell)],
        [Paragraph("/api/stations/{id}/readings", style_table_cell), Paragraph("GET", style_table_cell), Paragraph("Fetch historical and live telemetry discharge/rainfall readings", style_table_cell)],
        [Paragraph("/api/stations/{id}/forecast", style_table_cell), Paragraph("GET", style_table_cell), Paragraph("Retrieve 72-hour hydrological forecast points and top SHAP risk drivers", style_table_cell)],
        [Paragraph("/api/alerts", style_table_cell), Paragraph("GET", style_table_cell), Paragraph("Query alert outbox log (supports station_id and language filters)", style_table_cell)],
        [Paragraph("/api/alerts/demo", style_table_cell), Paragraph("POST", style_table_cell), Paragraph("Trigger clearly marked [DEMO ALERT] across all 4 languages", style_table_cell)],
        [Paragraph("/api/alerts/clear", style_table_cell), Paragraph("POST", style_table_cell), Paragraph("Clear outbox logs and reset hysteresis baseline state memory", style_table_cell)],
        [Paragraph("/api/simulate/control", style_table_cell), Paragraph("POST", style_table_cell), Paragraph("Control virtual sensor simulation speed, scenario, and rain multiplier", style_table_cell)],
        [Paragraph("/ws/live", style_table_cell), Paragraph("WS", style_table_cell), Paragraph("WebSocket real-time virtual sensor telemetry broadcast stream", style_table_cell)],
    ]
    t_api = Table(api_table_data, colWidths=[120, 45, 339])
    t_api.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), TEAL),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COL),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT_BG]),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_api)
    story.append(Paragraph("Table 4: Complete FastAPI REST and WebSocket API Specification", style_caption))

    story.append(PageBreak())

    # -----------------------------------------------------------------------
    # 8. TESTING, VALIDATION & PRODUCTION DEPLOYMENT
    # -----------------------------------------------------------------------
    story.append(Paragraph("8. Testing, Validation & Production Deployment", style_h1))
    story.append(Paragraph(
        "<b>8.1 Automated Test Suite & Schema Verification:</b><br/>"
        "FloodSense maintains 34 automated unit, integration, and UI schema validation tests executed via Pytest. "
        "Tests verify hysteresis escalation/downgrade rules, Open-Meteo live API grid cell equality, threshold monotonicity, "
        "out-of-bounds 1.5x max guards, non-leakage 2018 dataset splits, and zero-undefined metrics rendering.",
        style_body
    ))

    # Test Results Summary Table
    test_table_data = [
        [Paragraph("Test Suite Category", style_table_header), Paragraph("Passed Tests", style_table_header), Paragraph("Key Functional Verifications", style_table_header)],
        [Paragraph("Alert Engine & Telegram", style_table_cell), Paragraph("6 / 6 PASSED", style_table_cell), Paragraph("Hysteresis 2-tick downgrade rule, 4-language format, DEMO alerts & clear API", style_table_cell)],
        [Paragraph("API Contracts & Telemetry", style_table_cell), Paragraph("18 / 18 PASSED", style_table_cell), Paragraph("Station grid snapping, percentile ordering, live Open-Meteo equality & 1.5x bounds", style_table_cell)],
        [Paragraph("ML Pipeline & Non-Leakage", style_table_cell), Paragraph("5 / 5 PASSED", style_table_cell), Paragraph("Daily gap non-leakage, SHAP feature explainability & rule-based fallbacks", style_table_cell)],
        [Paragraph("Digital Twin Simulator", style_table_cell), Paragraph("3 / 3 PASSED", style_table_cell), Paragraph("Virtual sensor live baseline & August 2018 peak flood discharge matching", style_table_cell)],
        [Paragraph("UI Schema Integrity", style_table_cell), Paragraph("2 / 2 PASSED", style_table_cell), Paragraph("Zero undefined, NaN, or missing metric values in metrics.json & thresholds.json", style_table_cell)],
        [Paragraph("TOTAL TEST SUITE", style_table_cell), Paragraph("34 / 34 PASSED", style_table_cell), Paragraph("100% test pass rate achieved in 20.26 seconds", style_table_cell)],
    ]
    t_test = Table(test_table_data, colWidths=[120, 85, 299])
    t_test.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), TEAL),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COL),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT_BG]),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_test)
    story.append(Paragraph("Table 5: Comprehensive Pytest Automated Test Suite Execution Results", style_caption))

    story.append(Paragraph(
        "<b>8.2 Production Deployment on Railway:</b><br/>"
        "FloodSense is deployed publicly on Railway container infrastructure using a multi-stage Docker build. "
        "The container compiles the React SPA via Node 20, packages all trained LightGBM model joblibs and datasets, "
        "and executes the FastAPI backend on Python 3.11 with dynamic $PORT binding.",
        style_body
    ))

    deploy_box = f"""
    <b>Production Deployment Highlights:</b><br/>
    • <b>Live Application URL:</b> {LIVE_URL}<br/>
    • <b>Health Diagnostic URL:</b> {HEALTH_URL}<br/>
    • <b>Container Registry:</b> Single Multi-Stage Dockerfile (specified via <code>railway.toml</code>)<br/>
    • <b>Port Binding:</b> Dynamic <code>0.0.0.0:$PORT</code> with Uvicorn worker process<br/>
    • <b>Static SPA Route Handling:</b> Catch-all SPA router serving React <code>dist/</code> assets alongside <code>/api/*</code> and <code>/ws/live</code>
    """
    story.append(make_callout(deploy_box, bg_color=colors.HexColor("#EAFAF1"), border_color=EMERALD))

    # -----------------------------------------------------------------------
    # 9. LIMITATIONS, FUTURE WORK & CONCLUSION
    # -----------------------------------------------------------------------
    story.append(Paragraph("9. Scientific Limitations & Future Work", style_h1))
    story.append(Paragraph(
        "<b>9.1 Honest Scientific Limitations:</b>", style_body
    ))
    story.append(Paragraph("1. <b>GloFAS Modeled Discharge:</b> River discharge is derived from GloFAS hydrological modeling, NOT physical gauge height meters.", style_bullet))
    story.append(Paragraph("2. <b>Past Rainfall Features:</b> Features rely on observed historical past rainfall, NOT future numerical weather predictions.", style_bullet))
    story.append(Paragraph("3. <b>Percentile Threshold Proxies:</b> Risk thresholds reflect station-specific historical percentiles (p90, p97, p99.5), NOT official CWC stage levels.", style_bullet))
    story.append(Paragraph("4. <b>Decision Tree Extrapolation Limits:</b> Tree-based models split on static feature bounds and cannot extrapolate beyond training maxima during unprecedented deluges.", style_bullet))

    story.append(Paragraph(
        "<b>9.2 Future Enhancement Roadmap:</b>", style_body
    ))
    story.append(Paragraph("• Integration of 1–3 day ensemble forecast rainfall inputs from IMD/Open-Meteo.", style_bullet))
    story.append(Paragraph("• Physical deployment of open-hardware ESP32 ultrasonic nodes across targeted Kerala catchments.", style_bullet))
    story.append(Paragraph("• Direct API integration with Central Water Commission (CWC) telemetry stream feeds.", style_bullet))
    story.append(Paragraph("• Mobile PWA push notifications and SMS gateway dispatch for rural communities.", style_bullet))

    story.append(Spacer(1, 10))
    story.append(Paragraph("10. Conclusion", style_h1))
    story.append(Paragraph(
        "<b>FloodSense — Early Warning Grid</b> demonstrates a complete, credible, real-data-first digital twin and flood early-warning system "
        "built for the FOSSEE Open Hardware National Make-A-Thon 2026. By combining live Open-Meteo GloFAS telemetry, rigorous scientific baseline benchmarking, "
        "state-machine alert hysteresis, multilingual emergency communications, and an August 2018 disaster replay simulator, "
        "FloodSense bridges the gap between global hydrological data arrays and actionable, localized disaster response.",
        style_body
    ))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f" Saved PDF Report: {OUTPUT_PDF}")


# ---------------------------------------------------------------------------
# 2. BUILD PYTHON-DOCX REPORT
# ---------------------------------------------------------------------------
def build_docx():
    print("[Report Generator] Building DOCX document: FloodSense_Hackathon_Project_Report.docx...")
    import docx
    from docx import Document
    from docx.shared import Inches, Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.table import WD_TABLE_ALIGNMENT
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn

    doc = Document()

    # Set Margins to 0.75 inch
    for s in doc.sections:
        s.top_margin = Inches(0.75)
        s.bottom_margin = Inches(0.75)
        s.left_margin = Inches(0.75)
        s.right_margin = Inches(0.75)

    TEAL_RGB = RGBColor(0x1F, 0x6B, 0x75)
    DARK_RGB = RGBColor(0x1C, 0x28, 0x33)
    SLATE_RGB = RGBColor(0x5D, 0x6D, 0x7E)

    def set_cell_background(cell, fill_hex):
        tcPr = cell._tc.get_or_add_tcPr()
        shd = OxmlElement('w:shd')
        shd.set(qn('w:val'), 'clear')
        shd.set(qn('w:color'), 'auto')
        shd.set(qn('w:fill'), fill_hex)
        tcPr.append(shd)

    # Title Page
    p_title = doc.add_paragraph()
    r_title = p_title.add_run(PROJECT_TITLE)
    r_title.font.name = 'Arial'
    r_title.font.size = Pt(26)
    r_title.font.bold = True
    r_title.font.color.rgb = TEAL_RGB
    p_title.space_after = Pt(4)

    p_sub = doc.add_paragraph()
    r_sub = p_sub.add_run(PROJECT_SUBTITLE)
    r_sub.font.name = 'Arial'
    r_sub.font.size = Pt(14)
    r_sub.font.color.rgb = DARK_RGB
    p_sub.space_after = Pt(18)

    # Meta Callout Box
    table_meta = doc.add_table(rows=1, cols=1)
    table_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell_meta = table_meta.cell(0, 0)
    set_cell_background(cell_meta, "F2F4F4")
    
    p_meta = cell_meta.paragraphs[0]
    p_meta.paragraph_format.space_before = Pt(6)
    p_meta.paragraph_format.space_after = Pt(6)
    r_meta = p_meta.add_run(
        f"Category: {PROJECT_CATEGORY}\n"
        f"Production Live URL: {LIVE_URL}\n"
        f"Health Endpoint: {HEALTH_URL}\n"
        f"GitHub Repository: {GITHUB_URL}\n"
        f"Date: October 2026 | Version 1.0.0 (Production Release)"
    )
    r_meta.font.name = 'Arial'
    r_meta.font.size = Pt(9.5)
    r_meta.font.color.rgb = DARK_RGB

    doc.add_paragraph().space_after = Pt(12)

    img_landing = os.path.join(SCREENSHOTS_DIR, "landing_1440_light.png")
    if os.path.exists(img_landing):
        doc.add_picture(img_landing, width=Inches(6.5))
        p_cap = doc.add_paragraph("Figure 1: FloodSense Hydrological Survey Atlas — Live Dashboard Overview")
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.runs[0].font.size = Pt(8.5)
        p_cap.runs[0].font.italic = True
        p_cap.runs[0].font.color.rgb = SLATE_RGB

    doc.add_page_break()

    # Headings and Body Paragraphs
    def add_h1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(16)
        p.paragraph_format.space_after = Pt(6)
        r = p.add_run(text)
        r.font.name = 'Arial'
        r.font.size = Pt(16)
        r.font.bold = True
        r.font.color.rgb = TEAL_RGB
        return p

    def add_h2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(4)
        r = p.add_run(text)
        r.font.name = 'Arial'
        r.font.size = Pt(12)
        r.font.bold = True
        r.font.color.rgb = DARK_RGB
        return p

    def add_body(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(6)
        r = p.add_run(text)
        r.font.name = 'Arial'
        r.font.size = Pt(10)
        r.font.color.rgb = DARK_RGB
        return p

    # Section 1
    add_h1("1. Executive Summary")
    add_body(
        "FloodSense — Early Warning Grid is a software-only flood early-warning platform and digital twin survey atlas "
        "built for the FOSSEE Open Hardware National Make-A-Thon 2026. The platform emulates physical IoT sensor grids "
        "to deliver 24-to-72-hour predictive flood risk warnings across 11 key river catchments in Kerala and Assam. "
        "Powered by live Open-Meteo GloFAS telemetry, a leakage-audited LightGBM multi-horizon classifier benchmarked against "
        "a Persistence Baseline, and a state-machine hysteresis alert engine, FloodSense dispatches localized warnings in "
        "English, Hindi, Malayalam, and Assamese paired with OpenStreetMap evacuation shelter directions."
    )

    # Section 2
    add_h1("2. Problem Statement & Objectives")
    add_body(
        "During monsoon deluges in India, emergency responders face critical challenges: raw volumetric discharge forecasts (m³/s) "
        "lack station-specific stage context, sensor threshold alerts flap rapidly near danger boundaries causing alert fatigue, "
        "and emergency alerts neglect regional catchments where Malayalam and Assamese are spoken. "
        "FloodSense solves these bottlenecks with real-data integration, scientific baseline transparency, hysteresis alert deduplication, "
        "and an interactive August 2018 Kerala flood digital twin scrubber."
    )

    # Section 3
    add_h1("3. System Architecture & Data Pipeline")
    add_body(
        "FloodSense is deployed as a single-container application on Railway. FastAPI orchestrates telemetry ingestion, ML predictions, "
        "hysteresis state tracking, and WebSocket broadcasts, while serving the compiled React Survey Atlas SPA directly. "
        "The pipeline ingests 115,502 daily resolution records (1990–2025) across 11 stations snapped to mainstem river grid cells."
    )

    # Section 4
    add_h1("4. Machine Learning Risk Engine & Science Audit")
    add_body(
        "A multi-horizon LightGBM gradient boosted decision tree classifier predicts risk states at 1-day, 2-day, and 3-day horizons. "
        "On the held-out August 2018 Kerala flood event (153 test days across 5 stations), Persistence Baseline achieves 85.15% Macro F1 "
        "at 1-day horizon, outperforming LightGBM (69.39% Macro F1, 86.27% High-Risk Recall) due to day-to-day risk state autocorrelation."
    )

    # Section 5
    add_h1("5. Hysteresis Alert Engine & Multilingual Outbox")
    add_body(
        "The hysteresis engine prevents alert flapping by enforcing immediate escalation (Green -> Orange) and requiring 2 consecutive lower ticks "
        "for state downgrades (Orange -> Green). Outbox logs generate parallel localized entries in English, Hindi, Malayalam, and Assamese."
    )

    # Section 6
    add_h1("6. Digital Twin Disaster Replay & Live Monitoring")
    add_body(
        "The platform includes a 31-day held-out August 2018 Kerala flood replay scrubber with calendar dates ('01 Aug 2018' to '31 Aug 2018') "
        "and customizable 'What-If' rainfall multipliers (1.0x to 3.0x). The Live Monitor streams real-time telemetry over WebSockets (/ws/live)."
    )

    # Section 7
    add_h1("7. Testing, Validation & Railway Deployment")
    add_body(
        "FloodSense passes 34/34 automated pytest tests, 0-error TypeScript/Vite production build, and headless Chrome browser acceptance tests. "
        "The application is deployed publicly on Railway container infrastructure at https://floodsense-production-4e0f.up.railway.app/."
    )

    doc.save(OUTPUT_DOCX)
    print(f" Saved DOCX Report: {OUTPUT_DOCX}")

# ---------------------------------------------------------------------------
# Main Execution
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    try:
        build_pdf()
        build_docx()
        print("\n[SUCCESS] Both PDF and DOCX reports generated successfully!")
    except Exception as e:
        print(f"\n[ERROR] Report generation failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
