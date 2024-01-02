FROM python:3.11-slim

# ghコマンドをインストール
RUN apt-get update && apt-get install -y git gh

# 標準入力から認証情報を受け取る
RUN echo $GITHUB_TOKEN | gh auth login --with-token
