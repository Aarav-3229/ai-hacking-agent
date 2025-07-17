""" from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import subprocess
import os
import shutil
from fastapi.responses import PlainTextResponse
import json
from ai_patcher import get_full_patch

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def form_get(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})

@app.post("/submit", response_class=HTMLResponse)
def scan_code(request: Request, repo_url: str = Form(...), token: str = Form(...)):
    folder_name = "repo_code"

    # 🔧 Safely remove old folder
    if os.path.exists(folder_name):
        shutil.rmtree(folder_name)

    # 🔐 Clone with token
    repo_url_with_token = repo_url.replace("https://", f"https://{token}@")
    subprocess.run([r"C:\Program Files\Git\cmd\git.exe", "clone", repo_url_with_token, folder_name], check=True)


    # 🕵️‍♂️ Run Semgrep
    subprocess.run(
    ["semgrep", "--config=auto", folder_name, "-o", "report.json"],
    check=False,
    encoding='utf-8',
    errors='ignore'
)
    import pdb;pdb.set_trace()


        # ✅ Load and parse the report
    with open("report.json", "r", encoding="utf-8") as f:
        report_data = json.load(f)

    results = []
    for v in report_data.get("results", []):
        file_path = v["path"]
        message = v["extra"]["message"]
        line = v["start"]["line"]

        try:
            with open(file_path, "r", encoding="utf-8") as code_file:
                full_code = code_file.read()
            patch = get_full_patch(full_code, message)
        except Exception as e:
            full_code = "[Could not read file]"
            patch = f"⚠️ Error generating patch: {str(e)}"

        results.append({
            "file": file_path,
            "line": line,
            "message": message,
            "code": full_code,
            "patch": patch
        })

    return templates.TemplateResponse("result.html", {
        "request": request,
        "results": results
    })




@app.get("/vulnerabilities", response_class=PlainTextResponse)
def get_vulnerabilities():
    try:
        with open("report.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        output = ""
        vulnerabilities = data.get("results", [])
        for v in vulnerabilities:
            output += f"File: {v['path']}\n"
            output += f"Line: {v['start']['line']}\n"
            output += f"Message: {v['extra']['message']}\n"
            output += f"Code: {v['extra'].get('lines', 'N/A')}\n"
            output += "-" * 50 + "\n"
        return output

    except Exception as e:
        return f"Error: {str(e)}"  """


from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
import subprocess
import os
import shutil
import json
from ai_patcher import get_full_patch

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def form_get(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})

@app.post("/submit", response_class=HTMLResponse)
def scan_code(request: Request, repo_url: str = Form(...), token: str = Form(...)):
    folder_name = "repo_code"

    # 🔧 Safely remove old folder
    if os.path.exists(folder_name):
        shutil.rmtree(folder_name)

    # 🔐 Clone the GitHub repo (token optional)
    if token.lower() != "none":
        repo_url_with_token = repo_url.replace("https://", f"https://{token}@")
    else:
        repo_url_with_token = repo_url

    subprocess.run([r"C:\Program Files\Git\cmd\git.exe", "clone", repo_url_with_token, folder_name], check=True)

    # 🕵️‍♂️ Run Semgrep and capture JSON output
    print("semgrep starting")
    result = subprocess.run(
        ["semgrep", "--config=auto", "--json", folder_name],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding='utf-8',
        errors='ignore',
        check=False
    )
    print("semgrep ended")

    try:
        report_data = json.loads(result.stdout)

    except json.JSONDecodeError:
        return templates.TemplateResponse("result.html", {
            "request": request,
            "results": [],
            "message": "❌ Semgrep scan failed or returned invalid JSON."
        })

    # 🧠 AI Patch per vulnerability
    results = []
    for v in report_data.get("results", []):
        import pdb;pdb.set_trace()
        file_path = os.path.join(folder_name, v["path"])
        message = v["extra"]["message"]
        line = v["start"]["line"]

        try:
            with open(file_path, "r", encoding="utf-8") as code_file:
                full_code = code_file.read()
            patch = get_full_patch(full_code, message)
        except Exception as e:
            full_code = "[❌ Could not read file]"
            patch = f"⚠️ Error generating patch: {str(e)}"

        results.append({
            "file": file_path,
            "line": line,
            "message": message,
            "code": full_code,
            "patch": patch
        })

    return templates.TemplateResponse("result.html", {
        "request": request,
        "results": results,
        "message": "✅ Scan complete!"
    })

@app.get("/vulnerabilities", response_class=PlainTextResponse)
def get_vulnerabilities():
    return "This route is no longer used since we're not writing report.json anymore."

