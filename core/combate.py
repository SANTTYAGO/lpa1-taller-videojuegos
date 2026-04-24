# core/combate.py
import random

class HabilidadCombate:
    """Clase Base (Interfaz) para cualquier tipo de habilidad en combate"""
    def __init__(self, nombre, costo_mp=0):
        self.nombre = nombre
        self.costo_mp = costo_mp

    def ejecutar(self, atacante, defensor):
        raise NotImplementedError("Este método debe ser sobrescrito por las clases hijas.")


class AtaqueBasico(HabilidadCombate):
    """Ataque normal sin costo. Resta defensa directamente."""
    def __init__(self):
        super().__init__("Ataque Básico", costo_mp=0)

    def ejecutar(self, atacante, defensor):
        # Pequeña variación aleatoria para no hacer el mismo daño siempre
        variacion = random.randint(-2, 2)
        dano = max(1, atacante.ataque - defensor.defensa + variacion)
        defensor.recibir_dano(dano)
        return dano, f"¡{atacante.nombre} ataca! Causa {dano} pts de daño."


class GolpeEspecial(HabilidadCombate):
    """Ataque poderoso. Consume MP, escala al 180% e ignora mitad de armadura."""
    def __init__(self):
        super().__init__("Golpe Feroz", costo_mp=15)

    def ejecutar(self, atacante, defensor):
        atacante.puntos_magia -= self.costo_mp
        dano_base = atacante.ataque * 1.8
        # Ignora el 60% de la defensa enemiga
        dano = max(5, int(dano_base - (defensor.defensa * 0.4))) 
        defensor.recibir_dano(dano)
        return dano, f"¡{atacante.nombre} usa {self.nombre}! CRÍTICO de {dano} pts."


class Curacion(HabilidadCombate):
    """Magia defensiva. Consume mucho MP pero restaura HP."""
    def __init__(self):
        super().__init__("Luz Sanadora", costo_mp=20)

    def ejecutar(self, atacante, defensor):
        atacante.puntos_magia -= self.costo_mp
        cura = 30 + (atacante.nivel * 10) # Cura más mientras más nivel tengas
        atacante.puntos_vida = min(atacante.puntos_vida_max, atacante.puntos_vida + cura)
        # Retorna daño 0 porque es curación
        return 0, f"¡{atacante.nombre} usa {self.nombre}! Recupera {cura} HP."