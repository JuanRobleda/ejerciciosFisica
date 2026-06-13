import math
import tkinter as tk
from tkinter import ttk


G = 9.81


class SimuladorCazador:
    def __init__(self, root):
        self.root = root
        self.root.title("Cazador y mono")
        self.root.geometry("980x650")
        self.root.minsize(880, 560)

        self.variables = {
            "x_mono": tk.DoubleVar(value=15.0),
            "y_mono": tk.DoubleVar(value=20.0),
            "y_cazador": tk.DoubleVar(value=1.8),
            "v0": tk.DoubleVar(value=20.0),
            "t_max": tk.DoubleVar(value=3.0),
            "paso": tk.DoubleVar(value=0.5),
        }

        self._crear_interfaz()
        self.actualizar()

    def _crear_interfaz(self):
        contenedor = ttk.Frame(self.root, padding=12)
        contenedor.pack(fill="both", expand=True)
        contenedor.columnconfigure(1, weight=1)
        contenedor.rowconfigure(0, weight=1)

        panel = ttk.Frame(contenedor, padding=(0, 0, 12, 0))
        panel.grid(row=0, column=0, sticky="ns")

        ttk.Label(panel, text="Controles", font=("Segoe UI", 14, "bold")).pack(anchor="w")

        self._control(panel, "Distancia al mono (m)", "x_mono", 5, 60)
        self._control(panel, "Altura del mono (m)", "y_mono", 2, 50)
        self._control(panel, "Altura del cazador (m)", "y_cazador", 0, 5)
        self._control(panel, "Velocidad inicial (m/s)", "v0", 1, 60)
        self._control(panel, "Tiempo maximo (s)", "t_max", 0.5, 8)
        self._control(panel, "Paso de tiempo (s)", "paso", 0.1, 1.0)

        self.info = ttk.Label(panel, justify="left", font=("Segoe UI", 10))
        self.info.pack(anchor="w", pady=(16, 0))

        ttk.Button(panel, text="Restablecer", command=self.restablecer).pack(anchor="w", pady=(14, 0))

        area = ttk.Frame(contenedor)
        area.grid(row=0, column=1, sticky="nsew")
        area.columnconfigure(0, weight=1)
        area.rowconfigure(0, weight=1)

        self.canvas = tk.Canvas(area, bg="#f7fbff", highlightthickness=1, highlightbackground="#9fb3c8")
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.canvas.bind("<Configure>", lambda _event: self.actualizar())

        tabla_frame = ttk.Frame(area, padding=(0, 10, 0, 0))
        tabla_frame.grid(row=1, column=0, sticky="ew")
        tabla_frame.columnconfigure(0, weight=1)

        columnas = ("t", "y_mono", "x_proy", "y_proy")
        self.tabla = ttk.Treeview(tabla_frame, columns=columnas, show="headings", height=7)
        self.tabla.heading("t", text="t (s)")
        self.tabla.heading("y_mono", text="Y mono (m)")
        self.tabla.heading("x_proy", text="X bala (m)")
        self.tabla.heading("y_proy", text="Y bala (m)")

        for columna in columnas:
            self.tabla.column(columna, width=115, anchor="center")

        self.tabla.grid(row=0, column=0, sticky="ew")

        barra = ttk.Scrollbar(tabla_frame, orient="vertical", command=self.tabla.yview)
        barra.grid(row=0, column=1, sticky="ns")
        self.tabla.configure(yscrollcommand=barra.set)

    def _control(self, padre, texto, nombre, minimo, maximo):
        marco = ttk.Frame(padre)
        marco.pack(fill="x", pady=(12, 0))

        ttk.Label(marco, text=texto).pack(anchor="w")

        fila = ttk.Frame(marco)
        fila.pack(fill="x", pady=(3, 0))

        escala = ttk.Scale(
            fila,
            from_=minimo,
            to=maximo,
            variable=self.variables[nombre],
            command=lambda _valor: self.actualizar(),
        )
        escala.pack(side="left", fill="x", expand=True)

        entrada = ttk.Entry(fila, textvariable=self.variables[nombre], width=7)
        entrada.pack(side="left", padx=(8, 0))
        entrada.bind("<Return>", lambda _event: self.actualizar())
        entrada.bind("<FocusOut>", lambda _event: self.actualizar())

    def restablecer(self):
        valores = {
            "x_mono": 15.0,
            "y_mono": 20.0,
            "y_cazador": 1.8,
            "v0": 20.0,
            "t_max": 3.0,
            "paso": 0.5,
        }

        for nombre, valor in valores.items():
            self.variables[nombre].set(valor)

        self.actualizar()

    def calcular(self):
        x_mono = max(0.1, self.variables["x_mono"].get())
        y_mono = self.variables["y_mono"].get()
        y_cazador = self.variables["y_cazador"].get()
        v0 = max(0.1, self.variables["v0"].get())
        t_max = max(0.1, self.variables["t_max"].get())
        paso = max(0.1, self.variables["paso"].get())

        theta = math.atan2(y_mono - y_cazador, x_mono)
        vx = v0 * math.cos(theta)
        vy = v0 * math.sin(theta)

        datos = []
        t = 0.0
        while t <= t_max + 1e-9:
            y_mono_t = y_mono - 0.5 * G * t**2
            x_proy = vx * t
            y_proy = y_cazador + vy * t - 0.5 * G * t**2
            datos.append((t, y_mono_t, x_proy, y_proy))
            t += paso

        return theta, vx, vy, datos

    def actualizar(self):
        try:
            theta, vx, _vy, datos = self.calcular()
        except (tk.TclError, ValueError):
            return

        self.info.configure(
            text=(
                f"Angulo: {math.degrees(theta):.2f} grados\n"
                f"Velocidad horizontal: {vx:.2f} m/s\n"
                f"Gravedad: {G:.2f} m/s2"
            )
        )

        for item in self.tabla.get_children():
            self.tabla.delete(item)

        for t, y_mono, x_proy, y_proy in datos:
            self.tabla.insert(
                "",
                "end",
                values=(f"{t:.2f}", f"{y_mono:.2f}", f"{x_proy:.2f}", f"{y_proy:.2f}"),
            )

        self.dibujar(datos)

    def dibujar(self, datos):
        self.canvas.delete("all")

        ancho = max(10, self.canvas.winfo_width())
        alto = max(10, self.canvas.winfo_height())
        margen = 42

        x_mono = self.variables["x_mono"].get()
        y_mono_inicial = self.variables["y_mono"].get()
        y_cazador = self.variables["y_cazador"].get()

        max_x = max(x_mono, *(x for _t, _ym, x, _yp in datos), 1) * 1.1
        max_y = max(y_mono_inicial, y_cazador, *(max(ym, yp) for _t, ym, _x, yp in datos), 1) * 1.15
        min_y = min(0, *(min(ym, yp) for _t, ym, _x, yp in datos))

        def px(x):
            return margen + (x / max_x) * (ancho - 2 * margen)

        def py(y):
            rango_y = max_y - min_y
            return alto - margen - ((y - min_y) / rango_y) * (alto - 2 * margen)

        suelo_y = py(0)
        self.canvas.create_line(margen, suelo_y, ancho - margen, suelo_y, fill="#425466", width=2)
        self.canvas.create_line(margen, margen, margen, alto - margen, fill="#425466", width=2)
        self.canvas.create_text(ancho - margen, suelo_y + 18, text="x", fill="#425466")
        self.canvas.create_text(margen - 16, margen, text="y", fill="#425466")

        puntos_bala = []
        puntos_mono = []
        for _t, y_mono, x_proy, y_proy in datos:
            puntos_bala.extend((px(x_proy), py(y_proy)))
            puntos_mono.extend((px(x_mono), py(y_mono)))

        if len(puntos_bala) >= 4:
            self.canvas.create_line(*puntos_bala, fill="#d1495b", width=3, smooth=True)

        if len(puntos_mono) >= 4:
            self.canvas.create_line(*puntos_mono, fill="#00798c", width=2, dash=(5, 4))

        cazador_x = px(0)
        cazador_y = py(y_cazador)
        self.canvas.create_oval(cazador_x - 8, cazador_y - 8, cazador_x + 8, cazador_y + 8, fill="#29335c", outline="")
        self.canvas.create_text(cazador_x + 34, cazador_y - 14, text="Cazador", fill="#29335c")

        mono_x = px(x_mono)
        mono_y = py(y_mono_inicial)
        self.canvas.create_oval(mono_x - 9, mono_y - 9, mono_x + 9, mono_y + 9, fill="#edae49", outline="")
        self.canvas.create_line(mono_x, mono_y, mono_x, py(0), fill="#8d6e63", dash=(4, 4))
        self.canvas.create_text(mono_x - 28, mono_y - 16, text="Mono", fill="#6d4c41")

        if datos:
            _t, y_mono_final, x_bala_final, y_bala_final = datos[-1]
            self.canvas.create_oval(
                px(x_bala_final) - 6,
                py(y_bala_final) - 6,
                px(x_bala_final) + 6,
                py(y_bala_final) + 6,
                fill="#d1495b",
                outline="",
            )
            self.canvas.create_oval(
                mono_x - 6,
                py(y_mono_final) - 6,
                mono_x + 6,
                py(y_mono_final) + 6,
                fill="#00798c",
                outline="",
            )


if __name__ == "__main__":
    ventana = tk.Tk()
    app = SimuladorCazador(ventana)
    ventana.mainloop()
