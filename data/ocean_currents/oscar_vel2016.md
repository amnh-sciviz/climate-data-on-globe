URL: https://podaac.jpl.nasa.gov/dataset/OSCAR_L4_OC_third-deg
File: oscar_vel2016.nc

NetCDF Global Attributes:
	VARIABLE: u'Ocean Surface Currents'
	DATATYPE: u'1/72 YEAR Interval'
	DATASUBTYPE: u'unfiltered'
	GEORANGE: u'20 to 420 -80 to 80'
	PERIOD: u'Jan.01,2016 to Dec.26,2016'
	year: u'2016'
	description: u'OSCAR Third Degree Sea Surface Velocity'
	CREATION_DATE: u'03:18 03-Aug-2017'
	version: 2009.0
	source: u'Gary Lagerloef, ESR (lager@esr.org) and Kathleen Dohan, ESR (kdohan@esr.org)'
	contact: u'Kathleen Dohan (kdohan@esr.org) or John T. Gunn (gunn@esr.org)'
	company: u'Earth & Space Research, Seattle, WA'
	reference: u'Bonjean F. and G.S.E. Lagerloef, 2002 ,Diagnostic model and analysis of the surface currents in the tropical Pacific ocean, J. Phys. Oceanogr., 32, 2,938-2,954'
	note1: u'Maximum Mask velocity is the geostrophic component at all points + any concurrent Ekman and buoyancy components'
	note2: u'Longitude extends from 20 E to 420 E to avoid a break in major ocean basins. Data repeats in overlap region.'
NetCDF dimension information:
	Name: time
		size: 72
		type: dtype('int32')
		units: u'day since 1992-10-05 00:00:00'
		long_name: u'Day since 1992-10-05 00:00:00'
	Name: year
		size: 72
		type: dtype('float32')
		units: u'time in years'
		long_name: u'Time in fractional year'
	Name: depth
		size: 1
		type: dtype('float32')
		units: u'meter'
		long_name: u'Depth'
	Name: latitude
		size: 481
		type: dtype('float64')
		units: u'degrees-north'
		long_name: u'Latitude'
	Name: longitude
		size: 1201
		type: dtype('float64')
		units: u'degrees-east'
		long_name: u'Longitude'
NetCDF variable information:
	Name: u
		dimensions: (u'time', u'depth', u'latitude', u'longitude')
		size: 41593032
		type: dtype('float64')
		units: u'meter/sec'
		long_name: u'Ocean Surface Zonal Currents'
		missing_value: nan
	Name: v
		dimensions: (u'time', u'depth', u'latitude', u'longitude')
		size: 41593032
		type: dtype('float64')
		units: u'meter/sec'
		long_name: u'Ocean Surface Meridional Currents'
		missing_value: nan
	Name: um
		dimensions: (u'time', u'depth', u'latitude', u'longitude')
		size: 41593032
		type: dtype('float64')
		units: u'meter/sec'
		long_name: u'Ocean Surface Zonal Currents Maximum Mask'
		missing_value: nan
	Name: vm
		dimensions: (u'time', u'depth', u'latitude', u'longitude')
		size: 41593032
		type: dtype('float64')
		units: u'meter/sec'
		long_name: u'Ocean Surface Meridional Currents Maximum Mask'
		missing_value: nan
