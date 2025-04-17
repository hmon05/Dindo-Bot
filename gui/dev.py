from PyQt5.QtWidgets import (QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox,
                             QSpinBox, QMenu, QAction, QTableView)
from PyQt5.QtGui import QPixmap, QImage, QCursor
from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex


from lib import tools, data, convert
from .custom import CustomComboBox, ButtonBox
from .dialog import CopyTextDialog
from threading import Thread

class DevToolsWidget(QWidget):

	def __init__(self, parent):
		super().__init__()
		self.layout = QVBoxLayout(self)
		self.layout.setContentsMargins(10, 10, 10, 10)
		self.parent = parent

		## Pixel
		top_box = QVBoxLayout()
		top_box.addWidget(QLabel('<b>Pixel</b>'))
		hbox = QHBoxLayout()
		top_box.addLayout(hbox)
		self.layout.addLayout(top_box)

		# TableView
		self.tree_view = QTableView()
		self.table_model = PixelTableModel()
		self.tree_view.setModel(self.table_model)
		self.tree_view.doubleClicked.connect(self.on_tree_view_double_clicked)
		self.tree_view.selectionModel().selectionChanged.connect(self.on_tree_view_selection_changed)
		hbox.addWidget(self.tree_view)

		# Select
		buttons_box = ButtonBox(centered=True, linked=True)
		hbox.addLayout(buttons_box)
		self.select_pixel_button = QPushButton()
		pixmap = QPixmap(tools.get_full_path('icons/crosshair.png')).scaled(16, 16)
		self.select_pixel_button.setIcon(pixmap)
		self.select_pixel_button.setToolTip('Select')
		self.select_pixel_button.clicked.connect(self.on_select_pixel_button_clicked)
		buttons_box.addWidget(self.select_pixel_button)
		# Simulate
		self.simulate_click_button = QPushButton()
		pixmap = QPixmap(tools.get_full_path('icons/hand.png')).scaled(16, 16)
		self.simulate_click_button.setIcon(pixmap)
		self.simulate_click_button.setToolTip('Simulate Click')
		self.simulate_click_button.set_sensitive(False)
		self.simulate_click_button.clicked.connect(self.on_simulate_click_button_clicked)
		buttons_box.addWidget(self.simulate_click_button)
		# Delete
		self.delete_pixel_button = QPushButton()
		self.delete_pixel_button.setIcon(self.style().standardIcon(getattr(self.style(), 'SP_TrashIcon')))
		self.delete_pixel_button.setToolTip('Delete')
		self.delete_pixel_button.set_sensitive(False)
		self.delete_pixel_button.clicked.connect(self.on_delete_pixel_button_clicked)
		buttons_box.addWidget(self.delete_pixel_button)
		## Key Press
		bottom_box = QHBoxLayout()
		self.layout.addLayout(bottom_box)
		vbox = QVBoxLayout()
		bottom_box.addLayout(vbox)
		hbox = QHBoxLayout()
		vbox.addLayout(hbox)
		hbox.addWidget(QLabel('<b>Key Press</b>'))
		# Label
		self.keys_label = QLabel()
		hbox.addWidget(self.keys_label)
		# ComboBox
		hbox = QHBoxLayout()
		vbox.addLayout(hbox)
		self.keys_combo = CustomComboBox(data.KeyboardShortcuts, sort=True)
		self.keys_combo.currentIndexChanged.connect(self.on_keys_combo_changed)
		hbox.addWidget(self.keys_combo)
		# Simulate
		self.simulate_key_press_button = QPushButton()
		self.simulate_key_press_button.setIcon(self.style().standardIcon(getattr(self.style(), 'SP_DesktopIcon')))
		self.simulate_key_press_button.setToolTip('Simulate')
		self.simulate_key_press_button.set_sensitive(False)
		self.simulate_key_press_button.clicked.connect(self.on_simulate_key_press_button_clicked)
		hbox.addWidget(self.simulate_key_press_button)
		## Scroll
		vbox.addWidget(QLabel('<b>Scroll</b>'))
		hbox = QHBoxLayout()
		vbox.addLayout(hbox)
		# Direction
		self.scroll_direction_combo = CustomComboBox(['up', 'down'])
		self.scroll_direction_combo.setCurrentIndex(1)
		hbox.addWidget(self.scroll_direction_combo)
		# Value
		self.scroll_menu_button = QPushButton("1")
		self.scroll_menu_button.setMenu(QMenu())
		self.scroll_spin_button = QSpinBox()
		self.scroll_spin_button.setMinimum(1)
		self.scroll_spin_button.setMaximum(10)
		self.scroll_spin_button.valueChanged.connect(lambda value: self.scroll_menu_button.setText(str(value)))
		action = QWidgetAction(self.scroll_menu_button)
		action.setDefaultWidget(self.scroll_spin_button)
		self.scroll_menu_button.menu().addAction(action)
		hbox.addWidget(self.scroll_menu_button)
		# Simulate
		simulate_scroll_button = QPushButton()
		pixmap = QPixmap(tools.get_full_path('icons/scroll.png')).scaled(16, 16)
		simulate_scroll_button.setIcon(pixmap)
		simulate_scroll_button.setToolTip('Simulate')
		simulate_scroll_button.clicked.connect(self.on_simulate_scroll_button_clicked)
		hbox.addWidget(simulate_scroll_button)

	def on_simulate_scroll_button_clicked(self, button):
		# get scroll value
		direction = self.scroll_direction_combo.currentText()
		value = self.scroll_spin_button.value()
		clicks = value if direction == 'up' else -value
		if self.parent.game_window and not self.parent.game_window.is_destroyed() and self.parent.game_window_location:
			# get the center of the game location
			x, y = tools.coordinates_center(self.parent.game_window_location)
		else:
			x, y = (None, None)
		# scroll
		self.parent.focus_game()
		self.parent.debug('Scroll: %d' % clicks)
		tools.scroll_to(clicks, x, y, 0.5)	

	def on_keys_combo_changed(self, combo):
		selected = combo.currentText()
		self.keys_label.setText('(' + data.KeyboardShortcuts[selected] + ')')
		if not self.simulate_key_press_button.get_sensitive():
			self.simulate_key_press_button.setEnabled(True)

	def add_pixel(self, location):
		x, y, width, height, color = location
		# Create a pixmap
		image = QImage(10, 10, QImage.Format_RGB32)
		pixel = convert.rgb2pixel(color)
		image.fill(QColor(pixel))
		pixmap = QPixmap.fromImage(image)
		self.table_model.append_row([pixmap, x, y, width, height, str(color)])
		self.select_pixel_button.setEnabled(True)
		self.parent.set_cursor(QCursor(Qt.ArrowCursor))

	def on_select_pixel_button_clicked(self, button):
		button.setEnabled(False)
		self.parent.set_cursor(QCursor(Qt.CrossCursor))
		Thread(target=self.parent.wait_for_click, args=(self.add_pixel, self.parent.game_window_location)).start()

	def on_simulate_click_button_clicked(self, button):
		# get click coordinates
		selected_index = self.tree_view.currentIndex()
		row_data = self.table_model.get_row_data(selected_index.row())
		x, y, width, height = (row_data[1], row_data[2], row_data[3], row_data[4])
		# adjust for game area
		if self.parent.game_window and not self.parent.game_window.is_destroyed() and self.parent.game_window_location:
			game_x, game_y, game_width, game_height = self.parent.game_window_location
			click_x, click_y = tools.adjust_click_position(x, y, width, height, game_x, game_y, game_width, game_height)
		else:
			click_x = x
			click_y = y
		self.parent.debug('Simulate click on x: %d, y: %d' % (click_x, click_y))
		tools.perform_click(click_x, click_y)

	def on_delete_pixel_button_clicked(self, button):
		selected_index = self.tree_view.currentIndex()
		if selected_index.isValid():
			self.table_model.remove_row(selected_index.row())

	def on_simulate_key_press_button_clicked(self, button):
		selected = self.keys_combo.currentText()
		key = data.KeyboardShortcuts[selected]
		self.parent.focus_game()
		self.parent.debug('Press key: %s' % key)
		tools.press_key(key, 0.5)

	def on_click(self, widget, event):
		print('x: %d, y: %d' % (event.x, event.y))
		
	def on_tree_view_double_clicked(self, widget, event):
		selected_index = self.tree_view.currentIndex()
		if selected_index.isValid():
			selected_row = self.table_model.get_row_data(selected_index.row())
			if selected_row:
				x, y, width, height, color = (selected_row[1], selected_row[2], selected_row[3], selected_row[4], selected_row[5])
				CopyTextDialog(self.parent, "{'x': %d, 'y': %d, 'width': %d, 'height': %d, 'color': %s}" % (x, y, width, height, color)).exec_()
		
	def on_tree_view_selection_changed(self, selection):
		selected_indexes = self.tree_view.selectionModel().selectedRows()
		if not selected_indexes:
			self.simulate_click_button.setEnabled(False)
			self.delete_pixel_button.setEnabled(False)
		else:
			if not self.simulate_click_button.isEnabled():
				self.simulate_click_button.setEnabled(True)
			if not self.delete_pixel_button.isEnabled():
				self.delete_pixel_button.setEnabled(True)

class PixelTableModel(QAbstractTableModel):
	def __init__(self, data=None):
		super().__init__()
		self.data = data or []

	def rowCount(self, parent=QModelIndex()):
		return len(self.data)

	def columnCount(self, parent=QModelIndex()):
		return 6

	def data(self, index, role):
		if role == Qt.DisplayRole:
			return self.data[index.row()][index.column()]
		elif role == Qt.DecorationRole and index.column() == 0:
			return self.data[index.row()][0]
		return None

	def append_row(self, row_data):
		self.beginInsertRows(QModelIndex(), len(self.data), len(self.data))
		self.data.append(row_data)
		self.endInsertRows()

	def get_row_data(self, row_index):
		return self.data[row_index]
	
	def remove_row(self, row_index):
		if 0 <= row_index < len(self.data):
			self.beginRemoveRows(QModelIndex(), row_index, row_index)
			del self.data[row_index]
			self.endRemoveRows()
