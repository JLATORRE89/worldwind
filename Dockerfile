# Use the official Node.js image as the base image
FROM node:14

# Set the working directory inside the container
WORKDIR /app

# Copy package.json and package-lock.json files to the container
COPY ./app/* .

# Install project dependencies
RUN npm install -g http-server
RUN ln -s /usr/bin/nodejs /usr/bin/node


# Copy the rest of the application code to the container
COPY ./app/* .
#ADD ./app/index.html /app/index.html
#ADD ./app/WorldWind.js /app/WorldWind.js


EXPOSE 8080

# Specify the command to start the Node.js app
CMD [ "http-server", "-s" ]
