# ui/elementos.py

class TextoFlotante:
    """Controla los números de daño que saltan en la pantalla de combate."""
    def __init__(self, texto, x, y, color, fuente):
        self.texto = texto
        self.x = x
        self.y = y
        self.color = color
        self.fuente = fuente
        self.opacidad = 255 # 255 es sólido, 0 es invisible
        self.velocidad_subida = 2 # Píxeles que sube por cada frame

    def actualizar(self):
        self.y -= self.velocidad_subida
        self.opacidad -= 5 # Se desvanece gradualmente

    def dibujar(self, pantalla):
        if self.opacidad > 0:
            superficie_texto = self.fuente.render(self.texto, True, self.color)
            # Aplicamos la transparencia
            superficie_texto.set_alpha(self.opacidad)
            pantalla.blit(superficie_texto, (self.x, self.y))