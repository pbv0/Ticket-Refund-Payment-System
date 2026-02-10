import reflex as rx
import reflex_enterprise as rxe
from dotenv import load_dotenv

load_dotenv()

config = rxe.Config(app_name="app", use_single_port=True, plugins=[rx.plugins.TailwindV3Plugin()])
