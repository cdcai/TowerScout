from __future__ import annotations

import re
import zipfile
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable
from xml.sax.saxutils import escape


ROOT = Path(__file__).resolve().parents[2]
AGENT_WORK = ROOT / ".agent_work"
OUTPUT_DIR = AGENT_WORK / "context" / "analysis" / "project-end-planning"
AS_OF = date(2026, 10, 1)
PROJECT_END = date(2026, 10, 31)
OPERATIONAL_CLOSEOUT = date(2026, 10, 30)


def clean_text(value: object) -> str:
    text = "" if value is None else str(value)
    text = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", "", text)
    return text


def xml_text(value: object) -> str:
    return escape(clean_text(value), {'"': "&quot;", "'": "&apos;"})


def col_name(index: int) -> str:
    result = ""
    while index:
        index, remainder = divmod(index - 1, 26)
        result = chr(65 + remainder) + result
    return result


def safe_table_name(name: str) -> str:
    value = re.sub(r"[^A-Za-z0-9_]", "_", name)
    if not value or value[0].isdigit():
        value = "T_" + value
    return value[:200]


def style_for_value(header: str, value: object) -> int:
    heading = header.lower()
    text = clean_text(value).lower()
    if not any(
        token in heading
        for token in (
            "status",
            "priority",
            "recommendation",
            "gate",
            "disposition",
            "authority",
            "risk",
            "interpretation",
        )
    ):
        return 4
    if any(token in text for token in ("complete", "pass", "closed", "resolved")):
        return 6
    if any(token in text for token in ("critical", "blocked", "at risk", "must", "high risk")):
        return 8
    if any(token in text for token in ("defer", "historical", "not scheduled", "superseded", "low")):
        return 9
    if any(token in text for token in ("conditional", "owner-gated", "medium", "decision")):
        return 7
    if any(token in text for token in ("required", "in progress", "work now", "high", "open")):
        return 10
    return 4


def build_styles_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <fonts count="4">
    <font><sz val="11"/><name val="Calibri"/><family val="2"/></font>
    <font><b/><color rgb="FFFFFFFF"/><sz val="16"/><name val="Calibri"/></font>
    <font><b/><color rgb="FFFFFFFF"/><sz val="11"/><name val="Calibri"/></font>
    <font><i/><color rgb="FF44546A"/><sz val="10"/><name val="Calibri"/></font>
  </fonts>
  <fills count="9">
    <fill><patternFill patternType="none"/></fill>
    <fill><patternFill patternType="gray125"/></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FF17365D"/><bgColor indexed="64"/></patternFill></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FFD9EAF7"/><bgColor indexed="64"/></patternFill></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FFE2F0D9"/><bgColor indexed="64"/></patternFill></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FFFFF2CC"/><bgColor indexed="64"/></patternFill></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FFF4CCCC"/><bgColor indexed="64"/></patternFill></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FFE7E6E6"/><bgColor indexed="64"/></patternFill></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FFFCE4D6"/><bgColor indexed="64"/></patternFill></fill>
  </fills>
  <borders count="2">
    <border><left/><right/><top/><bottom/><diagonal/></border>
    <border>
      <left style="thin"><color rgb="FFB4C6E7"/></left>
      <right style="thin"><color rgb="FFB4C6E7"/></right>
      <top style="thin"><color rgb="FFB4C6E7"/></top>
      <bottom style="thin"><color rgb="FFB4C6E7"/></bottom>
      <diagonal/>
    </border>
  </borders>
  <cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
  <cellXfs count="11">
    <xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>
    <xf numFmtId="0" fontId="1" fillId="2" borderId="0" xfId="0" applyFont="1" applyFill="1" applyAlignment="1"><alignment vertical="center"/></xf>
    <xf numFmtId="0" fontId="3" fillId="3" borderId="0" xfId="0" applyFont="1" applyFill="1" applyAlignment="1"><alignment wrapText="1" vertical="center"/></xf>
    <xf numFmtId="0" fontId="2" fillId="2" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment horizontal="center" vertical="center" wrapText="1"/></xf>
    <xf numFmtId="0" fontId="0" fillId="0" borderId="1" xfId="0" applyBorder="1" applyAlignment="1"><alignment vertical="top" wrapText="1"/></xf>
    <xf numFmtId="0" fontId="2" fillId="2" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment vertical="center" wrapText="1"/></xf>
    <xf numFmtId="0" fontId="0" fillId="4" borderId="1" xfId="0" applyFill="1" applyBorder="1" applyAlignment="1"><alignment vertical="top" wrapText="1"/></xf>
    <xf numFmtId="0" fontId="0" fillId="5" borderId="1" xfId="0" applyFill="1" applyBorder="1" applyAlignment="1"><alignment vertical="top" wrapText="1"/></xf>
    <xf numFmtId="0" fontId="0" fillId="6" borderId="1" xfId="0" applyFill="1" applyBorder="1" applyAlignment="1"><alignment vertical="top" wrapText="1"/></xf>
    <xf numFmtId="0" fontId="0" fillId="7" borderId="1" xfId="0" applyFill="1" applyBorder="1" applyAlignment="1"><alignment vertical="top" wrapText="1"/></xf>
    <xf numFmtId="0" fontId="0" fillId="8" borderId="1" xfId="0" applyFill="1" applyBorder="1" applyAlignment="1"><alignment vertical="top" wrapText="1"/></xf>
  </cellXfs>
  <cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>
  <dxfs count="0"/>
  <tableStyles count="1" defaultTableStyle="TableStyleMedium2" defaultPivotStyle="PivotStyleLight16"/>
