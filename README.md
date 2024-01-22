## Requirements
* rootless docker
* nvidia-container-toolkit or other

## Init workspace

run docker compose
```
docker compose up
```

open container bash
```
./ros-bash
```

init catkin workspace
```
cd ~/catkin_ws/src
catkin_init_workspace
cd ..
catkin_make
```

init python env
```
python -m venv .venv
sudo python -m pip install -r requirements.txt
``` 