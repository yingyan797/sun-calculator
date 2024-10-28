# Y-Earth: Interactive sun calculator 
  
## For easier usage, please try out the online Frontend version [Y-Astronomy]
https://yingyan797.github.io/no-backend/y-astronomy (More STEM applications are also available on this site)

This web application is designed to Calculate and Visualize the Sun's position and time given user inquiries in natural language or questionnaires. OpenAI chatbot is Not used; instead, a parser is written for understanding user inquiries. Available calculations include sunrise, sunset, solar noon, sun height angle, sun's direction, local time, date, etc. The program is able to produce solutions in either numeric values or plots, depending on what user asks or implies. If any condition/detail essential for calculating/plotting a particular variable is missing in user queries, user will be prompted to add the corresponding details.

In addition, user is welcome to search for geographical information of places and register them in the record. As a result, user can directly enter registered place names instead of writing all details out, as details will be included automatically.

Calculation/Visualization is based solely on spherical geometry and 3D vector calculations with no reliance on external data sources. The model is relatively simple, so results are not 100% accurate for rigorous scientific usage. For example, the Sun's slightly elliptical orbit is treated as circle, and all years are assumed to be 365.25 day (average). Nevertheless, the deviation of calcultions is small enough for less sensitive geographical/astronomical analysis, architecture design, civil engineering, and photography, etc.

This product is written in Python, Flask, and html. It is currently available for local machines after downloading the code. To launch the calculator, open "dashboard.py", run the file, and use a browser (localhost: 5005) to see the web page. No internet connection is required to use the calculator (except for built-in geographical information searching).

The mathematical models, query processing system, calculator, and web pages are 100% designed by the owner, with no reliance on other sources (except for basic HTML/Flask coding guidance).
