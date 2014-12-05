import numpy as np
from scipy import optimize

def _createXYArrays(marker_list):
    """Given a list of QGraphicsEllipseItem's, qgei_point_list, return a numpy
    array of the x coordinates and a numpy array of the y coordinates.
    """

    # get the number of points
    num_points = marker_list.count()

    # initialize two numpy arrays as long as the number of points
    x_array = np.zeros(num_points)
    y_array = np.zeros(num_points)

    # loop over each marker's ellipse and populate x_array with x_coordinates
    # of the points; populate y_array with y_coordinates
    for row in range(num_points):
        point = marker_list.item(row)
        x_array[row] = np.float64(point.ellipse.rect().center().x())
        y_array[row] = np.float64(point.ellipse.rect().center().y())

    return x_array, y_array

def _distanceResiduals(center_tuple, x_array, y_array):

    distances = np.sqrt((x_array - center_tuple[0])**2 + (y_array - center_tuple[1])**2)
    residuals = distances - distances.mean()
    return residuals

def circleFit(marker_list):
    """Given a list of QGraphicsEllipseItem's, qgei_point_list, return """

    # convert list of qgei's to arrays of x_coordinates and y_coordinates
    x_array, y_array = _createXYArrays(marker_list)

    # use the means of the x coorindates, y_coordinates as initial guesses for the circle centre coordinates
    center_estimate = (x_array.mean(), y_array.mean())

    center_lsq, cov_matrix, infodict, mesg, ier = optimize.leastsq(_distanceResiduals, center_estimate, args=(x_array, y_array), full_output=True, 
             ftol=1e-15, xtol=1e-15)
    chi2_dof = (_distanceResiduals(center_lsq, x_array, y_array)**2).sum()/(len(y_array)-len(center_estimate))
    pcov = cov_matrix * chi2_dof
    center_x, center_y = center_lsq
    delta_c_x, delta_c_y = np.sqrt(np.diag(pcov))
    radius = np.sqrt((x_array - center_x)**2 + (y_array - center_y)**2).mean()
    delta_radius = np.sqrt(((center_x-x_array).mean()/radius*delta_c_x)**2 + ((center_y-y_array).mean()/radius*delta_c_y)**2)

    return [(center_x, delta_c_x), (center_y, delta_c_y), (radius, delta_radius)]
