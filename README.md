# sun-calculator
The program is able to calculate the sunrise and sunset times at any geographic coordinate on earth and on any date of the year (approximately), as long as the time zone (GMT+n) information is known. 

The current version assumes observations are made on the surface of the earth without altitude information. 365.25 days per year (average), 28.25 days in February, and 86400 seconds per day are used for calculation. Simple models and spherical geometry analysis are used, without considering details in more depth, so calculation is only an approximate result.

To try this program, run test.py to see two examples or use the tabulate() function to view a table of 3 locations and 4 dates.

Also, you can use calcSun() function in test.py to create your own example. Provide latitude, longitude, time zone (GMT+n), and date, in this order, to view results. Sunrise and sunset are local times in the given time zone.

For example: calcSun(43.65, -79.35, -4, Date(7,1))
Note: 
1) Latitude (-90 to 90) and lontitude (-180 to 180) units are degree, with positive suggesting north/east and negative south/west
2) GMT input range is from -12 to 12 inclusive
3) Date argument is constructed by the Date(month, day) constructor
