#!/usr/bin/env python
import GuiTextArea, RouterPacket, F
from copy import deepcopy

class RouterNode():
    myID = None
    myGUI = None
    sim = None
    costs = None

    # Access simulator variables with:
    # self.sim.POISONREVERSE, self.sim.NUM_NODES, etc.

    # --------------------------------------------------
    def __init__(self, ID, sim, costs):
        self.myID = ID
        self.sim = sim
        self.myGUI = GuiTextArea.GuiTextArea("  Output window for Router #" + str(ID) + "  ")
        self.costs = deepcopy(costs)
        self.costs_table = {}
        self.route_table = {}
        self.route_table[self.myID] = self.myID

        # Set up costs tables
        self.costs_table[self.myID] = deepcopy(self.costs)
        for node in range(self.sim.NUM_NODES):
            if node != self.myID:
                self.costs_table[node] = [self.sim.INFINITY]*self.sim.NUM_NODES
                self.route_table[node] = self.sim.INFINITY

        # Set up neighbors
        self.neighbors = []
        for i in range (len(costs)):
            if self.costs[i] != self.sim.INFINITY and i != ID:
                self.neighbors.append(i)

        for neighbor in self.neighbors:
            self.route_table[neighbor] = neighbor
            neighbor_pkt = RouterPacket.RouterPacket(self.myID, neighbor, self.costs)
            self.sendUpdate(neighbor_pkt)

    # --------------------------------------------------
    def recvUpdate(self, pkt):
        self.costs_table[pkt.sourceid] = pkt.mincost

        temp_self_costs = deepcopy(self.costs)

        table_updated = False

        for target_node in range(self.sim.NUM_NODES):
            if target_node == self.myID:
                continue

            min_distance = self.sim.INFINITY
            best_neighbor = target_node

            if target_node in self.neighbors: # If there's a direct path, set min_distance to that
                min_distance = temp_self_costs[target_node]

            for neighbor in range(self.sim.NUM_NODES): # Bellman ford
                if neighbor == self.myID:
                    continue

                distance_via_neighbor = (self.costs_table[neighbor][target_node] + temp_self_costs[neighbor])

                if distance_via_neighbor < min_distance:
                    min_distance = distance_via_neighbor
                    best_neighbor = neighbor

            if self.costs_table[self.myID][target_node] != min_distance:
                self.costs_table[self.myID][target_node] = min_distance
                self.route_table[target_node] = best_neighbor
                table_updated = True

            if table_updated:
                for neighbor in self.neighbors:
                    new_distances = deepcopy(self.costs_table[self.myID])
                    
                    if self.sim.POISONREVERSE:
                        for dest in range(self.sim.NUM_NODES):
                            if self.route_table.get(dest) == neighbor and dest != neighbor:
                                new_distances[dest] = self.sim.INFINITY
                    
                    update_packet = RouterPacket.RouterPacket(self.myID, neighbor, new_distances)
                    self.sendUpdate(update_packet)


    # --------------------------------------------------
    def sendUpdate(self, pkt):
        self.sim.toLayer2(pkt)


    # --------------------------------------------------
    def printDistanceTable(self):
        self.myGUI.println("Current table for " + str(self.myID) +
                           "  at time " + str(self.sim.getClocktime()))
        
        output = f"[{self.myID}] Distancetable:\n"
        # --- Distancetable ---
        header_row = "{:>8}".format("dst ") + "|"
        for nb in range(self.sim.NUM_NODES):
            header_row += "{:>5}".format(nb)

        output += header_row + "\n" + "-"*len(header_row) + "\n"

        for nb in self.neighbors:
            output += "{:>8}".format(f"nbr {nb} ") + "|"
            for cost in self.costs_table[nb]:
                output += "{:>5}".format(cost)
            output += "\n"

        # --- Vector and routes ---
        route_output = f"Our distance vector and routes:\n" + header_row + "\n" + "-"*len(header_row) + "\n"
        route_output += " cost   |"

        # for cost in self.costs: #If print costs instead of costs_table
        for cost in self.costs_table[self.myID]:
            route_output += "{:>5}".format(cost)

        route_output += "\n route  |"
        for node in range(self.sim.NUM_NODES):
            if self.route_table[node] != self.sim.INFINITY:
                route_output += "{:>5}".format(self.route_table[node])
            else:
                route_output += "{:>5}".format("-")

        self.myGUI.println( output + "\n" + route_output)

    # --------------------------------------------------
    def updateLinkCost(self, dest, newcost):
        self.costs[dest] = newcost
        self.costs_table[self.myID][dest] = newcost

        for neighbor in self.neighbors:
           
            if self.sim.POISONREVERSE:
                for dest in range(self.sim.NUM_NODES):
                    if self.route_table.get(dest) == neighbor and dest != neighbor:
                        self.costs_table[self.myID][dest] = self.sim.INFINITY
                            
            update_packet = RouterPacket.RouterPacket(self.myID, neighbor, self.costs_table[neighbor])
            self.sendUpdate(update_packet)
