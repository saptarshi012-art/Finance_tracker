import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, QPoint, QAbstractAnimation
from PyQt5.QtGui import QFont, QColor, QPainter, QPen, QIcon

from src.database import init_db
from src.expense_manager import add_expense, read_expenses, delete_expense, update_expense, filter_expenses
from src.alerts import overspending_report, get_limits, save_limits, DEFAULT_LIMITS
from src.prediction import predict_next_month_expense
from src.insights import generate_insights
from src.ml_model import predict_category


# ═══════════════════════════════════════════════
#  THEME MANAGER  (dark / light)
# ═══════════════════════════════════════════════

class Theme:
    _dark = True

    # ── dark palette ──
    DARK = dict(
        BG_DEEP     = "#060B18",
        BG_SURFACE  = "#0D1526",
        BG_ELEVATED = "#131F35",
        BG_HOVER    = "#1A2845",
        TEXT_PRIMARY   = "#F0F4FF",
        TEXT_SECONDARY = "#8899BB",
        TEXT_MUTED     = "#445577",
        BORDER_DIM  = "#1A2845",
    )

    # ── light palette ──
    LIGHT = dict(
        BG_DEEP     = "#F0F4FF",
        BG_SURFACE  = "#FFFFFF",
        BG_ELEVATED = "#E8EEF8",
        BG_HOVER    = "#D6E0F5",
        TEXT_PRIMARY   = "#0D1526",
        TEXT_SECONDARY = "#445577",
        TEXT_MUTED     = "#8899BB",
        BORDER_DIM  = "#C8D4EC",
    )

    # accents stay the same in both modes
    ACCENT_BLUE   = "#3B82F6"
    ACCENT_CYAN   = "#06B6D4"
    ACCENT_GREEN  = "#10B981"
    ACCENT_AMBER  = "#F59E0B"
    ACCENT_RED    = "#EF4444"
    ACCENT_PURPLE = "#8B5CF6"

    FONT_DISPLAY = "Segoe UI"
    FONT_MONO    = "Consolas"

    CATEGORIES = ["Food", "Transport", "Rent", "Shopping", "Entertainment", "Others"]

    @classmethod
    def toggle(cls):
        cls._dark = not cls._dark

    @classmethod
    def is_dark(cls):
        return cls._dark

    @classmethod
    def p(cls):
        """Return current palette dict."""
        return cls.DARK if cls._dark else cls.LIGHT

    @classmethod
    def v(cls, key):
        """Get a color value by key from the current palette."""
        return cls.p()[key]


# Shortcut aliases used throughout
def _v(key):  return Theme.v(key)
FONT_DISPLAY  = Theme.FONT_DISPLAY
FONT_MONO     = Theme.FONT_MONO
CATEGORIES    = Theme.CATEGORIES

CATEGORY_COLORS = {
    "Food":          (Theme.ACCENT_AMBER,  "#78350F"),
    "Transport":     (Theme.ACCENT_BLUE,   "#1E3A5F"),
    "Rent":          (Theme.ACCENT_CYAN,   "#164E63"),
    "Shopping":      (Theme.ACCENT_PURPLE, "#4C1D95"),
    "Entertainment": (Theme.ACCENT_GREEN,  "#064E3B"),
    "Others":        ("#8899BB",           "#1F2937"),
}


# ═══════════════════════════════════════════════
#  NAV BUTTON
# ═══════════════════════════════════════════════

class NavButton(QPushButton):
    def __init__(self, icon_char, label, parent=None):
        super().__init__(parent)
        self._active = False
        self.setText(f"  {icon_char}   {label}")
        self.setFont(QFont(FONT_DISPLAY, 13))
        self.setFixedHeight(52)
        self.setCursor(Qt.PointingHandCursor)
        self.setCheckable(True)
        self._refresh_style()

    def _refresh_style(self):
        if self._active:
            self.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                        stop:0 {Theme.ACCENT_BLUE}, stop:1 #1D4ED8);
                    color: white;
                    border: none; border-radius: 12px;
                    padding: 0 16px; font-weight: bold;
                    font-size: 13px; text-align: left;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    color: {_v('TEXT_SECONDARY')};
                    border: none; border-radius: 12px;
                    padding: 0 16px; font-size: 13px; text-align: left;
                }}
                QPushButton:hover {{
                    background: {_v('BG_HOVER')};
                    color: {_v('TEXT_PRIMARY')};
                }}
            """)

    def set_active(self, val):
        self._active = val
        self._refresh_style()

    def apply_theme(self):
        self._refresh_style()


# ═══════════════════════════════════════════════
#  STAT CARD
# ═══════════════════════════════════════════════

class StatCard(QFrame):
    def __init__(self, icon, label, value, accent, parent=None):
        super().__init__(parent)
        self.accent = QColor(accent)
        self.setMinimumHeight(140)
        self._apply_style()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(8)

        icon_label = QLabel(icon)
        icon_label.setFont(QFont(FONT_DISPLAY, 24))
        icon_label.setStyleSheet(f"color:{accent}; background:transparent; border:none;")

        self.val_label = QLabel(value)
        self.val_label.setFont(QFont(FONT_DISPLAY, 26, QFont.Bold))
        self.val_label.setStyleSheet(f"color:{_v('TEXT_PRIMARY')}; background:transparent; border:none;")

        lbl = QLabel(label)
        lbl.setFont(QFont(FONT_DISPLAY, 11))
        lbl.setStyleSheet(f"color:{_v('TEXT_SECONDARY')}; background:transparent; border:none;")
        lbl.setWordWrap(True)

        layout.addWidget(icon_label)
        layout.addWidget(self.val_label)
        layout.addWidget(lbl)
        layout.addStretch()

    def _apply_style(self):
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {_v('BG_ELEVATED')};
                border: 1px solid {_v('BORDER_DIM')};
                border-radius: 20px;
            }}
        """)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        pen = QPen(self.accent, 3)
        painter.setPen(pen)
        painter.drawLine(24, 0, self.width() - 24, 0)
        painter.end()


# ═══════════════════════════════════════════════
#  GLOW LINE EDIT
# ═══════════════════════════════════════════════

class GlowLineEdit(QLineEdit):
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setMinimumHeight(46)
        self.setFont(QFont(FONT_DISPLAY, 13))
        self.apply_theme()

    def apply_theme(self):
        self.setStyleSheet(f"""
            QLineEdit {{
                background-color: {_v('BG_DEEP')};
                color: {_v('TEXT_PRIMARY')};
                border: 1.5px solid {_v('BORDER_DIM')};
                border-radius: 12px;
                padding: 0 16px; font-size: 13px;
            }}
            QLineEdit:focus {{ border: 1.5px solid {Theme.ACCENT_BLUE}; }}
        """)


# ═══════════════════════════════════════════════
#  CATEGORY COMBO BOX
# ═══════════════════════════════════════════════

