# Reverse Engineering portal

This is a basic FastAPI application which interacts with reverse engineered solution of the apps like OLX, instagram, etc 

## Assignment Submission
The image with this project named System_design_rev_eng_app.png is the diagram which would be explained further on a call. The image is also included in the TRG_task_submission.pdf along with references to websites which I took help from while attempting the solution of the assignment.

## How to Test and Run the App

1. Ensure the dependencies are installed:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the application by running:
   ```bash
   fastapi run main.py
   ```
   *(For development with auto-reload, you can also use `fastapi dev main.py`)*

3. **View the Auto-created Docs:**
   Once the server is running, FastAPI automatically generates interactive API documentation. You can test the endpoints directly from your browser:
   - **Swagger UI** (interactive): [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
   - **ReDoc** (alternative documentation): [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
