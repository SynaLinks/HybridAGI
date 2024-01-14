# syntax=docker/dockerfile:1
FROM python:3.9
WORKDIR HybridAGI
COPY ./ ./
RUN python3 -m pip install --upgrade pip && pip3 install .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]