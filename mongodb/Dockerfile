# mongo db with value added to the image
FROM mongo:latest

# Set the docker volume for MongoDB data
VOLUME /data/db
# Expose the default MongoDB port
EXPOSE 27017
# Set the default command to run MongoDB
CMD ["mongod", "--bind_ip_all"]