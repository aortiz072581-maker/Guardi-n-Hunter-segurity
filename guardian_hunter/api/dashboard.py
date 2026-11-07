from fastapi import FastAPI, HTMLResponse

app = FastAPI(title="Guardian Hunter - SOC Dashboard")

@app.get("/soc", response_class=HTMLResponse)
def get_soc_dashboard():
    return """
    <html>
        <head><title>Guardian Hunter - SOC Enterprise</title></head>
        <body style="background:#0d1117; color:#58a6ff; font-family:monospace; padding:30px;">
            <h1 style="color:#238636;">[GUARDIAN HUNTER] - Panel Soberano SOC</h1>
            <p>Estado del Motor eBPF: <span style="color:#3fb950;">ACTIVO (37 Capas de Blindaje)</span></p>
        </body>
    </html>
    """
