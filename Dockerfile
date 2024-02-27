# syntax=docker/dockerfile:1
FROM python:3.10
WORKDIR HybridAGI
COPY ./ ./
RUN python3 -m pip install --upgrade pip && pip3 install .
CMD ["python3", "main.py"]