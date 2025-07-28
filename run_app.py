#!/usr/bin/env python3
# run_app.py

import pathlib
import webbrowser
from threading import Timer
from datetime import date

from flask import (
    Flask, send_from_directory, jsonify,
    request, abort
)
import sqlite3

# --- CONFIGURACIÓN ---
ROOT = pathlib.Path(__file__).parent.resolve()
DB_PATH = ROOT / "config" / "data.cdb"
PORT = 5000

# --- APP SETUP ---
app = Flask(__name__, static_folder=str(ROOT), static_url_path="")

# ─────────────────────────── GRUPOS ───────────────────────────
@app.get("/api/grupos")
def list_grupos():
    rows = get_db().execute(
        "SELECT id, descripcion, activo FROM grupos ORDER BY descripcion"
    ).fetchall()
    return jsonify([dict(r) for r in rows])

@app.post("/api/grupos")
def add_grupo():
    nombre = (request.json or {}).get("descripcion", "").strip()
    if not nombre:
        return abort(400, "Falta la descripción del grupo")
    db = get_db()
    db.execute("INSERT INTO grupos (descripcion, activo) VALUES (?,1)", (nombre,))
    db.commit()
    return "", 204

@app.route("/api/grupos/<int:_id>", methods=["PUT"])
def update_grupo(_id):
    data   = request.json or {}
    nombre = data.get("descripcion", "").strip()
    activo = 1 if str(data.get("activo")).lower() in ("1","true","t","yes") else 0
    if not nombre:
        return abort(400, "Falta la descripción del grupo")
    db = get_db()
    db.execute(
        "UPDATE grupos SET descripcion = ?, activo = ? WHERE id = ?",
        (nombre, activo, _id)
    )
    db.commit()
    return "", 204


# ─────────────────────────── RUTAS ────────────────────────────
@app.get("/api/rutas")
def list_rutas():
    rows = get_db().execute(
        "SELECT id, descripcion, activo FROM rutas ORDER BY descripcion"
    ).fetchall()
    return jsonify([dict(r) for r in rows])

@app.post("/api/rutas")
def add_ruta():
    nombre = (request.json or {}).get("descripcion", "").strip()
    if not nombre:
        return abort(400, "Falta la descripción de la ruta")
    db = get_db()
    db.execute("INSERT INTO rutas (descripcion, activo) VALUES (?,1)", (nombre,))
    db.commit()
    return "", 204

@app.route("/api/rutas/<int:_id>", methods=["PUT"])
def update_ruta(_id):
    data   = request.json or {}
    nombre = data.get("descripcion", "").strip()
    activo = 1 if str(data.get("activo")).lower() in ("1","true","t","yes") else 0
    if not nombre:
        return abort(400, "Falta la descripción de la ruta")
    db = get_db()
    db.execute(
        "UPDATE rutas SET descripcion = ?, activo = ? WHERE id = ?",
        (nombre, activo, _id)
    )
    db.commit()
    return "", 204


# ─────────────────────────── TURNOS ───────────────────────────
@app.get("/api/turnos")
def list_turnos():
    rows = get_db().execute(
        "SELECT id, descripcion, activo FROM turnos ORDER BY id"
    ).fetchall()
    return jsonify([dict(r) for r in rows])

@app.post("/api/turnos")
def add_turno():
    desc = (request.json or {}).get("descripcion", "").strip()
    if not desc:
        return abort(400, "Falta la descripción del turno")
    db = get_db()
    db.execute("INSERT INTO turnos (descripcion, activo) VALUES (?,1)", (desc,))
    db.commit()
    return "", 204

@app.route("/api/turnos/<int:_id>", methods=["PUT"])
def update_turno(_id):
    data   = request.json or {}
    desc   = data.get("descripcion", "").strip()
    activo = 1 if str(data.get("activo")).lower() in ("1","true","t","yes") else 0
    if not desc:
        return abort(400, "Falta la descripción del turno")
    db = get_db()
    db.execute(
        "UPDATE turnos SET descripcion = ?, activo = ? WHERE id = ?",
        (desc, activo, _id)
    )
    db.commit()
    return "", 204

