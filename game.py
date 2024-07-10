import pygame
import random

# Répertoire de travail
# Initialisation de pygame
pygame.init()

# Dimensions de la fenêtre et de la carte
scorewin = 500
tile_size = 30
size = 20
width, height = size * tile_size, size * tile_size
interface_height = 100  # Hauteur supplémentaire pour l'interface

# Couleurs
PASSABLE_COLOR = (200, 200, 200)        # Gris clair pour les cases passables
PLAYER_COLOR = (0, 0, 255)              # Bleu pour le joueur
PLAYER_COLOR_LIGHT = (100, 100, 255)    # Bleu clair pour le joueur capable de bouger
ENEMY_COLOR = (255, 0, 0)               # Rouge pour les ennemis
ENEMY_COLOR_LIGHT = (255, 100, 100)     # Rouge clair pour les ennemis capables de bouger
SELECTED_COLOR = (0, 255, 0)            # Vert pour la sélection
OBJECTIVE_MAJOR_COLOR = (255, 255, 0)   # Jaune pour objectif majeur
OBJECTIVE_MINOR_COLOR = (255, 215, 0)   # Doré pour objectif mineur

# Classe pour les unités
class Unit:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.selected = False
        self.moved = False  # Indicateur de mouvement pour le tour
        self.pv = 2  # Points de Vie
        self.attacked_this_turn = False  # Indicateur d'attaque dans ce tour

    def draw(self, screen, units, objectives):
        """Affiche l'unité sur l'écran."""
        rect = pygame.Rect(self.x * tile_size, self.y * tile_size, tile_size, tile_size)
        if not self.moved:
            color = PLAYER_COLOR_LIGHT if self.color == PLAYER_COLOR else ENEMY_COLOR_LIGHT
        else:
            color = self.color
        pygame.draw.rect(screen, color, rect)

        if self.selected:
            pygame.draw.rect(screen, SELECTED_COLOR, rect, 3)

        font = pygame.font.SysFont(None, 16)
        symbols = self.get_symbols_on_same_tile(units)
        combined_text = font.render(symbols, True, (255, 255, 255))
        text_width = combined_text.get_width()
        text_x = self.x * tile_size + (tile_size - text_width) // 2
        screen.blit(combined_text, (text_x, self.y * tile_size + 5))

        for obj in objectives:
            if self.x == obj['x'] and self.y == obj['y']:
                pygame.draw.rect(screen, (0, 255, 0), rect, 1)

    def can_move(self, x, y):
        """Vérifie si l'unité peut se déplacer vers une case."""
        if 0 <= x < size and 0 <= y < size:
            if abs(self.x - x) <= 1 and abs(self.y - y) <= 1:
                return True
        return False

    def move(self, x, y):
        """Déplace l'unité vers une case spécifiée."""
        self.x = x
        self.y = y
        self.moved = True

    def attack(self, target_unit, units, objectives):
        """Attaque une unité ennemie."""
        if self.can_move(target_unit.x, target_unit.y):
            dx = target_unit.x - self.x
            dy = target_unit.y - self.y
            new_x, new_y = target_unit.x + dx, target_unit.y + dy

            if target_unit.attacked_this_turn:
                target_unit.pv -= 1
                if target_unit.pv <= 0:
                    units.remove(target_unit)
                    return

            if not (0 <= new_x < size and 0 <= new_y < size) or any(u.x == new_x and u.y == new_y for u in units):
                units.remove(target_unit)
            else:
                target_unit.move(new_x, new_y)
                self.move(target_unit.x, target_unit.y)
                target_unit.attacked_this_turn = True


    def get_symbols_on_same_tile(self, units):
        """Retourne les symboles des unités sur la même case."""
        symbols = [u.get_symbol() for u in units if u.x == self.x and u.y == self.y]
        return ' '.join(symbols)

    def get_symbol(self):
        """Retourne le symbole de l'unité."""
        return "U"

# Générer la carte
def generate_map(size):
    """Génère une carte de taille spécifiée."""
    return [[1 for _ in range(size)] for _ in range(size)]

# Afficher la carte
def draw_map(screen, game_map, tile_size):
    """Affiche la carte."""
    for y in range(size):
        for x in range(size):
            color = PASSABLE_COLOR
            pygame.draw.rect(screen, color, (x * tile_size, y * tile_size, tile_size, tile_size))

