run_template:
	cd services/template && pipenv run python init_db.py && pipenv run python -m uvicorn main:app --reload

run_sso:
	cd services/sso && pipenv run python init_db.py && pipenv run python -m uvicorn main:app --reload