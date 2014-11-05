import numpy
from scipy import odr, row_stack

def createXYArrays(qgei_point_list):
	"""Given a list of QGraphicsEllipseItem's, qgei_point_list, return a numpy array of the x coordinates and a numpy array of the y coordinates."""

	# get the number of points
	num_points = len(qgei_point_list)

	# initialize two numpy arrays as long as the number of points
	x_array = numpy.zeros(num_points)
	y_array = numpy.zeros(num_points)

	# loop over each QGraphicsEllipseItem and populate x_array with x_coordinates of the points; populate y_array with y_coordinates
	for index,point in enumerate(qgei_point_list):
		x_array[index] = point.rect().center().x()
		y_array[index] = point.rect().center().y()

	return x_array, y_array

def implicitCircle(p, x):
	"""Implicit function definition of the circle. p is a list of parameters(p[0] is x coordinate of centre, p[1] is y coordinate of centre, p[2] is radius), x is list of variables (x[0] is x, x[1] is y)."""
	return (x[0]-p[0])**2 + (x[1]-p[1])**2 - p[2]**2

def circleFit(qgei_point_list):
	"""Given a list of QGraphicsEllipseItem's, qgei_point_list, return """

	# convert list of qgei's to arrays of x_coordinates and y_coordinates
	x_array, y_array = createXYArrays(point_list)

	# use the means of the x coorindates, y_coordinates and "radii" as initial guesses for the circle centre coordinates and radius
	x_m = x_array.mean()
	y_m = y_array.mean()
	r_m = numpy.sqrt((x_array - x_m)**2 + (y_array - y_m)**2).mean()

	beta0 = [x_m, y_m, r_m]

	fit_data = odr.Data(row_stack([x_array, y_array]), y=1)
	fit_model = odr.Model(implicitCircle, implicit=True)
	fit_odr = odr.ODR(fit_data, fit_model, beta0=beta0)
	fit_out = fit_odr.run()

	centre_x, centre_y, radius = fit_out.beta
	delta_c_x = fit_out.sd_beta[0]
	delta_c_y = fit_out.sd_beta[1]
	delta_radius = fit_out.sd_beta[2]

	return [(centre_x, delta_c_x), (centre_y, delta_c_y), (radius, delta_radius)]

if __name__ == "__main__":
	from PyQt5.QtWidgets import QGraphicsEllipseItem as qgei
	import matplotlib.pyplot as plt

	point_list = [qgei(36, 14, 10, 10), qgei(36, 10, 10, 10), qgei(19, 28, 10, 10), qgei(18, 31, 10, 10), qgei(33, 18, 10, 10), qgei(26, 26, 10, 10)]

	x, y = createXYArrays(point_list)
	fitted_circle = circleFit(point_list)
	print(fitted_circle)

	circle = plt.Circle((fitted_circle[0][0], fitted_circle[1][0]), fitted_circle[2][0], color='r', fill=False)
	ax = plt.gca()
	ax.cla()
	ax.scatter(x, y)
	fig = plt.gcf()
	fig.gca().add_artist(circle)
	plt.show()
