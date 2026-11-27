from __future__ import annotations

import csv
import html
import io
import json
import os
import sqlite3
import time
from pathlib import Path
from typing import Any
import urllib.parse
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from starlette.requests import Request
from App.src.utils.req import _request_ctx


# Exact Adminer compiled stylesheet extracted from Adminer 6.3.0
ADMINER_CSS = """html{--bg:#fff;--fg:#000;--dim:#eee;--lit:#ddf;}body{color:var(--fg);background:var(--bg);font:90%/1.25 Verdana,Arial,Helvetica,sans-serif;margin:0;min-width:fit-content;}a{color:blue;text-decoration:none;}a:visited{color:navy;}a:link:hover,a:visited:hover{color:red;text-decoration:underline;}a.text:hover,a.icon-copy:hover{text-decoration:none;}a.jush-help:hover{color:inherit;}button.link{font:inherit;padding:0;border:0;background:none;color:blue;cursor:pointer;}button.link:hover{color:red;text-decoration:underline;}h1{font-size:150%;margin:0;padding:.8em .667em;border-bottom:1px solid #999;font-weight:normal;color:#777;background:var(--dim);}h2{font-size:150%;margin:0 0 20px;margin-inline-start:-18px;padding:.8em 1em;border-bottom:1px solid var(--fg);font-weight:normal;background:var(--lit);}h2 .doc{float:right;position:sticky;right:20px;}h3{font-weight:normal;font-size:130%;margin:1em 0 0;}form{margin:0;}table{margin:1em 0 0;margin-inline-end:20px;font-size:90%;border-spacing:0;border:0;}table,td,th,.column{border-color:#999;border-style:solid;}td,th{border-width:0;border-block-end-width:1px;border-inline-end-width:1px;padding:.3em .5em;margin:0;}td:first-child,th:first-child{border-inline-start-width:1px;}table >:first-child >:first-child > td,table >:first-child >:first-child > th{border-top-width:1px;}td table{width:100%;margin:0;}fieldset table:first-child{margin:0;}th{background:var(--dim);text-align:start;}th .doc{font-weight:normal;}thead{position:sticky;top:0;z-index:1;}thead th{text-align:center;padding:.3em .6em;}thead td,thead th{background:var(--lit);}tbody tr:hover td,tbody tr:hover th{background:var(--dim);}td.hover,tr:hover td.hover,.js .checkable .checked td.hover{background-color:var(--bg);border-bottom-width:0;}td.hover:first-child{border-inline-start-width:0;}td.hover:last-child{border-inline-end-width:0;}table >:first-child >:first-child > td.hover{border-top-width:0;}fieldset{display:inline;vertical-align:top;padding:.5em .8em;margin:.8em 0 0;margin-inline-end:.5em;border:1px solid #999;border-radius:5px;}p{margin:.8em 0 0;margin-inline-end:20px;}img{vertical-align:middle;border:0;}td img{max-width:200px;max-height:200px;}code{padding:1px 2px;background:var(--dim);}mark{color:inherit;background:#ff9;}pre{margin:1em 0 0;tab-size:4;}td pre{margin:0;}textarea{font-family:inherit;line-height:inherit;}code,pre.jush:not(.sqlarea){font:inherit;}pre,.sqlarea,.sql{font:110%/1.25 monospace;}pre.jush{background:var(--bg);}pre code{display:block;}input,textarea{box-sizing:border-box;}input,select{vertical-align:middle;}input[type="radio"]{vertical-align:text-bottom;}input.default{box-shadow:1px 1px 1px #777;}input.required,input.maxlength,textarea.maxlength{box-shadow:1px 1px 1px red;}[draggable]{cursor:grab;}:target{background:var(--lit);}.block{display:block;}.version{color:#777;font-size:62%;}.js .hidden,.nojs .jsonly,.insecure .icon-copy{display:none;}[hidden]{display:none !important;}.column{position:absolute;background:var(--lit);padding:.27em 0 .33em;padding-inline-end:1ex;margin-top:-.37em;border-width:1px;border-inline-start-width:0;border-radius:0 8px 8px 0;}th:not(:hover) .column{display:none;}.nowrap td,.nowrap th,td.nowrap,p.nowrap{white-space:pre;}.error{color:red;background:#fee;}.error b{background:var(--bg);font-weight:normal;}.error pre code{background:var(--bg);}.message{color:green;background:#efe;}.message table{color:var(--fg);background:var(--bg);}.error,.message{padding:.5em .8em;margin:1em 0 0;margin-inline-end:20px;}td .error{padding:1px;margin:0;}.odds tbody tr{background:var(--bg);}.odds tbody tr:nth-child(2n){background:#F5F5F5;}.js .checkable .checked td,.js .checkable .checked th{background:var(--lit);}.time{color:#666;font-size:70%;}.function,.number,.datetime{text-align:right;}.type{width:15ex;}.options select,.options input{width:20ex;}.view{font-style:italic;}.active{font-weight:bold;}.sqlarea{width:98%;}.sql-footer{margin-bottom:2.5em;}.links a{white-space:nowrap;margin-inline-end:20px;}#menu{margin:10px 0 0;}#menu p,#logins,#tables{padding:.8em 1em;margin:0;border-bottom:1px solid #ccc;}#tables li{list-style:none;}#tables{white-space:nowrap;overflow:hidden;}#tables a,#tables span{background:var(--bg);}#content{margin:2em 0 0;margin-inline-start:21em;padding:10px 0 20px;padding-inline-end:20px;}#breadcrumb{white-space:nowrap;position:absolute;top:0;left:21em;background:var(--dim);height:2em;line-height:1.8em;padding:0 1em;margin:0;margin-inline-start:-18px;}#menu{position:absolute;top:2em;left:0;width:19em;}.act-btn{display:inline-flex;align-items:center;gap:3px;padding:2px 6px;border-radius:3px;text-decoration:none !important;font-size:11px;}.act-edit{color:#1e40af;background:#dbeafe;border:1px solid #bfdbfe;}.act-edit:hover{background:#bfdbfe;color:#1e3a8a;}.act-del{color:#991b1b;background:#fee2e2;border:1px solid #fecaca;margin-left:4px;}.act-del:hover{background:#fecaca;color:#7f1d1d;}.act-uniq{color:#6b21a8;background:#f3e8ff;border:1px solid #e9d5ff;margin-left:4px;}.act-uniq:hover{background:#e9d5ff;color:#581c87;}.act-idx{color:#0369a1;background:#e0f2fe;border:1px solid #bae6fd;margin-left:4px;}.act-idx:hover{background:#bae6fd;color:#0c4a6e;}.badge-pk{display:inline-block;padding:1px 5px;border-radius:3px;font-size:10px;font-weight:bold;background:#fef3c7;color:#b45309;border:1px solid #fde68a;}.badge-uniq{display:inline-block;padding:1px 5px;border-radius:3px;font-size:10px;font-weight:bold;background:#f3e8ff;color:#7e22ce;border:1px solid #e9d5ff;margin-left:3px;}.badge-idx{display:inline-block;padding:1px 5px;border-radius:3px;font-size:10px;font-weight:bold;background:#e0f2fe;color:#0284c7;border:1px solid #bae6fd;margin-left:3px;}@media all and (max-width:800px){#menu{position:static;width:auto;margin:10px;}#content{margin-inline-start:10px !important;}#breadcrumb{position:static;margin:0;}}"""


