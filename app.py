from flask import Flask, render_template, request, redirect, Response
import sqlite3
import csv
import io

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect("leads.db")
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            email TEXT,
            age INTEGER,
            interest TEXT,
            credit_card TEXT,
            restrictions TEXT,
            property TEXT,
            status TEXT,
            contact_method TEXT
        )
    """)

    conn.commit()
    conn.close()

init_db()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/step2", methods=["POST"])
def step2():
    return render_template("step2.html", data=request.form)

@app.route("/step3", methods=["POST"])
def step3():
    return render_template("step3.html", data=request.form)

@app.route("/submit", methods=["POST"])
def submit():
    conn = sqlite3.connect("leads.db")
    c = conn.cursor()

    c.execute("""
        INSERT INTO leads VALUES (NULL,?,?,?,?,?,?,?,?,?,?)
    """, (
        request.form["name"],
        request.form["phone"],
        request.form["email"],
        request.form["age"],
        request.form["interest"],
        request.form["credit_card"],
        request.form["restrictions"],
        request.form["property"],
        request.form["status"],
        request.form["contact_method"]
    ))

    conn.commit()
    conn.close()

    return "תודה! נחזור אליך בקרוב."

@app.route("/admin")
def admin():
    conn = sqlite3.connect("leads.db")
    c = conn.cursor()
    c.execute("SELECT * FROM leads ORDER BY id DESC")
    leads = c.fetchall()
    conn.close()

    return render_template("admin.html", leads=leads)

# =========================
# 🔥 CLEAN GOOGLE SHEETS EXPORT (FIXED)
# =========================
@app.route("/export")
def export():

    conn = sqlite3.connect("leads.db")
    c = conn.cursor()
    c.execute("SELECT * FROM leads ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()

    output = io.StringIO()

    writer = csv.writer(
        output,
        delimiter=",",
        quoting=csv.QUOTE_MINIMAL
    )

    # ✅ Clean professional headers
    writer.writerow([
        "ID",
        "Name",
        "Phone",
        "Email",
        "Age",
        "Interest",
        "Credit Card",
        "Restrictions",
        "Property",
        "Status",
        "Contact Method"
    ])

    # ✅ Clean + normalize rows for Google Sheets stability
    for row in rows:
        cleaned = []
        for v in row:
            if v is None:
                cleaned.append("")
            else:
                cleaned.append(str(v).replace("\n", " ").replace("\r", " ").strip())
        writer.writerow(cleaned)

    output.seek(0)

    return Response(
        output.getvalue().encode("utf-8-sig"),
        mimetype="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=CRM_GOOGLE_SHEETS_CLEAN.csv"
        }
    )

@app.route("/delete/<int:id>")
def delete(id):
    conn = sqlite3.connect("leads.db")
    c = conn.cursor()
    c.execute("DELETE FROM leads WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/admin")

@app.route("/clear")
def clear():
    conn = sqlite3.connect("leads.db")
    c = conn.cursor()
    c.execute("DELETE FROM leads")
    conn.commit()
    conn.close()
    return redirect("/admin")

if __name__ == "__main__":
    app.run(debug=True)
