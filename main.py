import threading
import socket
import time
import networkx as nx
import matplotlib.pyplot as plt
import math
import json

#global vars
port_num = 60000
Routers = []
G = nx.Graph()


class Router():


    def __init__(self, name, adj):
        global port_num
        self.name = name
        self.adj = adj
        self.direct_link = [False] * 100
        self.port = port_num
        self.send_port = port_num + 1
        self.bellman_port = port_num + 2
        port_num += 3
        self.routing_table = dict()
        self.calculate_routing_table()

    def calculate_routing_table(self):
        for node in G.nodes:
            if (G.has_edge(self.name, node)):
                self.routing_table[str(node)] = G.get_edge_data(self.name, node).get('weight')
                self.direct_link[node] = True
            else:
                weight = math.inf
                if(node == self.name):
                    weight = 0
                self.routing_table[str(node)] = weight
        # print(self.routing_table)



    def bellman_ford(self, updated_table, port_number):
        # print(f'bellman: router: {self.name}    dict: {self.routing_table}   updated: {updated_table}    port: {port_number}')
        change = False
        Routers.sort(key=lambda x: x.name, reverse=False)
        R = Routers[0]
        for r in Routers:
            # print(f'port_num = {port_number} and r is {r.name} and {r.port}')
            if((r.send_port == int(port_number)) or (r.bellman_port == int(port_number))):
                # print('found')
                R = r
        for r in Routers:
            try:
                if((self.routing_table.get(str(R.name)) + updated_table.get(str(r.name))) < (self.routing_table.get(str(r.name)))):
                    change = True
                    self.routing_table[str(r.name)] = self.routing_table.get(str(R.name)) + updated_table.get(str(r.name))
                    if(updated_table.get(str(r.name)) != 0):
                        self.direct_link[r.name] = False
            except:
                pass
        if(change):
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.bind(('localhost', self.bellman_port))
            data = json.dumps(self.routing_table)
            for n in Routers:
                if(G.has_edge(n.name, self.name)):
                    # print(f'I AM SENDIG with router number : {self.name} and port: {self.send_port}')
                    s.sendto(data.encode('utf-8'), ('localhost', n.port))
            change = False
            # s.close()

    def send_to_adj(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(('localhost', self.send_port))
        # print(f'I AM SENDIG with router number : {self.name} and port: {self.send_port}')

        # print(f'here the dict : {data}')
        # enc = data.encode('utf-8')
        # print(f'here the encoded dict : {enc}')
        # dec = enc.decode('utf-8')
        # print(f'here is the decoded: {dec}')
        # dic = json.loads(dec)
        # print(f'here is the load: {dic.get(str(self.name))} and type: {type(dic.get(str(self.name)))}')

        while True:
            data = json.dumps(self.routing_table)
            for n in Routers:
                if (G.has_edge(n.name, self.name)):
                    s.sendto(data.encode('utf-8'), ('localhost', n.port))
            time.sleep(10) #timeout

    def recieve_from_adj(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(('localhost', self.port))
        # print(f'port of this router is: {self.port}')
        while True:
            data, address = s.recvfrom(2048)
            recieved_table = json.loads(data.decode('utf-8'))
            # print(f'ADDR: {address}  and self: {self.name} and {self.port}  address[0]: {address[0]} address[1]: {address[1]}')
            # print(f'router {self.name} with port {self.port} and dic: {self.routing_table}  recieved from router {R.name} with port {R.port} and dic: {R.routing_table} ')
            self.bellman_ford(recieved_table, address[1])



def cheapest_path(src, dst):
    if(src.routing_table.get(str(dst.name)) != math.inf):
        print(f'Cheapest path between router number {src.name} and router number {dst.name} cost is {src.routing_table.get(str(dst.name))} ')
    else:
        print(f'There is no path from router number {src.name} to router number {dst.name}')

def show_routing_table(R):
    Routers.sort(key=lambda x: x.name, reverse=False)
    print(f'Latest routing table of router number {R.name}')
    for i in Routers:
        if (R.routing_table.get(str(i.name)) == math.inf):
            print(f'{i.name} : ∞')
        else:
            print(f'{i.name} : {R.routing_table.get(str(i.name))}')

def edit_link(src, dst):
    if(G.has_edge(src.name, dst.name)):
        weight = input(f'Enter the new link\'s cost: ')
        while (int(weight) < 1 or weight[0] == '-'):
            weight = input(f'Not a valid cost, please re-enter the new link\'s cost: ')
        src_update = (G.get_edge_data(src.name, dst.name).get('weight') == src.routing_table.get(str(dst.name)))
        dst_update = (G.get_edge_data(src.name, dst.name).get('weight') == dst.routing_table.get(str(src.name)))
        G.add_edge(src.name, dst.name, weight = int(weight))
        if (src_update):
            src.direct_link[dst.name] = True
            src.routing_table[str(dst.name)] = int(weight)
        if (dst_update):
            dst.direct_link[src.name] = True
            dst.routing_table[str(src.name)] = int(weight)
        src_update = (G.get_edge_data(src.name, dst.name).get('weight') < src.routing_table.get(str(dst.name)))
        dst_update = (G.get_edge_data(src.name, dst.name).get('weight') < dst.routing_table.get(str(src.name)))
        if(src_update):
            src.direct_link[dst.name] = True
            src.routing_table[str(dst.name)] = int(weight)
        if(dst_update):
            dst.direct_link[src.name] = True
            dst.routing_table[str(src.name)] = int(weight)
        src.bellman_ford(src.routing_table, src.send_port)
        dst.bellman_ford(dst.routing_table, dst.send_port)
    else:
        print(f'There is no link to edit between router number {src.name} and router number {dst.name}')

def add_router():
    name = input('Please enter router number, to return to menu enter 0: ')
    while (int(name) in G.nodes and name != '0'):
        name = input(f'Router number {name} is already available in network, try again, to return to menu enter 0: ')
    if(name == '0'):
        return
    adj = ''
    while adj != '0':
        adj = input(f'Now please enter number of a connected router to router number {name}, if you\'re done enter 0: ')
        if (adj == '0'):
            break
        while ((int(adj) not in G.nodes) and (adj != '0')) or (int(adj) == int(name)):
            adj = input(f'you have entered invalid router number, try again or enter 0: ')
        if (adj != '0'):
            weight = input(f'Enter the cost of link between router number {name} and router number {adj}: ')
            while(int(weight) < 1 or weight[0] == '-'):
                weight = input(f'This cost is not acceptable, please re-enter the cost of link between router number {name} and router number {adj}: ')

            G.add_edge(int(name), int(adj), weight= int(weight))
    G.add_node(int(name))
    neighbors = []
    for r in Routers:
        if(r.name in G[int(name)]):
            neighbors.append(r)
    router = Router(int(name), neighbors)
    Routers.append(router)
    for r in Routers:
        if (r == router):
            continue
        if(G.has_edge(r.name, router.name)):
            r.routing_table[str(router.name)] = G.get_edge_data(r.name, router.name).get('weight')
        else:
            r.routing_table[str(router.name)] = math.inf
    send_thread = threading.Thread(target= router.send_to_adj).start() #permanant thread for sending to neighbours
    rcv_thread = threading.Thread(target= router.recieve_from_adj).start() #permanant thread for listening from neighbours
    # time.sleep(5)
    show_topology()

def remove_router(R):
    for r in Routers:
        if(r.direct_link[R.name]):
            r.routing_table[str(R.name)] = math.inf
            r.direct_link[R.name] = False
    G.remove_node(int(R.name))
    to_be_removed = Router
    for r in Routers:
        if (r.name == R.name):
            to_be_removed = r
            break
    Routers.remove(to_be_removed)
    del R

def show_topology():
    layout = nx.spectral_layout(G)
    # layout = nx.random_layout(G)
    nx.draw(G, layout, with_labels=True, font_weight='bold')
    edge_weight = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, layout, edge_labels=edge_weight)
    plt.show()

def print_menu():
    print('○•○•○•○•○•○•○•○•○•○•○•○•○•○•○•○•○•○•○•○•○•○•○•○•○•○•○')
    print('•○•○•○•○•○•○•○•○•○•○•○•○•○•○•○•○•○•○•○•○•○•○•○•○•○•○•')
    print('             Distance Vector Routing')
    print(' 1. Show The Cheapest Path    2. Show Routing Table ')
    print(' 3. Edit Some Links           4. Add Router ')
    print(' 5. Remove A Router           6. Show Topology ')
    print('                    7. Exit ')
    print('○•○•○•○•○•○•○•○•○•○•○•○•○•○•○•○•○•○•○•○•○•○•○•○•○•○•○')
    print('•○•○•○•○•○•○•○•○•○•○•○•○•○•○•○•○•○•○•○•○•○•○•○•○•○•○•')

def main():


    choice = -1
    while choice != 7:
        print_menu()
        choice = int(input('What is your choice: '))
        while choice not in [1, 2, 3, 4, 5, 6, 7]:
            print(f'{choice} is not a valid selection...')
            choice = input('What is your choice: ')
        if(choice == 1):
            r1 = r2 = ''
            r1 = input('Enter the source router number: ')
            while (int(r1) not in G.nodes and r1 != '0'):
                r1 = input(f'Router number {r1} is not available in network, try another one, to return to menu enter 0: ')
            if(r1 != '0'):
                r2 = input('Enter the destination router number: ')
                while (((int(r2) not in G.nodes) or (int(r2) == int(r1))) and r2 != '0'):
                    r2 = input(f'Entered an invalid router number, try another one, to return to menu enter 0: ')
            if(r2 != '0' and r1 != '0'):
                src = dst = Router
                for i in Routers:
                    if i.name == int(r1):
                        src = i
                        break
                for i in Routers:
                    if i.name == int(r2):
                        dst = i
                        break
                cheapest_path(src, dst)
            # shortest_path()
        elif(choice == 2):
            r = input('Enter the router number, to return to menu enter 0: ')
            while(int(r) not in G.nodes and r != '0'):
                r = input(f'Router number {r} is not available in network, try another one, to return to menu enter 0: ')
            if(r == '0'):
                break
            R = Router
            for i in Routers:
                if i.name == int(r):
                    R = i
                    break
            show_routing_table(R)
        elif(choice == 3):
            r1 = input('Enter the source router number, to return to menu enter 0: ')
            while (int(r1) not in G.nodes and r1 != '0'):
                r1 = input(f'Router number {r1} is not available in network, try another one, to return to menu enter 0: ')
            if(r1 == '0'):
                continue
            r2 = input('Enter the destination router number: ')
            while (int(r2) not in G.nodes) or (int(r2) == int(r1)):
                r2 = input(f'Entered an invalid router number, try another one: ')
            src = dst = Router
            for i in Routers:
                if i.name == int(r1):
                    src = i
                    break
            for i in Routers:
                if i.name == int(r2):
                    dst = i
                    break
            edit_link(src, dst)
        elif(choice == 4):
            add_router()
        elif(choice == 5):
            r = input('Enter the router number, to return to menu enter 0: ')
            while (int(r) not in G.nodes and r != '0'):
                r = input(f'Router number {r} is not available in network, try another one, to return to menu enter 0: ')
            if(r == '0'):
                continue
            R = Router
            for i in Routers:
                if i.name == int(r):
                    R = i
                    break
            remove_router(R)
        elif(choice == 6):
            show_topology()


main()