# Générer des unités sur des cases passables uniquement
def generate_units():
    """Génère les unités pour les joueurs et les ennemis."""
    units = []
    player_positions = [(0, i) for i in range(size)]
    enemy_positions = [(size - 1, i) for i in range(size)]

    player_positions = random.sample(player_positions, 5)
    enemy_positions = random.sample(enemy_positions, 5)

    player_units = [Unit(*pos, PLAYER_COLOR) for pos in player_positions]
    enemy_units = [Unit(*pos, ENEMY_COLOR) for pos in enemy_positions]
    
    units.extend(player_units)
    units.extend(enemy_units)
    
    return units

# Ajouter des objectifs à la carte
def add_objectives():
    """Ajoute des objectifs à la carte."""
    objectives = []
    center_x, center_y = size // 2, size // 2
    while True:
        x, y = random.randint(center_x - 3, center_x + 3), random.randint(center_y - 3, center_y + 3)
        if not any(obj['x'] == x and obj['y'] == y for obj in objectives):
            objectives.append({'x': x, 'y': y, 'type': 'MAJOR'})
            break

    for _ in range(3):
        while True:
            x, y = random.randint(center_x - 5, center_x + 5), random.randint(center_y - 5, center_y + 5)
            if not any(obj['x'] == x and obj['y'] == y for obj in objectives):
                objectives.append({'x': x, 'y': y, 'type': 'MINOR'})
                break

    return objectives

# Afficher les objectifs
def draw_objectives(screen, objectives, tile_size):
    """Affiche les objectifs sur la carte."""
    for obj in objectives:
        color = OBJECTIVE_MAJOR_COLOR if obj['type'] == 'MAJOR' else OBJECTIVE_MINOR_COLOR
        pygame.draw.rect(screen, color, (obj['x'] * tile_size, obj['y'] * tile_size, tile_size, tile_size))

# Calculer les scores
def calculate_scores(units, objectives):
    """Calcule les scores des joueurs et des ennemis en fonction des objectifs contrôlés."""
    player_score = 0
    enemy_score = 0

    for obj in objectives:
        if any(unit.x == obj['x'] and unit.y == obj['y'] and unit.color == PLAYER_COLOR for unit in units):
            player_score += 3 if obj['type'] == 'MAJOR' else 1
        elif any(unit.x == obj['x'] and unit.y == obj['y'] and unit.color == ENEMY_COLOR for unit in units):
            enemy_score += 3 if obj['type'] == 'MAJOR' else 1

    return player_score, enemy_score

# Afficher le message de changement de tour
def draw_turn_indicator(screen, player_turn):
    """Affiche l'indicateur de tour."""
    font = pygame.font.SysFont(None, 36)
    text = "Joueur" if player_turn else "Ennemi"
    img = font.render(text, True, (255, 255, 255))
    screen.blit(img, (10, 10))

