from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics.texture import Texture
from kivy.clock import Clock
from kivy.graphics import Rectangle
from renderer import RealtimeQuadRenderer, RealtimeJuliaQuadRenderer

class RendererWidget(Widget):
	def __init__(self):
		super().__init__()
		self.res = 512
		self.texture = Texture.create(size=(self.res, self.res), bufferfmt="ubyte", colorfmt='rgb')
		with self.canvas:
			Rectangle(texture=self.texture, pos=(0, 0), size=(self.res, self.res))
		self.renderer = RealtimeJuliaQuadRenderer(res = self.res, AA = 8, maxIters = 100)
		self.renderer.begin()
		Clock.schedule_interval(self.tick, 1 / 30.)

	def tick(self, dt):
		for i in range(10):
			self.renderer.tick()
		self.renderer.updateImage()
		self.texture.blit_buffer(self.renderer.image.tostring(), bufferfmt="ubyte", colorfmt="rgb")
		self.canvas.ask_update()


class RendererApp(App):
	def build(self):
		self.title = 'Quadtree Renderer'
		return RendererWidget()


if __name__=="__main__":
	RendererApp().run()