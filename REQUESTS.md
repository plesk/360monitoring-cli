# Wishlist for 360 Monitoring CLI

* show average uptime, average response time, etc. for a specified time interval: either --start 2023-01-01 13:24:11 --end 2023-01-01 15:24:11 or via --interval [1d, 7d, 1m, 2m, 1q, 1y]
* add ability to create status pages and remove incidents for status pages, as well as manage incident updates

## Delivered

* v1.0.14: added ability to add incidents and list them for a given status page.
* v1.0.14: added ability to add incidents and list them for a given status page.
* v1.0.13: added "recommendations" command to display upgrade recommendations for servers that have exceeded their limits for the current workload.
* v1.0.11: introduced "--limit [0-9]*" to limit the number of items returned.
* v1.0.11: introduced "--sort FIELD [--reverse]" to sort items in a table according to the specified criteria.
