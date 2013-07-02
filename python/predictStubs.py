def getPredictCurve(growthCurve):
	try:
		predictX = []
		predictY = []
		class Object(object):
				pass
		predictCurve = Object()
		startTime = growthCurve.startTime
		time = startTime
		print 'startTime:'+str(time)
		f = interp1d(growthCurve.X, growthCurve.Y, bounds_error=False,kind='cubic')
		while time<=startTime+(24*3600):
			time = time+(30*60)
			print time
 			predictX.append(time)
			predictY.append(f(time))
			print f(time)
		print predictX
		print predictY	
		predictCurve.predictX = predictX
		predictCurve.predictY = predictY	
		return predictCurve

	except Exception, e:
		print 'Error in line:'+str(sys.exc_traceback.tb_lineno)
		print e
		pass
	finally:
		pass

def getPredictCurve(growthCurve):
	try:
		predictX = []
		predictY = []
		class Object(object):
				pass
		predictCurve = Object()
		startTime = growthCurve.startTime
		time = startTime
		print 'startTime:'+str(time)
		xnew = np.linspace(startTime,growthCurve.X.max(),600)
		power_smooth = spline(growthCurve.X,growthCurve.Y,xnew)	
		predictCurve.predictX = xnew
		predictCurve.predictY = power_smooth
		return predictCurve

	except Exception, e:
		print 'Error in line:'+str(sys.exc_traceback.tb_lineno)
		print e
		pass
	finally:
		pass