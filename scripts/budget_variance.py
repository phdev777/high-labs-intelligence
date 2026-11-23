#!/usr/bin/env python3
"""Read-only CSV aggregation of budget vs actual using decimal arithmetic."""
from __future__ import annotations
import argparse
import csv
import json
import re
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path

def parse_amount(raw: str, locale: str = "br") -> Decimal:
    text = str(raw).strip().replace("\u00a0", "").replace(" ", "")
    if not text:
        raise ValueError("valor monetário vazio")
    negative_parens = text.startswith("(") and text.endswith(")")
    if negative_parens:
        text = text[1:-1]
    text = text.replace("R$", "").replace("$", "")
    if locale == "br":
        text = text.replace(".", "").replace(",", ".")
    elif locale == "us":
        text = text.replace(",", "")
    else:
        raise ValueError("locale deve ser br ou us")
    if not re.fullmatch(r"[+-]?\d+(?:\.\d+)?", text):
        raise ValueError("formato monetário inválido")
    try:
        result = Decimal(text)
        if not result.is_finite():
            raise ValueError("valor não finito")
        return -result if negative_parens else result
    except InvalidOperation as exc:
        raise ValueError("valor numérico inválido") from exc

def analyze(path: Path, group_by: list[str], budget_col: str, actual_col: str, locale: str, allow_partial: bool = False) -> tuple[dict, int]:
    with path.open("r", encoding="utf-8-sig", newline="") as fp:
        sample = fp.read(8192)
        fp.seek(0)
        try:
            delim = csv.Sniffer().sniff(sample, delimiters=",;\t|").delimiter
        except csv.Error:
            delim = ";" if sample.count(";") > sample.count(",") else ","
        reader = csv.DictReader(fp, delimiter=delim)
        if not reader.fieldnames:
            raise ValueError("CSV sem cabeçalho")
        fields = [c.strip() for c in reader.fieldnames]
        if len(fields) != len(set(fields)) or any(not c for c in fields):
            raise ValueError("Cabeçalhos duplicados/vazios")
        missing = set(group_by + [budget_col, actual_col]).difference(fields)
        if missing:
            raise ValueError("Colunas ausentes: " + ", ".join(sorted(missing)))
        totals = defaultdict(lambda: [Decimal(0), Decimal(0), 0])
        errors = []
        read_count = 0
        for rowno, row in enumerate(reader, start=2):
            if row.get(None):
                errors.append({"line": rowno, "error": "células extras; conferir delimitador"})
                continue
            if all(not str(v or "").strip() for v in row.values()):
                continue
            read_count += 1
            try:
                key = tuple(str(row[c] or "").strip() for c in group_by)
                if any(not x for x in key):
                    raise ValueError("dimensão de agrupamento vazia")
                budget = parse_amount(row[budget_col], locale)
                actual = parse_amount(row[actual_col], locale)
                totals[key][0] += budget
                totals[key][1] += actual
                totals[key][2] += 1
            except (ValueError, TypeError, KeyError) as exc:
                errors.append({"line": rowno, "error": str(exc)})
        valid_rows = sum(v[2] for v in totals.values())
        if errors and not allow_partial:
            return ({"status": "error", "reason": "linhas inválidas; agregação não publicada", "input_rows": read_count, "invalid_rows": len(errors), "error_examples": errors[:20]}, 2)
        rows = []
        total_budget = Decimal(0)
        total_actual = Decimal(0)
        for key in sorted(totals):
            budget, actual, count = totals[key]
            diff = actual - budget
            pct = str((diff / abs(budget) * 100).quantize(Decimal("0.01"))) if budget != 0 else None
            total_budget += budget
            total_actual += actual
            rows.append({**dict(zip(group_by, key)), "rows": count, "orcado": str(budget), "realizado": str(actual), "variacao_absoluta": str(diff), "variacao_percentual": pct})
        return {
            "status": "partial" if errors else "ok", "currency": "não inferida", "numeric_locale": locale,
            "input_rows": read_count, "valid_rows": valid_rows, "invalid_rows": len(errors),
            "error_examples": errors[:20], "group_by": group_by,
            "total_orcado": str(total_budget), "total_realizado": str(total_actual),
            "total_variacao": str(total_actual - total_budget), "groups": rows,
            "interpretation": "Variação = realizado - orçado. Sinal favorável/desfavorável depende da natureza da conta. Base zero => percentual não aplicável."
        }, 0

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Orçado x realizado por dimensões em CSV; modo somente leitura")
    ap.add_argument("file", type=Path)
    ap.add_argument("--group-by", default="categoria,periodo")
    ap.add_argument("--budget-column", default="orcado")
    ap.add_argument("--actual-column", default="realizado")
    ap.add_argument("--locale", choices=("br", "us"), default="br")
    ap.add_argument("--allow-partial", action="store_true")
    args = ap.parse_args(argv)
    if not args.file.is_file() or args.file.suffix.lower() != ".csv":
        ap.error("Informe um CSV existente")
    group = [x.strip() for x in args.group_by.split(",") if x.strip()]
    if not group or len(group) != len(set(group)):
        ap.error("--group-by deve conter dimensões únicas")
    try:
        result, code = analyze(args.file, group, args.budget_column, args.actual_column, args.locale, args.allow_partial)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return code
    except (OSError, ValueError, csv.Error) as exc:
        print(json.dumps({"status": "error", "message": str(exc)}, ensure_ascii=False, indent=2))
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