@app.get("/api/rutas")
def api_rutas():
    rows = get_db().execute("SELECT id, descripcion, activo FROM rutas ORDER BY descripcion").fetchall()
    return jsonify([dict(r) for r in rows])

@app.get("/api/grupos")
def api_grupos():
    rows = get_db().execute("SELECT id, descripcion, activo FROM grupos ORDER BY descripcion").fetchall()
    return jsonify([dict(r) for r in rows])

@app.get("/api/colores")
def api_colores():
    rows = get_db().execute("SELECT id, descripcion, activo FROM colores ORDER BY descripcion").fetchall()
    return jsonify([dict(r) for r in rows])

@app.get("/api/guias")
def api_guias():
    rows = get_db().execute("SELECT id, descripcion, activo FROM guias ORDER BY descripcion").fetchall()
    return jsonify([dict(r) for r in rows])

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# POST: guardar registro de la pestaña GRUPOS
@app.post("/api/inc-grupos")
def api_add_inc_grupos():
    d = request.json or {}
    fecha        = d.get("fecha")
    ruta_id      = d.get("ruta_id")
    grupo_id     = d.get("grupo_id")
    color_id     = d.get("color_id")
    guia_id      = d.get("guia_id")
    pax          = d.get("pax", 0)
    hora_llegada = d.get("hora_llegada")

    if not all([fecha, ruta_id, grupo_id, color_id, guia_id, hora_llegada]):
        return abort(400, "Faltan campos obligatorios")

    db = get_db()
    db.execute("""
      INSERT INTO inc_grupos(fecha, ruta_id, grupo_id, color_id, guia_id, pax, hora_llegada)
      VALUES(?,?,?,?,?,?,?)
    """, (fecha, ruta_id, grupo_id, color_id, guia_id, pax, hora_llegada))
    db.commit()
    return "", 201

from datetime import date

@app.get("/api/grupos-dia")
def api_grupos_dia():
    fecha = request.args.get("fecha") or date.today().isoformat()
    rows = get_db().execute("""
        SELECT g.id, g.descripcion
          FROM inc_grupos ig
          JOIN grupos g ON g.id = ig.grupo_id
         WHERE ig.fecha = ?
         GROUP BY g.id, g.descripcion
         ORDER BY g.descripcion
    """, (fecha,)).fetchall()
    return jsonify([dict(r) for r in rows])

# ──────────────────────────────────────────────────────────────
#  API: GUIAS
# ──────────────────────────────────────────────────────────────
@app.get("/api/guias")
def list_guias():
    rows = get_db().execute(
        "SELECT id, descripcion, activo FROM guias ORDER BY descripcion"
    ).fetchall()
    return jsonify([dict(r) for r in rows])


@app.post("/api/guias")
def add_guia():
    nombre = (request.json or {}).get("descripcion", "").strip()
    if not nombre:
        return abort(400, "Falta la descripción de la guía")
    db = get_db()
    db.execute("INSERT INTO guias(descripcion, activo) VALUES (?, 1)", (nombre,))
    db.commit()
    return "", 204


# ──────────────────────────────────────────────────────────────
#  API: COLORES
# ──────────────────────────────────────────────────────────────
@app.get("/api/colores")
def list_colores():
    rows = get_db().execute(
        "SELECT id, descripcion, activo FROM colores ORDER BY descripcion"
    ).fetchall()
    return jsonify([dict(r) for r in rows])


@app.post("/api/colores")
def add_color():
    nombre = (request.json or {}).get("descripcion", "").strip()
    if not nombre:
        return abort(400, "Falta la descripción del color")
    db = get_db()
    db.execute("INSERT INTO colores(descripcion, activo) VALUES (?, 1)", (nombre,))
    db.commit()
    return "", 204

def _to_int_bool(val):
    """True/1/'true' → 1   |   False/0/'false'/None → 0"""
    if isinstance(val, bool):
        return 1 if val else 0
    if isinstance(val, (int, float)):
        return 1 if val else 0
    return 1 if str(val).lower() in ('1', 'true', 't', 'yes') else 0


