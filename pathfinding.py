import heapq

def dijkstras(grid_data):
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    player_pos = grid_data['start']
    goal_pos = grid_data['goal']
    grid = grid_data['grid']

    # print(player_pos)

    shortest_path = {}
    minHeap = [[0, tuple(player_pos)]]

    while minHeap:
        current_cost, current = heapq.heappop(minHeap)

        if current in shortest_path:
            continue
        
        shortest_path[current] = current_cost

        for direction in directions:
            next = (current[0] + direction[0], current[1] + direction[1])
            
            if next == tuple(goal_pos):
                # print("Goal found!")
                # Reconstruct path from goal back to start
                path = []
                current_node = next
                while current_node != tuple(player_pos):
                    path.append(current_node)
                    # Find neighbor with minimum path cost
                    min_cost = float('inf')
                    min_neighbor = None
                    for d in directions:
                        neighbor = (current_node[0] - d[0], current_node[1] - d[1])
                        if neighbor in shortest_path and shortest_path[neighbor] < min_cost:
                            min_cost = shortest_path[neighbor]
                            min_neighbor = neighbor
                    current_node = min_neighbor
                path.append(tuple(player_pos))
                path.reverse()
                # print(path)
                return path
            # print(next)

            if next[0] < 0 or next[0] >= len(grid[0]) or next[1] < 0 or next[1] >= len(grid):
                continue

            elif grid[next[1]][next[0]] == 1:
                next_cost = float('inf')
            else:
                next_cost = current_cost + 1

            heapq.heappush(minHeap, [next_cost, tuple(next)])

    return []