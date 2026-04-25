# ui/estados.py
import pygame
import os
import math
from ui.constantes import *
from ui.elementos import TextoFlotante
from core.combate import AtaqueBasico, GolpeEspecial, Curacion 
from models.objeto import Equipamiento, Consumible 

OFFSET_X = (ESCALA_PERSONAJE - TAMANO_CELDA) // 2
OFFSET_Y = ESCALA_PERSONAJE - TAMANO_CELDA

class EstadoJuego:
    def __init__(self, motor_grafico): self.motor = motor_grafico 
    def manejar_evento(self, evento): pass
    def actualizar(self): pass
    def dibujar(self): pass

class EstadoMenuPrincipal(EstadoJuego):
    def __init__(self, motor_grafico):
        super().__init__(motor_grafico)
        self.opciones = ["Nueva Aventura", "Cargar Partida"]
        self.opcion_seleccionada = 0
        self.mensaje_error = ""

    def manejar_evento(self, evento):
        if evento.type == pygame.KEYDOWN:
            self.mensaje_error = ""
            if evento.key == pygame.K_UP: self.opcion_seleccionada = (self.opcion_seleccionada - 1) % len(self.opciones)
            elif evento.key == pygame.K_DOWN: self.opcion_seleccionada = (self.opcion_seleccionada + 1) % len(self.opciones)
            elif evento.key == pygame.K_RETURN:
                if self.opcion_seleccionada == 0:
                    if self.motor.usar_sonidos:
                        pygame.mixer.music.load(os.path.join("assets", "Sonidos", "game soundtrack.mp3"))
                        pygame.mixer.music.play(-1)
                    self.motor.estado_actual = self.motor.estado_exploracion
                elif self.opcion_seleccionada == 1:
                    exito = self.motor.cargar_partida()
                    if exito:
                        if self.motor.usar_sonidos:
                            pygame.mixer.music.load(os.path.join("assets", "Sonidos", "game soundtrack.mp3"))
                            pygame.mixer.music.play(-1)
                        self.motor.estado_actual = self.motor.estado_exploracion
                    else:
                        self.mensaje_error = "¡No hay ninguna partida guardada!"

    def dibujar(self):
        self.motor.pantalla.fill(COLOR_NEGRO_FONDO)
        texto_titulo = self.motor.fuente_gigante.render(TITULO_JUEGO, True, COLOR_GIRASOL_ACENTO)
        self.motor.pantalla.blit(texto_titulo, (ANCHO_VENTANA // 2 - texto_titulo.get_width() // 2, ALTO_VENTANA // 4))
        
        for i, opcion in enumerate(self.opciones):
            color = COLOR_GIRASOL_ACENTO if i == self.opcion_seleccionada else COLOR_BLANCO
            marcador = "> " if i == self.opcion_seleccionada else "  "
            texto_render = self.motor.fuente_grande.render(f"{marcador}{opcion}", True, color)
            self.motor.pantalla.blit(texto_render, (ANCHO_VENTANA // 2 - 120, ALTO_VENTANA // 2 + (i * 60)))
            
        if self.mensaje_error:
            txt_err = self.motor.fuente.render(self.mensaje_error, True, COLOR_ROJO_ENEMIGO)
            self.motor.pantalla.blit(txt_err, (ANCHO_VENTANA // 2 - txt_err.get_width() // 2, ALTO_VENTANA - 80))

class EstadoFinJuego(EstadoJuego):
    def __init__(self, motor_grafico):
        super().__init__(motor_grafico)
        self.es_victoria = False 

    def manejar_evento(self, evento):
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_RETURN: self.motor.corriendo = False 

    def dibujar(self):
        self.motor.pantalla.fill(COLOR_NEGRO_FONDO)
        if self.es_victoria:
            texto_principal = self.motor.fuente_gigante.render("¡VICTORIA SUPREMA!", True, COLOR_GIRASOL_ACENTO)
            texto_secundario = self.motor.fuente.render("El Rey Demonio ha caído. El mundo está a salvo.", True, COLOR_BLANCO)
        else:
            texto_principal = self.motor.fuente_gigante.render("FIN DEL JUEGO", True, COLOR_ROJO_ENEMIGO)
            texto_secundario = self.motor.fuente.render("Tu viaje ha terminado en la derrota...", True, COLOR_BLANCO)
            
        texto_salir = self.motor.fuente.render("Presiona ENTER para salir", True, COLOR_GRIS_PANEL)
        self.motor.pantalla.blit(texto_principal, (ANCHO_VENTANA // 2 - texto_principal.get_width() // 2, ALTO_VENTANA // 3))
        self.motor.pantalla.blit(texto_secundario, (ANCHO_VENTANA // 2 - texto_secundario.get_width() // 2, ALTO_VENTANA // 2))
        self.motor.pantalla.blit(texto_salir, (ANCHO_VENTANA // 2 - texto_salir.get_width() // 2, ALTO_VENTANA - 100))

class EstadoPausa(EstadoJuego):
    def __init__(self, motor_grafico):
        super().__init__(motor_grafico)
        self.opciones = ["Guardar Partida", "Musica", "Efectos (SFX)", "Pantalla Completa", "Volver al Juego", "Salir del Juego"]
        self.opcion_seleccionada = 0
        self.mensaje_guardado = ""

    def manejar_evento(self, evento):
        if evento.type == pygame.KEYDOWN:
            self.mensaje_guardado = ""
            if evento.key == pygame.K_ESCAPE: 
                self.motor.estado_actual = self.motor.estado_exploracion
            elif evento.key == pygame.K_UP: 
                self.opcion_seleccionada = (self.opcion_seleccionada - 1) % len(self.opciones)
            elif evento.key == pygame.K_DOWN: 
                self.opcion_seleccionada = (self.opcion_seleccionada + 1) % len(self.opciones)
            elif evento.key == pygame.K_LEFT:
                if self.opcion_seleccionada == 1: self.motor.ajustar_volumen_musica(-0.1)
                elif self.opcion_seleccionada == 2: self.motor.ajustar_volumen_sfx(-0.1)
            elif evento.key == pygame.K_RIGHT:
                if self.opcion_seleccionada == 1: self.motor.ajustar_volumen_musica(0.1)
                elif self.opcion_seleccionada == 2: self.motor.ajustar_volumen_sfx(0.1)
            elif evento.key == pygame.K_RETURN:
                if self.opcion_seleccionada == 0:
                    if self.motor.guardar_partida(): self.mensaje_guardado = "¡Partida Guardada!"
                    else: self.mensaje_guardado = "¡Error al guardar!"
                elif self.opcion_seleccionada == 3: 
                    self.motor.alternar_pantalla_completa()
                elif self.opcion_seleccionada == 4: 
                    self.motor.estado_actual = self.motor.estado_exploracion
                elif self.opcion_seleccionada == 5:
                    self.motor.corriendo = False

    def dibujar(self):
        self.motor.estado_exploracion.dibujar()
        superficie_oscura = pygame.Surface((ANCHO_VENTANA, ALTO_VENTANA))
        superficie_oscura.set_alpha(220) 
        superficie_oscura.fill(COLOR_NEGRO_FONDO)
        self.motor.pantalla.blit(superficie_oscura, (0, 0))

        titulo = self.motor.fuente_gigante.render("Pausa - Sistema", True, COLOR_GIRASOL_ACENTO)
        self.motor.pantalla.blit(titulo, (ANCHO_VENTANA // 2 - titulo.get_width() // 2, 80))

        rect_config = pygame.Rect(200, 180, 400, 280)
        pygame.draw.rect(self.motor.pantalla, COLOR_GRIS_PANEL, rect_config, border_radius=15)
        pygame.draw.rect(self.motor.pantalla, COLOR_BLANCO, rect_config, 3, border_radius=15)
        
        texto_cabecera = self.mensaje_guardado if self.mensaje_guardado else "Ajustes de Juego"
        color_cabecera = (100, 255, 100) if self.mensaje_guardado else COLOR_BLANCO
        tit_ajustes = self.motor.fuente_grande.render(texto_cabecera, True, color_cabecera)
        self.motor.pantalla.blit(tit_ajustes, (ANCHO_VENTANA // 2 - tit_ajustes.get_width() // 2, 200))

        pygame.draw.line(self.motor.pantalla, COLOR_GIRASOL_ACENTO, (220, 240), (580, 240), 2)

        for i, opcion in enumerate(self.opciones):
            color = COLOR_GIRASOL_ACENTO if i == self.opcion_seleccionada else COLOR_BLANCO
            marcador = "> " if i == self.opcion_seleccionada else "  "
            
            if i == 0: texto = f"{marcador}Guardar Progreso"
            elif i == 1: texto = f"{marcador}Musica: {int(self.motor.volumen_musica * 100)}%"
            elif i == 2: texto = f"{marcador}Efectos SFX: {int(self.motor.volumen_sfx * 100)}%"
            elif i == 3: estado_pant = "Completa" if self.motor.pantalla_completa else "Ventana"; texto = f"{marcador}Pantalla: {estado_pant}"
            elif i == 4: texto = f"{marcador}Volver al Juego"
            elif i == 5: texto = f"{marcador}Salir del Juego"
            
            txt_rend = self.motor.fuente.render(texto, True, color)
            self.motor.pantalla.blit(txt_rend, (250, 260 + (i * 30)))

class EstadoInventario(EstadoJuego):
    def __init__(self, motor_grafico):
        super().__init__(motor_grafico)
        self.cursor_inventario = 0

    def manejar_evento(self, evento):
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE or evento.key == pygame.K_i: 
                self.motor.estado_actual = self.motor.estado_exploracion
            else:
                inventario_actual = self.motor.heroe.inventario
                if evento.key == pygame.K_UP and len(inventario_actual) > 0:
                    self.cursor_inventario = (self.cursor_inventario - 1) % len(inventario_actual)
                elif evento.key == pygame.K_DOWN and len(inventario_actual) > 0:
                    self.cursor_inventario = (self.cursor_inventario + 1) % len(inventario_actual)
                elif evento.key == pygame.K_RETURN and len(inventario_actual) > 0:
                    objeto_seleccionado = inventario_actual[self.cursor_inventario]
                    if isinstance(objeto_seleccionado, Consumible):
                        objeto_seleccionado.usar(self.motor.heroe) 
                        self.motor.heroe.inventario.remove(objeto_seleccionado) 
                        if self.motor.usar_sonidos: self.motor.sonido_moneda.play()
                        if self.cursor_inventario >= len(self.motor.heroe.inventario):
                            self.cursor_inventario = max(0, len(self.motor.heroe.inventario) - 1)

    def dibujar(self):
        self.motor.estado_exploracion.dibujar()
        superficie_oscura = pygame.Surface((ANCHO_VENTANA, ALTO_VENTANA))
        superficie_oscura.set_alpha(230) 
        superficie_oscura.fill((20, 20, 30)) 
        self.motor.pantalla.blit(superficie_oscura, (0, 0))

        titulo = self.motor.fuente_gigante.render("Perfil e Inventario", True, COLOR_GIRASOL_ACENTO)
        self.motor.pantalla.blit(titulo, (ANCHO_VENTANA // 2 - titulo.get_width() // 2, 30))

        rect_stats = pygame.Rect(50, 100, 350, 420)
        pygame.draw.rect(self.motor.pantalla, COLOR_NEGRO_FONDO, rect_stats, border_radius=10)
        pygame.draw.rect(self.motor.pantalla, COLOR_AZUL_HEROE, rect_stats, 3, border_radius=10)
        
        self.motor.pantalla.blit(self.motor.fuente_grande.render("Estadisticas del Heroe", True, COLOR_BLANCO), (70, 120))
        pygame.draw.line(self.motor.pantalla, COLOR_AZUL_HEROE, (70, 160), (380, 160), 2)
        
        textos_stats = [
            f"Nombre: {self.motor.heroe.nombre}",
            f"Nivel: {self.motor.heroe.nivel}  (EXP: {self.motor.heroe.experiencia}/100)",
            f"Vida (HP): {self.motor.heroe.puntos_vida} / {self.motor.heroe.puntos_vida_max}",
            f"Mana (MP): {self.motor.heroe.puntos_magia} / {self.motor.heroe.puntos_magia_max}",
            f"Ataque (ATK): {self.motor.heroe.ataque}",
            f"Defensa (DEF): {self.motor.heroe.defensa}",
            f"Oro acumulado: {self.motor.heroe.puntaje} pts",
            f"Zonas Exploradas: {self.motor.heroe.zonas_exploradas}/20"
        ]
        for indice, texto in enumerate(textos_stats):
            color = (100, 255, 100) if "Oro" in texto else COLOR_AMARILLO_MENU
            self.motor.pantalla.blit(self.motor.fuente.render(texto, True, color), (70, 180 + (indice * 35)))

        rect_inv = pygame.Rect(420, 100, 330, 420)
        pygame.draw.rect(self.motor.pantalla, COLOR_NEGRO_FONDO, rect_inv, border_radius=10)
        pygame.draw.rect(self.motor.pantalla, COLOR_GIRASOL_ACENTO, rect_inv, 3, border_radius=10)
        
        self.motor.pantalla.blit(self.motor.fuente_grande.render("Tu Mochila", True, COLOR_BLANCO), (440, 120))
        self.motor.pantalla.blit(self.motor.fuente.render("Usa Flechas y ENTER", True, COLOR_AMARILLO_MENU), (440, 160))
        pygame.draw.line(self.motor.pantalla, COLOR_GIRASOL_ACENTO, (440, 190), (730, 190), 2)

        inventario = self.motor.heroe.inventario
        if len(inventario) == 0:
            self.motor.pantalla.blit(self.motor.fuente.render("(La mochila esta vacia)", True, (150,150,150)), (440, 210))
        else:
            max_items = min(len(inventario), 7)
            inicio_lista = 0
            if self.cursor_inventario >= 7:
                inicio_lista = self.cursor_inventario - 6
                
            for i in range(max_items):
                idx_real = inicio_lista + i
                item = inventario[idx_real]
                
                es_seleccionado = (idx_real == self.cursor_inventario)
                color_item = COLOR_BLANCO if es_seleccionado else (150, 150, 150)
                marcador = "> " if es_seleccionado else "  "
                
                tipo_item = "[Pocion]" if isinstance(item, Consumible) else "[Objeto]"
                texto_item = f"{marcador}{tipo_item} {item.nombre}"
                self.motor.pantalla.blit(self.motor.fuente.render(texto_item, True, color_item), (440, 210 + (i * 30)))

class EstadoExploracion(EstadoJuego):
    def manejar_evento(self, evento):
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_t and self.motor.es_tienda:
                self.motor.estado_actual = self.motor.estado_tienda
                self.motor.mensaje_tienda = "¡Bienvenido! Tengo mercancia de primera."
            elif evento.key == pygame.K_ESCAPE:
                self.motor.estado_actual = self.motor.estado_pausa
            elif evento.key == pygame.K_i:
                self.motor.estado_actual = self.motor.estado_inventario

    def actualizar(self):
        self._procesar_movimiento_heroe()
        
        if self.motor.enemigo_en_zona and self.motor.enemigo_en_zona.esta_vivo():
            self.motor.enemigo_en_zona.actualizar_ia(self.motor.posicion_jugador_x, self.motor.posicion_jugador_y)
            self.motor.rectangulo_enemigo.x = self.motor.enemigo_en_zona.x
            self.motor.rectangulo_enemigo.y = self.motor.enemigo_en_zona.y

        self._verificar_colisiones_entidades()

    def _procesar_movimiento_heroe(self):
        teclas = pygame.key.get_pressed()
        esta_moviendose = False
        
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
            self.motor.posicion_jugador_x -= VELOCIDAD_MOVIMIENTO
            self.motor.mirando_izquierda = True
            esta_moviendose = True
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
            self.motor.posicion_jugador_x += VELOCIDAD_MOVIMIENTO
            self.motor.mirando_izquierda = False
            esta_moviendose = True
        if teclas[pygame.K_UP] or teclas[pygame.K_w]:
            self.motor.posicion_jugador_y -= VELOCIDAD_MOVIMIENTO
            esta_moviendose = True
        if teclas[pygame.K_DOWN] or teclas[pygame.K_s]:
            self.motor.posicion_jugador_y += VELOCIDAD_MOVIMIENTO
            esta_moviendose = True

        self.motor.accion_actual_heroe = "WALK" if esta_moviendose else "IDLE"
        self.motor.posicion_jugador_y = max(0, min(self.motor.posicion_jugador_y, ALTO_VENTANA - 60 - TAMANO_CELDA))

        if self.motor.posicion_jugador_x > ANCHO_VENTANA - TAMANO_CELDA:
            if self.motor.indice_zona_actual < len(self.motor.mundo.zonas) - 1:
                self.motor.indice_zona_actual += 1
                self.motor.cargar_zona()
                self.motor.posicion_jugador_x = 0 
                self.motor.heroe.zonas_exploradas += 1 
            else: self.motor.posicion_jugador_x = ANCHO_VENTANA - TAMANO_CELDA 
        elif self.motor.posicion_jugador_x < 0:
            if self.motor.indice_zona_actual > 0:
                self.motor.indice_zona_actual -= 1
                self.motor.cargar_zona()
                self.motor.posicion_jugador_x = ANCHO_VENTANA - TAMANO_CELDA 
            else: self.motor.posicion_jugador_x = 0 

    def _verificar_colisiones_entidades(self):
        rectangulo_heroe = pygame.Rect(self.motor.posicion_jugador_x, self.motor.posicion_jugador_y, TAMANO_CELDA, TAMANO_CELDA)
        
        if self.motor.enemigo_en_zona and self.motor.enemigo_en_zona.esta_vivo():
            if rectangulo_heroe.colliderect(self.motor.rectangulo_enemigo):
                self.motor.estado_actual = self.motor.estado_combate 
                self.motor.turno_actual = "JUGADOR"
                self.motor.mensaje_combate = f"¡Emboscada! {self.motor.enemigo_en_zona.nombre} te ataca."
                if self.motor.enemigo_en_zona.x < self.motor.posicion_jugador_x:
                    self.motor.posicion_jugador_x += 40 
                else:
                    self.motor.posicion_jugador_x -= 40
                    
                self.motor.efecto_combate_activo = None 
                if self.motor.usar_sonidos:
                    pygame.mixer.music.load(os.path.join("assets", "Sonidos", "fight soundtrack.ogg"))
                    pygame.mixer.music.play(-1)
                    
        if self.motor.objeto_en_zona:
            if rectangulo_heroe.colliderect(self.motor.rectangulo_objeto):
                if hasattr(self.motor.objeto_en_zona, 'dano_explosion'):
                    self.motor.heroe.recibir_dano(self.motor.objeto_en_zona.dano_explosion)
                    if not self.motor.heroe.esta_vivo():
                        self.motor.estado_fin.es_victoria = False
                        self.motor.estado_actual = self.motor.estado_fin
                else:
                    self.motor.heroe.recolectar_objeto(self.motor.objeto_en_zona)
                    self.motor.heroe.ganar_puntaje(50) 
                    if self.motor.usar_sonidos: self.motor.sonido_moneda.play()
                self.motor.mundo.zonas[self.motor.indice_zona_actual].objeto = None
                self.motor.objeto_en_zona = None

    def dibujar(self):
        if self.motor.usar_sprites:
            for x in range(0, ANCHO_VENTANA, TAMANO_CELDA):
                for y in range(0, ALTO_VENTANA - 60, TAMANO_CELDA):
                    self.motor.pantalla.blit(self.motor.imagen_suelo, (x, y))
        else: self.motor.pantalla.fill(COLOR_VERDE_PASTO)
            
        if self.motor.es_tienda:
            pygame.draw.rect(self.motor.pantalla, COLOR_MORADO_MERCADER, self.motor.rectangulo_mercader)
            texto_tienda = self.motor.fuente.render("Refugio del Mercader ('T')", True, COLOR_BLANCO)
            self.motor.pantalla.blit(texto_tienda, (ANCHO_VENTANA//2 - texto_tienda.get_width()//2, 160))
            
        if self.motor.objeto_en_zona:
            if self.motor.imagen_objeto: self.motor.pantalla.blit(self.motor.imagen_objeto, self.motor.rectangulo_objeto.topleft)
            else:
                color_obj = (139, 0, 0) if hasattr(self.motor.objeto_en_zona, 'dano_explosion') else COLOR_NARANJA_TESORO
                pygame.draw.rect(self.motor.pantalla, color_obj, self.motor.rectangulo_objeto)
                
        if self.motor.enemigo_en_zona and self.motor.enemigo_en_zona.esta_vivo():
            if self.motor.usar_sprites:
                if self.motor.enemigo_en_zona.estado_ia == "PERSIGUIENDO": anim_orco = self.motor.anim_enemigo_walk
                else: anim_orco = self.motor.anim_enemigo_idle
                
                indice_frame = self.motor.indice_animacion % len(anim_orco)
                imagen_orco = anim_orco[indice_frame]
                
                if self.motor.enemigo_en_zona.direccion_patrulla == -1 or (self.motor.enemigo_en_zona.estado_ia == "PERSIGUIENDO" and self.motor.posicion_jugador_x < self.motor.enemigo_en_zona.x):
                    imagen_orco = pygame.transform.flip(imagen_orco, True, False)

                pos_e_x = self.motor.rectangulo_enemigo.x - OFFSET_X
                pos_e_y = self.motor.rectangulo_enemigo.y - OFFSET_Y
                self.motor.pantalla.blit(imagen_orco, (pos_e_x, pos_e_y))
            else: pygame.draw.rect(self.motor.pantalla, COLOR_ROJO_ENEMIGO, self.motor.rectangulo_enemigo)
                
        if self.motor.usar_sprites:
            lista_frames = self.motor.anim_heroe_walk if self.motor.accion_actual_heroe == "WALK" else self.motor.anim_heroe_idle
            indice_frame = self.motor.indice_animacion % len(lista_frames)
            imagen_actual = lista_frames[indice_frame]
            if self.motor.mirando_izquierda: imagen_actual = pygame.transform.flip(imagen_actual, True, False)
            
            pos_h_x = self.motor.posicion_jugador_x - OFFSET_X
            pos_h_y = self.motor.posicion_jugador_y - OFFSET_Y
            self.motor.pantalla.blit(imagen_actual, (pos_h_x, pos_h_y))
        else:
            rect_h = pygame.Rect(self.motor.posicion_jugador_x, self.motor.posicion_jugador_y, TAMANO_CELDA, TAMANO_CELDA)
            pygame.draw.rect(self.motor.pantalla, COLOR_AZUL_HEROE, rect_h)

        if not self.motor.es_tienda and self.motor.usar_sprites:
            superficie_niebla = pygame.Surface((ANCHO_VENTANA, ALTO_VENTANA), pygame.SRCALPHA)
            superficie_niebla.fill((5, 5, 10, 250)) 
            
            centro_heroe_x = self.motor.posicion_jugador_x + (TAMANO_CELDA // 2)
            centro_heroe_y = self.motor.posicion_jugador_y + (TAMANO_CELDA // 2)
            
            superficie_niebla.blit(self.motor.imagen_luz, (centro_heroe_x - 250, centro_heroe_y - 250), special_flags=pygame.BLEND_RGBA_MIN)
            self.motor.pantalla.blit(superficie_niebla, (0, 0))


class EstadoCombate(EstadoJuego):
    def manejar_evento(self, evento):
        if evento.type != pygame.KEYDOWN: return
        
        if self.motor.turno_actual == "JUGADOR":
            habilidad_seleccionada = None
            
            if evento.key == pygame.K_a:
                habilidad_seleccionada = AtaqueBasico()
                self.motor.efecto_combate_activo = "HEROE_ATACA"
            elif evento.key == pygame.K_s:
                habilidad_seleccionada = GolpeEspecial()
                self.motor.efecto_combate_activo = "HEROE_ATACA"
            elif evento.key == pygame.K_c:
                habilidad_seleccionada = Curacion()
                self.motor.efecto_combate_activo = "HEROE_ATACA" 
                
            if habilidad_seleccionada:
                if self.motor.heroe.puntos_magia < habilidad_seleccionada.costo_mp:
                    self.motor.mensaje_combate = "¡No tienes suficiente Mana (MP) para hacer eso!"
                    return 
                
                if self.motor.usar_sonidos and evento.key != pygame.K_c: 
                    self.motor.sonido_ataque.play()

                self.motor.tiempo_inicio_efecto = pygame.time.get_ticks()
                self.motor.indice_animacion = 0 
                
                danio, msg = habilidad_seleccionada.ejecutar(self.motor.heroe, self.motor.enemigo_en_zona)
                self.motor.mensaje_combate = msg
                
                if danio > 0:
                    texto_danio = TextoFlotante(f"-{danio}", 500, 150, COLOR_BLANCO, self.motor.fuente_gigante)
                    self.motor.textos_flotantes.append(texto_danio)
                elif evento.key == pygame.K_c:
                    texto_cura = TextoFlotante("+HP", 200, 150, (100, 255, 100), self.motor.fuente_gigante)
                    self.motor.textos_flotantes.append(texto_cura)

                if not self.motor.enemigo_en_zona.esta_vivo(): 
                    self.motor.turno_actual = "VICTORIA"
                else: 
                    self.motor.turno_actual = "ENEMIGO"
                    
        elif self.motor.turno_actual == "ENEMIGO":
            if evento.key == pygame.K_SPACE:
                self.motor.efecto_combate_activo = "ENEMIGO_ATACA"
                self.motor.tiempo_inicio_efecto = pygame.time.get_ticks()
                self.motor.indice_animacion = 0
                
                ataque_enemigo = AtaqueBasico()
                danio, msg = ataque_enemigo.ejecutar(self.motor.enemigo_en_zona, self.motor.heroe)
                self.motor.mensaje_combate = msg
                
                texto_danio = TextoFlotante(f"-{danio}", 200, 150, COLOR_ROJO_ENEMIGO, self.motor.fuente_gigante)
                self.motor.textos_flotantes.append(texto_danio)
                
                if not self.motor.heroe.esta_vivo():
                    self.motor.turno_actual = "DERROTA"
                    self.motor.estado_fin.es_victoria = False
                else: 
                    self.motor.turno_actual = "JUGADOR"
                    
        elif self.motor.turno_actual == "VICTORIA":
            if evento.key == pygame.K_RETURN:
                self.motor.heroe.ganar_experiencia(100)
                self.motor.efecto_combate_activo = None
                self.motor.textos_flotantes.clear() 
                if self.motor.enemigo_en_zona.nombre == "Rey Demonio":
                    self.motor.estado_fin.es_victoria = True
                    self.motor.estado_actual = self.motor.estado_fin
                else:
                    self.motor.estado_actual = self.motor.estado_exploracion
                    if self.motor.usar_sonidos:
                        pygame.mixer.music.load(os.path.join("assets", "Sonidos", "game soundtrack.mp3"))
                        pygame.mixer.music.play(-1)
                        
        elif self.motor.turno_actual == "DERROTA":
            if evento.key == pygame.K_RETURN:
                self.motor.textos_flotantes.clear()
                self.motor.estado_actual = self.motor.estado_fin

    def actualizar(self):
        for texto in self.motor.textos_flotantes[:]:
            texto.actualizar()
            if texto.opacidad <= 0: self.motor.textos_flotantes.remove(texto)

    def dibujar(self):
        self.motor.pantalla.fill(COLOR_NEGRO_FONDO)
        texto_vs = self.motor.fuente_grande.render(f"VS {self.motor.enemigo_en_zona.nombre}", True, COLOR_ROJO_ENEMIGO)
        texto_vida_e = self.motor.fuente.render(f"Vida Enemigo: {self.motor.enemigo_en_zona.puntos_vida}", True, COLOR_BLANCO)
        self.motor.pantalla.blit(texto_vs, (ANCHO_VENTANA // 2 - texto_vs.get_width() // 2, 30))
        self.motor.pantalla.blit(texto_vida_e, (ANCHO_VENTANA // 2 - texto_vida_e.get_width() // 2, 80))
        
        if self.motor.usar_sprites:
            tiempo_actual = pygame.time.get_ticks()
            duracion = tiempo_actual - self.motor.tiempo_inicio_efecto
            
            if self.motor.efecto_combate_activo == "HEROE_ATACA" and duracion < 600: frame_idx = min(self.motor.indice_animacion, len(self.motor.anim_heroe_attack) - 1); img_heroe = self.motor.anim_heroe_attack[frame_idx]
            else: frame_idx = self.motor.indice_animacion % len(self.motor.anim_heroe_idle); img_heroe = self.motor.anim_heroe_idle[frame_idx]
                
            if self.motor.efecto_combate_activo == "ENEMIGO_ATACA" and duracion < 600: frame_idx = min(self.motor.indice_animacion, len(self.motor.anim_enemigo_attack) - 1); img_enemigo = self.motor.anim_enemigo_attack[frame_idx]
            else: frame_idx = self.motor.indice_animacion % len(self.motor.anim_enemigo_idle); img_enemigo = self.motor.anim_enemigo_idle[frame_idx]
                
            self.motor.pantalla.blit(pygame.transform.scale(img_heroe, (250, 250)), (100, 100))
            enemigo_g = pygame.transform.scale(img_enemigo, (250, 250))
            self.motor.pantalla.blit(pygame.transform.flip(enemigo_g, True, False), (450, 100))
            
        rect_mensaje = pygame.Rect(100, 350, 600, 150)
        pygame.draw.rect(self.motor.pantalla, COLOR_GRIS_PANEL, rect_mensaje)
        pygame.draw.rect(self.motor.pantalla, COLOR_AMARILLO_MENU, rect_mensaje, 3)
        self.motor.pantalla.blit(self.motor.fuente.render(self.motor.mensaje_combate, True, COLOR_BLANCO), (120, 370))
        
        if self.motor.turno_actual == "JUGADOR": 
            inst = "[A] Basico | [S] Feroz (-15 MP) | [C] Curar (-20 MP)"
            color_inst = COLOR_AMARILLO_MENU
        elif self.motor.turno_actual == "ENEMIGO": inst = "▶ Presiona 'ESPACIO' para recibir ataque"; color_inst = COLOR_AMARILLO_MENU
        elif self.motor.turno_actual == "VICTORIA": inst = "▶ ¡Victoria! Presiona 'ENTER' para seguir"; color_inst = (100, 255, 100)
        elif self.motor.turno_actual == "DERROTA": inst = "▶ Has caido... Presiona 'ENTER'"; color_inst = COLOR_ROJO_ENEMIGO
            
        self.motor.pantalla.blit(self.motor.fuente.render(inst, True, color_inst), (120, 450))
        for texto in self.motor.textos_flotantes: texto.dibujar(self.motor.pantalla)

class EstadoTienda(EstadoJuego):
    def manejar_evento(self, evento):
        if evento.type != pygame.KEYDOWN: return
        
        if evento.key == pygame.K_b:
            if self.motor.heroe.puntaje >= self.motor.objeto_tienda.precio_compra:
                self.motor.heroe.puntaje -= self.motor.objeto_tienda.precio_compra
                self.motor.heroe.equipar(self.motor.objeto_tienda)
                if self.motor.usar_sonidos: self.motor.sonido_moneda.play()
                
                self.motor.mensaje_tienda = f"¡Equipado: {self.motor.objeto_tienda.nombre}!"
                n_atk = self.motor.objeto_tienda.aumento_ataque + 5
                n_def = self.motor.objeto_tienda.aumento_defensa + 5
                n_precio = self.motor.objeto_tienda.precio_compra + 100
                self.motor.objeto_tienda = Equipamiento(f"Arma Mejorada +{n_atk}", n_atk, n_def, n_precio, n_precio//2)
            else: 
                self.motor.mensaje_tienda = "No tienes suficiente Oro para el Arma."
                
        elif evento.key == pygame.K_1:
            if self.motor.heroe.puntaje >= 30:
                self.motor.heroe.puntaje -= 30
                self.motor.heroe.recolectar_objeto(Consumible("Pocion de Vida", "HP", 50, 30))
                self.motor.mensaje_tienda = "¡Pocion de Vida guardada en tu mochila!"
                if self.motor.usar_sonidos: self.motor.sonido_moneda.play()
            else:
                self.motor.mensaje_tienda = "Oro insuficiente para la pocion."
                
        elif evento.key == pygame.K_2:
            if self.motor.heroe.puntaje >= 30:
                self.motor.heroe.puntaje -= 30
                self.motor.heroe.recolectar_objeto(Consumible("Pocion de Mana", "MP", 50, 30))
                self.motor.mensaje_tienda = "¡Pocion de Mana guardada en tu mochila!"
                if self.motor.usar_sonidos: self.motor.sonido_moneda.play()
            else:
                self.motor.mensaje_tienda = "Oro insuficiente para la pocion."

        elif evento.key == pygame.K_RETURN or evento.key == pygame.K_ESCAPE: 
            self.motor.estado_actual = self.motor.estado_exploracion 

    def dibujar(self):
        self.motor.estado_exploracion.dibujar()
        superficie = pygame.Surface((ANCHO_VENTANA, ALTO_VENTANA))
        superficie.set_alpha(235)
        superficie.fill((20, 15, 30)) 
        self.motor.pantalla.blit(superficie, (0, 0))

        titulo = self.motor.fuente_gigante.render("~ El Refugio del Mercader ~", True, COLOR_MORADO_MERCADER)
        self.motor.pantalla.blit(titulo, (ANCHO_VENTANA // 2 - titulo.get_width() // 2, 40))

        rect_jugador = pygame.Rect(50, 130, 320, 220)
        pygame.draw.rect(self.motor.pantalla, COLOR_GRIS_PANEL, rect_jugador, border_radius=15)
        pygame.draw.rect(self.motor.pantalla, COLOR_BLANCO, rect_jugador, 2, border_radius=15)
        
        self.motor.pantalla.blit(self.motor.fuente_grande.render("Tus Bolsillos", True, COLOR_BLANCO), (70, 140))
        self.motor.pantalla.blit(self.motor.fuente.render(f"Oro disponible: {self.motor.heroe.puntaje} pts", True, (100, 255, 100)), (70, 200))
        self.motor.pantalla.blit(self.motor.fuente.render(f"Ataque actual: {self.motor.heroe.ataque}", True, COLOR_AMARILLO_MENU), (70, 240))
        self.motor.pantalla.blit(self.motor.fuente.render(f"Defensa actual: {self.motor.heroe.defensa}", True, COLOR_AMARILLO_MENU), (70, 280))

        rect_item = pygame.Rect(420, 130, 330, 220)
        pygame.draw.rect(self.motor.pantalla, (40, 20, 50), rect_item, border_radius=15) 
        pygame.draw.rect(self.motor.pantalla, COLOR_GIRASOL_ACENTO, rect_item, 3, border_radius=15)
        
        self.motor.pantalla.blit(self.motor.fuente_grande.render("Ofertas del Dia", True, COLOR_GIRASOL_ACENTO), (440, 140))
        self.motor.pantalla.blit(self.motor.fuente.render(f"[ B ] Arma: {self.motor.objeto_tienda.nombre} ({self.motor.objeto_tienda.precio_compra} Oro)", True, COLOR_BLANCO), (440, 200))
        self.motor.pantalla.blit(self.motor.fuente.render(f"[ 1 ] Pocion de Vida (+50 HP) : 30 Oro", True, (255, 100, 100)), (440, 240))
        self.motor.pantalla.blit(self.motor.fuente.render(f"[ 2 ] Pocion de Mana (+50 MP) : 30 Oro", True, (100, 200, 255)), (440, 280))

        rect_msg = pygame.Rect(50, 380, 700, 130)
        pygame.draw.rect(self.motor.pantalla, COLOR_NEGRO_FONDO, rect_msg, border_radius=10)
        pygame.draw.rect(self.motor.pantalla, COLOR_MORADO_MERCADER, rect_msg, 3, border_radius=10)
        
        self.motor.pantalla.blit(self.motor.fuente.render(f"Mercader: \"{self.motor.mensaje_tienda}\"", True, COLOR_BLANCO), (80, 400))
        self.motor.pantalla.blit(self.motor.fuente.render("[ ENTER ] Salir de la Tienda", True, COLOR_AMARILLO_MENU), (80, 460))