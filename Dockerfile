FROM python:3.10-slim

# লিনাক্স সার্ভারে ক্রোমিয়াম ও বাংলা ফন্ট ইনস্টল
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    fonts-beng \
    && rm -rf /var/lib/apt/lists/*

ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 10000

CMD ["python", "bot.py"]
