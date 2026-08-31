GV_IMAGE_NAME=$1
GV_IMAGE_TAG=$2

DOCKER_IMG_FULL=$GV_IMAGE_NAME:$GV_IMAGE_TAG

export DOCKER_BUILDKIT=1  # caching purposes

docker pull $DOCKER_IMG_FULL || true

docker inspect $DOCKER_IMG_FULL > /dev/null   # important for caching - forces to download image metadata

docker build --build-arg BUILDKIT_INLINE_CACHE=1 \
             --cache-from $DOCKER_IMG_FULL \
             -t $DOCKER_IMG_FULL .

docker push $DOCKER_IMG_FULL