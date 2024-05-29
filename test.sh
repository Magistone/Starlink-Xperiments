#Build image for testing
docker build -f Dockerfile_test_image -t testainer -q .

#Run tests
docker run --rm testainer

#Delete image to avoid dangling images
docker image rm testainer