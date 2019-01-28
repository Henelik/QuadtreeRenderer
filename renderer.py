from numba import jit
from scipy.misc import imsave
import gradient, mandelbrot, cactus, julia
import time
from math import ceil, floor
import itertools

class FullRenderer():
	def __init__(self, xRes = 512, yRes = 512, AA = 0):
		self.xRes = xRes
		self.yRes = yRes
		self.AA = min(AA, 7)

		self.cam = Camera(xRes, yRes, xPos = -.5)

	def render(self, maxIters):
		t = time.clock()

		image = [[mandelbrot.render(self.cam.convertX(x), self.cam.convertY(y), maxIters) for x in range(self.xRes)] for y in range(self.yRes)]

		print("Render time was " + str(time.clock()-t) + " seconds.")
		return image

class QuadRenderer():
	def __init__(self, res = 512, AA = 0, disableMaxResAA = True):
		self.res = res
		self.AA = AA
		self.disableMaxResAA = disableMaxResAA

		self.cam = Camera(res, res, xPos = -.5)

	def render(self, subdivMax, maxIters):
		def sparseRender(x, y, size):
			if size == 1 and self.disableMaxResAA:
				return mandelbrot.render(self.cam.convertX(x), self.cam.convertY(y), maxIters)
			half = size/2
			pixelList = [(x, y), (x+size, y+size), (x+size, y), (x, y+size), (x+half, y+half), (x+half, y), (x, y+half), (x+half, y+size), (x+size, y+half)]
			pix = []
			for i in pixelList:
				if len(pix) > self.AA+2:
					break
				if i in sparseArray:
					pix.append(sparseArray[i])
				else:
					pix.append(mandelbrot.render(self.cam.convertX(i[0]), self.cam.convertY(i[1]), maxIters))
					sparseArray[i] = pix[-1]
			return sum(pix)

		t = time.clock()
		image = [[0 for x in range(self.res)] for y in range(self.res)]
		sparseArray = {}

		s = floor(self.res/2)
		quadList = [
		Quad(0, 0, s, sparseRender(0, 0, s)),
		Quad(0, s, s, sparseRender(0, s, s)),
		Quad(s, 0, s, sparseRender(s, 0, s)),
		Quad(s, s, s, sparseRender(s, s, s))]
		sortLimit = 0 # heuristically limit how often we sort to improve performance
		while subdivMax:
			subdivMax -= 1
			sortLimit -= 1
			if sortLimit <= 0 or quadList[0].priority == 0:
				quadList.sort(key = lambda q: q.priority, reverse = True)
				sortLimit = floor(len(quadList)/2)
				if quadList[0].priority == 0:
					break
			current = quadList.pop(0)
			newSize = floor(current.size/2)
			for j in [(current.x, current.y), (current.x+newSize, current.y), (current.x, current.y+newSize), (current.x+newSize, current.y+newSize)]:
				quadList.append(Quad(j[0], j[1], newSize, sparseRender(j[0], j[1], newSize)))
		print(len(quadList))
		for i in range(len(quadList)):
			q = quadList[i]
			for y in range(q.y, q.y + q.size):
				for x in range(q.x, q.x + q.size):
					#image[y][x] = q.color
					image[y][x] = i
		print("Dynamic render time was " + str(time.clock()-t) + " seconds.")
		return image


class Camera(): # This class is responsible for handling the conversion from pixel position to mathematical space
	def __init__(self, xRes, yRes, xPos = 0, yPos = 0, zoom = 2):
		self.xRes = xRes
		self.yRes = yRes
		self.xPos = xPos
		self.yPos = yPos
		self.zoom = zoom

	def convertPos(self, x, y):
		return((convertX(x), convertY(y)))

	def convertX(self, x):
		return (x-self.xRes/2)*self.zoom/self.xRes+self.xPos

	def convertY(self, y):
		return (y-self.yRes/2)*self.zoom/self.yRes-self.yPos


class Quad():
	def __init__(self, x, y, size, color):
		self.x = x
		self.y = y
		self.size = size
		self.color = color
		if size <= 1:
			self.priority = 0
		else:
			self.priority = size*color

if __name__ == "__main__":
	fullR = FullRenderer()
	quadR = QuadRenderer(AA = 2, disableMaxResAA = True)
	imsave('dynamic.png', quadR.render(100000, 100))
	imsave('fullRes.png', fullR.render(100))
