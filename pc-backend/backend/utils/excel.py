from io import BytesIO
from flask import Response
from openpyxl import Workbook
from typing import List, Dict

def build_excel_response(wb: Workbook, filename: str) -> Response:
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return Response(output, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": f"attachment;filename={filename}"})

def _build_campaign_command_workbook(rows: List[Dict], totals: Dict, args: Dict) -> Workbook:
    wb = Workbook()
    ws = wb.active
    for k in ("start_date", "end_date", "master_store_ids", "bm_ids", "status", "mode"):
        ws.append([k, str(args.get(k))])
    ws.append([])
    if rows:
        ws.append(list(rows[0].keys()))
        for r in rows:
            ws.append(list(r.values()))
    ws.append([])
    ws.append(["TOTALS"])
    for k, v in totals.items():
        ws.append([k, v])
    return wb