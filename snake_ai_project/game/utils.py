from collections import deque
from heapq import heappop, heappush
from math import inf


GridPos = tuple[int, int]


def manhattan_distance(a: GridPos, b: GridPos) -> int:
	return abs(a[0] - b[0]) + abs(a[1] - b[1])


def _neighbors(pos: GridPos, grid_width: int, grid_height: int):
	x, y = pos
	candidates = ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1))

	for nx, ny in candidates:
		if 0 <= nx < grid_width and 0 <= ny < grid_height:
			yield (nx, ny)


def _reconstruct_path(came_from: dict[GridPos, GridPos], current: GridPos) -> list[GridPos]:
	path = [current]
	while current in came_from:
		current = came_from[current]
		path.append(current)
	path.reverse()
	return path


def a_star_search(
	start: GridPos,
	goal: GridPos,
	blocked_cells: set[GridPos],
	grid_width: int,
	grid_height: int,
) -> list[GridPos]:
	if start == goal:
		return [start]

	blocked = set(blocked_cells)
	blocked.discard(start)
	blocked.discard(goal)

	open_heap = []
	heappush(open_heap, (manhattan_distance(start, goal), 0, start))

	came_from: dict[GridPos, GridPos] = {}
	g_score: dict[GridPos, float] = {start: 0}

	while open_heap:
		_, current_g, current = heappop(open_heap)

		if current == goal:
			return _reconstruct_path(came_from, current)

		if current_g > g_score.get(current, inf):
			continue

		for neighbor in _neighbors(current, grid_width, grid_height):
			if neighbor in blocked:
				continue

			tentative_g = current_g + 1
			if tentative_g < g_score.get(neighbor, inf):
				came_from[neighbor] = current
				g_score[neighbor] = tentative_g
				f_score = tentative_g + manhattan_distance(neighbor, goal)
				heappush(open_heap, (f_score, tentative_g, neighbor))

	return []


def reachable_cell_count(
	start: GridPos,
	blocked_cells: set[GridPos],
	grid_width: int,
	grid_height: int,
) -> int:
	blocked = set(blocked_cells)

	if start in blocked:
		return 0

	x, y = start
	if not (0 <= x < grid_width and 0 <= y < grid_height):
		return 0

	visited = {start}
	queue = deque([start])

	while queue:
		current = queue.popleft()
		for neighbor in _neighbors(current, grid_width, grid_height):
			if neighbor in blocked or neighbor in visited:
				continue
			visited.add(neighbor)
			queue.append(neighbor)

	return len(visited)
