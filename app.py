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
# ✅ FIXED EXPORT (READY)
# =========================
@app.route("/export")
def export():

    conn = sqlite3.connect("leads.db")
    c = conn.cursor()
    c.execute("SELECT * FROM leads ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_ALL)

    # clean headers for Google Sheets
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

    # clean data rows
    for row in rows:
        writer.writerow([x if x is not None else "" for x in row])

    output.seek(0)

    return Response(
        output,
        mimetype="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=leads_google_sheets.csv"
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
