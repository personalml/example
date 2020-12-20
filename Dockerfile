ARG base_image
FROM $base_image

ARG config_path

LABEL maintainer="dna@dextra-sw.com"

ADD $config_path/wheels wheels
RUN pip install ./wheels/*

ADD requirements.txt .
RUN pip install --quiet -r requirements.txt
ADD tests/requirements.txt .
RUN pip install --quiet -r requirements.txt

ADD $config_path/spark/* $SPARK_HOME/conf/

RUN echo 'c.NotebookApp.contents_manager_class = "notedown.NotedownContentsManager"' >> ~/.jupyter/jupyter_notebook_config.py
