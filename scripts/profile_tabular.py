#!/usr/bin/env python3
"""Read-only aggregate profile for CSV and XLSX; no uploads or source edits."""
from __future__ import annotations
import argparse
import csv
import json
from collections import Counter
from datetime import date, datetime
from pathlib import Path

def csv_rows(path, delimiter):
    with path.open("r", encoding="utf-8-sig", newline="") as fp:
        sample = fp.read(8192)
        fp.seek(0)
        if delimiter is None:
            try:
                delimiter = csv.Sniffer().sniff(sample, delimiters=",;\t|").delimiter
            except csv.Error:
                delimiter = ";" if sample.count(";") > sample.count(",") else ","
        reader = csv.reader(fp, delimiter=delimiter)
        try:
            header = list(next(reader))
        except StopIteration:
            raise ValueError("Arquivo CSV vazio")
        yield header, reader, {"format": "csv", "delimiter": delimiter}

def xlsx_rows(path, sheet_name):
    try:
        import openpyxl
    except ImportError as exc:
        raise RuntimeError("XLSX exige openpyxl. Instale com: pip install openpyxl") from exc
    workbook = openpyxl.load_workbook(path, read_only=True, data_only=False)
    try:
        if sheet_name and sheet_name not in workbook.sheetnames:
            raise ValueError("Aba ausente")
        sheets = [workbook[sheet_name]] if sheet_name else workbook.worksheets
        for sheet in sheets:
            iterator = sheet.iter_rows(values_only=True)
            try:
                header = [str(v).strip() if v is not None else "" for v in next(iterator)]
            except StopIteration:
                continue
            yield header, iterator, {"format": "xlsx", "sheet": sheet.title}
    finally:
        workbook.close()

def is_blank(v):
    return v is None or (isinstance(v, str) and v.strip() == "")

def profile(header, rows, key, max_rows, max_keys):
    header = [str(h).strip() for h in header]
    if not any(header):
        raise ValueError("Cabeçalho vazio")
    if len(set(header)) != len(header) or "" in header:
        raise ValueError("Cabeçalhos duplicados ou vazios")
    if key and key not in header:
        raise ValueError(f"Chave {key!r} não encontrada")
    counts = {c: Counter() for c in header}
    n = 0
    observed = set()
    key_dupes = 0
    key_missing = 0
    key_coverage_limited = False
    extra_cells = 0
    truncated = False
    kidx = header.index(key) if key else None
    for raw in rows:
        if max_rows and n >= max_rows:
            truncated = True
            break
        cells = list(raw)
        if len(cells) > len(header):
            extra_cells += 1
        cells = (cells + [None] * len(header))[:len(header)]
        if all(is_blank(v) for v in cells):
            continue
        n += 1
        for i,c in enumerate(header):
            val = cells[i]
            if is_blank(val):
                counts[c]["missing"] += 1
            elif isinstance(val, str) and val.startswith("="):
                counts[c]["formulas"] += 1
            elif isinstance(val, (int,float)) and not isinstance(val,bool):
                counts[c]["numeric_cells"] += 1
            elif isinstance(val,(date,datetime)):
                counts[c]["date_cells"] += 1
            else:
                counts[c]["other_cells"] += 1
        if kidx is not None:
            value = cells[kidx]
            if is_blank(value):
                key_missing += 1
            elif not key_coverage_limited:
                identifier = str(value).strip()
                if identifier in observed:
                    key_dupes += 1
                elif len(observed) < max_keys:
                    observed.add(identifier)
                else:
                    key_coverage_limited = True
    return {
        "rows_profiled":n,"truncated_by_max_rows":truncated,
        "rows_with_extra_cells":extra_cells,"key":key,
        "duplicate_keys_in_observed_set":key_dupes if key else None,
        "missing_keys":key_missing if key else None,
        "key_uniqueness_check_limited":key_coverage_limited if key else None,
        "columns":[{"name":c,**dict(counts[c]),"missing_pct":round(100*counts[c]["missing"]/n,2) if n else None} for c in header],
        "note":"Perfil agregado; não revela valores de células e não recalcula fórmulas."
    }

def main(argv=None):
    ap=argparse.ArgumentParser(description="Perfil de CSV ou XLSX somente leitura")
    ap.add_argument("file",type=Path)
    ap.add_argument("--sheet")
    ap.add_argument("--key")
    ap.add_argument("--delimiter")
    ap.add_argument("--max-rows",type=int,default=0)
    ap.add_argument("--max-keys",type=int,default=100000)
    args=ap.parse_args(argv)
    if args.max_rows<0 or args.max_keys<1:
        ap.error("Limites inválidos")
    if not args.file.is_file():
        ap.error("Arquivo inexistente")
    try:
        ext=args.file.suffix.lower()
        if ext==".csv":
            if args.sheet:
                raise ValueError("--sheet é permitido apenas para XLSX")
            source=csv_rows(args.file,args.delimiter)
        elif ext==".xlsx":
            source=xlsx_rows(args.file,args.sheet)
        else:
            raise ValueError("Use CSV ou XLSX")
        results=[{**meta,**profile(header,rows,args.key,args.max_rows,args.max_keys)} for header,rows,meta in source]
        print(json.dumps({"status":"ok","files_profiled":len(results),"profiles":results},ensure_ascii=False,indent=2))
        return 0
    except (OSError,ValueError,RuntimeError,csv.Error) as exc:
        print(json.dumps({"status":"error","message":str(exc)},ensure_ascii=False,indent=2))
        return 2

if __name__=="__main__":
    raise SystemExit(main())
