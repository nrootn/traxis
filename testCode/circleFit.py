import numpy
from scipy import odr, row_stack
import matplotlib.pyplot as plt

def implicitCircle(p, x):
	return (x[0]-p[0])**2 + (x[1]-p[1])**2 - p[2]**2

def circleFit(x_array, y_array, delta_x, delta_y):
	if len(x_array) != len(delta_x) or len(y_array) != len(delta_y):
		return
	if len(x_array) != len(y_array):
		return
	if len(x_array) < 3:
		return

	x_m = x_array.mean()
	y_m = y_array.mean()
	r_m = numpy.sqrt((x_array - x_m)**2 + (y_array - y_m)**2).mean()

	p0 = [x_m, y_m, r_m]

	odr_data = odr.Data(row_stack([x_array, y_array]), y=1)
	odr_model = odr.Model(implicitCircle, implicit=True)
	odr_odr = odr.ODR(odr_data, odr_model, beta0=p0, delta0=row_stack([delta_x, delta_y]))
	odr_out = odr_odr.run()

	return odr_out

if __name__ == "__main__":
	x = numpy.array([36, 36, 19, 18, 33, 26])
	y = numpy.array([14, 10, 28, 31, 18, 26])
	delta_x = numpy.array([2, 1, 1, 3, 2, 1])
	delta_y = numpy.array([1, 1, 2, 1, 2, 1])

	odr_fit = circleFit(x, y, delta_x, delta_y)

	print(odr_fit.beta)
	print(odr_fit.cov_beta)
	plt.scatter(x, y)
	plt.scatter(numpy.array(odr_fit.beta[0]), numpy.array(odr_fit.beta[1]))
	
	plt.show()
