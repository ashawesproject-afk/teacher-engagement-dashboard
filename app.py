from flask import Flask, render_template, request, jsonify
from datetime import datetime

app = Flask(__name__)

TEACHERS = ["teacher1", "teacher2", "teacher3", "teacher4"]

def empty_teacher_state():
    return {
        "timestamp": "--",
        "total": 0,
        "counts": {"reading": 0, "writing": 0, "hand_raise": 0, "phone": 0, "other": 0},
        "engagement": 0.0,
        "history": [],
        "students": []  # list of {id, activity, engaged, attention, last_seen}
    }

DATA = {tid: empty_teacher_state() for tid in TEACHERS}

def compute_engagement(counts, total):
    engaged = counts.get("reading", 0) + counts.get("writing", 0) + counts.get("hand_raise", 0)
    return round(engaged / total, 3) if total > 0 else 0.0

@app.route("/")
def index():
    return render_template("index.html", teachers=TEACHERS)

@app.route("/api/update", methods=["POST"])
def update():
    payload = request.get_json(force=True)

    teacher_id = payload.get("teacher_id", "teacher1")
    if teacher_id not in DATA:
        DATA[teacher_id] = empty_teacher_state()

    total = int(payload.get("total", 0))
    counts_in = payload.get("counts", {})

    counts = {}
    for k in DATA[teacher_id]["counts"].keys():
        counts[k] = int(counts_in.get(k, 0))

    ts = datetime.now().strftime("%H:%M:%S")
    engagement = compute_engagement(counts, total)

    # Per-student analysis (optional)
    students_in = payload.get("students", [])
    students = []
    for s in students_in:
        sid = str(s.get("id", "Unknown"))
        activity = str(s.get("activity", "other"))
        engaged = bool(s.get("engaged", False))
        attention = float(s.get("attention", 0.0))  # 0..1
        students.append({
            "id": sid,
            "activity": activity,
            "engaged": engaged,
            "attention": round(attention, 3),
            "last_seen": ts
        })

    DATA[teacher_id]["timestamp"] = ts
    DATA[teacher_id]["total"] = total
    DATA[teacher_id]["counts"] = counts
    DATA[teacher_id]["engagement"] = engagement
    DATA[teacher_id]["students"] = students

    DATA[teacher_id]["history"].append({"t": ts, "e": engagement})
    if len(DATA[teacher_id]["history"]) > 80:
        DATA[teacher_id]["history"] = DATA[teacher_id]["history"][-80:]

    return jsonify({"status": "ok", "teacher_id": teacher_id, "engagement": engagement})

@app.route("/api/latest")
def latest():
    teacher_id = request.args.get("teacher_id", "teacher1")
    if teacher_id not in DATA:
        DATA[teacher_id] = empty_teacher_state()
    return jsonify(DATA[teacher_id])

if __name__ == "__main__":
    app.run(debug=True, port=5000)
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