# ───────────── GUIAS ─────────────
@app.route("/api/guias/<int:_id>", methods=["PUT"])
def update_guia(_id):
    data   = request.json or {}
    nombre = data.get("descripcion", "").strip()
    activo = _to_int_bool(data.get("activo"))
    if not nombre:
        return abort(400, "Falta la descripción de la guía")

    db = get_db()
    db.execute(
        "UPDATE guias SET descripcion = ?, activo = ? WHERE id = ?",
        (nombre, activo, _id)
    )
    db.commit()
    return "", 204


# ──────────── COLORES ────────────
@app.route("/api/colores/<int:_id>", methods=["PUT"])
def update_color(_id):
    data   = request.json or {}
    nombre = data.get("descripcion", "").strip()
    activo = _to_int_bool(data.get("activo"))
    if not nombre:
        return abort(400, "Falta la descripción del color")

    db = get_db()
    db.execute(
        "UPDATE colores SET descripcion = ?, activo = ? WHERE id = ?",
        (nombre, activo, _id)
    )
    db.commit()
    return "", 204


@app.get('/api/incidencias-reporte')
def api_incidencias_reporte():
    d1 = request.args.get('desde') or date.today().isoformat()
    d2 = request.args.get('hasta') or d1

    turno_txt = request.args.get('turno')          #  ← “Turno 1”, “Turno 2 …”
    grupo_id  = request.args.get('grupo_id')
    cat_id    = request.args.get('categoria_id')

    filtros = []
    params  = [d1, d2]

    if turno_txt:                       # ▲ usa texto, NO id
        filtros.append('I.turno = ?')
        params.append(turno_txt)        #     (“Turno 1”)

    if grupo_id:
        filtros.append('I.grupo_id = ?')
        params.append(int(grupo_id))

    if cat_id:
        filtros.append('I.inc_tipo_id = ?')
        params.append(int(cat_id))

    extra = (' AND ' + ' AND '.join(filtros)) if filtros else ''

    sql = f'''
        SELECT I.fecha,
               I.turno                       AS turno,      -- ya es texto
               G.descripcion                 AS grupo,
               R.descripcion                 AS ruta,
               GU.descripcion                AS guia,
               C.descripcion                 AS color,
               IT.descripcion                AS categoria,
               I.comentario
          FROM incidencias   I
          JOIN grupos        G  ON G.id = I.grupo_id
          LEFT JOIN inc_grupos IG ON IG.fecha = I.fecha
                                AND IG.grupo_id = I.grupo_id
          LEFT JOIN rutas     R  ON R.id = IG.ruta_id
          LEFT JOIN guias     GU ON GU.id = IG.guia_id
          LEFT JOIN colores   C  ON C.id = IG.color_id
          JOIN inc_tipos      IT ON IT.id = I.inc_tipo_id
         WHERE I.fecha BETWEEN ? AND ? {extra}
         ORDER BY I.fecha, I.id
    '''
    rows = get_db().execute(sql, params).fetchall()
    return jsonify([dict(r) for r in rows])

# --- Catálogos filtrados por fecha ---------------------------------
@app.get("/api/grupos-disponibles")
def api_grupos_disponibles():
    fecha = request.args.get("fecha") or date.today().isoformat()
    rows = get_db().execute("""
        SELECT id, descripcion
          FROM grupos
         WHERE id NOT IN (SELECT grupo_id
                            FROM inc_grupos
                           WHERE fecha = ?)
         ORDER BY descripcion
    """, (fecha,)).fetchall()
    return jsonify([dict(r) for r in rows])

@app.get("/api/rutas-disponibles")
def api_rutas_disponibles():
    fecha = request.args.get("fecha") or date.today().isoformat()
    rows = get_db().execute("""
        SELECT id, descripcion
          FROM rutas
         WHERE id NOT IN (SELECT ruta_id
                            FROM inc_grupos
                           WHERE fecha = ?)
         ORDER BY descripcion
    """, (fecha,)).fetchall()
    return jsonify([dict(r) for r in rows])

