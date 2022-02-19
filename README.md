# Climate-Data-API

In order to prove to my dad that my room is the hottest in the house, I utilized ESP32 S2 Mini microproccessors running MicroPython to record and upload surrounding temperature to a web API at hourly intervals.
The file 'main.py' contains the code uploaded onto these microprocessors. The file 'connection.py' is omitted in the repository, but all it contains is data such as wifi information and access keys.

Then I created an ASP.NET web API hosted on Microsoft Azure to process temperature data and store it in a SQL database. Due to security reasons, the backend code will not be uploaded here.

The last step was visualizing the data! So I used Jupyter to plot data in combination with local weather data, making it easy to quickly analyze trends and patterns.
The ipynb file is uploaded in the repository, but for your convenience here is a link to view it:

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/ryan-skabelund/Climate-Data-API/main?labpath=ClimateData.ipynb)

Note that you will have to run the first cell, let both data tables load, and then run the second cell to see graphs.