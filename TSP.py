import numpy as np
import matplotlib.pyplot as plt
import random
from matplotlib.widgets import Button  

# PARAMETRY ALGORYTMU 
POPULATION_SIZE = 500
GENERATIONS = 3000
MUTATION_RATE = 0.65
ELITISM_SIZE = 4
GENERATION_RATE = 50
TOURNAMENT_SELECTION_SIZE = 3

cities = np.array([]) 
distance_matrix = np.array([]) 

# Funkcja wczytywania z pliku
def load_tsplib_berlin(filepath):
    data = np.loadtxt(filepath)
    return data[:, 1:]

# Funkcja do tworzenia macierzy odległości
def calculate_distance_matrix(coords):
    num_cities = len(coords)
    matrix = np.zeros((num_cities, num_cities))
    for i in range(num_cities):
        for j in range(num_cities):
            matrix[i, j] = np.linalg.norm(coords[i] - coords[j])
    return matrix

# Funkcja do liczenia całkowitego dystansu
def route_distance(route):
    dist = 0
    for i in range(len(route)): 
        dist += distance_matrix[route[i], route[(i + 1) % len(route)]]
    return dist 

# Algorytm najbliższego sąsiada
def get_best_nearest_neighbor(num_cities, dist_matrix):
    best_dist = float('inf')
    
    for start in range(num_cities):
        unvisited = set(range(num_cities))
        unvisited.remove(start)
        current = start
        current_dist = 0
        
        while unvisited:
            nearest = min(unvisited, key=lambda city: dist_matrix[current, city])
            current_dist += dist_matrix[current, nearest]
            current = nearest
            unvisited.remove(current)
            
        current_dist += dist_matrix[current, start]
        if current_dist < best_dist:
            best_dist = current_dist
            
    return best_dist

# Inicjalizacja początkowej populacji
def create_starting_population(size, num_cities):
    population = []
    all_cities = list(range(num_cities))
    for i in range(size):
        new_route = random.sample(all_cities, num_cities)
        population.append(new_route)
    return population 

# Selekcja ruletkowa
def selection_roulette(population, fitness_scores, total_fitness):
    pick = random.uniform(0, total_fitness)
    current = 0
    for i, fitness in enumerate(fitness_scores):
        current += fitness
        if current > pick:
            return population[i]
    return population[-1]

# Selekcja turniejowa
def selection_tournament(population, k):
    competitors = random.sample(population, k)
    return min(competitors, key=route_distance)

# Selekcja rankingowa
def selection_rank(population):
    n = len(population)
    ranks = list(range(n, 0, -1)) 
    total_ranks = sum(ranks)
    pick = random.uniform(0, total_ranks)
    current = 0
    for i, rank in enumerate(ranks):
        current += rank
        if current > pick:
            return population[i]
    return population[-1]

# Funkcja crossover
def crossover(parent1, parent2):
    length = len(parent1)
    random_picked = random.sample(range(length), 2)
    picked_sorted = sorted(random_picked)
    start, end = picked_sorted[0], picked_sorted[1]

    child = [-1] * length 
    child[start:end] = parent1[start:end] 
    
    child_set = set(child[start:end]) 
    p2_left = [item for item in parent2 if item not in child_set] 
    
    index = 0
    for i in range(length): 
        if child[i] == -1: 
            child[i] = p2_left[index] 
            index += 1
    return child

# Mutacja swap
def mutate_swap(route):
    if random.random() < MUTATION_RATE: 
        length = len(route)
        random_picked = random.sample(range(length), 2)
        i, j = random_picked[0], random_picked[1]
        route[i], route[j] = route[j], route[i] 
    return route

# Mutacja inwersja
def mutate_inversion(route):
    if random.random() < MUTATION_RATE: 
        length = len(route)
        random_picked = random.sample(range(length), 2)
        start, end = min(random_picked), max(random_picked)
        route[start:end] = route[start:end][::-1] 
    return route


# Wczytanie danych wejściowych
try:
    cities = load_tsplib_berlin('berlin52.tsp')
except FileNotFoundError:
    print("Nie znaleziono pliku 'berlin52.tsp'!")
    exit()

NUM_CITIES = len(cities)
distance_matrix = calculate_distance_matrix(cities)
best_nn_distance = get_best_nearest_neighbor(NUM_CITIES, distance_matrix)

# Zmienne przechowujące wybory użytkownika
selection_choice = None
mutation_choice = None

def choose_roulette(event): 
    global selection_choice
    if selection_choice is None: selection_choice = '1'
def choose_tournament(event): 
    global selection_choice
    if selection_choice is None: selection_choice = '2'
def choose_rank(event): 
    global selection_choice
    if selection_choice is None: selection_choice = '3'

