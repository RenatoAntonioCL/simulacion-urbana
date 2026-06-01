"""view — la capa Pygame del cliente (ADR-0011).

Solo presentación: dibuja lo que el `SimController` expone y le manda eventos de input.
Sin lógica de simulación, sin mutar estado. Pygame se importa **aquí** (nunca en
`controller`/`layout`), de modo que el resto del cliente funciona y se testea sin display.
"""

from __future__ import annotations

import pygame

from . import layout
from .controller import SCREEN_CREATE, SCREEN_WORLD, SimController
from .paths import default_save_path

WIDTH, HEIGHT = 1100, 720
PANEL_W = 320          # ancho del panel de eventos (derecha)
BAR_H = 64             # alto de la barra de controles (abajo)
FPS = 60


def _load_font(size: int) -> "pygame.font.Font":
    """Fuente integrada de Pygame (freesansbold).

    Se prefiere a `SysFont` porque viaja con Pygame: en un ejecutable congelado
    (PyInstaller) no depende de que el SO tenga una fuente concreta instalada (ADR-0013).
    """
    return pygame.font.Font(None, size)

# Paleta sobria.
BG = (18, 20, 28)
PANEL_BG = (26, 29, 40)
INK = (228, 231, 240)
MUTED = (140, 146, 162)
ACCENT = (90, 160, 250)
OK = (90, 200, 140)
WARN = (235, 170, 80)
FIELD_BG = (38, 42, 56)
FIELD_ACTIVE = (54, 60, 80)

PLACE_COLORS = {
    "home": (90, 130, 200),
    "business": (210, 160, 70),
    "school": (160, 120, 210),
    "hospital": (220, 100, 110),
    "shop": (90, 200, 140),
    "park": (110, 190, 120),
}


class Button:
    def __init__(self, rect: tuple[int, int, int, int], label: str, action) -> None:
        self.rect = pygame.Rect(rect)
        self.label = label
        self.action = action

    def draw(self, surf, font) -> None:
        pygame.draw.rect(surf, FIELD_BG, self.rect, border_radius=6)
        pygame.draw.rect(surf, MUTED, self.rect, width=1, border_radius=6)
        txt = font.render(self.label, True, INK)
        surf.blit(txt, txt.get_rect(center=self.rect.center))

    def handle(self, pos) -> bool:
        if self.rect.collidepoint(pos):
            self.action()
            return True
        return False


class TextField:
    def __init__(self, rect, label: str, value: str) -> None:
        self.rect = pygame.Rect(rect)
        self.label = label
        self.value = value
        self.active = False

    def draw(self, surf, font, small) -> None:
        lbl = small.render(self.label, True, MUTED)
        surf.blit(lbl, (self.rect.x, self.rect.y - 20))
        bg = FIELD_ACTIVE if self.active else FIELD_BG
        pygame.draw.rect(surf, bg, self.rect, border_radius=6)
        border = ACCENT if self.active else MUTED
        pygame.draw.rect(surf, border, self.rect, width=1, border_radius=6)
        txt = font.render(self.value or "0", True, INK)
        surf.blit(txt, (self.rect.x + 10, self.rect.y + 8))

    def handle_key(self, event) -> None:
        if event.key == pygame.K_BACKSPACE:
            self.value = self.value[:-1]
        elif event.unicode.isdigit():
            self.value = (self.value + event.unicode)[:7]

    def as_int(self, default: int) -> int:
        return int(self.value) if self.value.isdigit() and int(self.value) > 0 else default


