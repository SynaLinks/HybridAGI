# syntax=docker/dockerfile:1
FROM python:3.9
RUN git clone https://github.com/SynaLinks/HybridAGI-library
WORKDIR HybridAGI
COPY ./ ./
RUN pip3 install .
CMD ["python3", "main.py"]