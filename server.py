import io
import json
from os import environ as env
from urllib.parse import quote_plus, urlencode

from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask, redirect, render_template, session, url_for, request, Response, jsonify, send_file
import workers_kv
from pylatex import Document, Section, Subsection, Command
from pylatex.utils import italic, NoEscape
import google.generativeai as genai

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

genai.configure(api_key=env.get("MAKERSUITE_KEY"))

# Set up the model
generation_config = {
"temperature": 0.9,
"top_p": 1,
"top_k": 1,
"max_output_tokens": 2048,
}

safety_settings = [
{
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
},
{
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
},
{
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
},
{
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
},
]

model = genai.GenerativeModel(model_name="gemini-pro",
                                generation_config=generation_config,
                                safety_settings=safety_settings)

# Controllers API


@app.route("/")
def home():
    if session.get("user"):
        user_info = session["user"]
        user_id = user_info["userinfo"]["sub"]

        existing_data = kv.read(user_id)

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

    # Personal information and links
    personal_info = {
        "name": request.form.get("name", ""),
        "email": request.form.get("email", ""),
        "phone_number": request.form.get("phone_number", "")
    }
    links = {
        "linkedin": request.form.get("linkedin", ""),
        "github": request.form.get("github", ""),
        "website": request.form.get("website", "")
    }

    # Initialize containers for each dynamic section
    education_data = []
    research_experience_data = []
    industry_experience_data = []
    projects_data = []
    technical_skills_data = {
        "languages": request.form.getlist("languages"),
        "frameworks": request.form.getlist("frameworks"),
        "dev_tools": request.form.getlist("dev_tools"),
        "libraries": request.form.getlist("libraries")
    }

    # Process each dynamic section
    for key in request.form:
        # Education Data
        if key.startswith('education_'):
            parts = key.split('_')
            index = parts[1]
            field = parts[2]
            if len(education_data) < int(index):
                education_data.append({})
            education_data[int(index)-1][field] = request.form[key]

        # Research Experience Data
        elif key.startswith('researchexperience_'):
            parts = key.split('_')
            index = parts[1]
            field = parts[2]
            if len(research_experience_data) < int(index):
                research_experience_data.append({})
            research_experience_data[int(index)-1][field] = request.form[key]

        # Industry Experience Data
        elif key.startswith('industryexperience_'):
            parts = key.split('_')
            index = parts[1]
            field = parts[2]
            if len(industry_experience_data) < int(index):
                industry_experience_data.append({})
            industry_experience_data[int(index)-1][field] = request.form[key]

        # Projects Data
        elif key.startswith('projects_'):
            parts = key.split('_')
            index = parts[1]
            field = parts[2]
            if len(projects_data) < int(index):
                projects_data.append({})
            projects_data[int(index)-1][field] = request.form[key]

    # Compile all data
    user_data = {
        "personal_info": personal_info,
        "links": links,
        "education": education_data,
        "research_experience": research_experience_data,
        "industry_experience": industry_experience_data,
        "projects": projects_data,
        "technical_skills": technical_skills_data
    }

    # Serialize data to JSON
    json_data = json.dumps(user_data)

    # Storing data in Cloudflare KV (assuming kv.write is a valid function call)
    kv.write({user_id: json_data})

    return "Information submitted successfully!"

@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    if session.get("user"):
        user_info = session["user"]
        user_id = user_info["userinfo"]["sub"]
        prompt_parts = [
        f"Create a job description with the given HTML file {request}",
        ]

        response = model.generate_content(prompt_parts)
        print(response.text)

        # Assuming you get your LaTeX code from the POST request
        # Here, we create a simple LaTeX document for demonstration
        doc = Document()

        with doc.create(Section('A section')):
            doc.append('Some regular text and some ')
            doc.append(italic('italic text. '))
            with doc.create(Subsection('A subsection')):
                doc.append('Also, some crazy characters: $&#{}')

        
        # Compile LaTeX document
        doc.generate_pdf(user_id, clean_tex=False)

        download_url = request.url_root + 'download/' + user_id + ".pdf"

        return {'url': download_url}
    else:
        return {'url': 'resumeai.select'}

@app.route('/download/<filename>', methods=['GET'])
def download_pdf(filename):
    # Send the generated PDF file for download
    return send_file(filename, as_attachment=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=env.get("PORT", 5000))
