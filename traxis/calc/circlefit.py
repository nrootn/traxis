# Copyright (C) 2014 Syed Haider Abidi, Nooruddin Ahmed and Christopher Dydula
#
# This file is part of traxis.
#
# traxis is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# traxis is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with traxis.  If not, see <http://www.gnu.org/licenses/>.

import numpy as np
from scipy import optimize

def _createXYArrays(markerList):
    """Given markerList, a MarkerList object, return two numpy arrays, one
    containing the x-coordinates of the markers and the second the
    corrsponding y-coordinates.
    """

    # initialize two numpy arrays whose lengths are equal to the number of
    # markers in markerList
    xArray = np.zeros(markerList.count())
    yArray = np.zeros(markerList.count())

    # loop over each marker, setting the x-coordinate of each marker as an
    # element of xArray and each y-coordinate as an element of yArray
    for row in range(markerList.count()):
        marker = markerList.item(row)
        # using 64 bit floats seems to be necessary to ensure consistent
        # results across all systems. Some systems get the same results
        # with or without np.float64() but others don't. When using
        # float64, results match for all systems tested.
        xArray[row] = np.float64(marker.ellipse.rect().center().x())
        yArray[row] = np.float64(marker.ellipse.rect().center().y())

    return xArray, yArray

def _distanceResiduals(referencePoint, xArray, yArray):
    """Given referencePoint, a tuple whose first element is the x-coordinate
    and whose second element is the y-coordinate, xArray, an array of
    x-coordinates, and yArray, an array of the corresponding y-coordinates of
    a set of points (xArray and yArray are expected to have the same length),
    return an array containing for each point the difference between the
    distance from that point to the reference point and the mean of the
    distances.
    """

    # compute the distance from each point to the reference point
    distances = np.sqrt((xArray - referencePoint[0])**2 + \
                        (yArray - referencePoint[1])**2)
    # compute the difference between the distance from each point to the
    # reference point and the mean of the distances
    distanceResiduals = distances - distances.mean()

    return distanceResiduals

def fitCircle(markerList):
    """Given markerList, a MarkerList object, fit a circle to the markers
    using the least squares method and return the coordinates of the centre
    and the radius of the fitted circle along with their errors.
    """

    # convert the list of track markers to arrays of the x-coordinates and
    # y-coordinates of the markers
    xArray, yArray = _createXYArrays(markerList)

    # use the mean of the x-coordinates of the markers as an initial guess for
    # x-coordinate of the circle center. Similarly for y-coordinates.
    centerEstimate = (xArray.mean(), yArray.mean())

    # initialize the dictionary containing the parameters of the fitted circle
    # to be returned by this function
    fitParams = {}

    # calculate the optimal centre coordinates for the fitted circle, such
    # that the squares of the residuals of the distances from each point to
    # the centre are minimized. Store the optimal coordinates in the variable
    # centerLsq. Pass full_output=True to the leastsq function so that the
    # covariance matrix of the optimized coordinates is returned. This also
    # makes the function return infodict, mesg and ier which are not used.
    # Decrease the desired error in the results by passing explicit values
    # for ftol and xtol (the default value is 1.49012e-8)
    centerLsq, covMatrix, infodict, mesg, ier = optimize.leastsq(
                                                    _distanceResiduals,
                                                    centerEstimate, 
                                                    args=(xArray, yArray), 
                                                    full_output=True, 
                                                    ftol=1e-15, xtol=1e-15)

    # note from the documentation for scipy.optimize.leastsq regarding the
    # covariance matrix it returns: "This matrix must be multiplied by the
    # residual variance to get the covariance of the parameter estimates"
    # The 'residual variance' is just chi-squared/degrees of freedom
    dof = len(yArray)-len(centerEstimate)
    chi2Dof = (_distanceResiduals(centerLsq, xArray, yArray)**2).sum()/dof
    # multiply covMatrix by the 'residual variance' to get the covariance
    # of the parameter estimates
    parameterCov = covMatrix * chi2Dof

    # store the optimal centre coordinates in the fitParams dict
    fitParams['centerX'], fitParams['centerY'] = centerLsq
    # store the errors on the optimal centre coordinates in the fitParams dict.
    # the errors are the square roots of the diagonal elements of the parameter
    # covariance
    fitParams['centerXErr'], fitParams['centerYErr'] = np.sqrt(np.diag(parameterCov))

    # store the radius of the fitted circle in the fitParams dict. Based on
    # how the lsq fit was performed, this is the mean of the distances from
    # each point to the optimal circle centre
    fitParams['radius'] = np.sqrt((xArray - fitParams['centerX'])**2 + \
                                  (yArray - fitParams['centerY'])**2).mean()

    # store the error on the radius in the fitParams dict. Given radius R,
    # centre coordinates (h, k) with error dh, dk and a point (x, y) assumed
    # to be known to perfect accuracy, the error on the radius is
    # dR^2 = ((x-h)/R * dh)^2 + ((y-k)/R * dk)^2
    # Compute this dR for each point individually and then take the mean
    fitParams['radiusErr'] = np.sqrt(
        ((fitParams['centerX']-xArray).mean()/ \
         fitParams['radius']*fitParams['centerXErr'])**2 + \
        ((fitParams['centerY']-yArray).mean()/ \
         fitParams['radius']*fitParams['centerYErr'])**2)

    return fitParams