def choose_swap(event): 
    global mutation_choice
    if mutation_choice is None: mutation_choice = '1'
def choose_inversion(event): 
    global mutation_choice
    if mutation_choice is None: mutation_choice = '2'

# Inicjalizacja okna bez dolnego paska menu
plt.style.use('dark_background')
plt.rcParams['toolbar'] = 'None'  

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
fig.canvas.manager.set_window_title('Algorytm Genetyczny')
plt.ion()
plt.subplots_adjust(bottom=0.2)

# Przyciski Selekcji
ax_btn1 = plt.axes([0.25, 0.04, 0.14, 0.06])
ax_btn2 = plt.axes([0.43, 0.04, 0.14, 0.06])
ax_btn3 = plt.axes([0.61, 0.04, 0.14, 0.06])

btn_roulette = Button(ax_btn1, '1. Ruletkowa', color='#222222', hovercolor="#41CB78")
btn_tournament = Button(ax_btn2, '2. Turniejowa', color='#222222', hovercolor="#41CB78")
btn_rank = Button(ax_btn3, '3. Rankingowa', color='#222222', hovercolor="#41CB78")

btn_roulette.label.set_color('white')
btn_tournament.label.set_color('white')
btn_rank.label.set_color('white')

btn_roulette.on_clicked(choose_roulette)
btn_tournament.on_clicked(choose_tournament)
btn_rank.on_clicked(choose_rank)

# Przyciski Mutacji
ax_btn4 = plt.axes([0.34, 0.04, 0.14, 0.06])
ax_btn5 = plt.axes([0.52, 0.04, 0.14, 0.06])
ax_btn4.set_visible(False)
ax_btn5.set_visible(False)

btn_swap = Button(ax_btn4, '1. Swap', color='#222222', hovercolor="#00E5FF")
btn_inversion = Button(ax_btn5, '2. Inwersja', color='#222222', hovercolor="#00E5FF")
btn_swap.label.set_color('white')
btn_inversion.label.set_color('white')

btn_swap.on_clicked(choose_swap)
btn_inversion.on_clicked(choose_inversion)

ax1.set_xlim(-50, 1850); ax1.set_ylim(-50, 1250)
text_instruction = ax1.text(0.5, 0.5, "KROK 1/2: WYBIERZ TYP SELEKCJI", 
         horizontalalignment='center', verticalalignment='center', 
         transform=ax1.transAxes, fontsize=14, color='#41CB78', fontweight='bold')
ax2.axis('off') 
plt.draw()

# Oczekiwanie na wybór selekcji
while selection_choice is None:
    plt.pause(0.05)
    if not plt.fignum_exists(fig.number): exit()

plt.pause(0.1) 

ax_btn1.set_visible(False)
ax_btn2.set_visible(False)
ax_btn3.set_visible(False)
ax_btn4.set_visible(True)
ax_btn5.set_visible(True)

text_instruction.set_text("KROK 2/2: WYBIERZ TYP MUTACJI")
text_instruction.set_color('#00E5FF')
plt.draw()

# Oczekiwanie na wybór mutacji
while mutation_choice is None:
    plt.pause(0.05)
    if not plt.fignum_exists(fig.number): exit()

plt.pause(0.1) 

ax_btn4.set_visible(False)
ax_btn5.set_visible(False)

text_instruction.set_visible(False)

ax2.axis('on') 
plt.subplots_adjust(bottom=0.1) 
plt.pause(0.1) 

selection_names = {'1': "Ruletkowa", '2': "Turniejowa", '3': "Rankingowa"}
mutation_names = {'1': "Swap", '2': "Inwersja"}

# Start algorytmu genetycznego
population = create_starting_population(POPULATION_SIZE, NUM_CITIES)
best_route_global = None
best_distance_global = float('inf')

history_current = [] 
history_global = []

