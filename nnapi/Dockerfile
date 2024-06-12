FROM pytorch/pytorch:1.7.0-cuda11.0-cudnn8-devel
# FROM python:3.9
# FROM tensorflow/tensorflow:2.9.1
WORKDIR /usr/src/web/nnapi

RUN python -m pip install --upgrade pip
RUN rm /etc/apt/sources.list.d/cuda.list
RUN rm /etc/apt/sources.list.d/nvidia-ml.list
RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y


# COPY ./torch_req.txt ./
# RUN pip install -r ./torch_req.txt

# RUN apt install protobuf-compiler
COPY ./requirements.txt .
# RUN pip install -r ./requirements.txt

# COPY ./research/ ./research/
# COPY ./egor_requ.txt .
# RUN pip install -r ./egor_requ.txt
RUN pip install -r ./requirements.txt

COPY ./r2.txt .
RUN pip install -r ./r2.txt
# RUN apt-get install glibc-source -y
ARG MEDIA_ROOT=/usr/src/web/media
ENV MEDIA_ROOT=$MEDIA_ROOT
RUN mkdir $MEDIA_ROOT
ENV PYTHONUNBUFFERED=1
# COPY ./server/ ./server
# RUN uname -a
# RUN cat /etc/os-release
# RUN apt-get update && apt-get install cuda -y
# ENV CUDA=11.0


# # ENV LD_LIBRARY_PATH /usr/local/cuda-${CUDA}/targets/x86_64-linux/lib:/usr/local/cuda/extras/CUPTI/lib64:/usr/local/cuda/lib64:$LD_LIBRARY_PATH
# # ENV LD_LIBRARY_PATH=/usr/local/cuda-11.0/targets/x86_64-linux/lib/
# RUN echo $LD_LIBRARY_PATH
# RUN ln -s /usr/local/cuda-11.0/targets/x86_64-linux/lib/libcusolver.so.10 /usr/local/cuda-11.0/targets/x86_64-linux/lib/libcusolver.so.11

CMD uvicorn --host ${NN_API_HOST} --port ${NN_API_PORT} --workers 1 --reload server.main:app 