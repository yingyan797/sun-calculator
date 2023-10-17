# Y-Earth: Interactive sun calculator 
 
This web application is designed to calculate the multiple categories of the sun's position and time information given a variety of user inquiries. User can describe their questions in natural sentences, and the query processor is capable of extracting essential information, understanding the questions, and produce solutions. Another way of presenting queries is by directly filling in a form. In fact, a combination of sentence description and form submission is accepted. The calculator can also detect any missing conditions in user queries and provide hints to add more details.

Calculation is based on spherical geometry and vector operations with no reliance on external data sources. The model is relatively simple, so result is not 100% accurate for rigorous scientific usage (although can serve as a good reference or verification). Nevertheless, deviation is small enough for applications like photography, architecture, detectives, and other daily, casual use cases. 

This product is written in Python, Flask, and html. It is currently available for local machines after downloading the code. To launch the calculator, open "dashboard.py", run the file, and use a browser (localhost: 5005) to see the web page. No internet connection is required to use the calculator, as long as user can provide every condition needed for solutions.

The mathematical models, query processor, and web page is 100% designed by the owner, with no reliance on other source. Code is 100% original.
