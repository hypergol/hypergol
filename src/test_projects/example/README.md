# Example

This project was generated with the Hypergol framework

Please see documentation for instructions: [https://hypergol.readthedocs.io/en/latest/](https://hypergol.readthedocs.io/en/latest/)

<maybe this can serve as a quickstart guide>

### How to start Tensorboard

It is recommended to start it in a screen session so you can close the terminal window or if you disconnect from a remote Linux machine. In the project directory:

```
screen -S tensorboard
source .venv/bin/activate
tensorboard --logdir=<data_directory>/example/tensorboard/
```
