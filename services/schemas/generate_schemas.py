import pathlib
import subprocess


schemas = pathlib.Path(__file__).parent / 'schemas'
for f in schemas.rglob('*.py'):
    subprocess.run(["python", f])