class App:
    def __init__(self, controller: SimController | None = None) -> None:
        pygame.init()
        pygame.display.set_caption("Simulación urbana — cliente de escritorio")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        # Fuente integrada de Pygame; tamaños ajustados a su métrica (≈ alto en píxeles).
        self.font = _load_font(22)
        self.big = _load_font(38)
        self.small = _load_font(18)
        self.ctrl = controller or SimController()
        self.save_path = default_save_path()
        self.running = True

        # Campos de la pantalla de creación.
        cx = WIDTH // 2 - 140
        self.fields = [
            TextField((cx, 230, 280, 36), "Semilla (seed)", "42"),
            TextField((cx, 300, 280, 36), "Personas", "100"),
            TextField((cx, 370, 280, 36), "Hogares", "30"),
            TextField((cx, 440, 280, 36), "Empresas", "20"),
        ]
        self.create_btn = Button((cx, 500, 135, 40), "Crear mundo", self._do_create)
        self.load_btn = Button((cx + 145, 500, 135, 40), "Cargar", self._do_load)
        self._world_buttons: list[Button] = []

    # --- Acciones ------------------------------------------------------------

    def _do_create(self) -> None:
        self.ctrl.create_world(
            seed=self.fields[0].as_int(42),
            n_persons=self.fields[1].as_int(100),
            n_households=self.fields[2].as_int(30),
            n_businesses=self.fields[3].as_int(20),
        )

    def _do_load(self) -> None:
        if self.save_path.exists():
            self.ctrl.load(self.save_path)

    def _do_save(self) -> None:
        self.ctrl.save(self.save_path)

    def _build_world_buttons(self) -> None:
        y = HEIGHT - BAR_H + 12
        self._world_buttons = [
            Button((16, y, 110, 40), "Play/Pausa", self.ctrl.toggle_play),
            Button((134, y, 70, 40), "Paso", self.ctrl.step),
            Button((212, y, 50, 40), "<<", self.ctrl.slower),
            Button((270, y, 50, 40), ">>", self.ctrl.faster),
            Button((328, y, 90, 40), "Guardar", self._do_save),
            Button((426, y, 90, 40), "Cargar", self._do_load),
        ]

    # --- Loop ----------------------------------------------------------------

    def run(self) -> None:
        self._build_world_buttons()
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self._handle_events()
            if self.ctrl.screen == SCREEN_WORLD:
                self.ctrl.update(dt)
            self._draw()
            pygame.display.flip()
        pygame.quit()

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._handle_click(event.pos)
            elif event.type == pygame.KEYDOWN:
                self._handle_key(event)

    def _handle_click(self, pos) -> None:
        if self.ctrl.screen == SCREEN_CREATE:
            for f in self.fields:
                f.active = f.rect.collidepoint(pos)
            self.create_btn.handle(pos)
            self.load_btn.handle(pos)
        else:
            for b in self._world_buttons:
                b.handle(pos)

    def _handle_key(self, event) -> None:
        if self.ctrl.screen == SCREEN_CREATE:
            for f in self.fields:
                if f.active:
                    f.handle_key(event)
            return
        # Pantalla del mundo: atajos.
        if event.key == pygame.K_SPACE:
            self.ctrl.toggle_play()
        elif event.key == pygame.K_RIGHT:
            self.ctrl.step()
        elif event.key in (pygame.K_PLUS, pygame.K_EQUALS):
            self.ctrl.faster()
        elif event.key == pygame.K_MINUS:
            self.ctrl.slower()
        elif event.key == pygame.K_s:
            self._do_save()
        elif event.key == pygame.K_l:
            self._do_load()

    # --- Dibujo --------------------------------------------------------------

    def _draw(self) -> None:
        self.screen.fill(BG)
        if self.ctrl.screen == SCREEN_CREATE:
            self._draw_create()
        else:
            self._draw_world()

    def _draw_create(self) -> None:
        title = self.big.render("Crear un mundo", True, INK)
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 150))
        hint = self.small.render(
            "El mismo seed + config produce siempre el mismo mundo (determinista).",
            True, MUTED,
        )
        self.screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, 190))
        for f in self.fields:
            f.draw(self.screen, self.font, self.small)
        self.create_btn.draw(self.screen, self.font)
        self.load_btn.draw(self.screen, self.font)

    def _draw_world(self) -> None:
        state = self.ctrl.world_state()
        if state is None:
            return
        canvas_w = WIDTH - PANEL_W
        canvas_h = HEIGHT - BAR_H

        # --- Vista del barrio ---
        place_pos = layout.place_positions(state.places, canvas_w, canvas_h)
        for place in state.places:
            x, y = place_pos[place.id]
            color = PLACE_COLORS.get(place.type, MUTED)
            pygame.draw.rect(self.screen, color, pygame.Rect(int(x) - 9, int(y) - 9, 18, 18), border_radius=3)
        for person in state.persons:
            x, y = layout.person_position(person, place_pos)
            color = OK if person.alive else (90, 90, 100)
            pygame.draw.circle(self.screen, color, (int(x), int(y)), 3)

        self._draw_event_panel(state, canvas_w)
        self._draw_bar(state)

    def _draw_event_panel(self, state, canvas_w: int) -> None:
        panel = pygame.Rect(canvas_w, 0, PANEL_W, HEIGHT - BAR_H)
        pygame.draw.rect(self.screen, PANEL_BG, panel)
        head = self.font.render("Eventos recientes", True, INK)
        self.screen.blit(head, (canvas_w + 16, 14))
        y = 46
        for e in self.ctrl.recent_events(16):
            line = f"t{e.tick:<5} {e.type}"
            txt = self.small.render(line[:40], True, MUTED)
            self.screen.blit(txt, (canvas_w + 16, y))
            y += 18
            if y > HEIGHT - BAR_H - 20:
                break

    def _draw_bar(self, state) -> None:
        bar = pygame.Rect(0, HEIGHT - BAR_H, WIDTH, BAR_H)
        pygame.draw.rect(self.screen, PANEL_BG, bar)
        for b in self._world_buttons:
            b.draw(self.screen, self.font)

        tick, day, hour = self.ctrl.clock
        play = "▶" if self.ctrl.playing else "❚❚"
        hud = (
            f"{play}  día {day:>3}  {hour:02d}:00   "
            f"vivos {state.n_persons_alive:>3}   "
            f"$ {self.ctrl.total_money():>10,.0f}   "
            f"vel {self.ctrl.speed}/s"
        )
        txt = self.font.render(hud, True, INK)
        self.screen.blit(txt, (540, HEIGHT - BAR_H + 22))


def main() -> None:
    App().run()


def run_smoke(ticks: int = 48) -> None:
    """Arranque de validación, sin interacción: crea un mundo, avanza y dibuja un frame.

    Pensado para correr el ejecutable congelado con `--smoke` (SDL en modo dummy) y
    confirmar que el bundle realmente inicia, sin necesidad de pantalla (ADR-0013).
    """
    app = App()
    app.ctrl.create_world(seed=42, n_persons=60, n_households=15, n_businesses=8)
    app.ctrl.toggle_play()
    app.ctrl.set_speed(24)
    app._build_world_buttons()
    for _ in range(5):
        app.ctrl.update(ticks / (5 * app.ctrl.speed))
        app._draw()
    pygame.quit()