class SQLite:
    PAGE_SIZE = 100  # Strictly max 100 rows per page to prevent freezing on large datasets

    @classmethod
    def view(
        cls,
        db_path: str | Path | None,
        request: Request | None = None,
        title: str = "Adminer - SQLite",
    ) -> Response:
        req = request or _request_ctx.get()
        query_params = dict(req.query_params) if req else {}

        if not db_path:
            return HTMLResponse(
                cls._render_error("No database path provided.", "Please specify a valid SQLite database path."),
                status_code=400,
            )

        resolved_path = Path(db_path).resolve()
        if not resolved_path.is_file():
            resolved_path.parent.mkdir(parents=True, exist_ok=True)
            if not resolved_path.exists():
                resolved_path.touch()

        # Connect to SQLite
        try:
            conn = sqlite3.connect(str(resolved_path), timeout=10)
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
        except Exception as exc:
            return HTMLResponse(
                cls._render_error(f"Cannot open database: {resolved_path.name}", str(exc)),
                status_code=500,
            )

        base_url = req.url.path if req else ""
        action = query_params.get("action", "").strip()
        selected_table = query_params.get("table", "").strip() or None
        search_query = query_params.get("q", "").strip()
        custom_sql = query_params.get("sql", "").strip()
        page = max(1, int(query_params.get("page", 1)))
        per_page = cls.PAGE_SIZE

        flash_msg: str | None = query_params.get("flash_msg")
        flash_error: str | None = query_params.get("flash_error")

        def redirect_response(target_tbl: str | None, target_act: str = "", msg: str | None = None, err: str | None = None) -> RedirectResponse:
            try:
                conn.close()
            except Exception:
                pass
            p: dict[str, str] = {}
            if target_tbl:
                p["table"] = target_tbl
            if target_act:
                p["action"] = target_act
            if msg:
                p["flash_msg"] = msg
            if err:
                p["flash_error"] = err
            qs = f"?{urllib.parse.urlencode(p)}" if p else ""
            return RedirectResponse(f"{base_url}{qs}", status_code=303)

        # -------------------------------------------------------------
        # Action Handler: Drop Table
        # -------------------------------------------------------------
        if action == "drop_table" and selected_table:
            try:
                cur.execute(f'DROP TABLE "{selected_table}"')
                conn.commit()
                return redirect_response(None, "", msg=f'Table "{selected_table}" was dropped successfully.')
            except Exception as exc:
                return redirect_response(selected_table, "", err=f"Failed to drop table: {exc}")

        # -------------------------------------------------------------
        # Action Handler: Delete Row
        # -------------------------------------------------------------
        elif action == "delete" and selected_table:
            rowid = query_params.get("rowid")
            if rowid is not None and rowid != "None":
                try:
                    rowid_val = int(rowid)
                except (ValueError, TypeError):
                    rowid_val = rowid
                try:
                    cur.execute(f'DELETE FROM "{selected_table}" WHERE rowid = ?', (rowid_val,))
                    conn.commit()
                    if cur.rowcount > 0:
                        return redirect_response(selected_table, "", msg=f"Item (rowid {rowid}) was deleted successfully.")
                    else:
                        return redirect_response(selected_table, "", err=f"Delete matched 0 rows for rowid {rowid}.")
                except Exception as exc:
                    return redirect_response(selected_table, "", err=f"Delete error: {exc}")
            else:
                return redirect_response(selected_table, "", err="Invalid rowid for delete.")

        # -------------------------------------------------------------
        # Action Handler: Do Insert Row
        # -------------------------------------------------------------
        elif action == "do_insert" and selected_table:
            try:
                cur.execute(f'PRAGMA table_info("{selected_table}")')
                cols_info = cur.fetchall()
                insert_cols = []
                insert_vals = []
                for col in cols_info:
                    cname = col["name"]
                    param_key = f"col_{cname}"
                    if param_key in query_params:
                        val = query_params[param_key]
                        if col["pk"] and val == "":
                            continue
                        insert_cols.append(f'"{cname}"')
                        insert_vals.append(None if val == "" and not col["notnull"] else val)

                if insert_cols:
                    placeholders = ", ".join(["?"] * len(insert_vals))
                    cols_str = ", ".join(insert_cols)
                    cur.execute(f'INSERT INTO "{selected_table}" ({cols_str}) VALUES ({placeholders})', insert_vals)
                    conn.commit()
                    return redirect_response(selected_table, "", msg="Item was inserted successfully.")
                else:
                    return redirect_response(selected_table, "insert", err="No values to insert.")
            except Exception as exc:
                return redirect_response(selected_table, "insert", err=f"Insert error: {exc}")

        # -------------------------------------------------------------
        # Action Handler: Do Update Row
        # -------------------------------------------------------------
        elif action == "do_update" and selected_table:
            rowid = query_params.get("rowid")
            if not rowid or str(rowid).strip() == "None":
                rowid = query_params.get("col_id")
            if not rowid or str(rowid).strip() == "None":
                try:
                    cur.execute(f'PRAGMA table_info("{selected_table}")')
                    cols_meta = cur.fetchall()
                    for c in cols_meta:
                        if c["pk"] and f"col_{c['name']}" in query_params:
                            rowid = query_params[f"col_{c['name']}"]
                            break
                except Exception:
                    pass
            if rowid is not None and str(rowid).strip() != "None":
                try:
                    rowid_val = int(rowid)
                except (ValueError, TypeError):
                    rowid_val = rowid

                try:
                    cur.execute(f'PRAGMA table_info("{selected_table}")')
                    cols_info = cur.fetchall()
                    set_clauses = []
                    update_vals = []
                    for col in cols_info:
                        cname = col["name"]
                        param_key = f"col_{cname}"
                        if param_key in query_params:
                            val = query_params[param_key]
                            if col["pk"]:
                                continue  # Keep primary key stable during row update
                            set_clauses.append(f'"{cname}" = ?')
                            update_vals.append(None if val == "" and not col["notnull"] else val)

                    if set_clauses:
                        update_vals.append(rowid_val)
                        set_str = ", ".join(set_clauses)
                        cur.execute(f'UPDATE "{selected_table}" SET {set_str} WHERE rowid = ?', update_vals)
                        conn.commit()
                        if cur.rowcount > 0:
                            return redirect_response(selected_table, "", msg=f"Item (rowid {rowid}) was updated successfully.")
                        else:
                            return redirect_response(selected_table, "", err=f"Update matched 0 rows for rowid {rowid}.")
                    else:
                        return redirect_response(selected_table, "", err="No values to update.")
                except Exception as exc:
                    return redirect_response(selected_table, "", err=f"Update error: {exc}")
            else:
                return redirect_response(selected_table, "", err="Invalid row identifier for update.")

        # -------------------------------------------------------------
        # Action Handler: Do Create Table
        # -------------------------------------------------------------
        elif action == "do_create_table":
            new_table_name = query_params.get("new_table_name", "").strip()
            if not new_table_name:
                return redirect_response(None, "create_table", err="Table name cannot be empty.")
            else:
                col_defs = []
                unique_cols = []
                index_cols = []
                idx = 0
                while f"cname_{idx}" in query_params:
                    cn = query_params[f"cname_{idx}"].strip()
                    ct = query_params.get(f"ctype_{idx}", "TEXT").strip()
                    cpk = query_params.get(f"cpk_{idx}") == "1"
                    cnn = query_params.get(f"cnn_{idx}") == "1"
                    cdflt = query_params.get(f"cdflt_{idx}", "").strip()
                    cuniq = query_params.get(f"cuniq_{idx}") == "1"
                    cidx = query_params.get(f"cidx_{idx}") == "1"

                    if cn:
                        line = f'"{cn}" {ct}'
                        if cpk:
                            line += " PRIMARY KEY AUTOINCREMENT" if ct.upper() == "INTEGER" else " PRIMARY KEY"
                        if cnn and not cpk:
                            line += " NOT NULL"
                        if cdflt:
                            line += f" DEFAULT '{cdflt}'"
                        col_defs.append(line)
                        if cuniq and not cpk:
                            unique_cols.append(cn)
                        elif cidx and not cpk:
                            index_cols.append(cn)
                    idx += 1

                if not col_defs:
                    return redirect_response(None, "create_table", err="At least one column definition is required.")
                else:
                    try:
                        create_sql = f'CREATE TABLE "{new_table_name}" (\n  ' + ",\n  ".join(col_defs) + "\n)"
                        cur.execute(create_sql)
                        for u_col in unique_cols:
                            cur.execute(f'CREATE UNIQUE INDEX IF NOT EXISTS "uniq_{new_table_name}_{u_col}" ON "{new_table_name}" ("{u_col}")')
                        for i_col in index_cols:
                            cur.execute(f'CREATE INDEX IF NOT EXISTS "idx_{new_table_name}_{i_col}" ON "{new_table_name}" ("{i_col}")')
                        conn.commit()
                        return redirect_response(new_table_name, "", msg=f'Table "{new_table_name}" was created successfully.')
                    except Exception as exc:
                        return redirect_response(None, "create_table", err=f"Create Table error: {exc}")

        # -------------------------------------------------------------
        # Action Handler: Drop Column (Schema Drop)
        # -------------------------------------------------------------
        elif action == "drop_column" and selected_table:
            col_to_drop = query_params.get("col", "").strip()
            if col_to_drop:
                try:
                    cur.execute(f'ALTER TABLE "{selected_table}" DROP COLUMN "{col_to_drop}"')
                    conn.commit()
                    return redirect_response(selected_table, "schema", msg=f'Column "{col_to_drop}" was dropped successfully.')
                except Exception as exc:
                    return redirect_response(selected_table, "schema", err=f"Drop column error: {exc}")
            else:
                return redirect_response(selected_table, "schema", err="Column name is missing.")

        # -------------------------------------------------------------
        # Action Handler: Add Column with Index / Unique Check/Radio
        # -------------------------------------------------------------
        elif action == "do_add_column" and selected_table:
            add_cname = query_params.get("add_col_name", "").strip()
            add_ctype = query_params.get("add_col_type", "TEXT").strip()
            add_cdflt = query_params.get("add_col_default", "").strip()
            add_cnn = query_params.get("add_col_notnull") == "1"
            add_cidx = query_params.get("add_col_index", "").strip().upper()

            if add_cname:
                try:
                    sql = f'ALTER TABLE "{selected_table}" ADD COLUMN "{add_cname}" {add_ctype}'
                    if add_cnn:
                        sql += f" NOT NULL DEFAULT '{add_cdflt}'"
                    elif add_cdflt:
                        sql += f" DEFAULT '{add_cdflt}'"
                    cur.execute(sql)
                    if add_cidx == "UNIQUE":
                        cur.execute(f'CREATE UNIQUE INDEX IF NOT EXISTS "uniq_{selected_table}_{add_cname}" ON "{selected_table}" ("{add_cname}")')
                        flash_msg = f'Column "{add_cname}" with UNIQUE index was added successfully.'
                    elif add_cidx == "INDEX":
                        cur.execute(f'CREATE INDEX IF NOT EXISTS "idx_{selected_table}_{add_cname}" ON "{selected_table}" ("{add_cname}")')
                        flash_msg = f'Column "{add_cname}" with INDEX was added successfully.'
                    else:
                        flash_msg = f'Column "{add_cname}" was added successfully.'
                    conn.commit()
                    return redirect_response(selected_table, "schema", msg=flash_msg)
                except Exception as exc:
                    return redirect_response(selected_table, "schema", err=f"Add column error: {exc}")
            else:
                return redirect_response(selected_table, "schema", err="Column name cannot be empty.")

        # -------------------------------------------------------------
        # Action Handler: Do Edit Column (Schema Change)
        # -------------------------------------------------------------
        elif action == "do_edit_column" and selected_table:
            old_cname = query_params.get("old_col_name", "").strip()
            new_cname = query_params.get("new_col_name", "").strip()
            new_ctype = query_params.get("new_col_type", "TEXT").strip()
            new_cnn = query_params.get("new_col_notnull") == "1"
            new_cdflt = query_params.get("new_col_default", "").strip()
            edit_cidx = query_params.get("edit_col_index", "").strip().upper()

            if old_cname and new_cname:
                try:
                    cur.execute(f'PRAGMA table_info("{selected_table}")')
                    cols_info = cur.fetchall()

                    new_cols_def = []
                    select_old_cols = []
                    insert_new_cols = []

                    for col in cols_info:
                        cn = col["name"]
                        if cn == old_cname:
                            is_pk = col["pk"]
                            line = f'"{new_cname}" {new_ctype}'
                            if is_pk:
                                line += " PRIMARY KEY AUTOINCREMENT" if new_ctype.upper() == "INTEGER" else " PRIMARY KEY"
                            if new_cnn and not is_pk:
                                line += " NOT NULL"
                            if new_cdflt:
                                line += f" DEFAULT '{new_cdflt}'"
                            new_cols_def.append(line)
                            select_old_cols.append(f'"{cn}"')
                            insert_new_cols.append(f'"{new_cname}"')
                        else:
                            is_pk = col["pk"]
                            line = f'"{cn}" {col["type"] or "TEXT"}'
                            if is_pk:
                                line += " PRIMARY KEY AUTOINCREMENT" if (col["type"] or "").upper() == "INTEGER" else " PRIMARY KEY"
                            if col["notnull"] and not is_pk:
                                line += " NOT NULL"
                            if col["dflt_value"] is not None:
                                line += f" DEFAULT '{col['dflt_value']}'"
                            new_cols_def.append(line)
                            select_old_cols.append(f'"{cn}"')
                            insert_new_cols.append(f'"{cn}"')

                    temp_table = f"{selected_table}_adminer_temp_{int(time.time())}"
                    create_sql = f'CREATE TABLE "{temp_table}" (\n  ' + ",\n  ".join(new_cols_def) + "\n)"
                    cur.execute(create_sql)
                    cur.execute(f'INSERT INTO "{temp_table}" ({", ".join(insert_new_cols)}) SELECT {", ".join(select_old_cols)} FROM "{selected_table}"')
                    cur.execute(f'DROP TABLE "{selected_table}"')
                    cur.execute(f'ALTER TABLE "{temp_table}" RENAME TO "{selected_table}"')

                    if edit_cidx == "UNIQUE":
                        cur.execute(f'CREATE UNIQUE INDEX IF NOT EXISTS "uniq_{selected_table}_{new_cname}" ON "{selected_table}" ("{new_cname}")')
                    elif edit_cidx == "INDEX":
                        cur.execute(f'CREATE INDEX IF NOT EXISTS "idx_{selected_table}_{new_cname}" ON "{selected_table}" ("{new_cname}")')

                    conn.commit()
                    return redirect_response(selected_table, "schema", msg=f'Column "{old_cname}" was modified to "{new_cname}" successfully.')
                except Exception as exc:
                    return redirect_response(selected_table, "schema", err=f"Edit column error: {exc}")
            else:
                return redirect_response(selected_table, "schema", err="Column names cannot be empty.")

        # -------------------------------------------------------------
        # Action Handler: Add Index / Unique (Direct Quick Action)
        # -------------------------------------------------------------
        elif action == "add_index" and selected_table:
            col_name = query_params.get("col", "").strip()
            idx_type = query_params.get("type", "index").strip().lower()
            if col_name:
                try:
                    if idx_type == "unique":
                        idx_name = f"uniq_{selected_table}_{col_name}"
                        cur.execute(f'CREATE UNIQUE INDEX IF NOT EXISTS "{idx_name}" ON "{selected_table}" ("{col_name}")')
                        msg = f'UNIQUE index on column "{col_name}" was created successfully.'
                    else:
                        idx_name = f"idx_{selected_table}_{col_name}"
                        cur.execute(f'CREATE INDEX IF NOT EXISTS "{idx_name}" ON "{selected_table}" ("{col_name}")')
                        msg = f'INDEX on column "{col_name}" was created successfully.'
                    conn.commit()
                    return redirect_response(selected_table, "schema", msg=msg)
                except Exception as exc:
                    return redirect_response(selected_table, "schema", err=f"Index creation error: {exc}")
            else:
                return redirect_response(selected_table, "schema", err="Column name is missing.")

        # -------------------------------------------------------------
        # Action Handler: Drop Index
        # -------------------------------------------------------------
        elif action == "drop_index" and selected_table:
            idx_name = query_params.get("index_name", "").strip()
            if idx_name:
                try:
                    cur.execute(f'DROP INDEX IF EXISTS "{idx_name}"')
                    conn.commit()
                    return redirect_response(selected_table, "schema", msg=f'Index "{idx_name}" was dropped successfully.')
                except Exception as exc:
                    return redirect_response(selected_table, "schema", err=f"Drop index error: {exc}")
            else:
                return redirect_response(selected_table, "schema", err="Index name is missing.")

        # -------------------------------------------------------------
        # Get List of All Tables
        # -------------------------------------------------------------
        try:
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
            tables = [row["name"] for row in cur.fetchall()]
        except Exception:
            tables = []

        if not selected_table and tables and action not in ("create_table", "sql"):
            selected_table = tables[0]

        table_counts: dict[str, int] = {}
        for t in tables:
            try:
                cur.execute(f'SELECT COUNT(*) AS cnt FROM "{t}"')
                table_counts[t] = cur.fetchone()["cnt"]
            except Exception:
                table_counts[t] = 0

        # -------------------------------------------------------------
        # Action Handler: Export CSV
        # -------------------------------------------------------------
        if action == "export_csv" and selected_table:
            try:
                cur.execute(f'SELECT * FROM "{selected_table}" LIMIT 5000')
                rows = cur.fetchall()
                if rows:
                    headers = [d[0] for d in cur.description]
                    output = io.StringIO()
                    writer = csv.writer(output)
                    writer.writerow(headers)
                    for r in rows:
                        writer.writerow([r[h] for h in headers])
                    csv_content = output.getvalue()
                    conn.close()
                    return Response(
                        csv_content,
                        media_type="text/csv",
                        headers={"Content-Disposition": f'attachment; filename="{selected_table}.csv"'},
                    )
            except Exception as exc:
                flash_error = f"Export error: {exc}"

        # -------------------------------------------------------------
        # Schema Columns & Existing Indexes for Selected Table
        # -------------------------------------------------------------
        schema_cols: list[dict[str, Any]] = []
        table_indexes: list[dict[str, Any]] = []
        col_index_status: dict[str, list[str]] = {}
        if selected_table:
            try:
                cur.execute(f'PRAGMA table_info("{selected_table}")')
                schema_cols = [dict(c) for c in cur.fetchall()]
            except Exception:
                schema_cols = []

            try:
                cur.execute(f'PRAGMA index_list("{selected_table}")')
                raw_indexes = cur.fetchall()
                for idx_row in raw_indexes:
                    idx_name = idx_row["name"]
                    is_unique = bool(idx_row["unique"])
                    origin = idx_row["origin"] if "origin" in idx_row.keys() else ""
                    cur.execute(f'PRAGMA index_info("{idx_name}")')
                    cols = [c_info["name"] for c_info in cur.fetchall()]
                    is_pk = (origin == "pk" or idx_name.startswith("sqlite_autoindex_"))
                    table_indexes.append({
                        "name": idx_name,
                        "unique": is_unique,
                        "origin": origin,
                        "columns": cols,
                        "is_pk": is_pk,
                    })
            except Exception:
                table_indexes = []

            for c in schema_cols:
                cname = c["name"]
                statuses = []
                if c.get("pk"):
                    statuses.append("PRIMARY KEY")
                for idx_entry in table_indexes:
                    if cname in idx_entry["columns"] and not idx_entry["is_pk"]:
                        if idx_entry["unique"] and "UNIQUE" not in statuses:
                            statuses.append("UNIQUE")
                        elif not idx_entry["unique"] and "INDEX" not in statuses:
                            statuses.append("INDEX")
                col_index_status[cname] = statuses

        # -------------------------------------------------------------
        # Action Handler: Edit Record Pre-fetch
        # -------------------------------------------------------------
        edit_row_data: dict[str, Any] | None = None
        if action == "edit" and selected_table:
            rowid = query_params.get("rowid")
            if rowid is not None:
                try:
                    cur.execute(f'SELECT rowid AS _adminer_rowid_, * FROM "{selected_table}" WHERE rowid = ?', (rowid,))
                    row_obj = cur.fetchone()
                    if row_obj:
                        edit_row_data = dict(row_obj)
                    else:
                        flash_error = f"Record (rowid {rowid}) not found."
                        action = ""
                except Exception as exc:
                    flash_error = f"Fetch error: {exc}"
                    action = ""

        # -------------------------------------------------------------
        # Query / Browse Data (Strict 100 Rows Limit)
        # Using `_adminer_rowid_` as distinct alias to prevent duplicate column names!
        # -------------------------------------------------------------
        query_result_headers: list[str] = []
        query_result_rows: list[list[Any]] = []
        exec_error: str | None = None
        exec_message: str | None = None
        exec_time: float = 0.0
        total_rows = 0

        if custom_sql or action == "sql":
            if custom_sql:
                start_t = time.perf_counter()
                try:
                    cur.execute(custom_sql)
                    exec_time = round(time.perf_counter() - start_t, 4)
                    if cur.description:
                        query_result_headers = [d[0] for d in cur.description]
                        query_result_rows = [[cell for cell in row] for row in cur.fetchmany(cls.PAGE_SIZE)]
                        exec_message = f"Query executed in {exec_time}s ({len(query_result_rows)} rows returned, max {cls.PAGE_SIZE})"
                    else:
                        conn.commit()
                        exec_message = f"Query executed successfully in {exec_time}s ({cur.rowcount} rows affected)"
                except Exception as exc:
                    exec_error = str(exc)
        elif selected_table and action not in ("insert", "edit", "schema", "edit_column", "create_table"):
            start_t = time.perf_counter()
            try:
                offset = (page - 1) * per_page
                if search_query:
                    search_cols = [c["name"] for c in schema_cols]
                    if search_cols:
                        where_clauses = [f'CAST("{c}" AS TEXT) LIKE ?' for c in search_cols]
                        where_sql = " OR ".join(where_clauses)
                        search_params = [f"%{search_query}%"] * len(search_cols)

                        cur.execute(f'SELECT COUNT(*) AS cnt FROM "{selected_table}" WHERE {where_sql}', search_params)
                        total_rows = cur.fetchone()["cnt"]

                        search_sql = f'SELECT rowid AS _adminer_rowid_, * FROM "{selected_table}" WHERE {where_sql} LIMIT {per_page} OFFSET {offset}'
                        cur.execute(search_sql, search_params)
                    else:
                        cur.execute(f'SELECT rowid AS _adminer_rowid_, * FROM "{selected_table}" LIMIT {per_page} OFFSET {offset}')
                else:
                    total_rows = table_counts.get(selected_table, 0)
                    cur.execute(f'SELECT rowid AS _adminer_rowid_, * FROM "{selected_table}" LIMIT {per_page} OFFSET {offset}')

                exec_time = round(time.perf_counter() - start_t, 4)
                if cur.description:
                    query_result_headers = [d[0] for d in cur.description]
                    query_result_rows = [[cell for cell in row] for row in cur.fetchall()]

                row_start = offset + 1 if query_result_rows else 0
                row_end = offset + len(query_result_rows)
                if search_query:
                    exec_message = f'Search "{search_query}": showing {row_start}-{row_end} of {total_rows} matches ({exec_time}s)'
            except Exception as exc:
                exec_error = str(exc)

        conn.close()

        # Database File Stats
        file_size_bytes = resolved_path.stat().st_size if resolved_path.exists() else 0
        if file_size_bytes > 1024 * 1024:
            size_str = f"{file_size_bytes / (1024 * 1024):.2f} MB"
        elif file_size_bytes > 1024:
            size_str = f"{file_size_bytes / 1024:.2f} KB"
        else:
            size_str = f"{file_size_bytes} B"

        html_content = cls._render_adminer_ui(
            db_name=resolved_path.name,
            db_path=str(resolved_path),
            size_str=size_str,
            tables=tables,
            table_counts=table_counts,
            selected_table=selected_table,
            custom_sql=custom_sql,
            search_query=search_query,
            headers=query_result_headers,
            rows=query_result_rows,
            schema_cols=schema_cols,
            table_indexes=table_indexes,
            col_index_status=col_index_status,
            exec_error=exec_error,
            exec_message=exec_message,
            flash_msg=flash_msg,
            flash_error=flash_error,
            page=page,
            per_page=per_page,
            total_rows=total_rows,
            base_url=base_url,
            action=action,
            edit_row_data=edit_row_data,
            query_params=query_params,
        )

        return HTMLResponse(html_content)

    @classmethod
    def _render_error(cls, title: str, details: str) -> str:
        return f"""<!DOCTYPE html>
<html>
<head><title>{html.escape(title)}</title>
<style>{ADMINER_CSS}</style>
</head>
<body>
<div id="content" style="margin-inline-start: 20px;">
  <div class="error">
    <h2>{html.escape(title)}</h2>
    <p>{html.escape(details)}</p>
  </div>
</div>
</body></html>"""

    @classmethod
    def _render_adminer_ui(
        cls,
        db_name: str,
        db_path: str,
        size_str: str,
        tables: list[str],
        table_counts: dict[str, int],
        selected_table: str | None,
        custom_sql: str,
        search_query: str,
        headers: list[str],
        rows: list[list[Any]],
        schema_cols: list[dict[str, Any]],
        table_indexes: list[dict[str, Any]],
        col_index_status: dict[str, list[str]],
        exec_error: str | None,
        exec_message: str | None,
        flash_msg: str | None,
        flash_error: str | None,
        page: int,
        per_page: int,
        total_rows: int,
        base_url: str,
        action: str,
        edit_row_data: dict[str, Any] | None,
        query_params: dict[str, str],
    ) -> str:
        # -------------------------------------------------------------
        # Left Sidebar (#menu) matching Adminer
        # -------------------------------------------------------------
        tables_list_html = ""
        for t in tables:
            active_style = "font-weight:bold;" if t == selected_table and action not in ("create_table", "sql") else ""
            cnt = table_counts.get(t, 0)
            tables_list_html += f"""
            <li>
                <a href="{base_url}?table={html.escape(t)}" class="select">select</a>
                <a href="{base_url}?table={html.escape(t)}" style="{active_style}">{html.escape(t)}</a>
                <span class="count">({cnt:,})</span>
            </li>"""

        menu_html = f"""
        <div id="menu">
            <h1><a href="{base_url}">Adminer</a> <span class="version">SQLite 3</span></h1>
            <p class="links">
                <a href="{base_url}?action=sql">SQL command</a><br>
                <a href="{base_url}?action=create_table">Create table</a><br>
                {f'<a href="{base_url}?table={html.escape(selected_table)}&action=export_csv">Export CSV</a><br>' if selected_table else ''}
            </p>
            <p id="tables">
                <span><b>Tables ({len(tables)})</b></span>
                <ul style="padding-left:0;margin:6px 0;">
                    {tables_list_html if tables else '<li style="color:#777;">No tables</li>'}
                </ul>
            </p>
            <p style="padding:.8em 1em;font-size:80%;color:#777;border-bottom:1px solid #ccc;">
                <b>File:</b> {html.escape(db_name)}<br>
                <b>Size:</b> {html.escape(size_str)}<br>
                <span title="{html.escape(db_path)}" style="word-break:break-all;"><b>Path:</b> {html.escape(db_path)}</span>
            </p>
        </div>"""

        # -------------------------------------------------------------
        # Breadcrumbs (#breadcrumb) matching Adminer
        # -------------------------------------------------------------
        breadcrumb_items = [f'<a href="{base_url}">SQLite 3</a>', f'<b>{html.escape(db_name)}</b>']
        if selected_table:
            breadcrumb_items.append(f'Table: <a href="{base_url}?table={html.escape(selected_table)}"><b>{html.escape(selected_table)}</b></a>')
        if action == "insert":
            breadcrumb_items.append("New item")
        elif action == "edit":
            breadcrumb_items.append("Edit item")
        elif action in ("schema", "edit_column"):
            breadcrumb_items.append("Table structure")
        elif action == "create_table":
            breadcrumb_items.append("Create table")
        elif action == "sql":
            breadcrumb_items.append("SQL command")

        breadcrumb_html = f'<div id="breadcrumb">{" » ".join(breadcrumb_items)}</div>'

        # -------------------------------------------------------------
        # Alerts (.message / .error) matching Adminer
        # -------------------------------------------------------------
        messages_html = ""
        js_alert_html = ""
        clean_url_script = ""
        if flash_msg or flash_error:
            clean_url_script = f"""
            <script>
            if (window.history && window.history.replaceState) {{
                var cleanPath = window.location.pathname + (window.location.search ? window.location.search.replace(/[?&]flash_msg=[^&]*/g, '').replace(/[?&]flash_error=[^&]*/g, '').replace(/^[?&]/, '?') : '');
                if (cleanPath === window.location.pathname + '?' || cleanPath === window.location.pathname + '&') {{
                    cleanPath = window.location.pathname;
                }}
                window.history.replaceState(null, document.title, cleanPath);
            }}
            </script>"""

        if flash_error:
            messages_html += f'<div class="error">{html.escape(flash_error)}</div>'
            js_alert_html = f"""
            <div id="modal-alert-box" style="position:fixed; top:30px; left:50%; transform:translateX(-50%); background:#fef2f2; border:2px solid #ef4444; color:#991b1b; padding:12px 20px; border-radius:8px; box-shadow:0 10px 30px rgba(0,0,0,0.3); z-index:999999; display:flex; align-items:center; gap:16px; font-family:Verdana,sans-serif; font-size:13px;">
                <span>❌ <b>{html.escape(flash_error)}</b></span>
                <button type="button" onclick="document.getElementById('modal-alert-box').remove();" style="background:#dc2626; color:#fff; border:none; padding:4px 14px; border-radius:4px; font-weight:bold; cursor:pointer;">OK</button>
            </div>
            {clean_url_script}
            """
        elif flash_msg:
            messages_html += f'<div class="message">{html.escape(flash_msg)}</div>'
            js_alert_html = f"""
            <div id="modal-alert-box" style="position:fixed; top:30px; left:50%; transform:translateX(-50%); background:#ecfdf5; border:2px solid #10b981; color:#065f46; padding:12px 20px; border-radius:8px; box-shadow:0 10px 30px rgba(0,0,0,0.3); z-index:999999; display:flex; align-items:center; gap:16px; font-family:Verdana,sans-serif; font-size:13px;">
                <span>✅ <b>{html.escape(flash_msg)}</b></span>
                <button type="button" onclick="document.getElementById('modal-alert-box').remove();" style="background:#059669; color:#fff; border:none; padding:4px 14px; border-radius:4px; font-weight:bold; cursor:pointer;">OK</button>
            </div>
            {clean_url_script}
            """

        if exec_error and exec_error != flash_error:
            messages_html += f'<div class="error">{html.escape(exec_error)}</div>'
        if exec_message and exec_message != flash_msg:
            messages_html += f'<div class="message">{html.escape(exec_message)}</div>'

        # -------------------------------------------------------------
        # Content Area (#content) matching Adminer
        # -------------------------------------------------------------
        content_inner = ""

        # --- View: SQL Command ---
        if action == "sql" or (custom_sql and not selected_table):
            result_table_html = ""
            if query_result_headers and query_result_rows:
                th_html = "".join([f"<th>{html.escape(h)}</th>" for h in query_result_headers])
                tr_html = ""
                for r in query_result_rows:
                    tr_html += "<tr>" + "".join([f"<td>{html.escape(str(cell) if cell is not None else '')}</td>" for cell in r]) + "</tr>"
                result_table_html = f"""
                <table class="checkable odds">
                    <thead><tr>{th_html}</tr></thead>
                    <tbody>{tr_html}</tbody>
                </table>"""

            content_inner = f"""
            <h2>SQL command</h2>
            <form action="{base_url}" method="GET">
                <input type="hidden" name="action" value="sql">
                {f'<input type="hidden" name="table" value="{html.escape(selected_table)}">' if selected_table else ''}
                <p><textarea name="sql" class="sqlarea" rows="8" style="width:100%;font-family:monospace;">{html.escape(custom_sql or "SELECT * FROM ... LIMIT 100;")}</textarea></p>
                <p><input type="submit" value="Execute"> <span style="color:#777;font-size:80%;">Supports SELECT, INSERT, UPDATE, DELETE, CREATE, DROP</span></p>
            </form>
            {result_table_html}"""

        # --- View: Create Table ---
        elif action == "create_table":
            content_inner = f"""
            <h2>Create table</h2>
            <form action="{base_url}" method="GET">
                <input type="hidden" name="action" value="do_create_table">
                <p>Table name: <input type="text" name="new_table_name" required style="width:250px;"></p>
                <table class="layout" id="create-table-cols">
                    <thead>
                        <tr>
                            <th>Column name</th>
                            <th>Type</th>
                            <th>Primary Key (AI)</th>
                            <th>Not Null</th>
                            <th>Default value</th>
                            <th>Unique</th>
                            <th>Index</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><input type="text" name="cname_0" value="id" required></td>
                            <td>
                                <select name="ctype_0">
                                    <option value="INTEGER" selected>INTEGER</option>
                                    <option value="TEXT">TEXT</option>
                                    <option value="REAL">REAL</option>
                                    <option value="BLOB">BLOB</option>
                                </select>
                            </td>
                            <td><input type="checkbox" name="cpk_0" value="1" checked></td>
                            <td><input type="checkbox" name="cnn_0" value="1"></td>
                            <td><input type="text" name="cdflt_0" placeholder="NULL"></td>
                            <td><input type="checkbox" name="cuniq_0" value="1"></td>
                            <td><input type="checkbox" name="cidx_0" value="1"></td>
                        </tr>
                        <tr>
                            <td><input type="text" name="cname_1" placeholder="name"></td>
                            <td>
                                <select name="ctype_1">
                                    <option value="TEXT" selected>TEXT</option>
                                    <option value="INTEGER">INTEGER</option>
                                    <option value="REAL">REAL</option>
                                    <option value="BLOB">BLOB</option>
                                </select>
                            </td>
                            <td><input type="checkbox" name="cpk_1" value="1"></td>
                            <td><input type="checkbox" name="cnn_1" value="1"></td>
                            <td><input type="text" name="cdflt_1"></td>
                            <td><input type="checkbox" name="cuniq_1" value="1"></td>
                            <td><input type="checkbox" name="cidx_1" value="1"></td>
                        </tr>
                        <tr>
                            <td><input type="text" name="cname_2" placeholder="created_at"></td>
                            <td>
                                <select name="ctype_2">
                                    <option value="TEXT" selected>TEXT</option>
                                    <option value="INTEGER">INTEGER</option>
                                    <option value="REAL">REAL</option>
                                    <option value="BLOB">BLOB</option>
                                </select>
                            </td>
                            <td><input type="checkbox" name="cpk_2" value="1"></td>
                            <td><input type="checkbox" name="cnn_2" value="1"></td>
                            <td><input type="text" name="cdflt_2" placeholder="CURRENT_TIMESTAMP"></td>
                            <td><input type="checkbox" name="cuniq_2" value="1"></td>
                            <td><input type="checkbox" name="cidx_2" value="1"></td>
                        </tr>
                    </tbody>
                </table>
                <p>
                    <input type="submit" value="Save">
                    <button type="button" onclick="addColRow()">+ Add column</button>
                    <a href="{base_url}{('?table=' + html.escape(selected_table)) if selected_table else ''}">Cancel</a>
                </p>
            </form>
            <script>
            let colIdx = 3;
            function addColRow() {{
                const tbody = document.querySelector('#create-table-cols tbody');
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><input type="text" name="cname_${{colIdx}}"></td>
                    <td>
                        <select name="ctype_${{colIdx}}">
                            <option value="TEXT" selected>TEXT</option>
                            <option value="INTEGER">INTEGER</option>
                            <option value="REAL">REAL</option>
                            <option value="BLOB">BLOB</option>
                        </select>
                    </td>
                    <td><input type="checkbox" name="cpk_${{colIdx}}" value="1"></td>
                    <td><input type="checkbox" name="cnn_${{colIdx}}" value="1"></td>
                    <td><input type="text" name="cdflt_${{colIdx}}"></td>
                    <td><input type="checkbox" name="cuniq_${{colIdx}}" value="1"></td>
                    <td><input type="checkbox" name="cidx_${{colIdx}}" value="1"></td>
                `;
                tbody.appendChild(tr);
                colIdx++;
            }}
            </script>"""

        # --- View: Edit Column Form (phpMyAdmin style Schema Edit) ---
        elif action == "edit_column" and selected_table:
            target_col_name = query_params.get("col", "").strip()
            matched_col = next((c for c in schema_cols if c["name"] == target_col_name), None)
            if not matched_col:
                matched_col = {"name": target_col_name, "type": "TEXT", "notnull": 0, "dflt_value": ""}

            c_type = (matched_col.get("type") or "TEXT").upper()
            c_notnull = matched_col.get("notnull", 0)
            c_dflt = str(matched_col.get("dflt_value") or "")

            cur_idx_status = col_index_status.get(target_col_name, [])
            cur_is_uniq = "UNIQUE" in cur_idx_status
            cur_is_idx = "INDEX" in cur_idx_status

            content_inner = f"""
            <h2>Change Column: {html.escape(target_col_name)} in {html.escape(selected_table)}</h2>
            <p class="links">
                <a href="{base_url}?table={html.escape(selected_table)}">Select data</a>
                <a href="{base_url}?table={html.escape(selected_table)}&action=insert">New item</a>
                <a href="{base_url}?table={html.escape(selected_table)}&action=schema" style="font-weight:bold;">Table structure</a>
                <a href="{base_url}?table={html.escape(selected_table)}&action=export_csv">Export CSV</a>
                <a href="{base_url}?action=drop_table&table={html.escape(selected_table)}" onclick="return confirm('Drop table {html.escape(selected_table)}?')">Drop table</a>
            </p>
            <form action="{base_url}" method="GET" onsubmit="return confirm('Are you sure you want to save changes to column \'{html.escape(target_col_name)}\'?');">
                <input type="hidden" name="action" value="do_edit_column">
                <input type="hidden" name="table" value="{html.escape(selected_table)}">
                <input type="hidden" name="old_col_name" value="{html.escape(target_col_name)}">
                <table class="layout">
                    <thead><tr><th>Column name</th><th>Type</th><th>Not Null</th><th>Default value</th><th>Index / Unique</th></tr></thead>
                    <tbody>
                        <tr>
                            <td><input type="text" name="new_col_name" value="{html.escape(target_col_name)}" required style="width:200px;"></td>
                            <td>
                                <select name="new_col_type">
                                    <option value="TEXT" {'selected' if c_type == 'TEXT' else ''}>TEXT</option>
                                    <option value="INTEGER" {'selected' if c_type == 'INTEGER' else ''}>INTEGER</option>
                                    <option value="REAL" {'selected' if c_type == 'REAL' else ''}>REAL</option>
                                    <option value="BLOB" {'selected' if c_type == 'BLOB' else ''}>BLOB</option>
                                    <option value="NUMERIC" {'selected' if c_type == 'NUMERIC' else ''}>NUMERIC</option>
                                </select>
                            </td>
                            <td><input type="checkbox" name="new_col_notnull" value="1" {'checked' if c_notnull else ''}></td>
                            <td><input type="text" name="new_col_default" value="{html.escape(c_dflt)}" placeholder="Default value"></td>
                            <td>
                                <div style="display:inline-flex;align-items:center;gap:6px;background:#f3f4f6;padding:3px 8px;border-radius:4px;border:1px solid #d1d5db;">
                                    <label style="cursor:pointer;"><input type="radio" name="edit_col_index" value="" {'checked' if not (cur_is_uniq or cur_is_idx) else ''}> None</label>
                                    <label style="cursor:pointer;color:#7c3aed;font-weight:bold;"><input type="radio" name="edit_col_index" value="UNIQUE" {'checked' if cur_is_uniq else ''}> 🔑 Unique</label>
                                    <label style="cursor:pointer;color:#0284c7;font-weight:bold;"><input type="radio" name="edit_col_index" value="INDEX" {'checked' if cur_is_idx else ''}> ⚡ Index</label>
                                </div>
                            </td>
                        </tr>
                    </tbody>
                </table>
                <p>
                    <input type="submit" value="Save Column Changes">
                    <a href="{base_url}?table={html.escape(selected_table)}&action=schema">Cancel</a>
                </p>
            </form>"""

        # --- View: Table Structure / Schema (phpMyAdmin style with Edit & Drop & Add Column & Index/Unique) ---
        elif action == "schema" and selected_table:
            schema_rows_html = ""
            for idx, col in enumerate(schema_cols, start=1):
                cname = col["name"]
                statuses = col_index_status.get(cname, [])
                extra_badges = ""
                if "PRIMARY KEY" in statuses or col["pk"]:
                    extra_badges += '<span class="badge-pk">PRIMARY KEY</span> '
                if "UNIQUE" in statuses:
                    extra_badges += '<span class="badge-uniq">UNIQUE</span> '
                if "INDEX" in statuses:
                    extra_badges += '<span class="badge-idx">INDEX</span> '

                notnull_badge = "NOT NULL" if col["notnull"] else "NULL"
                schema_rows_html += f"""<tr>
                    <td style="text-align:center;color:#777;">{idx}</td>
                    <td><b>{html.escape(cname)}</b></td>
                    <td><code>{html.escape(col["type"] or "ANY")}</code></td>
                    <td>{notnull_badge}</td>
                    <td>{html.escape(str(col["dflt_value"] if col["dflt_value"] is not None else ""))}</td>
                    <td>{extra_badges}</td>
                    <td style="white-space:nowrap;">
                        <a href="{base_url}?table={html.escape(selected_table)}&action=edit_column&col={html.escape(cname)}" class="act-btn act-edit" title="Change / Edit Column">✏️ Change</a>
                        <a href="{base_url}?table={html.escape(selected_table)}&action=drop_column&col={html.escape(cname)}" class="act-btn act-del" title="Drop Column" onclick="return confirm('Do you really want to DROP column \"{html.escape(cname)}\"? This cannot be undone!')">🗑️ Drop</a>
                        <a href="{base_url}?table={html.escape(selected_table)}&action=add_index&type=unique&col={html.escape(cname)}" class="act-btn act-uniq" title="Create UNIQUE Index on {html.escape(cname)}" onclick="return confirm('Create UNIQUE index on column \'{html.escape(cname)}\'?');">🔑 Unique</a>
                        <a href="{base_url}?table={html.escape(selected_table)}&action=add_index&type=index&col={html.escape(cname)}" class="act-btn act-idx" title="Create INDEX on {html.escape(cname)}" onclick="return confirm('Create INDEX on column \'{html.escape(cname)}\'?');">⚡ Index</a>
                    </td>
                </tr>"""

            # Indexes List Section (phpMyAdmin style)
            index_rows_html = ""
            for i_idx, t_idx in enumerate(table_indexes, start=1):
                type_badge = '<span class="badge-pk">PRIMARY KEY</span>' if t_idx["is_pk"] else ('<span class="badge-uniq">UNIQUE</span>' if t_idx["unique"] else '<span class="badge-idx">INDEX</span>')
                cols_str = ", ".join(t_idx["columns"])
                drop_btn = ""
                if not t_idx["is_pk"]:
                    drop_btn = f'<a href="{base_url}?table={html.escape(selected_table)}&action=drop_index&index_name={html.escape(t_idx["name"])}" class="act-btn act-del" title="Drop Index" onclick="return confirm(\'Do you really want to DROP index \"{html.escape(t_idx["name"])}\"?\');">🗑️ Drop</a>'
                else:
                    drop_btn = '<span style="color:#888;font-size:11px;">(Auto PK)</span>'
                index_rows_html += f"""<tr>
                    <td style="text-align:center;color:#777;">{i_idx}</td>
                    <td><code>{html.escape(t_idx["name"])}</code></td>
                    <td>{type_badge}</td>
                    <td><b>{html.escape(cols_str)}</b></td>
                    <td style="white-space:nowrap;">{drop_btn}</td>
                </tr>"""

            indexes_table_html = f"""
            <fieldset style="margin-top:20px;padding:12px 16px;">
                <legend><b>📑 Indexes on Table ({html.escape(selected_table)}) ({len(table_indexes)})</b></legend>
                <table class="checkable odds" style="margin-top:8px;">
                    <thead>
                        <tr>
                            <th style="width:30px;">#</th>
                            <th>Index Name</th>
                            <th>Type</th>
                            <th>Column(s)</th>
                            <th style="width:100px;">Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        {index_rows_html if index_rows_html else '<tr><td colspan="5" style="text-align:center;color:#777;">No indexes found</td></tr>'}
                    </tbody>
                </table>
            </fieldset>"""

            content_inner = f"""
            <h2>Structure: {html.escape(selected_table)}</h2>
            <p class="links">
                <a href="{base_url}?table={html.escape(selected_table)}">Select data</a>
                <a href="{base_url}?table={html.escape(selected_table)}&action=insert">New item</a>
                <a href="{base_url}?table={html.escape(selected_table)}&action=schema" style="font-weight:bold;">Table structure</a>
                <a href="{base_url}?table={html.escape(selected_table)}&action=export_csv">Export CSV</a>
                <a href="{base_url}?action=drop_table&table={html.escape(selected_table)}" onclick="return confirm('Drop table {html.escape(selected_table)}?')">Drop table</a>
            </p>
            <table class="checkable odds">
                <thead>
                    <tr>
                        <th style="width:30px;">#</th>
                        <th>Column</th>
                        <th>Type</th>
                        <th>Null</th>
                        <th>Default</th>
                        <th>Extra</th>
                        <th style="width:260px;">Action</th>
                    </tr>
                </thead>
                <tbody>{schema_rows_html}</tbody>
            </table>
            
            <fieldset style="margin-top:20px;padding:12px 16px;">
                <legend><b>➕ Add New Column to Table ({html.escape(selected_table)})</b></legend>
                <form action="{base_url}" method="GET" onsubmit="return confirm('Are you sure you want to add this column?');" style="display:flex;align-items:center;gap:12px;flex-wrap:wrap;">
                    <input type="hidden" name="action" value="do_add_column">
                    <input type="hidden" name="table" value="{html.escape(selected_table)}">
                    <label>Column Name: <input type="text" name="add_col_name" required placeholder="e.g. status, phone"></label>
                    <label>Type: 
                        <select name="add_col_type">
                            <option value="TEXT" selected>TEXT</option>
                            <option value="INTEGER">INTEGER</option>
                            <option value="REAL">REAL</option>
                            <option value="BLOB">BLOB</option>
                            <option value="NUMERIC">NUMERIC</option>
                        </select>
                    </label>
                    <label>Default: <input type="text" name="add_col_default" placeholder="Optional default"></label>
                    <label><input type="checkbox" name="add_col_notnull" value="1"> Not Null</label>
                    <div style="display:inline-flex;align-items:center;gap:8px;background:#f3f4f6;padding:4px 10px;border-radius:4px;border:1px solid #d1d5db;">
                        <span style="font-weight:bold;font-size:12px;">Index / Unique:</span>
                        <label style="cursor:pointer;"><input type="radio" name="add_col_index" value="" checked> None</label>
                        <label style="cursor:pointer;color:#7c3aed;font-weight:bold;"><input type="radio" name="add_col_index" value="UNIQUE"> 🔑 Unique</label>
                        <label style="cursor:pointer;color:#0284c7;font-weight:bold;"><input type="radio" name="add_col_index" value="INDEX"> ⚡ Index</label>
                    </div>
                    <input type="submit" value="Add Column">
                </form>
            </fieldset>
            {indexes_table_html}"""

        # --- View: New Item (Insert) ---
        elif action == "insert" and selected_table:
            form_fields_html = ""
            for col in schema_cols:
                cname = col["name"]
                ctype = col["type"] or "TEXT"
                is_pk = col["pk"]
                placeholder = "(Auto Increment)" if is_pk else ""
                form_fields_html += f"""<tr>
                    <th>{html.escape(cname)}</th>
                    <td>{html.escape(ctype)}</td>
                    <td><textarea name="col_{html.escape(cname)}" placeholder="{placeholder}" rows="2" style="width:400px;"></textarea></td>
                </tr>"""

            content_inner = f"""
            <h2>New item: {html.escape(selected_table)}</h2>
            <p class="links">
                <a href="{base_url}?table={html.escape(selected_table)}">Select data</a>
                <a href="{base_url}?table={html.escape(selected_table)}&action=insert" style="font-weight:bold;">New item</a>
                <a href="{base_url}?table={html.escape(selected_table)}&action=schema">Table structure</a>
                <a href="{base_url}?table={html.escape(selected_table)}&action=export_csv">Export CSV</a>
                <a href="{base_url}?action=drop_table&table={html.escape(selected_table)}" onclick="return confirm('Drop table {html.escape(selected_table)}?')">Drop table</a>
            </p>
            <form action="{base_url}" method="GET" onsubmit="return confirm('Are you sure you want to save this new record?');">
                <input type="hidden" name="action" value="do_insert">
                <input type="hidden" name="table" value="{html.escape(selected_table)}">
                <table class="layout">
                    <thead><tr><th>Column</th><th>Type</th><th>Value</th></tr></thead>
                    <tbody>{form_fields_html}</tbody>
                </table>
                <p>
                    <input type="submit" value="Save">
                    <a href="{base_url}?table={html.escape(selected_table)}">Cancel</a>
                </p>
            </form>"""

        # --- View: Edit Item ---
        elif action == "edit" and selected_table and edit_row_data:
            raw_rowid = query_params.get("rowid")
            if raw_rowid and str(raw_rowid).strip() != "None":
                rowid = str(raw_rowid)
            else:
                rowid = str(edit_row_data.get("_adminer_rowid_") or "")
                if not rowid or rowid == "None":
                    for c in schema_cols:
                        if c.get("pk") and c["name"] in edit_row_data:
                            rowid = str(edit_row_data[c["name"]])
                            break
            if not rowid or rowid == "None":
                rowid = str(edit_row_data.get("id") or "")
            form_fields_html = ""
            for col in schema_cols:
                cname = col["name"]
                ctype = col["type"] or "TEXT"
                is_pk = col.get("pk", 0)
                cur_val = edit_row_data.get(cname, "")
                val_str = "" if cur_val is None else str(cur_val)
                if is_pk:
                    form_fields_html += f"""<tr>
                        <th>{html.escape(cname)} <span style="font-size:10px;color:#d97706;font-weight:bold;">[PK]</span></th>
                        <td>{html.escape(ctype)}</td>
                        <td><input type="text" name="col_{html.escape(cname)}" value="{html.escape(val_str)}" readonly style="width:400px;background:#f3f4f6;color:#6b7280;cursor:not-allowed;padding:4px 8px;border:1px solid #ccc;"></td>
                    </tr>"""
                else:
                    form_fields_html += f"""<tr>
                        <th>{html.escape(cname)}</th>
                        <td>{html.escape(ctype)}</td>
                        <td><textarea name="col_{html.escape(cname)}" rows="2" style="width:400px;">{html.escape(val_str)}</textarea></td>
                    </tr>"""

            content_inner = f"""
            <h2>Edit item (rowid: {rowid}): {html.escape(selected_table)}</h2>
            <p class="links">
                <a href="{base_url}?table={html.escape(selected_table)}">Select data</a>
                <a href="{base_url}?table={html.escape(selected_table)}&action=insert">New item</a>
                <a href="{base_url}?table={html.escape(selected_table)}&action=schema">Table structure</a>
                <a href="{base_url}?table={html.escape(selected_table)}&action=export_csv">Export CSV</a>
                <a href="{base_url}?action=drop_table&table={html.escape(selected_table)}" onclick="return confirm('Drop table {html.escape(selected_table)}?')">Drop table</a>
            </p>
            <form action="{base_url}" method="GET" onsubmit="return confirm('Are you sure you want to save changes to this record (rowid {rowid})?');">
                <input type="hidden" name="action" value="do_update">
                <input type="hidden" name="table" value="{html.escape(selected_table)}">
                <input type="hidden" name="rowid" value="{rowid}">
                <table class="layout">
                    <thead><tr><th>Column</th><th>Type</th><th>Value</th></tr></thead>
                    <tbody>{form_fields_html}</tbody>
                </table>
                <p>
                    <input type="submit" value="Save">
                    <a href="{base_url}?table={html.escape(selected_table)}">Cancel</a>
                </p>
            </form>"""

        # --- View: Select Data (Browse with strict 100 limit & Edit/Delete Icons) ---
        elif selected_table:
            total_pages = max(1, (total_rows + per_page - 1) // per_page)
            prev_page = page - 1 if page > 1 else 1
            next_page = page + 1 if page < total_pages else total_pages
            q_param = f"&q={html.escape(search_query)}" if search_query else ""
            offset = (page - 1) * per_page
            row_start = offset + 1 if rows else 0
            row_end = offset + len(rows)

            # Check if rowid is available in query results
            has_rowid = "_adminer_rowid_" in headers
            rowid_idx = headers.index("_adminer_rowid_") if has_rowid else -1

            table_rows_html = ""
            for row in rows:
                table_rows_html += "<tr>"
                row_rowid = row[rowid_idx] if rowid_idx != -1 else None

                # Actions column with explicit Edit & Delete icons
                if row_rowid is not None:
                    table_rows_html += f"""
                    <td style="white-space:nowrap;">
                        <a href="{base_url}?table={html.escape(selected_table)}&action=edit&rowid={row_rowid}" class="act-btn act-edit" title="Edit Record">✏️ Edit</a>
                        <a href="{base_url}?table={html.escape(selected_table)}&action=delete&rowid={row_rowid}" class="act-btn act-del" title="Delete Record" onclick="return confirm('Are you sure you want to delete record (rowid {row_rowid})?');">🗑️ Delete</a>
                    </td>"""

                for idx, cell in enumerate(row):
                    if idx == rowid_idx:
                        continue  # Skip internal rowid alias from data display!
                    if cell is None:
                        table_rows_html += '<td style="color:#777;font-style:italic;">NULL</td>'
                    else:
                        text = str(cell)
                        disp = text if len(text) <= 100 else text[:100] + "..."
                        table_rows_html += f'<td title="{html.escape(text)}">{html.escape(disp)}</td>'
                table_rows_html += "</tr>"

            header_cells = ""
            if has_rowid:
                header_cells += '<th style="width:140px;">Action</th>'
            for idx, h in enumerate(headers):
                if idx == rowid_idx:
                    continue  # Skip internal rowid alias header
                header_cells += f"<th>{html.escape(h)}</th>"

            content_inner = f"""
            <h2>Table: {html.escape(selected_table)}</h2>
            <p class="links">
                <a href="{base_url}?table={html.escape(selected_table)}" style="font-weight:bold;">Select data</a>
                <a href="{base_url}?table={html.escape(selected_table)}&action=insert">New item</a>
                <a href="{base_url}?table={html.escape(selected_table)}&action=schema">Table structure</a>
                <a href="{base_url}?table={html.escape(selected_table)}&action=export_csv">Export CSV</a>
                <a href="{base_url}?action=drop_table&table={html.escape(selected_table)}" onclick="return confirm('Drop table {html.escape(selected_table)}?')">Drop table</a>
            </p>
            <form action="{base_url}" method="GET">
                <input type="hidden" name="table" value="{html.escape(selected_table)}">
                <fieldset>
                    <legend>Search</legend>
                    <div>
                        <input type="search" name="q" placeholder="Search in table..." value="{html.escape(search_query)}" style="width:200px;">
                        <input type="submit" value="Search">
                        {f'<a href="{base_url}?table={html.escape(selected_table)}" style="margin-left:8px;">Reset</a>' if search_query else ''}
                    </div>
                </fieldset>
                <fieldset>
                    <legend>Limit (Strict 100 per page)</legend>
                    <div>
                        Showing <b>{row_start} - {row_end}</b> of <b>{total_rows:,}</b> items
                        {f' | <a href="{base_url}?table={html.escape(selected_table)}&page={prev_page}{q_param}">← Previous 100</a>' if page > 1 else ''}
                        {f' | <a href="{base_url}?table={html.escape(selected_table)}&page={next_page}{q_param}">Next 100 →</a>' if page < total_pages else ''}
                    </div>
                </fieldset>
            </form>
            <table class="checkable odds">
                <thead><tr>{header_cells}</tr></thead>
                <tbody>{table_rows_html if rows else '<tr><td colspan="' + str(max(1, len(headers))) + '" style="text-align:center;padding:1em;color:#777;">No data found</td></tr>'}</tbody>
            </table>
            {f'<p><a href="{base_url}?table={html.escape(selected_table)}&page={prev_page}{q_param}">← Previous 100</a> | <a href="{base_url}?table={html.escape(selected_table)}&page={next_page}{q_param}">Next 100 →</a></p>' if total_pages > 1 else ''}"""

        else:
            # Home view when no table is present
            content_inner = f"""
            <h2>Database: {html.escape(db_name)}</h2>
            <p>Select a table from the left menu or <a href="{base_url}?action=create_table">Create a new table</a>.</p>"""

        return f"""<!DOCTYPE html>
<html lang="en" dir="ltr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Adminer - {html.escape(db_name)}</title>
<style>{ADMINER_CSS}</style>
</head>
<body>
{breadcrumb_html}
<div id="content">
    {messages_html}
    {content_inner}
</div>
{menu_html}
{js_alert_html}
</body>
</html>"""


sqlite = SQLite
