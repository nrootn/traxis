import numpy
from scipy import optimize

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

def distanceResiduals(center_tuple, x_array, y_array):

	distances = numpy.sqrt((x_array - center_tuple[0])**2 + (y_array - center_tuple[1])**2)
	residuals = distances - distances.mean()
	return residuals

def circleFit(qgei_point_list):
	"""Given a list of QGraphicsEllipseItem's, qgei_point_list, return """

	# convert list of qgei's to arrays of x_coordinates and y_coordinates
	x_array, y_array = createXYArrays(qgei_point_list)

	# use the means of the x coorindates, y_coordinates as initial guesses for the circle centre coordinates
	center_estimate = (x_array.mean(), y_array.mean())

	center_lsq, cov_matrix, infodict, mesg, ier = optimize.leastsq(distanceResiduals, center_estimate, args=(x_array, y_array), full_output=True)
	chi2_dof = (distanceResiduals(center_lsq, x_array, y_array)**2).sum()/(len(y_array)-len(center_estimate))
	pcov = cov_matrix * chi2_dof
	center_x, center_y = center_lsq
	delta_c_x, delta_c_y = numpy.sqrt(numpy.diag(pcov))
	radius = numpy.sqrt((x_array - center_x)**2 + (y_array - center_y)**2).mean()
	delta_radius = numpy.sqrt(((center_x-x_array).mean()/radius*delta_c_x)**2 + ((center_y-y_array).mean()/radius*delta_c_y)**2)

	return [(center_x, delta_c_x), (center_y, delta_c_y), (radius, delta_radius)]

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
