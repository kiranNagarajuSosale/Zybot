# ZyBot


ZyBot is a full-stack chatbot application featuring a Python backend and an Angular frontend. The Angular ZyBot widget can run as a standalone app or be built as a web component to embed in any host application. The backend serves static files and provides secure, context-aware chat services.

## Features
- **Backend (Python, Flask):**
	- Secure server with SSL certificates
	- Context management and ingestion
	- Vector store for efficient retrieval
	- Modular chatbot logic
- **Frontend (Angular):**
	- Customizable chat widget
	- Modern UI/UX
	- Service-based architecture
	- Can run standalone or as a web component

## Project Structure
```
backend/
	app.py              # Main backend server
	chatbot.py          # Chatbot logic
	dom_context.py      # Context management
	ingest.py           # Data ingestion
	requirements.txt    # Python dependencies
	run_secure.py       # Secure server runner
	runtime_tracer.py   # Tracing and debugging
	certs/              # SSL certificates
	static/             # Frontend static files
	vectorstore/        # Vector database files
frontend/
	package.json        # Frontend dependencies
	chatbot-widget/     # Angular chat widget
		src/              # Source code
		public/           # Public assets
		examples/         # Usage examples
scripts/
    - Secure server with SSL certificates
    - Context management and ingestion
    - Vector store for efficient retrieval
    - Modular chatbot logic
- **Frontend (Angular):**
    - Customizable chat widget
    - Modern UI/UX
    - Service-based architecture
    - Can run standalone or as a web component

## Project Structure
```

## Setup Instructions

### Backend
1. Navigate to `backend/`.
2. Create and activate a Python virtual environment:
	 ```powershell
	 python -m venv venv
	 .\venv\Scripts\Activate.ps1
	 ```
3. Install dependencies:
	 ```powershell
	 pip install -r requirements.txt
	 ```
4. Run the server (secure):
	 ```powershell
	 python run_secure.py
	 ```


### Frontend: Run Standalone
1. Navigate to `frontend/chatbot-widget/`.
2. Install dependencies:
	```powershell
	npm install
	```
3. Run the development server:
	```powershell
	ng serve
	```
4. Access the app at `http://localhost:4200` in your browser.

### Frontend: Build as Web Component
1. Navigate to `frontend/chatbot-widget/`.
2. Build the project for production:
	```powershell
	ng build --configuration production
	```
3. The build output will be in `dist/chatbot-widget/browser/`.
4. Copy the generated `main.js` (and any required files) from `dist/chatbot-widget/browser/` to your backend's `static/` folder.

### Using ZyBot as a Web Component Plugin
To embed ZyBot in any host application (HTML page, React, Angular, etc.):

1. Ensure your backend is running and serving static files (e.g., `main.js`) at a public URL.
2. Add the following code to your host application's HTML:
	```html
	<script src="https://your-domain.com/static/main.js"></script>
	<zy-bot></zy-bot>
	```
	- Replace the `src` URL with your backend's actual static file URL if different.
	- `<zy-bot></zy-bot>` is the custom element for the chatbot widget.


## Usage
- Access the chatbot via the Angular frontend (standalone mode) or embed the web component in any host application.
- Backend runs on a secure Flask server and serves the widget's build files.
- Customize the chat widget and backend logic as needed.


## Contributing
Pull requests and issues are welcome! Please follow standard coding and documentation practices.


## License
This project is licensed under the MIT License.

---

For Angular widget setup details, see `frontend/chatbot-widget/setup_manual.txt`.