</styleSheet>"""


def build_cell(ref: str, value: object, style: int) -> str:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return f'<c r="{ref}" s="{style}"><v>{value}</v></c>'
    text = xml_text(value)
    return f'<c r="{ref}" s="{style}" t="inlineStr"><is><t xml:space="preserve">{text}</t></is></c>'


def build_sheet_xml(sheet: dict, table_id: int) -> tuple[str, str, str]:
    headers = sheet["headers"]
    rows = sheet["rows"]
    ncols = len(headers)
    last_col = col_name(ncols)
    last_row = 4 + len(rows)
    widths = sheet.get("widths", [16] * ncols)
    if len(widths) < ncols:
        widths = widths + [16] * (ncols - len(widths))

    xml_rows: list[str] = []
    title_cells = build_cell("A1", sheet["title"], 1)
    xml_rows.append(f'<row r="1" ht="26" customHeight="1">{title_cells}</row>')
    subtitle_cells = build_cell("A2", sheet.get("description", ""), 2)
    xml_rows.append(f'<row r="2" ht="42" customHeight="1">{subtitle_cells}</row>')
    xml_rows.append('<row r="3" ht="6" customHeight="1"></row>')
    header_cells = "".join(
        build_cell(f"{col_name(index)}4", header, 3)
        for index, header in enumerate(headers, start=1)
    )
    xml_rows.append(f'<row r="4" ht="36" customHeight="1">{header_cells}</row>')

    for row_index, row in enumerate(rows, start=5):
        cells = []
        for col_index, header in enumerate(headers, start=1):
            value = row[col_index - 1] if col_index - 1 < len(row) else ""
            style = style_for_value(header, value)
            cells.append(build_cell(f"{col_name(col_index)}{row_index}", value, style))
        xml_rows.append(
            f'<row r="{row_index}" ht="48" customHeight="1">{"".join(cells)}</row>'
        )

    col_xml = "".join(
        f'<col min="{index}" max="{index}" width="{width}" customWidth="1"/>'
        for index, width in enumerate(widths, start=1)
    )
    freeze_cols = int(sheet.get("freeze_cols", 0))
    if freeze_cols:
        pane = (
            f'<pane xSplit="{freeze_cols}" ySplit="4" topLeftCell="{col_name(freeze_cols + 1)}5" '
            'activePane="bottomRight" state="frozen"/>'
            f'<selection pane="bottomRight" activeCell="{col_name(freeze_cols + 1)}5" sqref="{col_name(freeze_cols + 1)}5"/>'
        )
    else:
        pane = '<pane ySplit="4" topLeftCell="A5" activePane="bottomLeft" state="frozen"/><selection pane="bottomLeft" activeCell="A5" sqref="A5"/>'

    worksheet_xml = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <dimension ref="A1:{last_col}{last_row}"/>
  <sheetViews><sheetView workbookViewId="0" showGridLines="0">{pane}</sheetView></sheetViews>
  <sheetFormatPr defaultRowHeight="15"/>
  <cols>{col_xml}</cols>
  <sheetData>{''.join(xml_rows)}</sheetData>
  <mergeCells count="2"><mergeCell ref="A1:{last_col}1"/><mergeCell ref="A2:{last_col}2"/></mergeCells>
  <pageMargins left="0.25" right="0.25" top="0.5" bottom="0.5" header="0.2" footer="0.2"/>
  <tableParts count="1"><tablePart r:id="rId1"/></tableParts>
</worksheet>'''

    table_ref = f"A4:{last_col}{last_row}"
    table_columns = "".join(
        f'<tableColumn id="{index}" name="{xml_text(header)}"/>'
        for index, header in enumerate(headers, start=1)
    )
    table_name = safe_table_name(sheet.get("table_name", f"Table{table_id}"))
    table_xml = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<table xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" id="{table_id}" name="{table_name}" displayName="{table_name}" ref="{table_ref}" totalsRowShown="0">
  <autoFilter ref="{table_ref}"/>
  <tableColumns count="{ncols}">{table_columns}</tableColumns>
  <tableStyleInfo name="TableStyleMedium2" showFirstColumn="0" showLastColumn="0" showRowStripes="1" showColumnStripes="0"/>
</table>'''
    rels_xml = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/table" Target="../tables/table{table_id}.xml"/>
</Relationships>'''
    return worksheet_xml, table_xml, rels_xml


def write_workbook(path: Path, sheets: list[dict], subject: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    sheet_entries = "".join(
        f'<sheet name="{xml_text(sheet["name"][:31])}" sheetId="{index}" r:id="rId{index}"/>'
        for index, sheet in enumerate(sheets, start=1)
    )
    workbook_xml = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <bookViews><workbookView xWindow="120" yWindow="120" windowWidth="24000" windowHeight="15000" activeTab="0"/></bookViews>
  <sheets>{sheet_entries}</sheets>
  <calcPr calcId="191029" fullCalcOnLoad="1"/>
</workbook>'''
    rel_entries = "".join(
        f'<Relationship Id="rId{index}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{index}.xml"/>'
        for index in range(1, len(sheets) + 1)
    )
    workbook_rels = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  {rel_entries}
  <Relationship Id="rId{len(sheets) + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>'''
    worksheet_overrides = "".join(
        f'<Override PartName="/xl/worksheets/sheet{index}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        for index in range(1, len(sheets) + 1)
    )
    table_overrides = "".join(
        f'<Override PartName="/xl/tables/table{index}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.table+xml"/>'
        for index in range(1, len(sheets) + 1)
    )
    content_types = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
  <Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>
  {worksheet_overrides}
  {table_overrides}
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>'''
    package_rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>'''
    stamp = datetime(2026, 10, 1, 16, 0, tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")
    core_xml = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:creator>OpenAI Codex for TowerScout</dc:creator>
  <cp:lastModifiedBy>OpenAI Codex for TowerScout</cp:lastModifiedBy>
  <dc:title>{xml_text(subject)}</dc:title>
  <dc:subject>{xml_text(subject)}</dc:subject>
  <dcterms:created xsi:type="dcterms:W3CDTF">{stamp}</dcterms:created>
  <dcterms:modified xsi:type="dcterms:W3CDTF">{stamp}</dcterms:modified>
</cp:coreProperties>'''
    titles = "".join(f'<vt:lpstr>{xml_text(sheet["name"][:31])}</vt:lpstr>' for sheet in sheets)
    app_xml = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>Microsoft Excel Compatible Open XML</Application>
  <DocSecurity>0</DocSecurity><ScaleCrop>false</ScaleCrop>
  <HeadingPairs><vt:vector size="2" baseType="variant"><vt:variant><vt:lpstr>Worksheets</vt:lpstr></vt:variant><vt:variant><vt:i4>{len(sheets)}</vt:i4></vt:variant></vt:vector></HeadingPairs>
  <TitlesOfParts><vt:vector size="{len(sheets)}" baseType="lpstr">{titles}</vt:vector></TitlesOfParts>
  <Company>TowerScout</Company><LinksUpToDate>false</LinksUpToDate><SharedDoc>false</SharedDoc><HyperlinksChanged>false</HyperlinksChanged><AppVersion>16.0300</AppVersion>
</Properties>'''

    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", content_types)
        archive.writestr("_rels/.rels", package_rels)
        archive.writestr("docProps/core.xml", core_xml)
        archive.writestr("docProps/app.xml", app_xml)
        archive.writestr("xl/workbook.xml", workbook_xml)
        archive.writestr("xl/_rels/workbook.xml.rels", workbook_rels)
        archive.writestr("xl/styles.xml", build_styles_xml())
        for index, sheet in enumerate(sheets, start=1):
            worksheet_xml, table_xml, rels_xml = build_sheet_xml(sheet, index)
            archive.writestr(f"xl/worksheets/sheet{index}.xml", worksheet_xml)
            archive.writestr(f"xl/worksheets/_rels/sheet{index}.xml.rels", rels_xml)
            archive.writestr(f"xl/tables/table{index}.xml", table_xml)


def action(
    action_id: str,
    workstream: str,
    title: str,
    summary: str,
    status: str,
    priority: str,
    recommendation: str,
    gate: str,
    source_task: str,
    created: str,
    why_open: str,
    effort: str,
    outcome: str,
    blockers: str,
    target: str,
    owner: str,
    done_when: str,
    risk: str,
    planned_week: str,
    confidence: str,
    source_ref: str,
) -> list[object]:
    return [
        action_id,
        workstream,
        title,
        summary,
        status,
        priority,
        recommendation,
        gate,
        source_task,
        created,
        why_open,
        effort,
        outcome,
        blockers,
        target,
        owner,
        done_when,
        risk,
        planned_week,
        confidence,
        source_ref,
    ]


ACTION_HEADERS = [
    "Action ID",
    "Workstream",
    "Action",
    "Plain-language summary",
    "Current status",
    "Priority",
    "Recommendation",
    "Release / handoff gate",
    "Task or source",
    "Created / first recorded",
    "Why it is still open",
    "Estimated effort",
    "Expected outcome",
    "Blockers / dependencies",
    "Target date",
    "Owner / role",
    "Done when",
    "Risk if skipped",
    "Planned week",
    "Estimate confidence",
    "Primary source reference",
]


def build_open_actions() -> list[list[object]]:
    common_release_created = "2026-09-21 plan; updated 2026-10-01"
    rows = [
        action("R01", "Release package", "Approve the updated packaged manuals", "Review and accept the unsigned-package wording as the content that will ship.", "In progress", "Critical", "Work now", "Required before package freeze", "TASK-092 / ADR-023", "2026-10-01", "ADR-023 changed files that are included in the ZIP.", "S: 0.25-0.5 day", "One approved set of package manuals.", "Documentation owner review.", "2026-10-02", "Documentation owner / release owner", "No conflicting wording remains and the owner accepts the shipped text.", "A later wording change creates new bytes and forces more reruns.", "Opening days: Oct 1-2", "High", ".agent_work/tasks/active/TASK-092-documentation-currentness.md"),
        action("R02", "Release package", "Choose the replacement control-package identity", "Name the new CPU and CUDA control ZIPs and bind them to accepted source, exact image digests, and the asset ZIP.", "Open", "Critical", "Work now", "Required before package build", "TASK-103 / W09", common_release_created, "The existing rc4 ZIPs contain older manuals.", "S: 0.25 day", "A unique, traceable candidate identity.", "R01; accepted main; confirmed image and asset identities.", "2026-10-02", "Release owner", "The release manifest and planned filenames agree on one new identity.", "Old and new evidence could be mixed or mislabeled.", "Opening days: Oct 1-2", "High", ".agent_work/tasks/active/TASK-103/W09-EVIDENCE-INDEX.md"),
        action("R03", "Release package", "Build replacement CPU and CUDA control ZIPs", "Repackage the accepted manuals without renaming or modifying an old ZIP.", "Blocked by R01-R02", "Critical", "Work now", "Required before testing", "TASK-103", common_release_created, "The package bytes changed after ADR-023.", "M: 0.5-1 day", "Two checksum-verifiable control ZIPs with current manuals.", "Clean source; exact identities; package tooling.", "2026-10-05", "Release implementer", "Both ZIPs and sidecars are produced from the clean accepted source.", "The current rc4 ZIPs cannot be final distribution artifacts.", "Week 1: Oct 5-9", "High", ".agent_work/tasks/active/TASK-103-cuda128-blackwell-ml-runtime.md"),
        action("R04", "Release package", "Inspect package integrity and secret hygiene", "Verify sidecars, internal checksums, manifests, allowlists, notices, scripts, and manuals; reject secrets and unexpected files.", "Open", "Critical", "Work now", "Required before tester distribution", "W09 / TASK-103", common_release_created, "The new ZIP identity has not been inspected.", "M: 0.5 day", "Auditable evidence that the ZIP contains exactly the intended files.", "R03.", "2026-10-06", "Release implementer / reviewer", "All package checks pass and sanitized evidence records the result.", "A malformed or sensitive package could be distributed.", "Week 1: Oct 5-9", "High", ".agent_work/context/status/Reprioritization Effort/2026-09-21-windows-deployment-hardening-v2.md"),
        action("R05", "Release package", "Repeat affected local package checks", "Run setup, start, status, logs, stop, fresh-shell relaunch, device, and volume checks for Docker/Podman CPU/GPU as affected by the new ZIPs.", "Open", "Critical", "Work now", "Required before freeze", "TASK-091 / TASK-103", common_release_created, "The previous local runtime evidence used rc4 package bytes.", "L: 1-2 days", "Local proof tied to the replacement ZIP hashes.", "R03-R04; Docker and Podman availability.", "2026-10-07", "Release implementer", "Affected W09/W10 cells reference the replacement ZIP hashes and pass.", "Untested replacement bytes could hide packaging regressions.", "Week 1: Oct 5-9", "Medium", ".agent_work/tasks/active/TASK-091-owner-runnable-release-qualification.md"),
        action("R06", "Release package", "Record authoritative SHA-256 values", "Put exact control and asset ZIP hashes in the owner-approved release record used by testers.", "Open / owner-controlled", "Critical", "Work now", "Required before extraction testing", "ADR-023 / W09", "2026-10-01", "The replacement ZIPs do not yet exist.", "S: 0.25 day", "One trusted place for testers to compare hashes.", "R03-R04; owner-approved publication or pre-release record.", "2026-10-08", "Release owner", "Displayed hashes match the exact tester downloads.", "A sidecar alone does not authenticate the publisher or download.", "Week 1: Oct 5-9", "High", ".agent_work/decisions/023-unsigned-windows-package-support-boundary.md"),
        action("R07", "Release acceptance", "Test a real browser download as an ordinary user", "Download the exact ZIP, verify its official hash before extraction, preserve the Windows download marker, extract to a path with spaces, and use the supplied wrapper.", "Blocked by R03 and R06", "Critical", "Work now", "Required before acceptance", "TASK-091 / TASK-103 / ADR-023", "2026-10-01", "This is the new acceptance proof created by the unsigned decision.", "M: 0.5-1 day", "Evidence that the supported unsigned path works without changing persistent policy.", "Download location; authoritative hash; ordinary account.", "2026-10-09", "Independent tester or separate ordinary-user session", "Hash, marker, extraction, wrapper, setup, and first-use results are recorded.", "The central unsigned-package support claim would remain unproven.", "Week 1: Oct 5-9", "Medium", ".agent_work/decisions/023-unsigned-windows-package-support-boundary.md"),
        action("R08", "Release acceptance", "Reserve the independent Windows tester and host", "Book the suitable computer, tester time, provider accounts, and runtime prerequisites before freeze.", "Blocked / external", "Critical", "Work immediately", "Required for full four-profile claim", "TASK-091 / W10", "2026-09-22", "No independent computer is confirmed in the current evidence.", "S: 0.25 day coordination", "A named tester, host inventory, and test window.", "Owner/tester availability; NVIDIA, Docker, Podman, Python 3.12, provider access.", "2026-10-02", "Test owner / project lead", "Anonymous host ID, capabilities, dates, and owners are recorded.", "Independent testing could consume the entire acceptance week or become impossible.", "Opening days: Oct 1-2", "Low", ".agent_work/tasks/active/TASK-091-owner-runnable-release-qualification.md"),
        action("R09", "Independent qualification", "Repeat Docker CPU on the independent host", "Follow only shipped instructions and run models, Google/Azure, review/export, cancel/error recovery, stop/relaunch, and persistence.", "Blocked by R03 and R08", "Critical", "Work after freeze", "Required for full acceptance", "TASK-091 / W10", "2026-09-21", "Only first-host evidence exists.", "M: 0.5-1 day", "Independent Docker CPU pass tied to exact hashes.", "Frozen package; assets; provider accounts; independent host.", "2026-10-13", "Independent tester", "Every required Docker CPU cell has a pass or an explicit blocker.", "The four-profile release claim remains incomplete.", "Week 2: Oct 12-16", "Medium", ".agent_work/context/status/Reprioritization Effort/2026-09-21-windows-deployment-prioritization-v2.md"),
        action("R10", "Independent qualification", "Repeat Docker GPU on the independent host", "Prove both models use CUDA with no CPU fallback, then repeat the user workflow and recovery checks.", "Blocked by R03 and R08", "Critical", "Work after freeze", "Required for full acceptance", "TASK-091 / TASK-103 / W10", "2026-09-21", "Only first-host CUDA evidence exists.", "M: 0.5-1 day", "Independent Docker GPU pass with actual CUDA evidence.", "Compatible NVIDIA host/driver/VRAM; frozen package.", "2026-10-14", "Independent tester", "Both models and a kernel run on CUDA and all workflow checks pass.", "A readiness label or CPU fallback could be mistaken for GPU support.", "Week 2: Oct 12-16", "Medium", ".agent_work/tasks/active/TASK-103/W10-LOCAL-FIRST-HOST-EVIDENCE-INDEX.md"),
        action("R11", "Independent qualification", "Repeat Podman CPU on the independent host", "Install/use the documented package-local Compose provider with supported Python, then run the full workflow.", "Blocked by R03 and R08", "Critical", "Work after freeze", "Required for full acceptance", "TASK-097 / W10", "2026-09-22", "Only first-host Podman evidence exists.", "M: 0.5-1 day", "Docker-Desktop-free independent Podman CPU proof.", "Podman machine/connection; Python 3.12; assets/providers.", "2026-10-14", "Independent tester", "Podman target binding, CPU models, providers, exports, and recovery pass.", "Podman support would remain a local-only result.", "Week 2: Oct 12-16", "Medium", ".agent_work/tasks/active/TASK-097-podman-final-path-qualification.md"),
        action("R12", "Independent qualification", "Repeat Podman GPU on the independent host", "Prove the intended WSL2/NVIDIA CDI path and both models on CUDA, then run the complete workflow.", "Blocked by R03 and R08", "Critical", "Work after freeze", "Required for full acceptance", "TASK-097 / TASK-103 / W10", "2026-09-22", "Only first-host Podman CUDA evidence exists.", "L: 0.75-1.25 days", "Independent Podman GPU proof with no Docker Desktop dependency.", "NVIDIA/CDI/Podman prerequisites; frozen package.", "2026-10-15", "Independent tester", "CDI, exact digest, CUDA models, providers, persistence, and exports pass.", "The highest-risk advertised profile would remain unverified.", "Week 2: Oct 12-16", "Low-Medium", ".agent_work/tasks/active/TASK-097-podman-final-path-qualification.md"),
        action("R13", "Independent qualification", "Repeat recovery, reboot, and shared failure cases", "Confirm eight volumes, provider/settings persistence, cancellation/error recovery, reboot behavior, wrong-target protection, and selected safe failure injections.", "Blocked by R09-R12", "Critical", "Work after profile runs", "Required for acceptance", "TASK-093 / W10", "2026-09-23", "Recovery has passed only on the first host.", "L: 0.75-1.5 days", "Independent evidence that normal failures do not lose data or target the wrong installation.", "Profile setup; permission to reboot; isolated test state.", "2026-10-16", "Independent tester / release implementer", "All required recovery cells pass without destructive volume cleanup.", "Data loss or a false recovery claim could reach end users.", "Week 2: Oct 12-16", "Medium", ".agent_work/tasks/active/TASK-093-persistent-data-recovery.md"),
        action("R14", "Release acceptance", "Perform the final evidence reconciliation", "Check every profile, host, hash, digest, device, provider, skip, limitation, and redaction before making the release claim.", "Open", "Critical", "Work after R09-R13", "Required for acceptance", "TASK-091 / TASK-103 / W10", "2026-09-21", "The final independent matrix does not yet exist.", "M: 0.5 day", "One accurate pass/fail/blocked matrix and evidence index.", "All test results and final artifact identities.", "2026-10-16", "Release owner / independent reviewer", "No missing or blocked cell is labeled pass; hashes and evidence references agree.", "The project could overstate readiness or lose traceability.", "Week 2: Oct 12-16", "High", ".agent_work/context/status/Reprioritization Effort/2026-09-21-windows-deployment-hardening-v2.md"),
        action("R15", "Release acceptance", "Make the acceptance or qualified-subset decision", "Approve the full four-profile candidate only if every required cell passes; otherwise name the exact supported subset and blockers.", "Open / owner decision", "Critical", "Decision gate", "October 16 milestone", "TASK-091 / project requirements", "2026-07-23 roadmap", "Independent acceptance has not finished.", "S: 1-2 hours", "A truthful, owner-approved acceptance result.", "R14; owner availability.", "2026-10-16", "Project lead and release owner", "Written sign-off identifies passes, limitations, residuals, and next actions.", "Publication could outrun evidence.", "Week 2: Oct 12-16", "High", ".agent_work/requirements.md"),

        action("D01", "Documentation", "Finalize shipped documentation for the exact candidate", "Insert final version, filenames, prerequisites, support limits, and tested behavior in Markdown and HTML before freeze.", "In progress", "High", "Work now", "Required before package freeze", "TASK-092", "2026-09-22", "The unsigned boundary is aligned, but final artifact-specific values do not yet exist.", "M: 0.5-1 day", "Shipped instructions match the exact package.", "R02; observed package behavior.", "2026-10-07", "Documentation owner", "Markdown/HTML pairs and package-local copies agree.", "Instructions could describe different bytes than testers receive.", "Week 1: Oct 5-9", "High", ".agent_work/tasks/active/TASK-092-documentation-currentness.md"),
        action("D02", "Documentation", "Verify in-app Help, links, and packaged guide copies", "Open the served Help pages, check navigation and repository links, and inspect the final ZIP/image for intended versions.", "Open", "High", "Work before freeze and acceptance", "Required before acceptance", "TASK-092 / post-Day-7 guide", "2026-09-21", "Text updates alone do not prove the app serves or packages them.", "M: 0.5 day", "Users reach working, current instructions from the app and package.", "D01; running frozen candidate.", "2026-10-09", "Documentation owner / tester", "All maintained pages render and links work in their supported context.", "Users may see stale or broken Help despite correct repository Markdown.", "Week 1: Oct 5-9", "High", ".agent_work/context/status/Reprioritization Effort/2026-09-21-post-day-7-backlog-and-handoff-guide.md"),
        action("D03", "Documentation", "Update the external Setup Guide", "Make the owner-held guide follow the exact accepted workflow and record its owner, storage location, editing access, and current link.", "Open / external", "High", "Work before publication", "Required before owner handoff", "TASK-092", "2026-07-23 roadmap", "The guide is outside the repository and final package details were not known.", "M: 0.5-1 day", "An owner-controlled external guide matching the candidate.", "Access to external document; final artifact values.", "2026-10-16", "Project lead / documentation owner", "The guide is reviewed against the frozen workflow and custody is recorded.", "A prominent external guide could lead users down an obsolete path.", "Week 2: Oct 12-16", "Medium", ".agent_work/requirements.md"),
        action("D04", "Documentation", "Prepare final release notes and download record", "Add exact URLs, hashes, prerequisites, tested profiles, unsigned support boundary, limitations, and rollback/support links.", "Open", "High", "Work before publication", "Required before publication", "TASK-092 / TASK-089", "2026-09-21", "Final URLs, hashes, and acceptance results are not yet available.", "M: 0.5 day", "A clear authoritative release record for users and maintainers.", "R06, R14-R15; final identity.", "2026-10-19", "Release owner / documentation owner", "Notes agree with final artifacts and never overclaim blocked cells.", "Users cannot safely identify or verify the intended downloads.", "Week 3: Oct 19-23", "High", ".agent_work/tasks/active/TASK-092-documentation-currentness.md"),
        action("D05", "Documentation", "Confirm the Podman Python prerequisite", "Verify the independent instructions clearly require a supported Python version and do not promise Python 3.14 compatibility.", "Open independent confirmation", "High", "Do with Podman tests", "Required for Podman support", "TASK-097", "2026-09-22", "Python 3.12 passed and 3.14 failed only on the first host.", "S: 0.25 day", "Accurate prerequisite wording backed by an independent run.", "R11-R12; suitable Python 3.12 installation.", "2026-10-15", "Podman tester / documentation owner", "The supported version works and the guide states the tested boundary.", "A new user could fail during provider installation.", "Week 2: Oct 12-16", "High", ".agent_work/tasks/active/TASK-103/W09-EVIDENCE-INDEX.md"),
        action("D06", "Documentation", "Verify administrator model-upload guidance", "Ensure the final owner/user materials explain the opt-in upload key, approved model hash, disabled-by-default behavior, rotation, and safe troubleshooting.", "Open verification", "High", "Work before handoff", "Required by DOC-001", "TASK-092 / requirements", "2026-07-23 requirements", "Current support contract text exists, but the public/owner documentation acceptance is not closed.", "M: 0.25-0.5 day", "Clear separation between normal user setup and restricted model administration.", "Final owner guide and public docs.", "2026-10-09", "Documentation owner / security reviewer", "All required controls are documented without a live secret.", "An owner could enable a sensitive feature without both controls.", "Week 1: Oct 5-9", "Medium", ".agent_work/requirements.md"),
        action("D07", "Installation video", "Write the video script and shot list", "Choose a permitted demo area, neutral desktop, recording location, primary profile, and short inserts for Podman/GPU differences.", "Open", "High", "Work now", "Required before video capture", "TASK-092 / post-Day-7 guide", "2026-09-21", "The recording must wait for the current workflow decision, but planning can start now.", "S: 0.25-0.5 day", "A privacy-safe plan for a 4-6 minute user video.", "Demo area/media permission; recording owner.", "2026-10-02", "Recorder / documentation owner", "Script identifies every screen, redaction pause, version statement, and owner-controlled destination.", "Late planning could expose credentials or force rushed recapture.", "Opening days: Oct 1-2", "High", ".agent_work/context/status/Reprioritization Effort/2026-09-21-post-day-7-backlog-and-handoff-guide.md"),
        action("D08", "Installation video", "Dry-run the video workflow", "Walk through the exact frozen-package steps without recording final footage; fix unclear instructions first.", "Blocked by frozen candidate", "High", "Work by freeze", "Required before final capture", "TASK-092", "2026-09-21", "The replacement package does not yet exist.", "S: 0.25-0.5 day", "A smooth, accurate recording path with no hidden setup.", "R03-R07; D07.", "2026-10-09", "Recorder / tester", "The full demonstrated path succeeds and matches the written guide.", "The final video could show unsupported or undocumented steps.", "Week 1: Oct 5-9", "Medium", ".agent_work/context/status/Reprioritization Effort/2026-09-21-post-day-7-backlog-and-handoff-guide.md"),
        action("D09", "Installation video", "Capture, edit, caption, and privacy-review the video", "Record the accepted package, add captions/transcript/chapters, and inspect every frame and audio segment for sensitive or misleading content.", "Blocked by acceptance candidate", "High", "Work after freeze", "Required before approved distribution", "TASK-092", "2026-09-21", "Final footage must use the inventoried candidate.", "L: 1-1.5 days", "A concise, accessible installation demonstration.", "Frozen candidate; recording/editing tools; privacy review.", "2026-10-16", "Recorder/editor / privacy reviewer", "The clip identifies version/profile, hides credential entry, and passes frame/audio review.", "A leaked key or outdated workflow could be published.", "Week 2: Oct 12-16", "Medium", ".agent_work/context/status/Reprioritization Effort/2026-09-21-post-day-7-backlog-and-handoff-guide.md"),
        action("D10", "Installation video", "Independent video comparison and custody transfer", "Have a tester repeat the demonstrated path, confirm audience access, and transfer video, transcript, editable project, and hosting permissions.", "Open", "High", "Work before owner rehearsal", "Required before handoff", "TASK-092 / TASK-095", "2026-09-21", "The final video and owner-controlled destination do not yet exist.", "M: 0.5 day", "A usable video that does not depend on the outgoing developer.", "D09; independent tester; owner-controlled hosting.", "2026-10-23", "Independent tester / receiving owner", "Tester succeeds and owner can access/edit/host all deliverables.", "The video may become inaccessible or impossible to maintain.", "Week 3: Oct 19-23", "Medium", ".agent_work/context/status/Reprioritization Effort/2026-09-21-post-day-7-backlog-and-handoff-guide.md"),

        action("H01", "Owner handoff", "Draft the owner operations guide", "Explain ownership, access, maintenance setup, release qualification, rollback, security, providers/assets/models, routine support, and backlog decisions in plain language.", "Open", "Critical", "Work in parallel now", "Required before rehearsal", "TASK-095 Phase B", "2026-07-23", "Phase B is still open and the exact candidate is only now stabilizing.", "L: 1-1.5 days", "A tool-neutral guide usable without this conversation or a specific AI product.", "Current tested procedures; owner role decisions.", "2026-10-09", "Maintainer / receiving owner reviewer", "Every chapter links maintained procedures and includes verification and rollback.", "Knowledge transfer would remain person-dependent.", "Opening days and Week 1", "Medium", ".agent_work/tasks/active/TASK-095-governance-ai-ready-handoff.md"),
        action("H02", "Owner handoff", "Document tool-neutral maintenance procedures", "Write how to plan, implement, test, release, roll back, and maintain TowerScout using repository-native steps.", "Open", "Critical", "Work before rehearsal", "Required by HANDOFF-001", "TASK-095 Phase B", "2026-07-23", "This was intentionally deferred to Phase B and final evidence.", "M: 0.5-1 day", "The owner can safely change and verify the project without Codex-specific knowledge.", "H01; final build/test procedures.", "2026-10-16", "Maintainer", "A new maintainer can prepare an environment and run a focused check from the guide.", "Future work could be blocked by missing process knowledge.", "Week 2: Oct 12-16", "Medium", ".agent_work/requirements.md"),
        action("H03", "Owner handoff", "Agree owner roles and maintenance cadence", "Name primary/backup roles and agree how often to review support, security, access, backups, storage, and qualification needs.", "Open / owner input", "High", "Work before owner review", "Required before handoff", "TASK-095", "2026-07-23", "Repository documents cannot assign real people or schedules by themselves.", "S: 0.25 day", "Clear responsibility and a realistic operating rhythm.", "Receiving owner and backup availability.", "2026-10-16", "Project lead / receiving owner", "Roles, escalation expectations, and accepted cadence are recorded without personal details in public files.", "Important work could have no accountable owner.", "Week 2: Oct 12-16", "Low-Medium", ".agent_work/context/status/Reprioritization Effort/2026-09-21-post-day-7-backlog-and-handoff-guide.md"),
        action("H04", "Owner handoff", "Verify access and custody", "Primary and backup demonstrate access to repositories, CI, packages, release tooling, assets, guides/video, test fixtures, and support records.", "Open / external", "Critical", "Work early", "Required before closeout", "TASK-095 / TASK-089", "2026-07-23", "Access cannot be proven by repository text and final destinations are not all selected.", "M: 0.5 day plus coordination", "No critical asset depends on the outgoing developer's personal account.", "Owner participation; account administrators.", "2026-10-09", "Project lead / receiving owner / backup", "Each role demonstrates its own access and missing permissions have named remediation owners.", "The project could end with inaccessible releases or support records.", "Opening days and Week 1", "Low-Medium", ".agent_work/tasks/active/TASK-095-governance-ai-ready-handoff.md"),
        action("H05", "Owner handoff", "Owner and backup review the guide", "Walk through the owner guide, record confusion and required assistance, and correct it before the formal rehearsal.", "Blocked by H01-H04", "Critical", "Work by acceptance", "Required before rehearsal", "TASK-095", "2026-09-21 guide", "The draft and confirmed access are not ready.", "M: 0.5 day", "An owner-reviewed guide and final rehearsal checklist.", "H01-H04; owner availability.", "2026-10-16", "Receiving owner and backup", "Review comments are resolved or listed as blockers.", "The formal rehearsal could discover basic gaps too late.", "Week 2: Oct 12-16", "Medium", ".agent_work/context/status/Reprioritization Effort/2026-09-21-post-day-7-backlog-and-handoff-guide.md"),
        action("H06", "Owner handoff", "Run the owner-operated release and recovery rehearsal", "The receiving owner performs package/release identification, support diagnosis, rollback/recovery, and evidence checks with minimal prompting.", "Blocked by acceptance and H05", "Critical", "Work in Week 3", "Required by October 23", "TASK-091 / TASK-095", "2026-07-23 roadmap", "The final candidate and owner guide are not accepted yet.", "L: 1 day", "Proof that ownership can continue after project end.", "Accepted candidate; owner/backup; isolated recovery target.", "2026-10-23", "Receiving owner; maintainer observes", "The owner completes critical procedures and all assistance/corrections are recorded.", "Operational dependence on the outgoing developer would remain.", "Week 3: Oct 19-23", "Medium", ".agent_work/requirements.md"),
        action("H07", "Backlog and governance", "Draft the owner-facing post-handoff backlog", "Turn open, conditional, and deferred work into one plain-language maintenance decision list with entry criteria and acceptance checks.", "Open", "High", "Work now", "Required before backlog review", "TASK-095", "2026-09-21 guide", "The current backlog is agent-oriented and the successor has not been created.", "M: 0.5-1 day", "A proposed owner-readable backlog without duplicating active authority.", "This workbook; current task dispositions.", "2026-10-05", "Project lead / maintainer", "Each carried item has impact, evidence, workaround, priority, effort, owner role, and last-reviewed date.", "The owner may need to reconstruct priorities from historical documents.", "Opening days and Week 1", "High", ".agent_work/context/status/Reprioritization Effort/2026-09-21-post-day-7-backlog-and-handoff-guide.md"),
        action("H08", "Backlog and governance", "Review 30/60/90-day priorities with the owner", "Agree which future items matter first without promising unallocated staff or time.", "Blocked by H07", "High", "Work before rehearsal close", "Required before backlog cutover", "TASK-095", "2026-09-21 guide", "Owner priorities and available capacity are not yet known.", "S: 0.25-0.5 day", "An owner-accepted near-term maintenance order.", "Receiving owner participation.", "2026-10-23", "Receiving owner / project lead", "The first maintenance review has agreed priorities and explicit deferrals.", "A technically complete backlog may still be unusable for real planning.", "Week 3: Oct 19-23", "Medium", ".agent_work/context/status/Reprioritization Effort/2026-09-21-post-day-7-backlog-and-handoff-guide.md"),
        action("H09", "Backlog and governance", "Cut over to one canonical maintenance backlog", "Update handoff and task entrypoints, archive or mark the outgoing board read-only, and preserve task-ID history.", "Blocked by H08", "Critical", "Work at closeout", "Required by October 30", "TASK-095", "2026-09-21 guide", "The project is still actively using the current board.", "M: 0.5 day", "One location the new owner updates after closeout.", "H08; final task dispositions.", "2026-10-30", "Project lead / maintainer", "All entrypoints point to the chosen backlog and old boards are clearly historical.", "Conflicting task authorities could confuse future maintainers or agents.", "Week 4: Oct 26-30", "High", ".agent_work/context/status/Reprioritization Effort/2026-09-21-post-day-7-backlog-and-handoff-guide.md"),
        action("H10", "Backlog and governance", "Record optional AI-assisted workflows", "Describe optional ways an owner may use AI while keeping every core procedure tool-neutral.", "Open", "Medium", "Work after core guide", "Required by TASK-095, not a release gate", "TASK-095", "2026-07-23", "Phase B has not completed.", "S: 0.25 day", "AI help is optional rather than a maintenance dependency.", "H02.", "2026-10-23", "Maintainer", "Guide clearly separates required repository processes from optional AI assistance.", "The handoff could accidentally require unavailable vendor tooling.", "Week 3: Oct 19-23", "High", ".agent_work/tasks/active/TASK-095-governance-ai-ready-handoff.md"),
        action("H11", "Backlog and governance", "Decide whether GitHub Issues supplement the backlog", "Choose one canonical destination and avoid two separately edited backlogs.", "Open / owner decision", "Medium", "Decide, do not overbuild", "Required before backlog transfer", "TASK-095 / TASK-089", "2026-07-23", "Issues availability and owner preference are unknown.", "S: 1-2 hours", "A documented backlog destination decision.", "Receiving owner; cdcai Issues availability.", "2026-10-23", "Receiving owner", "Decision and migration/cutover method are recorded.", "Duplicate lists could drift immediately after handoff.", "Week 3: Oct 19-23", "Medium", ".agent_work/tasks/active/TASK-095-governance-ai-ready-handoff.md"),
        action("H12", "Owner handoff", "Create the sanitized custody index", "List source, image/ZIP hashes, model/fixture provenance, evidence, guide/video versions, and storage locations without secrets.", "Open", "Critical", "Work before sign-off", "Required for closeout", "TASK-095 / W10", "2026-09-21 guide", "Final identities and external locations are not complete.", "M: 0.5 day", "A durable map of what exists and who holds it.", "R14; D03-D10; H04; sanitization results.", "2026-10-23", "Maintainer / receiving owner", "Every final deliverable and private-custody pointer is accounted for.", "Evidence or media could be lost after the outgoing developer leaves.", "Week 3: Oct 19-23", "Medium", ".agent_work/context/status/Reprioritization Effort/2026-09-21-post-day-7-backlog-and-handoff-guide.md"),
        action("H13", "Owner handoff", "Complete final operational sign-off", "Reconcile completed acceptance, known limitations, residual risks, open owner decisions, custody, access, and canonical backlog.", "Open", "Critical", "Work at closeout", "Hard closeout requirement", "TASK-095 / HANDOFF-002", "2026-07-23", "All other work feeds this final decision.", "M: 0.5 day", "No planned work depends on the outgoing developer after October 31.", "All critical actions; owner availability.", "2026-10-30", "Project lead and receiving owner", "Signed closeout states either completed adoption or the exact migration-ready fallback.", "Project responsibilities could remain ambiguous after the deadline.", "Week 4: Oct 26-30", "High", ".agent_work/requirements.md"),

        action("S01", "Sanitization", "Inventory the transfer scope and sensitive-material custody", "List paths and categories for source, branches, artifacts, fixtures, screenshots, logs, certificates, keys, environment files, media, and external assets without printing their contents.", "Open", "High", "Work now", "Required before transfer review", "TASK-095 / post-Day-7 guide", "2026-09-21", "The intended final transfer set was not previously fixed.", "M: 0.5 day", "A bounded scan scope and custody map.", "Owner-approved scope; access to relevant locations.", "2026-10-02", "Maintainer / security reviewer", "Every transfer surface is categorized as public, private, historical, or excluded.", "Later scanning may miss important artifacts or expose private data.", "Opening days: Oct 1-2", "Medium", ".agent_work/context/status/Reprioritization Effort/2026-09-21-post-day-7-backlog-and-handoff-guide.md"),
        action("S02", "Sanitization", "Run controlled redacting scans and remediate findings", "Scan an isolated transfer view, privately triage findings, replace private examples, fix allowlists/ignore rules, and arrange credential rotation if needed.", "Blocked by S01", "High", "Work before candidate review", "Required before transfer", "TASK-095", "2026-09-21", "No final transfer scope or approved method is recorded.", "L: 0.5-1 day; more if incident found", "No known unresolved sensitive exposure in the intended transfer set.", "Approved redacting tools; private findings process.", "2026-10-09", "Security reviewer / maintainer / credential owner", "All findings have a disposition and any real credential is rotated by its owner.", "Public release or handoff could expose keys, personal paths, or private evidence.", "Week 1: Oct 5-9", "Low-Medium", ".agent_work/context/status/Reprioritization Effort/2026-09-21-post-day-7-backlog-and-handoff-guide.md"),
        action("S03", "Sanitization", "Inspect the accepted candidate and media outputs", "Review final source, ZIPs, relevant image contents, reports, and video for inappropriate private content or missing notices.", "Blocked by candidate outputs", "High", "Work by acceptance", "Required before publication", "TASK-095", "2026-09-21", "Final candidate and media do not yet exist.", "M: 0.5 day", "A recorded candidate-level sanitization pass.", "R03; D09; S02.", "2026-10-16", "Security reviewer / release reviewer", "Reviewed artifacts, methods, exclusions, and dispositions are recorded.", "A clean source tree could hide problems in packaged or media outputs.", "Week 2: Oct 12-16", "Medium", ".agent_work/context/status/Reprioritization Effort/2026-09-21-post-day-7-backlog-and-handoff-guide.md"),
        action("S04", "Sanitization", "Run the final closeout delta review", "Check only changes since the candidate pass and verify the intended audience can access the sanitized destination material.", "Blocked by S03", "High", "Work at closeout", "Required by October 30", "TASK-095", "2026-09-21", "Closeout changes are not known yet.", "S: 0.25-0.5 day", "Final sanitization evidence for the actual transferred state.", "S03; final artifact/ownership state.", "2026-10-30", "Security reviewer / receiving owner", "No undisposed delta remains and destination access is verified.", "Late changes could bypass the earlier review.", "Week 4: Oct 26-30", "High", ".agent_work/context/status/Reprioritization Effort/2026-09-21-post-day-7-backlog-and-handoff-guide.md"),

        action("A01", "Adoption", "Review pilot feedback and final candidate findings", "Summarize actionable owner-held feedback and compare it with the qualified candidate without copying private feedback into the repo.", "Owner-gated / open", "High", "Schedule before adoption decision", "Required before cdcai adoption", "TASK-089", "2026-07-10", "The repository does not contain the external feedback review result.", "M: 0.25-0.5 day", "A documented candidate/adoption recommendation.", "Project lead; external feedback document; R15.", "2026-10-19", "Project lead / cdcai owner", "Feedback is reviewed and every blocker has an owner or disposition.", "The official repository could adopt a baseline that ignores user findings.", "Week 3: Oct 19-23", "Low-Medium", ".agent_work/tasks/active/TASK-089-cdcai-migration-execution.md"),
        action("A02", "Adoption", "Complete the migration-ready handoff packet", "Record candidate source, tags, image/package choices, hashes, evidence, backlog, namespace plan, and safe verification sequence without changing cdcai.", "Open preparation", "High", "Work regardless of adoption outcome", "Required for closeout fallback", "TASK-089", "2026-07-08", "Final candidate inputs and owner decisions are not known.", "M: 0.5-1 day", "A safe packet that can be executed later if adoption is delayed.", "R14-R15; D04; H12.", "2026-10-23", "Release owner / maintainer", "Packet contains exact current inputs and non-destructive steps.", "A delayed adoption would leave the new owner without an executable path.", "Week 3: Oct 19-23", "Medium", ".agent_work/tasks/active/TASK-089-cdcai-migration-execution.md"),
        action("A03", "Adoption", "Obtain the explicit adoption decision", "The project lead and cdcai owner approve a final baseline or decide to leave cdcai unchanged for now.", "Owner-gated", "Critical", "Decision gate", "Required before any cdcai mutation", "TASK-089", "2026-07-08", "Technical access is not authorization and qualification is unfinished.", "S: 1-2 hours", "A recorded go/no-go adoption decision.", "A01-A02; R15; owner availability.", "2026-10-23", "Project lead and cdcai owner", "Decision names the baseline and authorized actions, or explicitly selects the fallback.", "Unauthorized source, package, or release changes could occur.", "Week 3: Oct 19-23", "Low-Medium", ".agent_work/tasks/active/TASK-089-cdcai-migration-execution.md"),
        action("A04", "Adoption", "Select official tag, title, and namespace strategy", "Before an official build, choose the cdcai version/title and decide whether URLs/image defaults are rebuilt or explicitly carried forward.", "Blocked by A03", "High", "Do only if adoption approved", "Required before official build", "TASK-089", "2026-07-08", "Candidate naming does not reserve the official identity.", "S: 0.25 day", "One approved official identity and namespace plan.", "A03; cdcai owner decision.", "2026-10-23", "cdcai owner / project lead", "Tag, display title, release URLs, image paths, and disclosure strategy are written down.", "Packages and release records could disagree or silently change tag meaning.", "Week 3: Oct 19-23", "High", ".agent_work/requirements.md"),
        action("A05", "Adoption", "Confirm cdcai permissions and backlog destination", "Verify collaborator write, Actions, GHCR package ownership, release publication, and the approved durable backlog location.", "Owner-gated / open", "Critical", "Work early; mutate nothing", "Required before transfer", "TASK-089", "2026-07-08", "Execution-time permissions and Issues availability are unconfirmed.", "M: 0.25-0.5 day coordination", "A confirmed execution window with accountable owners.", "Account administrators; A03-A04 for execution.", "2026-10-23", "cdcai maintainer / project lead", "Primary and backup demonstrate required access and destination choices are recorded.", "The final week could be blocked by basic access gaps.", "Opening days through Week 3", "Low", ".agent_work/tasks/active/TASK-089-cdcai-migration-execution.md"),
        action("A06", "Adoption", "Build official cdcai images and packages", "Build from the approved tagged tree using the official identity; do not rename candidate ZIPs.", "Conditional on A03 approval", "High", "Do only if authorized", "Required for adopted release", "TASK-089", "2026-07-08", "Adoption and official identity are not approved.", "L: 0.5-1 day plus CI", "Official artifacts whose manifests, filenames, checksums, source refs, and docs agree.", "A03-A05; build/registry availability.", "2026-10-27", "Release owner / cdcai maintainer", "Official build completes with exact identity and required scans/checks.", "Renamed or inconsistently rebuilt artifacts would invalidate candidate evidence.", "Week 4: Oct 26-30", "Low-Medium", ".agent_work/tasks/active/TASK-089-cdcai-migration-execution.md"),
        action("A07", "Adoption", "Push approved history and tags safely", "Use the reviewed non-destructive sequence; no force push, squash of selected history, or bulk tag push.", "Conditional on A03 approval", "High", "Do only if authorized", "Required for adopted repository", "TASK-089", "2026-07-08", "The approved baseline/tag set is unknown.", "S: 0.25 day", "Traceable official source history without unintended tags.", "A03-A05; final tag list.", "2026-10-27", "cdcai maintainer", "Only approved refs are present and source provenance is verified.", "History or misleading historical tags could be published incorrectly.", "Week 4: Oct 26-30", "Medium", ".agent_work/tasks/active/TASK-089-cdcai-migration-execution.md"),
        action("A08", "Adoption", "Publish official images and release", "Publish the approved GHCR images and recreate the cdcai release from validated official artifacts.", "Conditional / owner-gated", "High", "Do only if authorized", "Required for adopted release", "TASK-089", "2026-07-08", "All qualification and adoption gates must pass first.", "M: 0.5 day plus propagation", "Owner-controlled official downloads and images.", "A06-A07; publication authorization.", "2026-10-28", "cdcai maintainer / release owner", "Visibility/linkage, assets, checksums, and release notes are correct.", "Users could receive incomplete or unverified official artifacts.", "Week 4: Oct 26-30", "Low-Medium", ".agent_work/tasks/active/TASK-089-cdcai-migration-execution.md"),
        action("A09", "Adoption", "Verify the transfer from a fresh consumer path", "Clone, pull, download, verify, and smoke the official package/source identities after transfer.", "Conditional on A08", "Critical", "Do after publication", "Required for adopted release", "TASK-089", "2026-07-08", "Official artifacts are not published.", "M: 0.5 day", "Evidence that the public official path works independently.", "A08; fresh test location; registry/release access.", "2026-10-29", "Independent tester / receiving owner", "Clone, image pull, ZIP verification, package smoke, and source-ref checks pass.", "A publication could look complete while downloads or provenance are broken.", "Week 4: Oct 26-30", "Medium", ".agent_work/tasks/active/TASK-089-cdcai-migration-execution.md"),
        action("A10", "Adoption", "Transfer the backlog to the approved destination", "Move or link the accepted maintenance backlog once, then stop independently editing the old board.", "Blocked by H11 and A05", "High", "Work at closeout", "Required before ownership transfer", "TASK-089 / TASK-095", "2026-07-08", "The durable destination has not been chosen.", "M: 0.25-0.5 day", "One owner-controlled backlog after project end.", "H08-H11; A05.", "2026-10-30", "Receiving owner / maintainer", "All carried items are present with working references and one canonical status location.", "Open work could be lost or split across duplicate systems.", "Week 4: Oct 26-30", "Medium", ".agent_work/tasks/active/TASK-089-cdcai-migration-execution.md"),
        action("A11", "Adoption", "Use the no-adoption fallback if approval is late", "Leave cdcai unchanged and deliver the qualified fork, evidence, feedback pointers, backlog, and migration-ready packet.", "Ready fallback", "Critical", "Use if A03 is not approved", "Required closeout alternative", "TASK-089", "2026-07-10", "Adoption is explicitly optional and owner-controlled.", "S: 0.25 day after A02", "A clean project closeout without unauthorized cdcai changes.", "A02; H12-H13.", "2026-10-30", "Project lead / receiving owner", "Closeout explicitly states the adoption blocker, owner, and next authorized action.", "The deadline could pressure the team into unauthorized publication.", "Week 4: Oct 26-30", "High", ".agent_work/context/status/Handoff-Planning/PILOT-FEEDBACK-AND-CDC-AI-ADOPTION-PLAN.md"),

        action("Q01", "Security and compliance", "Recheck final package/image scans, SBOM, notices, and licenses", "Confirm the exact final identities have the required scan/SBOM and compliance inventory; rerun image checks if an official rebuild changes digests.", "Open final-identity check", "High", "Work before publication", "Required for final identity", "TASK-103 / compliance requirements", "2026-09-24", "Existing evidence is tied to earlier image/package identities.", "M: 0.25-0.75 day", "Security/compliance evidence matches the actual released artifacts.", "Final digests/ZIPs; A06 if official rebuild occurs.", "2026-10-16 or after A06", "Release reviewer / compliance reviewer", "Every released digest/ZIP has its matching evidence and unresolved findings are dispositioned.", "Evidence could be incorrectly carried to changed bytes.", "Week 2 and conditional Week 4", "Medium", ".agent_work/tasks/active/TASK-103/NVIDIA-RUNTIME-COMPONENT-INVENTORY.md"),
        action("Q02", "Security and compliance", "Carry forward the remaining torch advisory and bridge exit triggers", "Keep the one residual advisory visible and explain when a future owner must leave or replace the CUDA 12.8 bridge.", "Open handoff note", "Medium", "Document for future owner", "Not a current release blocker if accepted", "TASK-103 / ADR-022", "2026-09-24", "The advisory has no current compatible replacement and must not disappear from handoff.", "S: 1-2 hours", "A transparent future upgrade trigger and security monitoring note.", "Owner guide/backlog.", "2026-10-23", "Security reviewer / maintainer", "Residual risk and exit triggers are present in the owner backlog/guide.", "A future owner may assume the dependency state is permanently accepted.", "Week 3: Oct 19-23", "High", ".agent_work/tasks/active/TASK-103/DEPENDENCY-SECURITY-DISPOSITION.md"),
        action("Q03", "Contingency", "Fix only acceptance blockers and rerun affected gates", "After freeze, make no optional changes. If a blocker is found, create a new identity and repeat only the checks affected by changed bytes.", "Reserved contingency", "Critical", "Use only when triggered", "Protects acceptance truth", "W09/W10 stop rule", "2026-09-21", "Independent testing may reveal real defects.", "Reserve 2-3 person-days", "A corrected candidate or an honest blocked result without scope creep.", "Observed blocker; owner decision; available buffer.", "2026-10-19 to 2026-10-21", "Release implementer / reviewer", "Every change has a new identity and affected evidence is rerun before acceptance.", "Late untracked fixes could invalidate all release evidence.", "Week 3 contingency", "Low", ".agent_work/context/status/Reprioritization Effort/2026-09-21-post-day-7-backlog-and-handoff-guide.md"),

        action("B01", "Conditional backlog", "TASK-076 provider key ownership and restriction guidance", "Clarify account ownership, key restrictions, billing/quota responsibility, rotation, and safe error guidance; change code only for observed ambiguity.", "Required guidance / not selected", "Medium", "Complete guidance during owner docs; defer code unless evidence requires it", "Conditional code; handoff guidance", "TASK-076", "Current backlog by 2026-09-24", "It was not needed for the bounded W00-W10 fixes and depends on owner/account decisions.", "S-M: 0.25-1 day", "Safe provider administration guidance.", "Owner/account input; observed errors for code work.", "2026-10-16 guidance; code future if needed", "Provider account owner / docs maintainer", "Owner guide covers restrictions/rotation and any reproduced ambiguity is resolved.", "Keys may be over-permissioned or support ownership unclear.", "Week 2 guidance only", "Medium", ".agent_work/task-backlog.md"),
        action("B02", "Conditional backlog", "TASK-077 manifest and asset-import hardening", "Select only if replacement-package testing shows an integrity, import, or recovery gap.", "Evidence-selected / not currently selected", "Medium", "Do not start unless triggered", "Conditional", "TASK-077", "Current backlog by 2026-09-24", "Current package evidence has not demonstrated a remaining gap.", "M-L: 1-3 days if triggered", "A bounded fix for a real artifact-integrity failure.", "Reproduced W09/W10 gap.", "Before acceptance if triggered; otherwise post-handoff", "Release implementer", "The reproduced gap has a focused test and replacement artifact evidence.", "Starting speculative hardening would consume closeout capacity.", "Contingency only", "Low", ".agent_work/task-backlog.md"),
        action("B03", "Conditional backlog", "TASK-027 enhanced error handling", "Fix only a reproduced user-facing release blocker that is not already owned by the current W02-W08 work.", "Conditional / not selected", "Medium", "Do not start unless triggered", "Conditional", "TASK-027", "Existing backlog; reconfirmed 2026-09-24", "No unowned blocking error is currently recorded.", "M-L: 1-3 days if triggered", "A clear error and recoverable user path for the specific failure.", "Reproduced blocker; acceptance test.", "Before acceptance if triggered; otherwise future", "Application maintainer", "The exact failure is tested and recovery works without broad framework changes.", "A broad error-system rewrite could displace acceptance work.", "Contingency only", "Low", ".agent_work/task-backlog.md"),
        action("B04", "Conditional backlog", "TASK-070 restricted-network enhancements", "Add offline/restricted distribution only if the owner explicitly claims that environment; keep normal managed-network support accurate.", "Conditional / not selected", "Low-Medium", "Defer unless required environment is claimed", "Conditional", "TASK-070", "Existing backlog; reconfirmed 2026-09-24", "The standard claim does not require fully offline installation.", "L-XL: 3-8 days", "A separately qualified restricted-network path.", "Owner scope decision; network/test environment; revised schedule.", "Post-handoff unless urgently required", "Future owner / runtime maintainer", "The new environment has explicit artifacts, instructions, and acceptance evidence.", "Selecting it now would threaten the fixed end date.", "Not scheduled", "Low", ".agent_work/task-backlog.md"),
        action("B05", "Conditional backlog", "TASK-094 sanitized support snapshot", "Add a small redacted support export only if real cases cannot be resolved with current status/log procedures.", "Evidence-gated / not selected", "Low-Medium", "Do not start unless support evidence demands it", "Conditional", "TASK-094", "2026-07-23 roadmap", "No unresolved support case demonstrates the need.", "M-L: 1-3 days", "A bounded support bundle with no keys or private data.", "Real support gap; privacy design/review.", "Post-handoff unless triggered before closeout", "Support maintainer / security reviewer", "A real case is solved and redaction tests pass.", "A speculative collector creates privacy and maintenance risk.", "Not scheduled", "Low", ".agent_work/task-backlog.md"),
        action("B06", "Conditional backlog", "TASK-026 CPU optimization", "Tune only after a measured bottleneck on the smallest supported host; preserve output and memory behavior.", "Conditional / not selected", "Low", "Defer unless measured regression blocks acceptance", "Conditional", "TASK-026", "Existing backlog; reconfirmed 2026-09-24", "No current supported-host performance blocker is recorded.", "L: 2-5 days", "Measured improvement without correctness regression.", "Repeatable measurement; protected qualification time.", "Post-handoff unless release blocker", "ML/runtime maintainer", "Benchmark, output parity, memory, and four-profile affected checks pass.", "Speculative optimization could destabilize the qualified ML runtime.", "Not scheduled", "Low", ".agent_work/task-backlog.md"),

        action("F01", "Deferred", "TASK-087 launcher and guided TLS control plane", "Preserve PR #64/#67 tags, commits, reviews, and evidence; do not resume or merge during this project closeout.", "Archived / deferred", "Low", "Do not work before October 31", "Not a release gate", "TASK-087", "2026-06-29", "The current command-based path passed the required first-host workflows and the redesign is explicitly deferred.", "XL: 4-7 days plus managed-network validation", "Future owner can reconsider from current main with preserved history.", "New owner scope and fresh branch.", "Post-handoff only", "Future owner", "History is preserved and the maintenance backlog states entry criteria.", "Resuming now would conflict with ADR-021 and consume acceptance/handoff time.", "Not scheduled", "High", ".agent_work/tasks/active/TASK-087-host-side-tls-repair-control-plane.md"),
        action("F02", "Deferred", "TASK-096 browser Exit/helper", "Continue using the tested command-based stop/start workflow; leave browser Exit redesign for a future owner.", "Deferred", "Low", "Do not work before October 31", "Not a release gate", "TASK-096", "2026-07-23 roadmap", "The existing lifecycle now satisfies the current supported outcome.", "L: multi-day feature", "Future optional convenience feature with its own safety review.", "New owner decision; TASK-087 design questions.", "Post-handoff only", "Future owner", "Deferred rationale and current safe commands are documented.", "A late host-control UI could introduce security and lifecycle defects.", "Not scheduled", "High", ".agent_work/task-backlog.md"),
        action("F03", "Deferred", "TASK-058 background detection jobs", "Do not start the job-queue/state-machine redesign; retain only the bounded admission/cancellation fixes already accepted.", "Deferred architecture", "Low", "Do not work before October 31", "Not a release gate", "TASK-058", "Existing pre-July backlog", "The synchronous path is qualified and closeout work has higher priority.", "XL: >5 days", "Future durable job architecture if owner selects it.", "Separate design, migration, recovery, and UI scope.", "Post-handoff only", "Future application owner", "Owner selects a new scoped task with tests and rollback plan.", "Large architecture work would threaten project completion.", "Not scheduled", "High", ".agent_work/task-backlog.md"),
        action("F04", "Deferred", "TASK-059 backend decomposition", "Do not restructure backend layers during release closeout.", "Deferred architecture", "Low", "Do not work before October 31", "Not a release gate", "TASK-059", "Existing pre-July backlog", "No current acceptance blocker requires the refactor.", "XL: >5 days", "Future maintainability improvement after release stability.", "Owner priority; preferably after TASK-058 decision.", "Post-handoff only", "Future application owner", "A separately approved plan protects APIs, data, and regression coverage.", "Refactoring now creates broad regression risk.", "Not scheduled", "High", ".agent_work/task-backlog.md"),
        action("F05", "Deferred", "TASK-060 frontend build modernization", "Keep the current maintained build because it is not blocking acceptance.", "Deferred maintenance", "Low", "Do not work before October 31", "Not a release gate", "TASK-060", "Existing backlog", "The current bundle build and parity checks pass.", "L-XL: 3-8 days", "A future modern build pipeline with migration evidence.", "Owner selection; frontend compatibility plan.", "Post-handoff only", "Future frontend owner", "New pipeline preserves generated bundle behavior and support docs.", "Build-system churn could invalidate the tested candidate.", "Not scheduled", "High", ".agent_work/task-backlog.md"),
        action("F06", "Deferred", "TASK-061 coordinated NumPy 2 migration", "Do not add a dependency migration to the current qualified ML/runtime line.", "Deferred dependency track", "Low", "Do not work before October 31", "Not a release gate", "TASK-061", "Existing backlog", "The current dependency set is qualified and no blocker requires this change.", "L-XL: 3-8 days", "Future coordinated compatibility migration.", "Dependency compatibility and full CPU/CUDA requalification.", "Post-handoff only", "Future runtime owner", "All dependent packages and runtime profiles pass together.", "A late dependency migration could break models or geospatial behavior.", "Not scheduled", "High", ".agent_work/task-backlog.md"),
        action("F07", "Deferred", "TASK-078 Apache-only runtime migration", "Retain the current compliant runtime and notices; treat a permissive-only migration as a future release track.", "Deferred release track", "Low", "Do not work before October 31", "Not a release gate", "TASK-078", "Existing backlog", "It is not required for the current owner-approved release boundary.", "XL: >5 days", "A separately designed replacement runtime if future ownership requires it.", "Legal/compliance/product decisions and model requalification.", "Post-handoff only", "Future owner / compliance reviewer", "A new track has approved requirements and equivalent model results.", "Attempting it now would create major scope and model risk.", "Not scheduled", "High", ".agent_work/task-backlog.md"),
        action("F08", "Deferred", "TASK-029 multi-provider fallback", "Keep explicit Google/Azure selection and current error guidance; do not add automatic fallback during closeout.", "Deferred product work", "Low", "Do not work before October 31", "Not a release gate", "TASK-029", "Existing backlog", "Provider policy/error behavior must stay stable through release.", "L: 3-5 days", "Future explicit fallback behavior with billing and state rules.", "Product policy; provider state design; user consent.", "Post-handoff only", "Future product owner", "Fallback cannot leak keys, surprise billing, or corrupt selection state.", "Late fallback work would broaden provider/race risk.", "Not scheduled", "High", ".agent_work/task-backlog.md"),
        action("F09", "Deferred", "TASK-028 mobile responsiveness", "Keep the supported Windows desktop/browser boundary; treat mobile layout as parking-lot work.", "Deferred / parking lot", "Low", "Do not work before October 31", "Not a release gate", "TASK-028", "Existing backlog", "Mobile is outside the current product boundary.", "L: 2-5 days", "Future mobile usability improvements if scope changes.", "Product support decision; device/browser testing.", "Post-handoff only", "Future product owner", "A new support claim is explicitly defined and tested.", "It would spend closeout time on an unsupported platform.", "Not scheduled", "High", ".agent_work/task-backlog.md"),
    ]
    return rows


def metadata_block(lines: list[str], label: str) -> str:
    marker = f"**{label}**:"
    for index, line in enumerate(lines):
        if line.startswith(marker):
            parts = [line[len(marker):].strip()]
            for following in lines[index + 1 :]:
                if not following.strip() or following.startswith("**") or following.startswith("#"):
                    break
                if following.startswith(" ") or not following.startswith(("-", "|")):
                    parts.append(following.strip())
                else:
                    break
            return " ".join(part for part in parts if part)
    return ""


CURRENT_DISPOSITIONS = {
    "068": "Completed current-sprint record; move at sprint closeout",
    "087": "Archived / deferred; no October implementation",
    "089": "Blocked / owner-gated preparation and possible adoption",
    "091": "At risk; replacement package, browser download, and independent host remain",
    "092": "In progress; final artifact/external documentation remains",
    "093": "In progress; independent-host recovery remains",
    "095": "In progress; Phase B governance/handoff remains",
    "097": "At risk; independent Podman proof remains",
    "099": "Completed current-sprint record; move at sprint closeout",
    "101": "Completed; unchecked PR #67 items are superseded, not open",
    "103": "In progress; replacement package/browser/independent host remain",
}


BACKLOG_ONLY = {
    "026": ("CPU Optimization", "Conditional"),
    "027": ("Enhanced Error Handling", "Conditional"),
    "028": ("Mobile Responsiveness", "Deferred / parking lot"),
    "029": ("Multi-Provider Fallback", "Deferred"),
    "058": ("Background Detection Jobs", "Deferred"),
    "059": ("Backend Layer Decomposition", "Deferred"),
    "060": ("Frontend Build Modernization", "Deferred"),
    "061": ("Coordinated NumPy 2 Migration", "Deferred"),
    "070": ("Restricted-Network Package Enhancements", "Conditional"),
    "076": ("Provider API Key Exposure And Restriction Policy", "Required guidance / conditional code"),
    "077": ("Public Release Manifest And Asset Import Hardening", "Evidence-selected"),
    "078": ("Permissive Apache-Only Runtime Migration", "Deferred"),
    "094": ("Evidence-Gated Support Snapshot", "Evidence-gated"),
    "096": ("User-Initiated Exit And Container Stop", "Deferred"),
}


def build_task_registry() -> list[list[object]]:
    grouped: dict[str, list[Path]] = defaultdict(list)
    task_re = re.compile(r"TASK-(\d{3})", re.IGNORECASE)
    for base in (AGENT_WORK / "tasks" / "active", AGENT_WORK / "tasks" / "completed"):
        for path in sorted(base.glob("TASK-*.md")):
            match = task_re.search(path.name)
            if match:
                grouped[match.group(1)].append(path)

    rows: list[list[object]] = []
    for task_id in sorted(set(grouped) | set(BACKLOG_ONLY), key=int):
        paths = grouped.get(task_id, [])
        title = BACKLOG_ONLY.get(task_id, ("", ""))[0]
        file_statuses = []
        created = ""
        effort = ""
        unchecked = 0
        locations = []
        for path in paths:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
            locations.append(path.relative_to(ROOT).as_posix())
            heading = next((line for line in lines if re.match(r"^# TASK-\d{3}:", line)), "")
            if heading and not title:
                title = heading.split(":", 1)[1].strip()
            status = metadata_block(lines, "Status")
            if status:
                file_statuses.append(status)
            created = created or metadata_block(lines, "Created")
            effort = effort or metadata_block(lines, "Estimated Effort")
            unchecked += sum(1 for line in lines if re.match(r"^- \[ \]", line))

        if task_id in CURRENT_DISPOSITIONS:
            current = CURRENT_DISPOSITIONS[task_id]
            authority = "Current board"
            included = "Yes" if task_id in {"089", "091", "092", "093", "095", "097", "103"} else "No"
        elif task_id in BACKLOG_ONLY:
            current = BACKLOG_ONLY[task_id][1]
            authority = "Current backlog"
            included = "Yes"
        else:
            current = "Historical / completed; not current work unless reselected"
            authority = "Completed-task history"
            included = "No"
        interpretation = (
            "Current open work is represented in the curated Open Actions sheet."
            if included == "Yes"
            else "Unchecked boxes or old status text are historical residue and do not reopen the task."
        )
        rows.append(
            [
                f"TASK-{task_id}",
                title or "Title not recovered from top-level task file",
                current,
                authority,
                " | ".join(file_statuses) if file_statuses else "No top-level task status",
                created or "Not recorded in current task metadata",
                effort or "Not estimated in current task metadata",
                unchecked,
                included,
                interpretation,
                "\n".join(locations) if locations else ".agent_work/task-backlog.md",
            ]
        )
    return rows


def iter_unchecked_items(path: Path) -> Iterable[tuple[int, str, str]]:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    heading = ""
    index = 0
    while index < len(lines):
        line = lines[index]
        if line.startswith("#"):
            heading = line.lstrip("#").strip()
        match = re.match(r"^- \[ \]\s*(.*)", line)
        if not match:
            index += 1
            continue
        parts = [match.group(1).strip()]
        cursor = index + 1
        while cursor < len(lines):
            follow = lines[cursor]
            if not follow.strip():
                break
            if re.match(r"^(?:#{1,6}\s|[-*+]\s|\d+\.\s)", follow):
                break
            if follow.startswith(" "):
                parts.append(follow.strip())
                cursor += 1
                continue
            break
        yield index + 1, heading, " ".join(parts)
        index = max(cursor, index + 1)


def source_authority(path: Path) -> tuple[str, str, str]:
    rel = path.relative_to(ROOT).as_posix()
    if "/tasks/completed/" in "/" + rel:
        return "Historical task", "No", "Historical checklist residue; do not reopen without owner reselection."
    if "TASK-101-" in path.name:
        return "Completed / superseded", "No", "PR #67 integration boxes were superseded by ADR-021."
    if "TASK-099-" in path.name or "TASK-068-" in path.name:
        return "Completed current-sprint record", "No", "Completed; retain until sprint closeout."
    if "/tasks/active/" in "/" + rel:
        return "Current task detail", "Yes", "Reconcile with the curated Open Actions sheet and current board."
    if path.name == "2026-07-23-OCTOBER-FIX-FIRST-IMPLEMENTATION-ROADMAP.md":
        return "Historical roadmap", "No", "Immediate PR #67/Task-087 sequence is superseded; milestones remain context."
    if path.name == "2026-09-21-windows-deployment-hardening-v2.md":
        return "Current controlling work plan", "Partial", "Use the W00-W10 Crosswalk; unchecked plan boxes were not maintained as a live tracker."
    if path.name == "2026-09-21-post-day-7-backlog-and-handoff-guide.md":
        return "Current suggested closeout guide", "Yes", "Mapped into release, documentation, sanitization, backlog, and handoff actions."
    return "Supporting or historical status", "No", "Consult current board and source precedence before treating as work."


def build_raw_unchecked() -> list[list[object]]:
    paths: list[Path] = []
    paths.extend((AGENT_WORK / "tasks").rglob("*.md"))
    for folder in (
        AGENT_WORK / "context" / "status" / "Handoff-Planning",
        AGENT_WORK / "context" / "status" / "Reprioritization Effort",
    ):
        paths.extend(folder.rglob("*.md"))
    rows: list[list[object]] = []
    for path in sorted(set(paths)):
        authority, included, guidance = source_authority(path)
        for line_number, heading, item in iter_unchecked_items(path):
            rows.append(
                [
                    path.relative_to(ROOT).as_posix(),
                    line_number,
                    heading,
                    item,
                    authority,
                    included,
                    guidance,
                ]
            )
    return rows


def build_source_register() -> list[list[object]]:
    paths: list[Path] = []
    paths.extend((AGENT_WORK / "tasks").rglob("*.md"))
    for folder in (
        AGENT_WORK / "context" / "status" / "Handoff-Planning",
        AGENT_WORK / "context" / "status" / "Reprioritization Effort",
    ):
        paths.extend(folder.rglob("*.md"))
    rows: list[list[object]] = []
    for path in sorted(set(paths)):
        rel = path.relative_to(ROOT).as_posix()
        content = path.read_text(encoding="utf-8", errors="replace")
        authority, _, guidance = source_authority(path)
        if "/tasks/active/" in "/" + rel and path.parent.name == "active":
            method = "Full read for current task or structured current-status review"
        elif "/tasks/active/TASK-103/" in "/" + rel:
            method = "Structured evidence/status scan; current open gates reconciled"
        elif "/tasks/completed/" in "/" + rel:
            method = "Structured metadata and unchecked-checklist scan; historical body not treated as current authority"
        elif "Reprioritization Effort" in rel or "Handoff-Planning" in rel:
            method = "Full read for controlling/current guides; structured scan for historical evidence files"
        else:
            method = "Structured documentation scan"
        rows.append(
            [
                rel,
                authority,
                len(content.splitlines()),
                len(content.encode("utf-8")),
                method,
                guidance,
            ]
        )
    return rows


def build_w_crosswalk() -> list[list[object]]:
    return [
        ["W00", "Direction and agent entrypoints", "Complete", "ADR-021/022/023, board, agent instructions, skills, and current direction are aligned.", "Keep aligned through closeout; final entrypoint check is part of H09/H13.", "Not a current implementation blocker."],
        ["W01", "Baseline package and feasibility", "Complete for first host; independent resources still open", "Real package attempts, host/runtime inventory, assets, accounts, and at-risk forecast were recorded.", "Reserve and inventory the independent host/tester (R08).", "External host availability remains critical."],
        ["W02", "Dormant helper dependency", "Complete", "Task-068 merged and final rc4 package lifecycle passed on the first host.", "Preserve completed evidence; no new Task-087 work.", "Move the completed task at sprint closeout."],
        ["W03", "Bound processes and target Podman", "Complete for first host", "Bounded commands, explicit rootless target, and package-local provider passed.", "Repeat target behavior on the independent host under R11-R12.", "Independent proof remains."],
        ["W04", "Transactional TLS repair", "Complete for first host", "Docker and Podman provider TLS repair passed dry-run/apply/relaunch and persistence.", "Repeat applicable managed-network steps during independent testing.", "Do not broaden into deferred launcher work."],
        ["W05", "Combined model qualification", "Complete for current local images", "Exact CPU/CUDA digests passed real YOLO and EfficientNet device/output gates.", "Reference the same model/device contract during independent W10 runs.", "No threshold or output relaxation."],
        ["W06", "Model failure and allocation limits", "Complete", "Bounded code changes merged and local/runtime evidence passed.", "Only reopen for a reproduced final-candidate blocker.", "Use contingency Q03 if triggered."],
        ["W07", "Rate limits, admission, recovery", "Complete for first host", "Cancellation readiness, next-request success, and controlled error recovery passed in all local profiles.", "Repeat on the independent host under R09-R13.", "Broad job-queue redesign remains deferred."],
        ["W08", "Google first-use bounds and bundle", "Complete", "Fix merged; live Google/Azure paths passed locally.", "Repeat live provider workflows on the independent host.", "No additional provider redesign planned."],
        ["W09", "Freeze and verify exact downloads", "Incomplete after ADR-023 docs change", "Images and rc4 local evidence are valid, but rc4 control ZIPs contain older manuals.", "R01-R07: new ZIP identity, integrity checks, local reruns, official hashes, browser-download proof.", "Must finish before tester distribution/freeze."],
        ["W10", "Independent reproduction and handoff", "Incomplete / blocked on independent host", "Complete first-host four-profile provider/recovery/reboot matrix exists.", "R08-R15 plus documentation, handoff, and evidence reconciliation.", "Full release claim is blocked until independent cells pass."],
    ]


def overview_rows(action_rows: list[list[object]], raw_rows: list[list[object]], source_rows: list[list[object]]) -> list[list[object]]:
    recommendations = Counter(str(row[6]) for row in action_rows)
    gates = sum(1 for row in action_rows if "Required" in str(row[7]) or "gate" in str(row[7]).lower())
    return [
        ["Purpose", "Deliverable", "Comprehensive inventory of currently open, conditional, owner-gated, and deliberately deferred work through project closeout."],
        ["Scope", "Documents reviewed", "All Markdown under .agent_work/tasks plus Handoff-Planning and Reprioritization Effort status folders; current board/backlog/requirements/design control interpretation."],
        ["As of", "Review date", AS_OF.isoformat()],
        ["Decision", "Unsigned package", "ADR-023 is accepted. Signing is not a standard release gate; browser-download/hash/ordinary-user proof remains."],
        ["Important", "rc4 package status", "rc4 remains valid historical local runtime evidence but is not the final distribution package because shipped manuals changed."],
        ["Count", "Curated action rows", len(action_rows)],
        ["Count", "Rows identified as release/handoff gates", gates],
        ["Count", "Raw unchecked checklist items retained for traceability", len(raw_rows)],
        ["Count", "Documentation sources registered", len(source_rows)],
        ["How to use", "Open Actions", "Filter Recommendation, Priority, Planned week, or Task/source. This is the decision-ready backlog."],
        ["How to use", "Raw Unchecked Items", "This sheet prevents old unchecked boxes from disappearing. Many are historical and must not be treated as active work."],
        ["Interpretation", "Completed-folder files", "Historical task bodies may contain stale IN_PROGRESS labels or unchecked test plans. Current board/backlog authority wins."],
        ["Recommendation count", "Work now", sum(1 for key, count in recommendations.items() if "Work now" in key or "immediately" in key.lower())],
        ["Recommendation count", "Deferred / not scheduled", sum(1 for row in action_rows if "Do not work" in str(row[6]) or str(row[18]) == "Not scheduled")],
        ["Authorization", "External actions", "Publication, cdcai mutation, account changes, and signing remain owner-controlled even when listed as plan steps."],
    ]


def make_backlog_workbook() -> Path:
    actions = build_open_actions()
    registry = build_task_registry()
    raw = build_raw_unchecked()
    sources = build_source_register()
    sheets = [
        {
            "name": "Read Me",
            "title": "TowerScout Comprehensive Backlog and Next Steps",
            "description": "As of October 1, 2026. The current board and ADRs control status; historical unchecked boxes are retained separately and do not automatically reopen completed work.",
            "headers": ["Category", "Topic", "Explanation"],
            "rows": overview_rows(actions, raw, sources),
            "widths": [22, 30, 110],
            "freeze_cols": 1,
            "table_name": "BacklogReadMe",
        },
        {
            "name": "Open Actions",
            "title": "Comprehensive Open Actions",
            "description": "Curated current, conditional, owner-gated, and deferred work. Filter by recommendation and planned week; deferred rows are documented so they are not accidentally pulled into October.",
            "headers": ACTION_HEADERS,
            "rows": actions,
            "widths": [11, 20, 38, 55, 23, 13, 30, 28, 25, 20, 45, 20, 42, 42, 16, 25, 48, 42, 24, 18, 70],
            "freeze_cols": 3,
            "table_name": "OpenActions",
        },
        {
            "name": "W00-W10 Crosswalk",
            "title": "W00-W10 Current Status Crosswalk",
            "description": "The original implementation-plan checkboxes were not maintained as a live tracker. This crosswalk applies current task/evidence status after ADR-022 and ADR-023.",
            "headers": ["Work package", "Purpose", "Current status", "Verified completed evidence", "Still required", "Planning note"],
            "rows": build_w_crosswalk(),
            "widths": [14, 32, 30, 65, 65, 45],
            "freeze_cols": 2,
            "table_name": "WCrosswalk",
        },
        {
            "name": "Task Registry",
            "title": "Task Documentation Registry",
            "description": "One row per task ID found in top-level task files or the current backlog. Current disposition overrides stale status text inside historical completed files.",
            "headers": ["Task ID", "Title", "Current disposition", "Authority", "Status text found in task files", "Created", "Estimated effort", "Unchecked boxes", "Included in Open Actions", "Interpretation", "Top-level source files"],
            "rows": registry,
            "widths": [12, 42, 45, 24, 65, 20, 28, 16, 20, 55, 80],
            "freeze_cols": 2,
            "table_name": "TaskRegistry",
        },
        {
            "name": "Raw Unchecked Items",
            "title": "Raw Unchecked Checklist Items",
            "description": "Traceability inventory across all requested task and status documentation. Use Authority and Included in Open Actions before treating any row as current work.",
            "headers": ["Source file", "Line", "Nearest heading", "Unchecked item", "Authority / lifecycle", "Included in curated backlog", "Disposition guidance"],
            "rows": raw,
            "widths": [80, 10, 45, 100, 32, 20, 65],
            "freeze_cols": 1,
            "table_name": "RawUnchecked",
        },
        {
            "name": "Source Register",
            "title": "Reviewed Documentation Source Register",
            "description": "Inventory of Markdown documentation under .agent_work/tasks and the requested Handoff-Planning and Reprioritization Effort folders.",
            "headers": ["Path", "Authority / lifecycle", "Lines", "Bytes", "Review method", "Interpretation guidance"],
            "rows": sources,
            "widths": [95, 34, 12, 14, 65, 70],
            "freeze_cols": 1,
            "table_name": "SourceRegister",
        },
    ]
    path = OUTPUT_DIR / "TowerScout-Comprehensive-Backlog-and-Next-Steps-2026-10-01.xlsx"
    write_workbook(path, sheets, "TowerScout Comprehensive Backlog and Next Steps")
    return path


def plan_row(
    plan_id: str,
    week: str,
    dates: str,
    priority: str,
    activity: str,
    simple_explanation: str,
    why_now: str,
    effort: str,
    owner: str,
    dependency: str,
    deliverable: str,
    done_when: str,
    deadline: str,
    status: str,
    source_ids: str,
) -> list[object]:
    return [plan_id, week, dates, priority, activity, simple_explanation, why_now, effort, owner, dependency, deliverable, done_when, deadline, status, source_ids]


PLAN_HEADERS = [
    "Plan ID",
    "Week",
    "Dates",
    "Priority",
    "Activity",
    "Simple explanation",
    "Why this happens now",
    "Estimated person-days",
    "Owner / participants",
    "Depends on",
    "Expected deliverable",
    "Done when",
    "Must finish by",
    "Starting status",
    "Backlog action IDs",
]


def build_weekly_plan() -> list[list[object]]:
    return [
        plan_row("P01", "Opening days", "Oct 1-2", "Critical", "Accept the unsigned-package manuals", "Finish the wording that tells users the package is unsigned, how to verify it, and what computers are outside support.", "The manuals are package files; every later package test depends on them.", "0.5", "Documentation owner; release owner", "ADR-023 decision", "Approved package text", "Owner accepts the text and conflict scan is clean.", "Oct 2", "In progress", "R01,D01"),
        plan_row("P02", "Opening days", "Oct 1-2", "Critical", "Book the independent test and owner sessions", "Reserve the independent Windows computer, tester, provider access, owner review, and rehearsal times now.", "People and suitable hardware are the largest schedule risk.", "0.25", "Project lead; test owner; receiving owner", "Owner calendars and host availability", "Named dates, roles, and host capability inventory", "Every external session has an owner and date.", "Oct 2", "Blocked / external", "R08,H03,H04"),
        plan_row("P03", "Opening days", "Oct 1-2", "High", "Start the owner guide and final backlog", "Draft plain-language maintenance instructions and use the comprehensive backlog as the source for the owner-facing version.", "These can be prepared while package work is underway and should not be left until the last week.", "1.0", "Maintainer; project lead", "Current procedures and this inventory", "Owner-guide outline and proposed post-handoff backlog", "All required chapters and every carried item have an owner/due date placeholder.", "Oct 5", "Open", "H01,H07"),
        plan_row("P04", "Opening days", "Oct 1-2", "High", "Plan the video and sanitization review", "Write the shot list and define exactly what source, packages, evidence, and media will be checked for private information.", "Good preparation prevents rushed recordings and unsafe broad scans.", "0.75", "Recorder; security reviewer", "Permitted demo area and transfer scope", "Video storyboard and sanitization inventory", "Recording/privacy choices and transfer categories are written down.", "Oct 2", "Open", "D07,S01"),

        plan_row("P05", "Week 1", "Oct 5-6", "Critical", "Build and inspect the replacement packages", "Give the package a new name, build new CPU/CUDA ZIPs, and verify every checksum, manifest, notice, script, guide, and exclusion.", "The old ZIPs contain older manuals and cannot be final downloads.", "1.5", "Release implementer; reviewer", "P01; accepted source/images/assets", "Two verified replacement control ZIPs", "Sidecars/internal checks/manifests/allowlists and secret hygiene pass.", "Oct 6", "Blocked by approved docs", "R02,R03,R04"),
        plan_row("P06", "Week 1", "Oct 6-8", "Critical", "Repeat local package checks", "Use the replacement ZIPs across Docker/Podman CPU/GPU and confirm setup, devices, volumes, stop, and relaunch still work.", "A documentation-only ZIP change still creates different distributed bytes.", "1.5", "Release implementer", "P05; Docker and Podman available", "Replacement-package W09 evidence", "Affected cells cite the new hashes and pass.", "Oct 8", "Open", "R05"),
        plan_row("P07", "Week 1", "Oct 7-9", "Critical", "Publish hashes and perform the real browser-download test", "Put the exact hashes in the trusted release record, download through a browser, verify before extraction, and run as an ordinary user.", "This is the main proof required by the unsigned-package decision.", "0.75", "Release owner; ordinary-user tester", "P05; owner-approved record", "Hash/MOTW/wrapper evidence", "The exact browser download works without changing persistent policy.", "Oct 9", "Blocked by package identity", "R06,R07"),
        plan_row("P08", "Week 1", "Oct 5-9", "High", "Finish shipped docs, owner guide v1, and video dry-run", "Check Markdown, HTML, Help pages, package copies, Podman Python wording, admin model guidance, and the planned video path.", "All shipped instructions must freeze with the candidate.", "1.5", "Documentation owner; owner-guide reviewer; recorder", "P05-P06", "Frozen guides, owner guide v1, successful video dry-run", "The ZIP and running app show the intended guide versions and working links.", "Oct 9", "In progress", "D01,D02,D05,D06,D08,H01"),
        plan_row("P09", "Week 1", "Oct 5-9", "High", "Resolve early sanitization and access gaps", "Use controlled redacting methods, fix real findings, and confirm repository/package/media access for primary and backup owners.", "Late discovery of a credential or access gap could block closeout.", "1.0", "Security reviewer; owner; account admins", "P04", "Finding dispositions and access matrix", "No unresolved high-risk finding or unnamed access owner remains.", "Oct 9", "Open", "S02,H04,A05"),
        plan_row("M1", "Milestone", "Oct 9", "Critical", "Freeze the final candidate", "Stop changing shipped code and package documents except for a true release blocker.", "Independent acceptance needs stable bytes.", "0.0", "Release owner", "P05-P09", "Frozen source, images, ZIPs, assets, tools, fixtures, and guides", "Every identity/hash is recorded and exact tester downloads are available.", "Oct 9", "Open milestone", "R02-R07,D01-D02"),

        plan_row("P10", "Week 2", "Oct 12-15", "Critical", "Run independent four-profile acceptance", "On the independent computer, repeat Docker CPU/GPU and Podman CPU/GPU using only the shipped instructions.", "First-host success is not enough for the full support claim.", "3.0", "Independent tester; release implementer available for observation", "M1; booked host; provider access", "Four independent profile records", "Models/devices, Google/Azure, exports, cancel/error recovery, and target identity pass.", "Oct 15", "Blocked by host and frozen package", "R09,R10,R11,R12,D05"),
        plan_row("P11", "Week 2", "Oct 15-16", "Critical", "Repeat reboot, persistence, and recovery", "Confirm settings, providers, assets, sessions, exports, and all eight volumes survive the required failure and reboot checks.", "This is the final data-safety proof.", "1.0", "Independent tester", "P10; permission to reboot", "Independent recovery matrix", "No destructive cleanup is used and successful state remains usable.", "Oct 16", "Blocked by P10", "R13"),
        plan_row("P12", "Week 2", "Oct 12-16", "High", "Finish public materials and candidate sanitization", "Update the external setup guide, create the final video, review every frame, and inspect final source/package/media outputs.", "User materials must match the accepted workflow and be safe to distribute.", "2.0 (can overlap testing)", "Documentation owner; recorder; security reviewer", "M1; final workflow stable", "Setup guide, video, transcript/captions, candidate sanitization record", "Written guide works without the video and media contains no private values.", "Oct 16", "Open", "D03,D09,S03"),
        plan_row("P13", "Week 2", "Oct 15-16", "Critical", "Reconcile evidence and decide acceptance", "Review every result and either accept all four profiles or describe the exact qualified subset.", "No release claim should be made from partial or mismatched evidence.", "0.75", "Release owner; project lead; independent reviewer", "P10-P12", "Final acceptance matrix and decision", "All hashes/digests/hosts/skips/limitations agree and owners sign the result.", "Oct 16", "Open", "R14,R15,Q01"),
        plan_row("P14", "Week 2", "Oct 12-16", "High", "Owner reviews the operating guide", "The owner and backup walk through responsibilities, access, routine checks, release, recovery, and support instructions.", "This leaves one week to fix handoff gaps before the formal rehearsal.", "0.5 (owner time)", "Receiving owner and backup", "P03,P08,P09", "Reviewed owner guide and rehearsal checklist", "Comments are resolved or assigned.", "Oct 16", "Blocked by guide/access", "H02,H03,H05"),
        plan_row("M2", "Milestone", "Oct 16", "Critical", "Complete acceptance", "Finish technical acceptance and make user documentation/video ready for approved distribution.", "This protects the remaining two weeks for owner transfer and closeout.", "0.0", "Project lead; release owner", "P10-P14", "Accepted release or precise blocked subset", "Decision, evidence, docs, and known limits are complete.", "Oct 16", "Open milestone", "R15"),

        plan_row("P15", "Week 3", "Oct 19-21", "Critical", "Use contingency only for real blockers", "If acceptance found a defect, make the smallest fix, issue a new identity, and rerun affected checks. Otherwise preserve this time as buffer.", "Late optional work would endanger handoff.", "0-2.0 reserved", "Release implementer; reviewer", "M2 findings", "Corrected evidence or preserved unused buffer", "No untracked byte change enters the release.", "Oct 21", "Reserved contingency", "Q03"),
        plan_row("P16", "Week 3", "Oct 19-22", "High", "Prepare release notes, custody map, and migration packet", "Fill in final hashes/links/results and document exactly where source, packages, models, evidence, guides, video, and backlog are held.", "The owner rehearsal needs final, not placeholder, information.", "1.25", "Maintainer; release owner", "M2; P12", "Release notes, custody index, migration-ready packet", "All identities and locations are current and no secret is copied into public records.", "Oct 22", "Open", "D04,H12,A02,Q02"),
        plan_row("P17", "Week 3", "Oct 19-23", "Critical", "Run the owner-operated rehearsal", "The owner performs the important release, diagnosis, recovery, and backlog steps with minimal help.", "This proves the project can continue after October 31.", "1.0", "Receiving owner; backup; maintainer observes", "M2; P14; P16", "Owner rehearsal record and corrected guide", "Owner completes critical procedures and remaining assistance is documented.", "Oct 23", "Blocked by owner availability", "H06"),
        plan_row("P18", "Week 3", "Oct 19-23", "High", "Review backlog and adoption decision", "Agree 30/60/90-day priorities, choose the backlog destination, review pilot feedback, and approve or decline cdcai adoption.", "The final week depends on whether official transfer is authorized.", "0.75 (owner time)", "Project lead; receiving owner; cdcai owner", "M2; P16-P17", "Backlog priorities and explicit adoption decision", "The baseline, official identity next step, and destination are named.", "Oct 23", "Owner-gated", "H08,H10,H11,A01,A03,A04"),
        plan_row("P19", "Week 3", "Oct 19-23", "High", "Finish independent video review and media custody", "A tester repeats the video path and the owner receives all editable and hosted media assets.", "Media that only the outgoing developer controls is not handed off.", "0.5", "Independent tester; recorder; receiving owner", "P12", "Video acceptance and custody record", "Audience access works and owner can maintain the source files.", "Oct 23", "Open", "D10"),
        plan_row("M3", "Milestone", "Oct 23", "Critical", "Complete owner rehearsal", "Owner can operate the release and the adoption path is either authorized or safely deferred.", "This leaves one week for transfer verification and sign-off.", "0.0", "Receiving owner; project lead", "P16-P19", "Rehearsal sign-off and adoption path", "No critical procedure depends only on the outgoing developer.", "Oct 23", "Open milestone", "H06,A03"),

        plan_row("P20", "Week 4", "Oct 26-29", "Critical", "Execute approved adoption or preserve the fallback", "If approved, build/publish official cdcai artifacts and verify them. If not approved, leave cdcai unchanged and deliver the migration-ready packet.", "The deadline does not authorize external changes by itself.", "1.5-2.5", "cdcai maintainer; release owner; independent tester", "M3; explicit authorization", "Official verified release or documented no-adoption handoff", "Every external action is authorized and verified, or explicitly not performed.", "Oct 29", "Owner-gated", "A06,A07,A08,A09,A11"),
        plan_row("P21", "Week 4", "Oct 26-30", "Critical", "Cut over backlog, access, and custody", "Move the accepted backlog to one owner-controlled location and verify all repository/package/media/support access.", "The new owner needs one trustworthy operating surface after closeout.", "0.75", "Receiving owner; maintainer", "M3; H08/H11 decisions", "Canonical backlog and final access/custody record", "Old boards are clearly historical and every needed destination is accessible.", "Oct 30", "Open", "H09,A10,H04,H12"),
        plan_row("P22", "Week 4", "Oct 29-30", "Critical", "Run final sanitization delta and sign off", "Check late changes, record limitations/residuals, close task dispositions, and sign operational closeout.", "October 31 is Saturday and no work should remain for the outgoing developer.", "0.75", "Security reviewer; project lead; receiving owner", "P20-P21", "Final sanitization record and closeout sign-off", "No unresolved critical exposure, ownership gap, hidden release gate, or outgoing-developer dependency remains.", "Oct 30", "Open", "S04,H13"),
        plan_row("M4", "Milestone", "Oct 30", "Critical", "Operational closeout", "End with either completed adoption or a complete migration-ready handoff.", "The hard project end is October 31, a Saturday.", "0.0", "Project lead; receiving owner", "P20-P22", "Signed project-end state", "The owner has artifacts, access, procedures, backlog, and named follow-ups.", "Oct 30", "Open milestone", "H13,A11"),
    ]


def weekday_dates(start: date, end: date) -> list[date]:
    dates = []
    current = start
    while current <= end:
        if current.weekday() < 5:
            dates.append(current)
        current += timedelta(days=1)
    return dates


def calendar_focus(day: date) -> tuple[str, str, str]:
    if day <= date(2026, 10, 2):
        return "Opening days", "Decisions, scheduling, owner guide/backlog/video/sanitization setup", "Book external people and hosts"
    if day <= date(2026, 10, 9):
        milestone = "Candidate freeze" if day == date(2026, 10, 9) else ""
        return "Week 1", "Replacement packages, local validation, browser download, shipped docs", milestone
    if day <= date(2026, 10, 16):
        milestone = "Acceptance complete" if day == date(2026, 10, 16) else ""
        note = "Possible U.S. federal holiday; confirm team availability" if day == date(2026, 10, 12) else milestone
        return "Week 2", "Independent four-profile testing, recovery, user materials, owner guide review", note
    if day <= date(2026, 10, 23):
        milestone = "Owner rehearsal complete" if day == date(2026, 10, 23) else ""
        return "Week 3", "Contingency fixes, final evidence, owner rehearsal, adoption decision", milestone
    milestone = "Operational closeout" if day == date(2026, 10, 30) else ""
    return "Week 4", "Authorized adoption or fallback, transfer verification, backlog cutover, sign-off", milestone


def build_calendar() -> list[list[object]]:
    rows = []
    for index, day in enumerate(weekday_dates(AS_OF, OPERATIONAL_CLOSEOUT), start=1):
        week, focus, milestone = calendar_focus(day)
        rows.append([index, day.isoformat(), day.strftime("%A"), week, focus, milestone or "Normal planned workday"])
    rows.append(["—", PROJECT_END.isoformat(), "Saturday", "Project end", "No planned outgoing-developer work", "Hard project end"])
    return rows


def build_milestones() -> list[list[object]]:
    return [
        ["October 2", "External sessions and preparation locked", "Independent host/tester, owner review/rehearsal, video plan, sanitization scope, and initial handoff work have owners/dates.", "If host/owner time is not reserved, mark the plan AT_RISK immediately."],
        ["October 9", "Final candidate freeze", "Replacement ZIPs, hashes, local checks, browser-download proof, shipped docs, and security review are complete.", "After this date, only release blockers may change shipped bytes; use a new identity and rerun affected checks."],
        ["October 16", "Acceptance complete", "Independent four-profile/recovery evidence is reconciled; user docs/video and owner-guide review are ready.", "If cells remain incomplete, report the exact qualified subset rather than relaxing acceptance."],
        ["October 23", "Owner rehearsal complete", "Owner can perform release/recovery/support procedures; backlog and adoption decisions are recorded.", "If adoption is not approved, finalize the migration-ready fallback."],
        ["October 30", "Operational closeout", "Access, custody, backlog, sanitization, adoption/fallback, and final sign-off are complete.", "No planned work may depend on the outgoing developer after this date."],
        ["October 31", "Hard project end", "Saturday; no project work is scheduled.", "Emergency work is not part of this plan."],
    ]


def build_capacity() -> list[list[object]]:
    return [
        ["Replacement package and local requalification", 3.0, "Required", "New ZIP identity, integrity checks, local four-profile affected checks, browser-download proof."],
        ["Independent acceptance and recovery", 4.0, "Required", "Four profiles plus reboot/persistence/recovery and final evidence reconciliation."],
        ["Public, in-app, external documentation", 2.0, "Required", "Shipped docs, external Setup Guide, release notes, Help/link verification."],
        ["Installation/demo video", 1.5, "Required handoff deliverable", "Storyboard, dry run, capture/edit/captions/privacy review, tester comparison, custody."],
        ["Owner guide and rehearsal", 2.5, "Required", "Guide, role/cadence review, walkthrough, owner-operated rehearsal."],
        ["Sanitization", 1.5, "Required", "Early scope/scan, candidate review, final delta."],
        ["Backlog and governance", 1.5, "Required", "Owner-facing backlog, task disposition, canonical cutover, optional AI/Issues decisions."],
        ["Adoption, access, publication, closeout", 2.5, "Owner-gated", "Permissions, adoption/fallback, official transfer if approved, consumer verification, sign-off."],
        ["Contingency", 3.0, "Protected buffer", "Blocker correction, reruns, owner delays, limited media/document correction."],
        ["Total planned primary-implementer capacity", 21.5, "Fits 22 weekdays", "Leaves only 0.5 day unallocated; if October 12 is non-working, nearly all slack is consumed."],
    ]


def build_risks() -> list[list[object]]:
    return [
        ["K01", "Independent host or tester is not booked", "Critical", "Reserve by October 2; record anonymous host capability and a backup window.", "Project lead / test owner", "If missing by Oct 2, status becomes AT_RISK."],
        ["K02", "Owner/backup cannot attend review or rehearsal", "High", "Book October 16 and October 23 sessions now; use a backup owner.", "Project lead", "If not booked by Oct 2, protect alternate dates."],
        ["K03", "Replacement package changes again after freeze", "High", "Block optional changes; new identity and affected reruns for any necessary change.", "Release owner", "Any byte change after Oct 9 triggers scope review."],
        ["K04", "Independent testing finds a real defect", "High", "Use the 2-3 day contingency; fix only the blocker or report a qualified subset.", "Release implementer / owner", "Do not consume owner-handoff time without reforecasting."],
        ["K05", "Podman/NVIDIA/Python prerequisites fail on the independent host", "High", "Inventory before freeze; prepare approved Python 3.12 and CDI prerequisites; never convert failure to pass.", "Test owner", "Missing prerequisites remain explicit blockers."],
        ["K06", "External Setup Guide/video access is unavailable", "Medium", "Confirm owner-controlled destination and editing/hosting permissions during Week 1.", "Documentation owner", "Written guide remains complete even if video link is delayed."],
        ["K07", "Sensitive content is found late", "High", "Start scoped inventory/scan now; keep findings private and rotate actual credentials through owners.", "Security reviewer", "A substantial incident displaces optional work and changes forecast."],
        ["K08", "cdcai adoption approval or permissions arrive late", "High", "Prepare the migration-ready packet in parallel and use the no-adoption fallback.", "cdcai owner / project lead", "Never treat the deadline as authorization."],
        ["K09", "October 12 is a non-working holiday for participants", "Medium", "Confirm calendar now; plan has 22 weekdays excluding weekends but only 21 if Oct 12 is unavailable.", "Project lead", "Use overlap and protected contingency, not reduced acceptance."],
        ["K10", "Optional backlog work consumes closeout capacity", "High", "Do not start conditional/deferred tasks unless they become direct release blockers.", "Project lead / maintainer", "Filter the backlog by Recommendation before selecting work."],
    ]


def build_plan_overview() -> list[list[object]]:
    return [
        ["Calendar", "Planning window", "October 1 through October 30, 2026; October 31 is Saturday and the hard project end."],
        ["Calendar", "Weekdays available", "22 weekdays when only weekends are excluded; 21 if October 12 is a non-working holiday."],
        ["Assessment", "Feasibility", "Feasible but tight. The plan reserves 3 person-days of contingency and requires documentation/handoff work to overlap technical testing."],
        ["Main risk", "External availability", "Independent Windows hardware/tester and owner/backup time must be booked by October 2."],
        ["Current release state", "Package", "Existing rc4 local evidence is useful, but a new control-package identity is required because packaged manuals changed."],
        ["Current release state", "Signing", "TowerScout stays unsigned under ADR-023; signature-enforcing managed endpoints are outside the standard support claim."],
        ["Must finish before freeze", "October 9", "Replacement ZIPs, integrity/local checks, official hashes, browser-download proof, and shipped documentation."],
        ["Must finish before acceptance", "October 16", "Independent four-profile/recovery evidence, final reconciliation, external guide/video readiness, and owner-guide review."],
        ["Must finish before rehearsal", "October 23", "Owner guide, release notes, custody map, backlog review, media custody, adoption decision or fallback."],
        ["Must finish before closeout", "October 30", "Authorized adoption or migration-ready fallback, access/custody transfer, backlog cutover, sanitization delta, and sign-off."],
        ["Scope rule", "Optional work", "Do not begin conditional or deferred backlog items unless they become direct acceptance blockers."],
        ["Authorization rule", "External changes", "Publishing, cdcai mutation, account changes, and signing require normal owner authorization."],
    ]


def build_source_mapping() -> list[list[object]]:
    return [
        ["Current board", ".agent_work/current-tasks.md", "Controls task status and immediate work."],
        ["Acceptance", ".agent_work/context/status/Reprioritization Effort/2026-09-21-windows-deployment-prioritization-v2.md", "Controls supported outcome as amended by ADR-022/023."],
        ["Work plan", ".agent_work/context/status/Reprioritization Effort/2026-09-21-windows-deployment-hardening-v2.md", "Controls W00-W10 sequence; raw checkboxes need current evidence crosswalk."],
        ["Closeout guide", ".agent_work/context/status/Reprioritization Effort/2026-09-21-post-day-7-backlog-and-handoff-guide.md", "Supplies October documentation, media, sanitization, backlog, owner-guide, and rehearsal work."],
        ["Unsigned decision", ".agent_work/decisions/023-unsigned-windows-package-support-boundary.md", "Removes signing as a standard gate and adds browser-download/hash proof."],
        ["ML decision", ".agent_work/decisions/022-cuda128-blackwell-ml-runtime.md", "Controls CPU/cuda128 identities and device/runtime evidence."],
        ["Release qualification", ".agent_work/tasks/active/TASK-091-owner-runnable-release-qualification.md", "Owns downloadable owner-reproducible acceptance."],
        ["Documentation", ".agent_work/tasks/active/TASK-092-documentation-currentness.md", "Owns repository/package/external user information."],
        ["Recovery", ".agent_work/tasks/active/TASK-093-persistent-data-recovery.md", "Owns data persistence and independent recovery."],
        ["Governance/handoff", ".agent_work/tasks/active/TASK-095-governance-ai-ready-handoff.md", "Owns Phase B owner transfer and closeout."],
        ["Podman", ".agent_work/tasks/active/TASK-097-podman-final-path-qualification.md", "Owns independent Podman CPU/GPU and Python prerequisite proof."],
        ["ML/package evidence", ".agent_work/tasks/active/TASK-103-cuda128-blackwell-ml-runtime.md", "Owns replacement package/browser/independent-host open gates."],
        ["Adoption", ".agent_work/tasks/active/TASK-089-cdcai-migration-execution.md", "Owns owner-gated cdcai transfer or migration-ready fallback."],
        ["Pilot hold", ".agent_work/context/status/Handoff-Planning/PILOT-FEEDBACK-AND-CDC-AI-ADOPTION-PLAN.md", "Keeps v0.1.2 immutable and cdcai unchanged until approval."],
    ]


def make_plan_workbook() -> Path:
    weekly = build_weekly_plan()
    calendar = build_calendar()
    milestones = build_milestones()
    capacity = build_capacity()
    risks = build_risks()
    sources = build_source_mapping()
    sheets = [
        {
            "name": "Plan Overview",
            "title": "TowerScout Project-End Plan: October 1-31, 2026",
            "description": "First draft. Simple language is used so the plan can be followed without knowing TowerScout task numbers. October 30 is operational closeout; October 31 is Saturday and the hard end date.",
            "headers": ["Category", "Topic", "Explanation"],
            "rows": build_plan_overview(),
            "widths": [24, 32, 110],
            "freeze_cols": 1,
            "table_name": "PlanOverview",
        },
        {
            "name": "Weekly Plan",
            "title": "Prioritized Week-by-Week Project-End Plan",
            "description": "Technical acceptance, documentation, media, sanitization, owner transfer, and contingency are planned together. Filter by Week, Priority, Starting status, or action IDs.",
            "headers": PLAN_HEADERS,
            "rows": weekly,
            "widths": [10, 18, 16, 12, 40, 60, 50, 22, 32, 45, 45, 55, 16, 24, 25],
            "freeze_cols": 5,
            "table_name": "WeeklyPlan",
        },
        {
            "name": "Workday Calendar",
            "title": "Available Workdays Through Operational Closeout",
            "description": "There are 22 Monday-Friday dates from October 1 through October 30. Confirm whether October 12 is a non-working holiday for the actual team.",
            "headers": ["Workday number", "Date", "Day", "Plan week", "Primary focus", "Milestone / note"],
            "rows": calendar,
            "widths": [18, 14, 14, 18, 75, 60],
            "freeze_cols": 2,
            "table_name": "WorkdayCalendar",
        },
        {
            "name": "Milestones",
            "title": "Project-End Milestones and Stop Rules",
            "description": "A missed gate changes the forecast or qualified subset. It does not reduce the acceptance standard or silently remove handoff work.",
            "headers": ["Date", "Milestone", "Required outcome", "If it is missed"],
            "rows": milestones,
            "widths": [16, 36, 90, 75],
            "freeze_cols": 2,
            "table_name": "Milestones",
        },
        {
            "name": "Capacity",
            "title": "Primary-Implementer Capacity Allocation",
            "description": "Planning allowances, not promises. Owner/tester time is additional and must be scheduled. Optional work is excluded.",
            "headers": ["Work allocation", "Reserved person-days", "Necessity", "What is included"],
            "rows": capacity,
            "widths": [48, 22, 26, 95],
            "freeze_cols": 1,
            "table_name": "CapacityPlan",
        },
        {
            "name": "Risks and Decisions",
            "title": "Schedule Risks and Required Decisions",
            "description": "These are the conditions most likely to make the plan fail. The mitigation should be started by the stated trigger, not after the milestone is missed.",
            "headers": ["Risk ID", "Risk", "Severity", "Mitigation", "Owner", "Trigger / decision rule"],
            "rows": risks,
            "widths": [10, 50, 16, 75, 30, 60],
            "freeze_cols": 2,
            "table_name": "RisksDecisions",
        },
        {
            "name": "Source Mapping",
            "title": "Planning Source Mapping",
            "description": "This plan is a first-draft synthesis. Current task status and acceptance continue to come from the listed repository sources.",
            "headers": ["Role", "Source", "How it was used"],
            "rows": sources,
            "widths": [28, 100, 80],
            "freeze_cols": 1,
            "table_name": "PlanSources",
        },
    ]
    path = OUTPUT_DIR / "TowerScout-Project-End-Plan-2026-10-01-to-2026-10-31.xlsx"
    write_workbook(path, sheets, "TowerScout Project-End Plan")
    return path


def validate_xlsx(path: Path, expected_sheet_count: int) -> None:
    import xml.etree.ElementTree as ET

    with zipfile.ZipFile(path, "r") as archive:
        names = set(archive.namelist())
        required = {
            "[Content_Types].xml",
            "_rels/.rels",
            "xl/workbook.xml",
            "xl/_rels/workbook.xml.rels",
            "xl/styles.xml",
        }
        missing = required - names
        if missing:
            raise RuntimeError(f"{path.name}: missing required XLSX parts: {sorted(missing)}")
        if archive.testzip() is not None:
            raise RuntimeError(f"{path.name}: ZIP CRC validation failed")
        xml_names = [name for name in names if name.endswith((".xml", ".rels"))]
        for name in xml_names:
            ET.fromstring(archive.read(name))
        worksheet_names = [name for name in names if re.match(r"xl/worksheets/sheet\d+\.xml$", name)]
        if len(worksheet_names) != expected_sheet_count:
            raise RuntimeError(
                f"{path.name}: expected {expected_sheet_count} worksheets, found {len(worksheet_names)}"
            )


def main() -> int:
    backlog = make_backlog_workbook()
    plan = make_plan_workbook()
    validate_xlsx(backlog, 6)
    validate_xlsx(plan, 7)
    print(f"created: {backlog.relative_to(ROOT)} ({backlog.stat().st_size} bytes)")
    print(f"created: {plan.relative_to(ROOT)} ({plan.stat().st_size} bytes)")
    print(f"weekday count through operational closeout: {len(weekday_dates(AS_OF, OPERATIONAL_CLOSEOUT))}")
    print(f"curated open-action rows: {len(build_open_actions())}")
    print(f"raw unchecked checklist rows: {len(build_raw_unchecked())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