class CategoryCombo(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFont(QFont(FONT_DISPLAY, 13))
        self.setMinimumHeight(46)
        self.setCursor(Qt.PointingHandCursor)
        self.apply_theme()

    def apply_theme(self):
        self.setStyleSheet(f"""
            QComboBox {{
                background-color: {_v('BG_DEEP')};
                color: {_v('TEXT_PRIMARY')};
                border: 1.5px solid {_v('BORDER_DIM')};
                border-radius: 12px;
                padding: 0 16px; font-size: 13px;
            }}
            QComboBox:focus {{ border: 1.5px solid {Theme.ACCENT_BLUE}; }}
            QComboBox::drop-down {{ border: none; width: 30px; }}
            QComboBox QAbstractItemView {{
                background: {_v('BG_SURFACE')};
                color: {_v('TEXT_PRIMARY')};
                selection-background-color: {_v('BG_HOVER')};
                border: 1px solid {_v('BORDER_DIM')};
                border-radius: 8px;
            }}
        """)


# ═══════════════════════════════════════════════
#  PRIMARY BUTTON
# ═══════════════════════════════════════════════

class PrimaryButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setMinimumHeight(46)
        self.setFont(QFont(FONT_DISPLAY, 13, QFont.Bold))
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 {Theme.ACCENT_BLUE}, stop:1 {Theme.ACCENT_CYAN});
                color: white; border: none; border-radius: 12px;
                padding: 0 24px; font-weight: bold; font-size: 13px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #2563EB, stop:1 #0891B2);
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #1D4ED8, stop:1 #0E7490);
            }}
        """)


# ═══════════════════════════════════════════════
#  ICON BUTTON  (edit / delete)
# ═══════════════════════════════════════════════

class IconButton(QPushButton):
    def __init__(self, text, color, parent=None):
        super().__init__(text, parent)
        self._color = color
        self.setFixedSize(34, 34)
        self.setCursor(Qt.PointingHandCursor)
        self.setFont(QFont(FONT_DISPLAY, 13))
        self._apply()

    def _apply(self):
        self.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {self._color};
                border: 1px solid {self._color}44;
                border-radius: 8px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background: {self._color}22;
                border-color: {self._color};
            }}
            QPushButton:pressed {{ background: {self._color}44; }}
        """)


# ═══════════════════════════════════════════════
#  DARK / LIGHT TOGGLE BUTTON
# ═══════════════════════════════════════════════

class ThemeToggle(QPushButton):
    def __init__(self, on_toggle, parent=None):
        super().__init__(parent)
        self._on_toggle = on_toggle
        self.setFixedSize(80, 34)
        self.setCursor(Qt.PointingHandCursor)
        self.clicked.connect(self._clicked)
        self._refresh()

    def _clicked(self):
        Theme.toggle()
        self._on_toggle()
        self._refresh()

    def _refresh(self):
        if Theme.is_dark():
            self.setText("☀  Light")
            self.setStyleSheet(f"""
                QPushButton {{
                    background: {Theme.DARK['BG_ELEVATED']};
                    color: {Theme.ACCENT_AMBER};
                    border: 1px solid {Theme.DARK['BORDER_DIM']};
                    border-radius: 10px; font-size: 11px;
                    font-family: {FONT_DISPLAY}; font-weight: bold;
                }}
                QPushButton:hover {{ border-color: {Theme.ACCENT_AMBER}; }}
            """)
        else:
            self.setText("🌙  Dark")
            self.setStyleSheet(f"""
                QPushButton {{
                    background: {Theme.LIGHT['BG_ELEVATED']};
                    color: {Theme.ACCENT_BLUE};
                    border: 1px solid {Theme.LIGHT['BORDER_DIM']};
                    border-radius: 10px; font-size: 11px;
                    font-family: {FONT_DISPLAY}; font-weight: bold;
                }}
                QPushButton:hover {{ border-color: {Theme.ACCENT_BLUE}; }}
            """)


# ═══════════════════════════════════════════════
#  TOAST
# ═══════════════════════════════════════════════

class Toast(QFrame):
    def __init__(self, message, success=True, parent=None):
        super().__init__(parent)
        color = Theme.ACCENT_GREEN if success else Theme.ACCENT_RED
        self.setFixedHeight(56)
        self.setMinimumWidth(320)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {_v('BG_ELEVATED')};
                border: 1.5px solid {color};
                border-radius: 14px;
            }}
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 0, 18, 0)
        layout.setSpacing(12)
        dot = QLabel("✓" if success else "✗")
        dot.setStyleSheet(f"color:{color};font-size:18px;font-weight:bold;border:none;background:transparent;")
        msg = QLabel(message)
        msg.setFont(QFont(FONT_DISPLAY, 12))
        msg.setStyleSheet(f"color:{_v('TEXT_PRIMARY')};border:none;background:transparent;")
        layout.addWidget(dot)
        layout.addWidget(msg)
        layout.addStretch()

    def show_in(self, parent_widget):
        self.setParent(parent_widget)
        self.resize(380, 56)
        start_x = parent_widget.width() // 2 - 190
        self.move(start_x, -60)
        self.show(); self.raise_()
        anim = QPropertyAnimation(self, b"pos")
        anim.setDuration(350)
        anim.setStartValue(QPoint(start_x, -60))
        anim.setEndValue(QPoint(start_x, 20))
        anim.setEasingCurve(QEasingCurve.OutBack)
        anim.start()
        self._anim = anim
        QTimer.singleShot(2800, lambda: self._slide_out(start_x))

    def _slide_out(self, x):
        anim = QPropertyAnimation(self, b"pos")
        anim.setDuration(300)
        anim.setStartValue(QPoint(x, 20))
        anim.setEndValue(QPoint(x, -80))
        anim.setEasingCurve(QEasingCurve.InBack)
        anim.finished.connect(self.deleteLater)
        anim.start()
        self._anim2 = anim


# ═══════════════════════════════════════════════
#  EXPENSE TABLE  (with row-level action buttons)
# ═══════════════════════════════════════════════