# GET: listar con filtros
@app.get("/api/inc-grupos")
def api_list_inc_grupos():
    args = request.args
    d1   = args.get("desde")
    d2   = args.get("hasta")
    ruta = args.get("ruta_id")
    grp  = args.get("grupo_id")
    gui  = args.get("guia_id")
    col  = args.get("color_id")

    where = []
    params = []

    if d1 and d2:
        where.append("fecha BETWEEN ? AND ?")
        params += [d1, d2]
    elif d1:
        where.append("fecha >= ?")
        params.append(d1)
    elif d2:
        where.append("fecha <= ?")
        params.append(d2)

    if ruta: where.append("ruta_id = ?");  params.append(int(ruta))
    if grp:  where.append("grupo_id = ?"); params.append(int(grp))
    if gui:  where.append("guia_id = ?");  params.append(int(gui))
    if col:  where.append("color_id = ?"); params.append(int(col))

    clause = "WHERE " + " AND ".join(where) if where else ""
    sql = f"""
      SELECT IG.id, IG.fecha, IG.pax, IG.hora_llegada,
             R.descripcion AS ruta,
             G.descripcion AS grupo,
             C.descripcion AS color,
             U.descripcion AS guia
        FROM inc_grupos IG
        JOIN rutas   R ON R.id = IG.ruta_id
        JOIN grupos  G ON G.id = IG.grupo_id
        JOIN colores C ON C.id = IG.color_id
        JOIN guias   U ON U.id = IG.guia_id
        {clause}
       ORDER BY IG.fecha DESC, IG.id DESC
    """
    rows = get_db().execute(sql, params).fetchall()
    return jsonify([dict(r) for r in rows])


@app.get("/api/turnos")
def api_turnos():
    rows = get_db().execute(
        "SELECT id, descripcion FROM turnos WHERE activo=1 ORDER BY id"
    ).fetchall()
    return jsonify([dict(r) for r in rows])

@app.get("/api/inc-tipos")
def api_inc_tipos():
    rows = get_db().execute(
        "SELECT id, descripcion FROM inc_tipos ORDER BY descripcion"
    ).fetchall()
    return jsonify([dict(r) for r in rows])

@app.post("/api/incidencias")
def api_add_incidencias():
    d = request.json or {}
    fecha    = d.get("fecha") or date.today().isoformat()
    turno_id = d.get("turno_id")
    grupo_id = d.get("grupo_id")
    dets     = d.get("incidencias") or []  # [{categoria_id, comentario}, ...]

    if not (turno_id and grupo_id and dets):
        return abort(400, "Faltan turno_id, grupo_id o incidencias")

    db = get_db()

    # Obtén texto del turno
    row_turno = db.execute("SELECT descripcion FROM turnos WHERE id=? AND activo=1", (turno_id,)).fetchone()
    if not row_turno:
        return abort(404, "Turno no válido")
    turno_txt = row_turno["descripcion"]

    insertados = 0
    for det in dets:
        cat_id     = det.get("categoria_id")
        comentario = (det.get("comentario") or "").strip()
        if not (cat_id and comentario):
            continue
        # Verifica categoría
        row_cat = db.execute("SELECT id FROM inc_tipos WHERE id=?", (cat_id,)).fetchone()
        if not row_cat:
            continue
        db.execute("""
            INSERT INTO incidencias (fecha, turno, grupo_id, inc_tipo_id, comentario)
            VALUES (?,?,?,?,?)
        """, (fecha, turno_txt, grupo_id, cat_id, comentario))
        insertados += 1

    db.commit()
    if not insertados:
        return abort(400, "No se insertó ninguna incidencia válida")
    return jsonify(insertadas=insertados), 201

# --- RUTAS DE ARCHIVOS ESTÁTICOS ---
@app.route("/")
def index():
    return send_from_directory(str(ROOT), "index.html")

@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory(str(ROOT), filename)

