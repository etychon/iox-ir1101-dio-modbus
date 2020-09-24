FROM multiarch/qemu-user-static:x86_64-aarch64 as qemu
FROM arm64v8/alpine:latest
COPY --from=qemu /usr/bin/qemu-aarch64-static /usr/bin

ENV DEBIAN_FRONTEND noninteractive
ENV TERM xterm

ADD idle.sh /idle.sh
ADD modbus_server.py /modbus_server.py

# Install.
RUN \
  	apk add --no-cache bash unzip less net-tools joe iproute2 python3 python3-dev gcc musl-dev && \
	pip3 install --upgrade pip && \
        pip3 install pymodbus twisted && \
  	apk del musl-dev gcc python3-dev

# Set environment variables.
ENV HOME /root

# Define working directory.
WORKDIR /root

# Define default command.
CMD ["bash", "/idle.sh"]
