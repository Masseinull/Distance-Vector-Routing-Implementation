# Distance Vector Routing Protocol Simulator

This project is a Python-based simulation of the **Distance Vector Routing (DVR)** protocol, a core algorithm in computer networking. The application runs in the command line and simulates a dynamic network of routers that communicate with each other to build and maintain their routing tables.

The simulation uses UDP sockets and multithreading to replicate the distributed and asynchronous nature of real-world routers. The network's topology can be visualized and modified dynamically through an interactive menu.

## Features

* **Interactive Command-Line Interface:** Manage the network through a simple menu.
* **Distributed Simulation:** Each router runs in its own thread, independently calculating its routing table.
* **UDP Socket Communication:** Routers exchange their routing table information with neighbors via UDP sockets.
* **Dynamic Topology:**
    * Add new routers to the network at runtime.
    * Edit the cost of existing links between routers.
* **Network Visualization:** Generate and display a real-time graph of the network topology using `networkx` and `matplotlib`.
* **Routing Table Display:** View the latest routing table for any router in the network.

## How It Works

The simulation is built around a few key components:

1.  **`Router` Class**: Each router in the network is an instance of the `Router` class. It is responsible for initializing and updating its own routing table.
2.  **`networkx` Graph**: The overall network topology (routers as nodes, links as edges with weights) is managed by a `networkx` graph object.
3.  **Bellman-Ford Algorithm**: The core of the Distance Vector protocol is implemented within the `bellman_ford` method of the `Router` class. Each router periodically shares its distance vector with its direct neighbors.
4.  **Multithreading & Sockets**: Each router runs listener threads to receive routing table updates from its neighbors over dedicated UDP ports. This allows the simulation to process updates asynchronously, just like in a real network.
5.  **JSON Serialization**: Routing tables are converted to JSON format before being sent over the network via sockets, ensuring a standardized data exchange format.

## Installation

1.  Clone the repository to your local machine:
    ```bash
    git clone https://github.com/Masseinull/Distance-Vector-Routing-Implementation.git
    ```
2.  Navigate to the project directory:
    ```bash
    cd <your-project-directory>
    ```
3.  Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

To start the simulation, run the `main.py` script from your terminal:

```bash
python main.py
```

You will be greeted with an interactive menu. An initial network of three routers will be created automatically.

```
What is your choice:
1. Print routing table of a router
2. Show Graph
3. Edit link cost
4. Add router
5. bellman-ford once
6. Exit
```

Simply enter the number corresponding to the action you wish to perform. You can add routers, change link costs, and observe how the routing tables converge towards the optimal paths.
