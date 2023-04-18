# Wishlist for 360 Monitoring CLI


* add ability to open the chart for a specific metric via Get Server Metrics
* add ability to create status pages and remove incidents for status pages, as well as manage incident updates

## Delivered

* v1.0.16: show average uptime, average response time, etc. for a specified time interval: either --start 2023-01-01 --end 2023-01-01, for common intervals (1d, 1w, 1m, 1q, 1y) or daily / monthly averages for the specified timespan
* v1.0.16: add ability to print the monthly uptime in a table for the total time span available (for each month since start)
* v1.0.14: added ability to add incidents and list them for a given status page.
* v1.0.14: added ability to add incidents and list them for a given status page.
* v1.0.13: added "recommendations" command to display upgrade recommendations for servers that have exceeded their limits for the current workload.
* v1.0.11: introduced "--limit [0-9]*" to limit the number of items returned.
* v1.0.11: introduced "--sort FIELD [--reverse]" to sort items in a table according to the specified criteria.
