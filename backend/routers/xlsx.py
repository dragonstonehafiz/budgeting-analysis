"""
XLSX router — exposes Excel file management operations.
"""
from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.post("/reformat")
def reformat_xlsx():
    """Reformat purchases.xlsx — sort by date, apply styles, rebuild validation."""
    try:
        from excel.handler import remake_xlsx_file
        remake_xlsx_file("data/purchases.xlsx")
        return {"status": "ok", "message": "File reformatted successfully."}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
