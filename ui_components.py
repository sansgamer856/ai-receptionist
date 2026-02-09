import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QProgressBar, QGridLayout
)
from PyQt5.QtCore import Qt, QRectF, QTimer
from PyQt5.QtGui import (
    QColor, QPainter, QPen, QFont, QBrush, QLinearGradient, QPalette
)
from PyQt5.QtWidgets import QGraphicsDropShadowEffect

# --- Constants for Styling ---
BG_COLOR = QColor("#0a0b10") # Dark background
PANEL_BG = QColor("#141622") # Slightly lighter panel background
ACCENT_COLOR = QColor("#00eaff") # Bright cyan/blue
ACCENT_GLOW = QColor("#00eaff40") # Faint glow of the accent
TEXT_COLOR = QColor("#ffffff")
FONT_FAMILY = "Orbitron" # A futuristic-looking font (you might need to install it)
FONT_SIZE_TITLE = 16
FONT_SIZE_VALUE = 28
FONT_SIZE_LABEL = 10

# --- Helper Functions ---
def get_glow_effect(color=ACCENT_COLOR, blur_radius=20, offset=0):
    """Creates a drop shadow effect to simulate a glow."""
    effect = QGraphicsDropShadowEffect()
    effect.setBlurRadius(blur_radius)
    effect.setColor(color)
    effect.setOffset(offset)
    return effect

# --- Custom UI Components ---

class GlowingPanel(QWidget):
    """A square/rectangular panel with a glowing border and title."""
    def __init__(self, title="PANEL"):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        # Title Label
        self.title_label = QLabel(title)
        self.title_label.setFont(QFont(FONT_FAMILY, FONT_SIZE_LABEL, QFont.Bold))
        self.title_label.setStyleSheet(f"color: {ACCENT_COLOR.name()};")
        self.title_label.setAlignment(Qt.AlignLeft)
        self.layout.addWidget(self.title_label)
        
        # Content placeholder (will be filled by subclasses or addWidget)
        self.content_layout = QVBoxLayout()
        self.layout.addLayout(self.content_layout)

        # Apply styles for the panel background and border
        self.setStyleSheet(f"""
            GlowingPanel {{
                background-color: {PANEL_BG.name()};
                border: 1px solid {ACCENT_COLOR.name()};
                border-radius: 8px;
            }}
        """)
        
        # Add a glow effect to the entire panel
        self.setGraphicsEffect(get_glow_effect(blur_radius=25))

    def add_widget(self, widget):
        """Adds a widget to the panel's content area."""
        self.content_layout.addWidget(widget)

class CircularGauge(QWidget):
    """A circular gauge to display a percentage value."""
    def __init__(self, title="GAUGE", value=0):
        super().__init__()
        self.title = title
        self.value = value
        self.setMinimumSize(150, 150)

    def set_value(self, value):
        self.value = max(0, min(100, value))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # --- Define Geometry ---
        rect = self.rect()
        center = rect.center()
        size = min(rect.width(), rect.height())
        outer_radius = (size / 2) - 10
        inner_radius = outer_radius - 15
        
        # --- Draw Outer Ring (Track) ---
        pen = QPen(QColor("#2a2d3d"), 8)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        painter.drawEllipse(center, outer_radius, outer_radius)

        # --- Draw Progress Arc ---
        pen.setColor(ACCENT_COLOR)
        painter.setPen(pen)
        
        # Calculate angles
        start_angle = -90 * 16 # Start from top
        span_angle = -int((self.value / 100) * 360 * 16)

        arc_rect = QRectF(center.x() - outer_radius, center.y() - outer_radius, 
                          outer_radius * 2, outer_radius * 2)
        painter.drawArc(arc_rect, start_angle, span_angle)

        # --- Draw Central Text (Value) ---
        painter.setPen(TEXT_COLOR)
        painter.setFont(QFont(FONT_FAMILY, FONT_SIZE_VALUE, QFont.Bold))
        painter.drawText(rect, Qt.AlignCenter, f"{self.value}%")
        
        # --- Draw Title Text ---
        painter.setPen(ACCENT_COLOR)
        painter.setFont(QFont(FONT_FAMILY, FONT_SIZE_LABEL))
        title_rect = QRectF(rect.left(), rect.bottom() - 30, rect.width(), 30)
        painter.drawText(title_rect, Qt.AlignCenter, self.title)

class FuturisticProgressBar(QProgressBar):
    """A progress bar with a glowing, segmented look."""
    def __init__(self):
        super().__init__()
        self.setTextVisible(False)
        self.setFixedHeight(12)
        
        # Apply custom styling with QSS
        self.setStyleSheet(f"""
            QProgressBar {{
                background-color: {PANEL_BG.name()};
                border: 1px solid {ACCENT_COLOR.name()};
                border-radius: 6px;
            }}
            QProgressBar::chunk {{
                background-color: {ACCENT_COLOR.name()};
                border-radius: 4px;
                /* A small gradient for a more metallic/glowing look */
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 {ACCENT_COLOR.name()},
                                            stop:1 #80faff);
            }}
        """)
        # Add a subtle glow to the progress chunk itself
        self.setGraphicsEffect(get_glow_effect(blur_radius=10))

