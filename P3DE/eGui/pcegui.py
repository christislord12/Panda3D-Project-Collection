# Python imports
import os, sys, string

# PyCEGUI imports
import PyCEGUI
import PyCEGUIOpenGLRenderer

# Panda imports
from panda3d.core import PythonCallbackObject, CallbackNode, DataNode
from pandac.PandaModules import WindowProperties, ModifierButtons

class PandaCEGUI(object):
	"""A python module for integrating PyCEGUI with Panda3D.

	"""
	buttons = {
		'mouse1': PyCEGUI.MouseButton.LeftButton,
		'mouse2': PyCEGUI.MouseButton.RightButton,
		'mouse3': PyCEGUI.MouseButton.MiddleButton,
		'mouse1-up': PyCEGUI.MouseButton.LeftButton,
		'mouse2-up': PyCEGUI.MouseButton.RightButton,
		'mouse3-up': PyCEGUI.MouseButton.MiddleButton,
		'wheel_up': PyCEGUI.MouseButton.NoButton,
		'wheel_down': PyCEGUI.MouseButton.NoButton,
	}
   
	keys = {
		'a': (PyCEGUI.Key.Scan.A, 'a', 'A'),
		'b': (PyCEGUI.Key.Scan.B, 'b', 'B'),
		'c': (PyCEGUI.Key.Scan.C, 'c', 'C'),
		'd': (PyCEGUI.Key.Scan.D, 'd', 'D'),
		'e': (PyCEGUI.Key.Scan.E, 'e', 'E'),
		'f': (PyCEGUI.Key.Scan.F, 'f', 'F'),
		'g': (PyCEGUI.Key.Scan.G, 'g', 'G'),
		'h': (PyCEGUI.Key.Scan.H, 'h', 'H'),
		'i': (PyCEGUI.Key.Scan.I, 'i', 'I'),
		'j': (PyCEGUI.Key.Scan.J, 'j', 'J'),
		'k': (PyCEGUI.Key.Scan.K, 'k', 'K'),
		'l': (PyCEGUI.Key.Scan.L, 'l', 'L'),
		'm': (PyCEGUI.Key.Scan.M, 'm', 'M'),
		'n': (PyCEGUI.Key.Scan.N, 'n', 'N'),
		'o': (PyCEGUI.Key.Scan.O, 'o', 'O'),
		'p': (PyCEGUI.Key.Scan.P, 'p', 'P'),
		'q': (PyCEGUI.Key.Scan.Q, 'q', 'Q'),
		'r': (PyCEGUI.Key.Scan.R, 'r', 'R'),
		's': (PyCEGUI.Key.Scan.S, 's', 'S'),
		't': (PyCEGUI.Key.Scan.T, 't', 'T'),
		'u': (PyCEGUI.Key.Scan.U, 'u', 'U'),
		'v': (PyCEGUI.Key.Scan.V, 'v', 'V'),
		'w': (PyCEGUI.Key.Scan.W, 'w', 'W'),
		'x': (PyCEGUI.Key.Scan.X, 'x', 'X'),
		'y': (PyCEGUI.Key.Scan.Y, 'y', 'Y'),
		'z': (PyCEGUI.Key.Scan.Z, 'z', 'Z'),

		'`': (PyCEGUI.Key.Scan.Grave, '`', '~'),
		'0': (PyCEGUI.Key.Scan.Zero, '0', ')'),
		'1': (PyCEGUI.Key.Scan.One, '1', '!'),
		'2': (PyCEGUI.Key.Scan.Two, '2', '@'),
		'3': (PyCEGUI.Key.Scan.Three, '3', '#'),
		'4': (PyCEGUI.Key.Scan.Four, '4', '$'),
		'5': (PyCEGUI.Key.Scan.Five, '5', '%'),
		'6': (PyCEGUI.Key.Scan.Six, '6', '^'),
		'7': (PyCEGUI.Key.Scan.Seven, '7', '&'),
		'8': (PyCEGUI.Key.Scan.Eight, '8', '*'),
		'9': (PyCEGUI.Key.Scan.Nine, '9', '('),
		'-': (PyCEGUI.Key.Scan.Minus, '-', '_'),
		'=': (PyCEGUI.Key.Scan.Equals, '=', '+'),


		'[': (PyCEGUI.Key.Scan.LeftBracket, '[', '{'),
		']': (PyCEGUI.Key.Scan.RightBracket, ']', '}'),
		'\\': (PyCEGUI.Key.Scan.Backslash, '\\', '|'),
		';': (PyCEGUI.Key.Scan.Semicolon, ';', ':'),

		"'": (PyCEGUI.Key.Scan.Apostrophe, "'", '"'),
		',': (PyCEGUI.Key.Scan.Comma, ',', '<'),
		'.': (PyCEGUI.Key.Scan.Period, '.', '>'),
		'/': (PyCEGUI.Key.Scan.Slash, '/', '?'),

		'f1': (PyCEGUI.Key.Scan.F1, '', ''),
		'f2': (PyCEGUI.Key.Scan.F3, '', ''),
		'f3': (PyCEGUI.Key.Scan.F3, '', ''),
		'f4': (PyCEGUI.Key.Scan.F4, '', ''),
		'f5': (PyCEGUI.Key.Scan.F5, '', ''),
		'f6': (PyCEGUI.Key.Scan.F6, '', ''),
		'f7': (PyCEGUI.Key.Scan.F7, '', ''),
		'f8': (PyCEGUI.Key.Scan.F8, '', ''),
		'f9': (PyCEGUI.Key.Scan.F9, '', ''),
		'f10': (PyCEGUI.Key.Scan.F10, '', ''),
		'f11': (PyCEGUI.Key.Scan.F11, '', ''),
		'f12': (PyCEGUI.Key.Scan.F12, '', ''),

		'enter': (PyCEGUI.Key.Scan.Return, '\r', '\r'),
		'tab': (PyCEGUI.Key.Scan.Tab, '\t', '\t'),
		'space': (PyCEGUI.Key.Scan.Space, ' ', ' '),

		'escape': (PyCEGUI.Key.Scan.Escape, '', ''),
		'backspace': (PyCEGUI.Key.Scan.Backspace, '', ''),

		'insert': (PyCEGUI.Key.Scan.Insert, '', ''),
		'delete': (PyCEGUI.Key.Scan.Delete, '', ''),

		'home': (PyCEGUI.Key.Scan.Home, '', ''),
		'end': (PyCEGUI.Key.Scan.End, '', ''),
		'page_up': (PyCEGUI.Key.Scan.PageUp, '', ''),
		'page_down': (PyCEGUI.Key.Scan.PageDown, '', ''),

		'arrow_left': (PyCEGUI.Key.Scan.ArrowLeft, '', ''),
		'arrow_up': (PyCEGUI.Key.Scan.ArrowUp, '', ''),
		'arrow_down': (PyCEGUI.Key.Scan.ArrowDown, '', ''),
		'arrow_right': (PyCEGUI.Key.Scan.ArrowRight, '', ''),

		'num_lock': (PyCEGUI.Key.Scan.NumLock, '', ''),
		'caps_lock': (PyCEGUI.Key.Scan.Capital, '', ''),
		'scroll_lock': (PyCEGUI.Key.Scan.ScrollLock, '', ''),

		'lshift': (PyCEGUI.Key.Scan.LeftShift, '', ''),
		'rshift': (PyCEGUI.Key.Scan.RightShift, '', ''),
		'lcontrol': (PyCEGUI.Key.Scan.LeftControl, '', ''),
		'rcontrol': (PyCEGUI.Key.Scan.RightControl, '', ''),
		'lalt': (PyCEGUI.Key.Scan.LeftAlt, '', ''),
		'ralt': (PyCEGUI.Key.Scan.RightAlt, '', ''),
		}

	# Tells PandaCEGUI to handle hiding/showing the system cursor on enable/disable
	hideSystemCursor = True
	_renderingEnabled = True
	_capsLock = False
	_shiftCount = 0

	def __init__(self):
		# Panda Setup
		ceguiCB = PythonCallbackObject(self.renderCallback)
		self.cbNode = CallbackNode("CEGUI")
		self.cbNode.setDrawCallback(ceguiCB)
		render2d.attachNewNode(self.cbNode)
	   
		base.accept('window-event', self.windowEvent)

		# Initialize the OpenGLRenderer
		PyCEGUIOpenGLRenderer.OpenGLRenderer.bootstrapSystem()

		self.props = WindowProperties()

		# For convienence
		self.System = PyCEGUI.System.getSingleton()
		self.WindowManager = PyCEGUI.WindowManager.getSingleton()
		self.SchemeManager = PyCEGUI.SchemeManager.getSingleton()
		self.FontManager = PyCEGUI.FontManager.getSingleton()
		self.ImagesetManager = PyCEGUI.ImagesetManager.getSingleton()

	def __del__(self):
		PyCEGUIOpenGLRenderer.OpenGLRenderer.destroySystem()

	def initializeResources(self, resourcePath):
		"""Initializes CEGUI's resource groups. This must be called before attempting to setup a UI.

		"""
		rp = self.System.getResourceProvider()

		# Setup our resource directories
		rp.setResourceGroupDirectory("schemes", resourcePath + "/schemes")
		rp.setResourceGroupDirectory("imagesets", resourcePath + "/imagesets")
		rp.setResourceGroupDirectory("fonts", resourcePath + "/fonts")
		rp.setResourceGroupDirectory("layouts", resourcePath + "/layouts")
		rp.setResourceGroupDirectory("looknfeels", resourcePath + "/looknfeel")
		rp.setResourceGroupDirectory("schemas", resourcePath + "/xml_schemas")
	   
		# Set default resource groups
		PyCEGUI.Imageset.setDefaultResourceGroup("imagesets")
		PyCEGUI.Font.setDefaultResourceGroup("fonts")
		PyCEGUI.Scheme.setDefaultResourceGroup("schemes")
		PyCEGUI.WidgetLookManager.setDefaultResourceGroup("looknfeels")
		PyCEGUI.WindowManager.setDefaultResourceGroup("layouts")
	   
		# Get our xml parser
		parser = self.System.getXMLParser()
		if parser.isPropertyPresent("SchemaDefaultResourceGroup"):
			parser.setProperty("SchemaDefaultResourceGroup", "schemas")	 

	def enableInputHandling(self):
		# Mouse button handling
		for button, cegui_name in self.buttons.iteritems():
			base.accept(button, self.captureButton, [button, cegui_name])

		# Turn off compound events so we can actually use the modifier keys
		# as expected in a game.
		base.mouseWatcherNode.setModifierButtons(ModifierButtons())
		base.buttonThrowers[0].node().setModifierButtons(ModifierButtons())

		# Key handling
		for key, keyTuple in self.keys.iteritems():
			base.accept(key, self.captureKeys, [key, keyTuple])
			base.accept(key + '-up', self.captureKeys, [key + '-up', keyTuple])
			base.accept(key + '-repeat', self.captureKeys, [key, keyTuple])

		if (self.hideSystemCursor):
			self.props.setCursorHidden(True)
			base.win.requestProperties(self.props)

	def disableInputHandling(self):
		# Mouse button handling
		for button, name in self.buttons.iteritems():
			base.ignore(button)

		# Key handling
		for key, keyTuple in self.keys.iteritems():
			base.ignore(key)
			base.ignore(key + '-up')
			base.ignore(key + '-repeat')

		if (self.hideSystemCursor):
			self.props.setCursorHidden(False)
			base.win.requestProperties(self.props)

	def enable(self):
		self.enableInputHandling()
		_renderingEnabled = True

	def disable(self):
		self.disableInputHandling()
		_renderingEnabled = False
   
	def captureKeys(self, key, keyTuple):
		cegui_key = keyTuple[0]
		key_ascii = keyTuple[1]
		key_shift = keyTuple[2]

		if key.find('shift') > 0:
			if key.endswith('-up'):
				if self._shiftCount > 0:
					self._shiftCount -= 1
			else:
				self._shiftCount += 1
	   
		elif key == 'caps_lock':
			self._capsLock = not self._capsLock

		elif key.endswith('-up'):
			self.System.injectKeyUp(cegui_key)
	   
		else:
			self.System.injectKeyDown(cegui_key)
			if key_ascii != '':
				if self._shiftCount > 0:
					if self._capsLock and key_ascii in string.lowercase:
						self.System.injectChar(ord(key_ascii))

					else:
						self.System.injectChar(ord(key_shift))

				elif self._capsLock and key_ascii in string.lowercase:
					self.System.injectChar(ord(key_shift))

				else:
					self.System.injectChar(ord(key_ascii))

	def captureButton(self, button, name):
		if button == 'wheel_up':
			self.System.injectMouseWheelChange(1)
		elif button == 'wheel_down':
			self.System.injectMouseWheelChange(-1)
		elif button.endswith('-up'):
			self.System.injectMouseButtonUp(self.buttons[button])
		else:
			self.System.injectMouseButtonDown(self.buttons[button])

	def windowEvent(self, window):
	   self.System.notifyDisplaySizeChanged(PyCEGUI.Size(window.getXSize(), window.getYSize()))

	def renderCallback(self, data):
		if self._renderingEnabled:
			dt = globalClock.getDt()
			self.System.injectTimePulse(dt)

			if base.mouseWatcherNode.hasMouse():
				x = base.win.getXSize() * (1 + base.mouseWatcherNode.getMouseX()) / 2
				y = base.win.getYSize() * (1 - base.mouseWatcherNode.getMouseY()) / 2
				self.System.injectMousePosition(x, y)

			self.System.renderGUI()
