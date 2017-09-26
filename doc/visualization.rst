==================
Data Visualization
==================

.. contents::
   :local:

How to visualize the data collected by the execution of your custom pipeline
depends a lot on the nature of collected data itself.

In many situations what is required is to visualize the data collected by your
pipeline over a period of time, or as it is called: *time series data*.

Examples of time series data are:

- Evolution of the code coverage of your project over time.
- Internet speed of a system over time.
- CPU load of a system over time.
- Number of tests implemented, passed, failed or skipped in your project over
  time.
- Temperature, humidity, and barometric pressure submitted by sensor over time.

We could implemented a custom application using visualization libraries like
Bokeh_, which provides great flexibility and features for data visualization.

But in most cases, a general purpose tool for data visualization that provides
dashboards is more than enough and provides all the flexibility to plot more
and more data types as your custom pipeline keeps growing.

This tools requires to consume data from one of your sinks. Both
:ref:`Grafana <visualization-grafana>` and
:ref:`Chronograf <visualization-chronograf>` are able to consume from
InfluxDB_, which is supported by the built-in
:ref:`InfluxDBSource <sinks-influxdb>`.


.. _visualization-grafana:

Grafana
=======

Grafana_ provides an Open Source web based application that allows to define
dashboards with panels to visualize data from several sources:

.. figure:: _static/images/grafana.png
   :align: center


.. _visualization-chronograf:

Chronograf
==========

Similar to Grafana, Chronograf_ allows to plot data from the InfluxDB_ time
series database in an easy to use Open Source web application.

Chronograf is part of the stack developed by InfluxData, the company behind
InfluxDB.

.. figure:: _static/images/chronograf.png
   :align: center


.. _Bokeh: https://bokeh.pydata.org/en/latest/
.. _Grafana: https://grafana.com/
.. _Chronograf: https://docs.influxdata.com/chronograf/v1.3/introduction/getting-started/#chronograf-setup
.. _InfluxDB: https://www.influxdata.com/time-series-platform/influxdb/