for generation in range(GENERATIONS):
    population = sorted(population, key=route_distance)
    current_best_dist = route_distance(population[0])
    
    if current_best_dist < best_distance_global:
        best_route_global = population[0].copy()
        best_distance_global = current_best_dist
        
    history_current.append(current_best_dist)
    history_global.append(best_distance_global)

    if generation % 10 == 0:
        fig.canvas.flush_events()

    if selection_choice == '1':
        fitness_scores = [1.0 / (route_distance(osobnik) + 1e-6) for osobnik in population]
        sum_fitness = sum(fitness_scores)

    new_population = population[:ELITISM_SIZE] 
    while len(new_population) < POPULATION_SIZE:
        if selection_choice == '1':
            p1 = selection_roulette(population, fitness_scores, sum_fitness)
            p2 = selection_roulette(population, fitness_scores, sum_fitness)
        elif selection_choice == '2':
            p1 = selection_tournament(population, TOURNAMENT_SELECTION_SIZE)
            p2 = selection_tournament(population, TOURNAMENT_SELECTION_SIZE)
        else:
            p1 = selection_rank(population)
            p2 = selection_rank(population)
            
        child = crossover(p1, p2)
        
        if mutation_choice == '1':
            child = mutate_swap(child)
        else:
            child = mutate_inversion(child)
            
        new_population.append(child)
        
    population = new_population

    if generation % GENERATION_RATE == 0: 
        if not plt.fignum_exists(fig.number):
            break

        ax1.clear()
        ax1.set_xlim(-50, 1850); ax1.set_ylim(-50, 1250)
        ax1.scatter(cities[:, 0], cities[:, 1], c='#FF5555', s=45, edgecolors='white', zorder=3, label='Miasta')
        route_coords = cities[best_route_global + [best_route_global[0]]]
        ax1.plot(route_coords[:, 0], route_coords[:, 1], c='#00E5FF', linewidth=2, zorder=2, label='Najlepsza trasa')
        ax1.set_title(f"Pokolenie: {generation}/{GENERATIONS}\nNajlepszy dystans: {best_distance_global:.2f}", fontsize=11, color='#FFFFFF')
        ax1.grid(True, linestyle=':', alpha=0.3, color='#888888')
        ax1.legend(loc='upper right')

        ax2.clear()
        ax2.plot(history_current, color='#41CB78', linewidth=1, alpha=0.6)
        ax2.plot(history_global, color='#00E5FF', linewidth=2, label='Globalne minimum')
        ax2.axhline(y=best_nn_distance, color='#FFA500', linestyle='-.', linewidth=1.5, label=f'N. Sasiad ({best_nn_distance:.0f})')
        ax2.axhline(y=7542, color='#FF3366', linestyle='--', linewidth=1.5, label='Optimum (7542)')
        
        ax2.set_title(f"Selekcja: {selection_names[selection_choice]} | Mutacja: {mutation_names[mutation_choice]}", fontsize=10, color='#FFFFFF')
        ax2.set_xlabel("Pokolenie")
        ax2.set_ylabel("Dystans")
        
        lowest_line_value = min(7542, best_nn_distance)
        ax2.set_ylim(bottom=lowest_line_value - 500)
        
        ax2.grid(True, linestyle=':', alpha=0.3, color='#888888')
        ax2.legend()

        plt.pause(0.001)

if plt.fignum_exists(fig.number):
    ax1.clear()
    ax1.set_xlim(-50, 1850); ax1.set_ylim(-50, 1250)
    ax1.scatter(cities[:, 0], cities[:, 1], c='#FF5555', s=45, edgecolors='white', zorder=3)
    route_coords = cities[best_route_global + [best_route_global[0]]]
    ax1.plot(route_coords[:, 0], route_coords[:, 1], c='#00E5FF', linewidth=2.5, zorder=2)
    ax1.set_title(f"KONIEC SYMULACJI\nNajkrotszy dystans: {best_distance_global:.2f}", fontsize=12, fontweight='bold', color='#00E5FF')
    ax1.grid(True, linestyle=':', alpha=0.3, color='#888888')

    ax2.clear()
    ax2.plot(history_current, color='#41CB78', linewidth=1, alpha=0.6)
    ax2.plot(history_global, color='#00E5FF', linewidth=2, label='Globalne minimum')
    ax2.axhline(y=best_nn_distance, color='#FFA500', linestyle='-.', linewidth=1.5, label=f'N. Sasiad ({best_nn_distance:.0f})')
    ax2.axhline(y=7542, color='#FF3366', linestyle='--', label='Optimum (7542)')
    
    ax2.set_title(f"Selekcja: {selection_names[selection_choice]} | Mutacja: {mutation_names[mutation_choice]}", fontsize=10, color='#FFFFFF')
    ax2.set_xlabel("Pokolenie")
    ax2.set_ylabel("Dystans")
    
    lowest_line_value = min(7542, best_nn_distance)
    ax2.set_ylim(bottom=lowest_line_value - 500)
    
    ax2.grid(True, linestyle=':', alpha=0.3, color='#888888')
    ax2.legend()

print()
print("=========== WYNIKI SYMULACJI ===========")
print(f"Wybrana selekcja:   {selection_names[selection_choice]}")
print(f"Wybrana mutacja:    {mutation_names[mutation_choice]}")
print(f"Wielkosc populacji: {POPULATION_SIZE}")
print(f"Liczba generacji:   {GENERATIONS}")
print(f"Najkrotsza trasa: {best_distance_global:.2f}")
print("========================================")
print()

plt.ioff()
plt.show(block=True)