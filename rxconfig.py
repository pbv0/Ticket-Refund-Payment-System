import reflex as rx
from dotenv import load_dotenv

load_dotenv()

config = rx.Config(app_name="app", use_single_port=True, plugins=[rx.plugins.TailwindV3Plugin()])