# --- API: LOGIN ---
@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.json or {}
    usuario = data.get("usuario")
    clave = data.get("clave")
    if not usuario or not clave:
        return abort(400, "Faltan credenciales")
    db = get_db()
    row = db.execute(
        "SELECT rol FROM usuarios WHERE usuario = ? AND clave = ? LIMIT 1",
        (usuario, clave)
    ).fetchone()
    if not row:
        return abort(401, "Credenciales inválidas")
    return jsonify(dict(rol=row["rol"]))


@app.get("/api/registros")
def get_registros():
    # rango obligatorio
    d1 = request.args.get("desde") or date.today().isoformat()
    d2 = request.args.get("hasta") or d1

    # filtros opcionales -------------------------------
    doctor  = request.args.get("doctor")    # id o None
    privado = request.args.get("privado")   # '1' o None

    sql_extra = []
    params    = [d1, d2]

    if doctor:
        sql_extra.append("R.doctor = ?")
        params.append(int(doctor))

    if privado == "1":                      # solo privados > 0
        sql_extra.append("R.privado > 0")

    # construir la cláusula final
    extra_clause = ""
    if sql_extra:
        extra_clause = " AND " + " AND ".join(sql_extra)

    rows = get_db().execute(f"""
        SELECT R.id, R.fecha, R.paciente,
               P.nombre  AS procedimiento,
               R.diferencia, R.privado, R.valor,
               R.a_pagar, R.monto_pct,
               D.nombre  AS doctor
          FROM Registros R
          JOIN Procedimientos P ON P.id = R.procedimiento
          JOIN Doctores       D ON D.id = R.doctor
         WHERE R.fecha BETWEEN ? AND ? {extra_clause}
         ORDER BY R.fecha, R.id
    """, params).fetchall()

    return jsonify([dict(r) for r in rows])

@app.post("/api/registros")
def add_registro():
    d = request.json or {}
    db = get_db()
    db.execute(
        """INSERT INTO Registros
           (fecha,paciente,procedimiento,diferencia,privado,valor,
            a_pagar,porciento,monto_pct,doctor)
           VALUES(?,?,?,?,?,?,?,?,?,?)""",
        (
            d["fecha"], d["paciente"], d["procedimiento"],
            d["diferencia"], d["privado"], d["valor"],
            d["a_pagar"], d["porciento"], d["monto_pct"],
            d["doctor"]
        )
    )
    db.commit()
    return "", 201

# --- API: USUARIOS ---
@app.route("/api/usuarios", methods=["GET"])
def list_usuarios():
    db = get_db()
    rows = db.execute(
        "SELECT usuario, clave, rol, activo FROM usuarios ORDER BY usuario"
    ).fetchall()
    return jsonify([dict(r) for r in rows])

@app.route("/api/usuarios", methods=["POST"])
def add_usuario():
    data = request.json or {}
    usuario = data.get("usuario")
    clave = data.get("clave")
    rol = data.get("rol")
    if not usuario or not clave or not rol:
        return abort(400, "Faltan datos de usuario")
    db = get_db()
    db.execute(
        "INSERT INTO usuarios(usuario, clave, rol, activo) VALUES(?, ?, ?, 1)",
        (usuario, clave, rol)
    )
    db.commit()
    return "", 204

@app.route("/api/usuarios/<usuario>", methods=["PUT"])
def update_usuario(usuario):
    data = request.json or {}
    clave = data.get("clave")
    rol = data.get("rol")
    activo = 1 if data.get("activo") else 0
    if clave is None or rol is None:
        return abort(400, "Faltan datos de usuario")
    db = get_db()
    db.execute(
        "UPDATE usuarios SET clave = ?, rol = ?, activo = ? WHERE usuario = ?",
        (clave, rol, activo, usuario)
    )
    db.commit()
    return "", 204

# --- ARRANQUE ---
if __name__ == "__main__":
    # Abrir navegador tras 1s
    Timer(1.0, lambda: webbrowser.open_new_tab(f"http://localhost:{PORT}")).start()
    print(f"📡 Servidor en http://localhost:{PORT} (Ctrl-C para detener)")
    app.run(port=PORT, debug=False)

