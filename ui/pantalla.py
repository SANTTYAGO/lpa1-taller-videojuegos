# ui/pantalla.py
import pygame
import os
from models.personaje import Personaje
from core.escenario import Escenario
from core.combate import SistemaCombate
from models.objeto import Equipamiento

# Constantes Globales
ANCHO = 800
ALTO = 600
FPS = 60
TAMANO_TILE = 64 
VELOCIDAD = 5

# Paleta de colores UI/UX
NEGRO_ELEGANTE = (15, 15, 20)
BLANCO = (255, 255, 255)
VERDE_OSCURO = (34, 139, 34) 
AZUL_HEROE = (30, 144, 255)
ROJO_ENEMIGO = (220, 20, 60) 
GRIS_PANEL = (50, 50, 50)
AMARILLO = (255, 215, 0)
NARANJA = (255, 140, 0)
MORADO_MERCADER = (128, 0, 128)
AMARILLO_GIRASOL = (255, 204, 51) # Color cálido de acento para la UI

# ==========================================
# PATRÓN DE DISEÑO: ESTADOS (STATE PATTERN)
# ==========================================

class EstadoJuego:
    def __init__(self, motor):
        self.motor = motor 

    def manejar_evento(self, evento): pass
    def actualizar(self): pass
    def dibujar(self): pass

