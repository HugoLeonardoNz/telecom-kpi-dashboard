"""
build_db.py
Grava os mesmos dados do painel num arquivo SQLite (data/fibernet_kpi.db).

O app usa um SQLite em memória (src/db.py) porque o Streamlit Cloud tem
filesystem efêmero -- não adianta persistir lá. Este script existe para quem
quiser abrir a base fora do app: DBeaver, DB Browser for SQLite, `sqlite3`
na linha de comando, ou só para conferir que as consultas de src/db.py
rodam contra uma base real, não um mock.

Uso:
    python tools/build_db.py

Saída:
    data/fibernet_kpi.db
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.data_loader import build_cohort, build_monthly, build_plans, build_regions, build_support  # noqa: E402

DEST = ROOT / "data" / "fibernet_kpi.db"


def main() -> None:
    DEST.parent.mkdir(parents=True, exist_ok=True)
    if DEST.exists():
        DEST.unlink()

    conn = sqlite3.connect(DEST)
    tabelas = {
        "monthly":            build_monthly(),
        "plans":              build_plans(),
        "regions":            build_regions(105.0),
        "cohort":              build_cohort(),
    }
    cat_df, trend_df = build_support()
    tabelas["support_categories"] = cat_df
    tabelas["support_trend"]      = trend_df

    for nome, df in tabelas.items():
        df.to_sql(nome, conn, index=False, if_exists="replace")
        print(f"  OK  {nome:20s} -> {len(df)} linhas")

    conn.close()
    print(f"\nGravado em {DEST.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
