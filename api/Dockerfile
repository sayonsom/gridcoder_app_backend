FROM node:14.14.0-alpine
WORKDIR "/app"
COPY ./package.json ./
COPY ./synclabd-firebase-adminsdk-ytj92-85babe429d.json ./
CMD ["export", "GOOGLE_APPLICATION_CREDENTIALS=./synclabd-firebase-adminsdk-ytj92-85babe429d.json"]
RUN npm install
COPY . .
CMD ["npm", "run", "dev"]