# --- NUEVA PANTALLA: MENÚ PRINCIPAL ---
class EstadoMenuPrincipal(EstadoJuego):
    def manejar_evento(self, evento):
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_RETURN:
                # Al presionar ENTER, iniciamos la aventura
                self.motor.estado_actual = self.motor.estado_exploracion

    def dibujar(self):
        m = self.motor
        m.pantalla.fill(NEGRO_ELEGANTE)

        # Título Armonioso
        titulo = m.fuente_gigante.render("La Leyenda de los 17 Girasoles", True, AMARILLO_GIRASOL)
        m.pantalla.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, ALTO // 3))

        # Efecto visual de "respiración" para el texto de inicio
        tiempo = pygame.time.get_ticks()
        parpadeo = abs(tiempo % 2000 - 1000) / 1000.0 # Oscila entre 0.0 y 1.0
        color_inst = (int(255 * parpadeo), int(255 * parpadeo), int(255 * parpadeo))
        
        instruccion = m.fuente.render("Presiona ENTER para adentrarte en las 20 zonas", True, color_inst)
        m.pantalla.blit(instruccion, (ANCHO // 2 - instruccion.get_width() // 2, ALTO // 2 + 50))

# --- NUEVA PANTALLA: GAME OVER / VICTORIA ---
class EstadoFinJuego(EstadoJuego):
    def __init__(self, motor):
        super().__init__(motor)
        self.victoria = False # Se ajustará dependiendo de cómo termine el juego

    def manejar_evento(self, evento):
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_RETURN:
                self.motor.corriendo = False # Cierra el juego al terminar

    def dibujar(self):
        m = self.motor
        m.pantalla.fill(NEGRO_ELEGANTE)
        
        if self.victoria:
            texto = m.fuente_gigante.render("¡VICTORIA SUPREMA!", True, AMARILLO_GIRASOL)
            sub = m.fuente.render("Has superado todas las pruebas de esta aventura.", True, BLANCO)
        else:
            texto = m.fuente_gigante.render("FIN DEL JUEGO", True, ROJO_ENEMIGO)
            sub = m.fuente.render("Tu viaje termina aquí en la oscuridad...", True, BLANCO)
            
        instruccion = m.fuente.render("Presiona ENTER para salir", True, GRIS_PANEL)
        
        m.pantalla.blit(texto, (ANCHO // 2 - texto.get_width() // 2, ALTO // 3))
        m.pantalla.blit(sub, (ANCHO // 2 - sub.get_width() // 2, ALTO // 2))
        m.pantalla.blit(instruccion, (ANCHO // 2 - instruccion.get_width() // 2, ALTO - 100))


class EstadoExploracion(EstadoJuego):
    def manejar_evento(self, evento):
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_t and self.motor.es_tienda:
                self.motor.estado_actual = self.motor.estado_tienda
                self.motor.mensaje_tienda = "¡Bienvenido! Tengo mercancía de primera."

    def actualizar(self):
        self._mover_jugador()
        self._verificar_colisiones()

    def _mover_jugador(self):
        m = self.motor
        teclas = pygame.key.get_pressed()
        moviendo = False
        
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
            m.jugador_x -= VELOCIDAD; m.mirando_izquierda = True; moviendo = True
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
            m.jugador_x += VELOCIDAD; m.mirando_izquierda = False; moviendo = True
        if teclas[pygame.K_UP] or teclas[pygame.K_w]:
            m.jugador_y -= VELOCIDAD; moviendo = True
        if teclas[pygame.K_DOWN] or teclas[pygame.K_s]:
            m.jugador_y += VELOCIDAD; moviendo = True

        m.accion_heroe = "WALK" if moviendo else "IDLE"
        m.jugador_y = max(0, min(m.jugador_y, ALTO - 60 - TAMANO_TILE))
        
        if m.jugador_x > ANCHO - TAMANO_TILE:
            if m.indice_zona < len(m.mundo.zonas) - 1:
                m.indice_zona += 1
                m.cargar_zona()
                m.jugador_x = 0 
                m.heroe.zonas_exploradas += 1 
            else:
                m.jugador_x = ANCHO - TAMANO_TILE 
        elif m.jugador_x < 0:
            if m.indice_zona > 0:
                m.indice_zona -= 1
                m.cargar_zona()
                m.jugador_x = ANCHO - TAMANO_TILE 
            else:
                m.jugador_x = 0 

    def _verificar_colisiones(self):
        m = self.motor
        jugador_rect = pygame.Rect(m.jugador_x, m.jugador_y, TAMANO_TILE, TAMANO_TILE)
        
        if m.enemigo and m.enemigo.esta_vivo():
            if jugador_rect.colliderect(m.enemigo_rect):
                m.estado_actual = m.estado_combate 
                m.turno_actual = "JUGADOR"
                m.mensaje_combate = f"¡Emboscada! {m.enemigo.nombre} te ataca."
                m.jugador_x -= 40 
                m.efecto_actual = None 

        if m.objeto:
            if jugador_rect.colliderect(m.objeto_rect):
                if hasattr(m.objeto, 'dano_explosion'):
                    m.heroe.recibir_dano(m.objeto.dano_explosion)
                    # Si la trampa te mata en exploración
                    if not m.heroe.esta_vivo():
                        m.estado_fin.victoria = False
                        m.estado_actual = m.estado_fin
                else:
                    m.heroe.recolectar_objeto(m.objeto)
                    m.heroe.ganar_puntaje(50) 
                m.mundo.zonas[m.indice_zona].objeto = None
                m.objeto = None

    def dibujar(self):
        m = self.motor
        if m.usar_sprites:
            for x in range(0, ANCHO, TAMANO_TILE):
                for y in range(0, ALTO - 60, TAMANO_TILE):
                    m.pantalla.blit(m.img_suelo, (x, y))
        else:
            m.pantalla.fill(VERDE_OSCURO)
        
        if m.es_tienda:
            pygame.draw.rect(m.pantalla, MORADO_MERCADER, m.mercader_rect)
            aviso = m.fuente.render("Presiona 'T' para Comerciar", True, BLANCO)
            m.pantalla.blit(aviso, (ANCHO//2 - aviso.get_width()//2, 160))

        if m.objeto:
            if m.img_objeto: m.pantalla.blit(m.img_objeto, m.objeto_rect.topleft)
            else:
                color_obj = (139, 0, 0) if hasattr(m.objeto, 'dano_explosion') else NARANJA
                pygame.draw.rect(m.pantalla, color_obj, m.objeto_rect)

        if m.enemigo and m.enemigo.esta_vivo():
            if m.usar_sprites:
                indice_e = m.frame_index % len(m.anim_enemigo_idle)
                m.pantalla.blit(m.anim_enemigo_idle[indice_e], m.enemigo_rect.topleft)
            else:
                pygame.draw.rect(m.pantalla, ROJO_ENEMIGO, m.enemigo_rect)

        if m.usar_sprites:
            lista_activa = m.anim_heroe_walk if m.accion_heroe == "WALK" else m.anim_heroe_idle
            indice_h = m.frame_index % len(lista_activa)
            imagen_actual = lista_activa[indice_h]
            if m.mirando_izquierda:
                imagen_actual = pygame.transform.flip(imagen_actual, True, False)
            m.pantalla.blit(imagen_actual, (m.jugador_x, m.jugador_y))
        else:
            jugador_rect = pygame.Rect(m.jugador_x, m.jugador_y, TAMANO_TILE, TAMANO_TILE)
            pygame.draw.rect(m.pantalla, AZUL_HEROE, jugador_rect)


class EstadoCombate(EstadoJuego):
    def manejar_evento(self, evento):
        m = self.motor
        if evento.type != pygame.KEYDOWN: return
        
        if m.turno_actual == "JUGADOR":
            if evento.key == pygame.K_a:
                m.efecto_actual = "HEROE_ATACA"
                m.tiempo_efecto = pygame.time.get_ticks()
                m.frame_index = 0 
                dano = SistemaCombate.calcular_dano(m.heroe.ataque, m.enemigo.defensa)
                m.enemigo.recibir_dano(dano)
                m.mensaje_combate = f"¡{m.heroe.nombre} ataca! Causa {dano} puntos de daño."
                m.turno_actual = "VICTORIA" if not m.enemigo.esta_vivo() else "ENEMIGO"

        elif m.turno_actual == "ENEMIGO":
            if evento.key == pygame.K_SPACE:
                m.efecto_actual = "ENEMIGO_ATACA"
                m.tiempo_efecto = pygame.time.get_ticks()
                m.frame_index = 0
                dano = SistemaCombate.calcular_dano(m.enemigo.ataque, m.heroe.defensa)
                m.heroe.recibir_dano(dano)
                m.mensaje_combate = f"¡{m.enemigo.nombre} contraataca y causa {dano} de daño!"
                
                # NUEVO: Lógica de muerte en combate conectada al menú de fin
                if not m.heroe.esta_vivo():
                    m.turno_actual = "DERROTA"
                    m.estado_fin.victoria = False
                else:
                    m.turno_actual = "JUGADOR"

        elif m.turno_actual == "VICTORIA":
            if evento.key == pygame.K_RETURN:
                m.heroe.ganar_experiencia(100)
                m.efecto_actual = None
                
                # NUEVO: Si vencimos al Rey Demonio, ganamos el juego completo
                if m.enemigo.nombre == "Rey Demonio":
                    m.estado_fin.victoria = True
                    m.estado_actual = m.estado_fin
                else:
                    m.estado_actual = m.estado_exploracion
                
        elif m.turno_actual == "DERROTA":
            if evento.key == pygame.K_RETURN:
                # Transición a la pantalla de Game Over
                m.estado_actual = m.estado_fin

    def dibujar(self):
        m = self.motor
        m.pantalla.fill(NEGRO_ELEGANTE) # Usamos el fondo elegante para el combate también
        titulo = m.fuente_grande.render(f"VS {m.enemigo.nombre}", True, ROJO_ENEMIGO)
        hp_enemigo = m.fuente.render(f"HP Enemigo: {m.enemigo.puntos_vida}", True, BLANCO)
        m.pantalla.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, 30))
        m.pantalla.blit(hp_enemigo, (ANCHO // 2 - hp_enemigo.get_width() // 2, 80))
        
        if m.usar_sprites:
            tiempo_transcurrido = pygame.time.get_ticks() - m.tiempo_efecto
            if m.efecto_actual == "HEROE_ATACA" and tiempo_transcurrido < 600:
                idx = min(m.frame_index, len(m.anim_heroe_attack) - 1)
                sprite_h = m.anim_heroe_attack[idx]
            else:
                idx = m.frame_index % len(m.anim_heroe_idle)
                sprite_h = m.anim_heroe_idle[idx]
                
            if m.efecto_actual == "ENEMIGO_ATACA" and tiempo_transcurrido < 600:
                idx = min(m.frame_index, len(m.anim_enemigo_attack) - 1)
                sprite_e = m.anim_enemigo_attack[idx]
            else:
                idx = m.frame_index % len(m.anim_enemigo_idle)
                sprite_e = m.anim_enemigo_idle[idx]

            hero_grande = pygame.transform.scale(sprite_h, (192, 192))
            m.pantalla.blit(hero_grande, (150, 120))

            enemigo_grande = pygame.transform.scale(sprite_e, (192, 192))
            enemigo_grande = pygame.transform.flip(enemigo_grande, True, False)
            m.pantalla.blit(enemigo_grande, (450, 120))
        
        caja_msg_rect = pygame.Rect(100, 350, 600, 150)
        pygame.draw.rect(m.pantalla, GRIS_PANEL, caja_msg_rect)
        pygame.draw.rect(m.pantalla, AMARILLO, caja_msg_rect, 3)
        
        texto_msg = m.fuente.render(m.mensaje_combate, True, BLANCO)
        m.pantalla.blit(texto_msg, (120, 370))
        
        if m.turno_actual == "JUGADOR": inst = "▶ Presiona 'A' para Atacar"
        elif m.turno_actual == "ENEMIGO": inst = "▶ Presiona 'ESPACIO' para continuar"
        elif m.turno_actual == "VICTORIA": inst = "▶ Has ganado la pelea. Presiona 'ENTER'"
        elif m.turno_actual == "DERROTA": inst = "▶ Has caído... Presiona 'ENTER'"
        
        color_inst = (100, 255, 100) if m.turno_actual == "VICTORIA" else (ROJO_ENEMIGO if m.turno_actual == "DERROTA" else AMARILLO)
        instruccion = m.fuente.render(inst, True, color_inst)
        m.pantalla.blit(instruccion, (120, 450))


class EstadoTienda(EstadoJuego):
    def manejar_evento(self, evento):
        m = self.motor
        if evento.type != pygame.KEYDOWN: return
        
        if evento.key == pygame.K_b:
            if m.heroe.puntaje >= m.item_tienda.precio_compra:
                m.heroe.puntaje -= m.item_tienda.precio_compra
                m.heroe.equipar(m.item_tienda)
                m.mensaje_tienda = f"¡Excelente compra! Has equipado {m.item_tienda.nombre}."
                m.item_tienda = Equipamiento("Armadura Épica", aumento_ataque=5, aumento_defensa=20, precio_compra=300, precio_venta=150)
            else:
                m.mensaje_tienda = "No tienes suficientes Puntos para comprar esto."
        elif evento.key == pygame.K_RETURN or evento.key == pygame.K_ESCAPE:
            m.estado_actual = m.estado_exploracion 

    def dibujar(self):
        m = self.motor
        m.pantalla.fill(NEGRO_ELEGANTE)
        
        titulo = m.fuente_grande.render("Refugio del Mercader", True, MORADO_MERCADER)
        m.pantalla.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, 50))
        
        oferta_rect = pygame.Rect(200, 150, 400, 200)
        pygame.draw.rect(m.pantalla, GRIS_PANEL, oferta_rect)
        pygame.draw.rect(m.pantalla, AMARILLO_GIRASOL, oferta_rect, 2)
        
        nombre_item = m.fuente_grande.render(m.item_tienda.nombre, True, AMARILLO)
        stats = m.fuente.render(f"+{m.item_tienda.aumento_ataque} ATK / +{m.item_tienda.aumento_defensa} DEF", True, BLANCO)
        precio = m.fuente.render(f"Costo: {m.item_tienda.precio_compra} Puntos", True, (100, 255, 100))
        
        m.pantalla.blit(nombre_item, (ANCHO // 2 - nombre_item.get_width() // 2, 170))
        m.pantalla.blit(stats, (ANCHO // 2 - stats.get_width() // 2, 230))
        m.pantalla.blit(precio, (ANCHO // 2 - precio.get_width() // 2, 280))

        caja_msg_rect = pygame.Rect(100, 400, 600, 120)
        pygame.draw.rect(m.pantalla, GRIS_PANEL, caja_msg_rect)
        pygame.draw.rect(m.pantalla, MORADO_MERCADER, caja_msg_rect, 3)
        
        texto_msg = m.fuente.render(m.mensaje_tienda, True, BLANCO)
        instruccion = m.fuente.render("▶ Presiona 'B' para Comprar | 'ENTER' para Salir", True, AMARILLO)
        
        m.pantalla.blit(texto_msg, (120, 420))
        m.pantalla.blit(instruccion, (120, 480))

# ==========================================
# CLASE PRINCIPAL (CONTEXTO)
# ==========================================

class MotorGrafico:
    def __init__(self, heroe: Personaje, mundo: Escenario):
        pygame.init()
        self.pantalla = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption("La Leyenda de los 17 Girasoles")
        self.reloj = pygame.time.Clock()
        self.corriendo = True
        
        self.heroe = heroe
        self.mundo = mundo
        self.indice_zona = 0 
        
        # Fuentes tipográficas limpias
        self.fuente = pygame.font.SysFont("Arial", 20, bold=True)
        self.fuente_grande = pygame.font.SysFont("Arial", 40, bold=True)
        self.fuente_gigante = pygame.font.SysFont("Arial", 50, bold=True) # Para los títulos
        
        # Instanciamos todos los estados
        self.estado_menu = EstadoMenuPrincipal(self)
        self.estado_exploracion = EstadoExploracion(self)
        self.estado_combate = EstadoCombate(self)
        self.estado_tienda = EstadoTienda(self)
        self.estado_fin = EstadoFinJuego(self)
        
        # NUEVO: Arrancamos en el Menú Principal en lugar de saltar directo al juego
        self.estado_actual = self.estado_menu 
        
        # Variables globales compartidas
        self.turno_actual = "JUGADOR"
        self.mensaje_combate = "¡Un enemigo bloquea el paso!"
        self.mensaje_tienda = "¡Bienvenido! ¿Qué vas a llevar?"
        self.item_tienda = Equipamiento("Espada Maestra", 15, 5, 150, 75)
        
        self.jugador_x = 50 
        self.jugador_y = ((ALTO - 60) // 2) - (TAMANO_TILE // 2)

        self.frame_index = 0
        self.tiempo_animacion = 0
        self.VELOCIDAD_ANIMACION = 120 
        self.accion_heroe = "IDLE" 
        self.mirando_izquierda = False 
        self.efecto_actual = None 
        self.tiempo_efecto = 0    

        self.cargar_sprites()
        self.cargar_zona() 

    def cargar_zona(self):
        zona_actual = self.mundo.zonas[self.indice_zona]
        self.enemigo = zona_actual.enemigo
        self.objeto = zona_actual.objeto
        self.es_tienda = zona_actual.es_tienda
        self.nombre_zona = zona_actual.nombre
        
        if self.enemigo: self.enemigo_rect = pygame.Rect(600, 300, TAMANO_TILE, TAMANO_TILE)
        if self.objeto: self.objeto_rect = pygame.Rect(300, 400, TAMANO_TILE, TAMANO_TILE)
        if self.es_tienda: self.mercader_rect = pygame.Rect(ANCHO // 2, 200, TAMANO_TILE, TAMANO_TILE)

    def extraer_frames(self, ruta, escala):
        hoja = pygame.image.load(ruta).convert_alpha()
        alto = hoja.get_height()
        frames = []
        for i in range(hoja.get_width() // alto):
            rect = pygame.Rect(i * alto, 0, alto, alto)
            frames.append(pygame.transform.scale(hoja.subsurface(rect), escala))
        return frames

    def cargar_sprites(self):
        self.usar_sprites = False
        self.img_objeto = None
        try:
            escala_mapa = (TAMANO_TILE, TAMANO_TILE) 
            self.anim_heroe_idle = self.extraer_frames(os.path.join("assets", "Heroe", "Soldier", "Soldier-Idle.png"), escala_mapa)
            self.anim_heroe_walk = self.extraer_frames(os.path.join("assets", "Heroe", "Soldier", "Soldier-Walk.png"), escala_mapa)
            self.anim_heroe_attack = self.extraer_frames(os.path.join("assets", "Heroe", "Soldier", "Soldier-Attack01.png"), escala_mapa)

            self.anim_enemigo_idle = self.extraer_frames(os.path.join("assets", "Enemigo", "Orc", "Orc-Idle.png"), escala_mapa)
            self.anim_enemigo_attack = self.extraer_frames(os.path.join("assets", "Enemigo", "Orc", "Orc-Attack01.png"), escala_mapa)

            self.img_suelo = pygame.transform.scale(pygame.image.load(os.path.join("assets", "Suelo", "Grass_Middle.png")).convert(), escala_mapa)
            try: self.img_objeto = pygame.transform.scale(pygame.image.load(os.path.join("assets", "Objeto", "item.png")).convert_alpha(), escala_mapa)
            except: pass
            self.usar_sprites = True
        except Exception: pass

    def manejar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.corriendo = False
            self.estado_actual.manejar_evento(evento)

    def dibujar_hud(self):
        # Solo dibujamos el HUD si estamos explorando, peleando o en la tienda (no en menús)
        if self.estado_actual in [self.estado_menu, self.estado_fin]: return
        
        panel_rect = pygame.Rect(0, ALTO - 60, ANCHO, 60)
        pygame.draw.rect(self.pantalla, GRIS_PANEL, panel_rect)
        pygame.draw.rect(self.pantalla, BLANCO, panel_rect, 2)

        texto_hp = self.fuente.render(f"HP: {self.heroe.puntos_vida}/{self.heroe.puntos_vida_max}", True, (255, 100, 100))
        texto_inv = self.fuente.render(f"ATK: {self.heroe.ataque} | DEF: {self.heroe.defensa} | Pts: {self.heroe.puntaje}", True, AMARILLO)
        color_zona = (100, 255, 100) if self.es_tienda else BLANCO
        texto_zona = self.fuente.render(f"{self.nombre_zona} ({self.indice_zona+1}/20)", True, color_zona)
        
        self.pantalla.blit(texto_hp, (20, ALTO - 40))
        self.pantalla.blit(texto_inv, (180, ALTO - 40))
        self.pantalla.blit(texto_zona, (500, ALTO - 40))

    def actualizar(self):
        self.estado_actual.actualizar()
        tiempo_actual = pygame.time.get_ticks()
        if tiempo_actual - self.tiempo_animacion > self.VELOCIDAD_ANIMACION:
            self.tiempo_animacion = tiempo_actual
            self.frame_index += 1
        self.reloj.tick(FPS)

    def dibujar(self):
        self.estado_actual.dibujar()
        self.dibujar_hud()
        pygame.display.flip()

    def salir(self):
        pygame.quit()