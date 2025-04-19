FROM node:18

# If your app also uses Python:
RUN apt update && apt install -y python3 python3-pip gcc

WORKDIR /app
COPY . .

RUN npm install
RUN pip install -r requirements.txt

CMD ["npm", "start"]
