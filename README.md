# Y-Earth: Interactive sun calculator 
 
This web application is designed to calculate Sun's position and time information (sunrise, sunset, solar noon, sun height angle, sun's direction, local time, date, etc.) given a variety of user inquiries. User can describe their questions in natural sentences, and the query processor is capable of extracting essential information, understanding the questions, and produce solutions. Another way of presenting queries is by directly filling in a form. In fact, a combination of sentence description and form submission is accepted. The calculator can detect any missing conditions in user queries and provide hints to add more details.

In addition, user is welcome to search for geographical information of places and register them in the record. As a result, user can directly enter registered place names instead of writing all details out, as details will be included automatically.

Calculation is based on spherical geometry and vector operations with no reliance on external data sources. The model is relatively simple, so result is not 100% accurate for rigorous scientific usage (although can serve as a good reference or verification). Nevertheless, deviation is small enough for less sensitive geographical/astronomical analysis and aviation/marinetime observations, as well as more casual applications like photography and architecture. 

This product is written in Python, Flask, and html. It is currently available for local machines after downloading the code. To launch the calculator, open "dashboard.py", run the file, and use a browser (localhost: 5005) to see the web page. No internet connection is required to use the calculator, as long as user can provide every condition needed for solutions.

The mathematical models, query processing system, calculator, and web pages are 100% designed by the owner, with no reliance on other sources (except for html basic guides).
