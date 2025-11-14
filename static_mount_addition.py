# Add static file mounting after the CORS middleware
app.mount("/", StaticFiles(directory="frontend", html=True), name="static")