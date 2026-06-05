from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from database import engine, SessionLocal
from models import Base, Delegate
import csv
import io

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

Base.metadata.create_all(bind=engine)


def page(title, body):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{title}</title>
        <link rel="stylesheet" href="/static/style.css">
    </head>
    <body>
        <nav>
            <h2>MUN Portal</h2>
            <div>
                <a href="/">Register</a>
                <a href="/admin">Admin</a>
            </div>
        </nav>

        <main>
            {body}
        </main>
    </body>
    </html>
    """


@app.get("/", response_class=HTMLResponse)
def home():
    body = """
    <section class="card">
        <h1>Delegate Registration</h1>
        <p>Register delegates for the Model United Nations conference.</p>

        <form method="post" action="/register">

            <label>Full Name</label>
            <input type="text" name="full_name" required>

            <label>Email</label>
            <input type="email" name="email" required>

            <label>School</label>
            <input type="text" name="school" required>

            <label>Country</label>
            <input type="text" name="country" required>

            <label>Committee</label>
            <select name="committee" required>
                <option value="UNSC">UNSC</option>
                <option value="WHO">WHO</option>
                <option value="UNHRC">UNHRC</option>
                <option value="DISEC">DISEC</option>
            </select>

            <button type="submit">Register Delegate</button>
        </form>
    </section>
    """
    return page("Delegate Registration", body)


@app.post("/register", response_class=HTMLResponse)
def register(
    full_name: str = Form(...),
    email: str = Form(...),
    school: str = Form(...),
    country: str = Form(...),
    committee: str = Form(...)
):
    db = SessionLocal()

    new_delegate = Delegate(
        full_name=full_name,
        email=email,
        school=school,
        country=country,
        committee=committee
    )

    db.add(new_delegate)
    db.commit()
    db.close()

    body = f"""
    <section class="card success">
        <h1>Registration Successful</h1>
        <p>Thank you, <strong>{full_name}</strong>.</p>
        <p>Your registration has been saved successfully.</p>

        <div class="actions">
            <a class="button" href="/">Register Another Delegate</a>
            <a class="button secondary" href="/admin">View Admin Dashboard</a>
        </div>
    </section>
    """
    return page("Registration Successful", body)


@app.get("/admin", response_class=HTMLResponse)
def admin(search: str = ""):
    db = SessionLocal()

    if search:
        delegates = (
            db.query(Delegate)
            .filter(Delegate.full_name.contains(search))
            .all()
        )
    else:
        delegates = db.query(Delegate).all()

    db.close()

    rows = ""

    for delegate in delegates:
        rows += f"""
        <tr>
            <td>{delegate.id}</td>
            <td>{delegate.full_name}</td>
            <td>{delegate.email}</td>
            <td>{delegate.school}</td>
            <td>{delegate.country}</td>
            <td>{delegate.committee}</td>
            <td>
                <form method="post" action="/delete/{delegate.id}">
                    <button class="danger" type="submit">Delete</button>
                </form>
            </td>
        </tr>
        """

    body = f"""
    <section class="card wide">
        <h1>Admin Dashboard</h1>
        <p>View, search, export, and manage registered delegates.</p>

        <form class="search-form" method="get" action="/admin">
            <input type="text" name="search" placeholder="Search by delegate name..." value="{search}">
            <button type="submit">Search</button>
            <a class="button secondary" href="/admin">Clear</a>
            <a class="button" href="/export">Export CSV</a>
        </form>

        <table>
            <tr>
                <th>ID</th>
                <th>Full Name</th>
                <th>Email</th>
                <th>School</th>
                <th>Country</th>
                <th>Committee</th>
                <th>Action</th>
            </tr>
            {rows}
        </table>
    </section>
    """

    return page("Admin Dashboard", body)


@app.post("/delete/{delegate_id}")
def delete_delegate(delegate_id: int):
    db = SessionLocal()

    delegate = db.query(Delegate).filter(Delegate.id == delegate_id).first()

    if delegate:
        db.delete(delegate)
        db.commit()

    db.close()

    return RedirectResponse(url="/admin", status_code=303)


@app.get("/export")
def export_csv():
    db = SessionLocal()
    delegates = db.query(Delegate).all()
    db.close()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["ID", "Full Name", "Email", "School", "Country", "Committee"])

    for delegate in delegates:
        writer.writerow([
            delegate.id,
            delegate.full_name,
            delegate.email,
            delegate.school,
            delegate.country,
            delegate.committee
        ])

    output.seek(0)

    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=delegates.csv"}
    )