class ExpenseTable(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setShowGrid(False)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setHighlightSections(False)
        self.setFocusPolicy(Qt.NoFocus)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setDefaultSectionSize(52)
        self.apply_theme()

    def apply_theme(self):
        self.setStyleSheet(f"""
            QTableWidget {{
                background-color: {_v('BG_SURFACE')};
                alternate-background-color: {_v('BG_ELEVATED')};
                border: none; border-radius: 16px;
                color: {_v('TEXT_PRIMARY')};
                font-size: 13px; gridline-color: transparent;
                selection-background-color: {_v('BG_HOVER')};
            }}
            QHeaderView::section {{
                background-color: {_v('BG_DEEP')};
                color: {_v('TEXT_SECONDARY')};
                padding: 14px 16px; border: none;
                font-size: 12px; font-weight: bold; letter-spacing: 1px;
            }}
            QTableWidget::item {{ padding: 12px 16px; border: none; }}
            QTableWidget::item:selected {{
                background-color: {_v('BG_HOVER')};
                color: {_v('TEXT_PRIMARY')};
            }}
            QScrollBar:vertical {{
                background: {_v('BG_DEEP')}; width: 6px; border-radius: 3px;
            }}
            QScrollBar::handle:vertical {{
                background: {_v('BORDER_DIM')}; border-radius: 3px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height:0; }}
        """)


# ═══════════════════════════════════════════════
#  INSIGHT PANEL
# ═══════════════════════════════════════════════

class InsightPanel(QFrame):
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.apply_theme()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(10)
        header = QHBoxLayout()
        icon = QLabel("🧠")
        icon.setFont(QFont(FONT_DISPLAY, 18))
        icon.setStyleSheet("border:none; background:transparent;")
        title = QLabel("Smart Insights")
        title.setFont(QFont(FONT_DISPLAY, 15, QFont.Bold))
        title.setStyleSheet(f"color:{Theme.ACCENT_BLUE}; border:none; background:transparent;")
        header.addWidget(icon); header.addWidget(title); header.addStretch()
        body = QLabel(text)
        body.setFont(QFont(FONT_DISPLAY, 12))
        body.setStyleSheet(f"color:{_v('TEXT_SECONDARY')}; border:none; background:transparent;")
        body.setWordWrap(True)
        layout.addLayout(header)
        layout.addWidget(body)

    def apply_theme(self):
        self.setStyleSheet(f"""
            QFrame {{
                background: {_v('BG_ELEVATED')};
                border: 1px solid {_v('BORDER_DIM')};
                border-left: 3px solid {Theme.ACCENT_BLUE};
                border-radius: 16px;
            }}
        """)


# ═══════════════════════════════════════════════
#  FADE PAGE
# ═══════════════════════════════════════════════

class FadePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

    def animate_in(self):
        from PyQt5.QtWidgets import QGraphicsOpacityEffect
        effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(effect)
        anim = QPropertyAnimation(effect, b"opacity")
        anim.setDuration(400)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.start()
        self._fade_anim = anim


# ═══════════════════════════════════════════════
#  ADD / EDIT EXPENSE DIALOG
# ═══════════════════════════════════════════════

class ExpenseDialog(QDialog):
    """Shared dialog for both adding and editing an expense."""

    def __init__(self, on_success, parent=None, expense=None):
        super().__init__(parent)
        self.on_success = on_success
        self.expense = expense  # None → add mode; dict → edit mode
        is_edit = expense is not None

        self.setWindowTitle("Edit Expense" if is_edit else "Add Expense")
        self.setFixedSize(480, 370 if not is_edit else 440)
        self.setModal(True)
        self._apply_theme()

        outer = QVBoxLayout(self)
        outer.setContentsMargins(40, 36, 40, 36)
        outer.setSpacing(0)

        # Title
        title = QLabel("Edit Expense" if is_edit else "New Expense")
        title.setFont(QFont(FONT_DISPLAY, 20, QFont.Bold))
        title.setStyleSheet(f"color:{_v('TEXT_PRIMARY')};font-size:20px;background:transparent;")
        sub = QLabel("Update the details below" if is_edit else "Enter details — category will be auto-detected")
        sub.setFont(QFont(FONT_DISPLAY, 11))
        sub.setStyleSheet(f"color:{_v('TEXT_MUTED')};background:transparent;")
        outer.addWidget(title)
        outer.addSpacing(4)
        outer.addWidget(sub)
        outer.addSpacing(28)

        # Amount
        amt_label = QLabel("AMOUNT  (₹)")
        amt_label.setFont(QFont(FONT_DISPLAY, 10, QFont.Bold))
        amt_label.setStyleSheet(f"color:{_v('TEXT_SECONDARY')};background:transparent;")
        self.amount = GlowLineEdit("0.00")
        if is_edit:
            self.amount.setText(str(expense["amount"]))
        outer.addWidget(amt_label)
        outer.addSpacing(6)
        outer.addWidget(self.amount)
        outer.addSpacing(18)

        # Category — only shown in EDIT mode; add mode is fully auto-detected
        self.cat_combo = None
        if is_edit:
            cat_label = QLabel("CATEGORY")
            cat_label.setFont(QFont(FONT_DISPLAY, 10, QFont.Bold))
            cat_label.setStyleSheet(f"color:{_v('TEXT_SECONDARY')};background:transparent;")
            self.cat_combo = CategoryCombo()
            self.cat_combo.addItems(CATEGORIES)
            if expense["category"] in CATEGORIES:
                self.cat_combo.setCurrentText(expense["category"])
            outer.addWidget(cat_label)
            outer.addSpacing(6)
            outer.addWidget(self.cat_combo)
            outer.addSpacing(18)

        # Description
        desc_label = QLabel("DESCRIPTION")
        desc_label.setFont(QFont(FONT_DISPLAY, 10, QFont.Bold))
        desc_label.setStyleSheet(f"color:{_v('TEXT_SECONDARY')};background:transparent;")
        self.desc = GlowLineEdit("e.g. Swiggy dinner, Netflix subscription…")
        if is_edit:
            self.desc.setText(expense["description"])
        outer.addWidget(desc_label)
        outer.addSpacing(6)
        outer.addWidget(self.desc)
        outer.addSpacing(22)

        # Status line
        self.status = QLabel("" if is_edit else "Category auto-detected on save")
        self.status.setFont(QFont(FONT_DISPLAY, 11))
        self.status.setStyleSheet(f"color:{_v('TEXT_MUTED')};background:transparent;")

        # Buttons
        btn_row = QHBoxLayout()
        btn_cancel = QPushButton("Cancel")
        btn_cancel.setFixedHeight(46)
        btn_cancel.setCursor(Qt.PointingHandCursor)
        btn_cancel.setFont(QFont(FONT_DISPLAY, 13))
        btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background:{_v('BG_HOVER')};color:{_v('TEXT_SECONDARY')};
                border:none;border-radius:12px;padding:0 24px;
            }}
            QPushButton:hover {{ background:{_v('BG_ELEVATED')};color:{_v('TEXT_PRIMARY')}; }}
        """)
        self.btn_save = PrimaryButton("Save Changes" if is_edit else "Save Expense")
        self.btn_save.setFixedHeight(46)
        btn_row.addWidget(btn_cancel)
        btn_row.addSpacing(12)
        btn_row.addWidget(self.btn_save)

        outer.addWidget(self.status)
        outer.addSpacing(16)
        outer.addLayout(btn_row)

        btn_cancel.clicked.connect(self.reject)
        self.btn_save.clicked.connect(self._save)

    def _apply_theme(self):
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {_v('BG_SURFACE')};
                border-radius: 24px;
            }}
            QLabel {{ color:{_v('TEXT_SECONDARY')}; font-size:12px; background:transparent; }}
        """)

    def _save(self):
        try:
            amt = float(self.amount.text())
            description = self.desc.text().strip()
            if not description:
                raise ValueError("Description cannot be empty.")

            if self.expense is None:
                # ADD mode — fully auto-detect, no combo override
                category = predict_category(description)
                add_expense(amt, category, description)
                self.on_success(category, "add")
            else:
                # EDIT mode — user picks category from combo
                category = self.cat_combo.currentText()
                update_expense(self.expense["id"], amt, category, description)
                self.on_success(category, "edit")
            self.accept()
        except Exception as e:
            self.status.setText(f"⚠  {e}")
            self.status.setStyleSheet(f"color:{Theme.ACCENT_RED};background:transparent;")


# ═══════════════════════════════════════════════
#  DELETE CONFIRMATION DIALOG
# ═══════════════════════════════════════════════

