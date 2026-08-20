from app import create_app
from dotenv import load_dotenv
from app.database.database import init_engine
from app.scheduler import start_scheduler

load_dotenv()
init_engine()
app = create_app()

if __name__ == '__main__':
    start_scheduler()
    app.run(debug=True)
