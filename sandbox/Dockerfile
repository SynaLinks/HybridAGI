FROM python:3.10
WORKDIR Workspace
RUN mkdir server & mkdir workspace
COPY ./requirements.txt ./server/requirements.txt
RUN python3 -m pip install --upgrade pip && pip3 install -r ./server/requirements.txt
COPY ./server.py ./server.py
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]