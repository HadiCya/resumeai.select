import io
import json
from os import environ as env
from urllib.parse import quote_plus, urlencode

from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask, redirect, render_template, session, url_for, request, Response
import workers_kv
from pylatex import Document, Section, Subsection, Command
from pylatex.utils import italic, NoEscape

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

app = Flask(__name__)
app.secret_key = env.get("APP_SECRET_KEY")


oauth = OAuth(app)

oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration'
)

kv = workers_kv.Namespace(account_id=env.get("CF_ACCOUNT_ID"),
                          api_key=env.get("CF_API_TOKEN"),
                          namespace_id=env.get("CF_NAMESPACE_ID"))

# Controllers API


@app.route("/")
def home():
    if session.get("user"):
        user_info = session["user"]
        user_id = user_info["userinfo"]["sub"]

        existing_data = kv.read(user_id)
        print(existing_data)
        if not existing_data:
            existing_data = {"school": "", "graduation_date": ""}

        return render_template(
            "index.html",
            session=user_info,
            pretty=json.dumps(user_info, indent=4),
            existing_data=existing_data
        )
    else:
        return render_template("index.html")


@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    return redirect("/")


@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://"
        + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("home", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )


@app.route("/submit-school-info", methods=["POST"])
def submit_school_info():
    if not session.get("user"):
        return redirect(url_for("login"))

    user_info = session["user"]
    user_id = user_info["userinfo"]["sub"]

    # Initialize containers for each section
    education_data = []
    skills_data = []
    certifications_data = []
    experience_data = []
    projects_data = []

    # Process each section
    for key in request.form:
        index = key.split('_')[-1]

        if key.startswith('school_'):
            education_entry = {
                'school': request.form.get('school_' + index, ''),
                'degree': request.form.get('degree_' + index, ''),
                'field_of_study': request.form.get('field_of_study_' + index, ''),
                'start_year': request.form.get('start_year_' + index, ''),
                'end_year': request.form.get('end_year_' + index, '')
            }
            education_data.append(education_entry)
        elif key.startswith('skill_'):
            skills_data.append(request.form.get(key, ''))
        elif key.startswith('certification_'):
            certifications_data.append(request.form.get(key, ''))
        elif key.startswith('job_title_'):
            experience_entry = {
                'job_title': request.form.get('job_title_' + index, ''),
                'company': request.form.get('company_' + index, ''),
                'start_date': request.form.get('start_date_' + index, ''),
                'end_date': request.form.get('end_date_' + index, ''),
                'job_description': request.form.get('job_description_' + index, '')
            }
            experience_data.append(experience_entry)
        elif key.startswith('project_title_'):
            project_entry = {
                'project_title': request.form.get('project_title_' + index, ''),
                'tech_used': request.form.get('tech_used_' + index, ''),
                'project_description': request.form.get('project_description_' + index, '')
            }
            projects_data.append(project_entry)

    # Compile all data
    user_data = {
        "education": education_data,
        "skills": skills_data,
        "certifications": certifications_data,
        "experience": experience_data,
        "projects": projects_data
    }

    # Serialize data to JSON
    json_data = json.dumps(user_data)

    # Storing data in Cloudflare KV
    kv.write({user_id: json_data})

    return "Information submitted successfully!"

@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    # Assuming you get your LaTeX code from the POST request
    # Here, we create a simple LaTeX document for demonstration
    doc = Document()

    with doc.create(Section('A section')):
        doc.append('Some regular text and some ')
        doc.append(italic('italic text. '))
        with doc.create(Subsection('A subsection')):
            doc.append('Also, some crazy characters: $&#{}')

    # Compile LaTeX document
    doc.generate_pdf('basic_maketitle', clean_tex=False)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=env.get("PORT", 3000))
