FROM python:3.11

ENV PIPENV_VENV_IN_PROJECT=1

RUN pip install -U pip pipenv

ADD Pipfile.lock Pipfile /usr/src/
WORKDIR /usr/src/
RUN pipenv sync

RUN adduser default
USER default

ADD . /usr/src/

CMD [ "python" ]