class DeleteDialog(QDialog):
    def __init__(self, description, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Delete Expense")
        self.setFixedSize(400, 220)
        self.setModal(True)
        self.setStyleSheet(f"QDialog{{background:{_v('BG_SURFACE')};}} QLabel{{background:transparent;}}")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(36, 32, 36, 32)
        outer.setSpacing(12)

        icon = QLabel("🗑")
        icon.setFont(QFont(FONT_DISPLAY, 28))
        icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet("background:transparent;")

        title = QLabel("Delete this expense?")
        title.setFont(QFont(FONT_DISPLAY, 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"color:{_v('TEXT_PRIMARY')};background:transparent;")

        desc = QLabel(f'"{description}"')
        desc.setFont(QFont(FONT_DISPLAY, 12))
        desc.setAlignment(Qt.AlignCenter)
        desc.setStyleSheet(f"color:{_v('TEXT_MUTED')};background:transparent;")
        desc.setWordWrap(True)

        btn_row = QHBoxLayout()
        btn_cancel = QPushButton("Cancel")
        btn_cancel.setFixedHeight(42)
        btn_cancel.setCursor(Qt.PointingHandCursor)
        btn_cancel.setFont(QFont(FONT_DISPLAY, 13))
        btn_cancel.setStyleSheet(f"""
            QPushButton{{background:{_v('BG_HOVER')};color:{_v('TEXT_SECONDARY')};
                border:none;border-radius:10px;padding:0 20px;}}
            QPushButton:hover{{background:{_v('BG_ELEVATED')};color:{_v('TEXT_PRIMARY')};}}
        """)
        btn_delete = QPushButton("Delete")
        btn_delete.setFixedHeight(42)
        btn_delete.setCursor(Qt.PointingHandCursor)
        btn_delete.setFont(QFont(FONT_DISPLAY, 13, QFont.Bold))
        btn_delete.setStyleSheet(f"""
            QPushButton{{background:{Theme.ACCENT_RED};color:white;border:none;
                border-radius:10px;padding:0 20px;}}
            QPushButton:hover{{background:#DC2626;}}
        """)
        btn_row.addWidget(btn_cancel)
        btn_row.addSpacing(10)
        btn_row.addWidget(btn_delete)

        outer.addWidget(icon)
        outer.addWidget(title)
        outer.addWidget(desc)
        outer.addSpacing(8)
        outer.addLayout(btn_row)

        btn_cancel.clicked.connect(self.reject)
        btn_delete.clicked.connect(self.accept)


# ═══════════════════════════════════════════════
#  MAIN WINDOW
# ═══════════════════════════════════════════════

class FinanceApp(QMainWindow):

    def __init__(self):
        super().__init__()
        init_db()
        self.setWindowTitle("FinancePro · Smart Finance Dashboard")
        self.resize(1380, 820)
        self._build_ui()

    # ──────────────────────────────────────────────
    def _build_ui(self):
        self._apply_window_style()

        root = QHBoxLayout()
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ─── SIDEBAR ──────────────────────────────
        self._nav_buttons = []
        self._sidebar_widget = QWidget()
        self._sidebar_widget.setFixedWidth(260)
        self._apply_sidebar_style()

        sidebar = QVBoxLayout(self._sidebar_widget)
        sidebar.setContentsMargins(16, 32, 16, 32)
        sidebar.setSpacing(4)

        # Logo
        logo_row = QHBoxLayout()
        logo_icon = QLabel("💳")
        logo_icon.setFont(QFont(FONT_DISPLAY, 22))
        logo_icon.setStyleSheet("background:transparent;color:white;")
        logo_text = QLabel("FinancePro")
        logo_text.setFont(QFont(FONT_DISPLAY, 18, QFont.Bold))
        logo_text.setStyleSheet(f"color:{_v('TEXT_PRIMARY')};background:transparent;")
        logo_row.addWidget(logo_icon); logo_row.addWidget(logo_text); logo_row.addStretch()
        sidebar.addLayout(logo_row)
        sidebar.addSpacing(8)

        chip = QLabel("v2.0  BETA")
        chip.setFont(QFont(FONT_MONO, 9))
        chip.setStyleSheet(f"color:{Theme.ACCENT_BLUE};background:#1E3A5F;border-radius:6px;padding:3px 10px;")
        chip.setFixedWidth(80)
        sidebar.addWidget(chip)
        sidebar.addSpacing(32)

        nav_label = QLabel("NAVIGATION")
        nav_label.setFont(QFont(FONT_DISPLAY, 9, QFont.Bold))
        nav_label.setStyleSheet(f"color:{_v('TEXT_MUTED')};background:transparent;letter-spacing:2px;")
        sidebar.addWidget(nav_label)
        sidebar.addSpacing(8)

        nav_items = [
            ("📊", "Dashboard",    self.show_dashboard),
            ("➕", "Add Expense",  self.add_expense_ui),
            ("📋", "Transactions", self.view_expenses),
            ("⚠",  "Alerts",      self.show_alerts),
            ("🔮", "AI Predict",   self.show_prediction),
        ]
        for icon, label, slot in nav_items:
            btn = NavButton(icon, label)
            btn.clicked.connect(lambda checked, s=slot, b=btn: self._nav_click(b, s))
            sidebar.addWidget(btn)
            self._nav_buttons.append(btn)

        sidebar.addStretch()

        # Theme toggle
        self._theme_toggle = ThemeToggle(self._apply_theme_all)
        sidebar.addWidget(self._theme_toggle)
        sidebar.addSpacing(12)

        # User card
        self._user_card = QFrame()
        self._apply_user_card_style()
        user_layout = QHBoxLayout(self._user_card)
        user_layout.setContentsMargins(12, 12, 12, 12)
        avatar = QLabel("FP")
        avatar.setFixedSize(38, 38)
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setFont(QFont(FONT_DISPLAY, 12, QFont.Bold))
        avatar.setStyleSheet(f"""
            color:white;
            background:qlineargradient(x1:0,y1:0,x2:1,y2:1,
                stop:0 {Theme.ACCENT_BLUE}, stop:1 {Theme.ACCENT_CYAN});
            border-radius:19px;
        """)
        name_col = QVBoxLayout(); name_col.setSpacing(1)
        user_name = QLabel("Finance Pro")
        user_name.setFont(QFont(FONT_DISPLAY, 11, QFont.Bold))
        user_name.setStyleSheet(f"color:{_v('TEXT_PRIMARY')};background:transparent;")
        user_sub = QLabel("Personal Account")
        user_sub.setFont(QFont(FONT_DISPLAY, 9))
        user_sub.setStyleSheet(f"color:{_v('TEXT_MUTED')};background:transparent;")
        name_col.addWidget(user_name); name_col.addWidget(user_sub)
        user_layout.addWidget(avatar); user_layout.addLayout(name_col)
        sidebar.addWidget(self._user_card)

        # ─── STACK ────────────────────────────────
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background:transparent;")
        root.addWidget(self._sidebar_widget)
        root.addWidget(self.stack)

        container = QWidget()
        container.setStyleSheet(f"background-color:{_v('BG_DEEP')};")
        container.setLayout(root)
        self._container = container
        self.setCentralWidget(container)

        # ─── PAGES ────────────────────────────────
        self._page_dashboard    = self._build_dashboard_page()
        self._page_transactions = self._build_transactions_page()
        self._page_alerts       = self._build_alerts_page()
        self._page_prediction   = self._build_prediction_page()
        for p in [self._page_dashboard, self._page_transactions,
                  self._page_alerts, self._page_prediction]:
            self.stack.addWidget(p)

        self._nav_click(self._nav_buttons[0], self.show_dashboard)

    # ──────────────────────────────────────────────
    #  STYLE HELPERS
    # ──────────────────────────────────────────────

    def _apply_window_style(self):
        self.setStyleSheet(f"""
            QMainWindow {{ background-color:{_v('BG_DEEP')}; }}
            QWidget {{ font-family:{FONT_DISPLAY}; color:{_v('TEXT_PRIMARY')}; }}
            QScrollArea {{ border:none; background:transparent; }}
            QScrollBar:vertical {{
                background:{_v('BG_DEEP')}; width:6px; border-radius:3px;
            }}
            QScrollBar::handle:vertical {{
                background:{_v('BORDER_DIM')}; border-radius:3px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height:0; }}
        """)

    def _apply_sidebar_style(self):
        self._sidebar_widget.setStyleSheet(
            f"background-color:{_v('BG_SURFACE')}; border-right:1px solid {_v('BORDER_DIM')};"
        )

    def _apply_user_card_style(self):
        self._user_card.setStyleSheet(f"""
            QFrame {{
                background-color:{_v('BG_ELEVATED')};
                border:1px solid {_v('BORDER_DIM')};
                border-radius:14px;
            }}
        """)

    def _apply_theme_all(self):
        """Re-apply theme everywhere after toggle."""
        self._apply_window_style()
        self._apply_sidebar_style()
        self._apply_user_card_style()
        self._container.setStyleSheet(f"background-color:{_v('BG_DEEP')};")
        for btn in self._nav_buttons:
            btn.apply_theme()
        self._rebuild_all_pages()

    def _rebuild_all_pages(self):
        """Rebuild all pages to pick up new theme colors."""
        def _swap(attr, builder):
            old = getattr(self, attr)
            idx = self.stack.indexOf(old)
            self.stack.removeWidget(old)
            new = builder()
            setattr(self, attr, new)
            self.stack.insertWidget(idx, new)

        _swap("_page_dashboard",    self._build_dashboard_page)
        _swap("_page_transactions", self._build_transactions_page)
        _swap("_page_alerts",       self._build_alerts_page)
        _swap("_page_prediction",   self._build_prediction_page)
        self.stack.setCurrentWidget(self._page_dashboard)

    # ──────────────────────────────────────────────
    def _nav_click(self, active_btn, slot):
        for btn in self._nav_buttons:
            btn.set_active(False)
        active_btn.set_active(True)
        slot()

    def _page_header(self, title, subtitle=""):
        w = QWidget(); w.setStyleSheet("background:transparent;")
        vb = QVBoxLayout(w); vb.setContentsMargins(0,0,0,0); vb.setSpacing(4)
        t = QLabel(title)
        t.setFont(QFont(FONT_DISPLAY, 26, QFont.Bold))
        t.setStyleSheet(f"color:{_v('TEXT_PRIMARY')};background:transparent;")
        vb.addWidget(t)
        if subtitle:
            s = QLabel(subtitle)
            s.setFont(QFont(FONT_DISPLAY, 13))
            s.setStyleSheet(f"color:{_v('TEXT_MUTED')};background:transparent;")
            vb.addWidget(s)
        return w

    def _ghost_btn(self, label):
        btn = QPushButton(label)
        btn.setFixedHeight(40); btn.setCursor(Qt.PointingHandCursor)
        btn.setFont(QFont(FONT_DISPLAY, 12))
        btn.setStyleSheet(f"""
            QPushButton {{
                background:{_v('BG_ELEVATED')};color:{_v('TEXT_SECONDARY')};
                border:1px solid {_v('BORDER_DIM')};border-radius:10px;padding:0 18px;
            }}
            QPushButton:hover {{ color:{_v('TEXT_PRIMARY')};border-color:{Theme.ACCENT_BLUE}; }}
        """)
        return btn

    # ═══════════════════════════════════════════════
    #  DASHBOARD PAGE
    # ═══════════════════════════════════════════════

    def _build_dashboard_page(self):
        page = FadePage(); page.setStyleSheet("background:transparent;")
        scroll = QScrollArea(); scroll.setWidget(page)
        scroll.setWidgetResizable(True); scroll.setStyleSheet("background:transparent;border:none;")
        layout = QVBoxLayout(page); layout.setContentsMargins(40,36,40,36); layout.setSpacing(0)

        hdr = QHBoxLayout()
        hdr.addWidget(self._page_header("Dashboard", "Here's your financial overview"))
        hdr.addStretch()
        refresh = self._ghost_btn("⟳  Refresh")
        refresh.clicked.connect(self._refresh_dashboard)
        hdr.addWidget(refresh)
        layout.addLayout(hdr); layout.addSpacing(32)

        data = read_expenses()
        total = sum(float(d["amount"]) for d in data) if data else 0.0
        avg   = total / len(data) if data else 0.0
        count = len(data)
        top_cat = "N/A"
        if data:
            from collections import defaultdict
            dct = defaultdict(float)
            for d in data: dct[d["category"]] += float(d["amount"])
            top_cat = max(dct, key=dct.get)

        cards_row = QHBoxLayout(); cards_row.setSpacing(20)
        for args in [
            ("💰","Total Expenses",   f"₹ {total:,.2f}", Theme.ACCENT_GREEN),
            ("📈","Average Expense",  f"₹ {avg:,.2f}",   Theme.ACCENT_BLUE),
            ("🔢","Transactions",     str(count),          Theme.ACCENT_CYAN),
            ("🏆","Top Category",     top_cat,             Theme.ACCENT_AMBER),
        ]:
            cards_row.addWidget(StatCard(*args))
        layout.addLayout(cards_row); layout.addSpacing(32)

        layout.addWidget(InsightPanel(generate_insights())); layout.addSpacing(32)

        recent_label = QLabel("Recent Transactions")
        recent_label.setFont(QFont(FONT_DISPLAY, 16, QFont.Bold))
        recent_label.setStyleSheet(f"color:{_v('TEXT_PRIMARY')};background:transparent;")
        layout.addWidget(recent_label); layout.addSpacing(12)
        layout.addWidget(self._make_expense_table(limit=5, show_actions=False))
        layout.addStretch()
        return scroll

    def _refresh_dashboard(self):
        idx = self.stack.indexOf(self._page_dashboard)
        self.stack.removeWidget(self._page_dashboard)
        self._page_dashboard = self._build_dashboard_page()
        self.stack.insertWidget(idx, self._page_dashboard)
        self.stack.setCurrentWidget(self._page_dashboard)

    # ═══════════════════════════════════════════════
    #  TRANSACTIONS PAGE  (with search, filter, edit, delete)
    # ═══════════════════════════════════════════════

    def _build_transactions_page(self):
        page = FadePage(); page.setStyleSheet("background:transparent;")
        scroll = QScrollArea(); scroll.setWidget(page)
        scroll.setWidgetResizable(True); scroll.setStyleSheet("background:transparent;border:none;")
        layout = QVBoxLayout(page); layout.setContentsMargins(40,36,40,36); layout.setSpacing(0)

        # ── header row ──
        hdr_row = QHBoxLayout()
        hdr_row.addWidget(self._page_header("Transactions", "All expense records"))
        hdr_row.addStretch()
        layout.addLayout(hdr_row); layout.addSpacing(20)

        # ── search + filter bar ──
        bar = QHBoxLayout(); bar.setSpacing(12)

        self._search_box = GlowLineEdit("🔍  Search by description…")
        self._search_box.setFixedHeight(44)

        self._cat_filter = CategoryCombo()
        self._cat_filter.addItem("All Categories")
        self._cat_filter.addItems(CATEGORIES)
        self._cat_filter.setFixedWidth(200)
        self._cat_filter.setFixedHeight(44)

        apply_btn = self._ghost_btn("Apply Filter")
        apply_btn.clicked.connect(self._apply_filter)

        clear_btn = self._ghost_btn("Clear")
        clear_btn.clicked.connect(self._clear_filter)

        bar.addWidget(self._search_box)
        bar.addWidget(self._cat_filter)
        bar.addWidget(apply_btn)
        bar.addWidget(clear_btn)
        layout.addLayout(bar); layout.addSpacing(20)

        # ── table ──
        self._tx_table_widget = self._make_expense_table(show_actions=True)
        layout.addWidget(self._tx_table_widget)
        layout.addStretch()
        return scroll

    def _apply_filter(self):
        keyword = self._search_box.text().strip()
        cat_sel = self._cat_filter.currentText()
        category = None if cat_sel == "All Categories" else cat_sel
        data = filter_expenses(keyword=keyword, category=category)
        self._populate_table(self._tx_table_widget, data, show_actions=True)

    def _clear_filter(self):
        self._search_box.clear()
        self._cat_filter.setCurrentIndex(0)
        data = read_expenses()
        self._populate_table(self._tx_table_widget, data, show_actions=True)

    # ═══════════════════════════════════════════════
    #  ALERTS PAGE
    # ═══════════════════════════════════════════════

    def _build_alerts_page(self):
        page = FadePage(); page.setStyleSheet("background:transparent;")
        scroll = QScrollArea(); scroll.setWidget(page)
        scroll.setWidgetResizable(True); scroll.setStyleSheet("background:transparent;border:none;")
        layout = QVBoxLayout(page); layout.setContentsMargins(40,36,40,36); layout.setSpacing(0)

        # ── header row ──
        hdr_row = QHBoxLayout()
        hdr_row.addWidget(self._page_header("Spending Alerts", "Set your own monthly limits per category"))
        hdr_row.addStretch()
        save_btn = PrimaryButton("💾  Save Limits")
        save_btn.setFixedHeight(42); save_btn.setFixedWidth(150)
        hdr_row.addWidget(save_btn)
        layout.addLayout(hdr_row); layout.addSpacing(28)

        # ── SET LIMITS CARD ──────────────────────────────────
        limits_card = QFrame()
        limits_card.setStyleSheet(f"""
            QFrame {{
                background:{_v('BG_ELEVATED')};
                border:1px solid {_v('BORDER_DIM')};
                border-top:3px solid {Theme.ACCENT_BLUE};
                border-radius:18px;
            }}
        """)
        lc = QVBoxLayout(limits_card); lc.setContentsMargins(28,24,28,28); lc.setSpacing(0)

        # card header
        lc_hdr = QHBoxLayout()
        lc_icon = QLabel("⚙"); lc_icon.setFont(QFont(FONT_DISPLAY,18))
        lc_icon.setStyleSheet(f"background:transparent;color:{Theme.ACCENT_BLUE};")
        lc_title = QLabel("Monthly Spending Limits")
        lc_title.setFont(QFont(FONT_DISPLAY,15,QFont.Bold))
        lc_title.setStyleSheet(f"color:{_v('TEXT_PRIMARY')};background:transparent;")
        lc_sub = QLabel("  —  edit any field and click Save")
        lc_sub.setFont(QFont(FONT_DISPLAY,11))
        lc_sub.setStyleSheet(f"color:{_v('TEXT_MUTED')};background:transparent;")
        lc_hdr.addWidget(lc_icon); lc_hdr.addSpacing(8)
        lc_hdr.addWidget(lc_title); lc_hdr.addWidget(lc_sub); lc_hdr.addStretch()
        lc.addLayout(lc_hdr); lc.addSpacing(22)

        # column headers
        col_hdr = QHBoxLayout()
        for txt, stretch in [("CATEGORY", 2), ("MONTHLY LIMIT  (₹)", 2), ("% USED THIS MONTH", 3)]:
            lbl = QLabel(txt)
            lbl.setFont(QFont(FONT_DISPLAY,9,QFont.Bold))
            lbl.setStyleSheet(f"color:{_v('TEXT_MUTED')};background:transparent;letter-spacing:1px;")
            col_hdr.addWidget(lbl, stretch)
        lc.addLayout(col_hdr); lc.addSpacing(10)

        # divider
        div = QFrame(); div.setFixedHeight(1)
        div.setStyleSheet(f"background:{_v('BORDER_DIM')};border:none;")
        lc.addWidget(div); lc.addSpacing(10)

        # fetch current limits + spending for progress bars
        current_limits = get_limits()
        report_lines   = overspending_report().splitlines()

        # pull current-month spending per category from report string
        import re
        spent_map = {}
        for line in report_lines:
            m = re.search(r'(Food|Transport|Rent|Shopping|Entertainment|Others).*?₹([\d,]+)', line)
            if m:
                spent_map[m.group(1)] = int(m.group(2).replace(",",""))

        # category icons for polish
        cat_icons = {
            "Food":"🍔","Transport":"🚗","Rent":"🏠",
            "Shopping":"🛍","Entertainment":"🎬","Others":"📦"
        }
        cat_accents = {
            "Food":     Theme.ACCENT_AMBER,
            "Transport":Theme.ACCENT_BLUE,
            "Rent":     Theme.ACCENT_CYAN,
            "Shopping": Theme.ACCENT_PURPLE,
            "Entertainment":Theme.ACCENT_GREEN,
            "Others":   Theme.ACCENT_RED,
        }

        self._limit_inputs = {}   # {category: QLineEdit}

        for cat, default_limit in current_limits.items():
            row_layout = QHBoxLayout(); row_layout.setSpacing(0)

            # ── Category label ──
            cat_widget = QWidget(); cat_widget.setStyleSheet("background:transparent;")
            cat_hl = QHBoxLayout(cat_widget); cat_hl.setContentsMargins(0,0,0,0); cat_hl.setSpacing(8)
            ic = QLabel(cat_icons.get(cat,"•"))
            ic.setFont(QFont(FONT_DISPLAY,16))
            ic.setStyleSheet("background:transparent;")
            name_lbl = QLabel(cat)
            name_lbl.setFont(QFont(FONT_DISPLAY,13,QFont.Bold))
            name_lbl.setStyleSheet(f"color:{_v('TEXT_PRIMARY')};background:transparent;")
            cat_hl.addWidget(ic); cat_hl.addWidget(name_lbl); cat_hl.addStretch()

            # ── Input field ──
            inp = QLineEdit(str(int(default_limit)))
            inp.setFont(QFont(FONT_MONO,13))
            inp.setFixedHeight(42); inp.setFixedWidth(160)
            inp.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            accent = cat_accents.get(cat, Theme.ACCENT_BLUE)
            inp.setStyleSheet(f"""
                QLineEdit {{
                    background:{_v('BG_DEEP')};
                    color:{accent};
                    border:1.5px solid {_v('BORDER_DIM')};
                    border-radius:10px;
                    padding:0 14px;
                    font-size:14px;
                    font-weight:bold;
                }}
                QLineEdit:focus {{ border-color:{accent}; }}
            """)
            self._limit_inputs[cat] = inp

            # ── Progress bar ──
            spent  = spent_map.get(cat, 0)
            pct    = min(int(spent / default_limit * 100), 100) if default_limit > 0 else 0
            over   = spent > default_limit
            bar_color = Theme.ACCENT_RED if over else accent

            prog_widget = QWidget(); prog_widget.setStyleSheet("background:transparent;")
            prog_vl = QVBoxLayout(prog_widget); prog_vl.setContentsMargins(16,0,0,0); prog_vl.setSpacing(4)

            pct_lbl = QLabel(f"₹{spent:,} / ₹{int(default_limit):,}  ({pct}%)" + ("  ⚠ OVER!" if over else ""))
            pct_lbl.setFont(QFont(FONT_DISPLAY,11))
            pct_lbl.setStyleSheet(f"color:{'#EF4444' if over else _v('TEXT_SECONDARY')};background:transparent;")

            bar_bg = QFrame(); bar_bg.setFixedHeight(6)
            bar_bg.setStyleSheet(f"background:{_v('BG_HOVER')};border-radius:3px;border:none;")

            bar_fill = QFrame(bar_bg)
            bar_fill.setFixedHeight(6)
            # width set after show; use a proportion of 260px max
            fill_w = int(pct / 100 * 260)
            bar_fill.setFixedWidth(max(fill_w, 4))
            bar_fill.setStyleSheet(f"""
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 {bar_color}, stop:1 {bar_color}99);
                border-radius:3px; border:none;
            """)

            prog_vl.addWidget(pct_lbl)
            prog_vl.addWidget(bar_bg)

            row_layout.addWidget(cat_widget, 2)
            row_layout.addWidget(inp, 0)
            row_layout.addWidget(prog_widget, 3)

            lc.addLayout(row_layout)

            # thin separator
            sep = QFrame(); sep.setFixedHeight(1)
            sep.setStyleSheet(f"background:{_v('BORDER_DIM')}33;border:none;")
            lc.addSpacing(10); lc.addWidget(sep); lc.addSpacing(10)

        layout.addWidget(limits_card); layout.addSpacing(28)

        # ── OVERSPENDING REPORT CARD ──────────────────────
        report_card = QFrame()
        report_card.setStyleSheet(f"""
            QFrame {{
                background:{_v('BG_ELEVATED')};
                border:1px solid {_v('BORDER_DIM')};
                border-left:4px solid {Theme.ACCENT_AMBER};
                border-radius:16px;
            }}
        """)
        al = QVBoxLayout(report_card); al.setContentsMargins(28,22,28,22); al.setSpacing(10)
        rpt_hdr = QHBoxLayout()
        rpt_icon = QLabel("⚠"); rpt_icon.setFont(QFont(FONT_DISPLAY,18))
        rpt_icon.setStyleSheet(f"background:transparent;color:{Theme.ACCENT_AMBER};")
        rpt_title = QLabel("Overspending Report")
        rpt_title.setFont(QFont(FONT_DISPLAY,15,QFont.Bold))
        rpt_title.setStyleSheet(f"color:{_v('TEXT_PRIMARY')};background:transparent;")
        rpt_hdr.addWidget(rpt_icon); rpt_hdr.addSpacing(8)
        rpt_hdr.addWidget(rpt_title); rpt_hdr.addStretch()
        body = QLabel(overspending_report())
        body.setFont(QFont(FONT_DISPLAY,12))
        body.setStyleSheet(f"color:{_v('TEXT_SECONDARY')};background:transparent;")
        body.setWordWrap(True)
        al.addLayout(rpt_hdr); al.addWidget(body)
        layout.addWidget(report_card); layout.addStretch()

        # wire Save button
        save_btn.clicked.connect(lambda: self._save_limits())
        return scroll

    def _save_limits(self):
        """Read all limit input fields, validate, persist, then refresh the page."""
        try:
            new_limits = {}
            for cat, inp in self._limit_inputs.items():
                val = float(inp.text().strip().replace(",",""))
                if val <= 0:
                    raise ValueError(f"{cat}: limit must be > 0")
                new_limits[cat] = val
            save_limits(new_limits)
            Toast("Spending limits saved ✓", success=True).show_in(self.centralWidget())
            # rebuild alerts page so progress bars refresh
            idx = self.stack.indexOf(self._page_alerts)
            self.stack.removeWidget(self._page_alerts)
            self._page_alerts = self._build_alerts_page()
            self.stack.insertWidget(idx, self._page_alerts)
            self.stack.setCurrentWidget(self._page_alerts)
        except ValueError as e:
            Toast(f"Invalid value — {e}", success=False).show_in(self.centralWidget())

    # ═══════════════════════════════════════════════
    #  PREDICTION PAGE
    # ═══════════════════════════════════════════════

    def _build_prediction_page(self):
        page = FadePage(); page.setStyleSheet("background:transparent;")
        scroll = QScrollArea(); scroll.setWidget(page)
        scroll.setWidgetResizable(True); scroll.setStyleSheet("background:transparent;border:none;")
        layout = QVBoxLayout(page); layout.setContentsMargins(40,36,40,36); layout.setSpacing(0)
        layout.addWidget(self._page_header("AI Prediction","Next-month expense forecast"))
        layout.addSpacing(28)

        predict_card = QFrame()
        predict_card.setStyleSheet(f"""
            QFrame {{
                background:{_v('BG_ELEVATED')};border:1px solid {_v('BORDER_DIM')};
                border-top:3px solid {Theme.ACCENT_PURPLE};border-radius:20px;
            }}
        """)
        pc = QVBoxLayout(predict_card); pc.setContentsMargins(40,36,40,36); pc.setSpacing(20)
        icon_lbl = QLabel("🔮"); icon_lbl.setFont(QFont(FONT_DISPLAY,48))
        icon_lbl.setAlignment(Qt.AlignCenter); icon_lbl.setStyleSheet("background:transparent;")
        self._predict_value = QLabel("Click predict to generate")
        self._predict_value.setFont(QFont(FONT_DISPLAY,36,QFont.Bold))
        self._predict_value.setAlignment(Qt.AlignCenter)
        self._predict_value.setStyleSheet(f"color:{_v('TEXT_PRIMARY')};background:transparent;")
        sub = QLabel("Predicted total expenses for next month")
        sub.setFont(QFont(FONT_DISPLAY,13)); sub.setAlignment(Qt.AlignCenter)
        sub.setStyleSheet(f"color:{_v('TEXT_MUTED')};background:transparent;")
        btn = PrimaryButton("Run AI Prediction"); btn.setFixedWidth(220)
        btn.clicked.connect(self._run_prediction)
        btn_row = QHBoxLayout(); btn_row.addStretch(); btn_row.addWidget(btn); btn_row.addStretch()
        pc.addWidget(icon_lbl); pc.addWidget(self._predict_value); pc.addWidget(sub)
        pc.addSpacing(8); pc.addLayout(btn_row)
        layout.addWidget(predict_card); layout.addStretch()
        return scroll

    def _run_prediction(self):
        try:
            val = predict_next_month_expense()
            self._predict_value.setText(f"₹ {val:,.2f}")
            self._predict_value.setStyleSheet(f"color:{Theme.ACCENT_GREEN};background:transparent;")
        except Exception as e:
            self._predict_value.setText(f"Error: {e}")
            self._predict_value.setStyleSheet(f"color:{Theme.ACCENT_RED};background:transparent;")

    # ═══════════════════════════════════════════════
    #  TABLE BUILDER  (with optional action buttons)
    # ═══════════════════════════════════════════════

    def _make_expense_table(self, limit=None, show_actions=False) -> ExpenseTable:
        data = read_expenses()
        if limit:
            data = data[:limit]
        table = ExpenseTable()
        self._populate_table(table, data, show_actions=show_actions)
        return table

    def _populate_table(self, table: ExpenseTable, data: list, show_actions=False):
        """Fill (or refill) an existing ExpenseTable with data rows."""
        cols = 5 if show_actions else 4
        table.setColumnCount(cols)
        headers = ["Date", "Amount", "Category", "Description"]
        if show_actions:
            headers.append("Actions")
        table.setHorizontalHeaderLabels(headers)
        table.setRowCount(len(data))

        for i, row in enumerate(data):
            expense_id = row["id"]

            date_item = QTableWidgetItem(row["date"])
            date_item.setForeground(QColor(_v("TEXT_MUTED")))

            amt_item = QTableWidgetItem(f'₹ {float(row["amount"]):,.2f}')
            amt_item.setForeground(QColor(Theme.ACCENT_GREEN))
            amt_item.setFont(QFont(FONT_MONO, 12, QFont.Bold))

            cat_item = QTableWidgetItem(row["category"])
            cat_item.setForeground(QColor(Theme.ACCENT_BLUE))

            desc_item = QTableWidgetItem(row["description"])
            desc_item.setForeground(QColor(_v("TEXT_SECONDARY")))

            for col, item in enumerate([date_item, amt_item, cat_item, desc_item]):
                table.setItem(i, col, item)

            if show_actions:
                action_widget = QWidget()
                action_widget.setStyleSheet("background:transparent;")
                action_layout = QHBoxLayout(action_widget)
                action_layout.setContentsMargins(8, 6, 8, 6)
                action_layout.setSpacing(8)

                edit_btn = IconButton("✏", Theme.ACCENT_BLUE)
                edit_btn.setToolTip("Edit expense")
                del_btn  = IconButton("🗑", Theme.ACCENT_RED)
                del_btn.setToolTip("Delete expense")

                # Capture row dict by value
                row_snapshot = dict(row)
                edit_btn.clicked.connect(lambda _, r=row_snapshot, t=table: self._on_edit(r, t))
                del_btn.clicked.connect(lambda _, eid=expense_id, edesc=row["description"], t=table:
                                         self._on_delete(eid, edesc, t))

                action_layout.addWidget(edit_btn)
                action_layout.addWidget(del_btn)
                action_layout.addStretch()
                table.setCellWidget(i, 4, action_widget)

        table.setColumnWidth(0, 120)
        table.setColumnWidth(1, 130)
        table.setColumnWidth(2, 130)
        if show_actions:
            table.setColumnWidth(4, 100)

    # ─── edit handler ──────────────────────────────────
    def _on_edit(self, expense: dict, table: ExpenseTable):
        def on_success(category, mode):
            Toast(f"Expense updated · {category}", success=True).show_in(self.centralWidget())
            data = read_expenses()
            self._populate_table(table, data, show_actions=True)
            self._refresh_dashboard()

        dlg = ExpenseDialog(on_success, self, expense=expense)
        dlg.exec_()

    # ─── delete handler ────────────────────────────────
    def _on_delete(self, expense_id: int, description: str, table: ExpenseTable):
        dlg = DeleteDialog(description, self)
        if dlg.exec_() == QDialog.Accepted:
            delete_expense(expense_id)
            Toast("Expense deleted", success=False).show_in(self.centralWidget())
            data = read_expenses()
            self._populate_table(table, data, show_actions=True)
            self._refresh_dashboard()

    # ═══════════════════════════════════════════════
    #  NAV SLOTS
    # ═══════════════════════════════════════════════

    def show_dashboard(self):
        self._animate_page(self._page_dashboard)

    def view_expenses(self):
        idx = self.stack.indexOf(self._page_transactions)
        self.stack.removeWidget(self._page_transactions)
        self._page_transactions = self._build_transactions_page()
        self.stack.insertWidget(idx, self._page_transactions)
        self._animate_page(self._page_transactions)

    def show_alerts(self):
        idx = self.stack.indexOf(self._page_alerts)
        self.stack.removeWidget(self._page_alerts)
        self._page_alerts = self._build_alerts_page()
        self.stack.insertWidget(idx, self._page_alerts)
        self._animate_page(self._page_alerts)

    def show_prediction(self):
        self._animate_page(self._page_prediction)

    def add_expense_ui(self):
        def on_success(category, mode):
            Toast(f"Expense saved · Category: {category}", success=True).show_in(self.centralWidget())

    # 🔥     AUTO ALERT SYSTEM
            from src.alerts import check_overspending
            alerts = check_overspending()
            if alerts:
                for alert in alerts:
                    Toast(alert, success=False).show_in(self.centralWidget())

            self._refresh_dashboard()

        dlg = ExpenseDialog(on_success, self)
        dlg.exec_()
        self._nav_click(self._nav_buttons[0], self.show_dashboard)

    def _animate_page(self, page):
        self.stack.setCurrentWidget(page)
        inner = page.widget() if isinstance(page, QScrollArea) else page
        if isinstance(inner, FadePage):
            inner.animate_in()


# ═══════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    palette = app.palette()
    palette.setColor(palette.Window,          QColor(Theme.DARK["BG_DEEP"]))
    palette.setColor(palette.WindowText,      QColor(Theme.DARK["TEXT_PRIMARY"]))
    palette.setColor(palette.Base,            QColor(Theme.DARK["BG_SURFACE"]))
    palette.setColor(palette.AlternateBase,   QColor(Theme.DARK["BG_ELEVATED"]))
    palette.setColor(palette.Text,            QColor(Theme.DARK["TEXT_PRIMARY"]))
    palette.setColor(palette.Button,          QColor(Theme.DARK["BG_ELEVATED"]))
    palette.setColor(palette.ButtonText,      QColor(Theme.DARK["TEXT_PRIMARY"]))
    palette.setColor(palette.Highlight,       QColor(Theme.ACCENT_BLUE))
    palette.setColor(palette.HighlightedText, QColor("#FFFFFF"))
    app.setPalette(palette)

    window = FinanceApp()
    window.show()
    sys.exit(app.exec_())