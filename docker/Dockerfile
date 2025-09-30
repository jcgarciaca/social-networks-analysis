FROM python:3.11

RUN python3 -m pip install -U pip

RUN apt-get update \
    && apt-get install -y nano screen \
    && apt-get autoremove \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install requests jupyterlab python-louvain pyvis matplotlib pandas scipy hdbscan umap-learn plotly wordcloud nltk \
    langchain langchain_openai langchain_core langchain_community langgraph python-multipart

WORKDIR /workdir