class DataLabel(QWidget):
    """A simple widget for a label-value pair."""
    def __init__(self, label_text, value_text):
        super().__init__()
        layout = QHBoxLayout()
        self.setLayout(layout)
        layout.setContentsMargins(0, 5, 0, 5)
        
        lbl = QLabel(label_text)
        lbl.setFont(QFont(FONT_FAMILY, FONT_SIZE_LABEL))
        lbl.setStyleSheet(f"color: {ACCENT_COLOR.name()};")
        layout.addWidget(lbl)
        
        val = QLabel(value_text)
        val.setFont(QFont(FONT_FAMILY, FONT_SIZE_LABEL + 2, QFont.Bold))
        val.setStyleSheet(f"color: {TEXT_COLOR.name()};")
        val.setAlignment(Qt.AlignRight)
        layout.addWidget(val)

# --- Main Application Window ---
class DashboardWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Futuristic Dashboard UI")
        self.setMinimumSize(900, 600)
        
        # Set main window background
        palette = self.palette()
        palette.setColor(QPalette.Window, BG_COLOR)
        self.setPalette(palette)

        # Central Widget & Main Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QGridLayout()
        central_widget.setLayout(main_layout)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # --- Build the UI Layout ---
        
        # Panel 1: Main System Status (Top Left)
        panel1 = GlowingPanel("MAIN SYSTEM STATUS")
        
        # Add a Circular Gauge
        self.sys_gauge = CircularGauge("SYSTEM LOAD", 47)
        panel1.add_widget(self.sys_gauge)
        
        # Add some data labels
        panel1.add_widget(DataLabel("CPU TEMP:", "65°C"))
        panel1.add_widget(DataLabel("MEMORY USAGE:", "8.2 GB"))
        
        main_layout.addWidget(panel1, 0, 0)

        # Panel 2: Power & Energy (Top Right)
        panel2 = GlowingPanel("POWER & ENERGY")
        
        # Add Progress Bars
        lbl_p1 = QLabel("REACTOR CORE 1")
        lbl_p1.setStyleSheet(f"color: {TEXT_COLOR.name()}; font-family: {FONT_FAMILY};")
        panel2.add_widget(lbl_p1)
        self.prog_bar1 = FuturisticProgressBar()
        self.prog_bar1.setValue(78)
        panel2.add_widget(self.prog_bar1)
        
        lbl_p2 = QLabel("CAPACITOR BANK")
        lbl_p2.setStyleSheet(f"color: {TEXT_COLOR.name()}; font-family: {FONT_FAMILY}; font-size: {FONT_SIZE_LABEL}px;")
        panel2.add_widget(lbl_p2)
        self.prog_bar2 = FuturisticProgressBar()
        self.prog_bar2.setValue(52)
        panel2.add_widget(self.prog_bar2)
        
        main_layout.addWidget(panel2, 0, 1)
        
        # Panel 3: Navigation & Diagnostics (Bottom - spanning both columns)
        panel3 = GlowingPanel("NAVIGATION & DIAGNOSTICS")
        
        # A horizontal layout inside this panel
        h_layout = QHBoxLayout()
        
        # Fake Radar/Map Area
        radar_widget = QLabel("RADAR / MAP DISPLAY")
        radar_widget.setAlignment(Qt.AlignCenter)
        radar_widget.setStyleSheet(f"""
            background-color: {PANEL_BG.darker(120).name()}; 
            color: {ACCENT_COLOR.name()};
            border: 1px dashed {ACCENT_COLOR.name()};
            border-radius: 50%;
        """)
        radar_widget.setMinimumSize(200, 200)
        h_layout.addWidget(radar_widget)
        
        # Diagnostic Data List
        v_layout = QVBoxLayout()
        v_layout.addWidget(DataLabel("LATITUDE:", "34.0522° N"))
        v_layout.addWidget(DataLabel("LONGITUDE:", "118.2437° W"))
        v_layout.addWidget(DataLabel("ALTITUDE:", "12,500 ft"))
        v_layout.addWidget(DataLabel("VELOCITY:", "450 kts"))
        
        h_layout.addLayout(v_layout)
        panel3.add_widget(QWidget()) # Spacer
        panel3.content_layout.addLayout(h_layout)
        
        main_layout.addWidget(panel3, 1, 0, 1, 2) # Span 1 row, 2 columns

        # --- Simple Timer to simulate data changes ---
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(2000) # Update every 2 seconds

    def update_data(self):
        """Simulates changing data for a live-feeling demo."""
        import random
        new_load = self.sys_gauge.value + random.randint(-5, 5)
        self.sys_gauge.set_value(new_load)
        
        new_prog1 = self.prog_bar1.value() + random.randint(-3, 3)
        self.prog_bar1.setValue(max(0, min(100, new_prog1)))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Optional: Load a futuristic font
    # QFontDatabase.addApplicationFont("path/to/Orbitron.ttf")

    window = DashboardWindow()
    window.show()
    sys.exit(app.exec_())