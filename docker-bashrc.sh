#!/bin/bash

# Locate the docker binary.
docker=$(which docker)
if [ "$?" == "0" ];
then
	# Wrap the existing docker so that we rebuild our docker-specific hosts
	# file directly after it has finished executing.
	function docker() {
		# Call the original docker binary.
		$docker "$@";
		# Run the host rebuild in the background.
		($HOME/bin/rebuild_docker_hosts.py &);
	}
fi