# Afficher le bouton de changement de tour
def draw_end_turn_button(screen, width, height, interface_height):
    """Affiche le bouton de fin de tour."""
    font = pygame.font.SysFont(None, 36)
    text = font.render("Terminé", True, (255, 255, 255))
    button_rect = pygame.Rect(width // 2 - 50, height, 100, interface_height - 10)
    pygame.draw.rect(screen, (100, 100, 100), button_rect)
    screen.blit(text, (width // 2 - 50 + 10, height + 10))

# Vérifier si le bouton de changement de tour est cliqué
def end_turn_button_clicked(mouse_pos, width, height, interface_height):
    """Vérifie si le bouton de fin de tour a été cliqué."""
    x, y = mouse_pos
    button_rect = pygame.Rect(width // 2 - 50, height, 100, interface_height - 10)
    return button_rect.collidepoint(x, y)

# Afficher les attributs de l'unité sélectionnée
def draw_unit_attributes(screen, unit, width, height, interface_height):
    """Affiche les attributs de l'unité sélectionnée."""
    if unit:
        font = pygame.font.SysFont(None, 24)
        pv_text = f"PV: {unit.pv} / 2"
        unit_img = font.render("Unité", True, (255, 255, 255))
        pv_img = font.render(pv_text, True, (255, 255, 255))
        screen.blit(unit_img, (10, height + 10))
        screen.blit(pv_img, (10, height + 40))

# Afficher les scores
def draw_scores(screen, player_score, enemy_score, width, height):
    """Affiche les scores des joueurs."""
    font = pygame.font.SysFont(None, 24)
    player_score_text = f"Score Joueur: {player_score}"
    enemy_score_text = f"Score Ennemi: {enemy_score}"
    player_score_img = font.render(player_score_text, True, (255, 255, 255))
    enemy_score_img = font.render(enemy_score_text, True, (255, 255, 255))
    screen.blit(player_score_img, (10, height + 70))
    screen.blit(enemy_score_img, (width - 150, height + 70))

# Afficher le message de victoire
def draw_victory_message(screen, message, width, height):
    """Affiche le message de victoire."""
    font = pygame.font.SysFont(None, 48)
    victory_img = font.render(message, True, (255, 255, 255))
    screen.blit(victory_img, (width // 2 - 100, height // 2 - 24))

# Fonction pour envoyer des unités vers les objectifs
def goObjectif(units, objectives):
    enemy_units = [unit for unit in units if unit.color == ENEMY_COLOR and not unit.moved]
    
    # Privilégier l'attaque des unités ennemies
    for unit in enemy_units:
        adjacent_enemies = [u for u in units if u.color == PLAYER_COLOR and abs(unit.x - u.x) <= 1 and abs(unit.y - u.y) <= 1]
        
        if adjacent_enemies:
            for enemy in adjacent_enemies:
                if unit.can_move(enemy.x, enemy.y):
                    unit.attack(enemy, units, objectives)
            continue

    # Assigner des unités aux objectifs restants
    assigned_units = []
    for obj in objectives:
        if enemy_units:
            closest_unit = min(enemy_units, key=lambda unit: abs(unit.x - obj['x']) + abs(unit.y - obj['y']))
            assigned_units.append(closest_unit)
            enemy_units.remove(closest_unit)
            dx = obj['x'] - closest_unit.x
            dy = obj['y'] - closest_unit.y
            move_x = closest_unit.x + (1 if dx > 0 else -1 if dx < 0 else 0)
            move_y = closest_unit.y + (1 if dy > 0 else -1 if dy < 0 else 0)
            if closest_unit.can_move(move_x, move_y):
                closest_unit.move(move_x, move_y)
    
    # Envoyer le reste des unités au centre de la carte
    center_x, center_y = size // 2, size // 2
    for unit in enemy_units:
        dx = center_x - unit.x
        dy = center_y - unit.y
        move_x = unit.x + (1 if dx > 0 else -1 if dx < 0 else 0)
        move_y = unit.y + (1 if dy > 0 else -1 if dy < 0 else 0)
        if unit.can_move(move_x, move_y):
            unit.move(move_x, move_y)


def appellerAide(units):
    for unit in units:
        if unit.color == ENEMY_COLOR:
            enemies_in_range = [u for u in units if u.color == PLAYER_COLOR and abs(unit.x - u.x) <= 1 and abs(unit.y - u.y) <= 1]
            if len(enemies_in_range) == 1:
                ally_in_range = [u for u in units if u.color == ENEMY_COLOR and abs(unit.x - u.x) <= 2 and abs(unit.y - u.y) <= 2 and u != unit]
                if ally_in_range:
                    closest_ally = min(ally_in_range, key=lambda u: abs(unit.x - u.x) + abs(unit.y - u.y))
                    dx = unit.x - closest_ally.x
                    dy = unit.y - closest_ally.y
                    move_x = closest_ally.x + (1 if dx < 0 else -1 if dx > 0 else 0)
                    move_y = closest_ally.y + (1 if dy < 0 else -1 if dy > 0 else 0)
                    if closest_ally.can_move(move_x, move_y):
                        closest_ally.move(move_x, move_y)


def tuePlayerUnite(units):
    for unit in units:
        if unit.color == ENEMY_COLOR:
            enemies_in_range = [u for u in units if u.color == PLAYER_COLOR and abs(unit.x - u.x) <= 1 and abs(unit.y - u.y) <= 1]
            if len(enemies_in_range) == 1:
                target_unit = enemies_in_range[0]
                allies_in_range = [u for u in units if u.color == ENEMY_COLOR and abs(target_unit.x - u.x) <= 1 and abs(target_unit.y - u.y) <= 1 and u != unit]
                if len(allies_in_range) >= 1:
                    dx = target_unit.x - unit.x
                    dy = target_unit.y - unit.y
                    new_x, new_y = target_unit.x + dx, target_unit.y + dy

                    if target_unit.attacked_this_turn:
                        target_unit.pv -= 1
                        if target_unit.pv <= 0:
                            units.remove(target_unit)
                            return

                    if not (0 <= new_x < size and 0 <= new_y < size) or any(u.x == new_x and u.y == new_y for u in units):
                        units.remove(target_unit)
                    else:
                        target_unit.move(new_x, new_y)
                        unit.move(target_unit.x, target_unit.y)
                        target_unit.attacked_this_turn = True


# Fonction principale pour gérer l'IA ennemie
def enemiIA(units, objectives, taille):
    matrix = [[0 for _ in range(taille)] for _ in range(taille)]
    for u in units:
        if u.color == PLAYER_COLOR:
            matrix[u.y][u.x] = 3
        elif u.color == ENEMY_COLOR and not u.moved:
            matrix[u.y][u.x] = 7
    for elt in objectives:
        if elt["type"] == "MINOR":
            matrix[elt["y"]][elt["x"]] = 1
        else:
            matrix[elt["y"]][elt["x"]] = 2
    
    rayon = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    
    for u in units:
        if u.color == PLAYER_COLOR:
            nbr = 0
            for dx, dy in rayon:
                nx, ny = u.x + dx, u.y + dy
                if 0 <= nx < taille and 0 <= ny < taille:
                    unit = matrix[ny][nx]
                    if unit == 7:
                        nbr += 1
            
            if nbr > 1:
                tuePlayerUnite(units)
            elif nbr == 1:
                appellerAide(units)
            else:
                goObjectif(units, objectives)


# Configuration de la fenêtre
screen = pygame.display.set_mode((width, height + interface_height))
pygame.display.set_caption("Carte de 20x20 avec unités et déplacement")

# Générer une carte de 20 par 20
game_map = generate_map(size)

# Générer les unités
units = generate_units()

# Ajouter des objectifs
objectives = add_objectives()

selected_unit = None
player_turn = True  # True pour le tour du joueur, False pour le tour de l'ennemi
units_to_move = [unit for unit in units if (unit.color == PLAYER_COLOR if player_turn else unit.color == ENEMY_COLOR)]
player_score = 0
enemy_score = 0
victory = False
victory_message = ""

# Boucle principale du jeu
running = True
while running:
    if not victory:
        unit_moved = False
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    unit_moved = True
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if end_turn_button_clicked((x, y), width, height, interface_height):
                    unit_moved = True
                else:
                    grid_x, grid_y = x // tile_size, y // tile_size
                    if event.button == 1:  # Clic gauche pour sélectionner
                        possible_units = [u for u in units if u.x == grid_x and u.y == grid_y and not u.moved and u.color == (PLAYER_COLOR if player_turn else ENEMY_COLOR)]
                        if selected_unit in possible_units:
                            current_index = possible_units.index(selected_unit)
                            selected_unit.selected = False
                            selected_unit = possible_units[(current_index + 1) % len(possible_units)]
                        else:
                            if selected_unit:
                                selected_unit.selected = False
                            if possible_units:
                                selected_unit = possible_units[0]
                        if selected_unit:
                            selected_unit.selected = True

                    elif event.button == 3:  # Clic droit pour déplacer ou attaquer
                        if selected_unit and selected_unit.color == (PLAYER_COLOR if player_turn else ENEMY_COLOR):
                            target_unit = [u for u in units if u.x == grid_x and u.y == grid_y and u.color != selected_unit.color]
                            
                            for cible in target_unit:
                                selected_unit.attack(cible, units, objectives)
                                
                            if selected_unit.can_move(grid_x, grid_y):
                                selected_unit.move(grid_x, grid_y)
                                selected_unit.selected = False
                                selected_unit = None

        if unit_moved:
            for unit in units_to_move:
                unit.moved = False  # Réinitialiser l'indicateur de mouvement
                unit.attacked_this_turn = False  # Réinitialiser l'indicateur d'attaque
            player_turn = not player_turn
            units_to_move = [unit for unit in units if (unit.color == PLAYER_COLOR if player_turn else unit.color == ENEMY_COLOR)]
            
            if not player_turn:  # C'est le tour de l'IA ennemie
                enemiIA(units, objectives, size)  # Passer la taille ici
            
            player_score_turn, enemy_score_turn = calculate_scores(units, objectives)
            player_score += player_score_turn
            enemy_score += enemy_score_turn

            if player_score >= scorewin:
                victory = True
                victory_message = "Victoire Joueur!"
            elif enemy_score >= scorewin:
                victory = True
                victory_message = "Victoire Ennemi!"
            elif not any(unit.color == PLAYER_COLOR for unit in units):
                victory = True
                victory_message = "Victoire Ennemi!"
            elif not any(unit.color == ENEMY_COLOR for unit in units):
                victory = True
                victory_message = "Victoire Joueur!"

            pygame.display.flip()

    screen.fill((0, 0, 0))
    draw_map(screen, game_map, tile_size)
    draw_objectives(screen, objectives, tile_size)
    
    for unit in units:
        unit.draw(screen, units, objectives)

    draw_turn_indicator(screen, player_turn)
    draw_end_turn_button(screen, width, height, interface_height)
    draw_unit_attributes(screen, selected_unit, width, height, interface_height)
    draw_scores(screen, player_score, enemy_score, width, height)

    if victory:
        draw_victory_message(screen, victory_message, width, height)
        pygame.display.flip()
        pygame.time.wait(5000)
        running = False

    pygame.display.flip()

pygame.quit()